#!/bin/bash
# ArrowTuner Deployment Test Script
# Tests Docker deployment with database initialization

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

header() {
    echo -e "${PURPLE}$1${NC}"
}

# Check prerequisites
check_prerequisites() {
    header "🔍 Checking Prerequisites"
    
    local missing_tools=()
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    else
        success "Docker is installed"
        docker --version
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
        missing_tools+=("docker-compose")
    else
        success "Docker Compose is available"
        if command -v docker-compose &> /dev/null; then
            docker-compose --version
        else
            docker compose version
        fi
    fi
    
    # Check curl for testing
    if ! command -v curl &> /dev/null; then
        missing_tools+=("curl")
    else
        success "curl is available for testing"
    fi
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        error "Missing required tools: ${missing_tools[*]}"
        echo
        echo "Install missing tools:"
        echo "  Ubuntu/Debian: sudo apt-get update && sudo apt-get install -y docker.io docker-compose curl"
        echo "  CentOS/RHEL: sudo yum install -y docker docker-compose curl"
        echo
        echo "Don't forget to:"
        echo "  sudo systemctl start docker"
        echo "  sudo systemctl enable docker"
        echo "  sudo usermod -aG docker \$USER"
        echo "  # Then log out and back in"
        exit 1
    fi
    
    success "All prerequisites met"
}

# Test source data for building database in image
test_data_preparation() {
    header "📦 Testing Source Data for Database Build"
    
    # Check if processed data exists for building database
    if [ -d "arrow_scraper/data/processed" ]; then
        success "Source processed data directory exists"
        
        JSON_COUNT=$(find arrow_scraper/data/processed -name "*.json" 2>/dev/null | wc -l || echo "0")
        if [ "$JSON_COUNT" -gt 0 ]; then
            success "Found $JSON_COUNT processed JSON files for database build"
        else
            error "No JSON files found in processed data directory"
            return 1
        fi
        
        # Check if build script exists
        if [ -f "arrow_scraper/build-database.py" ]; then
            success "Database build script exists"
        else
            error "Database build script missing"
            return 1
        fi
        
    else
        error "Source processed data directory not found: arrow_scraper/data/processed"
        log "Database will be built from processed JSON files during Docker image creation"
        return 1
    fi
}

# Build and start services
deploy_services() {
    header "🚀 Deploying Services"
    
    log "Stopping any existing containers..."
    if command -v docker-compose &> /dev/null; then
        docker-compose down || true
    else
        docker compose down || true
    fi
    
    log "Building and starting services..."
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d --build
    else
        docker compose up -d --build
    fi
    
    success "Services started"
}

# Test service health
test_services() {
    header "🩺 Testing Service Health"
    
    log "Waiting for services to start..."
    sleep 30
    
    # Test API health
    log "Testing API health endpoint..."
    local api_attempts=0
    local api_max_attempts=6
    
    while [ $api_attempts -lt $api_max_attempts ]; do
        if curl -f -s "http://localhost:5000/api/health" > /dev/null; then
            success "API health check passed"
            
            # Get detailed health info
            echo "API Health Details:"
            curl -s "http://localhost:5000/api/health" | python3 -m json.tool 2>/dev/null || curl -s "http://localhost:5000/api/health"
            break
        else
            api_attempts=$((api_attempts + 1))
            warning "API health check failed (attempt $api_attempts/$api_max_attempts)"
            if [ $api_attempts -lt $api_max_attempts ]; then
                log "Waiting 10 seconds before retry..."
                sleep 10
            fi
        fi
    done
    
    if [ $api_attempts -eq $api_max_attempts ]; then
        error "API health checks failed after $api_max_attempts attempts"
        return 1
    fi
    
    # Test database endpoint
    log "Testing database statistics endpoint..."
    if curl -f -s "http://localhost:5000/api/database/stats" > /dev/null; then
        success "Database statistics endpoint working"
        
        echo "Database Statistics:"
        curl -s "http://localhost:5000/api/database/stats" | python3 -m json.tool 2>/dev/null || curl -s "http://localhost:5000/api/database/stats"
    else
        error "Database statistics endpoint failed"
        return 1
    fi
    
    # Test frontend
    log "Testing frontend..."
    local frontend_attempts=0
    local frontend_max_attempts=3
    
    while [ $frontend_attempts -lt $frontend_max_attempts ]; do
        if curl -f -s "http://localhost:3000" > /dev/null; then
            success "Frontend health check passed"
            break
        else
            frontend_attempts=$((frontend_attempts + 1))
            warning "Frontend health check failed (attempt $frontend_attempts/$frontend_max_attempts)"
            if [ $frontend_attempts -lt $frontend_max_attempts ]; then
                sleep 10
            fi
        fi
    done
    
    if [ $frontend_attempts -eq $frontend_max_attempts ]; then
        warning "Frontend health checks failed - this may be normal if Nuxt is still building"
    fi
    
    # Test nginx (if running)
    log "Testing nginx proxy..."
    if curl -f -s "http://localhost:80" > /dev/null 2>&1; then
        success "Nginx proxy working"
    else
        warning "Nginx proxy not responding (may be normal for development)"
    fi
}

# Show container status
show_status() {
    header "📊 Container Status"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
    
    echo
    header "📋 Container Logs (last 20 lines)"
    
    if command -v docker-compose &> /dev/null; then
        echo "API Logs:"
        docker-compose logs --tail=20 api
        echo
        echo "Frontend Logs:"
        docker-compose logs --tail=20 frontend
    else
        echo "API Logs:"
        docker compose logs --tail=20 api
        echo
        echo "Frontend Logs:"
        docker compose logs --tail=20 frontend
    fi
}

# Main test function
main() {
    header "🧪 ArrowTuner Deployment Test"
    echo "=" * 50
    
    # Step 1: Check prerequisites
    check_prerequisites
    echo
    
    # Step 2: Test data preparation
    if ! test_data_preparation; then
        error "Data preparation failed"
        exit 1
    fi
    echo
    
    # Step 3: Deploy services
    deploy_services
    echo
    
    # Step 4: Test services
    if ! test_services; then
        error "Service tests failed"
        show_status
        exit 1
    fi
    echo
    
    # Step 5: Show status
    show_status
    
    echo
    header "🎉 Deployment Test Results"
    echo "=========================="
    success "API: http://localhost:5000"
    success "Frontend: http://localhost:3000"
    success "Nginx: http://localhost:80"
    echo
    log "To stop services: docker-compose down"
    log "To view logs: docker-compose logs -f [service_name]"
    
    success "Deployment test completed successfully!"
}

# Handle command line arguments
case "${1:-}" in
    "clean")
        log "Cleaning up containers and volumes..."
        if command -v docker-compose &> /dev/null; then
            docker-compose down -v
        else
            docker compose down -v
        fi
        docker system prune -f
        success "Cleanup completed"
        ;;
    "logs")
        if command -v docker-compose &> /dev/null; then
            docker-compose logs -f "${2:-}"
        else
            docker compose logs -f "${2:-}"
        fi
        ;;
    "status")
        show_status
        ;;
    *)
        main
        ;;
esac