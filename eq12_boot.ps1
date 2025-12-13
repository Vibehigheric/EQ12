param(
    [switch]$RebuildImages  # optional flag if you want to rebuild/sync images
)

$ErrorActionPreference = "Stop"

Write-Host "=== [EQ12 BOOT] Starting GodStack Boot Pipeline ===" -ForegroundColor Cyan

# 1) Ensure Docker Desktop is running and Linux engine is reachable
function Wait-Docker {
    Write-Host "[1/7] Checking Docker Desktop..." -ForegroundColor Yellow

    $dockerOk = $false
    for ($i = 0; $i -lt 30; $i++) {
        try {
            docker info --format '{{.ServerVersion}}' | Out-Null
            $dockerOk = $true
            break
        } catch {
            Start-Sleep -Seconds 2
        }
    }

    if (-not $dockerOk) {
        Write-Host "[1/7] Docker not responding. Attempting to start Docker Desktop..." -ForegroundColor Yellow
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue

        for ($i = 0; $i -lt 60; $i++) {
            try {
                docker info --format '{{.ServerVersion}}' | Out-Null
                $dockerOk = $true
                break
            } catch {
                Start-Sleep -Seconds 2
            }
        }
    }

    if (-not $dockerOk) {
        Write-Error "Docker Desktop failed to start. Fix this before continuing."
        exit 1
    }

    Write-Host "[1/7] Docker Desktop is online." -ForegroundColor Green
}

# 2) Ensure we are using desktop-linux context
function Ensure-DockerContext {
    Write-Host "[2/7] Ensuring docker context is 'desktop-linux'..." -ForegroundColor Yellow
    $ctx = docker context ls --format '{{.Name}} {{if .Current}}*{{end}}' | Select-String "\*"

    if ($ctx -notmatch "desktop-linux") {
        Write-Host "[2/7] Switching context to 'desktop-linux'..." -ForegroundColor Yellow
        docker context use desktop-linux | Out-Null
    }

    Write-Host "[2/7] docker context now: desktop-linux" -ForegroundColor Green
}

# 3) Ensure Buildx builder exists
function Ensure-Buildx {
    Write-Host "[3/7] Ensuring buildx builder 'eq12-builder' exists..." -ForegroundColor Yellow
    $builder = docker buildx ls | Select-String "eq12-builder"

    if (-not $builder) {
        Write-Host "Creating buildx builder 'eq12-builder'..." -ForegroundColor Yellow
        docker buildx create --name eq12-builder --driver docker-container --use desktop-linux | Out-Null
        docker buildx inspect eq12-builder --bootstrap | Out-Null
    } else {
        docker buildx use eq12-builder | Out-Null
    }

    Write-Host "[3/7] buildx builder 'eq12-builder' is ready." -ForegroundColor Green
}

# 4) Ping workers & verify SSH
function Test-Node {
    param(
        [string]$Name,
        [string]$IP
    )

    Write-Host "[4/7] Checking node $Name ($IP)..." -ForegroundColor Yellow

    if (-not (Test-Connection -ComputerName $IP -Count 1 -Quiet)) {
        Write-Warning "[4/7] Node $Name ($IP) not pingable. It may be off. GodStack can still run, but reduced."
        return
    }

    $sshTest = & ssh -o BatchMode=yes -o ConnectTimeout=5 "ricoj100@$IP" "echo OK" 2>$null
    if ($sshTest -ne "OK") {
        Write-Warning "[4/7] SSH to $Name ($IP) is not passwordless. Fix keys if you want full automation."
    } else {
        Write-Host "[4/7] Node $Name is reachable via SSH." -ForegroundColor Green
    }
}

function Check-Nodes {
    Test-Node -Name "M70q-Worker-Ubuntu" -IP "192.168.100.3"
    Test-Node -Name "Pi-Worker-01" -IP "192.168.1.80" # Management IP (Cluster IP: 192.168.100.1)
}

# 5) Ensure Swarm is initialized on EQ12
function Ensure-Swarm {
    Write-Host "[5/7] Checking Docker Swarm state..." -ForegroundColor Yellow
    $state = ""
    try {
        $state = docker info --format '{{.Swarm.LocalNodeState}}'
    } catch {
        Write-Error "Unable to query Docker info. Docker Desktop not healthy."
        exit 1
    }

    if ($state -eq "active") {
        Write-Host "[5/7] Swarm already active on EQ12." -ForegroundColor Green
        return
    }

    Write-Host "[5/7] Swarm inactive. Initializing..." -ForegroundColor Yellow
    docker swarm init --advertise-addr 192.168.100.2 | Out-Null
    Write-Host "[5/7] Swarm initialized on EQ12 as manager." -ForegroundColor Green
}

# 6) Optionally rebuild/sync images to M70q
function Rebuild-Images {
    Write-Host "[6/7] Rebuilding and syncing images to M70q (optional)..." -ForegroundColor Yellow
    & .\scripts\sync_images_to_m70q.ps1
}

# 7) Deploy Swarm stack
function Deploy-Stack {
    Write-Host "[7/7] Deploying Swarm stack 'eq12' to Manager (M70q)..." -ForegroundColor Yellow

    if (-not (Test-Path ".\eq12_stack.yml")) {
        Write-Error "eq12_stack.yml not found in current directory. Aborting."
        exit 1
    }

    # Copy stack file to Manager
    Write-Host "    Copying stack file to M70q..." -ForegroundColor Gray
    scp -o BatchMode=yes -q .\eq12_stack.yml ricoj100@192.168.100.3:~/eq12_stack.yml
    
    # Deploy on Manager
    Write-Host "    Executing deploy on M70q..." -ForegroundColor Gray
    ssh -o BatchMode=yes ricoj100@192.168.100.3 "docker stack deploy -c ~/eq12_stack.yml eq12"

    Write-Host "[7/7] Stack 'eq12' deployed on Manager. GodStack services starting up." -ForegroundColor Green
}

# ===== RUN PIPELINE =====

Set-Location "C:\EQ12_BROKEN_20251122_210342"

Wait-Docker
Ensure-DockerContext
Ensure-Buildx
Check-Nodes
Ensure-Swarm

if ($RebuildImages) {
    Rebuild-Images
}

Deploy-Stack

Write-Host "=== [EQ12 BOOT] GodStack boot sequence complete. ===" -ForegroundColor Cyan
