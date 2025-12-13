#!/bin/bash

# EQ12 Enterprise Deployment Script
# Supports Docker Compose and Kubernetes deployment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EQ12_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/tmp/eq12-deploy-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Usage function
usage() {
    cat << EOF
EQ12 Enterprise Deployment Script

Usage: $0 [OPTIONS] COMMAND

Commands:
    docker-deploy       Deploy using Docker Compose
    k8s-deploy         Deploy to Kubernetes
    docker-stop        Stop Docker deployment
    k8s-stop           Stop Kubernetes deployment
    status             Check deployment status
    logs               View logs
    backup             Create backup
    restore            Restore from backup
    upgrade            Upgrade to latest version
    health-check       Run health checks

Options:
    -e, --env FILE     Environment file (default: .env)
    -n, --namespace    Kubernetes namespace (default: eq12)
    -d, --domain       Custom domain name
    -s, --ssl          Enable SSL/TLS
    -m, --monitoring   Enable monitoring stack
    -b, --backup-dir   Backup directory
    -v, --verbose      Verbose output
    -h, --help         Show this help

Examples:
    $0 docker-deploy --env production.env --ssl --monitoring
    $0 k8s-deploy --namespace eq12-prod --domain api.example.com
    $0 status
    $0 backup --backup-dir /backups/eq12

EOF
}

# Default values
DEPLOYMENT_TYPE=""
ENV_FILE=".env"
NAMESPACE="eq12"
DOMAIN=""
ENABLE_SSL=false
ENABLE_MONITORING=false
BACKUP_DIR="/tmp/eq12-backups"
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENV_FILE="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -s|--ssl)
            ENABLE_SSL=true
            shift
            ;;
        -m|--monitoring)
            ENABLE_MONITORING=true
            shift
            ;;
        -b|--backup-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        docker-deploy|k8s-deploy|docker-stop|k8s-stop|status|logs|backup|restore|upgrade|health-check)
            DEPLOYMENT_TYPE="$1"
            shift
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Check if command was provided
if [[ -z "$DEPLOYMENT_TYPE" ]]; then
    error "No command provided. Use -h for help."
fi

# Verbose logging
if [[ "$VERBOSE" == "true" ]]; then
    set -x
fi

# Pre-flight checks
preflight_checks() {
    log "Running pre-flight checks..."

    # Check if running as root (for Docker)
    if [[ "$DEPLOYMENT_TYPE" == "docker-deploy" ]] && [[ $EUID -eq 0 ]]; then
        warn "Running as root. Consider using a non-root user for security."
    fi

    # Check Docker availability
    if [[ "$DEPLOYMENT_TYPE" =~ ^docker ]]; then
        if ! command -v docker &> /dev/null; then
            error "Docker is not installed or not in PATH"
        fi

        if ! command -v docker-compose &> /dev/null; then
            error "Docker Compose is not installed or not in PATH"
        fi

        if ! docker info &> /dev/null; then
            error "Docker daemon is not running"
        fi
    fi

    # Check Kubernetes availability
    if [[ "$DEPLOYMENT_TYPE" =~ ^k8s ]]; then
        if ! command -v kubectl &> /dev/null; then
            error "kubectl is not installed or not in PATH"
        fi

        if ! kubectl cluster-info &> /dev/null; then
            error "Cannot connect to Kubernetes cluster"
        fi
    fi

    # Check environment file
    if [[ ! -f "$SCRIPT_DIR/$ENV_FILE" ]]; then
        warn "Environment file $ENV_FILE not found. Creating default..."
        create_default_env
    fi

    success "Pre-flight checks completed"
}

# Create default environment file
create_default_env() {
    cat > "$SCRIPT_DIR/$ENV_FILE" << EOF
# EQ12 Enterprise Configuration

# Database
POSTGRES_PASSWORD=change_me_secure_password
REDIS_PASSWORD=change_me_redis_password

# Security
JWT_SECRET=change_me_jwt_secret_$(openssl rand -hex 32)
EQ12_API_KEY=eq12_$(openssl rand -hex 32)

# GitHub App Configuration
GITHUB_APP_ID=your_github_app_id
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_APP_ID_PR=your_pr_app_id
GITHUB_WEBHOOK_SECRET_PR=your_pr_webhook_secret

# Monitoring
GRAFANA_PASSWORD=change_me_grafana_password

# SSL/TLS
DOMAIN_NAME=${DOMAIN:-localhost}
SSL_EMAIL=admin@${DOMAIN:-example.com}
EOF

    warn "Default environment file created at $SCRIPT_DIR/$ENV_FILE"
    warn "Please edit the file and update all passwords and keys before deployment!"
}

# Docker deployment
docker_deploy() {
    log "Starting Docker deployment..."

    cd "$SCRIPT_DIR"

    # Source environment variables
    source "$ENV_FILE"

    # Create necessary directories
    mkdir -p logs ssl nginx monitoring/{prometheus,grafana,loki}

    # Generate SSL certificates if enabled
    if [[ "$ENABLE_SSL" == "true" ]]; then
        generate_ssl_certificates
    fi

    # Create monitoring configuration if enabled
    if [[ "$ENABLE_MONITORING" == "true" ]]; then
        create_monitoring_config
    fi

    # Start services
    log "Starting EQ12 services..."
    docker-compose up -d

    # Wait for services to be ready
    wait_for_services_docker

    success "Docker deployment completed successfully!"
    log "Access the EQ12 dashboard at: http${ENABLE_SSL:+s}://${DOMAIN:-localhost}"
}

# Kubernetes deployment
k8s_deploy() {
    log "Starting Kubernetes deployment..."

    cd "$SCRIPT_DIR"

    # Create namespace
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    # Create secrets from environment file
    create_k8s_secrets

    # Apply manifests
    log "Applying Kubernetes manifests..."
    kubectl apply -f k8s-manifests.yml -n "$NAMESPACE"

    # Wait for services to be ready
    wait_for_services_k8s

    success "Kubernetes deployment completed successfully!"

    # Get ingress IP
    if kubectl get ingress eq12-ingress -n "$NAMESPACE" &> /dev/null; then
        INGRESS_IP=$(kubectl get ingress eq12-ingress -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        if [[ -n "$INGRESS_IP" ]]; then
            log "Access the EQ12 API at: https://$INGRESS_IP"
        fi
    fi
}

# Generate SSL certificates
generate_ssl_certificates() {
    log "Generating SSL certificates..."

    if [[ -n "$DOMAIN" ]]; then
        # Use Let's Encrypt (requires certbot)
        if command -v certbot &> /dev/null; then
            certbot certonly --standalone -d "$DOMAIN" --email "${SSL_EMAIL:-admin@$DOMAIN}" --agree-tos --non-interactive
            cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ssl/
            cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ssl/
        else
            warn "Certbot not found, generating self-signed certificates"
            generate_self_signed_certs
        fi
    else
        generate_self_signed_certs
    fi
}

# Generate self-signed certificates
generate_self_signed_certs() {
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/privkey.pem \
        -out ssl/fullchain.pem \
        -subj "/CN=${DOMAIN:-localhost}/O=EQ12/C=US"
}

# Create monitoring configuration
create_monitoring_config() {
    log "Creating monitoring configuration..."

    # Prometheus configuration
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'eq12-license-server'
    static_configs:
      - targets: ['eq12-license-server:8000']

  - job_name: 'eq12-github-app'
    static_configs:
      - targets: ['eq12-github-app:3000']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
EOF

    # Grafana datasource
    mkdir -p monitoring/grafana/datasources
    cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true
EOF
}

# Create Kubernetes secrets
create_k8s_secrets() {
    log "Creating Kubernetes secrets..."

    source "$ENV_FILE"

    kubectl create secret generic eq12-secrets \
        --from-literal=database-url="postgresql://eq12:${POSTGRES_PASSWORD}@eq12-postgres:5432/eq12_license" \
        --from-literal=jwt-secret="$JWT_SECRET" \
        --from-literal=eq12-api-key="$EQ12_API_KEY" \
        --from-literal=github-app-id="$GITHUB_APP_ID" \
        --from-literal=github-webhook-secret="$GITHUB_WEBHOOK_SECRET" \
        --from-literal=postgres-password="$POSTGRES_PASSWORD" \
        --from-literal=redis-password="$REDIS_PASSWORD" \
        -n "$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
}

# Wait for Docker services
wait_for_services_docker() {
    log "Waiting for services to be ready..."

    local max_attempts=60
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if curl -s http://localhost:8000/ > /dev/null 2>&1; then
            success "EQ12 License Server is ready"
            break
        fi

        log "Attempt $attempt/$max_attempts - waiting for services..."
        sleep 5
        ((attempt++))
    done

    if [[ $attempt -gt $max_attempts ]]; then
        error "Services did not start within expected time"
    fi
}

# Wait for Kubernetes services
wait_for_services_k8s() {
    log "Waiting for Kubernetes services to be ready..."

    kubectl wait --for=condition=available --timeout=300s deployment/eq12-license-server -n "$NAMESPACE"
    kubectl wait --for=condition=available --timeout=300s deployment/eq12-github-app -n "$NAMESPACE"
    kubectl wait --for=condition=available --timeout=300s deployment/eq12-postgres -n "$NAMESPACE"

    success "All Kubernetes services are ready"
}

# Status check
check_status() {
    log "Checking EQ12 deployment status..."

    if docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep eq12 &> /dev/null; then
        log "Docker deployment status:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep eq12
    fi

    if kubectl get pods -n "$NAMESPACE" &> /dev/null; then
        log "Kubernetes deployment status:"
        kubectl get pods,svc,ingress -n "$NAMESPACE"
    fi
}

# View logs
view_logs() {
    if [[ -f "docker-compose.yml" ]]; then
        docker-compose logs -f --tail=100
    elif kubectl get namespace "$NAMESPACE" &> /dev/null; then
        kubectl logs -f -n "$NAMESPACE" -l app=eq12-license-server
    else
        error "No deployment found"
    fi
}

# Backup function
create_backup() {
    log "Creating EQ12 backup..."

    local backup_name="eq12-backup-$(date +%Y%m%d-%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"

    mkdir -p "$backup_path"

    # Database backup
    if docker ps | grep eq12-postgres > /dev/null; then
        docker exec eq12-postgres pg_dump -U eq12 eq12_license > "$backup_path/database.sql"
    fi

    # Configuration backup
    cp -r "$SCRIPT_DIR"/{*.yml,*.env,ssl,logs} "$backup_path/" 2>/dev/null || true

    # Create archive
    tar -czf "$backup_path.tar.gz" -C "$BACKUP_DIR" "$backup_name"
    rm -rf "$backup_path"

    success "Backup created: $backup_path.tar.gz"
}

# Health check
health_check() {
    log "Running EQ12 health checks..."

    local failed_checks=0

    # Check license server
    if curl -s http://localhost:8000/ | grep -q "EQ12 License Server"; then
        success "✅ License Server: OK"
    else
        error "❌ License Server: FAILED"
        ((failed_checks++))
    fi

    # Check database connectivity
    if docker exec eq12-postgres pg_isready -U eq12 &> /dev/null; then
        success "✅ Database: OK"
    else
        error "❌ Database: FAILED"
        ((failed_checks++))
    fi

    # Check Redis
    if docker exec eq12-redis redis-cli ping | grep -q "PONG"; then
        success "✅ Redis: OK"
    else
        error "❌ Redis: FAILED"
        ((failed_checks++))
    fi

    if [[ $failed_checks -eq 0 ]]; then
        success "All health checks passed!"
    else
        error "$failed_checks health check(s) failed"
    fi
}

# Main execution
main() {
    log "EQ12 Enterprise Deployment Starting..."
    log "Command: $DEPLOYMENT_TYPE"
    log "Log file: $LOG_FILE"

    case "$DEPLOYMENT_TYPE" in
        docker-deploy)
            preflight_checks
            docker_deploy
            ;;
        k8s-deploy)
            preflight_checks
            k8s_deploy
            ;;
        docker-stop)
            docker-compose down
            ;;
        k8s-stop)
            kubectl delete -f k8s-manifests.yml -n "$NAMESPACE"
            ;;
        status)
            check_status
            ;;
        logs)
            view_logs
            ;;
        backup)
            create_backup
            ;;
        health-check)
            health_check
            ;;
        *)
            error "Unknown command: $DEPLOYMENT_TYPE"
            ;;
    esac
}

# Run main function
main "$@"
