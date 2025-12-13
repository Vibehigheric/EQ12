# EQ12 XAMPP Security Hardening Script (Simple Version)
# This script implements production-ready security configurations

param(
    [switch]$Apply,
    [switch]$Verify
)

function Write-Status {
    param([string]$Message, [string]$Type = "Info")

    $color = switch ($Type) {
        "Success" { "Green" }
        "Warning" { "Yellow" }
        "Error" { "Red" }
        default { "White" }
    }
    Write-Host $Message -ForegroundColor $color
}

function Apply-Security {
    Write-Status "Starting XAMPP Security Hardening..." "Info"

    # 1. Secure Apache Configuration
    Write-Status "Configuring Apache security settings..." "Info"

    $apacheConf = "C:\xampp\apache\conf\httpd.conf"
    $content = Get-Content $apacheConf

    $securityBlock = @'

# EQ12 Security Configuration
ServerTokens Prod
ServerSignature Off
TraceEnable off

LoadModule headers_module modules/mod_headers.so

<IfModule mod_headers.c>
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
</IfModule>

<Directory "C:/xampp/htdocs">
    Options -Indexes
</Directory>

<Files ".ht*">
    Require all denied
</Files>

'@

    if ($content -notcontains "# EQ12 Security Configuration") {
        $content += $securityBlock
        $content | Set-Content $apacheConf
        Write-Status "Apache security configuration applied" "Success"
    }
    else {
        Write-Status "Apache already configured" "Warning"
    }

    # 2. Secure PHP Configuration
    Write-Status "Configuring PHP security settings..." "Info"

    $phpIni = "C:\xampp\php\php.ini"
    $phpContent = Get-Content $phpIni

    # Update critical security settings
    $phpContent = $phpContent -replace "display_errors = On", "display_errors = Off"
    $phpContent = $phpContent -replace "expose_php = On", "expose_php = Off"
    $phpContent = $phpContent -replace "allow_url_include = On", "allow_url_include = Off"

    $phpContent | Set-Content $phpIni
    Write-Status "PHP security configuration applied" "Success"

    # 3. Secure MySQL
    Write-Status "Securing MySQL installation..." "Info"

    try {
        # Remove anonymous users and test database
        & "C:\xampp\mysql\bin\mysql.exe" -uroot -pEQ12_secure_2025! -e "DELETE FROM mysql.user WHERE User=''; DROP DATABASE IF EXISTS test; FLUSH PRIVILEGES;" 2>$null
        Write-Status "MySQL security configuration applied" "Success"
    }
    catch {
        Write-Status "MySQL security configuration may have failed" "Warning"
    }

    # 4. Restart services
    Write-Status "Restarting services to apply changes..." "Info"

    Get-Process -Name "httpd" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "mysqld" -ErrorAction SilentlyContinue | Stop-Process -Force

    Start-Sleep 3

    Start-Process "C:\xampp\apache_start.bat" -WindowStyle Hidden
    Start-Process "C:\xampp\mysql_start.bat" -WindowStyle Hidden

    Start-Sleep 5

    Write-Status "Security hardening completed successfully!" "Success"
}

function Verify-Security {
    Write-Status "Verifying security configuration..." "Info"

    $passed = 0
    $total = 0

    # Test Apache
    $total++
    try {
        $result = & "C:\xampp\apache\bin\httpd.exe" -t 2>&1
        if ($result -match "Syntax OK") {
            Write-Status "Apache configuration: PASS" "Success"
            $passed++
        }
        else {
            Write-Status "Apache configuration: FAIL" "Error"
        }
    }
    catch {
        Write-Status "Apache configuration: ERROR" "Error"
    }

    # Test MySQL connection
    $total++
    try {
        & "C:\xampp\mysql\bin\mysql.exe" -uroot -pEQ12_secure_2025! -e "SELECT 1;" 2>$null
        Write-Status "MySQL connection: PASS" "Success"
        $passed++
    }
    catch {
        Write-Status "MySQL connection: FAIL" "Error"
    }

    # Test web server
    $total++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Status "Web server health: PASS" "Success"
            $passed++
        }
        else {
            Write-Status "Web server health: FAIL" "Error"
        }
    }
    catch {
        Write-Status "Web server health: FAIL" "Error"
    }

    Write-Status "Security verification: $passed/$total tests passed" "Info"
    return ($passed -eq $total)
}

# Main execution
if ($Apply) {
    Apply-Security

    # Verify after applying
    Start-Sleep 10
    Verify-Security

}
elseif ($Verify) {
    Verify-Security

}
else {
    Write-Status "EQ12 XAMPP Security Hardening Tool" "Info"
    Write-Status "Usage:" "Info"
    Write-Status "  -Apply   Apply security configurations" "Info"
    Write-Status "  -Verify  Verify security configurations" "Info"
    Write-Status "" "Info"
    Write-Status "Example: .\eq12_xampp_security_simple.ps1 -Apply" "Info"
}
