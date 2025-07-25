#!/bin/bash
# SSL Certificate Setup Script for ArrowTuner
# Automatically obtains and configures SSL certificates using Let's Encrypt

set -e

# Configuration
DOMAIN="${DOMAIN_NAME:-archerytool.online}"
EMAIL="${SSL_EMAIL:-admin@archerytool.online}"
SSL_DIR="/home/paal/arrowtuner2/deploy/ssl"
DOCKER_COMPOSE_FILE="/home/paal/arrowtuner2/docker-compose.ssl.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root for security reasons"
   exit 1
fi

# Check if domain and email are provided
if [[ -z "$DOMAIN" || -z "$EMAIL" ]]; then
    error "Domain name and email must be provided"
    echo "Usage: DOMAIN_NAME=yourdomain.com SSL_EMAIL=admin@yourdomain.com $0"
    exit 1
fi

# Verify prerequisites
log "Checking prerequisites..."

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    log "Installing certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    error "docker-compose is required but not installed"
    exit 1
fi

# Ensure SSL directory exists
mkdir -p "$SSL_DIR"

log "Setting up SSL certificates for domain: $DOMAIN"
log "Email: $EMAIL"

# Stop any running containers that might use port 80
log "Stopping any running ArrowTuner containers..."
cd /home/paal/arrowtuner2
docker-compose down || true

# Obtain SSL certificate using standalone method
log "Obtaining SSL certificate from Let's Encrypt..."
sudo certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --expand \
    --cert-name "$DOMAIN"

if [[ $? -eq 0 ]]; then
    success "SSL certificate obtained successfully"
else
    error "Failed to obtain SSL certificate"
    exit 1
fi

# Copy certificates to deployment directory
log "Copying certificates to deployment directory..."
sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/"
sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/"
sudo cp "/etc/letsencrypt/live/$DOMAIN/chain.pem" "$SSL_DIR/"

# Set proper ownership
sudo chown $USER:$USER "$SSL_DIR"/*.pem
sudo chmod 644 "$SSL_DIR"/fullchain.pem "$SSL_DIR"/chain.pem
sudo chmod 600 "$SSL_DIR"/privkey.pem

success "Certificates copied to $SSL_DIR"

# Create environment file if it doesn't exist
ENV_FILE="/home/paal/arrowtuner2/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    log "Creating environment file..."
    cat > "$ENV_FILE" << EOF
# ArrowTuner Production Configuration
DOMAIN_NAME=$DOMAIN
SSL_EMAIL=$EMAIL
SECRET_KEY=$(openssl rand -hex 32)
DEEPSEEK_API_KEY=your-deepseek-api-key-here
NODE_ENV=production
API_BASE_URL=https://$DOMAIN/api
EOF
    success "Environment file created at $ENV_FILE"
    warning "Please update DEEPSEEK_API_KEY in $ENV_FILE"
else
    log "Environment file already exists"
fi

# Set up automatic certificate renewal
log "Setting up automatic certificate renewal..."
CRON_JOB="0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'cd /home/paal/arrowtuner2 && docker-compose -f docker-compose.ssl.yml restart nginx' 2>&1 | logger -t certbot-renew"

# Check if cron job already exists
if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    success "Automatic renewal configured"
else
    log "Automatic renewal already configured"
fi

# Start the application with SSL
log "Starting ArrowTuner with SSL enabled..."
cd /home/paal/arrowtuner2
docker-compose -f docker-compose.ssl.yml up -d

# Wait for services to start
log "Waiting for services to start..."
sleep 30

# Test SSL configuration
log "Testing SSL configuration..."
if curl -f -s -k "https://$DOMAIN/health" > /dev/null; then
    success "SSL configuration is working!"
    success "ArrowTuner is now available at: https://$DOMAIN"
else
    warning "Could not verify SSL configuration immediately"
    log "Please wait a few moments for all services to fully start"
fi

# Display status
log "Deployment Status:"
docker-compose -f docker-compose.ssl.yml ps

success "SSL setup completed successfully!"
echo
echo -e "${GREEN}🎉 ArrowTuner is now running with HTTPS!${NC}"
echo -e "${BLUE}Frontend: https://$DOMAIN${NC}"
echo -e "${BLUE}API: https://$DOMAIN/api${NC}"
echo -e "${BLUE}Health Check: https://$DOMAIN/health${NC}"
echo
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Update DEEPSEEK_API_KEY in $ENV_FILE if not already done"
echo "2. Test the application thoroughly"
echo "3. Set up monitoring and backups"
echo "4. Consider firewall rules (UFW) for additional security"