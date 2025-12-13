# EQ12 SourceForge Toolchain Installer
# Downloads and installs development tools from SourceForge

[CmdletBinding()]
param(
    [string]$ManifestPath = "configs\sourceforge_manifest.json",
    [switch]$SportsTools = $false,
    [switch]$DryRun = $false,
    [switch]$VerifyOnly = $false,
    [string]$ToolFilter = "*"
)

Write-Host "[SF-INSTALLER] EQ12 SourceForge Toolchain Installer" -ForegroundColor Cyan
Write-Host "=" * 60

# Load the manifest
if ($SportsTools) {
    $ManifestPath = "configs\sourceforge_sports.json"
    Write-Host "[INFO] Using sports betting tools manifest" -ForegroundColor Yellow
}

if (-not (Test-Path $ManifestPath)) {
    Write-Host "[ERROR] Manifest not found: $ManifestPath" -ForegroundColor Red
    exit 1
}

try {
    $manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
    Write-Host "[SUCCESS] Loaded manifest with $($manifest.tools.Count) tools" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to parse manifest: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Create destination directory
$destDir = $manifest.destination
if (-not (Test-Path $destDir) -and -not $DryRun) {
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    Write-Host "[CREATED] Destination directory: $destDir" -ForegroundColor Green
}

# Filter tools if specified
$tools = $manifest.tools | Where-Object { $_.name -like $ToolFilter }
Write-Host "[INFO] Processing $($tools.Count) tools matching filter: $ToolFilter" -ForegroundColor White

# Function to download from SourceForge
function Get-SourceForgeDownloadUrl {
    param($project, $fileHint)
    
    # This is a simplified approach - in reality you'd parse the SF API
    # For now, return template URLs that need manual verification
    $baseUrl = "https://sourceforge.net/projects/$project/files"
    
    switch ($project) {
        "xampp" { return "$baseUrl/XAMPP%20Windows/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe/download" }
        "heidisql" { return "$baseUrl/HeidiSQL_12.6.0.6765_Setup.exe/download" }
        "winscp" { return "$baseUrl/WinSCP/6.1.2/WinSCP-6.1.2-Setup.exe/download" }
        "winmerge" { return "$baseUrl/winmerge/2.16.34/WinMerge-2.16.34-Setup.exe/download" }
        "keepass" { return "$baseUrl/KeePass%202.x/2.54/KeePass-2.54-Setup.exe/download" }
        default { return "$baseUrl/latest/download" }
    }
}

# Process each tool
foreach ($tool in $tools) {
    Write-Host ""
    Write-Host "[TOOL] $($tool.name) - $($tool.why)" -ForegroundColor Magenta
    
    if ($VerifyOnly) {
        # Just check if tool is already installed
        $installed = $false
        
        switch ($tool.category) {
            "web-stack" { 
                $installed = Test-Path "C:\xampp\xampp-control.exe"
                if ($installed) { Write-Host "   [FOUND] XAMPP installed" -ForegroundColor Green }
            }
            "db" { 
                $installed = Test-Path "C:\Program Files\HeidiSQL\heidisql.exe"
                if ($installed) { Write-Host "   [FOUND] HeidiSQL installed" -ForegroundColor Green }
            }
            "devops" { 
                $installed = Test-Path "C:\Program Files (x86)\WinSCP\WinSCP.exe"
                if ($installed) { Write-Host "   [FOUND] WinSCP installed" -ForegroundColor Green }
            }
            "security" {
                if ($tool.name -eq "KeePass") {
                    $installed = Test-Path "C:\Program Files\KeePass Password Safe 2\KeePass.exe"
                    if ($installed) { Write-Host "   [FOUND] KeePass installed" -ForegroundColor Green }
                }
            }
        }
        
        if (-not $installed) {
            Write-Host "   [MISSING] $($tool.name) not found" -ForegroundColor Yellow
        }
        continue
    }
    
    # Get download URL
    $downloadUrl = Get-SourceForgeDownloadUrl $tool.project $tool.file_hint
    $fileName = Split-Path $downloadUrl -Leaf
    $localFile = Join-Path $destDir $fileName
    
    Write-Host "   [URL] $downloadUrl" -ForegroundColor White
    Write-Host "   [FILE] $localFile" -ForegroundColor White
    
    if ($DryRun) {
        Write-Host "   [DRY-RUN] Would download and install" -ForegroundColor Yellow
        continue
    }
    
    # Download file
    if (-not (Test-Path $localFile)) {
        Write-Host "   [DOWNLOAD] Starting..." -ForegroundColor Yellow
        try {
            Invoke-WebRequest -Uri $downloadUrl -OutFile $localFile -UseBasicParsing
            Write-Host "   [SUCCESS] Downloaded $fileName" -ForegroundColor Green
        } catch {
            Write-Host "   [ERROR] Download failed: $($_.Exception.Message)" -ForegroundColor Red
            continue
        }
    } else {
        Write-Host "   [CACHED] File already exists" -ForegroundColor Green
    }
    
    # Install
    if ($tool.install -eq "installer" -and $tool.silent_args) {
        Write-Host "   [INSTALL] Running silent installer..." -ForegroundColor Yellow
        try {
            $process = Start-Process -FilePath $localFile -ArgumentList $tool.silent_args -Wait -PassThru
            if ($process.ExitCode -eq 0) {
                Write-Host "   [SUCCESS] Installation completed" -ForegroundColor Green
            } else {
                Write-Host "   [WARNING] Installer exit code: $($process.ExitCode)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   [ERROR] Installation failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    } elseif ($tool.install -eq "portable" -or $tool.install -eq "installer-or-portable") {
        Write-Host "   [PORTABLE] File ready for manual extraction" -ForegroundColor Blue
    } else {
        Write-Host "   [MANUAL] Requires manual installation" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[SUCCESS] SourceForge toolchain processing complete!" -ForegroundColor Green
Write-Host ""
Write-Host "[TIPS] Next steps:" -ForegroundColor Cyan
Write-Host "   1. Verify installations with: .\scripts\eq12_sf_installer.ps1 -VerifyOnly" -ForegroundColor White
Write-Host "   2. Add tool paths to your PATH environment variable" -ForegroundColor White
Write-Host "   3. Configure tools for EQ12 integration" -ForegroundColor White