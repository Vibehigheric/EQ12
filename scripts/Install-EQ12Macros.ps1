[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)][string]$ReposRoot = 'C:\Repos',
    [Parameter(Mandatory=$false)][string]$MacroFile = 'C:\EQ12\macros\EQ12Macros.xml',
    [switch]$Apply
)

function Install-EQ12Macros {
    param($ReposRoot, $MacroFile, $Apply)

    $macro = Resolve-Path $MacroFile
    if (-not $macro) { Write-Error "Macro file not found: $MacroFile"; return }

    $repos = Get-ChildItem -Path $ReposRoot -Directory -ErrorAction SilentlyContinue
    if (-not $repos) { Write-Warning "No repos found under $ReposRoot"; return }

    foreach ($r in $repos) {
        $target = Join-Path $r.FullName 'EQ12Macros.xml'
        if (-not $Apply) { Write-Host "Dry-run: would copy $macro to $target"; continue }
        Copy-Item -Path $macro -Destination $target -Force
        Write-Host "Copied EQ12Macros.xml to $target"

        # Optionally update JAMS config (DefaultMacroFile) if present
        $jamsCfg = Join-Path $r.FullName 'jams.config'
        if (Test-Path $jamsCfg) {
            try {
                (Get-Content $jamsCfg) -replace 'DefaultMacroFile=.*', "DefaultMacroFile=$target" | Set-Content $jamsCfg
                Write-Host "Updated JAMS config DefaultMacroFile in $jamsCfg"
            } catch {
                Write-Warning "Failed to update ${jamsCfg}: $_"
            }
        }
    }
}

Install-EQ12Macros -ReposRoot $ReposRoot -MacroFile $MacroFile -Apply:$Apply
