# EQ12 Enterprise Platform Deployment Guide

## Prerequisites

### 1. System Requirements
- Python 3.12+ (production servers)
- PostgreSQL 14+ (primary database)
- Redis 7+ (caching and rate limiting)
- Docker + Docker Compose (containerized deployment)
- SSL Certificate (for production HTTPS)

### 2. Required Environment Variables
Create production `.env` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/eq12_enterprise
REDIS_URL=redis://redis-host:6379/0

# Security
SECRET_KEY=your-256-bit-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=your-fernet-encryption-key

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email Configuration
SENDGRID_API_KEY=SG.your-sendgrid-key
FROM_EMAIL=noreply@yourdomain.com

# OpenAI Integration
OPENAI_API_KEY=sk-...

# Domain Configuration
DOMAIN=yourdomain.com
API_BASE_URL=https://api.yourdomain.com

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
```

## Deployment Steps

### 1. Server Setup (Production)

```bash
# Create EQ12 user and directory
sudo useradd -m -s /bin/bash eq12
sudo mkdir -p /opt/eq12
sudo chown eq12:eq12 /opt/eq12

# Install system dependencies
sudo apt update
sudo apt install -y python3.12 python3.12-venv postgresql-client redis-tools nginx certbot

# Setup application
cd /opt/eq12
sudo -u eq12 git clone https://github.com/yourusername/EQ12.git
cd EQ12
sudo -u eq12 python3.12 -m venv venv
sudo -u eq12 source venv/bin/activate
sudo -u eq12 pip install -r requirements-enterprise.txt
```

### 2. Database Setup

```sql
-- Create PostgreSQL database and user
CREATE DATABASE eq12_enterprise;
CREATE USER eq12_api WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE eq12_enterprise TO eq12_api;

-- Connect to database and setup extensions
\c eq12_enterprise
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

```bash
# Run database migrations
cd /opt/eq12/EQ12
source venv/bin/activate
alembic upgrade head
```

### 3. Docker Deployment (Recommended)

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  eq12-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://eq12_api:${DB_PASSWORD}@postgres:5432/eq12_enterprise
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=eq12_enterprise
      - POSTGRES_USER=eq12_api
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - eq12-api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

```bash
# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Nginx Configuration

Create `/etc/nginx/sites-available/eq12-enterprise`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site and restart nginx
sudo ln -s /etc/nginx/sites-available/eq12-enterprise /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL Certificate Setup

```bash
# Get Let's Encrypt certificate
sudo certbot --nginx -d api.yourdomain.com
```

### 6. Systemd Service (Alternative to Docker)

Create `/etc/systemd/system/eq12-enterprise.service`:

```ini
[Unit]
Description=EQ12 Enterprise API
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=eq12
Group=eq12
WorkingDirectory=/opt/eq12/EQ12
Environment=PATH=/opt/eq12/EQ12/venv/bin
ExecStart=/opt/eq12/EQ12/venv/bin/gunicorn eq12_enterprise_api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable eq12-enterprise
sudo systemctl start eq12-enterprise
```

### 7. Stripe Webhook Configuration

1. In Stripe Dashboard, add webhook endpoint: `https://api.yourdomain.com/webhooks/stripe`
2. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
3. Copy webhook secret to environment variables

### 8. Monitoring Setup

```bash
# Install monitoring stack
docker run -d --name prometheus -p 9090:9090 prom/prometheus
docker run -d --name grafana -p 3000:3000 grafana/grafana

# Setup health checks
curl https://api.yourdomain.com/health
```

### 9. Database Backups

Create automated backup script `/opt/eq12/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/eq12/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump eq12_enterprise | gzip > $BACKUP_DIR/eq12_backup_$TIMESTAMP.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "eq12_backup_*.sql.gz" -mtime +7 -delete
```

Add to crontab:
```bash
sudo crontab -e
# Add: 0 2 * * * /opt/eq12/backup.sh
```

## Post-Deployment Verification

### 1. API Health Checks
```bash
# Check API status
curl https://api.yourdomain.com/health

# Test authentication
curl -X POST https://api.yourdomain.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'
```

### 2. Database Connection
```bash
# Test database connectivity
psql -h localhost -U eq12_api -d eq12_enterprise -c "SELECT COUNT(*) FROM customers;"
```

### 3. Stripe Integration
```bash
# Test Stripe webhook
curl -X POST https://api.yourdomain.com/webhooks/stripe \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: test" \
  -d '{"type": "test"}'
```

## Scaling Considerations

### 1. Load Balancing
- Use multiple API instances behind load balancer
- Implement session affinity for WebSocket connections

### 2. Database Scaling
- Setup PostgreSQL read replicas
- Implement connection pooling with PgBouncer

### 3. Caching Strategy
- Redis cluster for high availability
- CDN for static assets

### 4. Monitoring
- Application performance monitoring (APM)
- Log aggregation with ELK stack
- Real-time alerting

## Security Checklist

- [ ] SSL/TLS certificates configured
- [ ] Environment variables secured
- [ ] Database access restricted
- [ ] Rate limiting enabled
- [ ] API key rotation implemented
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Access logs monitored
- [ ] Vulnerability scanning automated
- [ ] Incident response plan documented

## Maintenance

### Regular Tasks
- Weekly security updates
- Monthly dependency updates
- Quarterly penetration testing
- Annual disaster recovery testing

### Performance Monitoring
- API response times < 200ms
- Database query optimization
- Memory usage monitoring
- Disk space monitoring

This deployment guide ensures enterprise-grade availability, security, and scalability for the EQ12 platform.
