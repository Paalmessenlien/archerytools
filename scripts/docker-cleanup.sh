#!/bin/bash

# Docker Cleanup Script for ArrowTuner
# Handles orphan containers and ensures clean deployments

set -e

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

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    error "Docker is not running or you don't have permission to access it"
    exit 1
fi

log "Starting Docker cleanup for ArrowTuner..."

# Stop all ArrowTuner containers
log "Stopping ArrowTuner containers..."
docker ps -q --filter "name=arrowtuner" | xargs -r docker stop
success "Stopped all ArrowTuner containers"

# Remove all ArrowTuner containers (including stopped ones)
log "Removing ArrowTuner containers..."
docker ps -aq --filter "name=arrowtuner" | xargs -r docker rm
success "Removed all ArrowTuner containers"

# Clean up orphaned containers from all compose files
log "Cleaning up orphan containers..."
COMPOSE_FILES=(
    "docker-compose.yml"
    "docker-compose.ssl.yml"
    "docker-compose.dev.yml"
    "docker-compose.prod.yml"
    "docker-compose.simple.yml"
)

for compose_file in "${COMPOSE_FILES[@]}"; do
    if [ -f "$compose_file" ]; then
        log "Cleaning up with $compose_file..."
        docker-compose -f "$compose_file" down --remove-orphans --volumes 2>/dev/null || true
    fi
done

# Remove dangling images (optional)
if [ "${1:-}" = "--clean-images" ]; then
    log "Removing dangling Docker images..."
    docker image prune -f
    success "Removed dangling images"
fi

# Remove unused networks
log "Removing unused Docker networks..."
docker network prune -f >/dev/null 2>&1 || true
success "Cleaned up unused networks"

# Remove unused volumes (be careful with this)
if [ "${1:-}" = "--clean-volumes" ]; then
    warning "Removing unused Docker volumes (this may delete data)..."
    docker volume prune -f
    success "Removed unused volumes"
fi

success "Docker cleanup completed successfully!"

log "You can now run your Docker deployment without --remove-orphans"
log ""
log "Usage examples:"
log "  docker-compose up -d"
log "  docker-compose -f docker-compose.ssl.yml up -d"
log ""
log "Options:"
log "  $0 --clean-images   Also remove dangling images"
log "  $0 --clean-volumes  Also remove unused volumes (WARNING: may delete data)"