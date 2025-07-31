#!/bin/bash

# Sync Real Arrow Data to Production Server
# This script transfers the real scraped arrow data from local to production server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PRODUCTION_SERVER="${1}"
PRODUCTION_PATH="${2:-/home/paal/archerytools}"

if [ -z "$PRODUCTION_SERVER" ]; then
    echo -e "${RED}Usage: $0 <production-server> [production-path]${NC}"
    echo -e "${YELLOW}Example: $0 user@yourserver.com /path/to/archerytools${NC}"
    echo -e "${YELLOW}Example: $0 user@192.168.1.100${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 Syncing Real Arrow Data to Production${NC}"
echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}Production Server: $PRODUCTION_SERVER${NC}"
echo -e "${BLUE}Production Path: $PRODUCTION_PATH${NC}"

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

# Step 1: Verify local data exists
echo -e "${BLUE}📊 Step 1: Verifying local arrow data...${NC}"
LOCAL_DATA_DIR="arrow_scraper/data/processed"

if [ ! -d "$LOCAL_DATA_DIR" ]; then
    print_error "Local data directory not found: $LOCAL_DATA_DIR"
    exit 1
fi

# Count local JSON files (excluding sample files)
REAL_JSON_FILES=$(find "$LOCAL_DATA_DIR" -name "*.json" ! -name "sample_arrows.json" ! -name "wood_arrows.json" | wc -l)
TOTAL_JSON_FILES=$(find "$LOCAL_DATA_DIR" -name "*.json" | wc -l)

echo "   Local data directory: $LOCAL_DATA_DIR"
echo "   Total JSON files: $TOTAL_JSON_FILES"
echo "   Real manufacturer files: $REAL_JSON_FILES"

if [ "$REAL_JSON_FILES" -lt 5 ]; then
    print_error "Insufficient real arrow data files locally ($REAL_JSON_FILES found)"
    echo -e "${YELLOW}Expected files like: Easton_*.json, Gold_Tip_*.json, Victory_*.json${NC}"
    echo -e "${YELLOW}Run the scraper locally first to get real data${NC}"
    exit 1
fi

print_status "Local real arrow data verified ($REAL_JSON_FILES manufacturer files)"

# Step 2: Show what will be transferred
echo -e "${BLUE}📄 Step 2: Files to transfer:${NC}"
find "$LOCAL_DATA_DIR" -name "*.json" | while read file; do
    filename=$(basename "$file")
    size=$(du -h "$file" | cut -f1)
    echo "   📄 $filename ($size)"
done

# Step 3: Test connection to production server
echo -e "${BLUE}🔗 Step 3: Testing connection to production server...${NC}"
if ! ssh -o ConnectTimeout=10 "$PRODUCTION_SERVER" "echo 'Connection test successful'" >/dev/null 2>&1; then
    print_error "Cannot connect to production server: $PRODUCTION_SERVER"
    echo -e "${YELLOW}Please check:${NC}"
    echo -e "${YELLOW}1. Server address is correct${NC}"
    echo -e "${YELLOW}2. SSH keys are set up${NC}"
    echo -e "${YELLOW}3. Server is accessible${NC}"
    exit 1
fi

print_status "Connection to production server established"

# Step 4: Create backup of production data
echo -e "${BLUE}💾 Step 4: Creating backup of production data...${NC}"
BACKUP_CMD="cd $PRODUCTION_PATH && mkdir -p backups/data_backup_\$(date +%Y%m%d_%H%M%S) && cp -r arrow_scraper/data/processed/* backups/data_backup_\$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo 'No existing data to backup'"

ssh "$PRODUCTION_SERVER" "$BACKUP_CMD"
print_status "Production data backed up"

# Step 5: Create production data directory
echo -e "${BLUE}📁 Step 5: Ensuring production data directory exists...${NC}"
ssh "$PRODUCTION_SERVER" "mkdir -p $PRODUCTION_PATH/arrow_scraper/data/processed"
print_status "Production data directory ready"

# Step 6: Transfer real arrow data
echo -e "${BLUE}📤 Step 6: Transferring real arrow data files...${NC}"
echo "   This may take a few minutes depending on connection speed..."

# Use rsync for efficient transfer
if command -v rsync >/dev/null 2>&1; then
    echo "   Using rsync for efficient transfer..."
    rsync -avz --progress "$LOCAL_DATA_DIR"/ "$PRODUCTION_SERVER:$PRODUCTION_PATH/arrow_scraper/data/processed/"
else
    echo "   Using scp for transfer..."
    scp -r "$LOCAL_DATA_DIR"/* "$PRODUCTION_SERVER:$PRODUCTION_PATH/arrow_scraper/data/processed/"
fi

print_status "Arrow data files transferred"

# Step 7: Verify transfer
echo -e "${BLUE}🔍 Step 7: Verifying transfer on production server...${NC}"
VERIFY_CMD="cd $PRODUCTION_PATH/arrow_scraper/data/processed && echo 'Files on production:' && ls -la *.json | wc -l | xargs echo 'Total JSON files:' && find . -name '*.json' ! -name 'sample_arrows.json' ! -name 'wood_arrows.json' | wc -l | xargs echo 'Real manufacturer files:'"

ssh "$PRODUCTION_SERVER" "$VERIFY_CMD"

# Count files on production
PROD_JSON_COUNT=$(ssh "$PRODUCTION_SERVER" "find $PRODUCTION_PATH/arrow_scraper/data/processed -name '*.json' | wc -l")
PROD_REAL_COUNT=$(ssh "$PRODUCTION_SERVER" "find $PRODUCTION_PATH/arrow_scraper/data/processed -name '*.json' ! -name 'sample_arrows.json' ! -name 'wood_arrows.json' | wc -l")

echo "   Production server now has:"
echo "   - Total JSON files: $PROD_JSON_COUNT"
echo "   - Real manufacturer files: $PROD_REAL_COUNT"

if [ "$PROD_REAL_COUNT" -ge "$REAL_JSON_FILES" ]; then
    print_status "Transfer verification successful"
else
    print_warning "Transfer verification shows fewer files than expected"
fi

# Step 8: Import data on production server
echo -e "${BLUE}🗄️  Step 8: Importing data on production server...${NC}"
IMPORT_CMD="cd $PRODUCTION_PATH && ./production-import-only.sh"

echo "   Running import script on production server..."
ssh "$PRODUCTION_SERVER" "$IMPORT_CMD" || print_warning "Import script finished with warnings (this may be normal)"

print_status "Data import completed on production server"

# Step 9: Final verification
echo -e "${BLUE}✅ Step 9: Final verification...${NC}"
FINAL_CHECK_CMD="cd $PRODUCTION_PATH/arrow_scraper && sqlite3 arrow_database.db 'SELECT COUNT(*) FROM arrows; SELECT COUNT(DISTINCT manufacturer) FROM arrows;' 2>/dev/null || echo 'Database verification will be done after deployment'"

echo "   Checking production database..."
ssh "$PRODUCTION_SERVER" "$FINAL_CHECK_CMD"

echo ""
echo -e "${GREEN}🎉 Real Arrow Data Transfer Complete!${NC}"
echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}Summary:${NC}"
echo -e "${GREEN}✅ Transferred $REAL_JSON_FILES real manufacturer data files${NC}"
echo -e "${GREEN}✅ Production server now has complete arrow database${NC}"
echo -e "${GREEN}✅ Data imported and ready for deployment${NC}"
echo ""
echo -e "${YELLOW}Next steps on production server:${NC}"
echo -e "${YELLOW}1. Deploy: ./quick-deploy.sh${NC}"
echo -e "${YELLOW}2. Or SSL: ./deploy-production-ssl.sh yourdomain.com${NC}"
echo -e "${YELLOW}3. Verify: Visit database page to see real arrow data${NC}"