#!/bin/bash

# Production SSL Deployment - Fast, reliable deployment with SSL certificates
# Automatically detects and configures SSL certificates for production
# 
# Usage: ./deploy-production-ssl.sh [domain] [options]
# Options:
#   --rebuild-database    Rebuild entire database (arrows + components)
#   --rebuild-arrows      Rebuild only arrow database
#   --rebuild-components  Rebuild only components database
#   --help               Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
DOMAIN=""
REBUILD_DATABASE=false
REBUILD_ARROWS=false
REBUILD_COMPONENTS=false
REBUILD_USERS=false

for arg in "$@"; do
    case $arg in
        --rebuild-database)
            REBUILD_DATABASE=true
            ;;
        --rebuild-arrows)
            REBUILD_ARROWS=true
            ;;
        --rebuild-components)
            REBUILD_COMPONENTS=true
            ;;
        --rebuild-users)
            REBUILD_USERS=true
            ;;
        --help)
            echo "Production SSL Deployment Script"
            echo ""
            echo "Usage: ./deploy-production-ssl.sh [domain] [options]"
            echo ""
            echo "Arguments:"
            echo "  domain                Domain name (default: archerytool.online)"
            echo ""
            echo "Options:"
            echo "  --rebuild-database    Rebuild entire database (arrows + components + users)"
            echo "  --rebuild-arrows      Rebuild only arrow database from JSON files"
            echo "  --rebuild-components  Rebuild only components database from JSON files"
            echo "  --rebuild-users       Rebuild only user database (WARNING: deletes all users)"
            echo "  --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./deploy-production-ssl.sh                     # Deploy only"
            echo "  ./deploy-production-ssl.sh archerytool.online  # Deploy with custom domain"
            echo "  ./deploy-production-ssl.sh --rebuild-database  # Deploy + rebuild all data"
            echo "  ./deploy-production-ssl.sh mysite.com --rebuild-arrows  # Custom domain + arrows only"
            echo "  ./deploy-production-ssl.sh --rebuild-users     # Deploy + reset user database"
            exit 0
            ;;
        --*)
            echo "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
        *)
            if [[ "$arg" != *.* ]] && [[ "$DOMAIN" == "" ]]; then
                # Assume it's a domain if it contains dots and no domain set yet
                DOMAIN="$arg"
            elif [[ "$DOMAIN" == "" ]]; then
                DOMAIN="$arg"
            fi
            ;;
    esac
done

# Set default domain if not provided
DOMAIN="${DOMAIN:-archerytool.online}"

echo -e "${BLUE}🚀 Production SSL Deployment${NC}"
echo -e "${BLUE}=============================${NC}"
echo -e "${BLUE}Domain: $DOMAIN${NC}"

# Show what operations will be performed
if [ "$REBUILD_DATABASE" = true ]; then
    echo -e "${BLUE}🔄 Full database rebuild enabled (arrows + components + users)${NC}"
elif [ "$REBUILD_ARROWS" = true ] || [ "$REBUILD_COMPONENTS" = true ] || [ "$REBUILD_USERS" = true ]; then
    echo -e "${BLUE}🔄 Selective database rebuild enabled:${NC}"
    [ "$REBUILD_ARROWS" = true ] && echo -e "${BLUE}  - Arrow database${NC}"
    [ "$REBUILD_COMPONENTS" = true ] && echo -e "${BLUE}  - Components database${NC}"
    [ "$REBUILD_USERS" = true ] && echo -e "${BLUE}  - User database${NC}"
else
    echo -e "${BLUE}⚡ Fast deployment mode (no database rebuild)${NC}"
fi
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Check for SSL certificates
echo -e "${BLUE}🔍 Checking SSL certificates...${NC}"

SSL_CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
LOCAL_SSL_PATH="./deploy/ssl"

if [ -f "$SSL_CERT_PATH/fullchain.pem" ] && [ -f "$SSL_CERT_PATH/privkey.pem" ]; then
    echo -e "${GREEN}✅ SSL certificates found in $SSL_CERT_PATH${NC}"
    
    # Copy certificates to local SSL directory
    echo -e "${BLUE}📋 Copying SSL certificates...${NC}"
    sudo mkdir -p "$LOCAL_SSL_PATH"
    sudo cp "$SSL_CERT_PATH/fullchain.pem" "$LOCAL_SSL_PATH/"
    sudo cp "$SSL_CERT_PATH/privkey.pem" "$LOCAL_SSL_PATH/"
    sudo chown -R $USER:$USER "$LOCAL_SSL_PATH"
    sudo chmod 644 "$LOCAL_SSL_PATH"/*.pem
    
    print_status "SSL certificates copied to local directory"
    USE_SSL=true
    
elif [ -f "$LOCAL_SSL_PATH/fullchain.pem" ] && [ -f "$LOCAL_SSL_PATH/privkey.pem" ]; then
    echo -e "${GREEN}✅ SSL certificates found in local directory${NC}"
    USE_SSL=true
    
else
    print_error "No SSL certificates found!"
    echo -e "${BLUE}SSL certificates are required for production deployment.${NC}"
    echo -e "${BLUE}Please run one of the following:${NC}"
    echo ""
    echo -e "${YELLOW}Option 1: Generate certificates with Certbot${NC}"
    echo -e "${BLUE}  sudo certbot certonly --standalone -d $DOMAIN${NC}"
    echo ""
    echo -e "${YELLOW}Option 2: Use existing certificates${NC}"
    echo -e "${BLUE}  sudo mkdir -p $LOCAL_SSL_PATH${NC}"
    echo -e "${BLUE}  sudo cp /path/to/your/fullchain.pem $LOCAL_SSL_PATH/${NC}"
    echo -e "${BLUE}  sudo cp /path/to/your/privkey.pem $LOCAL_SSL_PATH/${NC}"
    echo -e "${BLUE}  sudo chown -R $USER:$USER $LOCAL_SSL_PATH${NC}"
    echo ""
    echo -e "${YELLOW}Option 3: Use HTTP-only for testing${NC}"
    echo -e "${BLUE}  ./quick-deploy.sh${NC}"
    echo ""
    exit 1
fi

# Step 2: Database operations (only if requested)
if [ "$REBUILD_DATABASE" = true ] || [ "$REBUILD_ARROWS" = true ] || [ "$REBUILD_COMPONENTS" = true ] || [ "$REBUILD_USERS" = true ]; then
    if [ "$REBUILD_DATABASE" = true ]; then
        echo -e "${BLUE}📦 Rebuilding entire database (arrows + components + users)...${NC}"
        ./production-import-only.sh
        
        # Also rebuild user database if full rebuild requested
        cd arrow_scraper
        echo -e "${BLUE}👥 Rebuilding user database...${NC}"
        if [ -f "user_data.db" ]; then
            rm user_data.db
            print_status "User database cleared"
        fi
        python3 -c "from user_database import UserDatabase; UserDatabase()" 
        print_status "User database reinitialized"
        cd ..
        
        print_status "Complete database rebuilt"
    else
        # Navigate to scraper directory for selective rebuilds
        cd arrow_scraper
        
        if [ "$REBUILD_ARROWS" = true ]; then
            echo -e "${BLUE}🏹 Rebuilding arrow database only...${NC}"
            if python3 database_import_manager.py --import-all --force; then
                print_status "Arrow database rebuilt"
            else
                print_error "Arrow database rebuild failed"
                cd ..
                exit 1
            fi
        fi
        
        if [ "$REBUILD_COMPONENTS" = true ]; then
            echo -e "${BLUE}🧩 Rebuilding components database only...${NC}"
            if python3 component_importer.py --force; then
                print_status "Components database rebuilt"
            else
                print_warning "Components database rebuild failed (continuing)"
            fi
        fi
        
        if [ "$REBUILD_USERS" = true ]; then
            echo -e "${BLUE}👥 Rebuilding user database only...${NC}"
            echo -e "${YELLOW}⚠️  WARNING: This will delete all user accounts, bow setups, and sessions!${NC}"
            read -p "Are you sure you want to continue? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                if [ -f "user_data.db" ]; then
                    rm user_data.db
                    print_status "User database cleared"
                fi
                python3 -c "from user_database import UserDatabase; UserDatabase()" 
                print_status "User database reinitialized"
            else
                print_warning "User database rebuild cancelled"
            fi
        fi
        
        cd ..
    fi
else
    echo -e "${BLUE}⚡ Skipping database rebuild (use --rebuild-database to rebuild)${NC}"
    print_status "Using existing databases"
fi

# Step 3: Update environment for HTTPS
echo -e "${BLUE}🔧 Configuring for HTTPS deployment...${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found, creating basic configuration"
    cat > .env << EOF
# Production Configuration
SECRET_KEY=change-this-secret-key-in-production
GOOGLE_CLIENT_SECRET=your-google-client-secret
NUXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_REDIRECT_URI=https://$DOMAIN
DOMAIN_NAME=$DOMAIN
SSL_EMAIL=admin@$DOMAIN
EOF
fi

# Update redirect URI in .env if needed
if grep -q "GOOGLE_REDIRECT_URI=" .env; then
    sed -i "s|GOOGLE_REDIRECT_URI=.*|GOOGLE_REDIRECT_URI=https://$DOMAIN|g" .env
else
    echo "GOOGLE_REDIRECT_URI=https://$DOMAIN" >> .env
fi

print_status "Environment configured for HTTPS"

# Step 4: Clean up previous deployment
echo -e "${BLUE}🧹 Cleaning up previous deployment...${NC}"
docker-compose -f docker-compose.minimal-ssl.yml down --remove-orphans 2>/dev/null || true
docker-compose down --remove-orphans 2>/dev/null || true
print_status "Cleanup completed"

# Step 5: Deploy with SSL
echo -e "${BLUE}🚀 Starting SSL deployment...${NC}"
docker-compose -f docker-compose.minimal-ssl.yml up -d --build

print_status "Services started with SSL"

# Step 6: Wait for services
echo -e "${BLUE}⏳ Waiting for services to start (60s)...${NC}"
sleep 60

# Step 7: Show status
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose -f docker-compose.minimal-ssl.yml ps

# Step 8: Health checks
echo -e "${BLUE}🔍 SSL health checks...${NC}"

# Check HTTP redirect
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null || echo "000")
if [ "$HTTP_STATUS" = "301" ] || [ "$HTTP_STATUS" = "302" ]; then
    print_status "HTTP redirect working (HTTP $HTTP_STATUS)"
else
    print_warning "HTTP redirect not working (HTTP $HTTP_STATUS)"
fi

# Check HTTPS
HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN -k 2>/dev/null || echo "000")
if [ "$HTTPS_STATUS" = "200" ]; then
    print_status "HTTPS site responding (HTTP $HTTPS_STATUS)"
else
    print_warning "HTTPS site not ready yet (HTTP $HTTPS_STATUS)"
fi

# Check API
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/api/health -k 2>/dev/null || echo "000")
if [ "$API_STATUS" = "200" ]; then
    print_status "HTTPS API responding (HTTP $API_STATUS)"
else
    print_warning "HTTPS API not ready yet (HTTP $API_STATUS)"
fi

echo -e "${GREEN}🎉 Production SSL deployment completed!${NC}"
echo -e "${BLUE}=============================${NC}"
echo -e "${GREEN}Access URLs:${NC}"
echo -e "${BLUE}  🌐 Website: https://$DOMAIN${NC}"
echo -e "${BLUE}  🔌 API: https://$DOMAIN/api${NC}"
echo -e "${BLUE}  💚 Health: https://$DOMAIN/api/health${NC}"
echo ""
echo -e "${YELLOW}Management Commands:${NC}"
echo -e "${YELLOW}  📊 Status: docker-compose -f docker-compose.minimal-ssl.yml ps${NC}"
echo -e "${YELLOW}  📋 Logs: docker-compose -f docker-compose.minimal-ssl.yml logs -f${NC}"
echo -e "${YELLOW}  🛑 Stop: docker-compose -f docker-compose.minimal-ssl.yml down${NC}"
echo ""

# Certificate info
echo -e "${BLUE}📋 SSL Certificate Info:${NC}"
if [ -f "$LOCAL_SSL_PATH/fullchain.pem" ]; then
    CERT_EXPIRY=$(openssl x509 -in "$LOCAL_SSL_PATH/fullchain.pem" -noout -dates | grep notAfter | cut -d= -f2)
    echo -e "${BLUE}  Expires: $CERT_EXPIRY${NC}"
fi

if [ "$HTTPS_STATUS" != "200" ] || [ "$API_STATUS" != "200" ]; then
    echo ""
    print_warning "Some services may still be starting up. Wait a moment and check again."
    echo -e "${BLUE}Manual check: curl -k https://$DOMAIN/api/health${NC}"
    echo ""
    echo -e "${YELLOW}If issues persist:${NC}"
    echo -e "${YELLOW}  1. Check logs: docker-compose -f docker-compose.minimal-ssl.yml logs${NC}"
    echo -e "${YELLOW}  2. Verify DNS: dig $DOMAIN${NC}"
    echo -e "${YELLOW}  3. Test certificates: openssl s_client -connect $DOMAIN:443${NC}"
fi