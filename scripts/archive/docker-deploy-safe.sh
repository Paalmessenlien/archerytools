#!/bin/bash

# ArrowTuner Safe Docker Deployment Script
# Preserves user data volumes during rebuilds

set -e

# Configuration
COMPOSE_FILE="${1:-docker-compose.yml}"
BUILD_FLAG="${2:-}"

echo "🚀 ArrowTuner Safe Docker Deployment"
echo "====================================="
echo "Compose file: $COMPOSE_FILE"
echo ""

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ Docker compose file '$COMPOSE_FILE' not found"
    echo ""
    echo "Available compose files:"
    ls -1 docker-compose*.yml 2>/dev/null || echo "  No compose files found"
    echo ""
    echo "Usage: $0 [compose-file] [--build]"
    echo "  Example: $0 docker-compose.ssl.yml --build"
    exit 1
fi

# List existing volumes before deployment
echo "📦 Existing volumes (will be preserved):"
docker volume ls | grep arrowtuner || echo "  No ArrowTuner volumes found"
echo ""

# Stop containers but preserve volumes
echo "🛑 Stopping existing containers (preserving volumes)..."
docker-compose -f "$COMPOSE_FILE" down --remove-orphans

# Build if requested
if [ "$BUILD_FLAG" = "--build" ]; then
    echo "🔨 Building containers..."
    docker-compose -f "$COMPOSE_FILE" build
fi

# Deploy
echo "🚀 Starting containers..."
docker-compose -f "$COMPOSE_FILE" up -d

# Wait a moment for containers to start
sleep 5

# Show status
echo ""
echo "📊 Deployment Status:"
docker-compose -f "$COMPOSE_FILE" ps

# Show logs if any containers failed
if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Exit"; then
    echo ""
    echo "⚠️  Some containers failed to start. Showing logs:"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20
fi

# Verify volumes are intact
echo ""
echo "✅ Volumes after deployment:"
docker volume ls | grep arrowtuner

echo ""
echo "✅ Safe deployment completed!"
echo ""
echo "🌐 Access URLs (if using default ports):"
echo "   Frontend: http://localhost:3000"
echo "   API:      http://localhost:5000"
echo ""
echo "📋 Useful commands:"
echo "   View logs:    docker-compose -f $COMPOSE_FILE logs -f"
echo "   Stop:         docker-compose -f $COMPOSE_FILE down"
echo "   Restart:      docker-compose -f $COMPOSE_FILE restart"
echo "   Backup data:  docker run --rm -v arrowtuner-userdata:/data alpine tar czf - -C /data . > userdata-backup.tar.gz"