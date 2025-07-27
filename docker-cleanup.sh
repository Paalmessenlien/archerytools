#!/bin/bash

# Docker Cleanup Script for ArrowTuner
# Run this before deployments to avoid orphan container issues

set -e

echo "🐳 ArrowTuner Docker Cleanup"
echo "============================"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running or you don't have permission"
    echo "   Try: sudo ./docker-cleanup.sh"
    exit 1
fi

echo "🧹 Stopping and removing ArrowTuner containers..."

# Stop all ArrowTuner containers
docker ps -q --filter "name=arrowtuner" | xargs -r docker stop 2>/dev/null || true

# Remove all ArrowTuner containers
docker ps -aq --filter "name=arrowtuner" | xargs -r docker rm 2>/dev/null || true

echo "🔄 Cleaning up with all compose files..."

# Clean up with all compose files to remove orphans
COMPOSE_FILES=(
    "docker-compose.yml"
    "docker-compose.ssl.yml" 
    "docker-compose.dev.yml"
    "docker-compose.prod.yml"
    "docker-compose.simple.yml"
)

for compose_file in "${COMPOSE_FILES[@]}"; do
    if [ -f "$compose_file" ]; then
        echo "   📁 Cleaning up with $compose_file"
        docker-compose -f "$compose_file" down --remove-orphans --volumes 2>/dev/null || true
    fi
done

# Clean up networks
echo "🌐 Cleaning up networks..."
docker network prune -f >/dev/null 2>&1 || true

echo "✅ Docker cleanup completed!"
echo ""
echo "You can now run Docker deployments without --remove-orphans:"
echo "   docker-compose up -d"
echo "   docker-compose -f docker-compose.ssl.yml up -d"
echo ""

# Optional: Show remaining containers
if docker ps -q --filter "name=arrowtuner" | grep -q .; then
    echo "⚠️  Still running ArrowTuner containers:"
    docker ps --filter "name=arrowtuner"
else
    echo "✅ No ArrowTuner containers currently running"
fi