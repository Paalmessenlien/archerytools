#!/bin/bash

# Arrow Tuner Dual Architecture Startup Script
# Starts both the Nuxt 3 frontend and Flask API backend

set -e

# Configuration
API_PORT=${API_PORT:-5000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}
ENVIRONMENT=${NODE_ENV:-production}

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
    error "Please run this script from the arrowtuner2 root directory"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to check if port is available
check_port() {
    local port=$1
    local service_name=$2
    
    if command -v lsof >/dev/null 2>&1; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            error "$service_name port $port is already in use"
            log "Attempting to kill existing process on port $port..."
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
            sleep 2
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                error "Failed to free port $port. Please check for running services."
                exit 1
            fi
        fi
    fi
}

# Function to run database migrations
run_migrations() {
    log "Running database migrations..."
    
    cd arrow_scraper
    
    # Activate virtual environment if it exists
    if [ -f "../venv/bin/activate" ]; then
        source ../venv/bin/activate
    fi
    
    # Run the migration script
    if [ -f "run-migrations.py" ]; then
        python run-migrations.py
        if [ $? -eq 0 ]; then
            success "Database migrations completed successfully"
        else
            error "Database migrations failed!"
            cd ..
            return 1
        fi
    else
        warning "Migration runner not found, checking for individual migrations..."
        # Try the legacy migration approach
        if [ -f "migrate_bow_setups_schema.py" ]; then
            python migrate_bow_setups_schema.py || true
        fi
    fi
    
    cd ..
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
    
    # Start Flask API with port environment variable
    if [ "$ENVIRONMENT" = "development" ]; then
        PORT=$API_PORT FLASK_DEBUG=true PYTHONUNBUFFERED=1 python api.py > ../logs/api.log 2>&1 &
    else
        # Use python for now, install gunicorn for production
        PORT=$API_PORT PYTHONUNBUFFERED=1 python api.py > ../logs/api.log 2>&1 &
    fi
    
    API_PID=$!
    echo $API_PID > ../logs/api.pid
    
    cd ..
    success "Flask API backend started (PID: $API_PID)"
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
    
    # Start frontend server
    if [ "$ENVIRONMENT" = "development" ]; then
        PORT=$FRONTEND_PORT npm run dev > ../logs/frontend.log 2>&1 &
    else
        npm run build
        PORT=$FRONTEND_PORT npm run preview > ../logs/frontend.log 2>&1 &
    fi
    
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    
    cd ..
    success "Nuxt 3 frontend started (PID: $FRONTEND_PID)"
}

# Function to check service health
check_health() {
    log "Checking service health..."
    
    # Check API health
    sleep 5
    if curl -f -s "http://localhost:$API_PORT/api/health" > /dev/null; then
        success "API backend is healthy"
    else
        error "API backend health check failed"
    fi
    
    # Check frontend
    if curl -f -s "http://localhost:$FRONTEND_PORT" > /dev/null; then
        success "Frontend is healthy"
    else
        warning "Frontend may still be starting up"
    fi
}

# Function to show status
show_status() {
    log "ArrowTuner Dual Architecture Status:"
    echo "  Frontend: http://localhost:$FRONTEND_PORT"
    echo "  API Backend: http://localhost:$API_PORT"
    echo "  Environment: $ENVIRONMENT"
    echo "  Logs: logs/"
}

# Function to stop services
stop_services() {
    log "Stopping services..."
    
    # Try to kill the entire process group if PGID is known
    if [ -f logs/script.pgid ]; then
        PGID=$(cat logs/script.pgid)
        if [ -n "$PGID" ] && kill -0 -- -$PGID 2>/dev/null; then # Check if process group exists and PGID is not empty
            log "Killing process group $PGID..."
            kill -- -$PGID 2>/dev/null || true
            sleep 2 # Give processes time to terminate
            if [ -n "$PGID" ] && kill -0 -- -$PGID 2>/dev/null; then
                warning "Process group $PGID still running, attempting forceful kill..."
                kill -9 -- -$PGID 2>/dev/null || true
            fi
        fi
        rm -f logs/script.pgid
        rm -f logs/script.pid
    fi

    # Clean up individual PID files if they exist (fallback/cleanup)
    if [ -f logs/api.pid ]; then
        API_PID=$(cat logs/api.pid)
        if [ -n "$API_PID" ] && kill -0 $API_PID 2>/dev/null; then # Check if process exists and PID is not empty
            log "Killing API backend (PID: $API_PID)..."
            kill $API_PID 2>/dev/null || true
        fi
        rm -f logs/api.pid
    fi
    
    if [ -f logs/frontend.pid ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if [ -n "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then # Check if process exists and PID is not empty
            log "Killing Frontend (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID 2>/dev/null || true
        fi
        rm -f logs/frontend.pid
    fi
    
    success "Services stopped."
}

# Handle script termination
trap stop_services INT TERM

# Main execution
case "${1:-start}" in
    start)
        log "Starting ArrowTuner Dual Architecture..."
        
        # Save script's PID and PGID for robust stopping
        echo $$ > logs/script.pid
        python -c "import os; print(os.getpgrp())" > logs/script.pgid
        
        # Run migrations before starting services
        run_migrations
        if [ $? -ne 0 ]; then
            error "Migration failed, aborting startup"
            exit 1
        fi
        
        start_api
        start_frontend
        check_health
        show_status
        
        ;;
    
    stop)
        stop_services
        ;;
    
    restart)
        stop_services
        sleep 2
        
        # Run migrations before starting services
        run_migrations
        if [ $? -ne 0 ]; then
            error "Migration failed, aborting startup"
            exit 1
        fi
        
        start_api
        start_frontend
        check_health
        show_status
        ;;
    
    status)
        show_status
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Environment variables:"
        echo "  API_PORT=5000         - Port for Flask API backend"
        echo "  FRONTEND_PORT=3000    - Port for Nuxt 3 frontend"
        echo "  NODE_ENV=production   - Environment (development|production)"
        exit 1
        ;;
esac