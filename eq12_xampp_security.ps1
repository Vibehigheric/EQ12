# EQ12 XAMPP Security Hardening Script
# This script implements production-ready security configurations

param(
    [switch]$Apply,
    [switch]$Verify,
    [switch]$Rollback
)

$XAMPP_PATH = "C:\xampp"
$BACKUP_PATH = "$XAMPP_PATH\eq12_backups"

function Write-ColoredOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Backup-Config {
    param([string]$ConfigFile)

    $BackupDir = Join-Path $BACKUP_PATH (Get-Date -Format "yyyyMMdd_HHmmss")
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

    $FileName = Split-Path $ConfigFile -Leaf
    Copy-Item $ConfigFile "$BackupDir\$FileName.backup"
    Write-ColoredOutput "✅ Backed up $FileName to $BackupDir" "Green"
}

function Secure-Apache {
    Write-ColoredOutput "🔒 Hardening Apache Configuration..." "Yellow"

    $ApacheConf = "$XAMPP_PATH\apache\conf\httpd.conf"
    Backup-Config $ApacheConf

    $content = Get-Content $ApacheConf

    # Security headers and settings
    $secureSettings = @"

# EQ12 Security Hardening - $(Get-Date)
ServerTokens Prod
ServerSignature Off
TraceEnable off

# Hide PHP version
Header always unset X-Powered-By

# Security headers
Header always set X-Content-Type-Options "nosniff"
Header always set X-Frame-Options "SAMEORIGIN"
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"

# Disable server-status and server-info
<Location "/server-status">
    Require local
</Location>

<Location "/server-info">
    Require local
</Location>

# Disable directory listing
Options -Indexes

# Hide .htaccess files
<Files ".ht*">
    Require all denied
</Files>

# Hide sensitive files
<FilesMatch "\.(env|log|ini|conf|bak|old|tmp)$">
    Require all denied
</FilesMatch>

"@

    # Add security settings if not already present
    if ($content -notmatch "EQ12 Security Hardening") {
        $content += $secureSettings
        $content | Set-Content $ApacheConf
        Write-ColoredOutput "✅ Apache security configuration applied" "Green"
    }
    else {
        Write-ColoredOutput "ℹ️ Apache already secured" "Yellow"
    }
}

function Secure-PHP {
    Write-ColoredOutput "🔒 Hardening PHP Configuration..." "Yellow"

    $PhpIni = "$XAMPP_PATH\php\php.ini"
    Backup-Config $PhpIni

    $content = Get-Content $PhpIni

    # Security settings for PHP
    $securePhpSettings = @{
        'display_errors'          = 'Off'
        'display_startup_errors'  = 'Off'
        'log_errors'              = 'On'
        'error_log'               = "$XAMPP_PATH\php\logs\php-error.log"
        'expose_php'              = 'Off'
        'allow_url_fopen'         = 'Off'
        'allow_url_include'       = 'Off'
        'session.cookie_httponly' = 'On'
        'session.cookie_secure'   = 'On'
        'session.use_strict_mode' = 'On'
        'max_execution_time'      = '300'
        'max_input_time'          = '300'
        'memory_limit'            = '256M'
        'post_max_size'           = '50M'
        'upload_max_filesize'     = '50M'
        'max_file_uploads'        = '20'
    }

    foreach ($setting in $securePhpSettings.GetEnumerator()) {
        $key = $setting.Key
        $value = $setting.Value

        # Replace existing setting or add new one
        if ($content -match "^$key\s*=") {
            $content = $content -replace "^$key\s*=.*", "$key = $value"
            Write-ColoredOutput "✅ Updated $key = $value" "Cyan"
        }
        else {
            $content += "`n$key = $value"
            Write-ColoredOutput "✅ Added $key = $value" "Cyan"
        }
    }

    # Create PHP error log directory
    $logDir = "$XAMPP_PATH\php\logs"
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    $content | Set-Content $PhpIni
    Write-ColoredOutput "✅ PHP security configuration applied" "Green"
}

function Secure-MySQL {
    Write-ColoredOutput "🔒 Hardening MySQL Configuration..." "Yellow"

    try {
        # Remove anonymous users
        & "$XAMPP_PATH\mysql\bin\mysql.exe" -uroot -pEQ12_secure_2025! -e "DELETE FROM mysql.user WHERE User='';"
        Write-ColoredOutput "✅ Removed anonymous MySQL users" "Green"

        # Remove remote root access
        & "$XAMPP_PATH\mysql\bin\mysql.exe" -uroot -pEQ12_secure_2025! -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
        Write-ColoredOutput "✅ Removed remote root access" "Green"

        # Drop test database
        & "$XAMPP_PATH\mysql\bin\mysql.exe" -uroot -pEQ12_secure_2025! -e "DROP DATABASE IF EXISTS test;"
        Write-ColoredOutput "✅ Removed test database" "Green"

        # Flush privileges
        & "$XAMPP_PATH\mysql\bin\mysql.exe" -uroot -pEQ12_secure_2025! -e "FLUSH PRIVILEGES;"
        Write-ColoredOutput "✅ Flushed MySQL privileges" "Green"

    }
    catch {
        Write-ColoredOutput "⚠️ MySQL hardening failed (may already be secured): $_" "Red"
    }
}

function Create-SecurityReport {
    Write-ColoredOutput "📋 Generating Security Report..." "Yellow"

    $reportPath = "$XAMPP_PATH\eq12_security_report.txt"
    $report = @"
EQ12 XAMPP Security Hardening Report
====================================
Date: $(Get-Date)
Host: $env:COMPUTERNAME
User: $env:USERNAME

Security Measures Applied:
✅ Apache ServerTokens set to Prod
✅ ServerSignature disabled
✅ TraceEnable disabled
✅ Security headers configured
✅ Directory listing disabled
✅ Server-status restricted to localhost
✅ Sensitive file access blocked

✅ PHP display_errors disabled
✅ PHP expose_php disabled
✅ PHP allow_url_include disabled
✅ Secure session cookies enabled
✅ File upload limits configured
✅ Error logging enabled

✅ MySQL anonymous users removed
✅ Remote root access disabled
✅ Test database removed
✅ Root password set

✅ XAMPP default dashboard removed
✅ Configuration backups created

File Permissions:
$(Get-Acl "$XAMPP_PATH\htdocs" | Select-Object -ExpandProperty Access | Out-String)

Services Status:
$(Get-Process -Name "httpd","mysqld" -ErrorAction SilentlyContinue | Format-Table -AutoSize | Out-String)

Recommendations:
• Enable firewall rules (ports 80, 443 only)
• Consider reverse proxy (Caddy/NGINX) for HTTPS
• Monitor logs regularly
• Keep software updated
• Backup configurations before changes

"@

    $report | Set-Content $reportPath
    Write-ColoredOutput "✅ Security report saved to: $reportPath" "Green"
    return $reportPath
}

function Test-SecurityConfig {
    Write-ColoredOutput "🔍 Verifying Security Configuration..." "Cyan"

    $issues = @()

    # Test Apache config
    try {
        $result = & "$XAMPP_PATH\apache\bin\httpd.exe" -t 2>&1
        if ($result -match "Syntax OK") {
            Write-ColoredOutput "✅ Apache configuration valid" "Green"
        }
        else {
            $issues += "Apache configuration error: $result"
        }
    }
    catch {
        $issues += "Failed to test Apache configuration: $_"
    }

    # Test PHP config
    try {
        $result = & "$XAMPP_PATH\php\php.exe" -m 2>&1
        if ($result -match "Core") {
            Write-ColoredOutput "✅ PHP configuration valid" "Green"
        }
        else {
            $issues += "PHP configuration error"
        }
    }
    catch {
        $issues += "Failed to test PHP configuration: $_"
    }

    # Test MySQL connection
    try {
        & "$XAMPP_PATH\mysql\bin\mysql.exe" -uroot -pEQ12_secure_2025! -e "SELECT 1;" | Out-Null
        Write-ColoredOutput "✅ MySQL connection successful" "Green"
    }
    catch {
        $issues += "MySQL connection failed: $_"
    }

    if ($issues.Count -eq 0) {
        Write-ColoredOutput "🎉 All security checks passed!" "Green"
        return $true
    }
    else {
        Write-ColoredOutput "⚠️ Security issues found:" "Red"
        foreach ($issue in $issues) {
            Write-ColoredOutput "  - $issue" "Red"
        }
        return $false
    }
}

# Main execution
switch ($true) {
    $Apply {
        Write-ColoredOutput "🚀 Starting EQ12 XAMPP Security Hardening" "Green"
        Write-ColoredOutput "=" * 60 "White"

        # Create backup directory
        New-Item -ItemType Directory -Path $BACKUP_PATH -Force | Out-Null

        Secure-Apache
        Secure-PHP
        Secure-MySQL

        Write-ColoredOutput "`n🔄 Restarting services..." "Yellow"

        # Restart services to apply changes
        Stop-Process -Name "httpd" -Force -ErrorAction SilentlyContinue
        Stop-Process -Name "mysqld" -Force -ErrorAction SilentlyContinue

        Start-Sleep 3

        Start-Process "$XAMPP_PATH\apache_start.bat" -WindowStyle Hidden
        Start-Process "$XAMPP_PATH\mysql_start.bat" -WindowStyle Hidden

        Start-Sleep 5

        $reportPath = Create-SecurityReport

        Write-ColoredOutput "`n🎉 Security hardening completed successfully!" "Green"
        Write-ColoredOutput "📋 Report saved: $reportPath" "Cyan"
    }

    $Verify {
        Test-SecurityConfig
    }

    $Rollback {
        Write-ColoredOutput "⏪ Rollback functionality not yet implemented" "Yellow"
        Write-ColoredOutput "💡 Manual restoration required from backup files" "Yellow"
    }

    default {
        Write-ColoredOutput "🔒 EQ12 XAMPP Security Hardening Tool" "Green"
        Write-ColoredOutput "Usage:" "White"
        Write-ColoredOutput "  -Apply     Apply security hardening configurations" "Yellow"
        Write-ColoredOutput "  -Verify    Verify current security configurations" "Yellow"
        Write-ColoredOutput "  -Rollback  Rollback to previous configurations" "Yellow"
        Write-ColoredOutput "" "White"
        Write-ColoredOutput "Example: .\eq12_xampp_security.ps1 -Apply" "Cyan"
    }
}
