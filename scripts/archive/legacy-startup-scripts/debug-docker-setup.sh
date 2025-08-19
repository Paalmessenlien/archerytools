#!/bin/bash

echo "🐳 Docker Container Status Debugging"
echo "======================================"

echo -e "\n1. Checking Docker containers..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n2. Checking service accessibility..."

echo -e "\n📡 Testing nginx proxy (port 80):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost/health || echo "❌ Nginx not accessible"

echo -e "\n🎯 Testing API directly (port 5000):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:5000/api/health || echo "❌ API not accessible"

echo -e "\n🖥️  Testing frontend directly (port 3000):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3000/ || echo "❌ Frontend not accessible"

echo -e "\n📋 Testing API through nginx proxy:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost/api/health || echo "❌ API through nginx not accessible"

echo -e "\n3. Checking container logs (last 10 lines)..."

echo -e "\n🔍 API container logs:"
docker logs arrowtuner-api --tail 10 2>/dev/null || echo "❌ Cannot get API logs"

echo -e "\n🔍 Frontend container logs:"
docker logs arrowtuner-frontend --tail 10 2>/dev/null || echo "❌ Cannot get frontend logs"

echo -e "\n🔍 Nginx container logs:"
docker logs arrowtuner-nginx --tail 10 2>/dev/null || echo "❌ Cannot get nginx logs"

echo -e "\n4. Network inspection..."
echo -e "\n🌐 Docker network details:"
docker network ls | grep arrowtuner || echo "❌ arrowtuner network not found"

echo -e "\n5. Container health status..."
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(arrowtuner-api|arrowtuner-frontend|arrowtuner-nginx)"

echo -e "\n6. Testing CORS headers..."
echo -e "\n🔧 CORS preflight test to API through nginx:"
curl -s -X OPTIONS -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: Content-Type,Authorization" -I http://localhost/api/auth/google 2>/dev/null | head -10 || echo "❌ CORS preflight failed"

echo -e "\n✅ Debug complete!"
echo -e "\n💡 Common fixes:"
echo "   - If nginx is not running: docker-compose up -d nginx"
echo "   - If API is not accessible: docker-compose restart api"
echo "   - If frontend has issues: docker-compose restart frontend"
echo "   - To rebuild containers: docker-compose up -d --build"