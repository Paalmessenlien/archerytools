#!/bin/bash

# Nuclear Docker Reset - Complete Docker state cleanup
# This script performs the most thorough Docker cleanup possible

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}☢️  Nuclear Docker Reset${NC}"
echo -e "${RED}========================${NC}"
echo -e "${YELLOW}WARNING: This will remove ALL Docker containers, images, volumes, and networks${NC}"
echo -e "${YELLOW}Only continue if you want to completely reset Docker state${NC}"
echo ""

# Ask for confirmation
read -p "Are you sure you want to proceed? (type 'YES' to continue): " confirm
if [ "$confirm" != "YES" ]; then
    echo "Cancelled."
    exit 1
fi

echo -e "${RED}🧹 Starting nuclear cleanup...${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Step 1: Stop all running containers
echo -e "${BLUE}1. Stopping all running containers...${NC}"
docker stop $(docker ps -aq) 2>/dev/null || true
print_status "All containers stopped"

# Step 2: Remove all containers
echo -e "${BLUE}2. Removing all containers...${NC}"
docker rm -f $(docker ps -aq) 2>/dev/null || true
print_status "All containers removed"

# Step 3: Remove all images
echo -e "${BLUE}3. Removing all images...${NC}"
docker rmi -f $(docker images -aq) 2>/dev/null || true
print_status "All images removed"

# Step 4: Remove all volumes
echo -e "${BLUE}4. Removing all volumes...${NC}"
docker volume rm $(docker volume ls -q) 2>/dev/null || true
print_status "All volumes removed"

# Step 5: Remove all networks
echo -e "${BLUE}5. Removing all networks...${NC}"
docker network rm $(docker network ls -q) 2>/dev/null || true
print_status "All networks removed"

# Step 6: Clean up build cache
echo -e "${BLUE}6. Cleaning build cache...${NC}"
docker builder prune -a -f 2>/dev/null || true
print_status "Build cache cleaned"

# Step 7: System prune (everything)
echo -e "${BLUE}7. Final system prune...${NC}"
docker system prune -a -f --volumes 2>/dev/null || true
print_status "System prune completed"

# Step 8: Reset Docker daemon
echo -e "${BLUE}8. Restarting Docker daemon...${NC}"
sudo systemctl restart docker
sleep 5

# Wait for Docker to be ready
echo -e "${BLUE}9. Waiting for Docker to be ready...${NC}"
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    if docker info >/dev/null 2>&1; then
        print_status "Docker daemon is ready"
        break
    fi
    echo "   Attempt $attempt/$max_attempts - waiting for Docker..."
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo -e "${RED}❌ Docker daemon failed to start properly${NC}"
    exit 1
fi

# Step 10: Verify clean state
echo -e "${BLUE}10. Verifying clean state...${NC}"
echo "   Containers: $(docker ps -aq | wc -l)"
echo "   Images: $(docker images -q | wc -l)"
echo "   Volumes: $(docker volume ls -q | wc -l)"
echo "   Networks: $(($(docker network ls -q | wc -l) - 3))"  # Subtract default networks

print_status "Nuclear cleanup completed!"

echo ""
echo -e "${GREEN}🎉 Docker has been completely reset!${NC}"
echo -e "${BLUE}========================${NC}"
echo -e "${GREEN}Next steps:${NC}"
echo -e "${GREEN}1. Import data: ./production-import-only.sh${NC}"
echo -e "${GREEN}2. Quick deploy: ./quick-deploy.sh${NC}"
echo -e "${GREEN}3. Or SSL deploy: ./deploy-production-ssl.sh yourdomain.com${NC}"
echo ""
echo -e "${YELLOW}Note: First deployment will take longer as all images need to be downloaded${NC}"