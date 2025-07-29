#!/bin/bash
# Container Health Diagnostic Script
# Quick diagnosis of enhanced deployment container issues

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

echo "🔍 ArrowTuner Container Health Diagnosis"
echo "========================================"
echo "Compose file: $COMPOSE_FILE"
echo ""

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    log_error "Compose file $COMPOSE_FILE not found"
    exit 1
fi

# Check if containers are running
log_info "Checking container status..."
if ! docker-compose -f "$COMPOSE_FILE" ps >/dev/null 2>&1; then
    log_error "No containers found for $COMPOSE_FILE"
    exit 1
fi

# Get container status
echo ""
log_info "Container Status:"
docker-compose -f "$COMPOSE_FILE" ps

# Check health status for each service
echo ""
log_info "Health Check Status:"
echo "===================="

services=$(docker-compose -f "$COMPOSE_FILE" ps --services)
for service in $services; do
    if [[ "$service" != "db-verifier" ]]; then
        container_id=$(docker-compose -f "$COMPOSE_FILE" ps -q "$service" 2>/dev/null)
        if [ -n "$container_id" ]; then
            health=$(docker inspect --format='{{.State.Health.Status}}' "$container_id" 2>/dev/null || echo "no-healthcheck")
            case $health in
                "healthy")
                    log_success "$service: $health"
                    ;;
                "unhealthy")
                    log_error "$service: $health"
                    ;;
                "starting")
                    log_warning "$service: $health"
                    ;;
                *)
                    log_info "$service: $health"
                    ;;
            esac
        else
            log_error "$service: not running"
        fi
    fi
done

# Show logs for unhealthy services
echo ""
log_info "Checking logs for unhealthy services..."
echo "======================================"

unhealthy_found=false
for service in $services; do
    if [[ "$service" != "db-verifier" ]]; then
        container_id=$(docker-compose -f "$COMPOSE_FILE" ps -q "$service" 2>/dev/null)
        if [ -n "$container_id" ]; then
            health=$(docker inspect --format='{{.State.Health.Status}}' "$container_id" 2>/dev/null || echo "unknown")
            if [ "$health" = "unhealthy" ] || [ "$health" = "starting" ]; then
                echo ""
                log_error "=== $service logs (last 20 lines) ==="
                docker-compose -f "$COMPOSE_FILE" logs --tail=20 "$service"
                unhealthy_found=true
            fi
        fi
    fi
done

if [ "$unhealthy_found" = false ]; then
    echo ""
    log_success "No unhealthy services found"
fi

# Test basic connectivity
echo ""
log_info "Testing Service Connectivity:"
echo "============================="

# Test API health
if curl -f -s http://localhost:5000/api/health >/dev/null 2>&1; then
    log_success "API health endpoint responding"
else
    log_error "API health endpoint not responding"
fi

# Test frontend
if curl -f -s http://localhost:3000/ >/dev/null 2>&1; then
    log_success "Frontend responding"
else
    log_error "Frontend not responding"
fi

# Test nginx
if curl -f -s http://localhost/ >/dev/null 2>&1; then
    log_success "Nginx responding"
else
    log_error "Nginx not responding"
fi

echo ""
log_info "Diagnosis complete"