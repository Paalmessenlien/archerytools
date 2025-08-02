#!/bin/bash

# Quick Production Deploy - Uses latest configurations
# For use after database rebuild or when containers need refresh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DOMAIN=""
USE_SSL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --domain)
            DOMAIN="$2"
            USE_SSL=true
            shift 2
            ;;
        --ssl)
            USE_SSL=true
            shift
            ;;
        --http)
            USE_SSL=false
            shift
            ;;
        *)
            if [ -n "$1" ] && [ "${1:0:1}" != "-" ]; then
                DOMAIN="$1"
                USE_SSL=true
            fi
            shift
            ;;
    esac
done

echo -e "${BLUE}🚀 Quick Production Deploy${NC}"
echo -e "${BLUE}=========================${NC}"

if [ "$USE_SSL" = true ] && [ -n "$DOMAIN" ]; then
    echo -e "${GREEN}Deploying with SSL for domain: $DOMAIN${NC}"
elif [ "$USE_SSL" = true ]; then
    echo -e "${YELLOW}SSL mode enabled but no domain specified${NC}"
    read -p "Enter domain name: " DOMAIN
else
    echo -e "${YELLOW}Deploying in HTTP-only mode${NC}"
fi

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_step() {
    echo -e "${BLUE}$1${NC}"
}

# Step 1: Clean up existing containers
print_step "🧹 Step 1: Cleaning up existing containers..."
docker-compose down 2>/dev/null || true
docker-compose -f docker-compose.fresh.yml down 2>/dev/null || true
docker-compose -f docker-compose.ssl.yml down 2>/dev/null || true
docker-compose -f docker-compose.enhanced-ssl.yml down 2>/dev/null || true

# Remove containers that might be stuck
docker rm -f fresh-archery-api fresh-archery-frontend fresh-archery-nginx 2>/dev/null || true
docker rm -f archerytools_archery-api archerytools_archery-frontend archerytools_nginx 2>/dev/null || true

print_status "Containers cleaned up"

# Step 2: Update environment configuration
print_step "⚙️ Step 2: Configuring environment..."

if [ "$USE_SSL" = true ] && [ -n "$DOMAIN" ]; then
    # Update .env for SSL deployment
    if [ -f ".env" ]; then
        # Backup current .env
        cp .env .env.backup
        
        # Update URLs for SSL
        sed -i "s|GOOGLE_REDIRECT_URI=.*|GOOGLE_REDIRECT_URI=https://$DOMAIN|g" .env
        sed -i "s|NUXT_PUBLIC_API_BASE=.*|NUXT_PUBLIC_API_BASE=https://$DOMAIN/api|g" .env
        sed -i "s|NODE_ENV=.*|NODE_ENV=production|g" .env
        
        print_status "Environment configured for SSL ($DOMAIN)"
    else
        print_warning ".env file not found - creating basic configuration"
    fi
fi

# Step 3: Choose deployment method
print_step "🚀 Step 3: Starting deployment..."

if [ "$USE_SSL" = true ] && [ -n "$DOMAIN" ]; then
    echo -e "${BLUE}Using enhanced SSL deployment...${NC}"
    
    # Check if enhanced deployment script exists
    if [ -f "./deploy-enhanced.sh" ]; then
        # Use enhanced deployment with SSL
        ./deploy-enhanced.sh docker-compose.enhanced-ssl.yml
    elif [ -f "docker-compose.enhanced-ssl.yml" ]; then
        # Direct enhanced SSL deployment
        docker-compose -f docker-compose.enhanced-ssl.yml up -d --build
    elif [ -f "docker-compose.ssl.yml" ]; then
        # Fallback to basic SSL
        docker-compose -f docker-compose.ssl.yml up -d --build
    else
        print_warning "No SSL configuration found, falling back to HTTP"
        docker-compose -f docker-compose.fresh.yml up -d --build
    fi
else
    echo -e "${BLUE}Using HTTP deployment...${NC}"
    
    # Use fresh deployment to avoid conflicts
    if [ -f "./deploy-fresh.sh" ]; then
        ./deploy-fresh.sh
    else
        docker-compose -f docker-compose.fresh.yml up -d --build
    fi
fi

# Step 4: Wait for services
print_step "⏳ Step 4: Waiting for services to start..."
echo -e "${YELLOW}Allowing 60 seconds for container startup...${NC}"
sleep 60

# Step 5: Health checks
print_step "🔍 Step 5: Health verification..."

# Determine URLs based on deployment type
if [ "$USE_SSL" = true ] && [ -n "$DOMAIN" ]; then
    API_URL="https://$DOMAIN/api/simple-health"
    FRONTEND_URL="https://$DOMAIN"
    MAIN_URL="https://$DOMAIN"
else
    API_URL="http://localhost:5000/api/simple-health"
    FRONTEND_URL="http://localhost:3000"
    MAIN_URL="http://localhost"
fi

# Check API
echo -e "${YELLOW}Checking API at: $API_URL${NC}"
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL" 2>/dev/null || echo "000")
if [ "$API_STATUS" = "200" ]; then
    print_status "API is healthy (HTTP $API_STATUS)"
else
    print_warning "API not ready (HTTP $API_STATUS)"
fi

# Check frontend
echo -e "${YELLOW}Checking frontend at: $FRONTEND_URL${NC}"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo "000")
if [ "$FRONTEND_STATUS" = "200" ]; then
    print_status "Frontend is healthy (HTTP $FRONTEND_STATUS)"
else
    print_warning "Frontend not ready (HTTP $FRONTEND_STATUS)"
fi

# Check main site (nginx)
echo -e "${YELLOW}Checking main site at: $MAIN_URL${NC}"
MAIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$MAIN_URL" 2>/dev/null || echo "000")
if [ "$MAIN_STATUS" = "200" ]; then
    print_status "Main site is healthy (HTTP $MAIN_STATUS)"
else
    print_warning "Main site not ready (HTTP $MAIN_STATUS)"
fi

# Step 6: Show container status
print_step "📊 Step 6: Container status..."
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Step 7: Final summary
echo ""
echo -e "${GREEN}🎉 Quick deployment completed!${NC}"
echo -e "${BLUE}=========================${NC}"

echo -e "${GREEN}📊 Health Status:${NC}"
echo -e "${BLUE}  API: HTTP $API_STATUS${NC}"
echo -e "${BLUE}  Frontend: HTTP $FRONTEND_STATUS${NC}"
echo -e "${BLUE}  Main Site: HTTP $MAIN_STATUS${NC}"

echo -e "${GREEN}🌐 Access URLs:${NC}"
if [ "$USE_SSL" = true ] && [ -n "$DOMAIN" ]; then
    echo -e "${BLUE}  Main: https://$DOMAIN${NC}"
    echo -e "${BLUE}  API: https://$DOMAIN/api${NC}"
    echo -e "${BLUE}  Database: https://$DOMAIN/database${NC}"
else
    echo -e "${BLUE}  Main: http://localhost${NC}"
    echo -e "${BLUE}  API: http://localhost:5000${NC}"
    echo -e "${BLUE}  Frontend: http://localhost:3000${NC}"
fi

echo -e "${GREEN}🔧 Management:${NC}"
if [ "$USE_SSL" = true ] && [ -n "$DOMAIN" ]; then
    echo -e "${YELLOW}  Logs: docker-compose -f docker-compose.enhanced-ssl.yml logs -f${NC}"
    echo -e "${YELLOW}  Restart: docker-compose -f docker-compose.enhanced-ssl.yml restart${NC}"
    echo -e "${YELLOW}  Stop: docker-compose -f docker-compose.enhanced-ssl.yml down${NC}"
else
    echo -e "${YELLOW}  Logs: docker-compose -f docker-compose.fresh.yml logs -f${NC}"
    echo -e "${YELLOW}  Restart: docker-compose -f docker-compose.fresh.yml restart${NC}"
    echo -e "${YELLOW}  Stop: docker-compose -f docker-compose.fresh.yml down${NC}"
fi

if [ "$API_STATUS" != "200" ] || [ "$FRONTEND_STATUS" != "200" ] || [ "$MAIN_STATUS" != "200" ]; then
    echo ""
    print_warning "Some services are not responding properly."
    echo -e "${BLUE}Troubleshooting:${NC}"
    echo -e "${YELLOW}  1. Wait 2-3 more minutes for full startup${NC}"
    echo -e "${YELLOW}  2. Check logs: docker-compose logs${NC}"
    echo -e "${YELLOW}  3. Verify databases: ls -la arrow_scraper/*.db${NC}"
    echo -e "${YELLOW}  4. Test individual services:${NC}"
    echo -e "${YELLOW}     curl $API_URL${NC}"
    echo -e "${YELLOW}     curl $FRONTEND_URL${NC}"
fi

echo ""
echo -e "${GREEN}✨ Production deployment ready!${NC}"