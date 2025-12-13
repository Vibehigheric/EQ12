Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -Command "Import-Module PSWindowsUpdate; Get-WindowsUpdate; Install-WindowsUpdate -AcceptAll -AutoReboot"'
