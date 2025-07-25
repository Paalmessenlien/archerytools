#!/bin/bash
# Arrow Tuning Platform - Ubuntu Server Setup Script
# Run as root on fresh Ubuntu 20.04+ server

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging
LOG_FILE="/var/log/arrowtuner-setup.log"
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

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root (use sudo)"
fi

log "Starting Arrow Tuning Platform server setup..."

# Update system
log "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
log "Installing required packages..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    nginx \
    supervisor \
    ufw \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    wget \
    unzip \
    sqlite3 \
    logrotate \
    htop \
    fail2ban

# Create application user
log "Creating application user..."
if ! id "arrowtuner" &>/dev/null; then
    useradd -r -m -s /bin/bash arrowtuner
    usermod -aG www-data arrowtuner
fi

# Create application directories
log "Creating application directories..."
mkdir -p /opt/arrowtuner/{app,data,logs,backups,static}
chown -R arrowtuner:arrowtuner /opt/arrowtuner

# Install Python dependencies system-wide
log "Installing Python packages..."
pip3 install --upgrade pip setuptools wheel

# Configure firewall
log "Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Configure fail2ban for additional security
log "Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 1800
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/*error.log
findtime = 600
bantime = 7200
maxretry = 10
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# Configure logrotate for application logs
log "Configuring log rotation..."
cat > /etc/logrotate.d/arrowtuner << 'EOF'
/opt/arrowtuner/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 arrowtuner arrowtuner
    postrotate
        supervisorctl restart arrowtuner > /dev/null 2>&1 || true
    endscript
}
EOF

# Set up basic nginx configuration (will be replaced during deployment)
log "Setting up basic nginx configuration..."
rm -f /etc/nginx/sites-enabled/default

# Create basic health check page
mkdir -p /var/www/html
cat > /var/www/html/health << 'EOF'
Server ready for Arrow Tuning Platform deployment
EOF

# Configure basic nginx for setup
cat > /etc/nginx/sites-available/setup << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    root /var/www/html;
    index index.html;
    
    location /health {
        try_files /health =404;
    }
}
EOF

ln -sf /etc/nginx/sites-available/setup /etc/nginx/sites-enabled/setup
nginx -t && systemctl restart nginx

# Install Chrome for Crawl4AI (headless browsing)
log "Installing Chrome for web scraping..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt update
apt install -y google-chrome-stable

# Set up system limits for better performance
log "Configuring system limits..."
cat >> /etc/security/limits.conf << 'EOF'
arrowtuner soft nofile 65536
arrowtuner hard nofile 65536
arrowtuner soft nproc 4096
arrowtuner hard nproc 4096
EOF

# Configure sysctl for better network performance
cat >> /etc/sysctl.conf << 'EOF'
# Arrow Tuning Platform optimizations
net.core.somaxconn = 1024
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_syncookies = 1
net.ipv4.ip_local_port_range = 1024 65535
EOF

sysctl -p

# Create deployment ready marker
touch /opt/arrowtuner/.server-ready

log "Server setup completed successfully!"
log "Ready for Arrow Tuning Platform deployment"
log "Next steps:"
log "1. Update /deploy/config/production.env with your settings"
log "2. Run ./deploy.sh to deploy the application"
log "3. Configure your domain name and SSL certificate"

echo ""
log "Server information:"
log "- OS: $(lsb_release -d | cut -f2)"
log "- Python: $(python3 --version)"
log "- Nginx: $(nginx -v 2>&1)"
log "- Chrome: $(google-chrome --version)"
log "- Application user: arrowtuner"
log "- Application directory: /opt/arrowtuner"