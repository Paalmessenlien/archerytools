#\!/bin/bash

echo "🌐 Container Network Test"
echo "========================"
echo ""

echo "1. Testing API health from host:"
curl -s http://localhost:5000/api/health | python -m json.tool 2>/dev/null && echo "✅ API accessible from host" || echo "❌ API not accessible from host"
echo ""

echo "2. Testing frontend from host:"
curl -s http://localhost:3000 >/dev/null && echo "✅ Frontend accessible from host" || echo "❌ Frontend not accessible from host"
echo ""

echo "3. Checking Docker containers:"
echo "API container:"
docker ps --filter "name=arrowtuner-api" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Need sudo for docker commands"
echo ""
echo "Frontend container:"
docker ps --filter "name=arrowtuner-frontend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Need sudo for docker commands"
echo ""

echo "4. Testing container-to-container connectivity:"
echo "Checking if frontend can reach API service..."
docker exec arrowtuner-frontend curl -s http://api:5000/api/health 2>/dev/null && echo "✅ Frontend can reach API" || echo "❌ Frontend cannot reach API"
echo ""

echo "💡 If frontend cannot reach API, restart with updated environment:"
echo "docker-compose -f docker-compose.prod.yml down"
echo "docker-compose -f docker-compose.prod.yml up -d --build"
