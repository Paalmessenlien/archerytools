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
JSON_COUNT=$(find data/processed -name "*.json" -not -path "*/archive/*" -not -name "*learn*" | wc -l)
echo "   Found $JSON_COUNT JSON files to import (excluding learn files)"

if [ "$JSON_COUNT" -eq 0 ]; then
    echo "❌ No JSON files found in data/processed/"
    echo "   This suggests the repository doesn't have scraped data"
    echo "   Run scraper locally first to generate data files"
    exit 1
fi

echo ""
echo "📋 JSON Files Available for Import:"
find data/processed -name "*.json" -not -path "*/archive/*" -not -name "*learn*" | sort | sed 's/^/   /'

LEARN_COUNT=$(find data/processed -name "*learn*.json" -not -path "*/archive/*" | wc -l)
if [ "$LEARN_COUNT" -gt 0 ]; then
    echo ""
    echo "📚 Pattern Learning Files (excluded from import):"
    find data/processed -name "*learn*.json" -not -path "*/archive/*" | sort | sed 's/^/   /'
fi

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

# Run the arrow import
if python3 database_import_manager.py --import-all --force; then
    echo ""
    echo "✅ Arrow import completed successfully\!"
    
    # Check arrow database status
    if [ -f "arrow_database.db" ]; then
        FINAL_COUNT=$(sqlite3 arrow_database.db "SELECT COUNT(*) FROM arrows" 2>/dev/null || echo "0")
        MANUFACTURER_COUNT=$(sqlite3 arrow_database.db "SELECT COUNT(DISTINCT manufacturer) FROM arrows" 2>/dev/null || echo "0")
        
        echo ""
        echo "📊 Arrow Database Statistics:"
        echo "   Total Arrows: $FINAL_COUNT"
        echo "   Manufacturers: $MANUFACTURER_COUNT"
        
        if [ "$FINAL_COUNT" -gt 100 ]; then
            echo "   ✅ Database has good content volume"
        else
            echo "   ⚠️  Warning: Low arrow count, may indicate import issues"
        fi
        
        echo ""
        echo "🏭 Top Arrow Manufacturers:"
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
    
    # Import components if component files exist
    echo ""
    echo "🔍 Checking for component data files..."
    COMPONENT_COUNT=$(find data/processed/components -name "*.json" 2>/dev/null | wc -l || echo "0")
    echo "   Found $COMPONENT_COUNT component JSON files to import"
    
    if [ "$COMPONENT_COUNT" -gt 0 ]; then
        echo "📋 Component Files Available:"
        find data/processed/components -name "*.json" 2>/dev/null | sort | sed 's/^/   /' || true
        
        echo ""
        echo "🧩 Starting component import process..."
        if python3 component_importer.py --force; then
            echo "✅ Component import completed successfully\!"
            
            # Check component statistics
            COMPONENT_TOTAL=$(sqlite3 arrow_database.db "SELECT COUNT(*) FROM components" 2>/dev/null || echo "0")
            COMPONENT_CATEGORIES=$(sqlite3 arrow_database.db "SELECT COUNT(DISTINCT cc.name) FROM component_categories cc JOIN components c ON cc.id = c.category_id" 2>/dev/null || echo "0")
            COMPONENT_MANUFACTURERS=$(sqlite3 arrow_database.db "SELECT COUNT(DISTINCT manufacturer) FROM components" 2>/dev/null || echo "0")
            
            echo ""
            echo "🧩 Component Database Statistics:"
            echo "   Total Components: $COMPONENT_TOTAL"
            echo "   Categories: $COMPONENT_CATEGORIES"
            echo "   Component Manufacturers: $COMPONENT_MANUFACTURERS"
            
            if [ "$COMPONENT_TOTAL" -gt 0 ]; then
                echo ""
                echo "📦 Component Categories:"
                sqlite3 arrow_database.db "
                    SELECT cc.name || ': ' || COUNT(c.id) || ' components'
                    FROM component_categories cc 
                    LEFT JOIN components c ON cc.id = c.category_id
                    GROUP BY cc.name
                    ORDER BY COUNT(c.id) DESC
                " | sed 's/^/   /' 2>/dev/null || echo "   Unable to retrieve category statistics"
                
                echo ""
                echo "🏭 Component Manufacturers:"
                sqlite3 arrow_database.db "
                    SELECT manufacturer || ': ' || COUNT(*) || ' components' 
                    FROM components 
                    GROUP BY manufacturer 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 3
                " | sed 's/^/   /' 2>/dev/null || echo "   Unable to retrieve manufacturer statistics"
            fi
        else
            echo "⚠️  Component import failed - continuing with arrow database only"
            echo "   This is not critical - arrow functionality will work normally"
        fi
    else
        echo "   No component files found - skipping component import"
        echo "   This is normal if components haven't been scraped yet"
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
echo "✅ Component database ready (if component files were found)"
echo "✅ NO web scraping performed (production-safe)"
echo "✅ Data imported from existing JSON files only"
echo ""
echo "Next steps:"
echo "1. Deploy application (database will be included)"
echo "2. Server startup will automatically check for newer JSON files"
echo "3. Regular updates: commit new JSON files and redeploy"
echo "4. Component functionality available in frontend /components page"