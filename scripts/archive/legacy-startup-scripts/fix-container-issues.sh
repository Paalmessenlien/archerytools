#!/bin/bash
# Container Issue Fix Script
# Common fixes for enhanced deployment container problems

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Configuration
COMPOSE_FILE="${1:-docker-compose.enhanced-ssl.yml}"

echo "🔧 ArrowTuner Container Issue Fix"
echo "================================="
echo "Compose file: $COMPOSE_FILE"
echo ""

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    log_error "Compose file $COMPOSE_FILE not found"
    exit 1
fi

# Function to restart unhealthy services
restart_unhealthy_services() {
    log_info "Restarting unhealthy services..."
    
    services=$(docker-compose -f "$COMPOSE_FILE" ps --services)
    restarted=false
    
    for service in $services; do
        if [[ "$service" != "db-verifier" ]]; then
            container_id=$(docker-compose -f "$COMPOSE_FILE" ps -q "$service" 2>/dev/null)
            if [ -n "$container_id" ]; then
                health=$(docker inspect --format='{{.State.Health.Status}}' "$container_id" 2>/dev/null || echo "unknown")
                if [ "$health" = "unhealthy" ]; then
                    log_warning "Restarting unhealthy service: $service"
                    docker-compose -f "$COMPOSE_FILE" restart "$service"
                    restarted=true
                fi
            fi
        fi
    done
    
    if [ "$restarted" = false ]; then
        log_info "No unhealthy services found to restart"
    fi
}

# Function to check for common issues
check_common_issues() {
    log_info "Checking for common issues..."
    
    # Check disk space
    log_info "Checking disk space..."
    df_output=$(df -h . | tail -1)
    usage=$(echo "$df_output" | awk '{print $5}' | sed 's/%//')
    if [ "$usage" -gt 90 ]; then
        log_error "Disk space critical: $usage% used"
        log_error "Free up disk space before retrying deployment"
    else
        log_success "Disk space OK: $usage% used"
    fi
    
    # Check memory
    log_info "Checking memory usage..."
    memory_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$memory_usage" -gt 90 ]; then
        log_warning "Memory usage high: $memory_usage%"
    else
        log_success "Memory usage OK: $memory_usage%"
    fi
    
    # Check if ports are available
    log_info "Checking port availability..."
    if netstat -tuln | grep -q ":3000 "; then
        log_warning "Port 3000 already in use"
    else
        log_success "Port 3000 available"
    fi
    
    if netstat -tuln | grep -q ":5000 "; then
        log_warning "Port 5000 already in use"
    else
        log_success "Port 5000 available"
    fi
}

# Function to clean and rebuild
clean_and_rebuild() {
    log_info "Cleaning and rebuilding containers..."
    
    # Stop all services
    log_info "Stopping services..."
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    
    # Remove any orphaned containers
    log_info "Removing orphaned containers..."
    docker container prune -f >/dev/null 2>&1 || true
    
    # Remove unused images
    log_info "Removing unused images..."
    docker image prune -f >/dev/null 2>&1 || true
    
    # Rebuild and start
    log_info "Rebuilding and starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d --build
    
    log_success "Clean rebuild completed"
}

# Main menu
echo "Select fix option:"
echo "1) Restart unhealthy services"
echo "2) Check common issues"
echo "3) Clean and rebuild all containers"
echo "4) Show detailed diagnosis"
echo "5) Exit"
echo ""

read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        restart_unhealthy_services
        ;;
    2)
        check_common_issues
        ;;
    3)
        echo ""
        log_warning "This will stop all containers and rebuild. Continue? (y/N)"
        read -p "> " confirm
        if [[ $confirm == [yY] ]]; then
            clean_and_rebuild
        else
            log_info "Operation cancelled"
        fi
        ;;
    4)
        ./diagnose-containers.sh "$COMPOSE_FILE"
        ;;
    5)
        log_info "Exiting"
        exit 0
        ;;
    *)
        log_error "Invalid choice"
        exit 1
        ;;
esac

echo ""
log_info "Fix operation completed. Run ./diagnose-containers.sh to check status."