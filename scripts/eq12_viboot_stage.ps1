<#
.SYNOPSIS
Stage the latest Macrium Reflect full backup into a VM with viBoot, run idempotent tests, collect logs, and tear down.

.DESCRIPTION
This script finds the latest full backup image in the configured backup directory, attempts to stage it via Macrium viBoot
(prefer Hyper-V, fallback to VirtualBox), waits for the VM to boot, runs configured test commands inside the VM, collects logs,
then shuts down and removes the VM. All actions are read-only with respect to backup images.

.PARAMETER ConfigPath
Path to configuration JSON (defaults: C:\EQ12\configs\viboot_config.json)
#>
[CmdletBinding()]
param(
    [string]$ConfigPath = 'C:\EQ12\configs\viboot_config.json'
)

function Write-JsonAndExit($obj) {
    $enc = $obj | ConvertTo-Json -Depth 5
    Write-Output $enc
    Exit 1
}

try {
    if (-not (Test-Path $ConfigPath)) {
        Write-JsonAndExit @{ ok = $false; error = "Config not found: $ConfigPath" }
    }
    $cfg = Get-Content -Raw -Path $ConfigPath | ConvertFrom-Json
    $backupDir = $cfg.backup_directory
    if (-not $backupDir) { Write-JsonAndExit @{ ok = $false; error = 'backup_directory missing in config' } }
    if (-not (Test-Path $backupDir)) { Write-JsonAndExit @{ ok = $false; error = "Backup directory not found: $backupDir" } }
} catch {
    Write-JsonAndExit @{ ok = $false; error = ("Failed to load config: {0}" -f $_.Exception.Message) }
}

# Find latest full image file (assume full images have .mrimg and contain 'full' in name or are the largest)
$images = Get-ChildItem -Path $backupDir -Filter *.mrimg -File -Recurse -ErrorAction SilentlyContinue
if (-not $images) {
    Write-JsonAndExit @{ ok = $false; error = "No .mrimg images found under $backupDir" }
}
# choose the most recently modified image as latest full
$latest = $images | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $latest) { Write-JsonAndExit @{ ok = $false; error = 'No backup image selected' } }

$latestPath = $latest.FullName
Write-Output "Selected image: $latestPath"

# Determine hypervisor availability
$hasHyperV = (Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -ErrorAction SilentlyContinue).State -eq 'Enabled'
$hasVBox = Get-Command -Name 'VBoxManage' -ErrorAction SilentlyContinue

$vmName = "EQ12_viBoot_$(Get-Date -Format 'yyyyMMddHHmmss')"
$useHyperV = $false

function Invoke-TestsInVM($session, $testCmds, $logsHostPath) {
    $results = @()
    foreach ($cmd in $testCmds) {
        try {
            Write-Output "Running inside VM: $cmd"
            $out = Invoke-Command -Session $session -ScriptBlock { param($c) Invoke-Expression $c } -ArgumentList $cmd -ErrorAction Stop
            $results += @{ cmd = $cmd; ok = $true; output = ($out -join "`n") }
        } catch {
            $results += @{ cmd = $cmd; ok = $false; error = $_.Exception.Message }
        }
    }
    # try to copy logs (if path exists inside VM)
    if ($logsHostPath) { New-Item -Path $logsHostPath -ItemType Directory -Force | Out-Null }
    return $results
}

function Get-VBoxVMIPAddress($vmName) {
    # Attempt to query VirtualBox guestproperty for IP addresses
    if (-not (Get-Command -Name 'VBoxManage' -ErrorAction SilentlyContinue)) { return $null }
    try {
        $props = & VBoxManage guestproperty enumerate $vmName 2>$null
        if (-not $props) { return $null }
        # search for '/VirtualBox/GuestInfo/Net/0/V4/IP' type entries
        foreach ($line in $props) {
            if ($line -match 'Name: /VirtualBox/GuestInfo/Net/\d+/V4/IP, value: ([0-9\.]+)') {
                return $matches[1]
            }
        }
        return $null
    } catch {
        return $null
    }
}

function Try-WinRMConnection($ip, $cred, [int]$timeoutSec = 120) {
    $start = Get-Date
    while ((Get-Date) -lt $start.AddSeconds($timeoutSec)) {
        try {
            $session = New-PSSession -ComputerName $ip -Credential $cred -Authentication Negotiate -ErrorAction Stop
            return $session
        } catch {
            Start-Sleep -Seconds 5
        }
    }
    return $null
}

# Try Hyper-V viBoot method
if ($hasHyperV) {
    try {
        Write-Output 'Hyper-V available; attempting viBoot via Hyper-V'
        # Mocked viBoot CLI call — Macrium's viBoot CLI usage may differ; replace with actual vendor CLI as needed.
        $viBootExe = 'C:\Program Files\Macrium\Reflect\vibootcmd.exe'
        if (-not (Test-Path $viBootExe)) { Write-Output 'viBoot CLI not found; skipping Hyper-V viBoot'; throw 'viBoot CLI missing' }
        # Example command: vibootcmd.exe create -image "path" -vmname "name" -hyperv
        $createArgs = "create -image `"$latestPath`" -vmname `"$vmName`" -hyperv"
        $create = & $viBootExe $createArgs
        Write-Output $create
        # Assume create returns VM guid or name; we will use vmName for lookup
        $useHyperV = $true
    } catch {
    Write-Output ("Hyper-V viBoot failed: {0}" -f $_.Exception.Message)
        $useHyperV = $false
    }
}

# If Hyper-V not used, try VirtualBox viBoot method
if (-not $useHyperV) {
    if ($hasVBox) {
        try {
            Write-Output 'Attempting viBoot via VirtualBox/viBoot'
            # Placeholder: actual viBoot to VirtualBox mapping may require different CLI; vendor docs should be consulted
            $viBootExe = 'C:\Program Files\Macrium\Reflect\vibootcmd.exe'
            if (-not (Test-Path $viBootExe)) { throw 'viBoot CLI missing' }
            $createArgs = "create -image `"$latestPath`" -vmname `"$vmName`" -virtualbox"
            $create = & $viBootExe $createArgs
            Write-Output $create
        } catch {
            Write-JsonAndExit @{ ok = $false; error = ("Failed to stage VM via viBoot: {0}" -f $_.Exception.Message) }
        }
    } else {
        Write-JsonAndExit @{ ok = $false; error = 'No supported hypervisor (Hyper-V or VirtualBox) available' }
    }
}

# Wait for VM to boot and create a session
$bootTimeout = $cfg.vm.BootTimeoutSec -as [int]
if (-not $bootTimeout) { $bootTimeout = 300 }
$start = Get-Date
$session = $null

try {
    if ($useHyperV) {
        # Use PowerShell Direct if available (works on Hyper-V host)
        Write-Output 'Attempting PowerShell Direct to the VM'
        $tries = 0
        while ((Get-Date) -lt $start.AddSeconds($bootTimeout)) {
            try {
                $session = New-PSSession -VMName $vmName -ErrorAction Stop
                break
            } catch {
                Start-Sleep -Seconds 5
                $tries++
            }
        }
        if (-not $session) { throw 'Timed out waiting for PowerShell Direct session' }
    } else {
        # For VirtualBox, attempt to discover the VM IP via VBoxManage guestproperty and connect via WinRM
        Write-Output 'Attempting WinRM connection to VM (VirtualBox)'
        $vmIp = Get-VBoxVMIPAddress -vmName $vmName
        if (-not $vmIp) { throw 'Could not discover VM IP via VBoxManage guestproperty' }
        Write-Output "Discovered VM IP: $vmIp"
        # Load credential from config if provided
        $cred = $null
        if ($cfg.tests.vm_credential) {
            $u = $cfg.tests.vm_credential.username
            $p = $cfg.tests.vm_credential.password
            $secure = ConvertTo-SecureString $p -AsPlainText -Force
            $cred = New-Object System.Management.Automation.PSCredential ($u, $secure)
        }
        $session = Try-WinRMConnection -ip $vmIp -cred $cred -timeoutSec $bootTimeout
        if (-not $session) { throw 'Timed out waiting for WinRM session to VM' }
    }

    # Run tests inside VM
    $testCmds = $cfg.tests.test_commands
    $logsHostPath = $cfg.tests.vm_logs_path
    if (-not $logsHostPath) {
        $logsHostPath = Join-Path -Path (Split-Path -Parent $ConfigPath) 'viboot_logs'
    }
    $results = Invoke-TestsInVM -session $session -testCmds $testCmds -logsHostPath $logsHostPath

    # write results to host JSON
    $out = @{ ok = $true; vm = $vmName; results = $results }
    $out | ConvertTo-Json -Depth 5 | Out-File -FilePath (Join-Path $logsHostPath "$vmName.results.json") -Encoding UTF8

} catch {
    Write-JsonAndExit @{ ok = $false; error = $_.Exception.Message }
} finally {
    # Tear down VM (attempt graceful shutdown then remove)
    try {
        if ($session) { Invoke-Command -Session $session -ScriptBlock { Stop-Computer -Force } -ErrorAction SilentlyContinue }
        Start-Sleep -Seconds 5
        if ($useHyperV) {
            Write-Output "Removing Hyper-V VM $vmName via viBoot"
            # Placeholder: vendor CLI to remove viBoot-created VM
            if (Test-Path $viBootExe) { & $viBootExe "delete -vmname `"$vmName`" -hyperv" }
        } else {
            Write-Output "Removing VirtualBox VM $vmName via viBoot"
            if (Get-Command -Name 'VBoxManage' -ErrorAction SilentlyContinue) { & VBoxManage unregistervm $vmName --delete }
        }
    } catch {
    Write-Output ("VM teardown error: {0}" -f $_.Exception.Message)
    }
}

Write-Output (ConvertTo-Json @{ ok = $true; vm = $vmName } -Depth 5)
