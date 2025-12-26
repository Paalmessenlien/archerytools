#\!/bin/bash

echo "🔒 Enable HTTPS for ArrowTuner"
echo "=============================="
echo ""

# Check if Let's Encrypt certificates exist
CERT_DIR="/etc/letsencrypt/live/archerytool.online"

if [ -d "$CERT_DIR" ]; then
    echo "✅ Found existing Let's Encrypt certificates in $CERT_DIR"
    
    echo ""
    echo "🔧 Step 1: Copying certificates to deploy/ssl/..."
    
    # Copy certificates
    sudo cp "$CERT_DIR/fullchain.pem" ./deploy/ssl/ 2>/dev/null || echo "   ⚠️  Could not copy fullchain.pem (may need sudo)"
    sudo cp "$CERT_DIR/privkey.pem" ./deploy/ssl/ 2>/dev/null || echo "   ⚠️  Could not copy privkey.pem (may need sudo)"
    sudo cp "$CERT_DIR/chain.pem" ./deploy/ssl/ 2>/dev/null || echo "   ⚠️  Could not copy chain.pem (may need sudo)"
    
    # Set proper ownership
    sudo chown $USER:$USER ./deploy/ssl/*.pem 2>/dev/null || echo "   ⚠️  Could not change ownership (may need sudo)"
    
    echo "   ✅ Certificates copied to deploy/ssl/"
    
else
    echo "❌ Let's Encrypt certificates not found in $CERT_DIR"
    echo ""
    echo "🎯 To create new certificates, run:"
    echo "sudo certbot certonly --standalone \\"
    echo "  -d archerytool.online \\"
    echo "  -d www.archerytool.online \\"
    echo "  --email admin@archerytool.online \\"
    echo "  --agree-tos"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo ""
echo "📋 Step 2: Checking certificate files..."
if [ -f "./deploy/ssl/fullchain.pem" ] && [ -f "./deploy/ssl/privkey.pem" ]; then
    echo "   ✅ Certificate files are ready:"
    ls -la ./deploy/ssl/*.pem
else
    echo "   ❌ Certificate files missing. Manual copy required:"
    echo "   sudo cp /etc/letsencrypt/live/archerytool.online/*.pem ./deploy/ssl/"
    echo "   sudo chown $USER:$USER ./deploy/ssl/*.pem"
    exit 1
fi

echo ""
echo "🚀 Step 3: Deploying with HTTPS..."

# Stop current deployment
echo "   Stopping current deployment..."
sudo docker-compose down

# Deploy with SSL configuration
echo "   Starting HTTPS deployment..."
sudo docker-compose -f docker-compose.ssl.yml up -d --build

echo ""
echo "⏳ Step 4: Waiting for services to start..."
sleep 15

echo ""
echo "🩺 Step 5: Testing HTTPS..."

echo "   HTTP (should redirect to HTTPS):"
curl -s -I http://archerytool.online | head -n 3 || echo "   ❌ HTTP test failed"

echo ""
echo "   HTTPS:"
curl -s -I https://archerytool.online | head -n 3 || echo "   ❌ HTTPS test failed"

echo ""
echo "📊 Step 6: Container status..."
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🌐 Access URLs:"
echo "   🔓 HTTP: http://archerytool.online (should redirect)"
echo "   🔒 HTTPS: https://archerytool.online"
echo "   📱 Direct: https://79.160.142.222"

echo ""
echo "🎯 Next steps:"
echo "   1. Test HTTPS access: https://archerytool.online"
echo "   2. Set up auto-renewal: sudo crontab -e"
echo "      Add: 0 12 * * * /usr/bin/certbot renew --quiet --post-hook \"docker-compose restart nginx\""
