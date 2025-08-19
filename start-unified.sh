#!/bin/bash
#
# Unified Startup Script for ArrowTuner Platform
# Handles all deployment scenarios: development, production, SSL
#
# Usage:
#   ./start-unified.sh                    # Docker development mode
#   ./start-unified.sh dev               # Local development mode (no Docker)
#   ./start-unified.sh production         # Production HTTP mode
#   ./start-unified.sh ssl yourdomain.com # Production SSL mode

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Default values
DEPLOYMENT_MODE="${1:-development}"
DOMAIN_NAME="${2:-localhost}"
SSL_ENABLED="false"
COMPOSE_PROFILES=""


# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Handle special case for dev mode with stop command
if [[ "$1" == "dev" && "$2" == "stop" ]]; then
    print_message "$BLUE" "🛑 Stopping local development services..."
    
    # Stop API server
    if [[ -f "logs/api.pid" ]]; then
        api_pid=$(cat logs/api.pid)
        if kill -0 $api_pid 2>/dev/null; then
            kill $api_pid
            print_message "$GREEN" "✅ Stopped API server (PID: $api_pid)"
        fi
        rm -f logs/api.pid
    fi
    
    # Stop frontend server
    if [[ -f "logs/frontend.pid" ]]; then
        frontend_pid=$(cat logs/frontend.pid)
        if kill -0 $frontend_pid 2>/dev/null; then
            kill $frontend_pid
            print_message "$GREEN" "✅ Stopped frontend server (PID: $frontend_pid)"
        fi
        rm -f logs/frontend.pid
    fi
    
    # Kill any remaining processes
    pkill -f "python.*api.py" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "nuxt" 2>/dev/null || true
    
    print_message "$GREEN" "✅ All local development services stopped"
    exit 0
fi

# Function to check prerequisites
check_prerequisites() {
    print_message "$BLUE" "🔍 Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_message "$RED" "❌ Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_message "$RED" "❌ Docker Compose is not installed"
        exit 1
    fi
    
    # Check dig command (needed for domain resolution check)
    if ! command -v dig &> /dev/null; then
        print_message "$YELLOW" "⚠️  dig command not found, installing bind-utils..."
        if [[ -f /etc/debian_version ]]; then
            apt-get update && apt-get install -y dnsutils
        elif [[ -f /etc/redhat-release ]]; then
            if command -v dnf &> /dev/null; then
                dnf install -y bind-utils
            else
                yum install -y bind-utils
            fi
        fi
    fi
    
    # Check .env file
    if [[ ! -f ".env" ]]; then
        print_message "$YELLOW" "⚠️  No .env file found, creating from example..."
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            print_message "$GREEN" "✅ Created .env file from example"
        else
            print_message "$RED" "❌ No .env.example file found"
            exit 1
        fi
    fi
    
    print_message "$GREEN" "✅ Prerequisites check passed"
}

# Function to setup environment variables
setup_environment() {
    print_message "$BLUE" "🔧 Setting up environment for $DEPLOYMENT_MODE mode..."
    
    # Export deployment mode
    export DEPLOYMENT_MODE
    export DOMAIN_NAME
    
    case "$DEPLOYMENT_MODE" in
        "development")
            export FLASK_ENV="development"
            export NODE_ENV="development"
            export NUXT_PUBLIC_API_BASE="http://localhost:5000/api"
            export API_DOCKERFILE="Dockerfile"
            export FRONTEND_DOCKERFILE="Dockerfile"
            COMPOSE_PROFILES="--profile with-nginx"
            print_message "$GREEN" "✅ Docker development environment configured"
            ;;
            
        "dev")
            export FLASK_ENV="development"
            export NODE_ENV="development"
            export NUXT_PUBLIC_API_BASE="http://localhost:5000/api"
            print_message "$GREEN" "✅ Local development environment configured"
            print_message "$BLUE" "🚀 Starting local development servers (no Docker)..."
            start_local_development
            exit 0
            ;;
            
        "production")
            export FLASK_ENV="production"
            export NODE_ENV="production"
            export NUXT_PUBLIC_API_BASE="http://${DOMAIN_NAME}/api"
            export API_DOCKERFILE="Dockerfile.enhanced"
            export FRONTEND_DOCKERFILE="Dockerfile.enhanced"
            COMPOSE_PROFILES="--profile with-nginx"
            print_message "$GREEN" "✅ Production HTTP environment configured"
            ;;
            
        "ssl")
            export FLASK_ENV="production"
            export NODE_ENV="production"
            export SSL_ENABLED="true"
            export NUXT_PUBLIC_API_BASE="https://${DOMAIN_NAME}/api"
            export GOOGLE_REDIRECT_URI="https://${DOMAIN_NAME}"
            export API_DOCKERFILE="Dockerfile.enhanced"
            export FRONTEND_DOCKERFILE="Dockerfile.enhanced"
            COMPOSE_PROFILES="--profile with-nginx --profile with-backup"
            
            # Check SSL certificates
            check_ssl_certificates
            
            print_message "$GREEN" "✅ Production SSL environment configured"
            ;;
            
        *)
            print_message "$RED" "❌ Invalid deployment mode: $DEPLOYMENT_MODE"
            echo "Usage: $0 [dev|development|production|ssl] [domain_name]"
            exit 1
            ;;
    esac
}

# Function to check and install certbot if needed
ensure_certbot_installed() {
    if ! command -v certbot &> /dev/null; then
        print_message "$YELLOW" "⚠️  Certbot not found, installing..."
        
        # Detect OS and install certbot
        if [[ -f /etc/debian_version ]]; then
            # Debian/Ubuntu
            apt-get update
            apt-get install -y certbot
        elif [[ -f /etc/redhat-release ]]; then
            # RHEL/CentOS/Fedora
            if command -v dnf &> /dev/null; then
                dnf install -y certbot
            else
                yum install -y certbot
            fi
        else
            print_message "$RED" "❌ Unsupported OS for automatic certbot installation"
            echo "Please install certbot manually:"
            echo "  - Ubuntu/Debian: sudo apt-get install certbot"
            echo "  - RHEL/CentOS: sudo yum install certbot"
            echo "  - Fedora: sudo dnf install certbot"
            exit 1
        fi
        
        print_message "$GREEN" "✅ Certbot installed successfully"
    else
        print_message "$GREEN" "✅ Certbot is already installed"
    fi
}

# Function to check SSL certificates
check_ssl_certificates() {
    print_message "$BLUE" "🔒 Checking SSL certificates..."
    
    SSL_DIR="$SCRIPT_DIR/deploy/ssl"
    mkdir -p "$SSL_DIR"
    
    # First check if we have Let's Encrypt certificates
    LETSENCRYPT_CERT="/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem"
    LETSENCRYPT_KEY="/etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem"
    
    if [[ -f "$LETSENCRYPT_CERT" ]] && [[ -f "$LETSENCRYPT_KEY" ]]; then
        print_message "$GREEN" "✅ Let's Encrypt certificates found"
        
        # Copy certificates to our SSL directory
        cp "$LETSENCRYPT_CERT" "$SSL_DIR/cert.pem"
        cp "$LETSENCRYPT_KEY" "$SSL_DIR/key.pem"
        cp "/etc/letsencrypt/live/$DOMAIN_NAME/chain.pem" "$SSL_DIR/chain.pem" 2>/dev/null || true
        cp "$LETSENCRYPT_CERT" "$SSL_DIR/fullchain.pem"
        
        # Check certificate expiration
        check_certificate_expiration
        
    elif [[ -f "$SSL_DIR/cert.pem" ]] && [[ -f "$SSL_DIR/key.pem" ]]; then
        print_message "$GREEN" "✅ SSL certificates found in deploy/ssl/"
        check_certificate_expiration
        
    else
        print_message "$YELLOW" "⚠️  No SSL certificates found"
        
        # Ensure certbot is installed
        ensure_certbot_installed
        
        # Offer certificate generation options
        echo
        echo "SSL Certificate Options:"
        echo "1) Generate Let's Encrypt certificate (recommended for production)"
        echo "2) Create self-signed certificate (testing only)"
        echo "3) Exit and manually provide certificates"
        echo
        read -p "Choose option (1-3): " -n 1 -r
        echo
        
        case $REPLY in
            1)
                generate_letsencrypt_certificate
                ;;
            2)
                create_self_signed_certificates
                ;;
            3)
                print_message "$RED" "❌ SSL certificates required for SSL mode"
                echo "Please place your SSL certificates at:"
                echo "  - $SSL_DIR/cert.pem (certificate)"
                echo "  - $SSL_DIR/key.pem (private key)"
                echo "  - $SSL_DIR/chain.pem (certificate chain - optional)"
                exit 1
                ;;
            *)
                print_message "$RED" "❌ Invalid option"
                exit 1
                ;;
        esac
    fi
}

# Function to generate Let's Encrypt certificate
generate_letsencrypt_certificate() {
    print_message "$BLUE" "🔐 Generating Let's Encrypt certificate for $DOMAIN_NAME..."
    
    # Check if domain resolves to this server
    check_domain_resolution
    
    # Create webroot directory for Let's Encrypt challenges
    WEBROOT_PATH="$SCRIPT_DIR/.well-known"
    mkdir -p "$WEBROOT_PATH/acme-challenge"
    
    # Stop any running web services that might use port 80
    print_message "$YELLOW" "⚠️  Temporarily stopping services for certificate generation..."
    docker-compose -f docker-compose.unified.yml down 2>/dev/null || true
    
    # Kill any processes using port 80/443
    fuser -k 80/tcp 2>/dev/null || true
    fuser -k 443/tcp 2>/dev/null || true
    
    # Wait a moment for ports to be freed
    sleep 2
    
    # Generate certificate using standalone mode
    print_message "$BLUE" "📝 Requesting SSL certificate from Let's Encrypt..."
    if certbot certonly --standalone \
        --non-interactive \
        --agree-tos \
        --email "${SSL_EMAIL:-admin@$DOMAIN_NAME}" \
        --domains "$DOMAIN_NAME" \
        --rsa-key-size 4096 \
        --preferred-challenges http; then
        
        print_message "$GREEN" "✅ Let's Encrypt certificate generated successfully"
        
        # Copy certificates to our SSL directory
        SSL_DIR="$SCRIPT_DIR/deploy/ssl"
        mkdir -p "$SSL_DIR"
        
        if [[ -f "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" ]]; then
            cp "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" "$SSL_DIR/cert.pem"
            cp "/etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem" "$SSL_DIR/key.pem"
            cp "/etc/letsencrypt/live/$DOMAIN_NAME/chain.pem" "$SSL_DIR/chain.pem" 2>/dev/null || true
            cp "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" "$SSL_DIR/fullchain.pem"
            
            # Set proper permissions
            chmod 644 "$SSL_DIR/cert.pem" "$SSL_DIR/fullchain.pem"
            chmod 600 "$SSL_DIR/key.pem"
            
            # Set up automatic renewal
            setup_certificate_renewal
        else
            print_message "$RED" "❌ Certificate files not found after generation"
            create_self_signed_certificates
        fi
        
    else
        print_message "$RED" "❌ Failed to generate Let's Encrypt certificate"
        echo "This could be due to:"
        echo "  - Domain not pointing to this server (DNS: $(dig +short $DOMAIN_NAME || echo 'resolution failed'))"
        echo "  - Port 80 not accessible from internet"
        echo "  - Rate limiting from Let's Encrypt (max 5 per week per domain)"
        echo "  - Firewall blocking connections"
        echo "  - Domain validation timeout"
        echo
        
        read -p "Would you like to continue with self-signed certificates for testing? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_self_signed_certificates
        else
            print_message "$RED" "❌ SSL certificate generation failed. Exiting."
            exit 1
        fi
    fi
}

# Function to check domain resolution
check_domain_resolution() {
    print_message "$BLUE" "🌐 Checking domain resolution for $DOMAIN_NAME..."
    
    # Get external IP of this server
    SERVER_IP=$(curl -s http://checkip.amazonaws.com || curl -s http://ipecho.net/plain || curl -s http://icanhazip.com)
    
    if [[ -z "$SERVER_IP" ]]; then
        print_message "$YELLOW" "⚠️  Could not determine server IP"
        return
    fi
    
    # Check if domain resolves to this server
    DOMAIN_IP=$(dig +short "$DOMAIN_NAME" | tail -n1)
    
    if [[ "$DOMAIN_IP" == "$SERVER_IP" ]]; then
        print_message "$GREEN" "✅ Domain $DOMAIN_NAME resolves to this server ($SERVER_IP)"
    else
        print_message "$YELLOW" "⚠️  Domain resolution mismatch:"
        echo "    Domain $DOMAIN_NAME resolves to: $DOMAIN_IP"
        echo "    This server IP: $SERVER_IP"
        echo "    Let's Encrypt may fail if domain doesn't point to this server"
    fi
}

# Function to check certificate expiration
check_certificate_expiration() {
    local cert_file="$SSL_DIR/cert.pem"
    
    if [[ -f "$cert_file" ]]; then
        local expiry_date=$(openssl x509 -enddate -noout -in "$cert_file" | cut -d= -f2)
        local expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null || echo "0")
        local current_epoch=$(date +%s)
        local days_left=$(( ($expiry_epoch - $current_epoch) / 86400 ))
        
        if [[ $days_left -lt 30 ]]; then
            print_message "$YELLOW" "⚠️  SSL certificate expires in $days_left days"
            if [[ $days_left -lt 7 ]]; then
                print_message "$YELLOW" "🔄 Certificate expires soon, attempting renewal..."
                renew_certificate
            fi
        else
            print_message "$GREEN" "✅ SSL certificate is valid for $days_left more days"
        fi
    fi
}

# Function to renew certificate
renew_certificate() {
    print_message "$BLUE" "🔄 Renewing SSL certificate..."
    
    if certbot renew --quiet --no-self-upgrade; then
        print_message "$GREEN" "✅ Certificate renewed successfully"
        
        # Copy renewed certificates
        SSL_DIR="$SCRIPT_DIR/deploy/ssl"
        cp "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" "$SSL_DIR/cert.pem"
        cp "/etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem" "$SSL_DIR/key.pem"
        cp "/etc/letsencrypt/live/$DOMAIN_NAME/chain.pem" "$SSL_DIR/chain.pem"
        cp "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" "$SSL_DIR/fullchain.pem"
        
        # Restart services to use new certificate
        print_message "$BLUE" "🔄 Restarting services with renewed certificate..."
        docker-compose -f docker-compose.unified.yml restart nginx 2>/dev/null || true
        
    else
        print_message "$RED" "❌ Certificate renewal failed"
    fi
}

# Function to setup automatic certificate renewal
setup_certificate_renewal() {
    print_message "$BLUE" "⚙️  Setting up automatic certificate renewal..."
    
    # Create renewal script
    RENEWAL_SCRIPT="/usr/local/bin/archerytools-ssl-renew.sh"
    
    cat > "$RENEWAL_SCRIPT" << 'EOF'
#!/bin/bash
# ArrowTuner SSL Certificate Renewal Script

SCRIPT_DIR="/root/archerytools"
SSL_DIR="$SCRIPT_DIR/deploy/ssl"
DOMAIN_NAME="archerytool.online"

# Renew certificate
if /usr/bin/certbot renew --quiet --no-self-upgrade; then
    # Copy renewed certificates
    cp "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" "$SSL_DIR/cert.pem"
    cp "/etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem" "$SSL_DIR/key.pem"
    cp "/etc/letsencrypt/live/$DOMAIN_NAME/chain.pem" "$SSL_DIR/chain.pem"
    cp "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" "$SSL_DIR/fullchain.pem"
    
    # Restart nginx container to use new certificate
    cd "$SCRIPT_DIR"
    /usr/bin/docker-compose -f docker-compose.unified.yml restart nginx 2>/dev/null || true
    
    echo "$(date): SSL certificate renewed and services restarted" >> /var/log/archerytools-ssl-renewal.log
fi
EOF
    
    chmod +x "$RENEWAL_SCRIPT"
    
    # Update domain name in script
    sed -i "s/archerytool.online/$DOMAIN_NAME/g" "$RENEWAL_SCRIPT"
    
    # Add cron job for automatic renewal (twice daily)
    CRON_JOB="0 */12 * * * $RENEWAL_SCRIPT"
    
    # Check if cron job already exists
    if ! crontab -l 2>/dev/null | grep -q "$RENEWAL_SCRIPT"; then
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
        print_message "$GREEN" "✅ Automatic renewal cron job added"
    else
        print_message "$GREEN" "✅ Automatic renewal cron job already exists"
    fi
    
    print_message "$GREEN" "✅ Certificate renewal setup complete"
    echo "    Renewal script: $RENEWAL_SCRIPT"
    echo "    Log file: /var/log/archerytools-ssl-renewal.log"
}

# Function to create self-signed certificates
create_self_signed_certificates() {
    print_message "$BLUE" "🔧 Creating self-signed certificates..."
    
    SSL_DIR="$SCRIPT_DIR/deploy/ssl"
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/key.pem" \
        -out "$SSL_DIR/cert.pem" \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN_NAME"
    
    print_message "$GREEN" "✅ Self-signed certificates created"
    print_message "$YELLOW" "⚠️  These are for testing only. Use proper certificates in production!"
}

# Function to ensure unified nginx configuration exists
ensure_nginx_config() {
    print_message "$BLUE" "📋 Ensuring nginx configuration..."
    
    NGINX_TEMPLATE="$SCRIPT_DIR/deploy/nginx/unified.conf.template"
    NGINX_CONFIG="$SCRIPT_DIR/deploy/nginx/nginx.generated.conf"
    
    if [[ ! -f "$NGINX_TEMPLATE" ]]; then
        print_message "$YELLOW" "⚠️  Creating unified nginx configuration template..."
        mkdir -p "$(dirname "$NGINX_TEMPLATE")"
        create_nginx_template
    fi
    
    # Generate nginx config based on SSL mode
    generate_nginx_config
}

# Function to clean up old containers and volumes
cleanup_old_setup() {
    print_message "$BLUE" "🧹 Cleaning up old Docker setup..."
    
    # Stop any running containers from old compose files
    local OLD_COMPOSE_FILES=(
        "docker-compose.yml"
        "docker-compose.enhanced-ssl.yml"
        "docker-compose.prod.yml"
        "docker-compose.ssl.yml"
        "docker-compose.dev.yml"
    )
    
    for compose_file in "${OLD_COMPOSE_FILES[@]}"; do
        if [[ -f "$compose_file" ]] && [[ "$compose_file" != "docker-compose.unified.yml" ]]; then
            print_message "$YELLOW" "  Stopping containers from $compose_file..."
            docker-compose -f "$compose_file" down --remove-orphans 2>/dev/null || true
        fi
    done
    
    print_message "$GREEN" "✅ Cleanup completed"
}

# Function to ensure unified databases exist
ensure_unified_databases() {
    print_message "$BLUE" "🗄️  Ensuring unified databases directory..."
    
    # Create unified databases directory if it doesn't exist
    mkdir -p "./databases"
    
    # The databases should already be in the unified location
    # If not, they will be created by the database classes on first run
    if [[ -f "./databases/arrow_database.db" ]]; then
        print_message "$GREEN" "✅ Arrow database found in unified location"
    else
        print_message "$YELLOW" "⚠️  Arrow database will be created on first run"
    fi
    
    if [[ -f "./databases/user_data.db" ]]; then
        print_message "$GREEN" "✅ User database found in unified location" 
    else
        print_message "$YELLOW" "⚠️  User database will be created on first run"
    fi
    
    # Run database migrations
    run_database_migrations
}

# Function to run database consolidation migration
run_database_consolidation() {
    print_message "$BLUE" "🎯 Running database consolidation migration..."
    
    local arrow_db_path="$SCRIPT_DIR/databases/arrow_database.db"
    
    # Check if consolidation is needed
    if [[ ! -f "$user_db_path" ]]; then
        print_message "$GREEN" "✅ No user database found - consolidation not needed"
        return 0
    fi
    
    # Check if consolidation already completed by looking for user tables in arrow database
    if sqlite3 "$arrow_db_path" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='users';" 2>/dev/null | grep -q "1"; then
        print_message "$GREEN" "✅ Database consolidation already completed (users table exists in arrow database)"
        return 0
    fi
    
    print_message "$YELLOW" "🔄 Running database consolidation: User DB → Arrow DB"
    print_message "$BLUE" "   Source: $user_db_path"
    print_message "$BLUE" "   Target: $arrow_db_path"
    
    # Run consolidation migration
    cd arrow_scraper
    if python3 migrations/023_consolidate_user_database.py "$arrow_db_path"; then
        print_message "$GREEN" "✅ Database consolidation completed successfully!"
        
        # Create backup of old user database
        local backup_name="user_data_pre_consolidation_$(date +%Y%m%d_%H%M%S).db"
        cp "$user_db_path" "$SCRIPT_DIR/databases/$backup_name"
        print_message "$GREEN" "💾 User database backup created: $backup_name"
        
        # Optional: Remove old user database (commented out for safety)
        # rm "$user_db_path"
        # print_message "$GREEN" "🗑️  Original user database removed"
        
        cd "$SCRIPT_DIR"
        return 0
    else
        print_message "$RED" "❌ Database consolidation failed!"
        cd "$SCRIPT_DIR"
        return 1
    fi
}

# Function to run database migrations
run_database_migrations() {
    print_message "$BLUE" "🔄 Running comprehensive database migrations..."
    
    # Step 1: Run database consolidation first
    if ! run_database_consolidation; then
        print_message "$RED" "❌ Database consolidation failed, stopping migration process"
        return 1
    fi
    
    # Step 2: Use the comprehensive migration runner
    if [[ -f "$SCRIPT_DIR/comprehensive-migration-runner.sh" ]]; then
        print_message "$BLUE" "🎯 Using comprehensive migration runner..."
        
        # Set environment variables for migration
        export ARROW_DATABASE_PATH="$SCRIPT_DIR/databases/arrow_database.db"
        
        # After consolidation, both database paths point to unified arrow database
        if sqlite3 "$SCRIPT_DIR/databases/arrow_database.db" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='users';" 2>/dev/null | grep -q "1"; then
            print_message "$BLUE" "   🎯 Using unified database (post-consolidation)"
            export USER_DATABASE_PATH="$SCRIPT_DIR/databases/arrow_database.db"
        else
            print_message "$BLUE" "   🔄 Using separate user database (pre-consolidation)"
        fi
        
        # Determine environment for migration
        local migration_environment="development"
        if [[ "$DEPLOYMENT_MODE" == "production" ]] || [[ "$DEPLOYMENT_MODE" == "ssl" ]]; then
            migration_environment="production"
        fi
        
        # Run comprehensive migration system
        if "$SCRIPT_DIR/comprehensive-migration-runner.sh" "$migration_environment"; then
            print_message "$GREEN" "✅ Comprehensive database migrations completed successfully"
            return 0
        else
            print_message "$YELLOW" "⚠️  Comprehensive migrations had issues, trying fallback..."
        fi
    fi
    
    # Fallback 1: Check for Docker migration runner
    if command -v docker &> /dev/null && docker ps &> /dev/null; then
        print_message "$BLUE" "🐳 Trying Docker migration runner as fallback..."
        
        # Give containers a moment to start if they're just starting up
        sleep 3
        
        if [[ -f "docker-migration-runner.sh" ]]; then
            if ./docker-migration-runner.sh migrate; then
                print_message "$GREEN" "✅ Database migrations completed successfully in Docker"
                return 0
            else
                print_message "$YELLOW" "⚠️  Docker migrations had issues, trying next fallback..."
            fi
        fi
    fi
    
    # Fallback 2: Direct migration runner execution
    if [[ -f "arrow_scraper/run_migrations.py" ]]; then
        cd arrow_scraper
        
        # Set environment variables for migration
        export ARROW_DATABASE_PATH="$SCRIPT_DIR/databases/arrow_database.db"
        
        # After consolidation, both database paths point to unified arrow database
        if sqlite3 "$SCRIPT_DIR/databases/arrow_database.db" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='users';" 2>/dev/null | grep -q "1"; then
            print_message "$BLUE" "   🎯 Using unified database (post-consolidation)"
            export USER_DATABASE_PATH="$SCRIPT_DIR/databases/arrow_database.db"
        else
            print_message "$BLUE" "   🔄 Using separate user database (pre-consolidation)"
        fi
        
        # Try to run migrations with Python
        if command -v python3 &> /dev/null; then
            print_message "$BLUE" "🔧 Running direct migrations with Python 3..."
            
            if python3 run_migrations.py --status-only; then
                # Show migration status and run if needed
                if python3 run_migrations.py; then
                    print_message "$GREEN" "✅ Database migrations completed successfully"
                    cd "$SCRIPT_DIR"
                    return 0
                else
                    print_message "$YELLOW" "⚠️  Some migrations failed, trying legacy migration..."
                fi
            else
                print_message "$YELLOW" "⚠️  Could not check migration status, trying legacy migration..."
            fi
        else
            print_message "$YELLOW" "⚠️  Python 3 not available, trying legacy migration..."
        fi
        
        cd "$SCRIPT_DIR"
    fi
    
    # Fallback 3: Legacy spine data migration
    print_message "$YELLOW" "⚠️  Using legacy migration system as final fallback..."
    ensure_spine_data_migration
}

# Function to ensure spine calculation data migration
ensure_spine_data_migration() {
    print_message "$BLUE" "🧮 Checking spine calculation data migration..."
    
    # Check if spine calculation tables exist
    if command -v sqlite3 &> /dev/null; then
        cd arrow_scraper
        
        # Check if enhanced spine tables exist in the arrow database
        SPINE_TABLES_COUNT=$(sqlite3 "../databases/arrow_database.db" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name IN ('manufacturer_spine_charts_enhanced', 'custom_spine_charts', 'spine_conversion_tables');" 2>/dev/null || echo "0")
        
        if [[ "$SPINE_TABLES_COUNT" == "3" ]]; then
            print_message "$GREEN" "✅ Enhanced spine calculation tables already exist"
            
            # Check if we have spine chart data
            SPINE_CHARTS_COUNT=$(sqlite3 "../databases/arrow_database.db" "SELECT COUNT(*) FROM manufacturer_spine_charts_enhanced;" 2>/dev/null || echo "0")
            if [[ "$SPINE_CHARTS_COUNT" == "0" ]]; then
                print_message "$YELLOW" "⚠️  Spine tables exist but no data found, importing data..."
                run_spine_data_import
            else
                print_message "$GREEN" "✅ Found $SPINE_CHARTS_COUNT spine charts in database"
            fi
        else
            print_message "$YELLOW" "⚠️  Enhanced spine calculation tables missing, running migration..."
            run_spine_data_import
        fi
        
        cd "$SCRIPT_DIR"
    else
        print_message "$YELLOW" "⚠️  sqlite3 not available, skipping spine data check"
    fi
}

# Function to run spine data import
run_spine_data_import() {
    if [[ -f "spine_calculator_data_importer.py" ]]; then
        # Set database path to unified location
        export ARROW_DATABASE_PATH="$SCRIPT_DIR/databases/arrow_database.db"
        
        print_message "$BLUE" "📊 Running comprehensive spine calculator data import..."
        if python3 spine_calculator_data_importer.py; then
            print_message "$GREEN" "✅ Spine calculator data import completed successfully"
            
            # Verify import
            SPINE_CHARTS_COUNT=$(sqlite3 "../databases/arrow_database.db" "SELECT COUNT(*) FROM manufacturer_spine_charts_enhanced;" 2>/dev/null || echo "0")
            print_message "$GREEN" "✅ Imported $SPINE_CHARTS_COUNT manufacturer spine charts"
            
        else
            print_message "$YELLOW" "⚠️  Warning: Spine calculator data import failed, continuing anyway"
            
            # Fall back to legacy migration if available
            if [[ -f "migrate_spine_calculation_data.py" ]]; then
                print_message "$YELLOW" "🔄 Trying legacy spine data migration..."
                if python3 migrate_spine_calculation_data.py; then
                    print_message "$GREEN" "✅ Legacy spine calculation migration completed"
                else
                    print_message "$YELLOW" "⚠️  Warning: All spine migration attempts failed"
                fi
            fi
        fi
    else
        print_message "$YELLOW" "⚠️  Warning: spine_calculator_data_importer.py not found"
        
        # Fall back to legacy migration
        if [[ -f "migrate_spine_calculation_data.py" ]]; then
            print_message "$YELLOW" "🔄 Using legacy spine data migration..."
            export ARROW_DATABASE_PATH="$SCRIPT_DIR/databases/arrow_database.db"
            if python3 migrate_spine_calculation_data.py; then
                print_message "$GREEN" "✅ Legacy spine calculation migration completed"
            else
                print_message "$YELLOW" "⚠️  Warning: Legacy spine migration failed"
            fi
        fi
    fi
}

# Function to set Docker environment variables for unified database
setup_docker_database_environment() {
    print_message "$BLUE" "🔧 Setting up Docker database environment..."
    
    # Check if consolidation has been completed
    if sqlite3 "$SCRIPT_DIR/databases/arrow_database.db" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='users';" 2>/dev/null | grep -q "1"; then
        print_message "$GREEN" "🎯 Database consolidation detected - using unified database"
        # Both database paths point to the unified arrow database
        export ARROW_DATABASE_PATH="/app/databases/arrow_database.db"
        export USER_DATABASE_PATH="/app/databases/arrow_database.db"
    else
        print_message "$BLUE" "🔄 Using separate databases (pre-consolidation)"
        # Use separate database paths
        export ARROW_DATABASE_PATH="/app/databases/arrow_database.db"
    fi
    
    print_message "$GREEN" "✅ Docker database environment configured"
}

# Function to start the services
start_services() {
    print_message "$BLUE" "🚀 Starting ArrowTuner services..."
    
    # Stop any existing containers first to prevent conflicts
    print_message "$BLUE" "🛑 Stopping any existing containers..."
    docker-compose -f docker-compose.unified.yml down --remove-orphans 2>/dev/null || true
    
    # Give Docker a moment to clean up
    sleep 2
    
    # Setup database environment variables for Docker
    setup_docker_database_environment
    
    # Try to build first, but handle network issues gracefully
    print_message "$YELLOW" "📦 Building services (this may take a moment)..."
    if ! docker-compose -f docker-compose.unified.yml $COMPOSE_PROFILES build; then
        print_message "$YELLOW" "⚠️  Build failed (likely network issue), trying with existing images..."
        
        # Check if we have existing images
        if docker images --format "table {{.Repository}}" | grep -q "archerytools"; then
            print_message "$BLUE" "✅ Found existing images, starting services..."
        else
            print_message "$RED" "❌ No existing images found and build failed"
            print_message "$YELLOW" "Try again when network connectivity is restored"
            exit 1
        fi
    fi
    
    # Start services
    docker-compose -f docker-compose.unified.yml $COMPOSE_PROFILES up -d
    
    print_message "$GREEN" "✅ Services started successfully"
}

# Function to show status
show_status() {
    print_message "$BLUE" "\n📊 Service Status:"
    docker-compose -f docker-compose.unified.yml ps
    
    print_message "$BLUE" "\n🌐 Access URLs:"
    case "$DEPLOYMENT_MODE" in
        "development")
            echo "  Frontend: http://localhost:3000"
            echo "  API: http://localhost:5000/api"
            ;;
        "production")
            echo "  Frontend: http://$DOMAIN_NAME"
            echo "  API: http://$DOMAIN_NAME/api"
            ;;
        "ssl")
            echo "  Frontend: https://$DOMAIN_NAME"
            echo "  API: https://$DOMAIN_NAME/api"
            ;;
    esac
    
    print_message "$BLUE" "\n📝 Logs:"
    echo "  View logs: docker-compose -f docker-compose.unified.yml logs -f"
    echo "  API logs: docker-compose -f docker-compose.unified.yml logs -f api"
    echo "  Frontend logs: docker-compose -f docker-compose.unified.yml logs -f frontend"
}

# Function to generate nginx config based on deployment mode
generate_nginx_config() {
    local NGINX_CONFIG="$SCRIPT_DIR/deploy/nginx/nginx.generated.conf"
    
    print_message "$BLUE" "📝 Generating nginx configuration for $DEPLOYMENT_MODE mode..."
    
    if [[ "$DEPLOYMENT_MODE" == "ssl" ]]; then
        # SSL mode - redirect HTTP to HTTPS
        create_ssl_nginx_config "$NGINX_CONFIG"
    else
        # Development or production HTTP mode
        create_http_nginx_config "$NGINX_CONFIG"
    fi
    
    print_message "$GREEN" "✅ Nginx configuration generated: $NGINX_CONFIG"
}

# Function to create SSL nginx config
create_ssl_nginx_config() {
    local config_file="$1"
    
    cat > "$config_file" << EOF
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Basic settings
    sendfile on;
    keepalive_timeout 65;
    server_tokens off;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Upstream servers
    upstream frontend {
        server frontend:3000;
        keepalive 32;
    }

    upstream api {
        server api:5000;
        keepalive 32;
    }

    # HTTP server - Redirect all to HTTPS
    server {
        listen 80;
        server_name _;

        # Health check endpoint - always available
        location /health {
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }

        # Let's Encrypt challenges
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # Redirect all other traffic to HTTPS
        location / {
            return 301 https://\$host\$request_uri;
        }
    }

    # HTTPS server
    server {
        listen 443 ssl;
        server_name _;
        http2 on;

        # SSL certificate configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Modern SSL configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Health check endpoint
        location /health {
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }

        # API endpoints
        location /api/ {
            proxy_pass http://api;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Frontend application
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }
}
EOF
}

# Function to create HTTP-only nginx config
create_http_nginx_config() {
    local config_file="$1"
    
    cat > "$config_file" << EOF
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Basic settings
    sendfile on;
    keepalive_timeout 65;
    server_tokens off;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Upstream servers
    upstream frontend {
        server frontend:3000;
        keepalive 32;
    }

    upstream api {
        server api:5000;
        keepalive 32;
    }

    # HTTP server
    server {
        listen 80;
        server_name _;

        # Health check endpoint
        location /health {
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }

        # API endpoints
        location /api/ {
            proxy_pass http://api;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Frontend application
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }
}
EOF
}

# Function to create nginx template
create_nginx_template() {
    cat > "$NGINX_TEMPLATE" << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Basic settings
    sendfile on;
    keepalive_timeout 65;
    server_tokens off;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Upstream servers
    upstream frontend {
        server frontend:3000;
        keepalive 32;
    }

    upstream api {
        server api:5000;
        keepalive 32;
    }

    # HTTP server - Behavior depends on SSL mode
    server {
        listen 80;
        server_name _;

        # Health check endpoint - always available
        location /health {
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Location for Let's Encrypt challenges
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # Main location block - redirect to HTTPS in SSL mode
        location / {
            if ($ssl_enabled = "true") {
                return 301 https://$host$request_uri;
            }
            
            # Serve content normally for non-SSL mode
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # API endpoints
        location /api/ {
            if ($ssl_enabled = "true") {
                return 301 https://$host$request_uri;
            }
            
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }

    # HTTPS server - Only active in SSL mode
    server {
        listen 443 ssl;
        server_name _;
        http2 on;

        # SSL certificate configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Modern SSL configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!3DES:!MD5:!PSK;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Health check endpoint
        location /health {
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # API endpoints - proxy to Flask backend
        location /api/ {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Frontend application - proxy to Nuxt frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }
}
EOF
}

# Function to check if port is available
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -i :$port &> /dev/null; then
        print_message "$YELLOW" "⚠️  Port $port is already in use by another process"
        print_message "$BLUE" "   Checking if it's our $service_name service..."
        
        # Check if it's our service by looking for specific processes
        if pgrep -f "$service_name" &> /dev/null; then
            print_message "$GREEN" "   Found existing $service_name process"
            return 1 # Port is used by our service
        else
            print_message "$RED" "   Port $port is used by a different service"
            return 2 # Port is used by different service
        fi
    fi
    return 0 # Port is available
}

# Function to stop local development services
stop_local_services() {
    print_message "$BLUE" "🛑 Stopping local development services..."
    
    # Stop API server
    if [[ -f "logs/api.pid" ]]; then
        local api_pid=$(cat logs/api.pid)
        if kill -0 $api_pid 2>/dev/null; then
            kill $api_pid
            print_message "$GREEN" "✅ Stopped API server (PID: $api_pid)"
        fi
        rm -f logs/api.pid
    fi
    
    # Stop frontend server
    if [[ -f "logs/frontend.pid" ]]; then
        local frontend_pid=$(cat logs/frontend.pid)
        if kill -0 $frontend_pid 2>/dev/null; then
            kill $frontend_pid
            print_message "$GREEN" "✅ Stopped frontend server (PID: $frontend_pid)"
        fi
        rm -f logs/frontend.pid
    fi
    
    # Kill any remaining processes
    pkill -f "python.*api.py" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "nuxt" 2>/dev/null || true
    
    print_message "$GREEN" "✅ All local development services stopped"
}

# Function to ensure databases exist and run migrations
ensure_local_databases() {
    print_message "$BLUE" "🗄️  Ensuring Docker-compatible database setup..."
    
    # Create directories to match Docker volume structure
    mkdir -p "./arrow_scraper/databases"
    mkdir -p "./logs"
    
    # Use Docker-compatible database paths (matching production)
    export ARROW_DATABASE_PATH="$SCRIPT_DIR/arrow_scraper/databases/arrow_database.db"
    
    # Always use unified database architecture for dev mode
    print_message "$GREEN" "✅ Using unified database architecture (Docker-compatible)"
    export USER_DATABASE_PATH="$SCRIPT_DIR/arrow_scraper/databases/arrow_database.db"
    
    # Check if the unified database exists
    if [[ ! -f "$SCRIPT_DIR/arrow_scraper/databases/arrow_database.db" ]]; then
        print_message "$YELLOW" "⚠️  Unified database not found, checking for migration source..."
        
        # Check if old databases exist in ./databases/ and migrate them
        if [[ -f "$SCRIPT_DIR/databases/arrow_database.db" ]]; then
            print_message "$BLUE" "🔄 Copying arrow database from ./databases/ to Docker-compatible location..."
            cp "$SCRIPT_DIR/databases/arrow_database.db" "$SCRIPT_DIR/arrow_scraper/databases/arrow_database.db"
        fi
    fi
    
    # Verify unified database has user tables (post-consolidation check)
    if [[ -f "$SCRIPT_DIR/arrow_scraper/databases/arrow_database.db" ]]; then
        if sqlite3 "$SCRIPT_DIR/arrow_scraper/databases/arrow_database.db" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='users';" 2>/dev/null | grep -q "1"; then
            print_message "$GREEN" "✅ Unified database architecture confirmed (user tables present)"
        else
            print_message "$YELLOW" "⚠️  Database consolidation may be needed (user tables missing)"
        fi
    fi
    
    # Run database migrations for local development
    if [[ -f "arrow_scraper/run_migrations.py" ]]; then
        cd arrow_scraper
        print_message "$BLUE" "🔄 Running database migrations with Docker-compatible paths..."
        
        # Try to run migrations
        if command -v python3 &> /dev/null; then
            python3 run_migrations.py --status-only &>/dev/null || true
            if python3 run_migrations.py; then
                print_message "$GREEN" "✅ Database migrations completed"
            else
                print_message "$YELLOW" "⚠️  Warning: Some migrations may have failed"
            fi
        else
            print_message "$YELLOW" "⚠️  Python 3 not available for migrations"
        fi
        
        cd "$SCRIPT_DIR"
    fi
}

# Function to start local development servers
start_local_development() {
    # Stop any existing services
    stop_local_services
    
    # Ensure databases exist
    ensure_local_databases
    
    # Configuration
    local API_PORT=${API_PORT:-5000}
    local FRONTEND_PORT=${FRONTEND_PORT:-3000}
    
    # Check ports
    check_port $API_PORT "api"
    local api_port_status=$?
    
    check_port $FRONTEND_PORT "frontend"
    local frontend_port_status=$?
    
    # Start API server if needed
    if [[ $api_port_status -eq 0 ]] || [[ $api_port_status -eq 2 ]]; then
        print_message "$BLUE" "🚀 Starting Flask API server..."
        
        cd arrow_scraper
        
        # Check if virtual environment exists and activate it
        if [[ -d "venv" ]]; then
            print_message "$BLUE" "   Activating Python virtual environment..."
            source venv/bin/activate
        else
            print_message "$YELLOW" "   No virtual environment found, using system Python"
        fi
        
        # Start API in background
        python3 api.py > ../logs/api.log 2>&1 &
        local api_pid=$!
        echo $api_pid > ../logs/api.pid
        
        # Wait a moment and check if it started successfully
        sleep 2
        if kill -0 $api_pid 2>/dev/null; then
            print_message "$GREEN" "✅ Flask API server started (PID: $api_pid, Port: $API_PORT)"
        else
            print_message "$RED" "❌ Failed to start Flask API server"
            print_message "$BLUE" "   Check logs/api.log for details"
            cd "$SCRIPT_DIR"
            return 1
        fi
        
        cd "$SCRIPT_DIR"
    else
        print_message "$GREEN" "✅ API server already running on port $API_PORT"
    fi
    
    # Start frontend server if needed
    if [[ $frontend_port_status -eq 0 ]] || [[ $frontend_port_status -eq 2 ]]; then
        print_message "$BLUE" "🚀 Starting Nuxt 3 frontend server..."
        
        cd frontend
        
        # Check if node_modules exists
        if [[ ! -d "node_modules" ]]; then
            print_message "$BLUE" "   Installing frontend dependencies..."
            npm install
        fi
        
        # Start frontend in background
        npm run dev > ../logs/frontend.log 2>&1 &
        local frontend_pid=$!
        echo $frontend_pid > ../logs/frontend.pid
        
        # Wait a moment and check if it started successfully
        sleep 3
        if kill -0 $frontend_pid 2>/dev/null; then
            print_message "$GREEN" "✅ Nuxt 3 frontend server started (PID: $frontend_pid, Port: $FRONTEND_PORT)"
        else
            print_message "$RED" "❌ Failed to start Nuxt 3 frontend server"
            print_message "$BLUE" "   Check logs/frontend.log for details"
            cd "$SCRIPT_DIR"
            return 1
        fi
        
        cd "$SCRIPT_DIR"
    else
        print_message "$GREEN" "✅ Frontend server already running on port $FRONTEND_PORT"
    fi
    
    # Show status and URLs
    print_message "$GREEN" "\n✅ Local development servers are running!"
    print_message "$BLUE" "\n🌐 Access URLs:"
    echo "  Frontend: http://localhost:$FRONTEND_PORT"
    echo "  API: http://localhost:$API_PORT/api"
    echo "  Health: http://localhost:$API_PORT/api/health"
    
    print_message "$BLUE" "\n📝 Log Files:"
    echo "  API logs: tail -f logs/api.log"
    echo "  Frontend logs: tail -f logs/frontend.log"
    
    print_message "$BLUE" "\n🛑 Stop Services:"
    echo "  ./start-unified.sh dev stop"
    
    # Handle stop command if provided as second argument
    if [[ "${2:-}" == "stop" ]]; then
        stop_local_services
        return 0
    fi
    
    print_message "$GREEN" "\n✅ Development servers started successfully!"
    print_message "$BLUE" "   Servers are running in the background"
}

# Main execution
main() {
    print_message "$GREEN" "🏹 ArrowTuner Unified Startup Script"
    print_message "$GREEN" "===================================="
    
    # Check prerequisites
    check_prerequisites
    
    # Setup environment
    setup_environment
    
    # Ensure nginx config exists
    ensure_nginx_config
    
    # Clean up old setup
    cleanup_old_setup
    
    # Ensure unified databases
    ensure_unified_databases
    
    # Start services
    start_services
    
    # Show status
    show_status
    
    print_message "$GREEN" "\n✅ ArrowTuner platform is running!"
}

# Run main function
main "$@"