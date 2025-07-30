#!/bin/bash

# Docker Production Setup Script
# Comprehensive production deployment with cleanup integration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${1:-docker-compose.enhanced-ssl.yml}"
CLEANUP_FLAG="${2:-auto}"

echo -e "${BLUE}🐳 Starting Docker Production Setup${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Compose file: $COMPOSE_FILE${NC}"
echo -e "${BLUE}Cleanup mode: $CLEANUP_FLAG${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is running"

# Check if Docker Compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    print_error "Docker Compose file '$COMPOSE_FILE' not found"
    echo -e "${YELLOW}Available compose files:${NC}"
    ls -1 docker-compose*.yml 2>/dev/null || echo "No compose files found"
    exit 1
fi

print_status "Docker Compose file found: $COMPOSE_FILE"

# Run cleanup if requested or if databases don't exist
NEED_CLEANUP=false

if [ "$CLEANUP_FLAG" = "force" ]; then
    NEED_CLEANUP=true
    echo -e "${YELLOW}🧹 Forced cleanup requested${NC}"
elif [ "$CLEANUP_FLAG" = "auto" ]; then
    # Check if databases exist and have data
    if [ ! -f "arrow_scraper/arrow_database.db" ] || [ ! -f "arrow_scraper/user_data.db" ]; then
        NEED_CLEANUP=true
        echo -e "${YELLOW}🧹 Missing databases detected - cleanup needed${NC}"
    else
        # Check if databases have minimal data
        ARROW_COUNT=$(sqlite3 arrow_scraper/arrow_database.db "SELECT COUNT(*) FROM arrows;" 2>/dev/null || echo "0")
        if [ "$ARROW_COUNT" -lt 100 ]; then
            NEED_CLEANUP=true
            echo -e "${YELLOW}🧹 Insufficient arrow data ($ARROW_COUNT arrows) - cleanup needed${NC}"
        fi
    fi
fi

# Ensure virtual environment is set up
echo -e "${BLUE}🐍 Ensuring Python virtual environment is ready...${NC}"
if [ -f "./setup-venv.sh" ]; then
    ./setup-venv.sh
    print_status "Virtual environment verified"
else
    print_warning "Virtual environment setup script not found - attempting manual setup"
    cd arrow_scraper
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        print_status "Virtual environment created manually"
    fi
    cd ..
fi

# Run cleanup if needed
if [ "$NEED_CLEANUP" = "true" ]; then
    echo -e "${BLUE}🚀 Running production cleanup first...${NC}"
    if [ -f "./production-cleanup.sh" ]; then
        ./production-cleanup.sh
        print_status "Production cleanup completed"
    else
        print_error "Production cleanup script not found"
        exit 1
    fi
else
    print_status "Skipping cleanup - databases appear to be ready"
fi

# Stop any existing containers
echo -e "${BLUE}🛑 Stopping existing containers...${NC}"
docker-compose -f "$COMPOSE_FILE" down --remove-orphans || true
print_status "Existing containers stopped"

# Clean up orphaned containers and networks
echo -e "${BLUE}🧹 Cleaning up Docker resources...${NC}"
docker system prune -f || true
docker network prune -f || true
print_status "Docker resources cleaned"

# Create necessary directories for Docker volumes
echo -e "${BLUE}📁 Creating Docker volume directories...${NC}"
mkdir -p docker-volumes/user-data
mkdir -p docker-volumes/arrow-data
mkdir -p docker-volumes/nginx-conf
mkdir -p docker-volumes/nginx-logs
mkdir -p docker-volumes/ssl-certs

# Copy databases to Docker volumes if they exist
if [ -f "arrow_scraper/arrow_database.db" ]; then
    cp arrow_scraper/arrow_database.db docker-volumes/arrow-data/
    print_status "Arrow database copied to Docker volume"
fi

if [ -f "arrow_scraper/user_data.db" ]; then
    cp arrow_scraper/user_data.db docker-volumes/user-data/
    print_status "User database copied to Docker volume"
fi

# Set proper permissions
chmod -R 755 docker-volumes/
print_status "Docker volume permissions set"

# Build and start containers
echo -e "${BLUE}🏗️  Building and starting containers...${NC}"
docker-compose -f "$COMPOSE_FILE" build --no-cache
print_status "Containers built"

echo -e "${BLUE}🚀 Starting containers...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d
print_status "Containers started"

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check container status
echo -e "${BLUE}📊 Container status:${NC}"
docker-compose -f "$COMPOSE_FILE" ps

# Health checks
echo -e "${BLUE}🔍 Running health checks...${NC}"

# Check API health
API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health || echo "000")
if [ "$API_HEALTH" = "200" ]; then
    print_status "API health check passed"
else
    print_warning "API health check failed (HTTP $API_HEALTH)"
fi

# Check frontend
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "000")
if [ "$FRONTEND_HEALTH" = "200" ]; then
    print_status "Frontend health check passed"
else
    print_warning "Frontend health check failed (HTTP $FRONTEND_HEALTH)"
fi

# Check database connections
echo -e "${BLUE}🗄️  Testing database connections...${NC}"
docker exec archerytools-api-1 python -c "
import sqlite3
import os

try:
    # Test arrow database
    conn = sqlite3.connect('/app/arrow_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM arrows')
    arrow_count = cursor.fetchone()[0]
    conn.close()
    print(f'✅ Arrow database: {arrow_count} arrows')
except Exception as e:
    print(f'❌ Arrow database error: {e}')

try:
    # Test user database
    conn = sqlite3.connect('/app/user_data/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE type=\"table\"')
    table_count = cursor.fetchone()[0]
    conn.close()
    print(f'✅ User database: {table_count} tables')
except Exception as e:
    print(f'❌ User database error: {e}')
" 2>/dev/null || print_warning "Database connection test failed"

# Show final status
echo -e "${BLUE}📈 Final deployment status:${NC}"
echo -e "${GREEN}Services:${NC}"
echo -e "  • API Server: http://localhost:5000"
echo -e "  • Frontend: http://localhost:3000"
echo -e "  • Combined (nginx): http://localhost (if configured)"

# Show logs for troubleshooting
echo -e "${BLUE}📋 Recent container logs:${NC}"
echo -e "${YELLOW}API logs:${NC}"
docker-compose -f "$COMPOSE_FILE" logs --tail=10 api || true

echo -e "${YELLOW}Frontend logs:${NC}"
docker-compose -f "$COMPOSE_FILE" logs --tail=10 frontend || true

# Show resource usage
echo -e "${BLUE}💻 Resource usage:${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" || true

# Final recommendations
echo -e "${GREEN}🎉 Docker production setup completed!${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}Next steps:${NC}"
echo -e "${GREEN}1. Test the application:${NC}"
echo -e "   curl http://localhost:5000/api/health"
echo -e "   curl http://localhost:3000"
echo -e "${GREEN}2. Check logs if needed:${NC}"
echo -e "   docker-compose -f $COMPOSE_FILE logs -f api"
echo -e "   docker-compose -f $COMPOSE_FILE logs -f frontend"
echo -e "${GREEN}3. Scale if needed:${NC}"
echo -e "   docker-compose -f $COMPOSE_FILE up -d --scale api=2"
echo -e "${GREEN}4. Stop when done:${NC}"
echo -e "   docker-compose -f $COMPOSE_FILE down"

# Save deployment info
cat > "deployment-info.txt" << EOF
Docker Production Deployment
===========================
Date: $(date)
Compose File: $COMPOSE_FILE
Cleanup Performed: $NEED_CLEANUP

Container Status:
$(docker-compose -f "$COMPOSE_FILE" ps 2>/dev/null || echo "Unable to get container status")

Health Check Results:
- API (port 5000): HTTP $API_HEALTH
- Frontend (port 3000): HTTP $FRONTEND_HEALTH

Access URLs:
- API: http://localhost:5000
- Frontend: http://localhost:3000
- Health: http://localhost:5000/api/health

Useful Commands:
- View logs: docker-compose -f $COMPOSE_FILE logs -f
- Restart: docker-compose -f $COMPOSE_FILE restart
- Stop: docker-compose -f $COMPOSE_FILE down
- Rebuild: docker-compose -f $COMPOSE_FILE up -d --build
EOF

print_status "Deployment info saved to deployment-info.txt"
echo -e "${BLUE}Docker production setup completed at $(date)${NC}"