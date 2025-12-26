#\!/bin/bash

echo "🔒 Fix Mixed Content Error for HTTPS"
echo "===================================="
echo ""

echo "Issue: Frontend making HTTP API calls from HTTPS site"
echo "Solution: Update frontend to use HTTPS API URLs"
echo ""

echo "🔧 Rebuilding containers with HTTPS API configuration..."

# Stop current containers
sudo docker-compose -f docker-compose.ssl.yml down

# Rebuild with updated configuration
sudo docker-compose -f docker-compose.ssl.yml up -d --build

echo ""
echo "⏳ Waiting for services to restart..."
sleep 15

echo ""
echo "🩺 Testing HTTPS endpoints..."

echo "Frontend:"
curl -s -I https://archerytool.online | head -n 2

echo ""
echo "API:"
curl -s -I https://archerytool.online/api/health | head -n 2

echo ""
echo "📊 Container status:"
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ Mixed content issue should now be resolved\!"
echo "   Frontend will use: https://archerytool.online/api"
echo "   Instead of: http://api:5000/api"
