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

echo "🎉 Migration deployment completed!"
echo "✅ Database migration deployment complete!"
echo "🚀 System is ready for production with image upload functionality"
