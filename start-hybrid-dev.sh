#!/bin/bash
# Hybrid Development Environment Startup Script
# Starts API in Docker + Frontend on Host (avoids oxc-parser native binding issues)

set -e

SCRIPT_NAME="Hybrid Development Environment"
API_COMPOSE_FILE="docker-compose.dev.yml"
FRONTEND_DIR="frontend"

echo "🚀 $SCRIPT_NAME Startup Script"
echo "=============================================="
echo "API: Docker Container (production schema)"
echo "Frontend: Host System (native bindings)"
echo ""

# Function to display help
show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start    - Start hybrid development environment"
    echo "  stop     - Stop all services"
    echo "  restart  - Restart all services"
    echo "  logs     - Show logs from all services"
    echo "  status   - Show service status"
    echo "  api-shell - Open shell in API container"
    echo "  help     - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start development environment"
    echo "  $0 logs     # Watch logs"
    echo "  $0 status   # Check service status"
}

# Function to check dependencies
check_dependencies() {
    echo "🔍 Checking dependencies..."
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        echo "❌ Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        echo "❌ Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node >/dev/null 2>&1; then
        echo "❌ Node.js is not installed or not in PATH"
        echo "Please install Node.js 18+ for frontend development"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm >/dev/null 2>&1; then
        echo "❌ npm is not installed or not in PATH"
        exit 1
    fi
    
    echo "✅ All dependencies are available"
    echo "   Docker: $(docker --version | head -1)"
    echo "   Node.js: $(node --version)"
    echo "   npm: $(npm --version)"
}

# Function to check environment
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
    
    echo "✅ Environment configuration checked"
}

# Function to setup frontend dependencies
setup_frontend() {
    echo "📦 Setting up frontend dependencies..."
    
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists and is valid
    if [ ! -d "node_modules" ] || [ ! -f ".nuxt/nuxt.d.ts" ]; then
        echo "🔧 Installing frontend dependencies..."
        echo "This may take a few minutes..."
        
        # Clean installation
        rm -rf node_modules package-lock.json .nuxt
        npm cache clean --force
        npm install --legacy-peer-deps
        
        if [ $? -eq 0 ]; then
            echo "✅ Frontend dependencies installed successfully"
        else
            echo "❌ Failed to install frontend dependencies"
            echo "💡 Try different Node.js version: nvm use 16 or nvm use 20"
            exit 1
        fi
    else
        echo "✅ Frontend dependencies already installed"
    fi
    
    cd ..
}

# Function to start services
start_services() {
    echo "🚀 Starting hybrid development services..."
    
    # Kill any existing frontend processes
    echo "🧹 Cleaning up existing processes..."
    pkill -f "nuxt dev" 2>/dev/null || true
    sleep 2
    
    # Stop any existing Docker containers
    docker-compose -f "$API_COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
    
    # Start API container
    echo "🐳 Starting API container..."
    docker-compose -f "$API_COMPOSE_FILE" up -d api
    
    # Wait for API to be ready
    echo "⏳ Waiting for API to start..."
    for i in {1..30}; do
        if curl -sf http://localhost:5000/api/simple-health >/dev/null 2>&1; then
            echo "✅ API is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "❌ API failed to start within 30 seconds"
            echo "📋 API logs:"
            docker-compose -f "$API_COMPOSE_FILE" logs api --tail=20
            exit 1
        fi
        sleep 1
    done
    
    # Start frontend in background
    echo "🌐 Starting frontend on host..."
    cd "$FRONTEND_DIR"
    
    # Start in background and capture PID
    npm run dev >/dev/null 2>&1 &
    FRONTEND_PID=$!
    echo "$FRONTEND_PID" > ../.frontend.pid
    
    # Wait for frontend to be ready
    echo "⏳ Waiting for frontend to start..."
    for i in {1..60}; do
        if curl -sf http://localhost:3000/ >/dev/null 2>&1; then
            echo "✅ Frontend is ready"
            break
        fi
        if [ $i -eq 60 ]; then
            echo "❌ Frontend failed to start within 60 seconds"
            echo "💡 Check frontend logs manually: cd frontend && npm run dev"
            exit 1
        fi
        sleep 1
    done
    
    cd ..
    
    echo ""
    echo "🎉 Hybrid development environment started successfully!"
    echo ""
    echo "📍 Access URLs:"
    echo "   Frontend:  http://localhost:3000"
    echo "   API:       http://localhost:5000/api/health"
    echo "   Admin:     http://localhost:3000/admin"
    echo ""
    echo "📋 Useful commands:"
    echo "   $0 logs      # Watch logs"
    echo "   $0 status    # Check service status"
    echo "   $0 stop      # Stop services"
    echo ""
    echo "💡 Both API and frontend support hot reload for development"
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping hybrid development services..."
    
    # Stop frontend
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            echo "🌐 Stopping frontend (PID: $FRONTEND_PID)..."
            kill "$FRONTEND_PID" 2>/dev/null || true
            # Also kill any child processes
            pkill -P "$FRONTEND_PID" 2>/dev/null || true
        fi
        rm -f .frontend.pid
    fi
    
    # Kill any remaining frontend processes
    pkill -f "nuxt dev" 2>/dev/null || true
    
    # Stop API container
    echo "🐳 Stopping API container..."
    docker-compose -f "$API_COMPOSE_FILE" down --remove-orphans
    
    echo "✅ All services stopped"
}

# Function to restart services
restart_services() {
    echo "🔄 Restarting hybrid development services..."
    stop_services
    sleep 2
    start_services
}

# Function to show logs
show_logs() {
    echo "📋 Showing service logs..."
    echo ""
    echo "🐳 API Container logs (last 20 lines):"
    docker-compose -f "$API_COMPOSE_FILE" logs api --tail=20
    echo ""
    echo "🌐 Frontend logs:"
    echo "Frontend runs in background. To see live logs:"
    echo "  cd frontend && npm run dev"
    echo ""
    echo "💡 To follow API logs: docker-compose -f $API_COMPOSE_FILE logs -f api"
}

# Function to show status
show_status() {
    echo "📊 Service Status:"
    echo "================="
    
    # Check API container
    if docker-compose -f "$API_COMPOSE_FILE" ps | grep -q "arrowtuner-api-dev.*Up"; then
        echo "✅ API Container: Running"
        if curl -sf http://localhost:5000/api/simple-health >/dev/null 2>&1; then
            echo "✅ API Health: OK"
        else
            echo "❌ API Health: Not responding"
        fi
    else
        echo "❌ API Container: Not running"
    fi
    
    # Check frontend
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            echo "✅ Frontend Process: Running (PID: $FRONTEND_PID)"
            if curl -sf http://localhost:3000/ >/dev/null 2>&1; then
                echo "✅ Frontend Health: OK"
            else
                echo "⏳ Frontend Health: Starting..."
            fi
        else
            echo "❌ Frontend Process: Not running"
            rm -f .frontend.pid
        fi
    else
        echo "❌ Frontend Process: Not running"
    fi
    
    echo ""
    echo "🌐 Access URLs (if services are running):"
    echo "   Frontend:  http://localhost:3000"
    echo "   API:       http://localhost:5000/api/health"
    echo "   Admin:     http://localhost:3000/admin"
}

# Function to open API shell
api_shell() {
    echo "🐚 Opening shell in API container..."
    if docker-compose -f "$API_COMPOSE_FILE" ps | grep -q "arrowtuner-api-dev.*Up"; then
        docker-compose -f "$API_COMPOSE_FILE" exec api /bin/bash
    else
        echo "❌ API container is not running. Start services first with: $0 start"
        exit 1
    fi
}

# Cleanup function for graceful shutdown
cleanup() {
    echo ""
    echo "🛑 Received interrupt signal, stopping services..."
    stop_services
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main command processing
case "${1:-start}" in
    start)
        check_dependencies
        check_environment
        setup_frontend
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
    status)
        show_status
        ;;
    api-shell)
        api_shell
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