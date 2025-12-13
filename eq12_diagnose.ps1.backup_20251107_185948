# EQ12 Workspace Diagnostic Script
param(
    [string]$OutputFile = "eq12_diagnostic_report.txt"
)

$ErrorActionPreference = "Continue"
$output = @()

function Write-DiagnosticOutput {
    param([string]$Message)
    $output += $Message
    Write-Host $Message
}

Write-DiagnosticOutput "=== EQ12 WORKSPACE DIAGNOSTIC REPORT ==="
Write-DiagnosticOutput "Generated: $(Get-Date)"
Write-DiagnosticOutput "Workspace: C:\EQ12"
Write-DiagnosticOutput ""

# 1. INVENTORY & STRUCTURE
Write-DiagnosticOutput "1. WORKSPACE INVENTORY"
Write-DiagnosticOutput "====================="
Write-DiagnosticOutput "Directory structure:"
Get-ChildItem -Path . -Directory | ForEach-Object {
    Write-DiagnosticOutput "   $($_.Name)"
}

Write-DiagnosticOutput ""
Write-DiagnosticOutput "Key files by type:"
Write-DiagnosticOutput "Python files:"
Get-ChildItem -Path . -Filter "*.py" -Recurse | Select-Object -First 20 | ForEach-Object {
    Write-DiagnosticOutput "   $($_.FullName.Replace($PWD.Path + '\', ''))"
}

Write-DiagnosticOutput ""
Write-DiagnosticOutput "PowerShell files:"
Get-ChildItem -Path . -Filter "*.ps1" -Recurse | Select-Object -First 20 | ForEach-Object {
    Write-DiagnosticOutput "   $($_.FullName.Replace($PWD.Path + '\', ''))"
}

Write-DiagnosticOutput ""
Write-DiagnosticOutput "Configuration files:"
@("*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg") | ForEach-Object {
    Get-ChildItem -Path . -Filter $_ -Recurse | Select-Object -First 10 | ForEach-Object {
        Write-DiagnosticOutput "   $($_.FullName.Replace($PWD.Path + '\', ''))"
    }
}

# 2. CI/CD FILES
Write-DiagnosticOutput ""
Write-DiagnosticOutput "2. CI/CD & AUTOMATION"
Write-DiagnosticOutput "====================="
if (Test-Path ".github") {
    Write-DiagnosticOutput "GitHub workflows found:"
    Get-ChildItem -Path ".github" -Recurse -Filter "*.yml" | ForEach-Object {
        Write-DiagnosticOutput "   $($_.FullName.Replace($PWD.Path + '\', ''))"
    }
} else {
    Write-DiagnosticOutput " No .github directory found"
}

# 3. PYTHON ENVIRONMENT CHECK
Write-DiagnosticOutput ""
Write-DiagnosticOutput "3. PYTHON ENVIRONMENT"
Write-DiagnosticOutput "====================="
try {
    $pyVersion = python --version 2>&1
    Write-DiagnosticOutput "Python version: $pyVersion"
} catch {
    Write-DiagnosticOutput " Python not found in PATH"
}

try {
    $pipList = pip list 2>&1
    Write-DiagnosticOutput "Installed packages (first 10):"
    $pipList | Select-Object -First 10 | ForEach-Object {
        Write-DiagnosticOutput "   $_"
    }
} catch {
    Write-DiagnosticOutput " pip not available"
}

# 4. REQUIREMENTS FILES CHECK
Write-DiagnosticOutput ""
Write-DiagnosticOutput "4. REQUIREMENTS & DEPENDENCIES"
Write-DiagnosticOutput "==============================="
@("requirements.txt", "requirements-*.txt", "pyproject.toml", "setup.py", "package.json") | ForEach-Object {
    if (Test-Path $_) {
        Write-DiagnosticOutput " Found: $_"
        $content = Get-Content $_ -TotalCount 5
        Write-DiagnosticOutput "  Preview: $($content -join '; ')"
    }
}

# 5. PYTHON SYNTAX CHECK
Write-DiagnosticOutput ""
Write-DiagnosticOutput "5. PYTHON SYNTAX VALIDATION"
Write-DiagnosticOutput "============================"
Get-ChildItem -Path . -Filter "*.py" -Recurse | Select-Object -First 10 | ForEach-Object {
    try {
        $result = python -m py_compile $_.FullName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-DiagnosticOutput " $($_.Name) - Syntax OK"
        } else {
            Write-DiagnosticOutput " $($_.Name) - Syntax Error: $result"
        }
    } catch {
        Write-DiagnosticOutput " $($_.Name) - Could not check syntax"
    }
}

# 6. SECURITY SCAN
Write-DiagnosticOutput ""
Write-DiagnosticOutput "6. SECURITY SCAN"
Write-DiagnosticOutput "================"
Write-DiagnosticOutput "Scanning for potential security issues..."

Get-ChildItem -Path . -Filter "*.py" -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($content) {
        if ($content -match "eval\(|exec\(|os\.system\(") {
            Write-DiagnosticOutput " $($_.Name) - Contains potentially unsafe functions"
        }
        if ($content -match "password\s*=\s*['\"].*['\"]|api_key\s*=\s*['\"].*['\"]") {
            Write-DiagnosticOutput " $($_.Name) - May contain hardcoded secrets"
        }
    }
}

# 7. POWERSHELL SYNTAX CHECK
Write-DiagnosticOutput ""
Write-DiagnosticOutput "7. POWERSHELL SYNTAX CHECK"
Write-DiagnosticOutput "=========================="
Get-ChildItem -Path . -Filter "*.ps1" -Recurse | Select-Object -First 10 | ForEach-Object {
    try {
        $result = powershell -NoProfile -Command "& { $ErrorActionPreference = 'Stop'; . '$($_.FullName)' }" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-DiagnosticOutput " $($_.Name) - Syntax OK"
        } else {
            Write-DiagnosticOutput " $($_.Name) - Syntax Error: $($result | Select-Object -First 1)"
        }
    } catch {
        Write-DiagnosticOutput " $($_.Name) - Could not check syntax: $($_.Exception.Message)"
    }
}

# 8. IMPORT ANALYSIS
Write-DiagnosticOutput ""
Write-DiagnosticOutput "8. IMPORT ANALYSIS"
Write-DiagnosticOutput "=================="
Get-ChildItem -Path . -Filter "*.py" -Recurse | Select-Object -First 5 | ForEach-Object {
    Write-DiagnosticOutput "Analyzing imports in $($_.Name):"
    $content = Get-Content $_.FullName -ErrorAction SilentlyContinue
    $imports = $content | Where-Object { $_ -match "^(import |from .* import)" }
    $imports | Select-Object -First 5 | ForEach-Object {
        Write-DiagnosticOutput "   $_"
    }
}

# 9. LOG FILES CHECK
Write-DiagnosticOutput ""
Write-DiagnosticOutput "9. LOG FILES & OUTPUTS"
Write-DiagnosticOutput "======================"
if (Test-Path "logs") {
    Write-DiagnosticOutput "Log directory contents:"
    Get-ChildItem -Path "logs" | ForEach-Object {
        Write-DiagnosticOutput "   $($_.Name) ($([math]::Round($_.Length/1KB, 2)) KB)"
    }
} else {
    Write-DiagnosticOutput "ℹ No logs directory found"
}

Write-DiagnosticOutput ""
Write-DiagnosticOutput "=== DIAGNOSTIC COMPLETE ==="
Write-DiagnosticOutput "Report saved to: $OutputFile"

# Save output to file
$output | Out-File -FilePath $OutputFile -Encoding UTF8