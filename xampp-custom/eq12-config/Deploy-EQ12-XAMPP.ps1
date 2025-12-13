# EQ12 XAMPP Deployment Script
# Deploys EQ12-specific XAMPP configuration for betting platform

param(
    [Parameter(Mandatory = $false)]
    [string]$XamppPath = "C:\\xampp",

    [Parameter(Mandatory = $false)]
    [string]$EQ12Root = "C:\\EQ12",

    [switch]$Backup
)

Write-Host "EQ12 XAMPP Deployment Starting..." -ForegroundColor Green

# Backup existing configuration if requested
if ($Backup) {
    $BackupDir = "$EQ12Root\\logs\\xampp_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -Path $BackupDir -ItemType Directory -Force

    Write-Host "Backing up existing XAMPP configuration..." -ForegroundColor Yellow

    # Backup key files
    $FilesToBackup = @(
        "$XamppPath\\php\\php.ini",
        "$XamppPath\\apache\\conf\\httpd.conf",
        "$XamppPath\\apache\\conf\\extra\\httpd-vhosts.conf",
        "$XamppPath\\mysql\\bin\\my.ini"
    )

    foreach ($File in $FilesToBackup) {
        if (Test-Path $File) {
            $BackupFile = Join-Path $BackupDir (Split-Path $File -Leaf)
            Copy-Item $File $BackupFile
            Write-Host "Backed up: $(Split-Path $File -Leaf)" -ForegroundColor Gray
        }
    }
}

# Deploy EQ12 configurations
Write-Host "Deploying EQ12 XAMPP configurations..." -ForegroundColor Cyan

# PHP Configuration
$PhpIni = "$XamppPath\\php\\php.ini"
if (Test-Path $PhpIni) {
    Write-Host "Updating PHP configuration..." -ForegroundColor Blue

    # Add EQ12-specific PHP settings
    $EQ12PhpSettings = @"

; EQ12 Betting Platform Configuration
memory_limit = 512M
max_execution_time = 300
upload_max_filesize = 100M
post_max_size = 100M
date.timezone = UTC
log_errors = On
display_errors = Off
error_log = C:/EQ12/logs/php_errors.log

; EQ12 Required Extensions
extension=curl
extension=json
extension=mysqli
extension=pdo_mysql
extension=openssl
extension=bcmath
extension=gd
extension=zip
extension=xml
"@

    Add-Content -Path $PhpIni -Value $EQ12PhpSettings
    Write-Host "PHP configuration updated" -ForegroundColor Green
}

# Apache Virtual Hosts
$VhostsConf = "$XamppPath\\apache\\conf\\extra\\httpd-vhosts.conf"
if (Test-Path $VhostsConf) {
    Write-Host "Adding EQ12 virtual hosts..." -ForegroundColor Blue

    $EQ12VirtualHosts = @"

# EQ12 Betting Platform Virtual Hosts
<VirtualHost *:80>
    ServerName eq12-betting.local
    DocumentRoot "C:/EQ12/dashboard"
    DirectoryIndex index.php index.html
    ErrorLog "C:/EQ12/logs/apache_eq12_error.log"
    CustomLog "C:/EQ12/logs/apache_eq12_access.log" common

    <Directory "C:/EQ12/dashboard">
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>

<VirtualHost *:80>
    ServerName eq12-api.local
    DocumentRoot "C:/EQ12/api"
    DirectoryIndex index.php
    ErrorLog "C:/EQ12/logs/apache_api_error.log"
    CustomLog "C:/EQ12/logs/apache_api_access.log" common

    <Directory "C:/EQ12/api">
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
"@

    Add-Content -Path $VhostsConf -Value $EQ12VirtualHosts
    Write-Host "Virtual hosts configured" -ForegroundColor Green
}

# Update hosts file
Write-Host "Updating Windows hosts file..." -ForegroundColor Blue
$HostsFile = "$env:SystemRoot\\System32\\drivers\\etc\\hosts"

$EQ12Hosts = @"

# EQ12 Betting Platform Local Hosts
127.0.0.1    eq12-betting.local
127.0.0.1    eq12-api.local
"@

# Check if EQ12 hosts already exist
$HostsContent = Get-Content $HostsFile -Raw
if ($HostsContent -notmatch "eq12-betting.local") {
    Add-Content -Path $HostsFile -Value $EQ12Hosts
    Write-Host "Hosts file updated" -ForegroundColor Green
}
else {
    Write-Host "EQ12 hosts already configured" -ForegroundColor Gray
}

Write-Host "EQ12 XAMPP Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Restart XAMPP services (Apache, MySQL)" -ForegroundColor White
Write-Host "2. Access EQ12 Betting Platform: http://eq12-betting.local" -ForegroundColor White
Write-Host "3. Access EQ12 API: http://eq12-api.local" -ForegroundColor White
Write-Host "4. Run EQ12 platform integration tests" -ForegroundColor White
