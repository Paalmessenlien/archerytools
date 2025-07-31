#!/bin/bash

# Check SSL and Deploy Script
# Automatically chooses the right nginx configuration based on SSL certificate availability

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

COMPOSE_FILE="${1:-docker-compose.enhanced-ssl.yml}"

echo -e "${BLUE}🔍 Checking SSL certificate availability...${NC}"

# Check if SSL certificates exist
SSL_CERT_PATH="/etc/letsencrypt/live"
LOCAL_SSL_PATH="./deploy/ssl"

if [ -f "/etc/letsencrypt/live/archerytool.online/fullchain.pem" ] && [ -f "/etc/letsencrypt/live/archerytool.online/privkey.pem" ]; then
    echo -e "${GREEN}✅ SSL certificates found in /etc/letsencrypt/live/${NC}"
    
    # Copy certificates to local SSL directory
    sudo mkdir -p "$LOCAL_SSL_PATH"
    sudo cp "/etc/letsencrypt/live/archerytool.online/fullchain.pem" "$LOCAL_SSL_PATH/"
    sudo cp "/etc/letsencrypt/live/archerytool.online/privkey.pem" "$LOCAL_SSL_PATH/"
    sudo chown $USER:$USER "$LOCAL_SSL_PATH"/*.pem
    
    # Update docker-compose to use SSL configuration
    echo -e "${BLUE}🔧 Configuring for HTTPS deployment...${NC}"
    sed -i 's|nginx.http-only.conf|nginx.ssl.conf|g' "$COMPOSE_FILE"
    
    echo -e "${GREEN}✅ HTTPS configuration enabled${NC}"
    
elif [ -f "$LOCAL_SSL_PATH/fullchain.pem" ] && [ -f "$LOCAL_SSL_PATH/privkey.pem" ]; then
    echo -e "${GREEN}✅ SSL certificates found in local directory${NC}"
    
    # Update docker-compose to use SSL configuration
    echo -e "${BLUE}🔧 Configuring for HTTPS deployment...${NC}"
    sed -i 's|nginx.http-only.conf|nginx.ssl.conf|g' "$COMPOSE_FILE"
    
    echo -e "${GREEN}✅ HTTPS configuration enabled${NC}"
    
else
    echo -e "${YELLOW}⚠️  No SSL certificates found${NC}"
    echo -e "${YELLOW}Using HTTP-only configuration for testing${NC}"
    
    # Update docker-compose to use HTTP-only configuration
    sed -i 's|nginx.ssl.conf|nginx.http-only.conf|g' "$COMPOSE_FILE"
    
    echo -e "${BLUE}ℹ️  To enable HTTPS later:${NC}"
    echo -e "${BLUE}1. Run: sudo certbot certonly --standalone -d archerytool.online${NC}"
    echo -e "${BLUE}2. Re-run this script${NC}"
fi

echo -e "${BLUE}🚀 Deploying with appropriate configuration...${NC}"

# Import data first
echo -e "${BLUE}📦 Importing arrow data...${NC}"
./production-import-only.sh

# Deploy
echo -e "${BLUE}🐳 Starting Docker deployment...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d --build

echo -e "${GREEN}✅ Deployment completed!${NC}"
echo -e "${BLUE}Access URLs:${NC}"
if grep -q "nginx.ssl.conf" "$COMPOSE_FILE"; then
    echo -e "${GREEN}  HTTPS: https://archerytool.online${NC}"
    echo -e "${BLUE}  HTTP: http://archerytool.online (redirects to HTTPS)${NC}"
else
    echo -e "${BLUE}  HTTP: http://localhost${NC}"
fi