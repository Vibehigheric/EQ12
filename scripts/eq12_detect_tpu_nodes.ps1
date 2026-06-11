#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 TPU Cluster Detection & Management System
.DESCRIPTION
    Automatically detects, benchmarks, and manages TPU-enabled Pi nodes in the EQ12 cluster.
    Performs comprehensive TPU discovery, performance testing, and cluster node registration.
.PARAMETER Action
    Action to perform: Scan, Benchmark, Register, Status, or Full
.PARAMETER IPRange
    IP range to scan (default: 192.168.100.2-254)
.PARAMETER Username
    SSH username for Pi nodes (default: ricoj100)
.PARAMETER Password
    SSH password for Pi nodes
.PARAMETER OutputFormat
    Output format: Console, JSON, or HTML (default: Console)
.EXAMPLE
    .\eq12_detect_tpu_nodes.ps1 -Action Full -Password "CLUSTER_PASSWORD_PLACEHOLDER"
.EXAMPLE
    .\eq12_detect_tpu_nodes.ps1 -Action Benchmark -IPRange "192.168.100.2" -Password "CLUSTER_PASSWORD_PLACEHOLDER"
#>

[CmdletBinding()]
param(
    [ValidateSet("Scan", "Benchmark", "Register", "Status", "Full")]
    [string]$Action = "Full",
    
    [string]$IPRange = "192.168.100.2-254",
    [string]$Username = "ricoj100",
    [string]$Password = "CLUSTER_PASSWORD_PLACEHOLDER",
    
    [ValidateSet("Console", "JSON", "HTML")]
    [string]$OutputFormat = "Console",
    
    [int]$Timeout = 30,
    [switch]$VerboseOutput,
    [switch]$GenerateReport
)

# Enhanced logging and paths
$LogPath = "C:\EQ12\logs"
$ReportsPath = "C:\EQ12\dashboard"
$ConfigPath = "C:\EQ12\configs"
$LogFile = Join-Path $LogPath "tpu_cluster_detection_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$ClusterConfigFile = Join-Path $ConfigPath "eq12_tpu_cluster_nodes.json"

# Ensure directories exist
@($LogPath, $ReportsPath, $ConfigPath) | ForEach-Object {
    if (-not (Test-Path $_)) { New-Item -Path $_ -ItemType Directory -Force }
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Test-SSHConnection {
    param([string]$IP, [int]$Port = 22)
    try {
        $Connection = Test-NetConnection -ComputerName $IP -Port $Port -WarningAction SilentlyContinue -InformationLevel Quiet
        return $Connection
    }
    catch {
        return $false
    }
}

function Invoke-SSHCommand {
    param([string]$IP, [string]$Command, [string]$Description = "")
    
    Write-Log "SSH [$IP]: $Description" "DEBUG"
    
    try {
        # Use Windows SSH client with password automation
        $SSHProcess = Start-Process -FilePath "ssh" -ArgumentList @(
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=$Timeout",
            "-o", "UserKnownHostsFile=nul",
            "$Username@$IP",
            $Command
        ) -PassThru -WindowStyle Hidden -RedirectStandardOutput "temp_ssh_output.txt" -RedirectStandardError "temp_ssh_error.txt"
        
        # Send password if prompted
        Start-Sleep -Seconds 2
        if (-not $SSHProcess.HasExited) {
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("$Password{ENTER}")
        }
        
        $SSHProcess.WaitForExit($Timeout * 1000)
        
        if (Test-Path "temp_ssh_output.txt") {
            $Output = Get-Content "temp_ssh_output.txt" -Raw
            Remove-Item "temp_ssh_output.txt" -Force -ErrorAction SilentlyContinue
        }
        
        if (Test-Path "temp_ssh_error.txt") {
            Remove-Item "temp_ssh_error.txt" -Force -ErrorAction SilentlyContinue
        }
        
        return $Output
    }
    catch {
        Write-Log "SSH Error [$IP]: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

function Get-TPUDevices {
    param([string]$IP)
    
    Write-Log "Scanning TPU devices on $IP..."
    
    $Command = "lsusb | grep -i 'Google\|Coral' && echo '---SEPARATOR---' && ls /dev/apex_* 2>/dev/null || echo 'No TPU devices found'"
    $Result = Invoke-SSHCommand -IP $IP -Command $Command -Description "TPU device scan"
    
    if ($Result) {
        $TPUDevices = @()
        $Lines = $Result -split "`n"
        
        foreach ($Line in $Lines) {
            if ($Line -match "Google|Coral") {
                if ($Line -match "Bus (\d+) Device (\d+): ID ([a-f0-9:]+) (.+)") {
                    $TPUDevices += @{
                        Bus = $Matches[1]
                        Device = $Matches[2]
                        VendorProduct = $Matches[3]
                        Description = $Matches[4].Trim()
                        Type = if ($Line -match "Coral") { "Coral" } else { "Google" }
                    }
                }
            }
        }
        
        return $TPUDevices
    }
    
    return @()
}

function Test-TPUPerformance {
    param([string]$IP)
    
    Write-Log "Running TPU benchmark on $IP..."
    
    $BenchmarkScript = @'
cd ~/coral_test 2>/dev/null || mkdir -p ~/coral_test && cd ~/coral_test
if [ ! -f mobilenet_edgetpu.tflite ]; then
    wget -q https://github.com/google-coral/test_data/raw/master/mobilenet_v1_1.0_224_quant_edgetpu.tflite -O mobilenet_edgetpu.tflite
    wget -q https://github.com/google-coral/test_data/raw/master/cat.bmp -O cat.bmp
fi

python3 - <<'EOF'
import time
import sys
from PIL import Image
import numpy as np
try:
    import tflite_runtime.interpreter as tflite
    
    # Run 10 inference cycles
    interpreter = tflite.Interpreter(
        model_path="mobilenet_edgetpu.tflite", 
        experimental_delegates=[tflite.load_delegate('libedgetpu.so.1')]
    )
    interpreter.allocate_tensors()
    
    input_details = interpreter.get_input_details()
    image = Image.open("cat.bmp").resize((224,224))
    input_data = np.expand_dims(image, axis=0)
    
    times = []
    for i in range(10):
        interpreter.set_tensor(input_details[0]['index'], input_data)
        start = time.time()
        interpreter.invoke()
        end = time.time()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"BENCHMARK_RESULT:avg={avg_time:.4f},min={min_time:.4f},max={max_time:.4f},iterations=10")
    
except Exception as e:
    print(f"BENCHMARK_ERROR:{str(e)}")
EOF
'@
    
    $Result = Invoke-SSHCommand -IP $IP -Command $BenchmarkScript -Description "TPU performance test"
    
    if ($Result -and $Result -match "BENCHMARK_RESULT:avg=([0-9.]+),min=([0-9.]+),max=([0-9.]+),iterations=(\d+)") {
        return @{
            AvgTime = [float]$Matches[1]
            MinTime = [float]$Matches[2]
            MaxTime = [float]$Matches[3]
            Iterations = [int]$Matches[4]
            InferencesPerSecond = [math]::Round(1 / [float]$Matches[1], 2)
            Status = "Success"
        }
    }
    elseif ($Result -match "BENCHMARK_ERROR:(.+)") {
        return @{
            Status = "Error"
            Error = $Matches[1]
        }
    }
    
    return @{ Status = "Unknown"; Error = "No benchmark data received" }
}

function Get-NodeInfo {
    param([string]$IP)
    
    Write-Log "Gathering node information for $IP..."
    
    $InfoScript = @'
echo "HOSTNAME:$(hostname)"
echo "KERNEL:$(uname -r)"
echo "ARCH:$(uname -m)"
echo "MEMORY:$(free -m | grep '^Mem:' | awk '{print $2}')"
echo "CPU:$(nproc)"
echo "TEMP:$(vcgencmd measure_temp 2>/dev/null | cut -d= -f2 || echo 'N/A')"
echo "UPTIME:$(uptime -p | sed 's/up //')"
echo "LOAD:$(uptime | awk -F'load average:' '{print $2}' | sed 's/ //g')"
'@
    
    $Result = Invoke-SSHCommand -IP $IP -Command $InfoScript -Description "System information"
    
    $NodeInfo = @{}
    if ($Result) {
        $Lines = $Result -split "`n"
        foreach ($Line in $Lines) {
            if ($Line -match "^([^:]+):(.+)$") {
                $NodeInfo[$Matches[1]] = $Matches[2].Trim()
            }
        }
    }
    
    return $NodeInfo
}

function Scan-ClusterNodes {
    Write-Log " Starting cluster node scan..." "INFO"
    
    $DiscoveredNodes = @()
    $IPList = @()
    
    if ($IPRange -match "^(\d+\.\d+\.\d+\.)(\d+)-(\d+)$") {
        $Base = $Matches[1]
        $Start = [int]$Matches[2]
        $End = [int]$Matches[3]
        
        for ($i = $Start; $i -le $End; $i++) {
            $IPList += "$Base$i"
        }
    }
    elseif ($IPRange -match "^\d+\.\d+\.\d+\.\d+$") {
        $IPList = @($IPRange)
    }
    else {
        Write-Log "Invalid IP range format: $IPRange" "ERROR"
        return @()
    }
    
    Write-Log "Scanning $($IPList.Count) IP addresses..."
    
    foreach ($IP in $IPList) {
        Write-Progress -Activity "Scanning cluster nodes" -Status "Testing $IP" -PercentComplete (($IPList.IndexOf($IP) / $IPList.Count) * 100)
        
        if (Test-SSHConnection -IP $IP) {
            Write-Log " Node found at $IP" "INFO"
            
            $Node = @{
                IP = $IP
                Status = "Online"
                LastSeen = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                TPUDevices = @()
                Performance = @{}
                SystemInfo = @{}
            }
            
            # Get system info
            $Node.SystemInfo = Get-NodeInfo -IP $IP
            
            # Check for TPU devices
            $TPUDevices = Get-TPUDevices -IP $IP
            if ($TPUDevices.Count -gt 0) {
                $Node.TPUDevices = $TPUDevices
                $Node.HasTPU = $true
                Write-Log " TPU devices found on $IP`: $($TPUDevices.Count)" "INFO"
            }
            else {
                $Node.HasTPU = $false
                Write-Log "  No TPU devices on $IP" "WARNING"
            }
            
            $DiscoveredNodes += $Node
        }
        else {
            Write-Log " No response from $IP" "DEBUG"
        }
    }
    
    Write-Progress -Activity "Scanning cluster nodes" -Completed
    Write-Log "Scan complete. Found $($DiscoveredNodes.Count) active nodes, $(($DiscoveredNodes | Where-Object {$_.HasTPU}).Count) with TPUs"
    
    return $DiscoveredNodes
}

function Start-TPUBenchmarking {
    param([array]$Nodes)
    
    Write-Log " Starting TPU performance benchmarking..." "INFO"
    
    $TPUNodes = $Nodes | Where-Object { $_.HasTPU -eq $true }
    
    if ($TPUNodes.Count -eq 0) {
        Write-Log "No TPU-enabled nodes found for benchmarking" "WARNING"
        return $Nodes
    }
    
    foreach ($Node in $TPUNodes) {
        Write-Progress -Activity "Benchmarking TPU nodes" -Status "Testing $($Node.IP)" -PercentComplete (($TPUNodes.IndexOf($Node) / $TPUNodes.Count) * 100)
        
        Write-Log "Benchmarking TPU performance on $($Node.IP)..."
        $Performance = Test-TPUPerformance -IP $Node.IP
        $Node.Performance = $Performance
        
        if ($Performance.Status -eq "Success") {
            Write-Log " TPU benchmark complete: $($Performance.InferencesPerSecond) inf/sec" "INFO"
        }
        else {
            Write-Log " TPU benchmark failed: $($Performance.Error)" "ERROR"
        }
    }
    
    Write-Progress -Activity "Benchmarking TPU nodes" -Completed
    return $Nodes
}

function Save-ClusterConfig {
    param([array]$Nodes)
    
    $ClusterConfig = @{
        LastUpdated = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        ClusterNetwork = "192.168.100.0/24"
        MasterNode = "192.168.100.1"
        TotalNodes = $Nodes.Count
        TPUNodes = ($Nodes | Where-Object { $_.HasTPU -eq $true }).Count
        Nodes = $Nodes
    }
    
    $ClusterConfig | ConvertTo-Json -Depth 10 | Out-File -FilePath $ClusterConfigFile -Encoding UTF8
    Write-Log "Cluster configuration saved to: $ClusterConfigFile"
}

function Show-ClusterStatus {
    param([array]$Nodes, [string]$Format = "Console")
    
    $TPUNodes = $Nodes | Where-Object { $_.HasTPU -eq $true }
    $OnlineNodes = $Nodes | Where-Object { $_.Status -eq "Online" }
    
    if ($Format -eq "Console") {
        Write-Host ""
        Write-Host " EQ12 TPU CLUSTER STATUS" -ForegroundColor Green
        Write-Host "=" * 50 -ForegroundColor Cyan
        Write-Host "Total Nodes:    $($Nodes.Count)" -ForegroundColor White
        Write-Host "Online Nodes:   $($OnlineNodes.Count)" -ForegroundColor Green
        Write-Host "TPU Nodes:      $($TPUNodes.Count)" -ForegroundColor Yellow
        Write-Host "Cluster Network: 192.168.100.0/24" -ForegroundColor Gray
        Write-Host ""
        
        if ($TPUNodes.Count -gt 0) {
            Write-Host " TPU-ENABLED NODES" -ForegroundColor Yellow
            Write-Host "-" * 50 -ForegroundColor Cyan
            
            foreach ($Node in $TPUNodes) {
                Write-Host "Node: $($Node.IP)" -ForegroundColor Cyan
                Write-Host "  Hostname: $($Node.SystemInfo.HOSTNAME)" -ForegroundColor White
                Write-Host "  TPU Devices: $($Node.TPUDevices.Count)" -ForegroundColor Green
                
                foreach ($TPU in $Node.TPUDevices) {
                    Write-Host "    - $($TPU.Description)" -ForegroundColor Gray
                }
                
                if ($Node.Performance.Status -eq "Success") {
                    Write-Host "  Performance: $($Node.Performance.InferencesPerSecond) inf/sec" -ForegroundColor Green
                    Write-Host "  Avg Latency: $($Node.Performance.AvgTime)ms" -ForegroundColor Gray
                }
                Write-Host ""
            }
        }
    }
    elseif ($Format -eq "JSON") {
        $StatusData = @{
            Summary = @{
                TotalNodes = $Nodes.Count
                OnlineNodes = $OnlineNodes.Count
                TPUNodes = $TPUNodes.Count
                LastUpdate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
            Nodes = $Nodes
        }
        
        return $StatusData | ConvertTo-Json -Depth 10
    }
    elseif ($Format -eq "HTML") {
        Generate-HTMLReport -Nodes $Nodes
    }
}

function Generate-HTMLReport {
    param([array]$Nodes)
    
    $ReportFile = Join-Path $ReportsPath "eq12_tpu_cluster_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').html"
    
    $HTMLContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>EQ12 TPU Cluster Report</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #0d1117; color: #c9d1d9; }
        .header { background: #21262d; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .summary { display: flex; gap: 20px; margin-bottom: 20px; }
        .card { background: #21262d; padding: 15px; border-radius: 8px; flex: 1; }
        .node { background: #21262d; padding: 15px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid #238636; }
        .tpu-node { border-left-color: #f85149; }
        .performance { background: #0d1117; padding: 10px; border-radius: 4px; margin-top: 10px; }
        .metric { display: inline-block; margin-right: 20px; }
        .value { font-weight: bold; color: #58a6ff; }
        h1, h2 { color: #58a6ff; }
        .status-online { color: #238636; }
        .status-tpu { color: #f85149; }
    </style>
</head>
<body>
    <div class="header">
        <h1>EQ12 TPU Cluster Report</h1>
        <p>Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")</p>
    </div>
    
    <div class="summary">
        <div class="card">
            <h3>Total Nodes</h3>
            <div class="value">$($Nodes.Count)</div>
        </div>
        <div class="card">
            <h3>Online Nodes</h3>
            <div class="value status-online">$(($Nodes | Where-Object {$_.Status -eq "Online"}).Count)</div>
        </div>
        <div class="card">
            <h3>TPU Nodes</h3>
            <div class="value status-tpu">$(($Nodes | Where-Object {$_.HasTPU -eq $true}).Count)</div>
        </div>
    </div>
    
    <h2>Node Details</h2>
"@

    foreach ($Node in $Nodes) {
        $NodeClass = if ($Node.HasTPU) { "node tpu-node" } else { "node" }
        $TPUBadge = if ($Node.HasTPU) { "TPU" } else { "CPU" }
        
        $HTMLContent += @"
    <div class="$NodeClass">
        <h3>$($Node.IP) $TPUBadge</h3>
        <p><strong>Hostname:</strong> $($Node.SystemInfo.HOSTNAME)</p>
        <p><strong>Status:</strong> <span class="status-online">$($Node.Status)</span></p>
        <p><strong>Architecture:</strong> $($Node.SystemInfo.ARCH)</p>
        <p><strong>Memory:</strong> $($Node.SystemInfo.MEMORY) MB</p>
        <p><strong>CPU Cores:</strong> $($Node.SystemInfo.CPU)</p>
        <p><strong>Temperature:</strong> $($Node.SystemInfo.TEMP)</p>
        
"@
        
        if ($Node.HasTPU) {
            $HTMLContent += "<p><strong>TPU Devices:</strong></p><ul>"
            foreach ($TPU in $Node.TPUDevices) {
                $HTMLContent += "<li>$($TPU.Description)</li>"
            }
            $HTMLContent += "</ul>"
            
            if ($Node.Performance.Status -eq "Success") {
                $HTMLContent += @"
        <div class="performance">
            <strong>Performance Metrics:</strong><br>
            <span class="metric">Inferences/sec: <span class="value">$($Node.Performance.InferencesPerSecond)</span></span>
            <span class="metric">Avg Latency: <span class="value">$($Node.Performance.AvgTime)ms</span></span>
            <span class="metric">Min Latency: <span class="value">$($Node.Performance.MinTime)ms</span></span>
        </div>
"@
            }
        }
        
        $HTMLContent += "    </div>`n"
    }
    
    $HTMLContent += @"
</body>
</html>
"@
    
    $HTMLContent | Out-File -FilePath $ReportFile -Encoding UTF8
    Write-Log "HTML report generated: $ReportFile"
    
    # Open report in browser
    Start-Process $ReportFile
}

# Main execution
Write-Log " EQ12 TPU Cluster Detection & Management System Starting" "INFO"
Write-Log "Action: $Action | IP Range: $IPRange | Output: $OutputFormat"

$ClusterNodes = @()

switch ($Action) {
    "Scan" {
        $ClusterNodes = Scan-ClusterNodes
        Show-ClusterStatus -Nodes $ClusterNodes -Format $OutputFormat
    }
    
    "Benchmark" {
        if (Test-Path $ClusterConfigFile) {
            $Config = Get-Content $ClusterConfigFile | ConvertFrom-Json
            $ClusterNodes = $Config.Nodes
        }
        else {
            $ClusterNodes = Scan-ClusterNodes
        }
        
        $ClusterNodes = Start-TPUBenchmarking -Nodes $ClusterNodes
        Show-ClusterStatus -Nodes $ClusterNodes -Format $OutputFormat
    }
    
    "Register" {
        if (Test-Path $ClusterConfigFile) {
            $Config = Get-Content $ClusterConfigFile | ConvertFrom-Json
            $ClusterNodes = $Config.Nodes
        }
        else {
            $ClusterNodes = Scan-ClusterNodes
        }
        
        Save-ClusterConfig -Nodes $ClusterNodes
        Write-Log "Cluster nodes registered in configuration"
    }
    
    "Status" {
        if (Test-Path $ClusterConfigFile) {
            $Config = Get-Content $ClusterConfigFile | ConvertFrom-Json
            $ClusterNodes = $Config.Nodes
            Show-ClusterStatus -Nodes $ClusterNodes -Format $OutputFormat
        }
        else {
            Write-Log "No cluster configuration found. Run with -Action Scan first." "WARNING"
        }
    }
    
    "Full" {
        Write-Log "Performing complete cluster analysis..." "INFO"
        $ClusterNodes = Scan-ClusterNodes
        $ClusterNodes = Start-TPUBenchmarking -Nodes $ClusterNodes
        Save-ClusterConfig -Nodes $ClusterNodes
        Show-ClusterStatus -Nodes $ClusterNodes -Format $OutputFormat
        
        if ($GenerateReport) {
            Generate-HTMLReport -Nodes $ClusterNodes
        }
    }
}

Write-Log " EQ12 TPU Cluster Detection Complete" "INFO"
Write-Log "Results logged to: $LogFile"

if ($OutputFormat -eq "JSON" -and $ClusterNodes.Count -gt 0) {
    $JSONOutput = Show-ClusterStatus -Nodes $ClusterNodes -Format "JSON"
    $JSONFile = Join-Path $LogPath "cluster_status_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $JSONOutput | Out-File -FilePath $JSONFile -Encoding UTF8
    Write-Log "JSON output saved to: $JSONFile"
}
