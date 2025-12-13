# EQ12 Launcher - Fixed Version
# Addresses quoting and encoding issues

[CmdletBinding()]
param(
    [int]$Option = 0
)

# Configure UTF-8
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $env:PYTHONIOENCODING = "utf-8"
} catch {
    Write-Warning "UTF-8 configuration issue"
}

function Show-Menu {
    Clear-Host
    Write-Host "EQ12 LAUNCHER - FIXED VERSION" -ForegroundColor Cyan
    Write-Host "=" * 40 -ForegroundColor Gray
    Write-Host ""
    Write-Host "1. Run Syntax Checker" -ForegroundColor Yellow
    Write-Host "2. Run Syntax Fixer" -ForegroundColor Yellow  
    Write-Host "3. Sports Betting Analysis" -ForegroundColor Yellow
    Write-Host "4. Chrome Governance" -ForegroundColor Yellow
    Write-Host "5. System Validation" -ForegroundColor Yellow
    Write-Host "6. UTF-8 Configuration" -ForegroundColor Yellow
    Write-Host "7. Program Discovery" -ForegroundColor Yellow
    Write-Host "8. System Statistics" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "0. Exit" -ForegroundColor Red
    Write-Host ""
}

function Invoke-Option {
    param([int]$Choice)
    
    switch ($Choice) {
        1 { 
            Write-Host "Running syntax checker..." -ForegroundColor Green
            python "C:\EQ12\eq12_syntax_checker.py" --quick-check
        }
        2 { 
            Write-Host "Running syntax fixer..." -ForegroundColor Green  
            python "C:\EQ12\eq12_focused_syntax_fixer.py"
        }
        3 { 
            Write-Host "Running sports betting analysis..." -ForegroundColor Green
            python "C:\EQ12\eq12_sports_betting.py" --demo
        }
        4 { 
            Write-Host "Starting Chrome governance..." -ForegroundColor Green
            python "C:\EQ12\chrome_governance_automation.py" --launch-browser
        }
        5 { 
            Write-Host "Running system validation..." -ForegroundColor Green
            & "C:\EQ12\configure_utf8.ps1"
        }
        6 { 
            Write-Host "Configuring UTF-8..." -ForegroundColor Green
            & "C:\EQ12\configure_utf8.ps1"  
        }
        7 { 
            Write-Host "Running program discovery..." -ForegroundColor Green
            & "C:\EQ12\eq12_improved_discovery.ps1"
        }
        8 { 
            Write-Host "Displaying system statistics..." -ForegroundColor Green
            & "C:\EQ12\eq12_improved_discovery.ps1"
        }
        0 { 
            Write-Host "Exiting..." -ForegroundColor Red
            exit 0 
        }
        default { 
            Write-Host "Invalid option. Please try again." -ForegroundColor Red
            Start-Sleep 2
        }
    }
}

# Main execution
if ($Option -eq 0) {
    do {
        Show-Menu
        $choice = Read-Host "Select an option (0-8)"
        if ($choice -match '^[0-8]$') {
            Invoke-Option ([int]$choice)
            if ($choice -ne 0) {
                Write-Host ""
                Write-Host "Press any key to continue..." -ForegroundColor Gray
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            }
        } else {
            Write-Host "Please enter a number between 0-8" -ForegroundColor Red
            Start-Sleep 2
        }
    } while ($true)
} else {
    Invoke-Option $Option
}
