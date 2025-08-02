#!/bin/bash

# Complete Production Reset Script
# This script performs a full production environment reset:
# 1. Complete Docker cleanup
# 2. Database removal and rebuild
# 3. Fresh data import
# 4. Clean deployment with SSL support

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🔄 Complete Production Reset${NC}"
echo -e "${PURPLE}=============================${NC}"
echo -e "${YELLOW}This script will:${NC}"
echo -e "${YELLOW}1. Stop and remove all Docker containers${NC}"
echo -e "${YELLOW}2. Remove all Docker images and volumes${NC}"
echo -e "${YELLOW}3. Delete all database files${NC}"
echo -e "${YELLOW}4. Import fresh arrow data${NC}"
echo -e "${YELLOW}5. Deploy with clean configuration${NC}"
echo -e "${YELLOW}6. Set up SSL (if domain provided)${NC}"
echo ""

# Ask for confirmation
read -p "Are you sure you want to COMPLETELY RESET production? (type 'RESET' to continue): " confirm
if [ "$confirm" != "RESET" ]; then
    echo "Cancelled."
    exit 1
fi

# Optional domain for SSL
DOMAIN=""
if [ -n "$1" ]; then
    DOMAIN="$1"
    echo -e "${BLUE}🌐 Domain provided: $DOMAIN${NC}"
    echo -e "${BLUE}Will set up SSL after deployment${NC}"
fi

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

print_step() {
    echo -e "${BLUE}$1${NC}"
}

# Step 1: Nuclear Docker Cleanup
print_step "🧹 Step 1: Complete Docker cleanup..."
echo -e "${YELLOW}Stopping all containers...${NC}"
docker stop $(docker ps -aq) 2>/dev/null || true

echo -e "${YELLOW}Removing all containers...${NC}"
docker rm -f $(docker ps -aq) 2>/dev/null || true

echo -e "${YELLOW}Removing all images...${NC}"
docker rmi -f $(docker images -aq) 2>/dev/null || true

echo -e "${YELLOW}Removing all volumes...${NC}"
docker volume rm $(docker volume ls -q) 2>/dev/null || true

echo -e "${YELLOW}Removing all networks...${NC}"
docker network rm $(docker network ls -q) 2>/dev/null || true

echo -e "${YELLOW}Cleaning build cache...${NC}"
docker builder prune -a -f 2>/dev/null || true

echo -e "${YELLOW}Final system prune...${NC}"
docker system prune -a -f --volumes 2>/dev/null || true

print_status "Docker completely cleaned"

# Step 2: Database Cleanup
print_step "🗄️ Step 2: Database cleanup..."

# Remove all database files
echo -e "${YELLOW}Removing database files...${NC}"
rm -f arrow_scraper/arrow_database.db
rm -f arrow_scraper/user_data.db
rm -f arrow_scraper/component_database.db
rm -f arrow_scraper/*.db
rm -rf arrow_scraper/logs/*
print_status "All database files removed"

# Step 3: Clean Git State
print_step "📦 Step 3: Ensuring latest code..."
git fetch origin
git reset --hard origin/main
print_status "Latest code pulled"

# Step 4: Import Fresh Arrow Data
print_step "🏹 Step 4: Importing fresh arrow data..."
if [ -f "./production-import-only.sh" ]; then
    ./production-import-only.sh
    print_status "Arrow data imported successfully"
else
    print_warning "production-import-only.sh not found, creating databases from scratch"
fi

# Step 5: Verify Database Creation
print_step "🔍 Step 5: Verifying database creation..."
cd arrow_scraper

# Initialize databases manually if needed
python3 -c "
from arrow_database import ArrowDatabase
from user_database import UserDatabase

print('Creating arrow database...')
arrow_db = ArrowDatabase()
print('Creating user database...')
user_db = UserDatabase()
print('Databases created successfully')
"

ARROW_COUNT=$(python3 -c "
from arrow_database import ArrowDatabase
db = ArrowDatabase()
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM arrows')
print(cursor.fetchone()[0])
conn.close()
" 2>/dev/null || echo "0")

USER_DB_SIZE=$(ls -la user_data.db 2>/dev/null | awk '{print $5}' || echo "0")

echo "   Arrow database: $ARROW_COUNT arrows"
echo "   User database: ${USER_DB_SIZE} bytes"

if [ "$ARROW_COUNT" -gt "100" ]; then
    print_status "Databases created successfully"
else
    print_warning "Database might be incomplete (only $ARROW_COUNT arrows)"
fi

cd ..

# Step 6: Clean Environment Setup
print_step "⚙️ Step 6: Environment configuration..."

# Ensure .env file exists with proper configuration
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env 2>/dev/null || cat > .env << EOF
# API Configuration
SECRET_KEY=production-secret-key-$(date +%s)
DEEPSEEK_API_KEY=your-deepseek-api-key-here
API_PORT=5000

# Frontend Configuration  
FRONTEND_PORT=3000
NODE_ENV=production
NUXT_PUBLIC_API_BASE=http://localhost:5000/api

# Google OAuth
NUXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost
EOF
    print_status ".env file created (update with your values)"
else
    print_status ".env file exists"
fi

# Step 7: Choose Deployment Strategy
print_step "🚀 Step 7: Fresh deployment..."

# Function to deploy with retry logic
deploy_with_retry() {
    local config_file="$1"
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo -e "${YELLOW}Deployment attempt $attempt of $max_attempts...${NC}"
        
        if [ -f "./deploy-enhanced.sh" ]; then
            if ./deploy-enhanced.sh "$config_file"; then
                print_status "Deployment successful on attempt $attempt"
                return 0
            fi
        else
            if docker-compose -f "$config_file" up -d --build; then
                print_status "Deployment successful on attempt $attempt"
                return 0
            fi
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            print_warning "Deployment attempt $attempt failed, retrying in 30 seconds..."
            sleep 30
            
            # Clean up failed containers before retry
            echo -e "${YELLOW}Cleaning up failed containers...${NC}"
            docker-compose -f "$config_file" down 2>/dev/null || true
            sleep 10
        fi
        
        attempt=$((attempt + 1))
    done
    
    print_error "All deployment attempts failed"
    return 1
}

if [ -n "$DOMAIN" ]; then
    echo -e "${BLUE}Deploying with SSL for domain: $DOMAIN${NC}"
    
    # Update environment for SSL
    sed -i "s|GOOGLE_REDIRECT_URI=.*|GOOGLE_REDIRECT_URI=https://$DOMAIN|g" .env
    sed -i "s|NUXT_PUBLIC_API_BASE=.*|NUXT_PUBLIC_API_BASE=https://$DOMAIN/api|g" .env
    
    # Deploy with enhanced SSL configuration and retry logic
    deploy_with_retry "docker-compose.enhanced-ssl.yml"
else
    echo -e "${BLUE}Deploying HTTP-only (no domain provided)${NC}"
    
    # Deploy with retry logic
    if [ -f "docker-compose.fresh.yml" ]; then
        deploy_with_retry "docker-compose.fresh.yml"
    else
        deploy_with_retry "docker-compose.yml"
    fi
fi

# Step 8: Wait for Services with Health Monitoring
print_step "⏳ Step 8: Waiting for services to start..."

# Function to wait for service health with timeout
wait_for_service() {
    local service_name="$1"
    local url="$2"
    local max_wait=300  # 5 minutes
    local wait_time=0
    local check_interval=15
    
    echo -e "${YELLOW}Waiting for $service_name to be healthy...${NC}"
    
    while [ $wait_time -lt $max_wait ]; do
        local status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
        
        if [ "$status" = "200" ]; then
            print_status "$service_name is healthy (HTTP $status) after ${wait_time}s"
            return 0
        fi
        
        echo -e "   ${YELLOW}$service_name not ready (HTTP $status), waiting... (${wait_time}s/${max_wait}s)${NC}"
        sleep $check_interval
        wait_time=$((wait_time + check_interval))
    done
    
    print_warning "$service_name not healthy after ${max_wait}s (HTTP $status)"
    return 1
}

# Step 9: Health Checks with Timeout
print_step "🔍 Step 9: Health verification..."

# Check API health
API_URL="http://localhost:5000/api/simple-health"
if [ -n "$DOMAIN" ]; then
    API_URL="https://$DOMAIN/api/simple-health"
fi

wait_for_service "API" "$API_URL"
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL" 2>/dev/null || echo "000")

# Check database stats
DB_STATS=$(curl -s "$API_URL" 2>/dev/null | grep -o '"arrows":[0-9]*' | cut -d: -f2 || echo "0")
echo "   Database contains: $DB_STATS arrows"

# Check frontend
FRONTEND_URL="http://localhost:3000"
if [ -n "$DOMAIN" ]; then
    FRONTEND_URL="https://$DOMAIN"
fi

wait_for_service "Frontend" "$FRONTEND_URL"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo "000")

# Step 10: SSL Setup (if domain provided)
if [ -n "$DOMAIN" ]; then
    print_step "🔒 Step 10: SSL Certificate setup..."
    
    echo -e "${YELLOW}Setting up SSL certificate for $DOMAIN...${NC}"
    echo -e "${YELLOW}Make sure DNS is pointing to this server before continuing${NC}"
    
    read -p "Is DNS configured for $DOMAIN? (y/N): " dns_ready
    if [ "$dns_ready" = "y" ] || [ "$dns_ready" = "Y" ]; then
        # Attempt SSL certificate generation
        if command -v certbot >/dev/null 2>&1; then
            sudo certbot certonly --standalone -d "$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN" || {
                print_warning "SSL certificate generation failed. You can set it up manually later."
            }
        else
            print_warning "Certbot not installed. Install it for SSL: sudo apt install certbot"
        fi
    else
        print_warning "Configure DNS first, then run: sudo certbot certonly --standalone -d $DOMAIN"
    fi
fi

# Step 11: Final Summary
print_step "🎉 Production reset completed!"
echo -e "${PURPLE}=================================${NC}"
echo -e "${GREEN}Fresh Production Environment Ready!${NC}"
echo -e "${PURPLE}=================================${NC}"

echo -e "${GREEN}📊 System Status:${NC}"
echo -e "${BLUE}  API Status: HTTP $API_STATUS${NC}"
echo -e "${BLUE}  Frontend Status: HTTP $FRONTEND_STATUS${NC}"
echo -e "${BLUE}  Database: $DB_STATS arrows${NC}"

echo -e "${GREEN}🌐 Access URLs:${NC}"
if [ -n "$DOMAIN" ]; then
    echo -e "${BLUE}  Main Site: https://$DOMAIN${NC}"
    echo -e "${BLUE}  API: https://$DOMAIN/api${NC}"
else
    echo -e "${BLUE}  Main Site: http://localhost${NC}"
    echo -e "${BLUE}  API: http://localhost:5000${NC}"
    echo -e "${BLUE}  Frontend: http://localhost:3000${NC}"
fi

echo -e "${GREEN}🔧 Management Commands:${NC}"
if [ -n "$DOMAIN" ]; then
    echo -e "${YELLOW}  View Logs: docker-compose -f docker-compose.enhanced-ssl.yml logs -f${NC}"
    echo -e "${YELLOW}  Restart: docker-compose -f docker-compose.enhanced-ssl.yml restart${NC}"
    echo -e "${YELLOW}  Stop: docker-compose -f docker-compose.enhanced-ssl.yml down${NC}"
else
    echo -e "${YELLOW}  View Logs: docker-compose -f docker-compose.fresh.yml logs -f${NC}"
    echo -e "${YELLOW}  Restart: docker-compose -f docker-compose.fresh.yml restart${NC}"
    echo -e "${YELLOW}  Stop: docker-compose -f docker-compose.fresh.yml down${NC}"
fi

if [ "$API_STATUS" != "200" ] || [ "$FRONTEND_STATUS" != "200" ]; then
    echo ""
    print_warning "Some services may still be starting. Wait a few minutes and check again."
    echo -e "${BLUE}Monitor progress: docker ps${NC}"
fi

echo ""
echo -e "${GREEN}✨ Production environment completely reset and deployed!${NC}"