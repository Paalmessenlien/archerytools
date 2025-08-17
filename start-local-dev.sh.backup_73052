#!/bin/bash

# Arrow Tuner Local Development Startup Script
# Fixes CORS issues by running frontend and API on direct ports without nginx

set -e

# Configuration
API_PORT=${API_PORT:-5000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}
NODE_ENV="development"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Check if we're in the correct directory
if [ ! -f "CLAUDE.md" ]; then
    error "Please run this script from the archerytools root directory"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to check if port is available
check_port() {
    local port=$1
    local service_name=$2
    
    # Wait up to 10 seconds for port to become free
    for i in {1..10}; do
        if command -v lsof >/dev/null 2>&1; then
            if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                # Port is free
                return 0
            fi
            
            if [ $i -eq 1 ]; then
                warning "$service_name port $port is already in use, attempting cleanup..."
                ps aux | grep "python api.py" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
                ps aux | grep "npm run dev" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
                lsof -ti:$port | xargs kill -9 2>/dev/null || true
            fi
            
            log "Waiting for port $port to become free... ($i/10)"
            sleep 1
        else
            # No lsof available, assume port is free
            return 0
        fi
    done
    
    error "Failed to free port $port after 10 seconds. Please check for running services."
    exit 1
}

# Function to ensure spine calculation data migration
ensure_spine_data_migration() {
    log "🧮 Checking spine calculation data migration..."
    
    # Check if spine calculation tables exist
    if command -v sqlite3 &> /dev/null; then
        # Check if spine tables exist in the arrow database
        SPINE_TABLES_COUNT=$(sqlite3 "${ARROW_DATABASE_PATH}" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name IN ('calculation_parameters', 'arrow_material_properties', 'manufacturer_spine_charts');" 2>/dev/null || echo "0")
        
        if [[ "$SPINE_TABLES_COUNT" == "3" ]]; then
            success "✅ Spine calculation tables already exist"
        else
            warning "⚠️  Spine calculation tables missing, running migration..."
            
            # Run spine data migration
            if [[ -f "migrate_spine_calculation_data.py" ]]; then
                if python migrate_spine_calculation_data.py; then
                    success "✅ Spine calculation migration completed"
                    
                    # Import sample data if available
                    if [[ -f "import_spine_calculator_data.py" ]]; then
                        log "📊 Importing spine calculation sample data..."
                        if python import_spine_calculator_data.py; then
                            success "✅ Spine calculation data imported successfully"
                        else
                            warning "⚠️  Warning: Spine data import failed, but migration completed"
                        fi
                    fi
                else
                    warning "⚠️  Warning: Spine calculation migration failed, continuing anyway"
                fi
            else
                warning "⚠️  Warning: Spine migration script not found"
            fi
        fi
    else
        warning "⚠️  sqlite3 not available, skipping spine data check"
    fi
}

# Function to start API backend
start_api() {
    log "Starting Flask API backend on port $API_PORT..."
    
    # Check if port is available
    check_port $API_PORT "API backend"
    
    cd arrow_scraper
    
    # Activate virtual environment if it exists
    if [ -f "../venv/bin/activate" ]; then
        source ../venv/bin/activate
        log "Activated Python virtual environment"
    fi
    
    # Set environment variables for local development
    export FLASK_ENV="development"
    export FLASK_DEBUG="true"
    export PORT="$API_PORT"
    export PYTHONUNBUFFERED="1"
    
    # NEW UNIFIED DATABASE ARCHITECTURE (August 2025)
    export ARROW_DATABASE_PATH="$(pwd)/databases/arrow_database.db"
    export USER_DATABASE_PATH="$(pwd)/databases/user_data.db"
    
    # Ensure spine calculation data migration
    ensure_spine_data_migration
    
    # Start Flask API
    python api.py > ../logs/api.log 2>&1 &
    
    API_PID=$!
    echo $API_PID > ../logs/api.pid
    
    cd ..
    success "Flask API backend started (PID: $API_PID) on http://localhost:$API_PORT"
}

# Function to start frontend
start_frontend() {
    log "Starting Nuxt 3 frontend on port $FRONTEND_PORT..."
    
    # Check if port is available
    check_port $FRONTEND_PORT "Frontend"
    
    cd frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        log "Installing frontend dependencies..."
        npm install
    fi
    
    # Set environment variables for local development
    export NODE_ENV="development"
    export PORT="$FRONTEND_PORT"
    # IMPORTANT: Set API base to direct port to avoid CORS issues
    export NUXT_PUBLIC_API_BASE="http://localhost:$API_PORT/api"
    
    log "Frontend will use API at: $NUXT_PUBLIC_API_BASE"
    
    # Start frontend server
    npm run dev > ../logs/frontend.log 2>&1 &
    
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    
    cd ..
    success "Nuxt 3 frontend started (PID: $FRONTEND_PID) on http://localhost:$FRONTEND_PORT"
}

# Function to check service health
check_health() {
    log "Checking service health..."
    
    # Wait a bit for services to start
    sleep 8
    
    # Check API health
    if curl -f -s "http://localhost:$API_PORT/api/health" > /dev/null; then
        success "✅ API backend is healthy at http://localhost:$API_PORT"
    else
        error "❌ API backend health check failed"
        log "API logs:"
        tail -n 10 logs/api.log || true
    fi
    
    # Check frontend
    if curl -f -s "http://localhost:$FRONTEND_PORT" > /dev/null; then
        success "✅ Frontend is healthy at http://localhost:$FRONTEND_PORT"
    else
        warning "⚠️  Frontend may still be starting up"
    fi
}

# Function to show status
show_status() {
    echo ""
    success "🏹 ArrowTuner Local Development Server Running!"
    echo "=================================="
    echo "  🎯 Frontend: http://localhost:$FRONTEND_PORT"
    echo "  🔧 API Backend: http://localhost:$API_PORT"
    echo "  📊 API Health: http://localhost:$API_PORT/api/health"
    echo "  📝 Logs: logs/"
    echo ""
    echo "🔧 Configuration:"
    echo "  Environment: $NODE_ENV"
    echo "  API URL: http://localhost:$API_PORT/api"
    echo "  No CORS issues - direct port access"
    echo ""
    echo "📖 Commands:"
    echo "  Stop: ./start-local-dev.sh stop"
    echo "  Restart: ./start-local-dev.sh restart"
    echo "  Status: ./start-local-dev.sh status"
    echo "  Logs: tail -f logs/api.log logs/frontend.log"
}

# Function to stop services
stop_services() {
    log "Stopping services..."
    
    # Kill processes by name pattern (more reliable)
    ps aux | grep "python api.py" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
    ps aux | grep "npm run dev" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
    
    # Clean up PID files if they exist
    if [ -f logs/api.pid ]; then
        API_PID=$(cat logs/api.pid)
        if [ -n "$API_PID" ] && kill -0 $API_PID 2>/dev/null; then
            log "Killing API backend (PID: $API_PID)..."
            kill -9 $API_PID 2>/dev/null || true
        fi
        rm -f logs/api.pid
    fi
    
    if [ -f logs/frontend.pid ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if [ -n "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
            log "Killing Frontend (PID: $FRONTEND_PID)..."
            kill -9 $FRONTEND_PID 2>/dev/null || true
        fi
        rm -f logs/frontend.pid
    fi
    
    # Wait for processes to actually terminate
    sleep 2
    
    # Final cleanup by port if lsof is available
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti:$API_PORT | xargs kill -9 2>/dev/null || true
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    fi
    
    success "Services stopped."
}

# Handle script termination (removed EXIT to allow script to exit cleanly)
trap stop_services INT TERM

# Main execution
case "${1:-start}" in
    start)
        log "🚀 Starting ArrowTuner Local Development Environment..."
        
        stop_services  # Clean up any existing processes
        sleep 1
        
        start_api
        start_frontend
        check_health
        show_status
        
        log "Services started successfully in background"
        log "Use './start-local-dev.sh stop' to stop services"
        log "Use './start-local-dev.sh status' to check service status"
        ;;
    
    stop)
        stop_services
        ;;
    
    restart)
        stop_services
        sleep 2
        start_api
        start_frontend
        check_health
        show_status
        ;;
    
    status)
        show_status
        if [ -f logs/api.pid ] && [ -f logs/frontend.pid ]; then
            API_PID=$(cat logs/api.pid)
            FRONTEND_PID=$(cat logs/frontend.pid)
            echo ""
            echo "Process Status:"
            if kill -0 $API_PID 2>/dev/null; then
                echo "  API (PID $API_PID): ✅ Running"
            else
                echo "  API (PID $API_PID): ❌ Not running"
            fi
            if kill -0 $FRONTEND_PID 2>/dev/null; then
                echo "  Frontend (PID $FRONTEND_PID): ✅ Running"
            else
                echo "  Frontend (PID $FRONTEND_PID): ❌ Not running"
            fi
        else
            echo "  Status: Not running (no PID files found)"
        fi
        ;;
    
    logs)
        if [ -f logs/api.log ] || [ -f logs/frontend.log ]; then
            echo "📝 Recent logs:"
            echo "==============="
            if [ -f logs/api.log ]; then
                echo ""
                echo "🔧 API Logs (last 20 lines):"
                tail -n 20 logs/api.log
            fi
            if [ -f logs/frontend.log ]; then
                echo ""
                echo "🎯 Frontend Logs (last 20 lines):"
                tail -n 20 logs/frontend.log
            fi
        else
            warning "No log files found"
        fi
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start both API and frontend servers"
        echo "  stop     - Stop all services"
        echo "  restart  - Stop and start services"
        echo "  status   - Show service status and URLs"
        echo "  logs     - Show recent logs from both services"
        echo ""
        echo "Environment variables:"
        echo "  API_PORT=5000         - Port for Flask API backend"
        echo "  FRONTEND_PORT=3000    - Port for Nuxt 3 frontend"
        exit 1
        ;;
esac