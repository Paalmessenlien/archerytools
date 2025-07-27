#!/bin/bash

# ArrowTuner Docker Deployment Script
# Automatically handles cleanup and deployment without orphan container issues

set -e

# Configuration
COMPOSE_FILE="${1:-docker-compose.yml}"
BUILD_FLAG="${2:-}"

echo "🚀 ArrowTuner Docker Deployment"
echo "==============================="
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

# Run cleanup first to avoid orphan containers
echo "🧹 Running Docker cleanup to avoid orphan containers..."
./docker-cleanup.sh

echo ""
echo "📦 Deploying with $COMPOSE_FILE..."

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

echo ""
echo "✅ Deployment completed!"
echo ""
echo "🌐 Access URLs (if using default ports):"
echo "   Frontend: http://localhost:3000"
echo "   API:      http://localhost:5000"
echo ""
echo "📋 Useful commands:"
echo "   View logs:    docker-compose -f $COMPOSE_FILE logs -f"
echo "   Stop:         docker-compose -f $COMPOSE_FILE down"
echo "   Restart:      docker-compose -f $COMPOSE_FILE restart"
echo "   Cleanup:      ./docker-cleanup.sh"