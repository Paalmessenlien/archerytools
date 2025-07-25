#!/bin/bash
# Arrow Tuning Platform - Production Deployment Script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$DEPLOY_DIR")"
APP_DIR="/opt/arrowtuner"
APP_USER="arrowtuner"
SERVICE_NAME="arrowtuner"

# Logging
LOG_FILE="/var/log/arrowtuner-deploy.log"
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root (use sudo)"
fi

# Check if server is ready
if [[ ! -f "$APP_DIR/.server-ready" ]]; then
    error "Server not ready. Run server-setup.sh first"
fi

log "Starting Arrow Tuning Platform deployment..."

# Load environment configuration
if [[ -f "$DEPLOY_DIR/config/production.env" ]]; then
    log "Loading production environment configuration..."
    set -a
    source "$DEPLOY_DIR/config/production.env"
    set +a
else
    error "Production environment file not found: $DEPLOY_DIR/config/production.env"
fi

# Validate required environment variables
required_vars=("SECRET_KEY" "DEEPSEEK_API_KEY" "DOMAIN_NAME")
for var in "${required_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        error "Required environment variable $var is not set"
    fi
done

# Stop existing services
log "Stopping existing services..."
supervisorctl stop $SERVICE_NAME 2>/dev/null || true

# Backup existing installation
if [[ -d "$APP_DIR/app" ]]; then
    log "Backing up existing installation..."
    backup_dir="$APP_DIR/backups/app-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    cp -r "$APP_DIR/app" "$backup_dir/" || warn "Failed to backup existing installation"
fi

# Create application structure
log "Setting up application structure..."
mkdir -p "$APP_DIR"/{app,data,logs,backups,static}

# Copy application files
log "Copying application files..."
cp -r "$PROJECT_DIR/arrow_scraper/." "$APP_DIR/app/"
cp -r "$PROJECT_DIR/crawl4ai" "$APP_DIR/"

# Copy static files
if [[ -d "$PROJECT_DIR/arrow_scraper/static" ]]; then
    cp -r "$PROJECT_DIR/arrow_scraper/static/." "$APP_DIR/static/"
fi

# Set permissions
chown -R $APP_USER:$APP_USER "$APP_DIR"
chmod -R 755 "$APP_DIR"
chmod 750 "$APP_DIR/data"
chmod 750 "$APP_DIR/logs"
chmod 750 "$APP_DIR/backups"

# Create production configuration
log "Setting up production configuration..."
cat > "$APP_DIR/app/config_production.py" << 'EOF'
import os
import sys
sys.path.insert(0, '/opt/arrowtuner/deploy/config')
from production import ProductionConfig as Config
EOF

# Install Python dependencies
log "Installing Python dependencies..."
sudo -u $APP_USER python3 -m venv "$APP_DIR/venv"
sudo -u $APP_USER "$APP_DIR/venv/bin/pip" install --upgrade pip setuptools wheel

# Install from requirements
if [[ -f "$APP_DIR/app/requirements.txt" ]]; then
    sudo -u $APP_USER "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/app/requirements.txt"
fi

# Install additional production packages
sudo -u $APP_USER "$APP_DIR/venv/bin/pip" install gunicorn flask-limiter

# Create production WSGI application
log "Creating production WSGI application..."
cat > "$APP_DIR/app/wsgi.py" << 'EOF'
#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add application directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')

# Import the Flask application
from webapp import app

if __name__ == "__main__":
    app.run()
EOF

chmod +x "$APP_DIR/app/wsgi.py"

# Initialize database
log "Initializing database..."
sudo -u $APP_USER "$APP_DIR/venv/bin/python" "$APP_DIR/app/arrow_database.py" || warn "Database initialization failed"

# Copy database if it exists
if [[ -f "$PROJECT_DIR/arrow_scraper/arrow_database.db" ]]; then
    cp "$PROJECT_DIR/arrow_scraper/arrow_database.db" "$APP_DIR/data/"
    chown $APP_USER:$APP_USER "$APP_DIR/data/arrow_database.db"
fi

# Create environment file for application
log "Creating application environment file..."
cat > "$APP_DIR/.env" << EOF
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
DATABASE_PATH=$APP_DIR/data/arrow_database.db
DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY
LOG_PATH=$APP_DIR/logs
BACKUP_PATH=$APP_DIR/backups
EOF

chown $APP_USER:$APP_USER "$APP_DIR/.env"
chmod 600 "$APP_DIR/.env"

# Configure supervisor
log "Configuring supervisor service..."
cat > "/etc/supervisor/conf.d/$SERVICE_NAME.conf" << EOF
[program:$SERVICE_NAME]
command=$APP_DIR/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --worker-class sync --worker-connections 1000 --max-requests 1000 --max-requests-jitter 100 --timeout 30 --keep-alive 5 --preload wsgi:app
directory=$APP_DIR/app
user=$APP_USER
group=$APP_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$APP_DIR/logs/gunicorn.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=5
environment=PATH="$APP_DIR/venv/bin"
EOF

# Configure nginx
log "Configuring nginx..."
# Update domain name in nginx config
sed "s/yourdomain.com/$DOMAIN_NAME/g" "$DEPLOY_DIR/nginx/arrowtuner.conf" > "/etc/nginx/sites-available/$SERVICE_NAME"

# Remove setup configuration and enable application
rm -f /etc/nginx/sites-enabled/setup
ln -sf "/etc/nginx/sites-available/$SERVICE_NAME" "/etc/nginx/sites-enabled/$SERVICE_NAME"

# Test nginx configuration
nginx -t || error "Nginx configuration test failed"

# Update supervisor and start services
log "Starting services..."
supervisorctl reread
supervisorctl update
supervisorctl start $SERVICE_NAME

# Restart nginx
systemctl restart nginx

# Set up SSL certificate with Let's Encrypt
if [[ -n "${SSL_EMAIL:-}" ]] && [[ -n "${DOMAIN_NAME:-}" ]]; then
    log "Setting up SSL certificate..."
    certbot --nginx -d "$DOMAIN_NAME" -d "www.$DOMAIN_NAME" --email "$SSL_EMAIL" --agree-tos --non-interactive --redirect || warn "SSL setup failed"
fi

# Create health check script
cat > "$APP_DIR/health-check.sh" << 'EOF'
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
if [[ $response -eq 200 ]]; then
    echo "OK"
    exit 0
else
    echo "FAIL: HTTP $response"
    exit 1
fi
EOF

chmod +x "$APP_DIR/health-check.sh"
chown $APP_USER:$APP_USER "$APP_DIR/health-check.sh"

# Wait for application to start
log "Waiting for application to start..."
sleep 10

# Test deployment
log "Testing deployment..."
if curl -s http://localhost:5000/health > /dev/null; then
    log "✓ Local health check passed"
else
    error "✗ Local health check failed"
fi

# Create deployment info file
cat > "$APP_DIR/deployment-info.txt" << EOF
Arrow Tuning Platform Deployment Information
==========================================

Deployment Date: $(date)
Version: Production
Domain: $DOMAIN_NAME
Application Directory: $APP_DIR
Service User: $APP_USER
Python Environment: $APP_DIR/venv

Services:
- Gunicorn: supervisorctl status $SERVICE_NAME
- Nginx: systemctl status nginx
- Database: $APP_DIR/data/arrow_database.db

Logs:
- Application: $APP_DIR/logs/
- Nginx: /var/log/nginx/
- Supervisor: /var/log/supervisor/

Management Commands:
- Restart application: supervisorctl restart $SERVICE_NAME
- Check status: supervisorctl status $SERVICE_NAME
- View logs: tail -f $APP_DIR/logs/gunicorn.log
- Health check: $APP_DIR/health-check.sh

EOF

log "Deployment completed successfully!"
log "Application should be available at: https://$DOMAIN_NAME"
log "Health check: curl https://$DOMAIN_NAME/health"
log "View logs: tail -f $APP_DIR/logs/gunicorn.log"
log "Service status: supervisorctl status $SERVICE_NAME"