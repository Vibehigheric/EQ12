# EQ12 Operations Runbook

##  Quick Start Commands

### Bootstrap Development Environment
```powershell
# Initialize development environment
.\ops\bootstrap.ps1

# Start all services
.\ops\make.ps1 up

# Run health checks
.\ops\make.ps1 test
```

### Daily Operations
```powershell
# Code quality check
.\ops\make.ps1 lint

# Run test suite  
.\ops\make.ps1 test

# Build containers
.\ops\make.ps1 build

# View logs
docker-compose logs -f godstack
```

---

##  Service Management

### Docker Services Status
```powershell
# Check all services
docker-compose ps

# View specific service logs
docker-compose logs -f [service_name]

# Restart specific service
docker-compose restart [service_name]

# Scale service
docker-compose up -d --scale godstack=3
```

### Individual Service Commands
```powershell
# EQ12 Godstack (Main Application)
docker-compose exec godstack python -c "print('Health Check')"

# Redis Cache
docker-compose exec redis redis-cli ping

# PostgreSQL Database  
docker-compose exec postgres psql -U eq12 -d eq12 -c "\dt"

# Grafana Monitoring
# Access: http://localhost:3000
# Default: admin/admin
```

---

##  Troubleshooting

### Common Issues

#### Service Won't Start
```powershell
# Check service logs
docker-compose logs [service_name]

# Verify environment variables
cat .env

# Check port conflicts
netstat -an | findstr ":8000"

# Rebuild container
docker-compose build --no-cache [service_name]
docker-compose up -d [service_name]
```

#### Database Connection Issues
```powershell
# Test PostgreSQL connection
docker-compose exec postgres psql -U eq12 -d eq12 -c "SELECT 1;"

# Check Redis connection
docker-compose exec redis redis-cli ping

# Verify network connectivity
docker network ls
docker network inspect eq12_default
```

#### Performance Issues
```powershell
# Check container resource usage
docker stats

# Monitor system resources
Get-WmiObject -Class Win32_Processor | Select-Object LoadPercentage
Get-WmiObject -Class Win32_OperatingSystem | Select-Object @{Name="MemoryUsage";Expression={"{0:N2}" -f ((($_.TotalVisibleMemorySize - $_.AvailableMemory)*100)/ $_.TotalVisibleMemorySize)}}
```

### Log Analysis
```powershell
# Application logs
Get-Content -Path ".\logs\*.log" | Select-String "ERROR"

# Container logs with timestamps
docker-compose logs -f -t godstack

# Search for specific errors
docker-compose logs godstack 2>&1 | Select-String "Exception"
```

---

##  Monitoring & Health Checks

### Service Health Endpoints
- **Main App**: http://localhost:8000/health
- **Redis**: `redis-cli ping`
- **PostgreSQL**: Connection test via psql
- **Grafana**: http://localhost:3000

### Key Metrics to Monitor
```powershell
# Application metrics
curl http://localhost:8000/metrics

# System metrics
Get-Counter "\Process(docker)\% Processor Time"
Get-Counter "\Memory\Available MBytes"

# Database performance
docker-compose exec postgres psql -U eq12 -d eq12 -c "SELECT * FROM pg_stat_activity;"
```

### Alert Conditions
- Memory usage > 80%
- CPU usage > 90% for 5+ minutes
- Disk space < 10GB
- Service response time > 5 seconds
- Database connection pool exhausted

---

##  Security Operations

### Secret Management
```powershell
# Verify no secrets in git history
gitleaks detect --source . --verbose

# Check environment files
Select-String -Path .env* -Pattern "REPLACE_ME"

# Rotate API keys (manual process)
# 1. Generate new keys in provider dashboards
# 2. Update .env file
# 3. Restart services: docker-compose restart
```

### Security Scanning
```powershell
# Python dependency scan
pip-audit

# Node.js dependency scan  
npm audit

# Container security scan
docker scan eq12:latest
```

### Backup Procedures
```powershell
# Database backup
docker-compose exec postgres pg_dump -U eq12 eq12 > backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# Volume backup
docker-compose exec godstack tar -czf /tmp/data_backup.tar.gz /home/appuser/app/data
docker cp $(docker-compose ps -q godstack):/tmp/data_backup.tar.gz ./backups/

# Configuration backup
Copy-Item -Recurse -Path .\configs -Destination .\backups\configs_$(Get-Date -Format "yyyyMMdd_HHmmss")
```

---

##  Incident Response

### Service Down
1. **Immediate Response**
   ```powershell
   # Check service status
   docker-compose ps
   
   # View recent logs  
   docker-compose logs --tail=100 [service_name]
   
   # Attempt restart
   docker-compose restart [service_name]
   ```

2. **Investigation**
   ```powershell
   # Check system resources
   Get-WmiObject Win32_ComputerSystem
   
   # Review error patterns
   Select-String -Path .\logs\*.log -Pattern "ERROR|CRITICAL"
   
   # Validate configuration
   docker-compose config
   ```

3. **Recovery**
   ```powershell
   # Rollback to last known good state
   git checkout HEAD~1
   docker-compose down
   docker-compose up -d
   
   # Or restore from backup
   # See backup procedures above
   ```

### Data Corruption
1. **Stop affected services**
   ```powershell
   docker-compose stop godstack postgres
   ```

2. **Assess damage**
   ```powershell
   # Check database integrity
   docker-compose run --rm postgres psql -U eq12 -d eq12 -c "SELECT * FROM pg_stat_database;"
   
   # Verify file system
   docker-compose run --rm godstack find /home/appuser/app/data -type f -exec md5sum {} \;
   ```

3. **Restore from backup**
   ```powershell
   # Restore database
   cat backup_latest.sql | docker-compose exec -T postgres psql -U eq12 -d eq12
   
   # Restore data files
   docker cp ./backups/data_latest.tar.gz $(docker-compose ps -q godstack):/tmp/
   docker-compose exec godstack tar -xzf /tmp/data_latest.tar.gz -C /home/appuser/app/
   ```

---

##  Maintenance Procedures

### Daily Maintenance
```powershell
# Log rotation
Get-ChildItem .\logs\*.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item

# Cache cleanup
docker-compose exec redis redis-cli FLUSHDB

# Temporary file cleanup
docker-compose exec godstack find /tmp -type f -mtime +1 -delete
```

### Weekly Maintenance
```powershell
# Update dependencies
pip install --upgrade pip
pip list --outdated

# Docker cleanup
docker system prune -f

# Security updates
docker-compose pull
docker-compose up -d
```

### Monthly Maintenance  
```powershell
# Full database backup
.\scripts\backup_database.ps1

# Performance analysis
.\scripts\performance_report.ps1

# Security audit
gitleaks detect --source . --report-path monthly_security_report.json
```

---

##  Emergency Contacts

### Internal Team
- **DevOps Lead**: [Contact Information]
- **Security Officer**: [Contact Information]  
- **Database Admin**: [Contact Information]

### External Vendors
- **Cloud Provider**: [Support Information]
- **Monitoring Service**: [Support Information]
- **Security Vendor**: [Support Information]

---

##  Reference Links

### Documentation
- [EQ12 Architecture](./ARCHITECTURE.md)
- [Security Policies](../SECURITY.md)
- [API Documentation](./API_REFERENCE.md)

### Tools
- **Docker**: https://docs.docker.com/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Redis**: https://redis.io/documentation
- **Grafana**: https://grafana.com/docs/

### Monitoring Dashboards
- **Application**: http://localhost:3000/d/app
- **Infrastructure**: http://localhost:3000/d/infra
- **Security**: http://localhost:3000/d/security

---

*Last Updated: November 10, 2025*  
*Document Version: 1.0*  
*Owner: Expert Quantum Team*