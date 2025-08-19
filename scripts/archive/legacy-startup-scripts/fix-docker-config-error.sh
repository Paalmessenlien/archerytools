#!/bin/bash

# Fix Docker Compose ContainerConfig Error
# This script resolves the 'ContainerConfig' KeyError by cleaning up Docker state

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Fixing Docker Compose ContainerConfig Error${NC}"
echo -e "${BLUE}===============================================${NC}"

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

# Step 1: Stop all containers
echo -e "${BLUE}🛑 Stopping all containers...${NC}"
docker-compose -f docker-compose.enhanced-ssl.yml down --remove-orphans || true
docker-compose down --remove-orphans || true
print_status "Containers stopped"

# Step 2: Clean up Docker system
echo -e "${BLUE}🧹 Cleaning Docker system...${NC}"
docker system prune -f
docker container prune -f
docker network prune -f
docker volume prune -f
print_status "Docker system cleaned"

# Step 3: Remove specific problematic containers
echo -e "${BLUE}🗑️  Removing specific containers...${NC}"
docker rm -f arrowtuner-api-enhanced arrowtuner-db-verifier arrowtuner-frontend-enhanced arrowtuner-nginx-enhanced 2>/dev/null || true
print_status "Specific containers removed"

# Step 4: Remove images to force rebuild
echo -e "${BLUE}🏗️  Removing images to force fresh build...${NC}"
docker rmi archerytools_api archerytools_frontend archerytools_db-verifier 2>/dev/null || true
docker rmi $(docker images --filter "dangling=true" -q) 2>/dev/null || true
print_status "Images removed"

# Step 5: Clean up Docker buildx cache
echo -e "${BLUE}💾 Cleaning build cache...${NC}"
docker builder prune -f || true
print_status "Build cache cleaned"

# Step 6: Check Docker daemon
echo -e "${BLUE}🐳 Checking Docker daemon...${NC}"
if ! docker info >/dev/null 2>&1; then
    print_error "Docker daemon is not running"
    exit 1
fi
print_status "Docker daemon is running"

# Step 7: Import data before rebuild
echo -e "${BLUE}📦 Importing arrow data...${NC}"
./production-import-only.sh
print_status "Arrow data imported"

echo -e "${GREEN}🎉 Docker cleanup completed!${NC}"
echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}Next steps:${NC}"
echo -e "${GREEN}1. Try deployment again:${NC}"
echo -e "   docker-compose -f docker-compose.enhanced-ssl.yml up -d --build"
echo -e "${GREEN}2. Or use the smart deployment script:${NC}"
echo -e "   ./check-ssl-and-deploy.sh"
echo ""
echo -e "${YELLOW}Note: This will take longer as images need to be rebuilt${NC}"