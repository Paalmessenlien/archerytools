#!/bin/bash

echo "🔄 Restarting ArrowTuner with updated CORS and nginx configuration..."

# Stop current services
echo "⏹️  Stopping current services..."
docker-compose -f docker-compose.unified.yml --profile with-nginx down

# Remove any old nginx containers that might be causing conflicts
echo "🧹 Cleaning up old nginx containers..."
docker container prune -f

# Start services again
echo "🚀 Starting services with updated configuration..."
docker-compose -f docker-compose.unified.yml --profile with-nginx up -d --build

# Wait a moment for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check status
echo "📊 Service status:"
docker-compose -f docker-compose.unified.yml ps

echo ""
echo "🌐 Testing connectivity..."
echo "Nginx health: $(curl -s -o /dev/null -w '%{http_code}' http://localhost/health || echo 'FAILED')"
echo "API health: $(curl -s -o /dev/null -w '%{http_code}' http://localhost/api/health || echo 'FAILED')" 
echo "Frontend: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 || echo 'FAILED')"

echo ""
echo "✅ Restart complete!"
echo "🌐 Access the application at: http://localhost:3000"
echo "📊 API documentation at: http://localhost/api/health"
echo ""
echo "If you still have issues with Google login, try:"
echo "1. Clear browser cache and cookies"
echo "2. Check browser console for any remaining CORS errors"
echo "3. Check logs: docker-compose -f docker-compose.unified.yml logs -f nginx"