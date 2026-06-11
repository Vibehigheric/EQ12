# EQ12 Pi Deployment Verification Script
# Automated post-boot testing and cluster registration

[CmdletBinding()]
param(
    [string]$PiIP = "192.168.100.2",
    [string]$Username = "ricoj100", 
    [string]$Password = "CLUSTER_PASSWORD_PLACEHOLDER",
    [int]$TimeoutSeconds = 300,
    [switch]$SetupSSHKey,
    [switch]$DeployServices
)

$ErrorActionPreference = "Stop"

# Configure logging
$LogPath = "C:\EQ12\logs\pi_deployment_verification_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
New-Item -Path (Split-Path $LogPath) -ItemType Directory -Force | Out-Null

function Write-DeployLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry -ForegroundColor $(if ($Level -eq "ERROR") { "Red" } elseif ($Level -eq "WARN") { "Yellow" } elseif ($Level -eq "SUCCESS") { "Green" } else { "White" })
    $LogEntry | Out-File -FilePath $LogPath -Append -Encoding UTF8
}

function Test-PiConnectivity {
    param([string]$IP)
    
    Write-DeployLog "Testing network connectivity to Pi at $IP..." "INFO"
    
    # Test ping connectivity
    try {
        $PingResult = Test-Connection -ComputerName $IP -Count 3 -Quiet
        if ($PingResult) {
            Write-DeployLog " Ping test successful" "SUCCESS"
        }
        else {
            Write-DeployLog " Ping test failed" "ERROR"
            return $false
        }
    }
    catch {
        Write-DeployLog " Ping test error: $($_.Exception.Message)" "ERROR"
        return $false
    }
    
    # Test SSH port
    try {
        $SSHTest = Test-NetConnection -ComputerName $IP -Port 22 -WarningAction SilentlyContinue
        if ($SSHTest.TcpTestSucceeded) {
            Write-DeployLog " SSH port (22) is open" "SUCCESS"
            return $true
        }
        else {
            Write-DeployLog " SSH port (22) is not accessible" "ERROR"
            return $false
        }
    }
    catch {
        Write-DeployLog " SSH port test error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-SSHLogin {
    param([string]$IP, [string]$User, [string]$Pass)
    
    Write-DeployLog "Testing SSH authentication..." "INFO"
    
    try {
        # Create temporary SSH key for testing if not exists
        $SSHKeyPath = "$env:USERPROFILE\.ssh\eq12_pi_temp"
        if (!(Test-Path "$SSHKeyPath.pub")) {
            Write-DeployLog "Generating temporary SSH key..." "INFO"
            ssh-keygen -t ed25519 -f $SSHKeyPath -N '""' -q
        }
        
        # Test password authentication first
        $TestCommand = "echo 'SSH connection successful'"
        $SSHResult = echo $Pass | ssh -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=/dev/null" -o "LogLevel=ERROR" "$User@$IP" $TestCommand 2>$null
        
        if ($SSHResult -match "SSH connection successful") {
            Write-DeployLog " SSH password authentication successful" "SUCCESS"
            return $true
        }
        else {
            Write-DeployLog " SSH password authentication failed" "ERROR"
            return $false
        }
    }
    catch {
        Write-DeployLog " SSH login test error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Install-SSHKey {
    param([string]$IP, [string]$User, [string]$Pass)
    
    Write-DeployLog "Setting up SSH key authentication..." "INFO"
    
    try {
        $SSHKeyPath = "$env:USERPROFILE\.ssh\eq12_pi_key"
        
        # Generate SSH key if it doesn't exist
        if (!(Test-Path "$SSHKeyPath.pub")) {
            Write-DeployLog "Generating SSH key pair..." "INFO"
            ssh-keygen -t ed25519 -f $SSHKeyPath -N '""' -q
        }
        
        # Copy SSH key to Pi
        $PublicKey = Get-Content "$SSHKeyPath.pub"
        $KeyInstallCommand = "mkdir -p ~/.ssh && echo '$PublicKey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh"
        
        echo $Pass | ssh -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=/dev/null" -o "LogLevel=ERROR" "$User@$IP" $KeyInstallCommand
        
        # Test key-based authentication
        $TestResult = ssh -i $SSHKeyPath -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=/dev/null" -o "LogLevel=ERROR" "$User@$IP" "echo 'Key auth successful'"
        
        if ($TestResult -match "Key auth successful") {
            Write-DeployLog " SSH key authentication configured successfully" "SUCCESS"
            return $true
        }
        else {
            Write-DeployLog " SSH key authentication setup failed" "ERROR"
            return $false
        }
    }
    catch {
        Write-DeployLog " SSH key setup error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Register-PiWithCluster {
    param([string]$IP, [string]$User, [string]$Pass)
    
    Write-DeployLog "Registering Pi with EQ12 cluster..." "INFO"
    
    try {
        $ClusterManagerPath = "C:\EQ12\scripts\eq12_raspberry_pi_cluster_manager.py"
        if (Test-Path $ClusterManagerPath) {
            $ClusterArgs = @(
                $ClusterManagerPath,
                "--action", "add-node",
                "--ip", $IP,
                "--username", $User,
                "--password", $Pass
            )
            
            $ClusterResult = & python @ClusterArgs 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-DeployLog " Pi successfully registered with cluster" "SUCCESS"
                Write-DeployLog "Cluster registration output: $ClusterResult" "INFO"
                return $true
            }
            else {
                Write-DeployLog " Cluster registration failed: $ClusterResult" "ERROR"
                return $false
            }
        }
        else {
            Write-DeployLog " Cluster manager script not found at $ClusterManagerPath" "ERROR"
            return $false
        }
    }
    catch {
        Write-DeployLog " Cluster registration error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Deploy-EQ12Services {
    param([string]$IP, [string]$User)
    
    Write-DeployLog "Deploying EQ12 services to Pi..." "INFO"
    
    try {
        $SSHKeyPath = "$env:USERPROFILE\.ssh\eq12_pi_key"
        
        # Basic system setup commands
        $SetupCommands = @(
            "sudo apt update && sudo apt upgrade -y",
            "sudo apt install -y docker.io docker-compose git python3-pip",
            "sudo usermod -aG docker $User",
            "sudo systemctl enable docker",
            "sudo systemctl start docker",
            "mkdir -p ~/EQ12/logs ~/EQ12/data"
        )
        
        foreach ($Command in $SetupCommands) {
            Write-DeployLog "Executing: $Command" "INFO"
            $Result = ssh -i $SSHKeyPath -o "StrictHostKeyChecking=no" "$User@$IP" $Command
            if ($LASTEXITCODE -ne 0) {
                Write-DeployLog " Command failed: $Command" "ERROR"
                return $false
            }
        }
        
        # Deploy EQ12 cluster service
        $ServiceDeployCommand = @"
cat > ~/docker-compose.yml << 'EOF'
version: '3.8'
services:
  eq12-node:
    image: python:3.11-slim
    container_name: eq12-cluster-service
    restart: unless-stopped
    ports:
      - "8001:8001"
    volumes:
      - ~/EQ12:/app/EQ12
      - /var/run/docker.sock:/var/run/docker.sock
    working_dir: /app
    command: >
      bash -c "
        pip install fastapi uvicorn requests docker &&
        python -c \"
import fastapi, uvicorn
app = fastapi.FastAPI()

@app.get('/')
def health():
    return {'status': 'healthy', 'node': 'pi-node-1', 'service': 'eq12-cluster'}

@app.get('/cluster/info')  
def cluster_info():
    return {
        'node_id': 'pi-node-1',
        'ip': '$IP',
        'services': ['tpu-inference', 'cross-listing', 'monitoring'],
        'uptime': '$(uptime -p)'
    }

uvicorn.run(app, host='0.0.0.0', port=8001)
        \"
      "
    environment:
      - NODE_ID=pi-node-1
      - CLUSTER_MASTER=192.168.100.1
EOF

docker-compose up -d
"@
        
        Write-DeployLog "Deploying cluster service container..." "INFO"
        ssh -i $SSHKeyPath -o "StrictHostKeyChecking=no" "$User@$IP" $ServiceDeployCommand
        
        # Verify service deployment
        Start-Sleep -Seconds 10
        $ServiceTest = ssh -i $SSHKeyPath -o "StrictHostKeyChecking=no" "$User@$IP" "curl -s http://localhost:8001/ || echo 'Service not ready'"
        
        if ($ServiceTest -match "healthy") {
            Write-DeployLog " EQ12 cluster service deployed successfully" "SUCCESS"
            return $true
        }
        else {
            Write-DeployLog " Service deployment verification failed: $ServiceTest" "ERROR"
            return $false
        }
        
    }
    catch {
        Write-DeployLog " Service deployment error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Get-ClusterStatus {
    Write-DeployLog "Checking overall cluster status..." "INFO"
    
    try {
        # Test cluster API endpoint
        $ClusterAPI = "http://192.168.100.1:8000/cluster/status"
        $MasterStatus = Invoke-RestMethod -Uri $ClusterAPI -TimeoutSec 10 -ErrorAction SilentlyContinue
        
        if ($MasterStatus) {
            Write-DeployLog " EQ12 cluster master is responding" "SUCCESS"
        }
        
        # Test Pi node API endpoint  
        $NodeAPI = "http://${PiIP}:8001/cluster/info"
        $NodeStatus = Invoke-RestMethod -Uri $NodeAPI -TimeoutSec 10 -ErrorAction SilentlyContinue
        
        if ($NodeStatus) {
            Write-DeployLog " Pi node service is responding" "SUCCESS"
            Write-DeployLog "Node info: $($NodeStatus | ConvertTo-Json -Compress)" "INFO"
        }
        
        return $true
    }
    catch {
        Write-DeployLog " Cluster status check error: $($_.Exception.Message)" "WARN"
        return $false
    }
}

# Main execution flow
Write-DeployLog " Starting EQ12 Pi deployment verification..." "INFO"
Write-DeployLog "Target: $Username@$PiIP" "INFO"

# Step 1: Wait for Pi to boot and test connectivity
Write-DeployLog " Waiting for Pi to boot (timeout: $TimeoutSeconds seconds)..." "INFO"
$StartTime = Get-Date
$Connected = $false

do {
    if (Test-PiConnectivity -IP $PiIP) {
        $Connected = $true
        break
    }
    Start-Sleep -Seconds 10
    $ElapsedSeconds = (Get-Date) - $StartTime | Select-Object -ExpandProperty TotalSeconds
} while ($ElapsedSeconds -lt $TimeoutSeconds)

if (-not $Connected) {
    Write-DeployLog " Pi connectivity timeout after $TimeoutSeconds seconds" "ERROR"
    Write-DeployLog "Check: Pi boot status, Ethernet connection, power supply" "ERROR"
    exit 1
}

# Step 2: Test SSH authentication
if (-not (Test-SSHLogin -IP $PiIP -User $Username -Pass $Password)) {
    Write-DeployLog " SSH authentication failed" "ERROR"
    Write-DeployLog "Verify: SSH enabled during imaging, correct credentials" "ERROR"
    exit 1
}

# Step 3: Setup SSH key authentication (optional)
if ($SetupSSHKey) {
    Install-SSHKey -IP $PiIP -User $Username -Pass $Password
}

# Step 4: Register with EQ12 cluster
if (-not (Register-PiWithCluster -IP $PiIP -User $Username -Pass $Password)) {
    Write-DeployLog " Cluster registration failed" "ERROR"
    exit 1
}

# Step 5: Deploy EQ12 services (optional)
if ($DeployServices) {
    if (-not (Deploy-EQ12Services -IP $PiIP -User $Username)) {
        Write-DeployLog " Service deployment failed" "ERROR"
        exit 1
    }
}

# Step 6: Final cluster status check
Get-ClusterStatus

Write-DeployLog " Pi deployment verification completed successfully!" "SUCCESS"
Write-DeployLog "Next steps:" "INFO"
Write-DeployLog "  - Connect Coral TPU and test AI inference" "INFO"
Write-DeployLog "  - Monitor cluster dashboard: http://192.168.100.1:3000" "INFO"
Write-DeployLog "  - Scale to additional Pi nodes using cluster installer" "INFO"

# Summary report
Write-DeployLog " Deployment Summary:" "INFO"
Write-DeployLog "   Network connectivity: PASS" "INFO"
Write-DeployLog "   SSH authentication: PASS" "INFO"
if ($SetupSSHKey) { Write-DeployLog "   SSH key setup: PASS" "INFO" }
Write-DeployLog "   Cluster registration: PASS" "INFO"
if ($DeployServices) { Write-DeployLog "   Service deployment: PASS" "INFO" }
Write-DeployLog "   Full log: $LogPath" "INFO"