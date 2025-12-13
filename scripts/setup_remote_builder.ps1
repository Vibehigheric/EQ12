<#
.SYNOPSIS
    Sets up a Docker Remote Context and Buildx Builder for the M70q node.
.DESCRIPTION
    This script:
    1. Creates a Docker Context 'm70q-context' pointing to the M70q SSH socket.
    2. Creates a Buildx Builder 'eq12-remote-builder' using the 'docker' driver.
    This allows builds to run directly on the M70q's Docker daemon, bypassing the Windows Docker Desktop VM
    and storing images directly on the M70q.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$TargetIP = "192.168.100.3"
$User = "ricoj100"
$ContextName = "m70q-context"
$BuilderName = "eq12-remote-builder"

Write-Host "=== Setting up Remote Builder for M70q ($TargetIP) ===" -ForegroundColor Cyan

# 1. Check SSH Connection
Write-Host "Testing SSH connection..." -ForegroundColor Yellow
try {
    $sshTest = ssh -o BatchMode=yes -o ConnectTimeout=5 ${User}@${TargetIP} "docker --version"
    Write-Host "SSH Connection Successful: $sshTest" -ForegroundColor Green
}
catch {
    Write-Error "Could not connect to ${User}@${TargetIP} via SSH. Please ensure SSH keys are set up and the host is reachable."
}

# 2. Create Docker Context
if (docker context ls -q | Select-String -Quiet "^${ContextName}$") {
    Write-Host "Context '$ContextName' already exists. Updating..."
    docker context update $ContextName --docker "host=ssh://${User}@${TargetIP}"
}
else {
    Write-Host "Creating context '$ContextName'..."
    docker context create $ContextName --docker "host=ssh://${User}@${TargetIP}" --description "Remote Docker Engine on M70q"
}

# 3. Create Buildx Builder
# We use the 'docker' driver to build directly into the remote daemon's image store.
# This avoids the need for 'docker load' or a registry.
if (docker buildx ls | Select-String -Quiet "^${BuilderName} ") {
    Write-Host "Builder '$BuilderName' already exists. Removing to ensure clean state..."
    docker buildx rm $BuilderName
}

Write-Host "Creating builder '$BuilderName'..."
# The 'docker' driver uses a context name as the endpoint.
# We must pass the context name as the positional argument, not --use flag alone.
docker buildx create --name $BuilderName --driver docker --use $ContextName

Write-Host "Bootstrapping builder..."
docker buildx inspect --bootstrap

Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host "You can now build directly on M70q using: docker buildx build --builder $BuilderName ..."
