#!/bin/bash
#
# Fix Production Unified Setup
# Temporary fix to get production running with unified architecture
#

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_message "$GREEN" "🔧 Fixing Production Unified Setup"
print_message "$GREEN" "================================="

# Stop services
print_message "$BLUE" "⏹️  Stopping services..."
docker-compose -f docker-compose.unified.yml down

# Create a temporary docker-compose override for production
print_message "$BLUE" "📝 Creating production override..."
cat > docker-compose.production-override.yml << 'EOF'
# Production Override for Unified Architecture
# This handles the existing volume structure in production

services:
  api:
    environment:
      # Override database paths to use existing locations
      - ARROW_DATABASE_PATH=/app/arrow_database.db
      - USER_DATABASE_PATH=/app/user_data/user_data.db
    volumes:
      # Map existing data structure
      - ./.env:/app/.env:ro
      - arrowtuner-userdata:/app/user_data
      - arrowtuner-arrowdata:/app/arrow_data
      - arrowtuner-logs:/app/logs
      - ./arrow_scraper/data:/app/data:ro
      # Add the arrow database from host
      - ./arrow_scraper/arrow_database.db:/app/arrow_database.db:ro

  frontend:
    # No changes needed

  nginx:
    # No changes needed

  db-init:
    # Skip database init in production
    entrypoint: ["echo", "Skipping database init in production"]
    command: [""]

  db-backup:
    environment:
      - ARROW_DATABASE_PATH=/app/arrow_database.db
      - USER_DATABASE_PATH=/app/user_data/user_data.db

volumes:
  # Use existing volume names
  arrowtuner-userdata:
    external: true
    name: arrowtuner2_arrowtuner-userdata
  
  arrowtuner-arrowdata:
    driver: local
  
  arrowtuner-databases:
    driver: local
  
  arrowtuner-logs:
    driver: local
  
  arrowtuner-backups:
    driver: local
EOF

# Check if arrow database exists locally
if [[ -f "arrow_scraper/arrow_database.db" ]]; then
    print_message "$GREEN" "✅ Found local arrow database"
else
    print_message "$YELLOW" "⚠️  No local arrow database found"
fi

# Start with override
print_message "$BLUE" "🚀 Starting services with production override..."
docker-compose -f docker-compose.unified.yml -f docker-compose.production-override.yml up -d

# Wait for services
print_message "$BLUE" "⏳ Waiting for services to start..."
sleep 10

# Check status
print_message "$BLUE" "📊 Checking service status..."
docker-compose -f docker-compose.unified.yml -f docker-compose.production-override.yml ps

print_message "$GREEN" "\n✅ Production fix applied!"
print_message "$YELLOW" "\nNote: This is a temporary fix. The proper solution is to:"
print_message "$YELLOW" "1. Backup your data"
print_message "$YELLOW" "2. Clean up old volumes"
print_message "$YELLOW" "3. Start fresh with unified architecture"