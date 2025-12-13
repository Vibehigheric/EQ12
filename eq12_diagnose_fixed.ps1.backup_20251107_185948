# EQ12 Workspace Diagnostic Script - Fixed Version
param(
    [string]$OutputFile = "eq12_diagnostic_report.txt"
)

$ErrorActionPreference = "Continue"
$output = @()

function Write-DiagnosticOutput {
    param([string]$Message)
    $global:output += $Message
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
    Write-DiagnosticOutput "  Folder: $($_.Name)"
}

Write-DiagnosticOutput ""
Write-DiagnosticOutput "Python files:"
Get-ChildItem -Path . -Filter "*.py" -Recurse | Select-Object -First 20 | ForEach-Object {
    Write-DiagnosticOutput "  Python: $($_.FullName.Replace($PWD.Path + '\', ''))"
}

Write-DiagnosticOutput ""
Write-DiagnosticOutput "PowerShell files:"
Get-ChildItem -Path . -Filter "*.ps1" -Recurse | Select-Object -First 20 | ForEach-Object {
    Write-DiagnosticOutput "  PowerShell: $($_.FullName.Replace($PWD.Path + '\', ''))"
}

Write-DiagnosticOutput ""
Write-DiagnosticOutput "Configuration files:"
@("*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg") | ForEach-Object {
    Get-ChildItem -Path . -Filter $_ -Recurse | Select-Object -First 10 | ForEach-Object {
        Write-DiagnosticOutput "  Config: $($_.FullName.Replace($PWD.Path + '\', ''))"
    }
}

# 2. CI/CD FILES
Write-DiagnosticOutput ""
Write-DiagnosticOutput "2. CI/CD AND AUTOMATION"
Write-DiagnosticOutput "======================"
if (Test-Path ".github") {
    Write-DiagnosticOutput "GitHub workflows found:"
    Get-ChildItem -Path ".github" -Recurse -Filter "*.yml" | ForEach-Object {
        Write-DiagnosticOutput "  Workflow: $($_.FullName.Replace($PWD.Path + '\', ''))"
    }
} else {
    Write-DiagnosticOutput "ERROR: No .github directory found"
}

# 3. PYTHON ENVIRONMENT CHECK
Write-DiagnosticOutput ""
Write-DiagnosticOutput "3. PYTHON ENVIRONMENT"
Write-DiagnosticOutput "====================="
try {
    $pyVersion = python --version 2>&1
    Write-DiagnosticOutput "Python version: $pyVersion"
} catch {
    Write-DiagnosticOutput "ERROR: Python not found in PATH"
}

try {
    Write-DiagnosticOutput "Installed packages (first 10):"
    $pipList = pip list 2>&1 | Select-Object -First 10
    $pipList | ForEach-Object {
        Write-DiagnosticOutput "  Package: $_"
    }
} catch {
    Write-DiagnosticOutput "ERROR: pip not available"
}

# 4. REQUIREMENTS FILES CHECK
Write-DiagnosticOutput ""
Write-DiagnosticOutput "4. REQUIREMENTS AND DEPENDENCIES"
Write-DiagnosticOutput "================================"
@("requirements.txt", "requirements-*.txt", "pyproject.toml", "setup.py", "package.json") | ForEach-Object {
    if (Test-Path $_) {
        Write-DiagnosticOutput "FOUND: $_"
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
            Write-DiagnosticOutput "OK: $($_.Name) - Syntax valid"
        } else {
            Write-DiagnosticOutput "ERROR: $($_.Name) - Syntax error: $result"
        }
    } catch {
        Write-DiagnosticOutput "WARNING: $($_.Name) - Could not check syntax"
    }
}

# 6. SECURITY SCAN
Write-DiagnosticOutput ""
Write-DiagnosticOutput "6. SECURITY SCAN"
Write-DiagnosticOutput "================"
Write-DiagnosticOutput "Scanning for potential security issues..."

Get-ChildItem -Path . -Filter "*.py" -Recurse | Select-Object -First 20 | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($content) {
        if ($content -match "eval\(|exec\(") {
            Write-DiagnosticOutput "WARNING: $($_.Name) - Contains eval/exec functions"
        }
        if ($content -match "os\.system\(") {
            Write-DiagnosticOutput "WARNING: $($_.Name) - Contains os.system calls"
        }
        if ($content -match "password.*=.*['\`"].*['\`"]") {
            Write-DiagnosticOutput "SECURITY: $($_.Name) - May contain hardcoded passwords"
        }
        if ($content -match "api_key.*=.*['\`"].*['\`"]") {
            Write-DiagnosticOutput "SECURITY: $($_.Name) - May contain hardcoded API keys"
        }
    }
}

# 7. POWERSHELL SYNTAX CHECK
Write-DiagnosticOutput ""
Write-DiagnosticOutput "7. POWERSHELL SYNTAX CHECK"
Write-DiagnosticOutput "=========================="
Get-ChildItem -Path . -Filter "*.ps1" -Recurse | Select-Object -First 10 | ForEach-Object {
    if ($_.Name -ne "eq12_diagnose.ps1") {
        # Skip the diagnostic script itself
        try {
            $tokens = $null
            $errors = $null
            $ast = [System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$tokens, [ref]$errors)
            if ($errors.Count -eq 0) {
                Write-DiagnosticOutput "OK: $($_.Name) - Syntax valid"
            } else {
                Write-DiagnosticOutput "ERROR: $($_.Name) - Syntax errors: $($errors.Count)"
                $errors | ForEach-Object {
                    Write-DiagnosticOutput "  Issue: $($_.Message)"
                }
            }
        } catch {
            Write-DiagnosticOutput "WARNING: $($_.Name) - Could not parse: $($_.Exception.Message)"
        }
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
        Write-DiagnosticOutput "  Import: $_"
    }
}

# 9. LOG FILES CHECK
Write-DiagnosticOutput ""
Write-DiagnosticOutput "9. LOG FILES AND OUTPUTS"
Write-DiagnosticOutput "========================"
if (Test-Path "logs") {
    Write-DiagnosticOutput "Log directory contents:"
    Get-ChildItem -Path "logs" | ForEach-Object {
        $sizeKB = [math]::Round($_.Length / 1KB, 2)
        Write-DiagnosticOutput "  LogFile: $($_.Name) ($sizeKB KB)"
    }
} else {
    Write-DiagnosticOutput "INFO: No logs directory found"
}

# 10. ENVIRONMENT VARIABLES CHECK
Write-DiagnosticOutput ""
Write-DiagnosticOutput "10. ENVIRONMENT VARIABLES"
Write-DiagnosticOutput "========================="
$envVars = @("OPENAI_API_KEY", "DATABASE_URL", "SECRET_KEY", "STRIPE_SECRET_KEY")
$envVars | ForEach-Object {
    if ($env:$_) {
        Write-DiagnosticOutput "FOUND: $_ (length: $((Get-Item "env:$_").Value.Length) chars)"
    } else {
        Write-DiagnosticOutput "MISSING: $_"
    }
}

Write-DiagnosticOutput ""
Write-DiagnosticOutput "=== DIAGNOSTIC COMPLETE ==="
Write-DiagnosticOutput "Report saved to: $OutputFile"

# Save output to file
$output | Out-File -FilePath $OutputFile -Encoding UTF8
