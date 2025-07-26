#\!/bin/bash

echo "🌐 Domain Access Diagnostic"
echo "=========================="
echo ""

echo "1. Checking DNS resolution:"
echo "archerytool.online resolves to:"
nslookup archerytool.online | grep -A 1 "Name:" || echo "DNS resolution failed"
echo ""

echo "2. Checking if we're on the right server:"
echo "External IP of this server:"
curl -s ifconfig.me || echo "Could not get external IP"
echo ""

echo "3. Checking Docker containers:"
if command -v docker >/dev/null 2>&1; then
    echo "Running containers:"
    sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Need sudo for docker commands"
else
    echo "Docker not available"
fi
echo ""

echo "4. Checking open ports:"
echo "Port 80 (HTTP):"
netstat -tlnp | grep ":80 " || echo "Port 80 not listening"
echo "Port 443 (HTTPS):"
netstat -tlnp | grep ":443 " || echo "Port 443 not listening"
echo "Port 3000 (Frontend):"
netstat -tlnp | grep ":3000 " || echo "Port 3000 not listening"
echo "Port 5000 (API):"
netstat -tlnp | grep ":5000 " || echo "Port 5000 not listening"
echo ""

echo "5. Checking firewall:"
if command -v ufw >/dev/null 2>&1; then
    echo "UFW status:"
    sudo ufw status
else
    echo "UFW not available"
fi
echo ""

echo "6. Testing local access:"
echo "Local HTTP (port 80):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:80 2>/dev/null || echo "Connection failed"
echo "Local Frontend (port 3000):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "Connection failed"
echo "Local API (port 5000):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health 2>/dev/null || echo "Connection failed"
echo ""

echo "7. Current Docker Compose setup:"
if [ -f "docker-compose.prod.yml" ]; then
    echo "Using production compose file:"
    grep -A 3 "ports:" docker-compose.prod.yml || echo "No ports section found"
else
    echo "No docker-compose.prod.yml found"
fi
echo ""

echo "💡 Next steps based on results:"
echo "- If containers aren't running: docker-compose -f docker-compose.prod.yml up -d"
echo "- If DNS doesn't point here: Update A record to point to this server's IP"
echo "- If ports not open: Check firewall and nginx configuration"
echo "- If nginx not running: Need to set up reverse proxy for domain access"
