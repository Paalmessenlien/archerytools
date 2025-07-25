#!/bin/bash
#
# ArrowTuner Production Deployment Script
# Deploys the application to Ubuntu server
#
# Usage: ./deploy.sh [domain_name] [ssl_email]
# Example: ./deploy.sh arrowtuner.com admin@arrowtuner.com
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
DOMAIN_NAME=${1:-"localhost"}
SSL_EMAIL=${2:-"admin@example.com"}
APP_DIR="/var/www/arrowtuner"
APP_USER="arrowtuner"
BACKUP_DIR="/opt/arrowtuner/backups"

print_status "Starting ArrowTuner deployment..."
print_status "Domain: $DOMAIN_NAME"
print_status "SSL Email: $SSL_EMAIL"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Create backup of existing installation
if [ -d "$APP_DIR" ]; then
    print_status "Creating backup of existing installation..."
    BACKUP_FILE="arrowtuner_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    cd /var/www
    tar -czf "$BACKUP_DIR/$BACKUP_FILE" arrowtuner/ 2>/dev/null || true
    print_success "Backup created: $BACKUP_FILE"
fi

# Ensure application directory exists
mkdir -p "$APP_DIR"
chown -R $APP_USER:$APP_USER "$APP_DIR"

# Deploy application code (assuming code is in current directory)
print_status "Deploying application code..."
if [ -f "package.json" ] || [ -f "requirements.txt" ]; then
    # Copy application files
    rsync -av --exclude-from='.gitignore' \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='venv' \
        --exclude='*.log' \
        . "$APP_DIR/"
    
    chown -R $APP_USER:$APP_USER "$APP_DIR"
    print_success "Application code deployed"
else
    print_error "No application code found in current directory"
    print_error "Please run this script from the ArrowTuner root directory"
    exit 1
fi

# Setup Python backend
print_status "Setting up Python backend..."
cd "$APP_DIR/arrow_scraper"

# Create virtual environment
sudo -u $APP_USER python3.9 -m venv ../venv
sudo -u $APP_USER ../venv/bin/pip install --upgrade pip
sudo -u $APP_USER ../venv/bin/pip install -r requirements.txt

# Initialize database if it doesn't exist
if [ ! -f "arrow_database.db" ]; then
    print_status "Initializing database..."
    sudo -u $APP_USER ../venv/bin/python arrow_database.py
    print_success "Database initialized"
fi

# Setup frontend
print_status "Setting up frontend..."
cd "$APP_DIR/frontend"

# Install dependencies
sudo -u $APP_USER npm ci --production

# Build for production
sudo -u $APP_USER npm run build

# Create environment files
print_status "Creating environment configuration..."

# Backend environment
cat > "$APP_DIR/arrow_scraper/.env" << EOF
SECRET_KEY=$(openssl rand -base64 32)
DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY:-"your-deepseek-api-key-here"}
FLASK_ENV=production
API_PORT=5000
EOF

# Frontend environment  
cat > "$APP_DIR/frontend/.env" << EOF
API_BASE_URL=http://localhost:5000/api
NODE_ENV=production
EOF

# Set proper permissions
chown $APP_USER:$APP_USER "$APP_DIR/arrow_scraper/.env"
chown $APP_USER:$APP_USER "$APP_DIR/frontend/.env"
chmod 600 "$APP_DIR/arrow_scraper/.env"
chmod 600 "$APP_DIR/frontend/.env"

# Configure Nginx
print_status "Configuring Nginx..."
cat > /etc/nginx/sites-available/arrowtuner << EOF
# ArrowTuner Production Configuration

# Rate limiting
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=general:10m rate=30r/s;

# Upstream for API
upstream arrowtuner_api {
    server 127.0.0.1:5000;
    keepalive 32;
}

# Upstream for frontend
upstream arrowtuner_frontend {
    server 127.0.0.1:3000;
    keepalive 32;
}

server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # API routes
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://arrowtuner_api/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # CORS headers
        add_header Access-Control-Allow-Origin "https://$DOMAIN_NAME" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization" always;
        
        if (\$request_method = 'OPTIONS') {
            return 200;
        }
    }
    
    # Frontend routes
    location / {
        limit_req zone=general burst=50 nodelay;
        
        proxy_pass http://arrowtuner_frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Test Nginx configuration
nginx -t

# Setup PM2 for frontend
print_status "Setting up PM2 for frontend..."
sudo -u $APP_USER pm2 delete arrowtuner-frontend 2>/dev/null || true

cat > "$APP_DIR/ecosystem.config.js" << EOF
module.exports = {
  apps: [{
    name: 'arrowtuner-frontend',
    cwd: '$APP_DIR/frontend',
    script: 'npm',
    args: 'start',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    instances: 2,
    exec_mode: 'cluster',
    watch: false,
    max_memory_restart: '500M',
    error_file: '/var/log/arrowtuner/frontend-error.log',
    out_file: '/var/log/arrowtuner/frontend-out.log',
    log_file: '/var/log/arrowtuner/frontend.log',
    time: true
  }]
};
EOF

chown $APP_USER:$APP_USER "$APP_DIR/ecosystem.config.js"

# Start PM2 as app user
sudo -u $APP_USER pm2 start "$APP_DIR/ecosystem.config.js"
sudo -u $APP_USER pm2 save
sudo -u $APP_USER pm2 startup systemd -u $APP_USER --hp /home/$APP_USER

# Start/restart services
print_status "Starting services..."
systemctl daemon-reload
systemctl enable arrowtuner-api
systemctl restart arrowtuner-api
systemctl reload nginx

# Wait for services to start
sleep 5

# Health check
print_status "Performing health checks..."
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health || echo "000")
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "000")

if [ "$API_STATUS" = "200" ]; then
    print_success "API service is healthy"
else
    print_error "API service health check failed (HTTP $API_STATUS)"
fi

if [ "$FRONTEND_STATUS" = "200" ]; then
    print_success "Frontend service is healthy"
else
    print_error "Frontend service health check failed (HTTP $FRONTEND_STATUS)"
fi

# Setup SSL if domain is not localhost
if [ "$DOMAIN_NAME" != "localhost" ] && [ "$DOMAIN_NAME" != "127.0.0.1" ]; then
    print_status "Setting up SSL certificate..."
    
    # Get SSL certificate
    certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME \
        --non-interactive \
        --agree-tos \
        --email $SSL_EMAIL \
        --redirect
    
    if [ $? -eq 0 ]; then
        print_success "SSL certificate obtained and configured"
    else
        print_warning "SSL certificate setup failed - continuing without SSL"
    fi
    
    # Setup auto-renewal
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
fi

# Create status script
cat > /opt/arrowtuner/status.sh << 'EOF'
#!/bin/bash
#
# ArrowTuner Status Check
#

echo "=== ArrowTuner System Status ==="
echo

echo "Services:"
systemctl is-active arrowtuner-api && echo "✓ API Service: Running" || echo "✗ API Service: Stopped"
systemctl is-active nginx && echo "✓ Nginx: Running" || echo "✗ Nginx: Stopped"
sudo -u arrowtuner pm2 describe arrowtuner-frontend > /dev/null 2>&1 && echo "✓ Frontend: Running" || echo "✗ Frontend: Stopped"

echo
echo "Health Checks:"
curl -s http://localhost:5000/api/health > /dev/null && echo "✓ API Health: OK" || echo "✗ API Health: Failed"
curl -s http://localhost:3000 > /dev/null && echo "✓ Frontend Health: OK" || echo "✗ Frontend Health: Failed"

echo
echo "System Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{printf "%s", $5}')"

echo
echo "Recent Logs:"
echo "API Logs (last 5 lines):"
journalctl -u arrowtuner-api --no-pager -n 5 --since "1 hour ago"

echo
echo "Frontend Logs (last 5 lines):"
sudo -u arrowtuner pm2 logs arrowtuner-frontend --lines 5 --nostream 2>/dev/null || echo "No frontend logs available"
EOF

chmod +x /opt/arrowtuner/status.sh

# Final status report
print_success "Deployment completed successfully!"
print_status ""
print_status "=== Deployment Summary ==="
print_status "Domain: $DOMAIN_NAME"
print_status "Application Directory: $APP_DIR"
print_status "API Service: arrowtuner-api.service"
print_status "Frontend Process: PM2 (arrowtuner-frontend)"
print_status "Web Server: Nginx"
print_status ""
print_status "URLs:"
if [ "$DOMAIN_NAME" != "localhost" ]; then
    print_status "- Frontend: https://$DOMAIN_NAME"
    print_status "- API: https://$DOMAIN_NAME/api/"
    print_status "- Health: https://$DOMAIN_NAME/health"
else
    print_status "- Frontend: http://localhost"
    print_status "- API: http://localhost/api/"
    print_status "- Health: http://localhost/health"
fi
print_status ""
print_status "Management Commands:"
print_status "- Status: /opt/arrowtuner/status.sh"
print_status "- Health Check: /opt/arrowtuner/health-check.sh"
print_status "- Backup: /opt/arrowtuner/backup.sh"
print_status "- View API Logs: journalctl -u arrowtuner-api -f"
print_status "- View Frontend Logs: sudo -u arrowtuner pm2 logs arrowtuner-frontend"
print_status ""
print_warning "Important:"
print_warning "- Update environment variables in $APP_DIR/arrow_scraper/.env"
print_warning "- Set your DEEPSEEK_API_KEY for arrow scraping functionality"
print_warning "- Monitor logs and system resources"
print_warning "- Regular backups are scheduled daily at 2 AM"
print_status ""
print_success "ArrowTuner is now deployed and ready for production use!"

# Run status check
/opt/arrowtuner/status.sh