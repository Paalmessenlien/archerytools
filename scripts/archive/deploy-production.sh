#\!/bin/bash

echo "🚀 ArrowTuner Production Deployment"
echo "==================================="
echo ""

echo "🔧 Step 1: Preparing production environment..."

# Temporarily disable development overrides for production
if [ -f "docker-compose.override.yml" ]; then
    echo "   Temporarily disabling development overrides..."
    mv docker-compose.override.yml docker-compose.override.yml.disabled
    echo "   ✅ Development overrides disabled"
fi

echo ""
echo "🐳 Step 2: Deploying containers..."

# Stop any existing containers
echo "   Stopping existing containers..."
sudo docker-compose down 2>/dev/null || true

# Deploy with production configuration
echo "   Starting production deployment..."
sudo docker-compose up -d --build

echo ""
echo "⏳ Step 3: Waiting for services to start..."
sleep 10

echo ""
echo "🩺 Step 4: Health checks..."

echo "   API Health:"
curl -s http://localhost:5000/api/health | grep -o '"status":"healthy"' && echo "   ✅ API is healthy" || echo "   ❌ API health check failed"

echo "   Frontend Health:"
curl -s http://localhost:3000 >/dev/null && echo "   ✅ Frontend is accessible" || echo "   ❌ Frontend not accessible"

echo "   Nginx Health:"
curl -s http://localhost:80 >/dev/null && echo "   ✅ Nginx is running" || echo "   ❌ Nginx not accessible"

echo ""
echo "📋 Step 5: Container status..."
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🌐 Step 6: Access information..."
echo "   Local access:"
echo "   - Frontend: http://localhost:3000"
echo "   - API: http://localhost:5000/api/health" 
echo "   - Nginx: http://localhost"
echo ""
echo "   External access (after DNS configuration):"
echo "   - Domain: http://archerytool.online"
echo "   - Server IP: http://79.160.142.222"

echo ""
echo "🎯 Next steps:"
echo "   1. Configure DNS A record: archerytool.online -> 79.160.142.222"
echo "   2. Wait for DNS propagation (5-30 minutes)"
echo "   3. Test domain access: curl http://archerytool.online"
echo "   4. Set up SSL: sudo docker-compose -f docker-compose.ssl.yml up -d --build"

echo ""
echo "🔄 To restore development mode later:"
echo "   mv docker-compose.override.yml.disabled docker-compose.override.yml"
