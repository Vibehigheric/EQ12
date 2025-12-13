param(
    [string]$ManagerIP = "192.168.100.3",
    [string]$User = "ricoj100",
    [string]$SourcePath = "C:\EQ12_BROKEN_20251122_210342",
    [string]$RemotePath = "~/eq12_build_context"
)

$ErrorActionPreference = "Stop"

Write-Host "=== [EQ12] Starting Remote Build on Manager ($ManagerIP) ===" -ForegroundColor Cyan

# 1. Sync Source Code
Write-Host "[1/3] Syncing source code to $ManagerIP..." -ForegroundColor Yellow

# Create remote directory and clean it
ssh -o BatchMode=yes "$User@$ManagerIP" "rm -rf $RemotePath && mkdir -p $RemotePath"

# Create a temporary tarball locally
$tarFile = "$env:TEMP\eq12_source.tar.gz"
Write-Host "    Creating local tarball: $tarFile" -ForegroundColor Gray

# Use tar to archive, excluding heavy/unnecessary folders
# Note: Windows tar supports --exclude
tar -czf "$tarFile" --exclude ".git" --exclude "__pycache__" --exclude ".venv" --exclude "logs" --exclude "reports" --exclude "workspace" --exclude "node_modules" -C "$SourcePath" .

# SCP the tarball
Write-Host "    Uploading tarball..." -ForegroundColor Gray
scp -o BatchMode=yes -q "$tarFile" "$User@$ManagerIP`:$RemotePath/source.tar.gz"

# Extract on remote
Write-Host "    Extracting on remote..." -ForegroundColor Gray
ssh -o BatchMode=yes "$User@$ManagerIP" "tar -xzf $RemotePath/source.tar.gz -C $RemotePath && rm $RemotePath/source.tar.gz"

# Cleanup local tarball
Remove-Item "$tarFile" -ErrorAction SilentlyContinue


# 2. Build Images Remotely
Write-Host "[2/3] Building Docker images on Manager..." -ForegroundColor Yellow
$buildCmd = "cd $RemotePath && docker build -t eq12/core:latest ."
ssh -o BatchMode=yes "$User@$ManagerIP" $buildCmd

if ($LASTEXITCODE -ne 0) {
    Write-Error "Remote build failed."
    exit 1
}

# 3. Deploy Stack
Write-Host "[3/3] Deploying Stack on Manager..." -ForegroundColor Yellow
$deployCmd = "cd $RemotePath && docker stack deploy -c eq12_stack.yml eq12"
ssh -o BatchMode=yes "$User@$ManagerIP" $deployCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "=== [EQ12] Remote Build & Deploy Complete! ===" -ForegroundColor Green
}
else {
    Write-Error "Remote deploy failed."
    exit 1
}
