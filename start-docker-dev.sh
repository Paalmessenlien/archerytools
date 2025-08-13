#!/bin/bash
# Unified Docker Development Environment Startup Script
# Uses production database schema but with development features

set -e

SCRIPT_NAME="Docker Development Environment"
COMPOSE_FILE="docker-compose.dev.yml"

echo "🚀 $SCRIPT_NAME Startup Script"
echo "================================================"

# Function to display help
show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start    - Start all services in development mode"
    echo "  stop     - Stop all services"
    echo "  restart  - Restart all services"
    echo "  logs     - Follow logs from all services"
    echo "  build    - Rebuild all containers"
    echo "  clean    - Stop and remove all containers, networks, and volumes"
    echo "  status   - Show service status"
    echo "  shell    - Open shell in API container"
    echo "  debug    - Debug frontend container for native binding issues"
    echo "  help     - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start          # Start development environment"
    echo "  $0 logs           # Watch logs"
    echo "  $0 shell          # Debug API container"
    echo "  $0 debug          # Debug frontend native binding issues"
}

# Function to check Docker and Docker Compose
check_dependencies() {
    echo "🔍 Checking dependencies..."
    
    if ! command -v docker >/dev/null 2>&1; then
        echo "❌ Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose >/dev/null 2>&1; then
        echo "❌ Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    echo "✅ Docker and Docker Compose are available"
}

# Function to check environment variables
check_environment() {
    echo "🔍 Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        echo "⚠️  .env file not found, creating from example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo "✅ Created .env from .env.example"
            echo "📝 Please edit .env with your actual credentials"
        else
            echo "❌ No .env.example found, please create .env manually"
            exit 1
        fi
    fi
    
    # Check critical variables
    if ! grep -q "GOOGLE_CLIENT_SECRET=" .env || grep -q "GOOGLE_CLIENT_SECRET=not-set" .env; then
        echo "⚠️  GOOGLE_CLIENT_SECRET not configured in .env"
    fi
    
    if ! grep -q "NUXT_PUBLIC_GOOGLE_CLIENT_ID=" .env || grep -q "NUXT_PUBLIC_GOOGLE_CLIENT_ID=not-set" .env; then
        echo "⚠️  NUXT_PUBLIC_GOOGLE_CLIENT_ID not configured in .env"
    fi
    
    echo "✅ Environment configuration checked"
}

# Function to start services
start_services() {
    echo "🚀 Starting development services..."
    echo "Using compose file: $COMPOSE_FILE"
    
    # Stop any existing services first
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
    
    # Build and start services
    docker-compose -f "$COMPOSE_FILE" up --build -d
    
    # Wait a moment for services to start
    echo "⏳ Waiting for services to initialize..."
    sleep 10
    
    # Check service status
    check_service_health
    
    echo ""
    echo "🎉 Development environment started successfully!"
    echo ""
    echo "📍 Access URLs:"
    echo "   Frontend:  http://localhost:3000"
    echo "   API:       http://localhost:5000/api/health"
    echo "   Nginx:     http://localhost:8080"
    echo "   Admin:     http://localhost:3000/admin"
    echo ""
    echo "📋 Useful commands:"
    echo "   $0 logs      # Watch logs"
    echo "   $0 shell     # Debug API container"
    echo "   $0 status    # Check service health"
    echo "   $0 stop      # Stop services"
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping development services..."
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    echo "✅ Services stopped"
}

# Function to restart services
restart_services() {
    echo "🔄 Restarting development services..."
    stop_services
    start_services
}

# Function to check service health
check_service_health() {
    echo "🔍 Checking service health..."
    
    # Check API health
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "arrowtuner-api-dev.*Up"; then
        echo "✅ API container is running"
        if curl -f http://localhost:5000/api/simple-health >/dev/null 2>&1; then
            echo "✅ API is responding to health checks"
        else
            echo "⚠️  API container running but not responding to health checks"
        fi
    else
        echo "❌ API container is not running"
    fi
    
    # Check Frontend health
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "arrowtuner-frontend-dev.*Up"; then
        echo "✅ Frontend container is running"
        if curl -f http://localhost:3000/ >/dev/null 2>&1; then
            echo "✅ Frontend is responding"
        else
            echo "⚠️  Frontend container running but not responding"
        fi
    else
        echo "❌ Frontend container is not running"
    fi
}

# Function to show logs
show_logs() {
    echo "📋 Following service logs (Ctrl+C to exit)..."
    docker-compose -f "$COMPOSE_FILE" logs -f
}

# Function to build containers
build_containers() {
    echo "🔨 Building containers..."
    echo "ℹ️  Note: Frontend build may take several minutes due to native binding compilation"
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    echo "✅ Containers built successfully"
}

# Function to clean everything
clean_environment() {
    echo "🧹 Cleaning development environment..."
    read -p "This will remove all containers, networks, and volumes. Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans --rmi local
        docker system prune -f
        echo "✅ Development environment cleaned"
    else
        echo "❌ Cleanup cancelled"
    fi
}

# Function to show service status
show_status() {
    echo "📊 Service Status:"
    echo "=================="
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    echo "💾 Volume Usage:"
    echo "==============="
    docker volume ls | grep arrowtuner-dev || echo "No development volumes found"
    
    echo ""
    echo "🌐 Network Status:"
    echo "=================="
    docker network ls | grep arrowtuner-dev || echo "No development networks found"
}

# Function to open shell in API container
open_shell() {
    echo "🐚 Opening shell in API container..."
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "arrowtuner-api-dev.*Up"; then
        docker-compose -f "$COMPOSE_FILE" exec api /bin/bash
    else
        echo "❌ API container is not running. Start services first with: $0 start"
        exit 1
    fi
}

# Function to debug frontend container
debug_frontend() {
    echo "🔍 Debugging frontend container for native binding issues..."
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "arrowtuner-frontend-dev.*Up"; then
        echo "Frontend container is running, opening shell..."
        docker-compose -f "$COMPOSE_FILE" exec frontend /bin/bash
    else
        echo "Frontend container is not running. Checking build logs..."
        echo ""
        echo "💡 Common solutions for native binding issues:"
        echo "1. Rebuild containers: $0 build"
        echo "2. Clean environment: $0 clean && $0 start"
        echo "3. Try manual fix inside container:"
        echo "   docker-compose -f $COMPOSE_FILE run --rm frontend /bin/bash"
        echo "   rm -rf node_modules package-lock.json"
        echo "   npm install"
        echo "   npm rebuild"
        echo ""
        echo "🏗️  Recent build logs:"
        docker-compose -f "$COMPOSE_FILE" logs frontend | tail -20
    fi
}

# Main command processing
case "${1:-start}" in
    start)
        check_dependencies
        check_environment
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs
        ;;
    build)
        check_dependencies
        build_containers
        ;;
    clean)
        clean_environment
        ;;
    status)
        show_status
        ;;
    shell)
        open_shell
        ;;
    debug)
        debug_frontend
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac