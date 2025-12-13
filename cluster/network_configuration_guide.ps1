# EQ12 Cluster Network Configuration Guide
# Complete network setup for optimal Pi 5 cluster performance

# ================================================
# PHASE 1: DIRECT CONNECTION (TESTING)
# ================================================

# Current Setup (1 Pi via USB-Ethernet)
Write-Host "=== PHASE 1: Single Pi Direct Connection ===" -ForegroundColor Cyan

# EQ12 Master Configuration (Already Done)
# IP: 192.168.100.1/24
# USB-Ethernet Adapter: Static IP configured
# Status:  WORKING

# Pi 5 Node Configuration Required
$Phase1PiConfig = @"
# On Raspberry Pi 5:
sudo nano /etc/dhcpcd.conf

# Add these lines:
interface eth0
static ip_address=192.168.100.11/24
static routers=192.168.100.1
static domain_name_servers=8.8.8.8 1.1.1.1

# Restart networking:
sudo systemctl restart dhcpcd
sudo reboot

# Test connectivity:
ping 192.168.100.1
"@

Write-Host $Phase1PiConfig -ForegroundColor Green
Write-Host "`n Phase 1 enables basic testing with 1 Pi node`n" -ForegroundColor Yellow

# ================================================
# PHASE 2: SWITCH-BASED CLUSTER (4-6 NODES)
# ================================================

Write-Host "=== PHASE 2: Gigabit Switch Cluster (4-6 Nodes) ===" -ForegroundColor Cyan

# Hardware Requirements
$Phase2Hardware = @{
    "Switch" = "NETGEAR GS108PP (8-port PoE+) - $89"
    "Cables" = "6 Cat6 patch cables (3ft) - $24"
    "Power"  = "PoE+ budget: 83W (sufficient for 6 Pi nodes)"
    "Uplink" = "EQ12  Switch via Gigabit Ethernet"
}

$Phase2Hardware.GetEnumerator() | ForEach-Object {
    Write-Host "  $($_.Key): $($_.Value)" -ForegroundColor White
}

# Network Topology
$Phase2Topology = @"


            PHASE 2 TOPOLOGY             

                                         
  Internet  Router  EQ12 Master    
                                        
                             Gigabit    
                                        
                          
                      8-Port PoE+      
                        Switch         
                          
                                        
           
                                       
                                       
       Pi-Node-01      Pi-Node-02   Pi-Node-03
       .100.11         .100.12      .100.13
                                         
                                       
                                       
       Pi-Node-04      Pi-Node-05   Pi-Node-06
       .100.14         .100.15      .100.16
                                         


"@

Write-Host $Phase2Topology -ForegroundColor Cyan

# Network Configuration Script
$Phase2NetworkSetup = @"
# EQ12 Master Network Reconfiguration
# Change from USB-Ethernet to built-in Gigabit

# 1. Disable USB-Ethernet adapter
Get-NetAdapter "Ethernet 3" | Disable-NetAdapter -Confirm:`$false

# 2. Configure built-in Gigabit adapter  
New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 192.168.100.1 -PrefixLength 24 -DefaultGateway 192.168.100.2
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses "8.8.8.8", "1.1.1.1"

# 3. Enable IP forwarding for cluster routing
Set-NetIPInterface -InterfaceAlias "Ethernet" -Forwarding Enabled

# 4. Configure Windows firewall for cluster traffic
New-NetFirewallRule -DisplayName "EQ12 Cluster Traffic" -Direction Inbound -Protocol TCP -LocalPort 8080-8095 -Action Allow
New-NetFirewallRule -DisplayName "EQ12 Pi Nodes" -Direction Inbound -Protocol Any -RemoteAddress 192.168.100.0/24 -Action Allow
"@

Write-Host "Network Setup Commands:" -ForegroundColor Yellow
Write-Host $Phase2NetworkSetup -ForegroundColor Green
Write-Host "`n Phase 2 enables 4-6 Pi nodes with PoE+ power`n" -ForegroundColor Yellow

# ================================================
# PHASE 3: PRODUCTION CLUSTER (8-12 NODES)
# ================================================

Write-Host "=== PHASE 3: Production Scale Cluster (8-12 Nodes) ===" -ForegroundColor Cyan

# Hardware Requirements
$Phase3Hardware = @{
    "Switch" = "NETGEAR GS728TP (24-port PoE+) - $349"
    "Cables" = "15 Cat6 patch cables (various lengths) - $60"
    "Power"  = "PoE+ budget: 380W (supports 12 Pi + headroom)"
    "Rack"   = "4U network rack or desktop switch stand - $75"
    "UPS"    = "CyberPower CP500AVR (500VA) - $119"
}

$Phase3Hardware.GetEnumerator() | ForEach-Object {
    Write-Host "  $($_.Key): $($_.Value)" -ForegroundColor White
}

# Advanced Network Features
$Phase3Features = @"
 VLAN Configuration:
  - VLAN 10: AI Inference Traffic (High Priority)
  - VLAN 20: Cross-listing Automation (Medium Priority)  
  - VLAN 30: Monitoring & Management (Low Priority)
  - VLAN 99: Quarantine/Isolation

 QoS Priority Classes:
  1. TPU Inference (Highest) - 50% bandwidth guarantee
  2. Cluster Coordination - 25% bandwidth guarantee
  3. Web Automation - 15% bandwidth allocation
  4. Background Tasks - 10% bandwidth allocation

 Security Features:
  - Port security (MAC address binding)
  - Storm control (broadcast/multicast limiting)
  - Access control lists (ACLs)
  - SNMP monitoring for switch health

 Link Aggregation:
  - 2 Gigabit uplinks to EQ12 (LACP bond)
  - Failover redundancy for critical traffic
  - Load balancing for maximum throughput
"@

Write-Host $Phase3Features -ForegroundColor Green

# Complete IP Allocation Table
$IPAllocationTable = @"

      DEVICE           IP ADDRESS           ROLE             SPECIALIZATION 

 EQ12 Master        192.168.100.1      Cluster Master     Coordination      
 Router/Gateway     192.168.100.2      Internet Gateway   WAN Connection    
 Network Switch     192.168.100.3      Managed Switch     SNMP Management   
 UPS Management     192.168.100.4      Power Management   SNMP Monitoring   
 [Reserved]         192.168.100.5-10   Future Infra       Expansion         

 Pi Node 01         192.168.100.11     Primary Worker     AI Inference      
 Pi Node 02         192.168.100.12     Secondary Worker   AI Inference      
 Pi Node 03         192.168.100.13     Inference Spec.    TPU Specialist    
 Pi Node 04         192.168.100.14     Cross-list Worker  eBay Automation   
 Pi Node 05         192.168.100.15     Cross-list Worker  Mercari Auto      
 Pi Node 06         192.168.100.16     Cross-list Worker  Facebook Market   
 Pi Node 07         192.168.100.17     Scraping Worker    Data Collection   
 Pi Node 08         192.168.100.18     Backup/Failover    Hot Standby       
 Pi Node 09         192.168.100.19     Load Balancer      Traffic Mgmt      
 Pi Node 10         192.168.100.20     Monitor Special    Health Tracking   
 Pi Node 11         192.168.100.21     Development        Testing/Debug     
 Pi Node 12         192.168.100.22     Expansion          Overflow Tasks    

 DHCP Pool          192.168.100.100+   Temporary Devices  Laptops/Phones    

"@

Write-Host $IPAllocationTable -ForegroundColor Cyan
Write-Host "`n Phase 3 enables full production cluster with enterprise features`n" -ForegroundColor Yellow

# ================================================
# PHASE 4: ADVANCED SCALING (16-20 NODES)
# ================================================

Write-Host "=== PHASE 4: Enterprise Scale (16-20+ Nodes) ===" -ForegroundColor Cyan

$Phase4Architecture = @"
 ADVANCED CLUSTER ARCHITECTURE:


                    ENTERPRISE TOPOLOGY                         

                                                                 
  Internet  [Firewall]  [Core Switch]  EQ12 Master     
                                                               
                                               
                                                              
                                   
                     Access Sw #1   Access Sw #2              
                     (12 Pi nodes)  (8 Pi nodes)              
                                   
                                                                 
  Software Stack:                                               
   Kubernetes Orchestration                                  
   Redis Cluster (3 masters + 3 replicas)                   
   MQTT Message Broker (Mosquitto cluster)                  
   InfluxDB Time Series Database                            
   ELK Stack (Elasticsearch + Logstash + Kibana)           
   Prometheus + Grafana Monitoring                          
                                                                 


 PERFORMANCE TARGETS:
   5,000+ inferences per hour cluster-wide
   < 0.1% system downtime (99.9% availability)
   Automatic scaling based on workload
   Multi-region failover capability
   Real-time analytics and ML model training

 INVESTMENT: ~$2,500 additional hardware
 ROI: Break-even in 6-8 weeks with full utilization
"@

Write-Host $Phase4Architecture -ForegroundColor Green

# ================================================
# NETWORK OPTIMIZATION SETTINGS
# ================================================

Write-Host "`n=== NETWORK OPTIMIZATION RECOMMENDATIONS ===" -ForegroundColor Cyan

$NetworkOptimizations = @"
 Windows Network Optimizations (EQ12 Master):

# Disable unnecessary network services
Disable-NetAdapterBinding -Name "Ethernet" -ComponentID ms_tcpip6, ms_lltdio, ms_rspndr

# Optimize TCP settings for cluster traffic
netsh int tcp set global autotuninglevel=normal
netsh int tcp set global chimney=enabled
netsh int tcp set global rss=enabled
netsh int tcp set global netdma=enabled

# Increase network buffer sizes
netsh int tcp set global maxsynretransmissions=2
netsh int tcp set global initalretransmissiontime=1000

# Configure receive side scaling
netsh int tcp set global rss=enabled
netsh int tcp set global rssprofile=closestprocessor

 Raspberry Pi Network Optimizations:

# Increase network buffer sizes
echo 'net.core.rmem_max = 16777216' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem = 4096 65536 16777216' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem = 4096 65536 16777216' | sudo tee -a /etc/sysctl.conf

# Optimize for low latency
echo 'net.ipv4.tcp_congestion_control = bbr' | sudo tee -a /etc/sysctl.conf
echo 'net.core.default_qdisc = fq' | sudo tee -a /etc/sysctl.conf

# Apply settings
sudo sysctl -p

 Performance Monitoring Commands:

# Monitor network traffic (EQ12)
Get-NetAdapterStatistics | Select-Object Name, BytesReceived, BytesSent, PacketsReceived, PacketsSent

# Monitor cluster connectivity
Test-NetConnection -ComputerName 192.168.100.11 -Port 8080 -InformationLevel Detailed

# Monitor bandwidth utilization  
typeperf "\Network Interface(*)\Bytes Total/sec" -sc 60 -si 1

# Pi node network monitoring
iftop -i eth0                    # Real-time traffic
nethogs eth0                     # Process-level bandwidth  
ss -tuln                         # Active connections
ping -c 10 192.168.100.1         # Latency test
"@

Write-Host $NetworkOptimizations -ForegroundColor Green

# ================================================
# TROUBLESHOOTING GUIDE
# ================================================

Write-Host "`n=== NETWORK TROUBLESHOOTING GUIDE ===" -ForegroundColor Cyan

$TroubleshootingSteps = @"
 COMMON ISSUES & SOLUTIONS:

 Issue: Pi node not getting IP address
 Solution:
   1. Check DHCP is disabled on router for 192.168.100.0/24
   2. Verify static IP configuration in /etc/dhcpcd.conf
   3. Restart networking: sudo systemctl restart dhcpcd
   4. Check cable connection and switch port LED

 Issue: EQ12 can't reach Pi nodes  
 Solution:
   1. Verify EQ12 has route to Pi subnet: route print
   2. Check Windows firewall rules: Get-NetFirewallRule
   3. Test connectivity: Test-NetConnection 192.168.100.11
   4. Verify switch configuration and VLAN settings

 Issue: Slow inference performance
 Solution:
   1. Check network latency: ping -t 192.168.100.11
   2. Monitor bandwidth usage: Get-NetAdapterStatistics  
   3. Verify QoS settings on switch
   4. Check for network congestion or packet loss

 Issue: Random node disconnections
 Solution:
   1. Check PoE+ power budget on switch
   2. Verify cable quality (Cat6 recommended)
   3. Monitor switch temperature and fan status
   4. Check for power supply fluctuations with UPS

 DIAGNOSTIC COMMANDS:

# Complete network diagnosis script
ping 192.168.100.1                    # Master connectivity
ping 192.168.100.11                   # Pi node connectivity  
nslookup google.com                    # DNS resolution
tracert 8.8.8.8                       # Route tracing
netstat -an | findstr :8080           # Service port status

# Switch management (if supported)
# Access switch web interface: http://192.168.100.3
# Check port status, VLAN config, PoE usage
# Monitor traffic statistics and error counters

 ESCALATION PROCEDURES:

1. Level 1: Check cables, power, basic connectivity
2. Level 2: Review switch logs, analyze traffic patterns  
3. Level 3: Packet capture analysis, replace hardware
4. Level 4: Redesign network topology, upgrade infrastructure
"@

Write-Host $TroubleshootingSteps -ForegroundColor Yellow

# ================================================
# DEPLOYMENT SUMMARY
# ================================================

Write-Host "`n=== DEPLOYMENT PHASE SUMMARY ===" -ForegroundColor Cyan

$DeploymentSummary = @"
 RECOMMENDED DEPLOYMENT SEQUENCE:

Week 1-2: PHASE 1 (Foundation)
   Current: EQ12 + 1 Pi via USB-Ethernet (WORKING)
   Goal: Validate cluster basics, test TPU load balancing
   Cost: $0 (using existing equipment)
  
Week 3-4: PHASE 2 (Core Cluster)  
   Hardware: 8-port PoE+ switch + 3 more Pi nodes
   Goal: 4-node production cluster with automated failover
   Cost: ~$400 (switch + 3 Pi + TPUs + accessories)
  
Week 5-8: PHASE 3 (Production Scale)
   Hardware: 24-port PoE+ switch + 8 more Pi nodes  
   Goal: Full 12-node cluster with enterprise monitoring
   Cost: ~$1,100 (upgrade switch + 8 Pi + infrastructure)
  
Week 9+: PHASE 4 (Enterprise Scale)
   Hardware: Additional switches + up to 8 more Pi nodes
   Goal: 20-node cluster with Kubernetes orchestration
   Cost: ~$1,000 (depends on expansion requirements)

 IMMEDIATE NEXT STEPS:

1. Test current Phase 1 setup (EQ12 + 1 Pi)
   - Configure Pi static IP: 192.168.100.11/24
   - Run TPU load balancer test
   - Validate cross-listing automation

2. Order Phase 2 hardware:
   - NETGEAR GS108PP 8-port PoE+ switch ($89)
   - 3 Raspberry Pi 5 (8GB) ($240)  
   - 3 Google Coral USB TPU ($225)
   - Cat6 patch cables ($24)

3. Deploy Phase 2 cluster:
   - Run deploy_eq12_cluster.ps1 script
   - Configure switch with VLANs and QoS
   - Bootstrap Pi nodes with automation

4. Scale to Phase 3 when ready:
   - Upgrade to 24-port switch
   - Add remaining 8 Pi nodes
   - Enable advanced monitoring and optimization

 SUCCESS METRICS:

Phase 1: 95%+ task completion, < 50ms latency
Phase 2: 500+ inferences/hour, automatic failover working  
Phase 3: 2000+ inferences/hour, < 1% downtime
Phase 4: 5000+ inferences/hour, real-time optimization

Total ROI: Break-even in < 2 months with conservative projections
"@

Write-Host $DeploymentSummary -ForegroundColor Green

Write-Host "`n EQ12 Multi-Pi Cluster Network Guide Complete!" -ForegroundColor Yellow
Write-Host " Next: Run deploy_eq12_cluster.ps1 to start Phase 2 deployment" -ForegroundColor Cyan