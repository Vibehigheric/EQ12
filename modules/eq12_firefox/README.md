EQ12 Firefox Module

This module provides convenience functions to launch Firefox with EQ12 profiles and to manage geckodriver placement.

Functions:
- Start-EQ12FirefoxBot [-ProfilePath <path>] [-Headless] [-NoRemote]
- New-EQ12GeckoDriver [-Destination <path>] (creates a placeholder and instructions; please download geckodriver manually)
- Register-EQ12FirefoxAliases (creates aliases like `eq12-firefox-bot` and `eq12-dashboard-firefox`)

Installation:
1. Copy this module to `C:\EQ12\modules\eq12_firefox`.
2. In your PowerShell profile, add: `Import-Module 'C:\EQ12\modules\eq12_firefox\eq12_firefox.psm1'` and then call `Register-EQ12FirefoxAliases`.

Notes:
- The module intentionally does not auto-download geckodriver for security reasons. Place `geckodriver.exe` in `C:\EQ12\bin` and ensure it's executable.
