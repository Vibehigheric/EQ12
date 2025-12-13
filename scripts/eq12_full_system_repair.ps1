#Requires -RunAsAdministrator

<#
.SYNOPSIS
    EQ12 Full System Repair - Fixes TLS/SSL SCHANNEL errors and Python argparse issues
.DESCRIPTION
    Comprehensive repair script that:
    - Patches Python tools to support missing CLI arguments
    - Fixes Windows SCHANNEL TLS certificate issues (Error 36861)
    - Kills stuck processes on critical ports
    - Repairs Windows certificate store
    - Resets TLS/SSL settings
.PARAMETER WorkspaceRoot
    Root path of EQ12 workspace (defaults to C:\EQ12)
#>

[CmdletBinding()]
param(
    [string]$WorkspaceRoot = "C:\EQ12"
)

# Enhanced logging
$LogPath = Join-Path $WorkspaceRoot "logs\eq12_full_system_repair.log"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-RepairLog {
    param($Message, $Level = "INFO")
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry -ForegroundColor $(if($Level -eq "ERROR") {"Red"} elseif($Level -eq "WARNING") {"Yellow"} else {"Green"})
    Add-Content -Path $LogPath -Value $LogEntry -Force
}

function Test-EQ12Path {
    param($Path)
    return (Test-Path $Path) -and (Get-ChildItem $Path -Name "*.py" | Measure-Object).Count -gt 0
}

# Initialize
New-Item -ItemType Directory -Path (Split-Path $LogPath) -Force -ErrorAction SilentlyContinue | Out-Null
Write-RepairLog "=== EQ12 FULL SYSTEM REPAIR STARTED ===" "INFO"
Write-RepairLog "Target Workspace: $WorkspaceRoot" "INFO"

# Find EQ12 installation paths
$SearchPaths = @(
    $WorkspaceRoot,
    "$env:USERPROFILE\EQ12",
    "$env:USERPROFILE\Documents\EQ12",
    "C:\EQ12",
    "D:\EQ12"
)

$EQ12Root = $null
foreach ($Path in $SearchPaths) {
    if (Test-EQ12Path $Path) {
        $EQ12Root = $Path
        Write-RepairLog "Found EQ12 installation at: $Path" "INFO"
        break
    }
}

if (-not $EQ12Root) {
    Write-RepairLog "ERROR: Could not find valid EQ12 installation" "ERROR"
    exit 1
}

# 1. PATCH PYTHON ARGPARSE ISSUES
Write-RepairLog "=== PHASE 1: PATCHING PYTHON TOOLS ===" "INFO"

# Patch eq12_universal_repair_assistant.py
$RepairAssistantPath = Join-Path $EQ12Root "scripts\eq12_universal_repair_assistant.py"
if (Test-Path $RepairAssistantPath) {
    $BackupPath = "${RepairAssistantPath}.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $RepairAssistantPath $BackupPath
    Write-RepairLog "Backing up repair assistant to: $BackupPath" "INFO"
    
    $Content = Get-Content $RepairAssistantPath -Raw
    if ($Content -notlike "*emergency-repair*") {
        # Add emergency-repair to action choices
        $Content = $Content -replace 'choices=\["health-check", "generate-prompts", "generate-tasks", "comprehensive"\]', 'choices=["health-check", "generate-prompts", "generate-tasks", "comprehensive", "emergency-repair"]'
        
        # Add emergency-repair handler
        $EmergencyHandler = @"

    elif args.action == "emergency-repair":
        logger.info(" EMERGENCY REPAIR MODE ACTIVATED")
        # Kill stuck processes
        for port in [8000, 8080, 4040]:
            try:
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if f':{port} ' in line and 'LISTENING' in line:
                        pid = line.strip().split()[-1]
                        if pid.isdigit():
                            subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                            logger.info(f"Killed process {pid} on port {port}")
            except Exception as e:
                logger.error(f"Failed to kill process on port {port}: {e}")
        
        # Run comprehensive repair
        run_comprehensive_repair(args)
        return
"@
        
        if ($Content -notlike "*emergency-repair*") {
            $Content = $Content -replace '(\s+)(return\s*\n\s*if __name__ == "__main__")', "$1$EmergencyHandler$1`$2"
        }
        
        Set-Content $RepairAssistantPath -Value $Content -Encoding UTF8
        Write-RepairLog "Patched eq12_universal_repair_assistant.py - Added emergency-repair mode" "INFO"
    }
}

# Patch eq12_self_healing_orchestrator.py
$OrchestratorPath = Join-Path $EQ12Root "scripts\eq12_self_healing_orchestrator.py"
if (Test-Path $OrchestratorPath) {
    $BackupPath = "${OrchestratorPath}.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $OrchestratorPath $BackupPath
    Write-RepairLog "Backing up orchestrator to: $BackupPath" "INFO"
    
    $Content = Get-Content $OrchestratorPath -Raw
    if ($Content -notlike "*--emergency-mode*") {
        # Add missing arguments
        $ArgumentPatch = @"
    parser.add_argument('--emergency-mode', action='store_true', help='Enable emergency repair mode')
    parser.add_argument('--alerts', type=str, help='JSON alert payload for emergency mode')
"@
        
        $Content = $Content -replace '(\s+)(args = parser\.parse_args\(\))', "$ArgumentPatch`n`$1`$2"
        Set-Content $OrchestratorPath -Value $Content -Encoding UTF8
        Write-RepairLog "Patched eq12_self_healing_orchestrator.py - Added missing CLI arguments" "INFO"
    }
}

# 2. KILL STUCK PROCESSES
Write-RepairLog "=== PHASE 2: KILLING STUCK PROCESSES ===" "INFO"

$CriticalPorts = @(8000, 8080, 4040)
foreach ($Port in $CriticalPorts) {
    try {
        $Netstat = netstat -ano | Select-String ":$Port "
        foreach ($Line in $Netstat) {
            if ($Line -match "LISTENING") {
                $PID = ($Line -split '\s+')[-1]
                if ($PID -match '^\d+$') {
                    try {
                        $ProcessInfo = Get-Process -Id $PID -ErrorAction SilentlyContinue
                        if ($ProcessInfo) {
                            Write-RepairLog "Killing process $($ProcessInfo.Name) (PID: $PID) on port $Port" "WARNING"
                            Stop-Process -Id $PID -Force -ErrorAction SilentlyContinue
                        }
                    }
                    catch {
                        Write-RepairLog "Could not kill process PID $PID on port $Port" "WARNING"
                    }
                }
            }
        }
    }
    catch {
        Write-RepairLog "Error checking port $Port : $_" "WARNING"
    }
}

# 3. FIX WINDOWS TLS/SSL SCHANNEL ISSUES
Write-RepairLog "=== PHASE 3: REPAIRING TLS/SSL CERTIFICATES ===" "INFO"

# Clear certificate cache
Write-RepairLog "Clearing Windows certificate cache..." "INFO"
try {
    & certutil -urlcache * delete 2>&1 | Out-Null
    Write-RepairLog "Certificate cache cleared successfully" "INFO"
}
catch {
    Write-RepairLog "Warning: Could not clear certificate cache: $_" "WARNING"
}

# Repair certificate stores
Write-RepairLog "Repairing certificate stores..." "INFO"
$CertStores = @("my", "root", "ca")
foreach ($Store in $CertStores) {
    try {
        & certutil -repairstore $Store * 2>&1 | Out-Null
        Write-RepairLog "Repaired certificate store: $Store" "INFO"
    }
    catch {
        Write-RepairLog "Warning: Could not repair store $Store : $_" "WARNING"
    }
}

# Update Group Policy
Write-RepairLog "Updating Group Policy..." "INFO"
try {
    & gpupdate /force 2>&1 | Out-Null
    Write-RepairLog "Group Policy updated successfully" "INFO"
}
catch {
    Write-RepairLog "Warning: Could not update Group Policy: $_" "WARNING"
}

# 4. RESET TLS SETTINGS
Write-RepairLog "=== PHASE 4: RESETTING TLS/SCHANNEL SETTINGS ===" "INFO"

$TLSKeys = @(
    @{Path = "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Client"; Name = "Enabled"; Value = 1},
    @{Path = "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Server"; Name = "Enabled"; Value = 1},
    @{Path = "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.3\Client"; Name = "Enabled"; Value = 1},
    @{Path = "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.3\Server"; Name = "Enabled"; Value = 1}
)

foreach ($Key in $TLSKeys) {
    try {
        if (-not (Test-Path $Key.Path)) {
            New-Item -Path $Key.Path -Force | Out-Null
        }
        Set-ItemProperty -Path $Key.Path -Name $Key.Name -Value $Key.Value -Type DWord -Force
        Write-RepairLog "Set TLS registry key: $($Key.Path)\$($Key.Name) = $($Key.Value)" "INFO"
    }
    catch {
        Write-RepairLog "Error setting TLS key $($Key.Path): $_" "ERROR"
    }
}

# 5. RESET WINHTTP AND CRYPTO SERVICES
Write-RepairLog "=== PHASE 5: RESETTING NETWORK SERVICES ===" "INFO"

$NetworkCommands = @(
    @{Cmd = "netsh"; Args = @("http", "flush", "logbuffer")},
    @{Cmd = "netsh"; Args = @("winhttp", "reset", "proxy")},
    @{Cmd = "netsh"; Args = @("winhttp", "reset", "tracing")}
)

foreach ($Command in $NetworkCommands) {
    try {
        & $Command.Cmd $Command.Args 2>&1 | Out-Null
        Write-RepairLog "Executed: $($Command.Cmd) $($Command.Args -join ' ')" "INFO"
    }
    catch {
        Write-RepairLog "Warning: Could not execute $($Command.Cmd): $_" "WARNING"
    }
}

# Restart cryptographic services
Write-RepairLog "Restarting cryptographic services..." "INFO"
try {
    Stop-Service -Name "CryptSvc" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Start-Service -Name "CryptSvc" -ErrorAction SilentlyContinue
    Write-RepairLog "Cryptographic services restarted" "INFO"
}
catch {
    Write-RepairLog "Warning: Could not restart CryptSvc: $_" "WARNING"
}

# 6. REREGISTER SCHANNEL DLL
Write-RepairLog "=== PHASE 6: REREGISTERING CRYPTO DLLS ===" "INFO"
try {
    & regsvr32 /u /s schannel.dll
    & regsvr32 /s schannel.dll
    Write-RepairLog "Reregistered schannel.dll successfully" "INFO"
}
catch {
    Write-RepairLog "Warning: Could not reregister schannel.dll: $_" "WARNING"
}

# 7. FINAL SYSTEM STATUS CHECK
Write-RepairLog "=== PHASE 7: FINAL SYSTEM CHECK ===" "INFO"

# Check if VS Code processes are running normally
$VSCodeProcesses = Get-Process -Name "Code" -ErrorAction SilentlyContinue
if ($VSCodeProcesses) {
    Write-RepairLog "Found $($VSCodeProcesses.Count) VS Code processes running" "INFO"
    foreach ($Proc in $VSCodeProcesses) {
        $MemoryMB = [math]::Round($Proc.WorkingSet / 1MB, 2)
        Write-RepairLog "VS Code PID $($Proc.Id): Memory = $MemoryMB MB" "INFO"
    }
}

# Check port availability
foreach ($Port in $CriticalPorts) {
    $PortCheck = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
    if ($PortCheck.TcpTestSucceeded) {
        Write-RepairLog "Port $Port is now occupied (service running)" "INFO"
    } else {
        Write-RepairLog "Port $Port is available" "INFO"
    }
}

Write-RepairLog "=== EQ12 FULL SYSTEM REPAIR COMPLETED ===" "INFO"
Write-RepairLog "Log saved to: $LogPath" "INFO"
Write-RepairLog "NEXT STEPS:" "INFO"
Write-RepairLog "1. Restart your computer to apply all TLS/registry changes" "WARNING"
Write-RepairLog "2. Launch VS Code and test for crashes" "WARNING"
Write-RepairLog "3. Start your EQ12 services (launcher, dashboard, etc.)" "WARNING"

Write-Host "`n REPAIR COMPLETED! Check the log file for details: $LogPath" -ForegroundColor Green
Write-Host " Please RESTART your computer to apply all changes." -ForegroundColor Yellow
