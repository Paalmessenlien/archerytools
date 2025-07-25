#!/bin/bash
#
# ArrowTuner Production Server Setup Script
# Ubuntu 20.04+ Server Setup and Hardening
#
# Usage: sudo ./server-setup.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
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

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_status "Starting ArrowTuner Production Server Setup..."

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
apt install -y \
    curl \
    wget \
    git \
    unzip \
    htop \
    ufw \
    fail2ban \
    nginx \
    certbot \
    python3-certbot-nginx \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install Node.js 18+
print_status "Installing Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Install Python 3.9+
print_status "Installing Python 3.9..."
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.9 python3.9-pip python3.9-venv python3.9-dev

# Install PM2 for process management
print_status "Installing PM2..."
npm install -g pm2

# Install Docker (optional but recommended)
print_status "Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Create application user
print_status "Creating application user..."
if ! id "arrowtuner" &>/dev/null; then
    useradd -m -s /bin/bash arrowtuner
    usermod -aG docker arrowtuner
    print_success "Created user: arrowtuner"
else
    print_warning "User arrowtuner already exists"
fi

# Create application directories
print_status "Creating application directories..."
mkdir -p /var/www/arrowtuner
mkdir -p /var/log/arrowtuner
mkdir -p /etc/arrowtuner
mkdir -p /opt/arrowtuner/backups

# Set proper permissions
chown -R arrowtuner:arrowtuner /var/www/arrowtuner
chown -R arrowtuner:arrowtuner /var/log/arrowtuner
chown -R arrowtuner:arrowtuner /opt/arrowtuner

# Configure UFW firewall
print_status "Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Configure fail2ban
print_status "Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 3

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# Configure Nginx base
print_status "Configuring Nginx..."
# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Create Nginx configuration template
cat > /etc/nginx/sites-available/arrowtuner << 'EOF'
# ArrowTuner Nginx Configuration
# This will be customized during deployment

server {
    listen 80;
    server_name _;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;
    
    location / {
        return 200 "ArrowTuner server is ready for deployment";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/arrowtuner /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Create systemd service template
print_status "Creating systemd service template..."
cat > /etc/systemd/system/arrowtuner-api.service << EOF
[Unit]
Description=ArrowTuner API Server
After=network.target

[Service]
Type=simple
User=arrowtuner
Group=arrowtuner
WorkingDirectory=/var/www/arrowtuner/arrow_scraper
Environment=PATH=/var/www/arrowtuner/venv/bin
Environment=FLASK_ENV=production
ExecStart=/var/www/arrowtuner/venv/bin/python api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create logrotate configuration
print_status "Configuring log rotation..."
cat > /etc/logrotate.d/arrowtuner << EOF
/var/log/arrowtuner/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 arrowtuner arrowtuner
    postrotate
        systemctl reload arrowtuner-api
    endscript
}
EOF

# Create backup script
print_status "Creating backup script..."
cat > /opt/arrowtuner/backup.sh << 'EOF'
#!/bin/bash
#
# ArrowTuner Backup Script
#

BACKUP_DIR="/opt/arrowtuner/backups"
APP_DIR="/var/www/arrowtuner"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="arrowtuner_backup_${DATE}.tar.gz"

echo "Creating backup: ${BACKUP_FILE}"

# Create backup
cd /var/www
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    --exclude="node_modules" \
    --exclude="venv" \
    --exclude=".git" \
    --exclude="*.log" \
    arrowtuner/

# Keep only last 30 backups
cd "${BACKUP_DIR}"
ls -t | tail -n +31 | xargs -d '\n' rm -f --

echo "Backup completed: ${BACKUP_FILE}"
EOF

chmod +x /opt/arrowtuner/backup.sh

# Create monitoring script
print_status "Creating health monitoring script..."
cat > /opt/arrowtuner/health-check.sh << 'EOF'
#!/bin/bash
#
# ArrowTuner Health Check Script
#

API_URL="http://localhost:5000/api/health"
FRONTEND_URL="http://localhost:3000"
LOG_FILE="/var/log/arrowtuner/health-check.log"

echo "$(date): Running health check" >> "$LOG_FILE"

# Check API
if curl -f -s "$API_URL" > /dev/null; then
    echo "$(date): API OK" >> "$LOG_FILE"
else
    echo "$(date): API FAILED - restarting service" >> "$LOG_FILE"
    systemctl restart arrowtuner-api
fi

# Check frontend (if using PM2)
if pm2 describe arrowtuner-frontend > /dev/null 2>&1; then
    if ! curl -f -s "$FRONTEND_URL" > /dev/null; then
        echo "$(date): Frontend FAILED - restarting" >> "$LOG_FILE"
        pm2 restart arrowtuner-frontend
    else
        echo "$(date): Frontend OK" >> "$LOG_FILE"
    fi
fi

# Check disk space
DISK_USE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USE" -gt 85 ]; then
    echo "$(date): WARNING - Disk usage at ${DISK_USE}%" >> "$LOG_FILE"
fi
EOF

chmod +x /opt/arrowtuner/health-check.sh

# Add health check to crontab
print_status "Setting up health monitoring..."
(crontab -u arrowtuner -l 2>/dev/null; echo "*/5 * * * * /opt/arrowtuner/health-check.sh") | crontab -u arrowtuner -

# Add daily backup to crontab
(crontab -u root -l 2>/dev/null; echo "0 2 * * * /opt/arrowtuner/backup.sh") | crontab -u root -

# Configure system limits
print_status "Configuring system limits..."
cat >> /etc/security/limits.conf << EOF
arrowtuner soft nofile 65536
arrowtuner hard nofile 65536
EOF

# Configure sysctl for performance
print_status "Optimizing system performance..."
cat >> /etc/sysctl.conf << EOF
# ArrowTuner Performance Optimizations
net.core.somaxconn = 65536
net.ipv4.tcp_max_syn_backlog = 65536
net.ipv4.ip_local_port_range = 1024 65535
vm.swappiness = 10
EOF

sysctl -p

# Install and configure htop
print_status "Configuring monitoring tools..."
apt install -y htop iotop nethogs

# Create deployment info file
cat > /etc/arrowtuner/server-info.txt << EOF
ArrowTuner Production Server
============================

Setup Date: $(date)
Ubuntu Version: $(lsb_release -d | cut -f2)
Node.js Version: $(node --version)
Python Version: $(python3.9 --version)
Docker Version: $(docker --version)

Directories:
- Application: /var/www/arrowtuner
- Logs: /var/log/arrowtuner
- Backups: /opt/arrowtuner/backups
- Config: /etc/arrowtuner

Services:
- API: arrowtuner-api.service
- Web Server: nginx
- Process Manager: PM2
- Monitoring: health-check.sh (every 5 minutes)
- Backups: backup.sh (daily at 2 AM)

Security:
- UFW Firewall: Enabled (SSH, HTTP, HTTPS)
- Fail2ban: Protection against brute force
- SSL: Ready for Let's Encrypt

Next Steps:
1. Deploy application code
2. Configure domain and SSL
3. Set environment variables
4. Start services
EOF

print_success "ArrowTuner server setup completed!"
print_status "Server information saved to: /etc/arrowtuner/server-info.txt"
print_status ""
print_status "Next steps:"
print_status "1. Deploy your application code to /var/www/arrowtuner"
print_status "2. Configure your domain name and SSL certificate"
print_status "3. Set up environment variables"
print_status "4. Run the deployment script"
print_status ""
print_warning "Don't forget to:"
print_warning "- Change default passwords"
print_warning "- Configure your domain name"
print_warning "- Set up SSL certificates"
print_warning "- Review firewall rules"
print_status ""
print_success "Server is ready for ArrowTuner deployment!"