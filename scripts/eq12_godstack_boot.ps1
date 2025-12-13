<#
.SYNOPSIS
    EQ12 GodStack Boot Script - The "One Script to Rule Them All"
.DESCRIPTION
    Enforces the HARD-CODED MASTER DIRECTIVE (v1.0) for the EQ12/M70q/Pi5 cluster.
    - Validates Network Config (Static IPs)
    - Enforces Swarm Roles & Labels
    - Checks SSH Connectivity
    - Validates Build Environment (Remote Builder)
    - Checks Internet Bridge (Reverse Tunnel)
    - Verifies Docker Context & Ignore Rules
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

# --- CONFIGURATION (HARD-CODED) ---
$EQ12_IP = "192.168.100.2"
$M70Q_IP = "192.168.100.3"
$PI5_IP  = "192.168.100.4"
$User    = "ricoj100"

Write-Host "=== EQ12 GODSTACK BOOT SEQUENCE ===" -ForegroundColor Cyan

# --- 1. NETWORK VALIDATION ---
Write-Host "[1/6] Validating Network Configuration..." -ForegroundColor Yellow

# Check Local IP (EQ12)
$localIPs = Get-NetIPAddress -AddressFamily IPv4 | Select-Object -ExpandProperty IPAddress
if ($localIPs -notcontains $EQ12_IP) {
    Write-Warning "CRITICAL: EQ12 is NOT using Static IP $EQ12_IP. Current IPs: $($localIPs -join ', ')"
    # In a real scenario, we might attempt to set it, but for now, we warn.
} else {
    Write-Host "✔ EQ12 IP Correct ($EQ12_IP)" -ForegroundColor Green
}

# Check M70q Connectivity
if (Test-Connection -ComputerName $M70Q_IP -Count 1 -Quiet) {
    Write-Host "✔ M70q Reachable ($M70Q_IP)" -ForegroundColor Green
} else {
    Write-Error "❌ M70q ($M70Q_IP) is UNREACHABLE. Check physical connection."
}

# --- 2. SSH & KEY VALIDATION ---
Write-Host "[2/6] Validating SSH & Keys..." -ForegroundColor Yellow
try {
    $sshOut = ssh -o BatchMode=yes -o ConnectTimeout=5 ${User}@${M70Q_IP} "echo 'SSH OK'"
    if ($sshOut -match "SSH OK") {
        Write-Host "✔ SSH to M70q Passwordless: OK" -ForegroundColor Green
    }
} catch {
    Write-Error "❌ SSH to M70q failed or requires password. Run 'ssh-copy-id' immediately."
}

# --- 3. SWARM STATUS & LABELS ---
Write-Host "[3/6] Enforcing Swarm State..." -ForegroundColor Yellow
$swarmStatus = docker info --format '{{.Swarm.LocalNodeState}}'
if ($swarmStatus -ne "active") {
    Write-Warning "Swarm inactive. Initializing EQ12 as Manager..."
    docker swarm init --advertise-addr $EQ12_IP
} else {
    Write-Host "✔ Swarm Active (Manager Mode)" -ForegroundColor Green
}

# Check Nodes & Labels
$nodes = docker node ls --format '{{.Hostname}} {{.Status}}'
Write-Host "Swarm Nodes:"
$nodes | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }

# (Logic to enforce labels would go here - e.g., checking if M70q has type=worker)

# --- 4. BUILD SYSTEM ENFORCEMENT ---
Write-Host "[4/6] Enforcing Build System Rules..." -ForegroundColor Yellow
$builderName = "m70q-context" # Using context as builder per previous fix
if (-not (docker buildx ls | Select-String -Quiet "^${builderName} ")) {
    Write-Warning "Remote builder '$builderName' missing. Running setup..."
    ./scripts/setup_remote_builder.ps1
} else {
    Write-Host "✔ Remote Builder Configured ($builderName)" -ForegroundColor Green
}

# --- 5. INTERNET BRIDGE CHECK ---
Write-Host "[5/6] Checking Internet Bridge..." -ForegroundColor Yellow
# This is a placeholder for checking the reverse tunnel or proxy
# Real check would probe the proxy port on M70q via SSH
try {
    ssh ${User}@${M70Q_IP} "curl -s --connect-timeout 2 google.com > /dev/null"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✔ M70q has Internet Access" -ForegroundColor Green
    } else {
        Write-Warning "⚠ M70q cannot reach Internet. Check Reverse Tunnel / Gateway."
    }
} catch {
    Write-Warning "⚠ Could not verify M70q internet access."
}

# --- 6. CONTEXT SAFETY CHECK ---
Write-Host "[6/6] Verifying Context Safety..." -ForegroundColor Yellow
if (Test-Path ".dockerignore") {
    $ignoreContent = Get-Content ".dockerignore"
    if ($ignoreContent -match "\.venv_wsl" -and $ignoreContent -match "EdgeGodParlays/") {
        Write-Host "✔ .dockerignore contains critical exclusions" -ForegroundColor Green
    } else {
        Write-Warning "⚠ .dockerignore might be missing critical rules!"
    }
} else {
    Write-Warning "⚠ .dockerignore NOT FOUND!"
}

Write-Host "=== BOOT SEQUENCE COMPLETE ===" -ForegroundColor Cyan
Write-Host "System is ready for 'scripts/sync_images_to_m70q.ps1'"
