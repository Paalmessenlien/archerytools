#\!/bin/bash
# Production Data Import Script
# This script imports arrow data from JSON files WITHOUT performing any web scraping
# Safe for production servers - NO network requests to manufacturer websites

set -e

echo "🏹 Production Arrow Data Import"
echo "=============================="
echo "⚠️  NO WEB SCRAPING - Import from JSON files only"
echo ""

# Check if we're in the right directory
if [ \! -f "arrow_scraper/database_import_manager.py" ]; then
    echo "❌ Error: Must run from project root directory"
    echo "   Expected: arrow_scraper/database_import_manager.py"
    exit 1
fi

# Navigate to scraper directory
cd arrow_scraper

echo "📂 Checking for JSON data files..."
JSON_COUNT=$(find data/processed -name "*.json" -not -path "*/archive/*" | wc -l)
echo "   Found $JSON_COUNT JSON files to import"

if [ "$JSON_COUNT" -eq 0 ]; then
    echo "❌ No JSON files found in data/processed/"
    echo "   This suggests the repository doesn't have scraped data"
    echo "   Run scraper locally first to generate data files"
    exit 1
fi

echo ""
echo "📋 JSON Files Available:"
find data/processed -name "*.json" -not -path "*/archive/*" | sort | sed 's/^/   /'

echo ""
echo "🔍 Checking current database status..."
if [ -f "arrow_database.db" ]; then
    CURRENT_COUNT=$(sqlite3 arrow_database.db "SELECT COUNT(*) FROM arrows" 2>/dev/null || echo "0")
    echo "   Current database has $CURRENT_COUNT arrows"
else
    echo "   No existing database found"
    CURRENT_COUNT=0
fi

echo ""
echo "🚀 Starting JSON import process..."
echo "================================="

# Run the import
if python3 database_import_manager.py --import-all --force; then
    echo ""
    echo "✅ Import completed successfully\!"
    
    # Check final count
    if [ -f "arrow_database.db" ]; then
        FINAL_COUNT=$(sqlite3 arrow_database.db "SELECT COUNT(*) FROM arrows" 2>/dev/null || echo "0")
        MANUFACTURER_COUNT=$(sqlite3 arrow_database.db "SELECT COUNT(DISTINCT manufacturer) FROM arrows" 2>/dev/null || echo "0")
        
        echo ""
        echo "📊 Final Database Statistics:"
        echo "   Total Arrows: $FINAL_COUNT"
        echo "   Manufacturers: $MANUFACTURER_COUNT"
        
        if [ "$FINAL_COUNT" -gt 100 ]; then
            echo "   ✅ Database has good content volume"
        else
            echo "   ⚠️  Warning: Low arrow count, may indicate import issues"
        fi
        
        echo ""
        echo "🏭 Top Manufacturers:"
        sqlite3 arrow_database.db "
            SELECT manufacturer || ': ' || COUNT(*) || ' arrows' 
            FROM arrows 
            GROUP BY manufacturer 
            ORDER BY COUNT(*) DESC 
            LIMIT 5
        " | sed 's/^/   /'
        
    else
        echo "❌ Database file not found after import"
        exit 1
    fi
else
    echo ""
    echo "❌ Import failed\!"
    echo "   Check the error messages above"
    echo "   Common issues:"
    echo "   - Missing Python dependencies"
    echo "   - Corrupted JSON files"
    echo "   - Database permission issues"
    exit 1
fi

echo ""
echo "🎯 Production Import Complete\!"
echo "============================="
echo "✅ Arrow database ready for production deployment"
echo "✅ NO web scraping performed (production-safe)"
echo "✅ Data imported from existing JSON files only"
echo ""
echo "Next steps:"
echo "1. Deploy application (database will be included)"
echo "2. Server startup will automatically check for newer JSON files"
echo "3. Regular updates: commit new JSON files and redeploy"