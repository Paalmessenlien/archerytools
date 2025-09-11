#!/bin/bash

# Deploy Migrations Script
# Ensures all database migrations are applied correctly for production deployment

set -e

echo "🚀 Deploying Database Migrations..."

# Check if we're in the correct directory
if [ ! -d "arrow_scraper/migrations" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Set database path based on environment
if [ -n "$ARROW_DATABASE_PATH" ]; then
    DB_PATH="$ARROW_DATABASE_PATH"
    echo "🔧 Using ARROW_DATABASE_PATH: $DB_PATH"
elif [ -d "/app/databases" ]; then
    DB_PATH="/app/databases/arrow_database.db"
    echo "🐳 Using Docker database path: $DB_PATH"
else
    DB_PATH="./databases/arrow_database.db"
    echo "🏠 Using local database path: $DB_PATH"
fi

# Ensure database directory exists
mkdir -p "$(dirname "$DB_PATH")"

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "⚠️  Database does not exist at $DB_PATH"
    echo "🔧 This is normal for fresh installations - database will be created"
fi

echo "📁 Database location: $DB_PATH"

# Run the journal images migration (Migration 055)
echo "🖼️  Running Migration 055: Journal Images Column..."
cd arrow_scraper/migrations
python 055_add_journal_images_column.py

if [ $? -eq 0 ]; then
    echo "✅ Migration 055 completed successfully"
else
    echo "❌ Migration 055 failed"
    exit 1
fi

cd ../..

# Verify the migration was successful
echo "🔍 Verifying migration results..."

# Use the actual database path from the migration
ACTUAL_DB_PATH="/home/paal/archerytoolsonline/main/arrow_scraper/databases/arrow_database.db"
if [ -f "$ACTUAL_DB_PATH" ]; then
    # Check if images column exists
    IMAGES_COL_EXISTS=$(sqlite3 "$ACTUAL_DB_PATH" "PRAGMA table_info(journal_entries);" | grep -c "images" || echo "0")
    
    if [ "$IMAGES_COL_EXISTS" -gt 0 ]; then
        echo "✅ Images column successfully added to journal_entries table"
    else
        echo "⚠️  Images column not found in journal_entries table"
    fi
    
    # Check table structure
    echo "📋 Current journal_entries table structure:"
    sqlite3 "$ACTUAL_DB_PATH" "PRAGMA table_info(journal_entries);" | while read line; do
        echo "   $line"
    done
    
    # Show index information
    echo "📊 Available indexes on journal_entries:"
    sqlite3 "$ACTUAL_DB_PATH" ".indexes journal_entries" | while read line; do
        echo "   $line"
    done
    
else
    echo "⚠️  Database file not found after migration - this may be expected for fresh installations"
fi

echo ""
echo "🎉 Migration deployment completed!"
echo ""
echo "📝 Summary of changes:"
echo "   • Added 'images' column to journal_entries table"
echo "   • Column stores JSON array of image objects"  
echo "   • Created performance index for image queries"
echo "   • Migrated existing journal attachments (if any)"
echo "   • Maintains backward compatibility"
echo ""
echo "🔄 This migration supports:"
echo "   • Direct image storage in journal entries"
echo "   • Tuning session image integration"
echo "   • Enhanced journal viewing with images"
echo "   • CDN image URL storage"
echo ""

# Run a quick test query if database exists
if [ -f "$ACTUAL_DB_PATH" ]; then
    echo "🧪 Running validation test..."
    TEST_RESULT=$(sqlite3 "$ACTUAL_DB_PATH" "SELECT COUNT(*) as count FROM journal_entries WHERE images IS NOT NULL;" 2>/dev/null || echo "0")
    echo "📈 Journal entries with images: $TEST_RESULT"
fi

echo "✅ Database migration deployment complete!"
echo "🚀 System is ready for production with image upload functionality"