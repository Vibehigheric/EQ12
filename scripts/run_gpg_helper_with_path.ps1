# Temporary helper: prepend Git-for-Windows gpg to PATH and run the GPG key generator
$gpgDir = 'C:\Program Files\Git\usr\bin'
if (Test-Path $gpgDir) { $env:PATH = "$gpgDir;" + $env:PATH }
# Run the helper (non-interactive sample name/email)
& 'C:\EQ12\scripts\generate_and_add_gpg_key.ps1' -Name 'Ricoj100' -Email 'ricoj100@example.com' -NoInteract
