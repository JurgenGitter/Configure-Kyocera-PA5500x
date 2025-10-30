This is a python script that configures Kyocera PA5500xs over the network to my specifications.

Packaged using PyInstaller CMD run: pyinstaller --onefile --add-binary "C:..\chromedriver.exe;." --add-data "chrome-win64;chrome-win64" C:..\script.py Packaged directory format: Folder - |_Chrome-Win64 |_Chromedriver.exe |_Script.py

Chromedriver version: 139.xx Chrome-Win64 version: 139.xx While Docker would have been a great alternative to a packaged EXE, there was a lot of difficulty have chrome work on a docker installation. Perhaps I am just bad, but signs pointed to chrome dependencies not functioning correctly.

Prerequisites: In Windows Credential Manger > Windows Credentials > Generic credentials you must have 4 entries. 2 for SNMP communities, 2 for Printer authentication. Without these, it will not work.
