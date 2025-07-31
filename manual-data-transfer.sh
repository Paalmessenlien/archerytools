#!/bin/bash

# Manual Real Data Transfer to Production
# Use this if the automated sync script has issues

set -e

PRODUCTION_SERVER="root@archerytool"
PRODUCTION_PATH="/root/archerytools"

echo "🚀 Manual Transfer of Real Arrow Data"
echo "===================================="

# Step 1: Create backup on production
echo "📦 Creating backup on production..."
ssh $PRODUCTION_SERVER "cd $PRODUCTION_PATH && mkdir -p backups/manual_backup_$(date +%Y%m%d_%H%M%S) && cp arrow_scraper/data/processed/* backups/manual_backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo 'Demo data backed up'"

# Step 2: Transfer all real data files
echo "📤 Transferring 14 real manufacturer files..."
scp arrow_scraper/data/processed/*.json $PRODUCTION_SERVER:$PRODUCTION_PATH/arrow_scraper/data/processed/

# Step 3: Verify transfer
echo "🔍 Verifying transfer..."
ssh $PRODUCTION_SERVER "cd $PRODUCTION_PATH/arrow_scraper/data/processed && echo 'Files on production:' && ls -la *.json && echo 'Total files:' && ls -1 *.json | wc -l"

# Step 4: Import data on production
echo "🗄️ Importing data on production server..."
ssh $PRODUCTION_SERVER "cd $PRODUCTION_PATH && ./production-import-only.sh"

# Step 5: Final check
echo "✅ Final verification..."
ssh $PRODUCTION_SERVER "cd $PRODUCTION_PATH/arrow_scraper && sqlite3 arrow_database.db 'SELECT COUNT(*) as arrows FROM arrows; SELECT COUNT(DISTINCT manufacturer) as manufacturers FROM arrows;' 2>/dev/null || echo 'Database will be created on next deployment'"

echo ""
echo "🎉 Manual transfer complete!"
echo "Next: Deploy on production with ./quick-deploy.sh"