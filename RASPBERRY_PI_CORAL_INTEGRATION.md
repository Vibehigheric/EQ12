# EQ12 Raspberry Pi 5 + Coral Network Integration Guide
# ====================================================

##  **ARCHITECTURE OVERVIEW**

```
Windows PC (EQ12 Host)
   Main EQ12 System (312 components)
   Coral USB Accelerator (host-connected)
   Docker Compose Cluster Manager
   Ethernet Network (Gigabit)
    
       Raspberry Pi 5 #1
          Coral USB Accelerator
          ARM64 Cortex-A76 (4 cores)
          8GB LPDDR4X RAM
          Edge Processing Node
    
       Raspberry Pi 5 #2 (optional)
          Data Processing Node
          Monitoring & Analytics
    
       Network Switch/Router
         DHCP: 192.168.1.1/24
         Pi #1: 192.168.1.100
         Pi #2: 192.168.1.101
         Host: 192.168.1.10
```

##  **IMPLEMENTATION BENEFITS**

### **Distributed AI Processing**
- **Coral TPU Load Balancing**: Host + Pi Coral accelerators work together
- **Parallel Inference**: Sports betting models run simultaneously on multiple nodes
- **Latency Reduction**: Edge processing reduces round-trip time for critical decisions

### **EQ12 System Enhancement**
- **Horizontal Scaling**: Add processing power without upgrading main system
- **Dedicated Edge Tasks**: Pi handles real-time monitoring while host manages heavy compute
- **Fault Tolerance**: System continues operating if any single node fails

### **Network Performance**
- **Gigabit Ethernet**: ~125MB/s data transfer between nodes
- **Low Latency**: <1ms ping time on local network
- **Reliable Connection**: Wired is more stable than WiFi for critical operations

##  **TECHNICAL CONFIGURATION**

### **1. Network Setup**
```powershell
# Configure static IP for Pi (on Pi):
sudo nano /etc/dhcpcd.conf

# Add these lines:
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# Restart networking
sudo reboot
```

### **2. Coral USB Configuration**
```bash
# Install Coral runtime on Pi
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt update
sudo apt install libedgetpu1-std python3-pycoral

# Test Coral detection
python3 -c "from pycoral.utils import edgetpu; print('Coral devices:', edgetpu.list_edge_tpus())"
```

### **3. EQ12 Integration Scripts**

#### **Host-side Cluster Manager**
```powershell
# Start cluster management
python C:\EQ12\scripts\eq12_raspberry_pi_cluster_manager.py --action discover
python C:\EQ12\scripts\eq12_raspberry_pi_cluster_manager.py --action add-node --ip 192.168.1.100
python C:\EQ12\scripts\eq12_raspberry_pi_cluster_manager.py --action start
```

#### **Docker Compose Orchestration**
```powershell
# Start distributed cluster
cd C:\EQ12
docker-compose -f docker-compose.pi-cluster.yml up -d

# Monitor cluster status
docker logs eq12-pi-coordinator
```

##  **USE CASES FOR EQ12 + PI CLUSTER**

### **Real-time Sports Analytics**
```python
# Submit betting analysis to Pi cluster
cluster.submit_edge_task(
    "coral_inference", 
    {
        "model_path": "/models/sports_ev_model.tflite",
        "game_data": current_odds_data,
        "confidence_threshold": 0.85
    }, 
    priority=9,
    requires_coral=True
)
```

### **Distributed Parlay Optimization**
```python
# Parallel parlay processing across nodes
cluster.submit_edge_task(
    "data_processing",
    {
        "operation": "parlay_optimization",
        "legs": available_betting_legs,
        "max_legs": 8,
        "min_ev": 0.05
    },
    priority=7
)
```

### **Continuous Market Monitoring**
```python
# Pi handles real-time market surveillance
cluster.submit_edge_task(
    "monitoring",
    {
        "operation": "odds_monitoring",
        "sportsbooks": ["draftkings", "fanduel", "caesars"],
        "alert_threshold": 0.03  # 3% EV threshold
    },
    priority=6
)
```

##  **PERFORMANCE EXPECTATIONS**

### **Processing Power Distribution**
- **Host PC**: Complex ML training, large dataset processing, UI/dashboard
- **Pi + Coral**: Real-time inference, edge analytics, monitoring
- **Combined**: 4-8x faster inference throughput for time-sensitive decisions

### **Network Throughput**
- **Gigabit Ethernet**: 125MB/s theoretical, ~90MB/s practical
- **Task Payload**: Typically 1-10KB, sub-millisecond transfer
- **Model Transfer**: 50MB models transfer in ~0.5 seconds

### **Latency Benefits**
- **Local Inference**: <50ms vs 200ms+ cloud processing
- **Edge Decisions**: Critical betting decisions made in real-time
- **Reduced Bottlenecks**: Host freed for strategic processing

##  **SECURITY CONSIDERATIONS**

### **Network Security**
```powershell
# SSH key authentication (recommended)
ssh-keygen -t rsa -b 4096 -f C:\EQ12\ssh_keys\eq12_cluster_key
scp C:\EQ12\ssh_keys\eq12_cluster_key.pub pi@192.168.1.100:~/.ssh/authorized_keys

# Disable password authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart ssh
```

### **Firewall Configuration**
```bash
# Pi firewall rules
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow from 192.168.1.0/24 to any port 22
sudo ufw allow from 192.168.1.0/24 to any port 8880:8890
```

##  **OPERATION WORKFLOWS**

### **Daily Startup Sequence**
1. **Power on Pi devices** (connected via ethernet)
2. **Start cluster coordinator** on host PC
3. **Auto-discovery** finds and configures Pi nodes
4. **Health check** verifies Coral TPU connectivity
5. **Task distribution** begins automatically

### **Betting Session Workflow**
1. **Host collects** live odds data from APIs
2. **Pi cluster processes** real-time analytics
3. **Coral TPUs execute** ML inference models
4. **Results aggregate** on host for decision making
5. **Alerts trigger** via Telegram for high-value opportunities

### **Monitoring & Maintenance**
- **Dashboard**: http://localhost:8880 (cluster status)
- **Grafana**: http://localhost:3001 (performance metrics)
- **Log aggregation**: C:\EQ12\logs\raspberry_pi_cluster_*.log

##  **INTEGRATION WITH EXISTING EQ12**

### **SCADA System Integration**
```python
# eq12_marketplace_scada_engine.py integration
from scripts.eq12_raspberry_pi_cluster_manager import RaspberryPiClusterManager

# Add cluster processing to SCADA
scada_engine.add_edge_processor(cluster_manager)
scada_engine.distribute_market_analysis_tasks()
```

### **Business Intelligence Enhancement**
```python
# eq12_ebay_intelligence.py distributed processing
cluster.submit_edge_task(
    "data_processing",
    {
        "operation": "market_analysis",
        "product_data": scraped_products,
        "competitive_analysis": True
    }
)
```

##  **COST-BENEFIT ANALYSIS**

### **Hardware Investment**
- **Raspberry Pi 5 (8GB)**: $80
- **Coral USB Accelerator**: $60
- **MicroSD Card (64GB)**: $15
- **Ethernet Cable**: $10
- **Total per node**: ~$165

### **Performance ROI**
- **4x faster inference**: More timely betting decisions
- **Parallel processing**: Handle 3x more opportunities simultaneously
- **Reduced latency**: 150ms faster response time
- **24/7 availability**: Continuous market monitoring

### **Business Value**
- **Increased EV capture**: Faster identification of profitable bets
- **Competitive advantage**: Real-time edge over slower systems
- **Scalability**: Add nodes as business grows
- **Reliability**: Distributed system reduces single points of failure

##  **GETTING STARTED**

1. **Install Raspberry Pi OS** on Pi 5 with 8GB RAM
2. **Connect Coral USB** accelerator to Pi
3. **Configure network** with static IP (192.168.1.100)
4. **Run cluster setup** from EQ12 host:
   ```powershell
   python C:\EQ12\scripts\eq12_raspberry_pi_cluster_manager.py --action add-node --ip 192.168.1.100 --username pi --password raspberry
   ```
5. **Start distributed processing**:
   ```powershell
   python C:\EQ12\scripts\eq12_raspberry_pi_cluster_manager.py --action start
   ```

The Raspberry Pi 5 + Coral integration transforms your EQ12 system into a powerful **distributed edge computing cluster**, enabling real-time AI-powered decision making across multiple processing nodes while maintaining the centralized intelligence of your main system.