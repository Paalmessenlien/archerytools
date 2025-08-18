#!/bin/bash

# Deploy with Complete Cleanup - Fixes ContainerConfig errors
# This script performs a complete cleanup and fresh deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

COMPOSE_FILE="${1:-docker-compose.fixed.yml}"

echo -e "${BLUE}🚀 Complete Cleanup and Deployment${NC}"
echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}Using compose file: $COMPOSE_FILE${NC}"

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

# Step 1: Import data first
echo -e "${BLUE}📦 Step 1: Importing arrow data...${NC}"
./production-import-only.sh
print_status "Arrow data imported"

# Step 2: Complete Docker cleanup
echo -e "${BLUE}🧹 Step 2: Complete Docker cleanup...${NC}"

# Stop all containers
echo "  Stopping all containers..."
docker-compose -f docker-compose.enhanced-ssl.yml down --remove-orphans 2>/dev/null || true
docker-compose down --remove-orphans 2>/dev/null || true

# Remove specific containers
echo "  Removing archerytools containers..."
docker rm -f $(docker ps -aq --filter "name=archerytools") 2>/dev/null || true
docker rm -f $(docker ps -aq --filter "name=arrowtuner") 2>/dev/null || true

# Clean up images
echo "  Removing archerytools images..."
docker rmi $(docker images --filter "reference=archerytools*" -q) 2>/dev/null || true
docker rmi $(docker images --filter "dangling=true" -q) 2>/dev/null || true

# System cleanup
echo "  Performing system cleanup..."
docker system prune -f
docker container prune -f
docker network prune -f

print_status "Complete cleanup finished"

# Step 3: Check compose file
echo -e "${BLUE}🔍 Step 3: Validating compose file...${NC}"
if [ ! -f "$COMPOSE_FILE" ]; then
    print_error "Compose file $COMPOSE_FILE not found!"
    echo -e "${YELLOW}Available compose files:${NC}"
    ls -la docker-compose*.yml
    exit 1
fi

# Validate compose file
docker-compose -f "$COMPOSE_FILE" config >/dev/null
print_status "Compose file validation passed"

# Step 4: Fresh deployment
echo -e "${BLUE}🚀 Step 4: Fresh deployment...${NC}"
echo "  Building and starting services..."
docker-compose -f "$COMPOSE_FILE" up -d --build --force-recreate

print_status "Services started"

# Step 5: Wait for health checks
echo -e "${BLUE}⏳ Step 5: Waiting for services to be healthy...${NC}"
sleep 30

# Check service status
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose -f "$COMPOSE_FILE" ps

# Step 6: Health verification
echo -e "${BLUE}🔍 Step 6: Health verification...${NC}"

# Test API
API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/simple-health 2>/dev/null || echo "000")
if [ "$API_HEALTH" = "200" ]; then
    print_status "API health check passed (HTTP $API_HEALTH)"
else
    print_warning "API health check failed (HTTP $API_HEALTH)"
    echo "API logs:"
    docker-compose -f "$COMPOSE_FILE" logs --tail=10 api
fi

# Test Frontend
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
if [ "$FRONTEND_HEALTH" = "200" ]; then
    print_status "Frontend health check passed (HTTP $FRONTEND_HEALTH)"
else
    print_warning "Frontend health check failed (HTTP $FRONTEND_HEALTH)"
    echo "Frontend logs:"
    docker-compose -f "$COMPOSE_FILE" logs --tail=10 frontend
fi

# Test Nginx (if present)
if docker-compose -f "$COMPOSE_FILE" ps nginx >/dev/null 2>&1; then
    NGINX_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health 2>/dev/null || echo "000")
    if [ "$NGINX_HEALTH" = "200" ]; then
        print_status "Nginx health check passed (HTTP $NGINX_HEALTH)"
    else
        print_warning "Nginx health check failed (HTTP $NGINX_HEALTH)"
        echo "Nginx logs:"
        docker-compose -f "$COMPOSE_FILE" logs --tail=10 nginx
    fi
fi

echo -e "${GREEN}🎉 Deployment completed!${NC}"
echo -e "${BLUE}==================================${NC}"
echo -e "${GREEN}Access URLs:${NC}"
echo -e "${BLUE}  API: http://localhost:5000${NC}"
echo -e "${BLUE}  Frontend: http://localhost:3000${NC}"
if docker-compose -f "$COMPOSE_FILE" ps nginx >/dev/null 2>&1; then
    echo -e "${BLUE}  Main: http://localhost${NC}"
fi
echo ""
echo -e "${YELLOW}To view logs: docker-compose -f $COMPOSE_FILE logs -f${NC}"
echo -e "${YELLOW}To stop: docker-compose -f $COMPOSE_FILE down${NC}"