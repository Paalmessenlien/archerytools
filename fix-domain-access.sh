#\!/bin/bash

echo "🔧 Domain Access Fix"
echo "==================="
echo ""

echo "Your server IP: 79.160.142.222"
echo "Domain: archerytool.online"
echo ""

echo "🎯 Step 1: Test direct IP access"
echo "Frontend: http://79.160.142.222:3000"
echo "API: http://79.160.142.222:5000/api/health"
echo ""

echo "🎯 Step 2: Set up nginx reverse proxy for domain access"
echo "sudo docker-compose down"
echo "sudo docker-compose up -d --build"
echo ""

echo "🎯 Step 3: Configure DNS (do this in your domain registrar)"
echo "Add A record:"
echo "  Type: A"
echo "  Name: @ (or archerytool.online)"
echo "  Value: 79.160.142.222"
echo "  TTL: 300"
echo ""

echo "🎯 Step 4: Set up SSL (after DNS is working)"
echo "sudo docker-compose -f docker-compose.ssl.yml up -d --build"
echo ""

echo "💡 Testing current setup:"
echo "Checking if frontend container is actually running..."
sudo docker ps | grep frontend || echo "Frontend container not running"

echo ""
echo "Checking if nginx container exists..."
sudo docker ps | grep nginx || echo "Nginx container not running"

echo ""
echo "Current docker-compose.prod.yml only exposes ports directly"
echo "For domain access, you need the main docker-compose.yml with nginx"
