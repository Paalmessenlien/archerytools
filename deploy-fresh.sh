#!/bin/bash

# Fresh Deploy - Uses completely new container names to avoid ContainerConfig errors
# This bypasses Docker Compose cache issues by using fresh configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🆕 Fresh Deploy - Bypass ContainerConfig Error${NC}"
echo -e "${BLUE}===============================================${NC}"

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

# Step 2: Clean up any existing fresh containers
echo -e "${BLUE}🧹 Cleaning up existing fresh containers...${NC}"
docker rm -f fresh-archery-api fresh-archery-frontend fresh-archery-nginx 2>/dev/null || true
docker-compose -f docker-compose.fresh.yml down 2>/dev/null || true
print_status "Fresh containers cleaned"

# Step 3: Remove any conflicting images
echo -e "${BLUE}🏗️  Removing potentially conflicting images...${NC}"
docker rmi archerytools_archery-api archerytools_archery-frontend 2>/dev/null || true
print_status "Conflicting images removed"

# Step 4: Deploy with fresh configuration
echo -e "${BLUE}🚀 Starting fresh deployment...${NC}"
docker-compose -f docker-compose.fresh.yml up -d --build

print_status "Fresh services started"

# Step 5: Wait for services
echo -e "${BLUE}⏳ Waiting for services (45s)...${NC}"
sleep 45

# Step 6: Show status
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose -f docker-compose.fresh.yml ps

# Step 7: Health checks
echo -e "${BLUE}🔍 Health checks...${NC}"

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

echo -e "${GREEN}🆕 Fresh deployment completed!${NC}"
echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}Access URLs:${NC}"
echo -e "${BLUE}  Main: http://localhost${NC}"
echo -e "${BLUE}  API: http://localhost:5000${NC}"
echo -e "${BLUE}  Frontend: http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}Commands:${NC}"
echo -e "${YELLOW}  Logs: docker-compose -f docker-compose.fresh.yml logs -f${NC}"
echo -e "${YELLOW}  Stop: docker-compose -f docker-compose.fresh.yml down${NC}"
echo -e "${YELLOW}  Restart: ./deploy-fresh.sh${NC}"

if [ "$API_STATUS" != "200" ] || [ "$FRONTEND_STATUS" != "200" ]; then
    echo ""
    print_warning "Some services may still be starting up. Wait a moment and check again."
    echo -e "${BLUE}To check again: curl http://localhost:5000/api/simple-health${NC}"
    echo ""
    echo -e "${YELLOW}If issues persist, check logs:${NC}"
    echo -e "${YELLOW}  docker-compose -f docker-compose.fresh.yml logs api${NC}"
    echo -e "${YELLOW}  docker-compose -f docker-compose.fresh.yml logs frontend${NC}"
fi