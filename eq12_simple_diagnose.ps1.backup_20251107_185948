# Simple EQ12 Diagnostic Script
$outputFile = "eq12_diagnostic_report.txt"
$output = @()

function Add-Output($message) {
    $global:output += $message
    Write-Host $message
}

Add-Output "=== EQ12 WORKSPACE DIAGNOSTIC ==="
Add-Output "Generated: $(Get-Date)"
Add-Output ""

# 1. Directory Structure
Add-Output "1. DIRECTORY STRUCTURE"
Add-Output "======================"
Get-ChildItem -Directory | ForEach-Object {
    Add-Output "FOLDER: $($_.Name)"
}
Add-Output ""

# 2. Python Files
Add-Output "2. PYTHON FILES"
Add-Output "==============="
Get-ChildItem -Filter "*.py" -Recurse | Select-Object -First 30 | ForEach-Object {
    Add-Output "PYTHON: $($_.FullName.Replace((Get-Location).Path + '\', ''))"
}
Add-Output ""

# 3. PowerShell Files
Add-Output "3. POWERSHELL FILES"
Add-Output "=================="
Get-ChildItem -Filter "*.ps1" -Recurse | Select-Object -First 20 | ForEach-Object {
    Add-Output "PS1: $($_.FullName.Replace((Get-Location).Path + '\', ''))"
}
Add-Output ""

# 4. Configuration Files
Add-Output "4. CONFIGURATION FILES"
Add-Output "======================"
@("*.json", "*.yaml", "*.yml", "*.txt", "*.md") | ForEach-Object {
    Get-ChildItem -Filter $_ -File | Select-Object -First 15 | ForEach-Object {
        Add-Output "CONFIG: $($_.Name)"
    }
}
Add-Output ""

# 5. Python Syntax Check
Add-Output "5. PYTHON SYNTAX CHECK"
Add-Output "======================"
Get-ChildItem -Filter "*.py" | Select-Object -First 10 | ForEach-Object {
    try {
        $null = python -m py_compile $_.FullName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Add-Output "OK: $($_.Name)"
        } else {
            Add-Output "SYNTAX ERROR: $($_.Name)"
        }
    } catch {
        Add-Output "CHECK FAILED: $($_.Name)"
    }
}
Add-Output ""

# 6. Requirements Analysis
Add-Output "6. REQUIREMENTS FILES"
Add-Output "===================="
if (Test-Path "requirements.txt") {
    Add-Output "FOUND: requirements.txt"
    Get-Content "requirements.txt" | Select-Object -First 5 | ForEach-Object {
        Add-Output "REQ: $_"
    }
}
if (Test-Path "requirements-enterprise.txt") {
    Add-Output "FOUND: requirements-enterprise.txt"
}
Add-Output ""

# 7. Environment Check
Add-Output "7. ENVIRONMENT VARIABLES"
Add-Output "======================="
$envKeys = @("OPENAI_API_KEY", "DATABASE_URL", "SECRET_KEY")
foreach ($key in $envKeys) {
    $value = [Environment]::GetEnvironmentVariable($key)
    if ($value) {
        Add-Output "SET: $key (length: $($value.Length))"
    } else {
        Add-Output "MISSING: $key"
    }
}
Add-Output ""

# 8. Security Issues
Add-Output "8. SECURITY SCAN"
Add-Output "==============="
Get-ChildItem -Filter "*.py" | Select-Object -First 10 | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($content) {
        if ($content -match "eval\(") { Add-Output "SECURITY: $($_.Name) contains eval()" }
        if ($content -match "exec\(") { Add-Output "SECURITY: $($_.Name) contains exec()" }
        if ($content -match "os\.system") { Add-Output "SECURITY: $($_.Name) contains os.system" }
        if ($content -match "sk-[a-zA-Z0-9]{32,}") { Add-Output "SECURITY: $($_.Name) may contain API keys" }
    }
}
Add-Output ""

# 9. Import Analysis
Add-Output "9. IMPORT ISSUES"
Add-Output "==============="
Get-ChildItem -Filter "*.py" | Select-Object -First 5 | ForEach-Object {
    $imports = Get-Content $_.FullName | Where-Object { $_ -match "^(import |from )" }
    if ($imports) {
        Add-Output "IMPORTS in $($_.Name):"
        $imports | Select-Object -First 3 | ForEach-Object {
            Add-Output "  $_"
        }
    }
}
Add-Output ""

Add-Output "=== DIAGNOSTIC COMPLETE ==="

# Save to file
$output | Out-File -FilePath $outputFile -Encoding UTF8
Add-Output "Report saved to: $outputFile"
