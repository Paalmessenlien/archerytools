#\!/bin/bash

echo "🔧 Docker Container Issue Fixer"
echo "================================"

echo "🧹 Step 1: Clean up any orphaned containers..."
docker system prune -f || echo "⚠️  Need sudo for Docker commands"

echo "🗑️  Step 2: Remove any conflicting arrowtuner containers..."
docker rm -f $(docker ps -aq --filter "name=arrowtuner") 2>/dev/null || echo "No containers to remove"

echo "🏗️  Step 3: Remove any conflicting images..."
docker rmi -f $(docker images -q --filter "reference=*arrowtuner*") 2>/dev/null || echo "No images to remove"

echo "🎯 Step 4: Test simple API deployment..."
docker-compose -f docker-compose.simple.yml up -d --build

echo "⏳ Waiting for API to start..."
sleep 10

echo "🩺 Step 5: Test health endpoint..."
curl -f http://localhost:5000/api/health && echo "✅ API is healthy\!" || echo "❌ API health check failed"

echo ""
echo "📋 To view logs: docker-compose -f docker-compose.simple.yml logs -f"
echo "🛑 To stop: docker-compose -f docker-compose.simple.yml down"
