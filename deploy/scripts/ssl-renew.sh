#!/bin/bash
# SSL Certificate Renewal Script for ArrowTuner
# Handles certificate renewal and service restart

set -e

# Configuration
DOMAIN="${DOMAIN_NAME:-archerytool.online}"
SSL_DIR="/home/paal/arrowtuner2/deploy/ssl"
DOCKER_COMPOSE_FILE="/home/paal/arrowtuner2/docker-compose.ssl.yml"
LOG_FILE="/var/log/arrowtuner-ssl-renewal.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    local message="[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    echo -e "${BLUE}${message}${NC}"
    echo "$message" >> "$LOG_FILE"
}

success() {
    local message="✅ $1"
    echo -e "${GREEN}${message}${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $message" >> "$LOG_FILE"
}

warning() {
    local message="⚠️  $1"
    echo -e "${YELLOW}${message}${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $message" >> "$LOG_FILE"
}

error() {
    local message="❌ $1"
    echo -e "${RED}${message}${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $message" >> "$LOG_FILE"
}

# Function to check certificate expiry
check_certificate_expiry() {
    log "Checking certificate expiry for $DOMAIN..."
    
    if [[ ! -f "$SSL_DIR/fullchain.pem" ]]; then
        error "Certificate file not found: $SSL_DIR/fullchain.pem"
        return 1
    fi
    
    # Get certificate expiry date
    EXPIRY_DATE=$(openssl x509 -enddate -noout -in "$SSL_DIR/fullchain.pem" | cut -d= -f2)
    EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
    CURRENT_EPOCH=$(date +%s)
    DAYS_UNTIL_EXPIRY=$(( (EXPIRY_EPOCH - CURRENT_EPOCH) / 86400 ))
    
    log "Certificate expires in $DAYS_UNTIL_EXPIRY days ($EXPIRY_DATE)"
    
    if [[ $DAYS_UNTIL_EXPIRY -lt 30 ]]; then
        warning "Certificate expires in less than 30 days"
        return 0
    elif [[ $DAYS_UNTIL_EXPIRY -lt 7 ]]; then
        error "Certificate expires in less than 7 days!"
        return 0
    else
        success "Certificate is valid for $DAYS_UNTIL_EXPIRY more days"
        return 1
    fi
}

# Function to renew certificate
renew_certificate() {
    log "Attempting to renew SSL certificate..."
    
    # Check if certificate actually needs renewal (certbot's built-in check)
    if sudo certbot renew --cert-name "$DOMAIN" --dry-run; then
        log "Dry run successful. Proceeding with actual renewal..."
        
        # Perform actual renewal
        if sudo certbot renew --cert-name "$DOMAIN" --quiet; then
            success "Certificate renewed successfully"
            return 0
        else
            error "Certificate renewal failed"
            return 1
        fi
    else
        log "Certificate does not need renewal at this time"
        return 1
    fi
}

# Function to copy renewed certificates
copy_certificates() {
    log "Copying renewed certificates..."
    
    # Copy certificates to deployment directory
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/chain.pem" "$SSL_DIR/"
    
    # Set proper ownership and permissions
    sudo chown $USER:$USER "$SSL_DIR"/*.pem
    sudo chmod 644 "$SSL_DIR"/fullchain.pem "$SSL_DIR"/chain.pem
    sudo chmod 600 "$SSL_DIR"/privkey.pem
    
    success "Certificates copied and permissions set"
}

# Function to restart services
restart_services() {
    log "Restarting ArrowTuner services..."
    
    cd /home/paal/arrowtuner2
    
    # Restart nginx container to load new certificates
    if docker-compose -f docker-compose.ssl.yml restart nginx; then
        success "Services restarted successfully"
        
        # Wait a moment for service to fully restart
        sleep 10
        
        # Test the SSL configuration
        if curl -f -s -k "https://$DOMAIN/health" > /dev/null; then
            success "SSL configuration verified after restart"
            return 0
        else
            error "SSL configuration test failed after restart"
            return 1
        fi
    else
        error "Failed to restart services"
        return 1
    fi
}

# Function to send notification (placeholder for future implementation)
send_notification() {
    local status="$1"
    local message="$2"
    
    # Log the notification (extend this to send emails, Slack messages, etc.)
    log "NOTIFICATION [$status]: $message"
    
    # Future: Implement email notifications, webhooks, etc.
    # Example:
    # echo "$message" | mail -s "ArrowTuner SSL $status" admin@$DOMAIN
}

# Main renewal process
main() {
    log "Starting SSL certificate renewal process for $DOMAIN"
    
    # Create log file if it doesn't exist
    sudo touch "$LOG_FILE"
    sudo chown $USER:$USER "$LOG_FILE"
    
    # Check if domain is configured
    if [[ -z "$DOMAIN" ]]; then
        error "Domain name not configured"
        exit 1
    fi
    
    # Check certificate expiry
    if check_certificate_expiry; then
        log "Certificate needs renewal"
        
        # Attempt renewal
        if renew_certificate; then
            # Copy new certificates
            copy_certificates
            
            # Restart services with new certificates
            if restart_services; then
                success "SSL certificate renewal completed successfully"
                send_notification "SUCCESS" "SSL certificate for $DOMAIN renewed successfully"
            else
                error "Service restart failed after certificate renewal"
                send_notification "WARNING" "SSL certificate renewed but service restart failed for $DOMAIN"
                exit 1
            fi
        else
            log "Certificate renewal not needed at this time"
        fi
    else
        log "Certificate renewal not needed"
    fi
    
    log "SSL renewal process completed"
}

# Handle command line arguments
case "${1:-}" in
    "check")
        check_certificate_expiry
        ;;
    "force")
        log "Forcing certificate renewal..."
        if renew_certificate; then
            copy_certificates
            restart_services
        fi
        ;;
    "status")
        if [[ -f "$SSL_DIR/fullchain.pem" ]]; then
            check_certificate_expiry
            echo
            log "Certificate details:"
            openssl x509 -text -noout -in "$SSL_DIR/fullchain.pem" | grep -E "(Subject:|Not After :)"
        else
            error "No certificate found"
        fi
        ;;
    *)
        main
        ;;
esac