#!/bin/bash
# Simple Docker Deployment Test
# Tests the simplified database-in-image approach

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    printf "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] %s${NC}\n" "$1"
}

success() {
    printf "${GREEN}✅ %s${NC}\n" "$1"
}

warning() {
    printf "${YELLOW}⚠️  %s${NC}\n" "$1"
}

error() {
    printf "${RED}❌ %s${NC}\n" "$1"
}

# Check if Docker is available
if ! command -v docker >/dev/null 2>&1; then
    error "Docker is not installed or not in PATH"
    exit 1
fi

# Check Docker Compose
COMPOSE_CMD=""
if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    error "Docker Compose is not available"
    exit 1
fi

log "Using Docker Compose command: $COMPOSE_CMD"

# Stop any existing containers
log "Stopping existing containers..."
$COMPOSE_CMD down || true

# Build and start the API service only (no volumes needed)
log "Building and starting API service..."
$COMPOSE_CMD up -d --build api

# Wait for service to start
log "Waiting for API to start..."
sleep 30

# Test the API
log "Testing API health endpoint..."
if curl -f -s "http://localhost:5000/api/health" >/dev/null; then
    success "API health check passed"
    
    # Get health details
    echo "Health Details:"
    curl -s "http://localhost:5000/api/health" | python3 -m json.tool 2>/dev/null || curl -s "http://localhost:5000/api/health"
    echo
    
    # Test database endpoint
    log "Testing database statistics..."
    if curl -f -s "http://localhost:5000/api/database/stats" >/dev/null; then
        success "Database statistics endpoint working"
        
        echo "Database Statistics:"
        curl -s "http://localhost:5000/api/database/stats" | python3 -m json.tool 2>/dev/null || curl -s "http://localhost:5000/api/database/stats"
        echo
    else
        error "Database statistics endpoint failed"
    fi
    
    # Test arrows endpoint
    log "Testing arrows endpoint..."
    if curl -f -s "http://localhost:5000/api/arrows?per_page=5" >/dev/null; then
        success "Arrows endpoint working"
        
        echo "Sample Arrows (first 5):"
        curl -s "http://localhost:5000/api/arrows?per_page=5" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"Total arrows: {data.get('total', 0)}\")
    for arrow in data.get('arrows', [])[:3]:
        print(f\"- {arrow.get('manufacturer', 'Unknown')} {arrow.get('model_name', 'Unknown')}\")
except:
    print('Could not parse arrows data')
"
        echo
    else
        error "Arrows endpoint failed"
    fi
    
else
    error "API health check failed"
    
    # Show container logs for debugging
    log "Container logs:"
    $COMPOSE_CMD logs api
    exit 1
fi

# Show container status
log "Container status:"
$COMPOSE_CMD ps

success "Simple deployment test passed!"
echo
log "API is running at: http://localhost:5000"
log "To stop: $COMPOSE_CMD down"