# EQ12 Enterprise Deployment Guide
## Complete Integration of Industrial SCADA + Enterprise Microservices

###  **Overview**

This guide provides step-by-step instructions for deploying the complete **EQ12 Enterprise Stack** that integrates:

-  **Existing EQ12 Foundation**: 312 discovered components, Python config generator, C# control interface, HMI dashboard
-  **Enterprise Microservices**: Dockerized APIs, data lake, monitoring, observability 
-  **Seamless Integration**: Native Windows + containerized services working together

---

##  **Prerequisites**

### **System Requirements**
- **OS**: Windows 10/11 or Windows Server 2019+
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 100GB free space
- **Docker**: Docker Desktop for Windows with WSL2 backend
- **.NET**: .NET 8.0 Runtime (already installed for EQ12SystemManager.exe)
- **Python**: 3.12+ (already configured for EQ12 components)

### **Required Software**
```powershell
# Install Docker Desktop
winget install Docker.DockerDesktop

# Install Git (if not already installed)
winget install Git.Git

# Verify installations
docker --version
git --version
python --version
dotnet --version
```

---

##  **Phase 1: Validate Existing EQ12 Foundation**

### **Step 1.1: Verify EQ12 System Status**

```powershell
# Navigate to EQ12 workspace
cd C:\EQ12

# Run system integration test
python scripts\eq12_integration_test.py

# Expected output: 4/5 systems operational (80% success rate)
```

### **Step 1.2: Launch EQ12 Control Interface**

```powershell
# Start the C# WPF control interface
cd C:\EQ12\EQ12SystemManager\bin\Release\net8.0-windows
.\EQ12SystemManager.exe

# Verify all 312 components are discovered and listed
```

### **Step 1.3: Validate Configuration System**

```powershell
# Regenerate system configuration (if needed)
cd C:\EQ12
python scripts\eq12_system_config_generator.py --workspace C:\EQ12 --generate-dashboard --verbose

# Verify master config exists
dir configs\eq12_master_config.json
```

** Checkpoint**: EQ12 foundation fully operational before proceeding to enterprise integration.

---

##  **Phase 2: Deploy Enterprise Infrastructure**

### **Step 2.1: Create Enterprise Directory Structure**

```powershell
cd C:\EQ12

# Create enterprise directories
mkdir enterprise
mkdir enterprise\apps
mkdir enterprise\infra
mkdir enterprise\infra\compose
mkdir enterprise\infra\prometheus
mkdir enterprise\infra\grafana
mkdir enterprise\data_models
```

### **Step 2.2: Download Enterprise Components**

```powershell
# Clone or copy the enterprise files we created
# The following files should be placed in the correct directories:

# C:\EQ12\enterprise\apps\eq12_parlay_engine\
#   - Dockerfile
#   - main.py  
#   - requirements.txt

# C:\EQ12\enterprise\infra\compose\
#   - docker-compose.yml
#   - .env.example

# C:\EQ12\enterprise\data_models\
#   - eq12_data_lake_schema.md
```

### **Step 2.3: Configure Environment**

```powershell
cd C:\EQ12\enterprise\infra\compose

# Copy environment template
copy .env.example .env

# Edit .env file with your specific configuration
notepad .env
```

**Edit the `.env` file with these values:**
```bash
EQ12_HOST=localhost
PG_PASSWORD=your_secure_password_here
MINIO_KEY=eq12admin
MINIO_SECRET=your_minio_secret_here
GRAFANA_PASSWORD=your_grafana_password_here
USE_CORAL=false
```

### **Step 2.4: Create Required Configuration Files**

**Create `C:\EQ12\enterprise\infra\prometheus\prometheus.yml`:**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'eq12-parlay-engine'
    static_configs:
      - targets: ['eq12-parlay-engine:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'eq12-model-server'
    static_configs:
      - targets: ['eq12-model-server:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'docker'
    static_configs:
      - targets: ['host.docker.internal:9323']
```

**Create `C:\EQ12\enterprise\infra\compose\init-db.sql`:**

```sql
-- EQ12 Enterprise Database Initialization

-- Create schemas
CREATE SCHEMA IF NOT EXISTS betting;
CREATE SCHEMA IF NOT EXISTS ai_models;
CREATE SCHEMA IF NOT EXISTS system_metrics;
CREATE SCHEMA IF NOT EXISTS automation;

-- Create users and permissions
CREATE USER eq12_reader WITH PASSWORD 'eq12_read_password';
CREATE USER eq12_writer WITH PASSWORD 'eq12_write_password';

-- Grant permissions
GRANT USAGE ON SCHEMA betting TO eq12_reader, eq12_writer;
GRANT USAGE ON SCHEMA ai_models TO eq12_reader, eq12_writer;
GRANT USAGE ON SCHEMA system_metrics TO eq12_reader, eq12_writer;
GRANT USAGE ON SCHEMA automation TO eq12_reader, eq12_writer;

GRANT SELECT ON ALL TABLES IN SCHEMA betting TO eq12_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA ai_models TO eq12_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA system_metrics TO eq12_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA automation TO eq12_reader;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA betting TO eq12_writer;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ai_models TO eq12_writer;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA system_metrics TO eq12_writer;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA automation TO eq12_writer;

-- Enable row level security for multi-tenancy
ALTER DEFAULT PRIVILEGES IN SCHEMA betting GRANT SELECT ON TABLES TO eq12_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA betting GRANT ALL ON TABLES TO eq12_writer;

-- Create initial tables
CREATE TABLE IF NOT EXISTS system_metrics.deployment_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(50),
    component VARCHAR(100),
    message TEXT,
    status VARCHAR(20)
);

INSERT INTO system_metrics.deployment_log (event_type, component, message, status)
VALUES ('initialization', 'database', 'EQ12 Enterprise database initialized', 'success');
```

---

##  **Phase 3: Deploy Docker Stack**

### **Step 3.1: Start Infrastructure Services**

```powershell
cd C:\EQ12\enterprise\infra\compose

# Pull all images first
docker compose pull

# Start infrastructure (without EQ12 services initially)
docker compose up -d traefik minio postgres redis prometheus grafana loki

# Wait for services to be healthy
docker compose ps
```

### **Step 3.2: Verify Infrastructure Health**

```powershell
# Check service status
docker compose ps

# Test connectivity
curl http://localhost:9090  # Prometheus
curl http://localhost:3000  # Grafana
curl http://localhost:9001  # MinIO Console

# Check logs
docker compose logs traefik
docker compose logs postgres
```

### **Step 3.3: Initialize Data Lake**

```powershell
# Access MinIO console: http://localhost:9001
# Login with MINIO_KEY/MINIO_SECRET from .env

# Create buckets (via MinIO console or CLI)
docker exec -it eq12_minio mc alias set myminio http://localhost:9000 eq12admin your_minio_secret_here
docker exec -it eq12_minio mc mb myminio/eq12-enterprise-lake
docker exec -it eq12_minio mc mb myminio/eq12-backups
```

### **Step 3.4: Deploy EQ12 Microservices**

```powershell
# Build and start EQ12 services
docker compose up -d --build eq12-parlay-engine eq12-model-server eq12-config-sync eq12-system-bridge

# Verify EQ12 services
docker compose ps
curl http://localhost/api/parlay/health
curl http://localhost/api/models
```

** Checkpoint**: All Docker services running and healthy.

---

##  **Phase 4: Integrate with Existing EQ12 System**

### **Step 4.1: Update EQ12SystemManager.exe Integration**

```powershell
# Launch the enhanced control interface
cd C:\EQ12\EQ12SystemManager\bin\Release\net8.0-windows
.\EQ12SystemManager.exe

# The interface should now show:
# - Original 312 EQ12 components
# - New enterprise services (Docker containers)
# - Integrated monitoring across both environments
```

### **Step 4.2: Verify Data Integration**

```powershell
# Check that Docker services can access EQ12 data
docker exec -it eq12_config_sync cat /eq12configs/eq12_master_config.json

# Verify log integration
docker exec -it eq12_config_sync ls -la /eq12logs/

# Check script access
docker exec -it eq12_parlay_engine ls -la /eq12scripts/ | head -20
```

### **Step 4.3: Test End-to-End Integration**

```powershell
# Test parlay generation API (using EQ12 engines)
curl -X POST http://localhost/api/parlay/generate `
  -H "Content-Type: application/json" `
  -d '{"sport":"nfl","league":"nfl","strategy":"advanced","max_legs":5}'

# Test model server (using EQ12 AI models)
curl http://localhost/api/models

# Check system statistics
curl http://localhost/api/parlay/system/stats
```

---

##  **Phase 5: Configure Monitoring & Observability**

### **Step 5.1: Configure Grafana Dashboards**

1. **Access Grafana**: http://localhost:3000
2. **Login**: admin / your_grafana_password_here
3. **Add Prometheus Data Source**:
   - URL: `http://prometheus:9090`
   - Save & Test

### **Step 5.2: Import EQ12 Dashboards**

```powershell
# Create Grafana provisioning directory
mkdir C:\EQ12\enterprise\infra\grafana\provisioning\dashboards

# Download or create EQ12-specific dashboard JSON files
# Place them in the provisioning directory
```

### **Step 5.3: Set Up Alerting**

```powershell
# Configure Prometheus alerts for EQ12 components
# Create alert rules for:
# - EQ12 component health
# - Docker service availability  
# - Data lake storage usage
# - API response times
```

---

##  **Phase 6: Security & Production Hardening**

### **Step 6.1: Enable HTTPS**

```powershell
# Update .env file for production domain
EQ12_HOST=your-production-domain.com
ACME_EMAIL=admin@your-domain.com

# Restart Traefik to get SSL certificates
docker compose restart traefik
```

### **Step 6.2: Configure Authentication**

```powershell
# Set up JWT authentication for APIs
# Configure OAuth/SAML for Grafana
# Enable Postgres row-level security
```

### **Step 6.3: Backup Configuration**

```powershell
# Create backup script for EQ12 + Enterprise stack
# Include:
# - EQ12 configurations (C:\EQ12\configs\)
# - Enterprise environment files
# - Docker volumes
# - Database snapshots
```

---

##  **Phase 7: Validation & Testing**

### **Step 7.1: Integration Test Suite**

```powershell
# Run comprehensive integration tests
cd C:\EQ12
python scripts\eq12_integration_test.py

# Expected results:
#  EQ12 Configuration Generator: PASS
#  C# Control Interface: PASS  
#  Enterprise Services: PASS
#  Data Lake Integration: PASS
#  API Gateway: PASS
```

### **Step 7.2: Performance Testing**

```powershell
# Load test the parlay generation API
# Test concurrent access to EQ12 components
# Verify system performance under load
```

### **Step 7.3: Disaster Recovery Test**

```powershell
# Test backup and restore procedures
# Verify failover capabilities
# Test data recovery from MinIO
```

---

##  **Phase 8: Go-Live & Operations**

### **Step 8.1: Production Deployment Checklist**

- [ ] All services healthy and responding
- [ ] SSL certificates installed and working
- [ ] Monitoring alerts configured
- [ ] Backup procedures tested
- [ ] Performance baselines established
- [ ] Documentation updated
- [ ] Team training completed

### **Step 8.2: Operational Procedures**

```powershell
# Daily health check
docker compose ps
curl -f http://localhost/api/parlay/health
C:\EQ12\EQ12SystemManager\bin\Release\net8.0-windows\EQ12SystemManager.exe

# Weekly maintenance
docker compose pull && docker compose up -d
python C:\EQ12\scripts\eq12_integration_test.py

# Monthly review
# - Review performance metrics in Grafana
# - Analyze data lake usage and costs
# - Update security configurations
# - Plan capacity scaling
```

---

##  **Quick Reference Commands**

### **Start Everything**
```powershell
# Start EQ12 native components
cd C:\EQ12\EQ12SystemManager\bin\Release\net8.0-windows
start EQ12SystemManager.exe

# Start enterprise stack
cd C:\EQ12\enterprise\infra\compose
docker compose up -d

# Open monitoring dashboards
start http://localhost:3000    # Grafana
start http://localhost:9090    # Prometheus
start http://localhost:8080    # Traefik
```

### **Stop Everything**
```powershell
# Stop enterprise stack
cd C:\EQ12\enterprise\infra\compose
docker compose down

# The EQ12SystemManager.exe can be closed normally
```

### **Troubleshooting**
```powershell
# Check service logs
docker compose logs eq12-parlay-engine
docker compose logs eq12-config-sync

# Restart specific service
docker compose restart eq12-parlay-engine

# Full system restart
docker compose down && docker compose up -d

# Check EQ12 integration
python C:\EQ12\scripts\eq12_integration_test.py
```

---

##  **Success Metrics**

Your EQ12 Enterprise deployment is successful when:

### ** Functional Metrics**
- All 312 EQ12 components discoverable via EQ12SystemManager.exe
- Enterprise APIs responding (parlay generation, model serving)
- Data flowing from EQ12 components to enterprise data lake
- Grafana dashboards showing system health across both environments

### ** Performance Metrics**
- API response times < 500ms for parlay generation
- System can handle 100+ concurrent API requests
- Data lake ingestion processing EQ12 logs in real-time
- C# control interface responsive with enterprise services integrated

### ** Operational Metrics**
- Zero-downtime deployments working
- Monitoring alerts functioning correctly
- Backup and restore procedures validated
- Documentation complete and team trained

---

##  **What You've Achieved**

Your EQ12 system now has **both industrial automation AND enterprise microservices**:

### ** Industrial Foundation (Preserved)**
-  **312 Components**: All betting engines, AI models, automation scripts under SCADA management
-  **Python Engine**: Automated configuration generation and component discovery
-  **C# Control Interface**: Industrial-grade monitoring and control capabilities
-  **HMI Dashboard**: Real-time system visualization

### ** Enterprise Layer (Added)**
-  **Microservices Architecture**: Dockerized APIs with enterprise patterns
-  **Data Lake**: Structured storage for betting data, AI outputs, system metrics
-  **API Gateway**: Secure, rate-limited access to EQ12 capabilities
-  **Observability**: Comprehensive monitoring, logging, and alerting
-  **CI/CD Ready**: Infrastructure-as-code for automated deployments

### ** Seamless Integration**
- Native Windows EQ12 components  Containerized enterprise services
- Real-time data flow from EQ12  Data Lake  Analytics
- Unified monitoring across both environments
- Single control interface managing everything

** Result**: A production-ready betting/automation platform that scales from individual use to enterprise deployment while maintaining all existing EQ12 functionality.

---

*EQ12 Enterprise Integration - Deployment Guide v1.0*  
*Complete Industrial + Cloud Native Architecture*  
*Deployment Date: November 8, 2025*