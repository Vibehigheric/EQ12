# Ngrok Integration Strategy for EQ12 GODSTACK

## Overview

This document outlines the comprehensive ngrok integration strategy for EQ12 GODSTACK, enabling secure tunneling for development, testing, and governance workflows while maintaining compliance with our multi-stack architecture.

## 🎯 Strategic Applications

### Development & Testing
- **Local API Development**: Expose FastAPI services for external testing
- **Webhook Development**: Test GitHub Apps, Telegram bots, and third-party integrations
- **Mobile Testing**: Access local services from mobile devices for responsive testing
- **Cross-Platform Development**: Seamless development across Windows/Linux/Codespaces

### Governance & Compliance
- **Audit Exposures**: Temporary secure access for compliance reviews
- **Stakeholder Demos**: Real-time demonstration of governance dashboards
- **External Integrations**: Secure tunneling for regulatory reporting systems
- **Emergency Access**: Rapid deployment of temporary access for incident response

### Business Stack Integration
- **🎰 Betting Stack**: Secure testing of gambling compliance endpoints
- **🌿 Cannabis Stack**: METRC integration testing without production exposure
- **💳 Credit Stack**: PCI-compliant development environment tunneling
- **Analytics Stack**: Real-time data pipeline monitoring and debugging

## 🔧 Installation & Configuration

### Windows EQ12 Setup
```powershell
# Install via Chocolatey
choco install ngrok -y

# Verify installation
ngrok version

# Authenticate with token
ngrok config add-authtoken $env:NGROK_AUTHTOKEN
```

### Linux/Codespaces Setup
```bash
# Install via snap
sudo snap install ngrok

# Or via apt (Ubuntu/Debian)
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Authenticate
ngrok config add-authtoken $NGROK_AUTHTOKEN
```

### Environment Configuration
```bash
# Set environment variables
export NGROK_AUTHTOKEN="your_ngrok_token_here"
export NGROK_DOMAIN="eq12-godstack"  # Custom domain if available
export NGROK_REGION="us"             # Choose region: us, eu, ap, au, sa, jp, in
```

## 📋 Service Configuration

### Ngrok Configuration File (`ngrok.yml`)
```yaml
version: "2"
authtoken: ${NGROK_AUTHTOKEN}
region: ${NGROK_REGION}
log_level: info
log_format: json
log: /var/log/ngrok.log

tunnels:
  # Core Development Services
  dashboard:
    proto: http
    addr: 8000
    subdomain: eq12-dashboard
    auth: "${NGROK_BASIC_AUTH}"
    inspect: true
    bind_tls: true
    schemes: [https]
    
  api:
    proto: http
    addr: 5000
    subdomain: eq12-api
    auth: "${NGROK_BASIC_AUTH}"
    inspect: true
    bind_tls: true
    schemes: [https]
    
  # Monitoring & Metrics
  prometheus:
    proto: http
    addr: 9090
    subdomain: eq12-prometheus
    auth: "${NGROK_BASIC_AUTH}"
    inspect: false
    bind_tls: true
    schemes: [https]
    
  grafana:
    proto: http
    addr: 3000
    subdomain: eq12-grafana
    auth: "${NGROK_BASIC_AUTH}"
    inspect: false
    bind_tls: true
    schemes: [https]
    
  # Webhook Testing
  webhook:
    proto: http
    addr: 8080
    subdomain: eq12-webhook
    inspect: true
    bind_tls: true
    schemes: [https]
    
  # Business Stack Services
  betting-api:
    proto: http
    addr: 8001
    subdomain: eq12-betting
    auth: "${BETTING_STACK_AUTH}"
    inspect: true
    bind_tls: true
    schemes: [https]
    
  cannabis-compliance:
    proto: http
    addr: 8002
    subdomain: eq12-cannabis
    auth: "${CANNABIS_STACK_AUTH}"
    inspect: true
    bind_tls: true
    schemes: [https]
    
  credit-gateway:
    proto: http
    addr: 8003
    subdomain: eq12-credit
    auth: "${CREDIT_STACK_AUTH}"
    inspect: true
    bind_tls: true
    schemes: [https]

# Custom domains (if using ngrok pro)
custom_domains:
  - name: api.eq12-godstack.dev
    tunnel: api
  - name: dashboard.eq12-godstack.dev
    tunnel: dashboard
```

## 🚀 Automated Service Management

### Windows Task Scheduler Configuration
```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2024-01-20T09:00:00.000000</Date>
    <Author>EQ12 GODSTACK</Author>
    <Description>Auto-start ngrok tunnels for EQ12 GODSTACK development</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions>
    <Exec>
      <Command>C:\ProgramData\chocolatey\bin\ngrok.exe</Command>
      <Arguments>start --all --config=C:\EQ12\configs\ngrok.yml</Arguments>
      <WorkingDirectory>C:\EQ12</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
```

### Linux Systemd Service
```ini
# /etc/systemd/system/eq12-ngrok.service
[Unit]
Description=EQ12 GODSTACK Ngrok Tunnels
After=network.target
Wants=network.target

[Service]
Type=simple
User=eq12
Group=eq12
WorkingDirectory=/workspaces/EQ12
ExecStart=/usr/local/bin/ngrok start --all --config=/workspaces/EQ12/configs/ngrok.yml
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=eq12-ngrok

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/workspaces/EQ12/logs
ProtectHome=true

[Install]
WantedBy=multi-user.target
```

## 🔒 Security & Compliance Configuration

### Authentication & Access Control
```yaml
# Authentication configurations for different business stacks
auth_configs:
  basic_auth:
    development: "dev:eq12dev123"
    staging: "stage:eq12stage456"
    
  betting_stack:
    auth: "betting:${BETTING_STACK_PASSWORD}"
    compliance_required: true
    audit_logging: true
    
  cannabis_stack:
    auth: "cannabis:${CANNABIS_STACK_PASSWORD}"
    state_compliance: true
    metrc_integration: true
    
  credit_stack:
    auth: "credit:${CREDIT_STACK_PASSWORD}"
    pci_compliance: true
    encryption_required: true
```

### Security Headers & Policies
```bash
# Security configuration for sensitive stacks
export NGROK_SECURITY_HEADERS="X-Frame-Options: DENY, X-Content-Type-Options: nosniff, X-XSS-Protection: 1; mode=block"
export NGROK_CSP_POLICY="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow Integration
```yaml
# .github/workflows/ngrok-preview.yml
name: "Ngrok Preview Deployment"

on:
  pull_request:
    types: [opened, synchronize]
  workflow_dispatch:

jobs:
  deploy-preview:
    runs-on: ubuntu-latest
    if: github.event.pull_request.draft == false
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup ngrok
        run: |
          wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
          tar xvzf ngrok-v3-stable-linux-amd64.tgz
          sudo mv ngrok /usr/local/bin
          ngrok config add-authtoken ${{ secrets.NGROK_AUTHTOKEN }}
          
      - name: Build and start services
        run: |
          docker-compose up -d
          sleep 30  # Wait for services to start
          
      - name: Start ngrok tunnels
        run: |
          ngrok start dashboard api --config=configs/ngrok.yml &
          sleep 10
          
      - name: Get tunnel URLs
        id: tunnels
        run: |
          DASHBOARD_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[] | select(.name=="dashboard") | .public_url')
          API_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[] | select(.name=="api") | .public_url')
          
          echo "dashboard_url=$DASHBOARD_URL" >> $GITHUB_OUTPUT
          echo "api_url=$API_URL" >> $GITHUB_OUTPUT
          
      - name: Comment PR with preview links
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 🚀 Preview Deployment Ready
              
              **Dashboard**: ${{ steps.tunnels.outputs.dashboard_url }}
              **API**: ${{ steps.tunnels.outputs.api_url }}
              
              These links will be available for the duration of this PR review.
              
              ### Test Credentials
              - Username: \`preview\`
              - Password: \`eq12preview\`
              
              ⚠️ **Note**: These are temporary preview environments for testing purposes only.`
            })
```

## 📊 Monitoring & Logging

### Ngrok API Monitoring
```python
# scripts/ngrok_monitor.py
import requests
import json
import time
import logging
from datetime import datetime

class NgrokMonitor:
    def __init__(self, api_url="http://localhost:4040/api"):
        self.api_url = api_url
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        logger = logging.getLogger('ngrok_monitor')
        handler = logging.FileHandler('logs/ngrok_monitor.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
    
    def get_tunnel_status(self):
        """Get current tunnel status and metrics"""
        try:
            response = requests.get(f"{self.api_url}/tunnels")
            tunnels = response.json()['tunnels']
            
            status = {
                'timestamp': datetime.utcnow().isoformat(),
                'tunnel_count': len(tunnels),
                'tunnels': []
            }
            
            for tunnel in tunnels:
                tunnel_info = {
                    'name': tunnel['name'],
                    'public_url': tunnel['public_url'],
                    'proto': tunnel['proto'],
                    'metrics': tunnel.get('metrics', {})
                }
                status['tunnels'].append(tunnel_info)
            
            self.logger.info(f"Tunnel status check: {len(tunnels)} active tunnels")
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get tunnel status: {e}")
            return None
    
    def monitor_continuously(self, interval=60):
        """Continuously monitor tunnel health"""
        while True:
            status = self.get_tunnel_status()
            if status:
                # Log metrics to file for analysis
                with open('logs/ngrok_metrics.json', 'a') as f:
                    f.write(json.dumps(status) + '\n')
            
            time.sleep(interval)

if __name__ == "__main__":
    monitor = NgrokMonitor()
    monitor.monitor_continuously()
```

## 🎯 Business Stack Specific Configurations

### Betting Stack Integration
```yaml
# Betting stack specific tunneling
betting_tunnels:
  responsible_gaming_api:
    addr: 8001
    auth: "${BETTING_COMPLIANCE_AUTH}"
    custom_domain: "rg-api.eq12-betting.dev"
    compliance_logging: true
    
  odds_calculator:
    addr: 8002
    auth: "${BETTING_COMPLIANCE_AUTH}"
    rate_limit: "100/hour"
    audit_trail: true
```

### Cannabis Stack Integration
```yaml
# Cannabis compliance tunneling
cannabis_tunnels:
  metrc_integration:
    addr: 8003
    auth: "${CANNABIS_COMPLIANCE_AUTH}"
    state_specific: true
    inventory_tracking: true
    
  compliance_dashboard:
    addr: 8004
    auth: "${CANNABIS_AUDIT_AUTH}"
    regulatory_reporting: true
```

### Credit Stack Integration
```yaml
# PCI DSS compliant tunneling
credit_tunnels:
  payment_gateway:
    addr: 8005
    auth: "${CREDIT_SECURE_AUTH}"
    pci_compliance: true
    encryption: "AES-256"
    
  fraud_detection:
    addr: 8006
    auth: "${CREDIT_FRAUD_AUTH}"
    real_time_monitoring: true
```

## 🔄 Package Integration Strategy

### Container Deployment with Ngrok
```dockerfile
# Dockerfile.ngrok
FROM ngrok/ngrok:latest

# Copy ngrok configuration
COPY configs/ngrok.yml /etc/ngrok.yml

# Set up environment
ENV NGROK_AUTHTOKEN=""
ENV NGROK_CONFIG="/etc/ngrok.yml"

# Expose ngrok web interface
EXPOSE 4040

# Start ngrok with all tunnels
CMD ["ngrok", "start", "--all", "--config", "/etc/ngrok.yml"]
```

### Docker Compose Integration
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  eq12-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=postgresql://localhost/eq12_dev
    
  eq12-dashboard:
    build: ./dashboard
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=development
    
  ngrok:
    build:
      context: .
      dockerfile: Dockerfile.ngrok
    ports:
      - "4040:4040"
    environment:
      - NGROK_AUTHTOKEN=${NGROK_AUTHTOKEN}
    volumes:
      - ./configs/ngrok.yml:/etc/ngrok.yml:ro
      - ./logs:/var/log/ngrok
    depends_on:
      - eq12-api
      - eq12-dashboard
```

## 📋 Operational Procedures

### Tunnel Management Scripts
```powershell
# scripts/eq12_ngrok_manager.ps1
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "logs")]
    [string]$Action,
    
    [string]$Service = "all"
)

function Start-NgrokTunnels {
    param([string]$Service)
    
    Write-Host "🚀 Starting EQ12 Ngrok tunnels..." -ForegroundColor Green
    
    if ($Service -eq "all") {
        Start-Process -NoNewWindow -FilePath "ngrok" -ArgumentList "start", "--all", "--config=C:\EQ12\configs\ngrok.yml"
    } else {
        Start-Process -NoNewWindow -FilePath "ngrok" -ArgumentList "start", $Service, "--config=C:\EQ12\configs\ngrok.yml"
    }
    
    # Wait for tunnels to initialize
    Start-Sleep -Seconds 10
    
    # Display tunnel URLs
    Get-NgrokStatus
}

function Stop-NgrokTunnels {
    Write-Host "🛑 Stopping EQ12 Ngrok tunnels..." -ForegroundColor Yellow
    Get-Process -Name "ngrok" -ErrorAction SilentlyContinue | Stop-Process -Force
}

function Get-NgrokStatus {
    Write-Host "📊 EQ12 Ngrok Tunnel Status:" -ForegroundColor Cyan
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method Get
        
        foreach ($tunnel in $response.tunnels) {
            Write-Host "  🔗 $($tunnel.name): $($tunnel.public_url)" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Unable to retrieve tunnel status. Ngrok may not be running." -ForegroundColor Red
    }
}

function Get-NgrokLogs {
    if (Test-Path "C:\EQ12\logs\ngrok.log") {
        Get-Content "C:\EQ12\logs\ngrok.log" -Tail 50
    } else {
        Write-Host "❌ Ngrok log file not found." -ForegroundColor Red
    }
}

# Execute requested action
switch ($Action) {
    "start" { Start-NgrokTunnels -Service $Service }
    "stop" { Stop-NgrokTunnels }
    "restart" { 
        Stop-NgrokTunnels
        Start-Sleep -Seconds 5
        Start-NgrokTunnels -Service $Service
    }
    "status" { Get-NgrokStatus }
    "logs" { Get-NgrokLogs }
}
```

## 🎉 Benefits Summary

### Development Benefits
- **Rapid Prototyping**: Instant external access to local services
- **Cross-Device Testing**: Test mobile interfaces with real devices
- **Webhook Development**: Direct integration testing with external services
- **Team Collaboration**: Share development environments instantly

### Governance Benefits
- **Compliance Demos**: Secure stakeholder access to governance dashboards
- **Audit Support**: Temporary access for external compliance reviews
- **Incident Response**: Rapid deployment of emergency access tunnels
- **Documentation**: Live demonstration capabilities for process documentation

### Business Stack Benefits
- **🎰 Betting Stack**: Secure compliance testing without production exposure
- **🌿 Cannabis Stack**: State-specific integration testing and demos
- **💳 Credit Stack**: PCI-compliant development environment access
- **Analytics Stack**: Real-time data pipeline monitoring and debugging

---

**Implementation Priority**: High  
**Security Level**: Enterprise-grade with business stack awareness  
**Maintenance**: Automated with monitoring and alerting  
**Documentation**: Complete with operational procedures