#!/bin/bash
#
# Unified Startup Script for ArrowTuner Platform
# Handles all deployment scenarios: development, production, SSL
#
# Usage:
#   ./start-unified.sh                    # Development mode
#   ./start-unified.sh production         # Production HTTP mode
#   ./start-unified.sh ssl yourdomain.com # Production SSL mode

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Default values
DEPLOYMENT_MODE="${1:-development}"
DOMAIN_NAME="${2:-localhost}"
SSL_ENABLED="false"
COMPOSE_PROFILES=""

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_message "$BLUE" "🔍 Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_message "$RED" "❌ Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_message "$RED" "❌ Docker Compose is not installed"
        exit 1
    fi
    
    # Check .env file
    if [[ ! -f ".env" ]]; then
        print_message "$YELLOW" "⚠️  No .env file found, creating from example..."
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            print_message "$GREEN" "✅ Created .env file from example"
        else
            print_message "$RED" "❌ No .env.example file found"
            exit 1
        fi
    fi
    
    print_message "$GREEN" "✅ Prerequisites check passed"
}

# Function to setup environment variables
setup_environment() {
    print_message "$BLUE" "🔧 Setting up environment for $DEPLOYMENT_MODE mode..."
    
    # Export deployment mode
    export DEPLOYMENT_MODE
    export DOMAIN_NAME
    
    case "$DEPLOYMENT_MODE" in
        "development")
            export FLASK_ENV="development"
            export NODE_ENV="development"
            export NUXT_PUBLIC_API_BASE="http://localhost/api"
            export API_DOCKERFILE="Dockerfile"
            export FRONTEND_DOCKERFILE="Dockerfile"
            COMPOSE_PROFILES="--profile with-nginx"
            print_message "$GREEN" "✅ Development environment configured"
            ;;
            
        "production")
            export FLASK_ENV="production"
            export NODE_ENV="production"
            export NUXT_PUBLIC_API_BASE="http://${DOMAIN_NAME}/api"
            export API_DOCKERFILE="Dockerfile.enhanced"
            export FRONTEND_DOCKERFILE="Dockerfile.enhanced"
            COMPOSE_PROFILES="--profile with-nginx"
            print_message "$GREEN" "✅ Production HTTP environment configured"
            ;;
            
        "ssl")
            export FLASK_ENV="production"
            export NODE_ENV="production"
            export SSL_ENABLED="true"
            export NUXT_PUBLIC_API_BASE="https://${DOMAIN_NAME}/api"
            export GOOGLE_REDIRECT_URI="https://${DOMAIN_NAME}"
            export API_DOCKERFILE="Dockerfile.enhanced"
            export FRONTEND_DOCKERFILE="Dockerfile.enhanced"
            COMPOSE_PROFILES="--profile with-nginx --profile with-backup"
            
            # Check SSL certificates
            check_ssl_certificates
            
            print_message "$GREEN" "✅ Production SSL environment configured"
            ;;
            
        *)
            print_message "$RED" "❌ Invalid deployment mode: $DEPLOYMENT_MODE"
            echo "Usage: $0 [development|production|ssl] [domain_name]"
            exit 1
            ;;
    esac
}

# Function to check SSL certificates
check_ssl_certificates() {
    print_message "$BLUE" "🔒 Checking SSL certificates..."
    
    SSL_DIR="$SCRIPT_DIR/deploy/ssl"
    mkdir -p "$SSL_DIR"
    
    if [[ ! -f "$SSL_DIR/cert.pem" ]] || [[ ! -f "$SSL_DIR/key.pem" ]]; then
        print_message "$YELLOW" "⚠️  SSL certificates not found"
        
        # Offer to create self-signed certificates for testing
        read -p "Would you like to create self-signed certificates for testing? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_self_signed_certificates
        else
            print_message "$RED" "❌ SSL certificates required for SSL mode"
            echo "Please place your SSL certificates at:"
            echo "  - $SSL_DIR/cert.pem"
            echo "  - $SSL_DIR/key.pem"
            exit 1
        fi
    else
        print_message "$GREEN" "✅ SSL certificates found"
    fi
}

# Function to create self-signed certificates
create_self_signed_certificates() {
    print_message "$BLUE" "🔧 Creating self-signed certificates..."
    
    SSL_DIR="$SCRIPT_DIR/deploy/ssl"
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/key.pem" \
        -out "$SSL_DIR/cert.pem" \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN_NAME"
    
    print_message "$GREEN" "✅ Self-signed certificates created"
    print_message "$YELLOW" "⚠️  These are for testing only. Use proper certificates in production!"
}

# Function to ensure unified nginx configuration exists
ensure_nginx_config() {
    print_message "$BLUE" "📋 Ensuring nginx configuration..."
    
    NGINX_TEMPLATE="$SCRIPT_DIR/deploy/nginx/unified.conf.template"
    
    if [[ ! -f "$NGINX_TEMPLATE" ]]; then
        print_message "$YELLOW" "⚠️  Creating unified nginx configuration template..."
        mkdir -p "$(dirname "$NGINX_TEMPLATE")"
        
        # Create the template (will be created in next step)
        create_nginx_template
    fi
}

# Function to clean up old containers and volumes
cleanup_old_setup() {
    print_message "$BLUE" "🧹 Cleaning up old Docker setup..."
    
    # Stop any running containers from old compose files
    local OLD_COMPOSE_FILES=(
        "docker-compose.yml"
        "docker-compose.enhanced-ssl.yml"
        "docker-compose.prod.yml"
        "docker-compose.ssl.yml"
        "docker-compose.dev.yml"
    )
    
    for compose_file in "${OLD_COMPOSE_FILES[@]}"; do
        if [[ -f "$compose_file" ]] && [[ "$compose_file" != "docker-compose.unified.yml" ]]; then
            print_message "$YELLOW" "  Stopping containers from $compose_file..."
            docker-compose -f "$compose_file" down --remove-orphans 2>/dev/null || true
        fi
    done
    
    print_message "$GREEN" "✅ Cleanup completed"
}

# Function to migrate databases to unified location
migrate_databases() {
    print_message "$BLUE" "🗄️  Migrating databases to unified location..."
    
    # This will be handled by the db-init service
    print_message "$GREEN" "✅ Database migration will be handled by db-init service"
}

# Function to start the services
start_services() {
    print_message "$BLUE" "🚀 Starting ArrowTuner services..."
    
    # Build and start services
    docker-compose -f docker-compose.unified.yml $COMPOSE_PROFILES build
    docker-compose -f docker-compose.unified.yml $COMPOSE_PROFILES up -d
    
    print_message "$GREEN" "✅ Services started successfully"
}

# Function to show status
show_status() {
    print_message "$BLUE" "\n📊 Service Status:"
    docker-compose -f docker-compose.unified.yml ps
    
    print_message "$BLUE" "\n🌐 Access URLs:"
    case "$DEPLOYMENT_MODE" in
        "development")
            echo "  Frontend: http://localhost:3000"
            echo "  API: http://localhost:5000/api"
            ;;
        "production")
            echo "  Frontend: http://$DOMAIN_NAME"
            echo "  API: http://$DOMAIN_NAME/api"
            ;;
        "ssl")
            echo "  Frontend: https://$DOMAIN_NAME"
            echo "  API: https://$DOMAIN_NAME/api"
            ;;
    esac
    
    print_message "$BLUE" "\n📝 Logs:"
    echo "  View logs: docker-compose -f docker-compose.unified.yml logs -f"
    echo "  API logs: docker-compose -f docker-compose.unified.yml logs -f api"
    echo "  Frontend logs: docker-compose -f docker-compose.unified.yml logs -f frontend"
}

# Function to create nginx template (placeholder for now)
create_nginx_template() {
    # This will be implemented in the next step
    touch "$NGINX_TEMPLATE"
}

# Main execution
main() {
    print_message "$GREEN" "🏹 ArrowTuner Unified Startup Script"
    print_message "$GREEN" "===================================="
    
    # Check prerequisites
    check_prerequisites
    
    # Setup environment
    setup_environment
    
    # Ensure nginx config exists
    ensure_nginx_config
    
    # Clean up old setup
    cleanup_old_setup
    
    # Migrate databases
    migrate_databases
    
    # Start services
    start_services
    
    # Show status
    show_status
    
    print_message "$GREEN" "\n✅ ArrowTuner platform is running!"
}

# Run main function
main "$@"