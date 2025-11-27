# windows iso checksum extractor

extracts the sha-256 checksum table from the windows 11 download page without having to interact with the website
useful if you want to verify 3rd party iso checksums

personally i made this because i couldnt access the official download page with my vpn on

once complete do the following:

npx playwright uninstall --all
pip uninstall playwright

navigate to:

- windows: %USERPROFILE%\AppData\Local\ms-playwright
- macOS: ~/Library/Caches/ms-playwright
- linux: ~/.cache/ms-playwright

and delete the folder

doing this will remove the leftover browser and chache made from playwright
