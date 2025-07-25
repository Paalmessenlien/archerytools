#!/bin/bash
# SSL Certificate Manager for ArrowTuner
# Comprehensive SSL management including setup, renewal, monitoring, and troubleshooting

set -e

# Configuration
DOMAIN="${DOMAIN_NAME:-archerytool.online}"
EMAIL="${SSL_EMAIL:-admin@archerytool.online}"
SSL_DIR="/home/paal/arrowtuner2/deploy/ssl"
DOCKER_COMPOSE_FILE="/home/paal/arrowtuner2/docker-compose.ssl.yml"
LOG_DIR="/var/log/arrowtuner"
LOG_FILE="$LOG_DIR/ssl-manager.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log() {
    local message="[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    echo -e "${BLUE}${message}${NC}"
    echo "$message" >> "$LOG_FILE" 2>/dev/null || true
}

success() {
    local message="✅ $1"
    echo -e "${GREEN}${message}${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $message" >> "$LOG_FILE" 2>/dev/null || true
}

warning() {
    local message="⚠️  $1"
    echo -e "${YELLOW}${message}${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $message" >> "$LOG_FILE" 2>/dev/null || true
}

error() {
    local message="❌ $1"
    echo -e "${RED}${message}${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $message" >> "$LOG_FILE" 2>/dev/null || true
}

info() {
    local message="ℹ️  $1"
    echo -e "${CYAN}${message}${NC}"
}

header() {
    echo -e "${PURPLE}$1${NC}"
}

# Initialize logging
init_logging() {
    sudo mkdir -p "$LOG_DIR" 2>/dev/null || mkdir -p "$LOG_DIR" 2>/dev/null || true
    sudo touch "$LOG_FILE" 2>/dev/null || touch "$LOG_FILE" 2>/dev/null || true
    sudo chown $USER:$USER "$LOG_FILE" 2>/dev/null || true
}

# Show usage information
show_usage() {
    header "ArrowTuner SSL Certificate Manager"
    echo
    echo "Usage: $0 <command> [options]"
    echo
    echo "Commands:"
    echo "  setup           - Initial SSL setup with Let's Encrypt"
    echo "  status          - Show certificate status and expiry"
    echo "  renew           - Renew certificates if needed"
    echo "  force-renew     - Force certificate renewal"
    echo "  test            - Test SSL configuration"
    echo "  install-cron    - Install automatic renewal cron job"
    echo "  remove-cron     - Remove automatic renewal cron job"
    echo "  logs            - Show SSL manager logs"
    echo "  troubleshoot    - Run SSL troubleshooting checks"
    echo "  backup          - Backup current certificates"
    echo "  cleanup         - Clean up old certificates and logs"
    echo
    echo "Environment Variables:"
    echo "  DOMAIN_NAME     - Domain name for SSL certificate (default: archerytool.online)"
    echo "  SSL_EMAIL       - Email for Let's Encrypt registration (default: admin@archerytool.online)"
    echo
    echo "Examples:"
    echo "  $0 setup                                    # Initial SSL setup"
    echo "  $0 status                                   # Check certificate status"
    echo "  DOMAIN_NAME=mysite.com SSL_EMAIL=me@mysite.com $0 setup"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
        exit 1
    fi
    
    # Check required commands
    local missing_commands=()
    
    for cmd in certbot docker-compose openssl curl; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_commands+=("$cmd")
        fi
    done
    
    if [[ ${#missing_commands[@]} -gt 0 ]]; then
        error "Missing required commands: ${missing_commands[*]}"
        info "Install missing commands and try again"
        exit 1
    fi
    
    # Check domain and email configuration
    if [[ -z "$DOMAIN" || -z "$EMAIL" ]]; then
        error "Domain name and email must be configured"
        info "Set DOMAIN_NAME and SSL_EMAIL environment variables"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Get certificate information
get_cert_info() {
    if [[ -f "$SSL_DIR/fullchain.pem" ]]; then
        local expiry_date=$(openssl x509 -enddate -noout -in "$SSL_DIR/fullchain.pem" | cut -d= -f2)
        local expiry_epoch=$(date -d "$expiry_date" +%s)
        local current_epoch=$(date +%s)
        local days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
        
        echo "$days_until_expiry|$expiry_date"
    else
        echo "0|No certificate found"
    fi
}

# SSL setup function
ssl_setup() {
    header "🔐 SSL Certificate Setup"
    log "Starting SSL setup for domain: $DOMAIN"
    
    check_prerequisites
    
    # Ensure SSL directory exists
    mkdir -p "$SSL_DIR"
    
    # Stop any running containers using port 80
    log "Stopping containers to free port 80..."
    cd /home/paal/arrowtuner2
    docker-compose down 2>/dev/null || true
    
    # Obtain SSL certificate
    log "Obtaining SSL certificate from Let's Encrypt..."
    if sudo certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        --expand \
        --cert-name "$DOMAIN"; then
        success "SSL certificate obtained successfully"
    else
        error "Failed to obtain SSL certificate"
        exit 1
    fi
    
    # Copy certificates
    log "Copying certificates to deployment directory..."
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/chain.pem" "$SSL_DIR/"
    
    # Set permissions
    sudo chown $USER:$USER "$SSL_DIR"/*.pem
    sudo chmod 644 "$SSL_DIR"/fullchain.pem "$SSL_DIR"/chain.pem
    sudo chmod 600 "$SSL_DIR"/privkey.pem
    
    success "Certificates installed successfully"
    
    # Start services with SSL
    log "Starting ArrowTuner with SSL..."
    docker-compose -f docker-compose.ssl.yml up -d
    
    # Wait and test
    sleep 30
    ssl_test
    
    success "SSL setup completed!"
    info "Run '$0 install-cron' to set up automatic renewal"
}

# SSL status function
ssl_status() {
    header "📊 SSL Certificate Status"
    
    local cert_info=$(get_cert_info)
    local days_until_expiry=$(echo "$cert_info" | cut -d'|' -f1)
    local expiry_date=$(echo "$cert_info" | cut -d'|' -f2)
    
    if [[ -f "$SSL_DIR/fullchain.pem" ]]; then
        info "Certificate file: $SSL_DIR/fullchain.pem"
        info "Domain: $DOMAIN"
        info "Expires: $expiry_date"
        info "Days until expiry: $days_until_expiry"
        
        if [[ $days_until_expiry -lt 7 ]]; then
            error "Certificate expires very soon!"
        elif [[ $days_until_expiry -lt 30 ]]; then
            warning "Certificate expires in less than 30 days"
        else
            success "Certificate is valid"
        fi
        
        echo
        info "Certificate details:"
        openssl x509 -text -noout -in "$SSL_DIR/fullchain.pem" | grep -E "(Subject:|Issuer:|DNS:|Not After :|Not Before:)" | sed 's/^/  /'
    else
        error "No SSL certificate found"
        info "Run '$0 setup' to obtain a certificate"
    fi
}

# SSL renewal function
ssl_renew() {
    header "🔄 SSL Certificate Renewal"
    log "Checking certificate renewal for $DOMAIN"
    
    # Check if renewal is needed
    if sudo certbot renew --cert-name "$DOMAIN" --dry-run; then
        log "Renewing certificate..."
        if sudo certbot renew --cert-name "$DOMAIN" --quiet; then
            success "Certificate renewed successfully"
            
            # Copy new certificates
            sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/"
            sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/"
            sudo cp "/etc/letsencrypt/live/$DOMAIN/chain.pem" "$SSL_DIR/"
            
            # Set permissions
            sudo chown $USER:$USER "$SSL_DIR"/*.pem
            sudo chmod 644 "$SSL_DIR"/fullchain.pem "$SSL_DIR"/chain.pem
            sudo chmod 600 "$SSL_DIR"/privkey.pem
            
            # Restart nginx
            cd /home/paal/arrowtuner2
            docker-compose -f docker-compose.ssl.yml restart nginx
            
            sleep 10
            ssl_test
            success "Certificate renewal completed"
        else
            error "Certificate renewal failed"
            exit 1
        fi
    else
        info "Certificate does not need renewal at this time"
    fi
}

# Force SSL renewal
ssl_force_renew() {
    header "🔄 Force SSL Certificate Renewal"
    warning "Forcing certificate renewal..."
    
    if sudo certbot renew --cert-name "$DOMAIN" --force-renewal; then
        success "Certificate force-renewed successfully"
        
        # Copy and restart as in regular renewal
        sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/"
        sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/"
        sudo cp "/etc/letsencrypt/live/$DOMAIN/chain.pem" "$SSL_DIR/"
        
        sudo chown $USER:$USER "$SSL_DIR"/*.pem
        sudo chmod 644 "$SSL_DIR"/fullchain.pem "$SSL_DIR"/chain.pem
        sudo chmod 600 "$SSL_DIR"/privkey.pem
        
        cd /home/paal/arrowtuner2
        docker-compose -f docker-compose.ssl.yml restart nginx
        
        sleep 10
        ssl_test
        success "Force renewal completed"
    else
        error "Force renewal failed"
        exit 1
    fi
}

# Test SSL configuration
ssl_test() {
    header "🧪 SSL Configuration Test"
    log "Testing SSL configuration for $DOMAIN"
    
    # Test HTTPS connectivity
    if curl -f -s -k "https://$DOMAIN/health" > /dev/null; then
        success "HTTPS connectivity test passed"
    else
        error "HTTPS connectivity test failed"
    fi
    
    # Test certificate validity
    if openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" </dev/null 2>/dev/null | openssl x509 -noout -dates > /dev/null; then
        success "Certificate validity test passed"
    else
        error "Certificate validity test failed"
    fi
    
    # Test HTTP to HTTPS redirect
    if curl -s -I "http://$DOMAIN" | grep -q "301\|302"; then
        success "HTTP to HTTPS redirect working"
    else
        warning "HTTP to HTTPS redirect may not be working"
    fi
    
    info "SSL test completed"
}

# Install cron job for automatic renewal
install_cron() {
    header "⏰ Installing Automatic Renewal"
    
    local cron_job="0 12 * * * $PWD/deploy/scripts/ssl-renew.sh >> $LOG_FILE 2>&1"
    
    if ! crontab -l 2>/dev/null | grep -q "ssl-renew.sh"; then
        (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
        success "Automatic renewal cron job installed"
        info "Certificates will be checked daily at 12:00 PM"
    else
        info "Automatic renewal already configured"
    fi
}

# Remove cron job
remove_cron() {
    header "🗑️  Removing Automatic Renewal"
    
    if crontab -l 2>/dev/null | grep -q "ssl-renew.sh"; then
        crontab -l 2>/dev/null | grep -v "ssl-renew.sh" | crontab -
        success "Automatic renewal cron job removed"
    else
        info "No automatic renewal cron job found"
    fi
}

# Show logs
show_logs() {
    header "📋 SSL Manager Logs"
    
    if [[ -f "$LOG_FILE" ]]; then
        echo "Last 50 lines of SSL manager logs:"
        echo "=====================================>"
        tail -n 50 "$LOG_FILE"
        echo "<====================================="
    else
        info "No log file found at $LOG_FILE"
    fi
}

# Troubleshooting function
troubleshoot() {
    header "🔍 SSL Troubleshooting"
    
    echo "Running comprehensive SSL troubleshooting..."
    echo
    
    # Check domain resolution
    info "1. Checking domain resolution..."
    if nslookup "$DOMAIN" > /dev/null 2>&1; then
        success "Domain resolves correctly"
    else
        error "Domain resolution failed"
    fi
    
    # Check port 443 connectivity
    info "2. Checking port 443 connectivity..."
    if timeout 5 bash -c "</dev/tcp/$DOMAIN/443"; then
        success "Port 443 is accessible"
    else
        error "Port 443 is not accessible"
    fi
    
    # Check Let's Encrypt certificate
    info "3. Checking Let's Encrypt certificate..."
    if [[ -d "/etc/letsencrypt/live/$DOMAIN" ]]; then
        success "Let's Encrypt certificate directory exists"
        ls -la "/etc/letsencrypt/live/$DOMAIN/"
    else
        error "Let's Encrypt certificate directory not found"
    fi
    
    # Check deployment certificates
    info "4. Checking deployment certificates..."
    if [[ -f "$SSL_DIR/fullchain.pem" ]]; then
        success "Deployment certificate exists"
        ls -la "$SSL_DIR/"
    else
        error "Deployment certificate not found"
    fi
    
    # Check Docker containers
    info "5. Checking Docker containers..."
    cd /home/paal/arrowtuner2
    docker-compose -f docker-compose.ssl.yml ps
    
    # Check nginx configuration
    info "6. Testing nginx configuration..."
    if docker-compose -f docker-compose.ssl.yml exec nginx nginx -t 2>/dev/null; then
        success "Nginx configuration is valid"
    else
        error "Nginx configuration has errors"
    fi
    
    echo
    info "Troubleshooting completed"
}

# Backup certificates
backup_certificates() {
    header "💾 Backing Up Certificates"
    
    local backup_dir="/home/paal/arrowtuner2/backups/ssl"
    local backup_file="$backup_dir/ssl-backup-$(date +%Y%m%d_%H%M%S).tar.gz"
    
    mkdir -p "$backup_dir"
    
    if [[ -d "$SSL_DIR" && -f "$SSL_DIR/fullchain.pem" ]]; then
        tar -czf "$backup_file" -C "$SSL_DIR" .
        success "Certificates backed up to: $backup_file"
    else
        error "No certificates found to backup"
    fi
}

# Cleanup old files
cleanup() {
    header "🧹 Cleaning Up"
    
    # Clean old log files (keep last 30 days)
    find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    # Clean old backups (keep last 10)
    local backup_dir="/home/paal/arrowtuner2/backups/ssl"
    if [[ -d "$backup_dir" ]]; then
        ls -t "$backup_dir"/ssl-backup-*.tar.gz 2>/dev/null | tail -n +11 | xargs -r rm
    fi
    
    success "Cleanup completed"
}

# Main script logic
main() {
    init_logging
    
    case "${1:-}" in
        "setup")
            ssl_setup
            ;;
        "status")
            ssl_status
            ;;
        "renew")
            ssl_renew
            ;;
        "force-renew")
            ssl_force_renew
            ;;
        "test")
            ssl_test
            ;;
        "install-cron")
            install_cron
            ;;
        "remove-cron")
            remove_cron
            ;;
        "logs")
            show_logs
            ;;
        "troubleshoot")
            troubleshoot
            ;;
        "backup")
            backup_certificates
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"