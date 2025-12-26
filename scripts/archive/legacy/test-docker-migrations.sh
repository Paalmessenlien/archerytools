#!/bin/bash
#
# Test Docker Migration System
# Run this on your production server to test the Docker migration integration
#

set -e

echo "🧪 Testing Docker Migration System"
echo "================================="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found on this system"
    exit 1
fi

echo "✅ Docker found"

# Check if containers are running
if ! docker ps &> /dev/null; then
    echo "❌ Cannot access Docker daemon"
    echo "   Make sure Docker is running and you have permissions"
    exit 1
fi

echo "✅ Docker daemon accessible"

# List running containers
echo ""
echo "📋 Running containers:"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

echo ""
echo "🔍 Looking for API containers..."

# Find API container using the same logic as docker-migration-runner.sh
containers=$(docker ps --format "{{.Names}}" 2>/dev/null || echo "")

if [ -z "$containers" ]; then
    echo "❌ No running containers found!"
    echo "   Start your containers with: ./start-unified.sh ssl yourdomain.com"
    exit 1
fi

echo "✅ Found running containers"

# Look for API container patterns
api_container=""
for pattern in "api" "arrowtuner" "archery"; do
    for container in $containers; do
        if echo "$container" | grep -i "$pattern" > /dev/null; then
            api_container="$container"
            break 2
        fi
    done
done

if [ -z "$api_container" ]; then
    # Use first container as fallback
    api_container=$(echo "$containers" | head -1)
    echo "⚠️  No API-specific container found, using: $api_container"
else
    echo "✅ Found API container: $api_container"
fi

echo ""
echo "🔍 Testing container database access..."

# Check if databases exist in container
docker exec "$api_container" ls -la /app/databases/ 2>/dev/null || {
    echo "❌ Cannot access /app/databases/ in container"
    echo "   Container may not be properly configured"
    exit 1
}

echo "✅ Container database directory accessible"

echo ""
echo "🧪 Testing migration runner..."

# Test docker migration runner
if [ -f "./docker-migration-runner.sh" ]; then
    echo "✅ docker-migration-runner.sh found"
    
    echo ""
    echo "📊 Checking migration status in container..."
    if ./docker-migration-runner.sh status; then
        echo ""
        echo "✅ Migration status check successful"
        
        echo ""
        echo "🎯 You can now run migrations in production with:"
        echo "   ./docker-migration-runner.sh migrate"
        echo ""
        echo "🚀 Or restart your production system to run migrations automatically:"
        echo "   ./start-unified.sh ssl yourdomain.com"
        
    else
        echo "❌ Migration status check failed"
        echo "   Check container logs: docker logs $api_container"
        exit 1
    fi
else
    echo "❌ docker-migration-runner.sh not found"
    echo "   Make sure you're in the project root directory"
    exit 1
fi

echo ""
echo "✅ Docker migration system test completed successfully!"
echo "🎉 Your production spine chart system should work after running migrations"