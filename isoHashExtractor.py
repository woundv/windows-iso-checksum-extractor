import asyncio
import json
import sys
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

URL = "https://www.microsoft.com/en-us/software-download/windows11"

async def scrape_hashes():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"--- going to url ---")
        try:
            await page.goto(URL, wait_until="domcontentloaded")
        except Exception as e:
            print(f"[!] -> failed to load page: {e}")
            await browser.close()
            return

        print("=> fetching verification section")
        
        try:
            verify_trigger = page.get_by_role("button", name="Verify your download").first
            
            await verify_trigger.wait_for(state="attached", timeout=10000)
            table_header_locator = page.locator("text='Hash values for the ISO files'")
            
            if not await table_header_locator.is_visible():
                print("==> section collapsed, fixing")
                await verify_trigger.click(force=True)
                await table_header_locator.wait_for(state="visible", timeout=5000)
            else:
                print("==> section already expanded")

        except PlaywrightTimeoutError:
            pass

        print("==> finding hash table")
        
        target_table = None
        tables = page.locator("table")
        count = await tables.count()
        
        for i in range(count):
            table = tables.nth(i)
            content = await table.text_content()
            if ("Hash Code" in content or "SHA256" in content) and "English" in content:
                target_table = table
                break
        
        extracted_data = {}

        if target_table:
            await asyncio.sleep(1)
            print("===> found, extracting rows")
            rows = target_table.locator("tbody tr")
            row_count = await rows.count()
            
            for i in range(row_count):
                row = rows.nth(i)
                cells = row.locator("td")
                
                if await cells.count() >= 2:
                    language_edition = await cells.nth(0).text_content()
                    hash_value = await cells.nth(1).text_content()
                    
                    if language_edition and hash_value:
                        clean_lang = language_edition.strip()
                        clean_hash = hash_value.strip()
                        extracted_data[clean_lang] = clean_hash
        else:
            await asyncio.sleep(1)
            print("[!] ===> no table found on page")

        if extracted_data:
            await asyncio.sleep(1)
            print(f"====> extracted **{len(extracted_data)}** hashes")
            
            with open("hashes.json", "w", encoding="utf-8") as f:
                json.dump(extracted_data, f, indent=4)
            await asyncio.sleep(1)
            print("=====> table saved to hashes.json")
        else:
            await asyncio.sleep(1)
            print("[!] =====> extraction failed")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_hashes())