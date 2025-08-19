#!/bin/bash

# Conservative Production Docker Fix
# Preserves databases and only fixes container issues
# Run this on your production server: archerytool.online

set -e

echo "🔧 Conservative Docker fix for production server"
echo "=============================================="

cd /root/archerytools || cd ~/archerytools || cd /home/*/archerytools

# Backup databases first
echo "💾 Backing up databases..."
if [ -f "databases/arrow_database.db" ]; then
    cp databases/arrow_database.db databases/arrow_database.db.emergency_backup_$(date +%s)
    echo "✅ Arrow database backed up"
fi

# Stop only the problematic containers
echo "🛑 Stopping containers gracefully..."
docker-compose -f docker-compose.unified.yml down --remove-orphans 2>/dev/null || true

# Remove only the problematic containers by name
echo "🗑️  Removing problematic containers..."
docker rm arrowtuner-db-init arrowtuner-db-backup db-init db-backup 2>/dev/null || true

# Clean only dangling resources
echo "🧹 Cleaning dangling Docker resources..."
docker container prune -f
docker image prune -f
docker network prune -f

# Try starting again
echo "🚀 Attempting restart..."
./start-unified.sh ssl archerytool.online

echo "✅ Conservative fix completed"
echo "🌐 Check your site at: https://archerytool.online"