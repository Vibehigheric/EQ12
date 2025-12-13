[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("Install", "Test", "Uninstall", "Status")]
    [string]$Action = "Install",

    [Parameter(Mandatory = $false)]
    [string]$EQ12Root = "C:\EQ12"
)# EQ12 Backtester Installation Script
# Professional installation and configuration for EQ12 Historic Backtester

Write-Host "EQ12 HISTORIC BACKTESTER INSTALLER" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Logging setup
$LogPath = Join-Path $EQ12Root "logs"
$LogFile = Join-Path $LogPath "backtester_install_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

if (!(Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
}

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")
    $LogEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

function Test-PythonInstallation {
    try {
        $PythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "Python found: $PythonVersion"
            return $true
        }
        else {
            Write-EQ12Log "Python not found in PATH" "ERROR"
            return $false
        }
    }
    catch {
        Write-EQ12Log "Python not installed or not accessible" "ERROR"
        return $false
    }
}

function Install-PythonPackages {
    Write-EQ12Log "Installing required Python packages..."

    $RequiredPackages = @(
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "requests>=2.28.0",
        "pytest>=7.0.0",
        "black>=22.0.0",
        "python-dateutil>=2.8.0"
    )

    foreach ($Package in $RequiredPackages) {
        Write-EQ12Log "Installing $Package..."
        try {
            & python -m pip install $Package --upgrade --quiet
            if ($LASTEXITCODE -eq 0) {
                Write-EQ12Log "Successfully installed $Package"
            }
            else {
                Write-EQ12Log "Failed to install $Package" "ERROR"
                return $false
            }
        }
        catch {
            Write-EQ12Log "Error installing $Package : $_" "ERROR"
            return $false
        }
    }

    return $true
}

function Test-BacktesterInstallation {
    Write-EQ12Log "Testing EQ12 Backtester installation..."

    # Check core files
    $CoreFiles = @(
        "eq12_backtester\core\engine.py",
        "eq12_backtester\data\loader.py",
        "eq12_backtester\simulators\sport_simulators.py",
        "eq12_backtester\optimizers\parlay_optimizer.py",
        "eq12_backtester\reporting.py",
        "eq12_backtester\run.py"
    )

    $AllFilesExist = $true
    foreach ($File in $CoreFiles) {
        $FilePath = Join-Path $EQ12Root $File
        if (Test-Path $FilePath) {
            Write-EQ12Log "Found: $File"
        }
        else {
            Write-EQ12Log "Missing: $File" "ERROR"
            $AllFilesExist = $false
        }
    }

    if (-not $AllFilesExist) {
        Write-EQ12Log "Core files missing - installation incomplete" "ERROR"
        return $false
    }

    # Test Python import
    try {
        $TestScript = @"
import sys
sys.path.append('$($EQ12Root.Replace('\', '\\'))')
from eq12_backtester.core.engine import EQ12BacktesterEngine
from eq12_backtester.reporting import EQ12ReportGenerator
print('EQ12 Backtester modules loaded successfully')
"@

        $TestResult = python -c $TestScript 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "Python modules test passed"
            return $true
        }
        else {
            Write-EQ12Log "Python modules test failed: $TestResult" "ERROR"
            return $false
        }
    }
    catch {
        Write-EQ12Log "Python test error: $_" "ERROR"
        return $false
    }
}

function Install-WindowsTask {
    Write-EQ12Log "Installing Windows scheduled task..."

    try {
        # Create task using Python script
        $TaskCreation = python -c @"
from eq12_backtester.reporting import EQ12TaskIntegration
integration = EQ12TaskIntegration('$($EQ12Root.Replace('\', '\\'))')
task_file = integration.create_daily_backtest_task()
print(f'Task XML created: {task_file}')
"@

        if ($LASTEXITCODE -ne 0) {
            Write-EQ12Log "Failed to create task XML" "ERROR"
            return $false
        }

        # Install the task
        $TaskXML = Join-Path $EQ12Root "EQ12_Daily_Backtest_Task.xml"
        if (Test-Path $TaskXML) {
            try {
                schtasks /create /xml $TaskXML /tn "EQ12_Daily_Backtest" /f | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-EQ12Log "Windows task installed successfully"
                    return $true
                }
                else {
                    Write-EQ12Log "Failed to install Windows task" "ERROR"
                    return $false
                }
            }
            catch {
                Write-EQ12Log "Task installation error: $_" "ERROR"
                return $false
            }
        }
        else {
            Write-EQ12Log "Task XML file not found" "ERROR"
            return $false
        }
    }
    catch {
        Write-EQ12Log "Task creation error: $_" "ERROR"
        return $false
    }
}

function Install-VSCodeTasks {
    Write-EQ12Log "Creating VS Code tasks integration..."

    try {
        $TasksCreation = python -c @"
from eq12_backtester.reporting import EQ12TaskIntegration
integration = EQ12TaskIntegration('$($EQ12Root.Replace('\', '\\'))')
tasks_file = integration.create_eq12_tasks_json()
print(f'VS Code tasks created: {tasks_file}')
"@

        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "VS Code tasks created successfully"
            return $true
        }
        else {
            Write-EQ12Log "Failed to create VS Code tasks" "ERROR"
            return $false
        }
    }
    catch {
        Write-EQ12Log "VS Code tasks error: $_" "ERROR"
        return $false
    }
}

function Show-InstallationStatus {
    Write-EQ12Log "=== EQ12 BACKTESTER STATUS ===" "INFO"

    # Check Python
    if (Test-PythonInstallation) {
        Write-Host "[OK] Python installation" -ForegroundColor Green
    }
    else {
        Write-Host "[FAIL] Python installation" -ForegroundColor Red
    }

    # Check core files
    if (Test-BacktesterInstallation) {
        Write-Host "[OK] Backtester modules" -ForegroundColor Green
    }
    else {
        Write-Host "[FAIL] Backtester modules" -ForegroundColor Red
    }

    # Check Windows task
    try {
        $TaskExists = schtasks /query /tn "EQ12_Daily_Backtest" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Windows scheduled task" -ForegroundColor Green
        }
        else {
            Write-Host "[MISSING] Windows scheduled task" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "[MISSING] Windows scheduled task" -ForegroundColor Yellow
    }

    # Check VS Code integration
    $VSCodeTasks = Join-Path $EQ12Root ".vscode\tasks.json"
    if (Test-Path $VSCodeTasks) {
        Write-Host "[OK] VS Code tasks integration" -ForegroundColor Green
    }
    else {
        Write-Host "[MISSING] VS Code tasks integration" -ForegroundColor Yellow
    }

    Write-EQ12Log "Status check completed"
}

function Uninstall-EQ12Backtester {
    Write-EQ12Log "Uninstalling EQ12 Backtester..."

    # Remove Windows task
    try {
        schtasks /delete /tn "EQ12_Daily_Backtest" /f 2>$null
        Write-EQ12Log "Removed Windows scheduled task"
    }
    catch {
        Write-EQ12Log "No Windows task to remove"
    }

    # Remove backtester directory (keep user choice)
    $BacktesterPath = Join-Path $EQ12Root "eq12_backtester"
    if (Test-Path $BacktesterPath) {
        $UserChoice = Read-Host "Remove backtester directory? (y/N)"
        if ($UserChoice -eq 'y' -or $UserChoice -eq 'Y') {
            Remove-Item -Path $BacktesterPath -Recurse -Force
            Write-EQ12Log "Removed backtester directory"
        }
    }

    Write-EQ12Log "Uninstallation completed"
}

# Main installation logic
switch ($Action) {
    "Install" {
        Write-EQ12Log "Starting EQ12 Backtester installation..."

        # Check prerequisites
        if (-not (Test-PythonInstallation)) {
            Write-EQ12Log "Python is required but not found. Please install Python 3.8+ first." "ERROR"
            exit 1
        }

        # Install Python packages
        if (-not (Install-PythonPackages)) {
            Write-EQ12Log "Failed to install required Python packages" "ERROR"
            exit 1
        }

        # Test installation
        if (-not (Test-BacktesterInstallation)) {
            Write-EQ12Log "Backtester modules not found or not working properly" "ERROR"
            exit 1
        }

        # Install Windows task
        Install-WindowsTask | Out-Null

        # Install VS Code integration
        Install-VSCodeTasks | Out-Null

        Write-EQ12Log "EQ12 Backtester installation completed successfully!" "INFO"
        Write-Host ""
        Write-Host "INSTALLATION COMPLETE!" -ForegroundColor Green
        Write-Host "You can now run:" -ForegroundColor Yellow
        Write-Host "  python $EQ12Root\eq12_backtester\run.py --help" -ForegroundColor Cyan
        Write-Host ""

        Show-InstallationStatus
    }

    "Test" {
        Write-EQ12Log "Running installation test..."
        if (Test-BacktesterInstallation) {
            Write-Host "TEST PASSED: EQ12 Backtester is properly installed" -ForegroundColor Green
            exit 0
        }
        else {
            Write-Host "TEST FAILED: EQ12 Backtester has issues" -ForegroundColor Red
            exit 1
        }
    }

    "Status" {
        Show-InstallationStatus
    }

    "Uninstall" {
        Uninstall-EQ12Backtester
    }

    default {
        Write-EQ12Log "Unknown action: $Action" "ERROR"
        exit 1
    }
}

Write-EQ12Log "Script execution completed"
