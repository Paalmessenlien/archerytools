#!/bin/bash
# Enhanced deployment script for ArrowTuner with comprehensive verification
# This script provides a robust deployment process with verification at each step

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="${1:-docker-compose.enhanced-ssl.yml}"
DEPLOYMENT_TIMEOUT=300  # 5 minutes
VERIFICATION_TIMEOUT=120  # 2 minutes

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

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking deployment prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose not found. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    # Check compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Compose file $COMPOSE_FILE not found."
        exit 1
    fi
    
    # Check .env file exists
    if [ ! -f ".env" ]; then
        log_warning ".env file not found. Some services may not work correctly."
    fi
    
    log_success "Prerequisites check passed"
}

# Function to verify environment variables
verify_environment() {
    log_info "Verifying environment variables..."
    
    # Source .env file if it exists
    if [ -f ".env" ]; then
        set -a  # Automatically export all variables
        source .env
        set +a
    fi
    
    # Check critical variables
    local missing_vars=()
    
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "change-this-secret-key-in-production" ]; then
        missing_vars+=("SECRET_KEY")
    fi
    
    if [ -z "$GOOGLE_CLIENT_SECRET" ] || [ "$GOOGLE_CLIENT_SECRET" = "not-set" ]; then
        missing_vars+=("GOOGLE_CLIENT_SECRET")
    fi
    
    if [ -z "$NUXT_PUBLIC_GOOGLE_CLIENT_ID" ] || [ "$NUXT_PUBLIC_GOOGLE_CLIENT_ID" = "not-set" ]; then
        missing_vars+=("NUXT_PUBLIC_GOOGLE_CLIENT_ID")
    fi
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_warning "Missing or default environment variables:"
        for var in "${missing_vars[@]}"; do
            log_warning "  - $var"
        done
        log_warning "Application may not function correctly"
    else
        log_success "Environment variables verified"
    fi
}

# Function to clean up old containers and volumes
cleanup_old_deployment() {
    log_info "Cleaning up old deployment..."
    
    # Stop and remove containers
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
    
    # Remove dangling images
    docker image prune -f &> /dev/null || true
    
    log_success "Cleanup completed"
}

# Function to build and start services
deploy_services() {
    log_info "Building and starting services..."
    
    # Build with no cache to ensure fresh build
    log_info "Building images (this may take several minutes)..."
    if ! timeout $DEPLOYMENT_TIMEOUT docker-compose -f "$COMPOSE_FILE" build --no-cache; then
        log_error "Build failed or timed out"
        exit 1
    fi
    
    # Start services
    log_info "Starting services..."
    if ! timeout $DEPLOYMENT_TIMEOUT docker-compose -f "$COMPOSE_FILE" up -d; then
        log_error "Service startup failed or timed out"
        exit 1
    fi
    
    log_success "Services started"
}

# Function to wait for services to be healthy
wait_for_health() {
    log_info "Waiting for services to become healthy..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts"
        
        # Check service health
        local healthy_services=0
        local total_services=0
        
        # Get service status
        local services=$(docker-compose -f "$COMPOSE_FILE" ps --services)
        
        for service in $services; do
            if [[ "$service" != "db-verifier" ]]; then  # Skip one-time verifier
                total_services=$((total_services + 1))
                local health=$(docker-compose -f "$COMPOSE_FILE" ps -q "$service" | xargs -r docker inspect --format='{{.State.Health.Status}}' 2>/dev/null || echo "unhealthy")
                
                if [ "$health" = "healthy" ]; then
                    healthy_services=$((healthy_services + 1))
                    log_info "  ✅ $service: healthy"
                else
                    log_info "  ⏳ $service: $health"
                fi
            fi
        done
        
        if [ $healthy_services -eq $total_services ]; then
            log_success "All services are healthy!"
            return 0
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Services failed to become healthy within timeout"
            return 1
        fi
        
        sleep 10
        attempt=$((attempt + 1))
    done
}

# Function to run database verification
verify_databases() {
    log_info "Running database verification..."
    
    # Run the database verifier
    if docker-compose -f "$COMPOSE_FILE" run --rm db-verifier; then
        log_success "Database verification passed"
    else
        log_error "Database verification failed"
        return 1
    fi
}

# Function to test API endpoints
test_api_endpoints() {
    log_info "Testing API endpoints..."
    
    local api_base="https://localhost/api"
    local max_attempts=10
    local attempt=1
    
    # Test basic health endpoint
    while [ $attempt -le $max_attempts ]; do
        log_info "Testing API health (attempt $attempt/$max_attempts)..."
        
        if curl -f -k -s "$api_base/health" > /dev/null 2>&1; then
            log_success "API health endpoint responding"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "API health endpoint not responding"
            return 1
        fi
        
        sleep 5
        attempt=$((attempt + 1))
    done
    
    # Test additional endpoints
    local endpoints=("simple-health" "guides" "bow-setups")
    
    for endpoint in "${endpoints[@]}"; do
        log_info "Testing /$endpoint endpoint..."
        if curl -f -k -s "$api_base/$endpoint" > /dev/null 2>&1; then
            log_success "  ✅ /$endpoint responding"
        else
            log_warning "  ⚠️  /$endpoint not responding (may require authentication)"
        fi
    done
}

# Function to test frontend
test_frontend() {
    log_info "Testing frontend..."
    
    local frontend_base="https://localhost"
    local pages=("/" "/database" "/tuning" "/guides")
    
    for page in "${pages[@]}"; do
        log_info "Testing page $page..."
        if curl -f -k -s "$frontend_base$page" > /dev/null 2>&1; then
            log_success "  ✅ $page responding"
        else
            log_warning "  ⚠️  $page not responding"
        fi
    done
}

# Function to show deployment status
show_status() {
    log_info "Deployment Status:"
    echo "=================="
    
    # Show container status
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    log_info "Service URLs:"
    echo "  Frontend: https://localhost/"
    echo "  API: https://localhost/api/"
    echo "  Health: https://localhost/api/health"
    
    echo ""
    log_info "To view logs:"
    echo "  docker-compose -f $COMPOSE_FILE logs -f"
    
    echo ""
    log_info "To stop services:"
    echo "  docker-compose -f $COMPOSE_FILE down"
}

# Function to save deployment info
save_deployment_info() {
    local deployment_info=$(cat <<EOF
{
  "deployment_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "compose_file": "$COMPOSE_FILE",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "git_branch": "$(git branch --show-current 2>/dev/null || echo 'unknown')",
  "services": $(docker-compose -f "$COMPOSE_FILE" ps --services | jq -R . | jq -s .),
  "environment": {
    "NODE_ENV": "${NODE_ENV:-not-set}",
    "FLASK_ENV": "${FLASK_ENV:-not-set}"
  }
}
EOF
)
    
    echo "$deployment_info" > deployment-info.json
    log_info "Deployment info saved to deployment-info.json"
}

# Main deployment process
main() {
    log_info "🚀 Starting Enhanced ArrowTuner Deployment"
    log_info "Compose file: $COMPOSE_FILE"
    log_info "Timeout: $DEPLOYMENT_TIMEOUT seconds"
    echo "============================================="
    
    # Step 1: Prerequisites
    check_prerequisites
    
    # Step 2: Environment verification
    verify_environment
    
    # Step 3: Cleanup
    cleanup_old_deployment
    
    # Step 4: Deploy services
    deploy_services
    
    # Step 5: Wait for health
    if ! wait_for_health; then
        log_error "Health check failed, showing logs..."
        docker-compose -f "$COMPOSE_FILE" logs --tail=50
        exit 1
    fi
    
    # Step 6: Verify databases
    if ! verify_databases; then
        log_error "Database verification failed"
        exit 1
    fi
    
    # Step 7: Test endpoints
    test_api_endpoints
    test_frontend
    
    # Step 8: Save deployment info
    save_deployment_info
    
    # Step 9: Show status
    show_status
    
    log_success "🎉 Enhanced deployment completed successfully!"
    log_info "Your ArrowTuner application is now running with comprehensive verification."
}

# Handle script interruption
trap 'log_error "Deployment interrupted"; exit 1' INT TERM

# Run main function
main "$@"