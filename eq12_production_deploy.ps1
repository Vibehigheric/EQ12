# EQ12 Production Deployment Script
# Comprehensive deployment automation for production environments

param(
    [switch]$Deploy,
    [switch]$Backup,
    [switch]$Rollback,
    [switch]$Status
)

$EQ12_ROOT = "C:\EQ12"
$XAMPP_ROOT = "C:\xampp"
$BACKUP_ROOT = "$EQ12_ROOT\production_backups"
$DEPLOYMENT_LOG = "$EQ12_ROOT\logs\deployment.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    Add-Content -Path $DEPLOYMENT_LOG -Value $logEntry
}

function Backup-Production {
    Write-Log "Creating production backup..." "INFO"

    $backupDir = Join-Path $BACKUP_ROOT (Get-Date -Format "yyyyMMdd_HHmmss")
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

    # Backup configurations
    $configs = @(
        "$XAMPP_ROOT\apache\conf\httpd.conf",
        "$XAMPP_ROOT\php\php.ini",
        "$XAMPP_ROOT\htdocs\api.php",
        "$XAMPP_ROOT\htdocs\index.html",
        "$XAMPP_ROOT\htdocs\.htaccess",
        "$EQ12_ROOT\.env",
        "$EQ12_ROOT\node\ecosystem.config.js"
    )

    foreach ($config in $configs) {
        if (Test-Path $config) {
            $dest = Join-Path $backupDir (Split-Path $config -Leaf)
            Copy-Item $config $dest -Force
            Write-Log "Backed up: $(Split-Path $config -Leaf)" "SUCCESS"
        }
    }

    # Backup database
    try {
        $dbBackup = Join-Path $backupDir "eq12_sportsbook_backup.sql"
        & "$XAMPP_ROOT\mysql\bin\mysqldump.exe" -uroot -pEQ12_secure_2025! --single-transaction eq12_sportsbook > $dbBackup
        Write-Log "Database backup created" "SUCCESS"
    } catch {
        Write-Log "Database backup failed" "ERROR"
    }

    Write-Log "Backup completed: $backupDir" "SUCCESS"
    return $backupDir
}

function Deploy-Production {
    Write-Log "Starting production deployment..." "INFO"

    # Create backup first
    $backupPath = Backup-Production

    # Stop services
    Write-Log "Stopping services..." "INFO"
    Get-Process -Name "httpd" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "mysqld" -ErrorAction SilentlyContinue | Stop-Process -Force
    pm2 stop all | Out-Null

    # Deploy configurations
    Write-Log "Deploying configurations..." "INFO"

    # Ensure all directories exist
    $directories = @(
        "$XAMPP_ROOT\htdocs",
        "$EQ12_ROOT\node",
        "$EQ12_ROOT\logs",
        "$EQ12_ROOT\data"
    )

    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Log "Created directory: $dir" "INFO"
        }
    }

    # Set permissions (Windows equivalent)
    try {
        # Grant full control to current user for EQ12 directory
        icacls $EQ12_ROOT /grant "${env:USERNAME}:(OI)(CI)F" /T | Out-Null
        icacls "$XAMPP_ROOT\htdocs" /grant "${env:USERNAME}:(OI)(CI)F" /T | Out-Null
        Write-Log "Permissions updated" "SUCCESS"
    } catch {
        Write-Log "Permission update failed" "WARNING"
    }

    # Start services
    Write-Log "Starting services..." "INFO"
    Start-Process "$XAMPP_ROOT\apache_start.bat" -WindowStyle Hidden
    Start-Process "$XAMPP_ROOT\mysql_start.bat" -WindowStyle Hidden

    Start-Sleep 5

    # Start Node.js services
    Set-Location "$EQ12_ROOT\node"
    pm2 start ecosystem.config.js | Out-Null

    # Verify deployment
    $verification = Test-Deployment

    if ($verification) {
        Write-Log "Production deployment completed successfully!" "SUCCESS"
    } else {
        Write-Log "Deployment verification failed!" "ERROR"
    }

    return $verification
}

function Test-Deployment {
    Write-Log "Verifying deployment..." "INFO"

    $tests = @()

    # Test Apache
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            $tests += @{ Name = "Apache/PHP"; Status = "PASS" }
        } else {
            $tests += @{ Name = "Apache/PHP"; Status = "FAIL" }
        }
    } catch {
        $tests += @{ Name = "Apache/PHP"; Status = "FAIL" }
    }

    # Test Node.js
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            $tests += @{ Name = "Node.js"; Status = "PASS" }
        } else {
            $tests += @{ Name = "Node.js"; Status = "FAIL" }
        }
    } catch {
        $tests += @{ Name = "Node.js"; Status = "FAIL" }
    }

    # Test MySQL
    try {
        & "$XAMPP_ROOT\mysql\bin\mysql.exe" -uroot -pEQ12_secure_2025! -e "SELECT 1;" 2>$null
        $tests += @{ Name = "MySQL"; Status = "PASS" }
    } catch {
        $tests += @{ Name = "MySQL"; Status = "FAIL" }
    }

    # Test PM2
    try {
        $pm2Status = pm2 status | Out-String
        if ($pm2Status -match "online") {
            $tests += @{ Name = "PM2"; Status = "PASS" }
        } else {
            $tests += @{ Name = "PM2"; Status = "FAIL" }
        }
    } catch {
        $tests += @{ Name = "PM2"; Status = "FAIL" }
    }

    # Report results
    Write-Log "Deployment Verification Results:" "INFO"
    $passed = 0
    foreach ($test in $tests) {
        Write-Log "  $($test.Name): $($test.Status)" "INFO"
        if ($test.Status -eq "PASS") { $passed++ }
    }

    $success = ($passed -eq $tests.Count)
    Write-Log "Overall: $passed/$($tests.Count) tests passed" $(if ($success) { "SUCCESS" } else { "ERROR" })

    return $success
}

function Show-ProductionStatus {
    Write-Log "EQ12 Production Status Report" "INFO"
    Write-Log "=" * 50 "INFO"

    # Service status
    $apache = Get-Process -Name "httpd" -ErrorAction SilentlyContinue
    $mysql = Get-Process -Name "mysqld" -ErrorAction SilentlyContinue

    Write-Log "Services:" "INFO"
    Write-Log "  Apache: $(if ($apache) { 'RUNNING' } else { 'STOPPED' })" "INFO"
    Write-Log "  MySQL: $(if ($mysql) { 'RUNNING' } else { 'STOPPED' })" "INFO"

    # PM2 status
    try {
        $pm2List = pm2 jlist | ConvertFrom-Json
        Write-Log "  PM2 Processes: $($pm2List.Count)" "INFO"
        foreach ($proc in $pm2List) {
            Write-Log "    $($proc.name): $($proc.pm2_env.status)" "INFO"
        }
    } catch {
        Write-Log "  PM2: Not available" "WARNING"
    }

    # Scheduled tasks
    $tasks = @("EQ12_OddsIngestion", "EQ12_AIOptimization", "EQ12_HealthMonitor", "EQ12_LogCleanup")
    Write-Log "Scheduled Tasks:" "INFO"
    foreach ($taskName in $tasks) {
        try {
            $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
            if ($task) {
                Write-Log "  $taskName - $($task.State)" "INFO"
            } else {
                Write-Log "  $taskName - NOT FOUND" "WARNING"
            }
        } catch {
            Write-Log "  $taskName - ERROR" "ERROR"
        }
    }

    # Disk space
    $drive = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
    $freeGB = [math]::Round($drive.FreeSpace / 1GB, 2)
    $totalGB = [math]::Round($drive.Size / 1GB, 2)
    Write-Log "Disk Space (C) - $freeGB GB free of $totalGB GB total" "INFO"

    # Recent activity
    $recentLogs = Get-ChildItem "$EQ12_ROOT\logs\*.log" | Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-1) }
    Write-Log "Recent Activity: $($recentLogs.Count) log files updated in last hour" "INFO"
}

# Main execution
switch ($true) {
    $Deploy {
        Deploy-Production
    }

    $Backup {
        Backup-Production
    }

    $Rollback {
        Write-Log "Manual rollback required - restore from backup directory" "WARNING"
        Write-Log "Backup location: $BACKUP_ROOT" "INFO"
    }

    $Status {
        Show-ProductionStatus
    }

    default {
        Write-Log "EQ12 Production Deployment Manager" "INFO"
        Write-Host "Usage:" -ForegroundColor White
        Write-Host "  -Deploy    Deploy to production" -ForegroundColor Yellow
        Write-Host "  -Backup    Create production backup" -ForegroundColor Yellow
        Write-Host "  -Rollback  Show rollback instructions" -ForegroundColor Yellow
        Write-Host "  -Status    Show production status" -ForegroundColor Yellow
        Write-Host "" -ForegroundColor White
        Write-Host "Example: .\eq12_production_deploy.ps1 -Status" -ForegroundColor Cyan
    }
}
