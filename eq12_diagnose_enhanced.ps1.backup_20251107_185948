# EQ12 Diagnose & Report (Windows)
# Run in an elevated PowerShell from C:\EQ12
# Usage:  pwsh -NoProfile -ExecutionPolicy Bypass -File .\eq12_diagnose.ps1

$ErrorActionPreference = "SilentlyContinue"
$report = @()

function Add-Section($title) { $report += "`n===== $title =====`n" }

Add-Section "Environment"
$report += "PWD: $(Get-Location)"
$report += "Python: $(py -3 --version 2>$null)"
$report += "Node: $(node --version 2>$null)"
$report += "NPM: $(npm --version 2>$null)"
$report += "Git: $(git --version 2>$null)"

Add-Section "Repo Summary"
$report += (git status --porcelain=v1 2>$null)
$report += "`nLanguages snapshot:"
$report += (Get-ChildItem -Recurse -File -Include *.py, *.ps1, *.psm1, *.js, *.ts, *.json, *.yml, *.yaml, *.toml, *.ini, *.cfg, *.sh, *.bat, *.psd1, *.psm1, *.dockerfile, Dockerfile  | Group-Object Extension | Sort-Object Count -Descending | Format-Table -AutoSize | Out-String)

Add-Section "Python: venv & deps"
if (Test-Path .\requirements.txt) { $report += "requirements.txt found" } else { $report += "requirements.txt NOT found" }
$report += (py -3 -m pip list 2>$null | Out-String)

Add-Section "Node: deps & audit"
if (Test-Path .\package.json) {
    $report += (npm ls --depth=0 2>$null | Out-String)
    $report += (npm audit --json 2>$null | Out-String)
} else { $report += "No package.json" }

Add-Section "Linters & Static Analysis"
if (Get-Command flake8 -ErrorAction SilentlyContinue) { $report += (flake8 . 2>&1 | Out-String) } else { $report += "flake8 not installed" }
if (Get-Command mypy -ErrorAction SilentlyContinue) { $report += (mypy . 2>&1 | Out-String) } else { $report += "mypy not installed" }
if (Get-Command bandit -ErrorAction SilentlyContinue) { $report += (bandit -q -r . 2>&1 | Out-String) } else { $report += "bandit not installed" }

Add-Section "Tests"
if (Get-Command pytest -ErrorAction SilentlyContinue) { $report += (pytest -q 2>&1 | Out-String) } else { $report += "pytest not installed" }

Add-Section "YAML & GitHub Actions"
$actions = Get-ChildItem -Recurse -File -Include *.yml, *.yaml | Where-Object { $_.FullName -match "\\.github\\workflows" }
if ($actions) { $report += "Workflows found:`n" + ($actions | Select-Object -Expand FullName) } else { $report += "No workflows found" }

Add-Section "Dockerfile Lint (hadolint if available)"
if (Get-Command hadolint -ErrorAction SilentlyContinue) {
    Get-ChildItem -Recurse -File -Include Dockerfile, *.[dD]ockerfile | ForEach-Object {
        $report += "`n-- $_ --"
        $report += (hadolint $_.FullName 2>&1 | Out-String)
    }
} else { $report += "hadolint not installed" }

Add-Section "Secret scan (gitleaks if available)"
if (Get-Command gitleaks -ErrorAction SilentlyContinue) {
    $report += (gitleaks detect --no-banner --redact --source . 2>&1 | Out-String)
} else { $report += "gitleaks not installed" }

Add-Section "Done"
$reportText = $report -join "`n"
$reportText | Out-File -FilePath .\eq12_diagnose.txt -Encoding UTF8
Write-Host "Wrote diagnostics to eq12_diagnose.txt"
