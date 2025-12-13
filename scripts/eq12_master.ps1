<#
.SYNOPSIS
Master helper for the EQ12 network control-plane node.

.DESCRIPTION
Collects diagnostics (network, Docker, SSH) for the local host, guarantees the
Windows OpenSSH service + firewall are ready, and reports on every node listed
in `scripts/swarm-admin/nodes.json`.

.PARAMETER NodesJson
Path to the JSON inventory describing the swarm nodes.
#>
param(
    [Parameter(Mandatory = $false)]
    [string]$NodesJson = "$PSScriptRoot\swarm-admin\nodes.json"
)

$ErrorActionPreference = 'Stop'

function Get-LocalHostInfo {
    $dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
    $dockerStatus = if ($dockerCmd) { 'Installed' } else { 'Missing' }

    [PSCustomObject]@{
        ComputerName = $env:COMPUTERNAME
        User         = $env:USERNAME
        OS           = (Get-CimInstance Win32_OperatingSystem).Caption
        IPs          = (Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp | Where-Object { $_.IPAddress -notlike '169.*' }).IPAddress
        Gateway      = (Get-NetIPConfiguration | Select-Object -First 1).Ipv4DefaultGateway.NextHop
        TimeZone     = (Get-TimeZone).Id
        DockerStatus = $dockerStatus
    }
}

function Ensure-AdminPrivilege {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Warning "Administrator rights are recommended for full remediation; some steps may fail without elevation."
    }
}

function Ensure-SSHDService {
    $svc = Get-Service -Name sshd -ErrorAction SilentlyContinue
    if (-not $svc) {
        Write-Warning "OpenSSH Server is not installed. Install it from Optional Features under Settings."
        return $false
    }
    if ($svc.Status -ne 'Running') {
        Write-Output "Starting sshd service..."
        Start-Service sshd
        $svc.WaitForStatus('Running', '00:00:30') | Out-Null
    }
    $true
}

function Ensure-SSHFirewall {
    $ruleName = 'EQ12 Allow SSH'
    $rule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if (-not $rule) {
        New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22 -RemoteAddress 192.168.1.0/24 -Profile Any
        Write-Output "Created firewall rule '$ruleName' for 192.168.1.0/24"
    }
    else {
        Write-Output "Existing firewall rule '$ruleName' is already allowing port 22."
    }
}

function Test-NodeConnectivity {
    param(
        [Parameter(Mandatory = $true)]
        [PSCustomObject]$Node
    )
    $reach = Test-Connection -Quiet -Count 2 -ComputerName $Node.ip
    $ssh = $false
    if ($reach) {
        $sshResult = & ssh -o BatchMode=yes -o ConnectTimeout=5 "$($Node.user)@$($Node.ip)" 'echo ok' 2>$null
        $ssh = $LASTEXITCODE -eq 0 -or ($sshResult -match 'ok')
    }
    [PSCustomObject]@{
        Name      = $Node.name
        IP        = $Node.ip
        Role      = $Node.role
        Reachable = $reach
        SSH       = $ssh
    }
}

function Get-Nodes {
    if (Test-Path $NodesJson) {
        Get-Content -Raw $NodesJson | ConvertFrom-Json
    }
    else {
        Write-Warning "Nodes inventory not found at $NodesJson"
        @()
    }
}

function Show-Report {
    Ensure-AdminPrivilege
    $local = Get-LocalHostInfo
    Write-Host "\n== Local Host Snapshot ==" -ForegroundColor Cyan
    $local | Format-List

    if (Ensure-SSHDService) {
        Ensure-SSHFirewall
    }

    Write-Host "\n== Docker Status ==" -ForegroundColor Cyan
    if ($local.DockerStatus -eq 'Installed') {
        docker version | Select-Object -First 1
    }
    else {
        Write-Warning 'Docker is not in PATH; install Docker Desktop or Docker Engine before running swarm upgrades.'
    }

    Write-Host "\n== Node Reachability ==" -ForegroundColor Cyan
    $nodes = Get-Nodes
    foreach ($node in $nodes) {
        $status = Test-NodeConnectivity -Node $node
        $status | Format-Table -AutoSize
    }

    $guidance = "Use wsl -e bash -lc 'cd ~/swarm-admin && ./scan_and_upgrade_swarm.sh' after every node has SSH + Docker available."
    Write-Host "`n$guidance" -ForegroundColor Green
}

Show-Report
