#!/bin/bash

# Quick Deploy - Fast, simple deployment without complex verification
# Uses standard Dockerfiles and minimal configuration for speed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}⚡ Quick Deploy - Archery Tools${NC}"
echo -e "${BLUE}===============================${NC}"

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

# Step 2: Quick cleanup
echo -e "${BLUE}🧹 Quick cleanup...${NC}"
docker-compose -f docker-compose.minimal.yml down --remove-orphans 2>/dev/null || true
print_status "Cleanup completed"

# Step 3: Quick deploy
echo -e "${BLUE}🚀 Starting quick deployment...${NC}"
docker-compose -f docker-compose.minimal.yml up -d --build

print_status "Services started"

# Step 4: Wait and check
echo -e "${BLUE}⏳ Waiting for services (30s)...${NC}"
sleep 30

# Show status
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose -f docker-compose.minimal.yml ps

# Quick health check
echo -e "${BLUE}🔍 Quick health check...${NC}"

API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/simple-health 2>/dev/null || echo "000")
if [ "$API_STATUS" = "200" ]; then
    print_status "API is responding (HTTP $API_STATUS)"
else
    print_warning "API not ready yet (HTTP $API_STATUS)"
fi

FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
if [ "$FRONTEND_STATUS" = "200" ]; then
    print_status "Frontend is responding (HTTP $FRONTEND_STATUS)"
else
    print_warning "Frontend not ready yet (HTTP $FRONTEND_STATUS)"
fi

NGINX_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health 2>/dev/null || echo "000")
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
echo ""
echo -e "${YELLOW}Commands:${NC}"
echo -e "${YELLOW}  Logs: docker-compose -f docker-compose.minimal.yml logs -f${NC}"
echo -e "${YELLOW}  Stop: docker-compose -f docker-compose.minimal.yml down${NC}"
echo -e "${YELLOW}  Restart: ./quick-deploy.sh${NC}"

if [ "$API_STATUS" != "200" ] || [ "$FRONTEND_STATUS" != "200" ]; then
    echo ""
    print_warning "Some services may still be starting up. Wait a moment and check again."
    echo -e "${BLUE}To check again: curl http://localhost:5000/api/simple-health${NC}"
fi