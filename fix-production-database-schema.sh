#!/bin/bash

# Fix Production Database Schema Issues
# Run this on production server after Docker issues are resolved
# Fixes flight path calculations and chronograph data errors

set -e

echo "🗄️  Fixing Production Database Schema Issues"
echo "==========================================="

cd /root/archerytools || cd ~/archerytools || cd /home/*/archerytools

# Backup database first
echo "💾 Creating database backup..."
if [ -f "databases/arrow_database.db" ]; then
    cp databases/arrow_database.db databases/arrow_database.db.schema_fix_backup_$(date +%s)
    echo "✅ Database backed up"
fi

# Run the specific migration for production schema fixes
echo "🔄 Running production schema migration..."
cd arrow_scraper

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Set environment variable for production database path
export ARROW_DATABASE_PATH="../databases/arrow_database.db"

# Run the migration directly
python3 migrations/033_production_schema_fixes.py

# Also run via migration manager to mark it as applied
echo "📝 Marking migration as applied..."
python3 -c "
import sys
sys.path.append('.')
from database_migration_manager import DatabaseMigrationManager
from migrations.production_schema_fixes_033 import Migration033

# Initialize migration manager
manager = DatabaseMigrationManager('../databases/arrow_database.db')

# Mark migration 033 as applied
migration = Migration033()
manager.mark_migration_applied(migration.version, migration.description)
print('✅ Migration 033 marked as applied')
" || echo "⚠️  Could not mark migration as applied (not critical)"

echo "✅ Production database schema fixes completed"
echo "🌐 Flight path calculations and chronograph should now work"
echo "🔄 Restart your application containers to pick up changes"

# Restart containers
echo "🔄 Restarting application..."
cd ..
docker-compose -f docker-compose.unified.yml restart api frontend 2>/dev/null || ./start-unified.sh ssl archerytool.online

echo "✅ Production database schema fix completed successfully"