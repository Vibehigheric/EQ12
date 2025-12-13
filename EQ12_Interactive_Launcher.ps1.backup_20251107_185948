# EQ12 GODSTACK Interactive Command Launcher
# Provides a simple menu interface for launching common EQ12 tasks.

[CmdletBinding()]
param()

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "EQ12 GODSTACK - INTERACTIVE COMMAND LAUNCHER" -ForegroundColor Cyan
    Write-Host "=============================================================" -ForegroundColor Cyan
    Write-Host ""

    Write-Host "CORE SERVICES:" -ForegroundColor Yellow
    Write-Host "  1. Main Dashboard (Unified)" -ForegroundColor White
    Write-Host "  2. Status Dashboard" -ForegroundColor White
    Write-Host "  3. Node.js Server" -ForegroundColor White
    Write-Host "  4. System Health Check" -ForegroundColor White
    Write-Host ""

    Write-Host "AI SERVICES:" -ForegroundColor Yellow
    Write-Host "  5. OpenAI Streaming Assistant" -ForegroundColor White
    Write-Host "  6. Governance Assistant (Interactive)" -ForegroundColor White
    Write-Host "  7. ChatGPT Integration" -ForegroundColor White
    Write-Host "  8. AI Security Audit" -ForegroundColor White
    Write-Host ""

    Write-Host "BROWSER AUTOMATION:" -ForegroundColor Yellow
    Write-Host "  9. Chrome Governance Setup" -ForegroundColor White
    Write-Host " 10. Firefox Governance Setup" -ForegroundColor White
    Write-Host " 11. Extension Testing" -ForegroundColor White
    Write-Host ""

    Write-Host "SPORTS BETTING:" -ForegroundColor Yellow
    Write-Host " 12. CFB Optimizer" -ForegroundColor White
    Write-Host " 13. Parlay Builder" -ForegroundColor White
    Write-Host " 14. Monte Carlo Suite" -ForegroundColor White
    Write-Host " 15. Bankroll Tracker" -ForegroundColor White
    Write-Host ""

    Write-Host "SYSTEM UTILITIES:" -ForegroundColor Yellow
    Write-Host " 16. Start Full EQ12 Stack" -ForegroundColor White
    Write-Host " 17. System Status Check" -ForegroundColor White
    Write-Host " 18. Security Scanner" -ForegroundColor White
    Write-Host " 19. VPN Guard" -ForegroundColor White
    Write-Host ""

    Write-Host "DEVELOPMENT TOOLS:" -ForegroundColor Yellow
    Write-Host " 20. GitHub CLI Integration" -ForegroundColor White
    Write-Host " 21. Code Fixer" -ForegroundColor White
    Write-Host " 22. System Manager" -ForegroundColor White
    Write-Host ""

    Write-Host "INFORMATION:" -ForegroundColor Yellow
    Write-Host " 23. Show Command Sheet" -ForegroundColor White
    Write-Host " 24. View System Statistics" -ForegroundColor White
    Write-Host " 25. Access Points and URLs" -ForegroundColor White
    Write-Host ""

    Write-Host "  0. Exit" -ForegroundColor Red
    Write-Host ""
    Write-Host "=============================================================" -ForegroundColor Cyan
}

function Invoke-PythonScript {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RelativePath,

        [string[]]$Arguments = @()
    )

    $scriptPath = Join-Path -Path $scriptRoot -ChildPath $RelativePath

    if (-not (Test-Path -LiteralPath $scriptPath)) {
        Write-Error "Python script not found at $scriptPath"
        return
    }

    python $scriptPath @Arguments
}

function Invoke-PowerShellScript {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RelativePath
    )

    $scriptPath = Join-Path -Path $scriptRoot -ChildPath $RelativePath

    if (-not (Test-Path -LiteralPath $scriptPath)) {
        Write-Error "PowerShell script not found at $scriptPath"
        return
    }

    & $scriptPath
}

function Execute-Choice {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Choice
    )

    switch ($Choice) {
        '1' {
            Write-Host "Starting Main Dashboard..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'eq12_unified_dashboard.py'
        }
        '2' {
            Write-Host "Starting Status Dashboard..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'eq12_status_dashboard.py'
        }
        '3' {
            Write-Host "Starting Node.js Server..." -ForegroundColor Green
            $serverPath = Join-Path -Path $scriptRoot -ChildPath 'server'
            if (Test-Path -LiteralPath $serverPath) {
                Push-Location -LiteralPath $serverPath
                try {
                    npm start
                }
                finally {
                    Pop-Location
                }
            } else {
                Write-Error "Server directory not found at $serverPath"
            }
        }
        '4' {
            Write-Host "Running System Health Check..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'eq12_system_health.py'
        }
        '5' {
            Write-Host "Starting OpenAI Streaming Assistant..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'eq12_streaming_assistant.py'
        }
        '6' {
            Write-Host "Starting Governance Assistant (Interactive)..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'eq12_governance_assistant.py' -Arguments @('--interactive')
        }
        '7' {
            Write-Host "Starting ChatGPT Integration..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'scripts\eq12_chatgpt.py'
        }
        '8' {
            Write-Host "Running AI Security Audit..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'eq12_governance_assistant.py' -Arguments @('--question', 'Perform comprehensive security audit', '--task-type', 'security_audit')
        }
        '9' {
            Write-Host "Setting up Chrome Governance..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'chrome_governance_automation.py' -Arguments @('--setup-profile', '--verbose')
        }
        '10' {
            Write-Host "Setting up Firefox Governance..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'scripts\firefox_governance_automation.py'
        }
        '11' {
            Write-Host "Running Extension Testing..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'scripts\eq12_extension_tester.py'
        }
        '12' {
            Write-Host "Starting CFB Optimizer..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'scripts\eq12_cfb_optimizer.py'
        }
        '13' {
            Write-Host "Starting Parlay Builder..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'parlay_builder.py'
        }
        '14' {
            Write-Host "Running Monte Carlo Suite..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'eq12_monte_carlo_suite.py'
        }
        '15' {
            Write-Host "Starting Bankroll Tracker..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'scripts\bankroll_tracker_clean.py'
        }
        '16' {
            Write-Host "Starting Full EQ12 Stack..." -ForegroundColor Green
            Invoke-PowerShellScript -RelativePath 'Start-EQ12-GODSTACK-Clean.ps1'
        }
        '17' {
            Write-Host "Running System Status..." -ForegroundColor Green
            Invoke-PowerShellScript -RelativePath 'scripts\eq12_status.ps1'
        }
        '18' {
            Write-Host "Running Security Scanner..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'eq12_security_scanner.py'
        }
        '19' {
            Write-Host "Starting VPN Guard..." -ForegroundColor Green
            Invoke-PowerShellScript -RelativePath 'eq12_vpn_guard.ps1'
        }
        '20' {
            Write-Host "Starting GitHub CLI Integration..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'scripts\eq12_github_cli.py'
        }
        '21' {
            Write-Host "Running Code Fixer..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'eq12_code_fixer.py'
        }
        '22' {
            Write-Host "Starting System Manager..." -ForegroundColor Green
            Invoke-PythonScript -RelativePath 'eq12_system_manager.py'
        }
        '23' {
            Write-Host "Command Sheet:" -ForegroundColor Yellow
            $commandSheet = Join-Path -Path $scriptRoot -ChildPath 'EQ12_Command_Sheet.txt'
            if (Test-Path -LiteralPath $commandSheet) {
                Get-Content -Path $commandSheet | Out-Host
            } else {
                Write-Error "Command sheet not found at $commandSheet"
            }
            Read-Host -Prompt "Press Enter to return to the menu" | Out-Null
        }
        '24' {
            Write-Host "System Statistics:" -ForegroundColor Yellow
            $pythonFiles = (Get-ChildItem -Path $scriptRoot -Filter '*.py' -Recurse | Measure-Object).Count
            $powershellFiles = (Get-ChildItem -Path $scriptRoot -Filter '*.ps1' -Recurse | Measure-Object).Count
            $vbFiles = (Get-ChildItem -Path $scriptRoot -Filter '*.vb' -Recurse | Measure-Object).Count
            $jsFiles = (Get-ChildItem -Path $scriptRoot -Filter '*.js' -Recurse | Measure-Object).Count
            Write-Host "  Python Programs: $pythonFiles" -ForegroundColor White
            Write-Host "  PowerShell Scripts: $powershellFiles" -ForegroundColor White
            Write-Host "  VB.NET Programs: $vbFiles" -ForegroundColor White
            Write-Host "  JavaScript Files: $jsFiles" -ForegroundColor White
            $total = $pythonFiles + $powershellFiles + $vbFiles + $jsFiles
            Write-Host "  Total Files: $total" -ForegroundColor Green
            Read-Host -Prompt "Press Enter to return to the menu" | Out-Null
        }
        '25' {
            Write-Host "Access Points:" -ForegroundColor Yellow
            Write-Host "  Local Dashboard: http://localhost:3000/dashboard" -ForegroundColor Green
            Write-Host "  Emergency Server: http://localhost:8081" -ForegroundColor Green
            Write-Host "  Public Access: https://b342ccc2bde9.ngrok-free.app/dashboard" -ForegroundColor Green
            Write-Host "  Ngrok Inspector: http://127.0.0.1:4040" -ForegroundColor Green
            Read-Host -Prompt "Press Enter to return to the menu" | Out-Null
        }
        '0' {
            Write-Host "Goodbye! EQ12 GODSTACK ready when you are." -ForegroundColor Green
            exit
        }
        default {
            Write-Host "Invalid choice. Please try again." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
}

do {
    Show-Menu
    $choice = Read-Host "Select an option (0-25)"
    Write-Host ""

    if ([string]::IsNullOrWhiteSpace($choice)) {
        Write-Host "No selection detected. Please choose an option." -ForegroundColor Yellow
        Start-Sleep -Seconds 1
        continue
    }

    Execute-Choice -Choice $choice

    if ($choice -notin @('0', '23', '24', '25')) {
        Write-Host ""
        Write-Host "Press any key to return to the menu..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    }
} while ($true)
