#!/bin/bash

# Quick Deploy - Fast, simple deployment without complex verification
# Uses standard Dockerfiles and minimal configuration for speed
# Usage: ./quick-deploy.sh [ssl] [domain]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check arguments
USE_SSL="$1"
DOMAIN="${2:-archerytool.online}"

if [ "$USE_SSL" = "ssl" ]; then
    COMPOSE_FILE="docker-compose.minimal-ssl.yml"
    echo -e "${BLUE}⚡ Quick Deploy - Archery Tools (SSL)${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}Domain: $DOMAIN${NC}"
else
    COMPOSE_FILE="docker-compose.minimal.yml"
    echo -e "${BLUE}⚡ Quick Deploy - Archery Tools${NC}"
    echo -e "${BLUE}===============================${NC}"
fi

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Step 1: Import data
echo -e "${BLUE}📦 Importing arrow data...${NC}"
./production-import-only.sh
print_status "Arrow data imported"

# Step 2: SSL Check (if needed)
if [ "$USE_SSL" = "ssl" ]; then
    echo -e "${BLUE}🔍 Checking SSL certificates...${NC}"
    LOCAL_SSL_PATH="./deploy/ssl"
    
    if [ ! -f "$LOCAL_SSL_PATH/fullchain.pem" ] || [ ! -f "$LOCAL_SSL_PATH/privkey.pem" ]; then
        print_warning "SSL certificates not found in $LOCAL_SSL_PATH"
        echo -e "${BLUE}For SSL deployment, use: ./deploy-production-ssl.sh${NC}"
        echo -e "${BLUE}For HTTP testing, use: ./quick-deploy.sh${NC}"
        exit 1
    fi
    print_status "SSL certificates found"
fi

# Step 3: Quick cleanup
echo -e "${BLUE}🧹 Quick cleanup...${NC}"
docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
print_status "Cleanup completed"

# Step 4: Quick deploy
echo -e "${BLUE}🚀 Starting quick deployment...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d --build

print_status "Services started"

# Step 5: Wait and check
echo -e "${BLUE}⏳ Waiting for services (30s)...${NC}"
sleep 30

# Show status
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose -f "$COMPOSE_FILE" ps

# Quick health check
echo -e "${BLUE}🔍 Quick health check...${NC}"

if [ "$USE_SSL" = "ssl" ]; then
    # HTTPS health checks
    MAIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN -k 2>/dev/null || echo "000")
    API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/api/health -k 2>/dev/null || echo "000")
    
    if [ "$MAIN_STATUS" = "200" ]; then
        print_status "HTTPS site is responding (HTTP $MAIN_STATUS)"
    else
        print_warning "HTTPS site not ready yet (HTTP $MAIN_STATUS)"
    fi
    
    if [ "$API_STATUS" = "200" ]; then
        print_status "HTTPS API is responding (HTTP $API_STATUS)"
    else
        print_warning "HTTPS API not ready yet (HTTP $API_STATUS)"
    fi
    
    echo -e "${GREEN}⚡ Quick SSL deployment completed!${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${GREEN}Access URLs:${NC}"
    echo -e "${BLUE}  🌐 Website: https://$DOMAIN${NC}"
    echo -e "${BLUE}  🔌 API: https://$DOMAIN/api${NC}"
    echo -e "${BLUE}  💚 Health: https://$DOMAIN/api/health${NC}"
    
else
    # HTTP health checks
    API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/simple-health 2>/dev/null || echo "000")
    FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
    NGINX_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health 2>/dev/null || echo "000")
    
    if [ "$API_STATUS" = "200" ]; then
        print_status "API is responding (HTTP $API_STATUS)"
    else
        print_warning "API not ready yet (HTTP $API_STATUS)"
    fi
    
    if [ "$FRONTEND_STATUS" = "200" ]; then
        print_status "Frontend is responding (HTTP $FRONTEND_STATUS)"
    else
        print_warning "Frontend not ready yet (HTTP $FRONTEND_STATUS)"
    fi
    
    if [ "$NGINX_STATUS" = "200" ]; then
        print_status "Nginx is responding (HTTP $NGINX_STATUS)"
    else
        print_warning "Nginx not ready yet (HTTP $NGINX_STATUS)"
    fi
    
    echo -e "${GREEN}⚡ Quick deployment completed!${NC}"
    echo -e "${BLUE}===============================${NC}"
    echo -e "${GREEN}Access URLs:${NC}"
    echo -e "${BLUE}  Main: http://localhost${NC}"
    echo -e "${BLUE}  API: http://localhost:5000${NC}"
    echo -e "${BLUE}  Frontend: http://localhost:3000${NC}"
fi

echo ""
echo -e "${YELLOW}Commands:${NC}"
echo -e "${YELLOW}  Logs: docker-compose -f $COMPOSE_FILE logs -f${NC}"
echo -e "${YELLOW}  Stop: docker-compose -f $COMPOSE_FILE down${NC}"
if [ "$USE_SSL" = "ssl" ]; then
    echo -e "${YELLOW}  Restart: ./quick-deploy.sh ssl $DOMAIN${NC}"
else
    echo -e "${YELLOW}  Restart: ./quick-deploy.sh${NC}"
fi

# Final warning if services not ready
if [ "$USE_SSL" = "ssl" ]; then
    if [ "$MAIN_STATUS" != "200" ] || [ "$API_STATUS" != "200" ]; then
        echo ""
        print_warning "Some services may still be starting up. Wait a moment and check again."
        echo -e "${BLUE}To check again: curl -k https://$DOMAIN/api/health${NC}"
    fi
else
    if [ "$API_STATUS" != "200" ] || [ "$FRONTEND_STATUS" != "200" ]; then
        echo ""
        print_warning "Some services may still be starting up. Wait a moment and check again."
        echo -e "${BLUE}To check again: curl http://localhost:5000/api/simple-health${NC}"
    fi
fi