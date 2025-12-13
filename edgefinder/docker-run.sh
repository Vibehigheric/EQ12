#!/bin/bash
# EdgeFinder Docker Management Script
# Provides convenient commands for managing EdgeFinder Docker environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
IMAGE_NAME="edgefinder"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prereqs() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "docker-compose.yml not found"
        exit 1
    fi
    
    if [ ! -f "$ENV_FILE" ] && [ ! -f ".env.example" ]; then
        log_warning "No .env file found. Please copy .env.example to .env and configure"
    fi
    
    log_success "Prerequisites check passed"
}

# Setup environment
setup() {
    log_info "Setting up EdgeFinder Docker environment..."
    
    # Copy example env file if needed
    if [ ! -f "$ENV_FILE" ] && [ -f ".env.example" ]; then
        log_info "Creating .env from example..."
        cp .env.example .env
        log_warning "Please edit .env file with your API tokens before running EdgeFinder"
    fi
    
    # Create required directories
    log_info "Creating required directories..."
    mkdir -p data/{output,downloads,reports}
    mkdir -p configs
    mkdir -p logs
    
    # Set permissions
    chmod 755 data configs logs
    
    log_success "Setup completed"
}

# Build images
build() {
    log_info "Building EdgeFinder Docker images..."
    
    docker-compose build --no-cache edgefinder
    
    if [ "$1" = "--with-dev" ]; then
        docker-compose build --no-cache edgefinder-dev
    fi
    
    log_success "Build completed"
}

# Start services
start() {
    local profile="$1"
    
    case "$profile" in
        "dev"|"development")
            log_info "Starting EdgeFinder in development mode..."
            docker-compose --profile dev up -d edgefinder-dev
            ;;
        "dashboard")
            log_info "Starting EdgeFinder with dashboard..."
            docker-compose --profile dashboard up -d edgefinder eq12-dashboard
            ;;
        "security")
            log_info "Starting EdgeFinder security scanner..."
            docker-compose --profile security up security-scanner
            ;;
        "all")
            log_info "Starting all EdgeFinder services..."
            docker-compose --profile dev --profile dashboard --profile security up -d
            ;;
        *)
            log_info "Starting EdgeFinder production service..."
            docker-compose up -d edgefinder
            ;;
    esac
    
    log_success "EdgeFinder started"
}

# Stop services
stop() {
    log_info "Stopping EdgeFinder services..."
    docker-compose down --remove-orphans
    log_success "EdgeFinder stopped"
}

# Run EdgeFinder command
run_command() {
    local command="$*"
    
    log_info "Running EdgeFinder command: $command"
    docker-compose run --rm edgefinder $command
}

# Run security scan
security_scan() {
    log_info "Running EdgeFinder security scan..."
    docker-compose --profile security run --rm security-scanner analyze --security-scan
    log_success "Security scan completed"
}

# Show logs
logs() {
    local service="${1:-edgefinder}"
    local follow="${2:-}"
    
    if [ "$follow" = "-f" ] || [ "$follow" = "--follow" ]; then
        docker-compose logs -f "$service"
    else
        docker-compose logs "$service"
    fi
}

# Clean up
cleanup() {
    log_info "Cleaning up EdgeFinder Docker environment..."
    
    # Stop and remove containers
    docker-compose down --remove-orphans --volumes
    
    # Remove images
    if docker images | grep -q "$IMAGE_NAME"; then
        docker rmi $(docker images "$IMAGE_NAME" -q) 2>/dev/null || true
    fi
    
    # Remove dangling images
    docker image prune -f
    
    log_success "Cleanup completed"
}

# Show status
status() {
    log_info "EdgeFinder Docker Status:"
    echo
    
    # Show running containers
    echo "Running containers:"
    docker-compose ps
    echo
    
    # Show images
    echo "Images:"
    docker images | grep -E "(REPOSITORY|$IMAGE_NAME)"
    echo
    
    # Show volumes
    echo "Volumes:"
    docker-compose config --volumes 2>/dev/null || echo "No volumes configured"
}

# Interactive shell
shell() {
    local service="${1:-edgefinder-dev}"
    
    log_info "Opening shell in $service..."
    docker-compose exec "$service" /bin/bash || \
    docker-compose run --rm "$service" /bin/bash
}

# Update images
update() {
    log_info "Updating EdgeFinder Docker images..."
    
    # Pull base images
    docker-compose pull
    
    # Rebuild with latest changes
    build
    
    log_success "Update completed"
}

# Show help
show_help() {
    cat << EOF
EdgeFinder Docker Management Script

Usage: $0 COMMAND [OPTIONS]

Commands:
    setup           Set up initial environment and directories
    build           Build EdgeFinder Docker images
                    --with-dev    Also build development image
    
    start [PROFILE] Start EdgeFinder services
                    dev       Development mode with mounted source
                    dashboard Dashboard with web interface
                    security  Security scanning mode
                    all       Start all services
                    (default) Production mode
    
    stop            Stop all EdgeFinder services
    
    run COMMAND     Run EdgeFinder command in container
                    Example: $0 run search --keywords "betting api"
    
    security        Run security scan
    
    logs [SERVICE]  Show logs for service (default: edgefinder)
                    -f, --follow    Follow log output
    
    shell [SERVICE] Open interactive shell (default: edgefinder-dev)
    
    status          Show status of containers, images, and volumes
    
    update          Update base images and rebuild
    
    cleanup         Stop services and remove containers/images
    
    help            Show this help message

Examples:
    $0 setup
    $0 build --with-dev
    $0 start dashboard
    $0 run search --keywords "machine learning" --max 20
    $0 logs edgefinder -f
    $0 shell
    $0 cleanup

EOF
}

# Main script logic
main() {
    case "${1:-help}" in
        "setup")
            check_prereqs
            setup
            ;;
        "build")
            check_prereqs
            build "$2"
            ;;
        "start")
            check_prereqs
            start "$2"
            ;;
        "stop")
            stop
            ;;
        "run")
            shift
            run_command "$@"
            ;;
        "security")
            security_scan
            ;;
        "logs")
            logs "$2" "$3"
            ;;
        "shell")
            shell "$2"
            ;;
        "status")
            status
            ;;
        "update")
            check_prereqs
            update
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"