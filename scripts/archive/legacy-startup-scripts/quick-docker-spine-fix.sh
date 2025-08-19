#!/bin/bash
#
# Quick Docker Spine Fix - One-liner command for production
#

echo "🐳 Quick Docker Production Spine Fix"
echo "===================================="

# Find API container
CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "(api|arrowtuner|archery)" | head -1)

if [ -z "$CONTAINER" ]; then
    echo "❌ No API container found!"
    echo "Available containers:"
    docker ps --format "{{.Names}}"
    exit 1
fi

echo "✅ Found container: $CONTAINER"

# Copy spine data to container
echo "📁 Copying spine data files..."
docker cp ./arrow_scraper/spinecalculatordata $CONTAINER:/app/ || {
    echo "❌ Failed to copy spine data directory"
    exit 1
}

docker cp ./arrow_scraper/spine_calculator_data_importer.py $CONTAINER:/app/ || {
    echo "❌ Failed to copy import script"
    exit 1
}

# Run import inside container
echo "🎯 Running spine import in container..."
docker exec $CONTAINER python3 /app/spine_calculator_data_importer.py || {
    echo "❌ Spine import failed"
    exit 1
}

# Verify import
echo "🔍 Verifying import..."
SPINE_COUNT=$(docker exec $CONTAINER python3 -c "import sqlite3; conn=sqlite3.connect('/app/databases/arrow_database.db'); print(conn.execute('SELECT COUNT(*) FROM manufacturer_spine_charts_enhanced').fetchone()[0]); conn.close()" 2>/dev/null)

if [ "$SPINE_COUNT" -gt "0" ]; then
    echo "✅ SUCCESS! $SPINE_COUNT spine charts imported to container database"
    echo ""
    echo "🎯 Your production spine chart system should now work!"
    echo "Refresh your browser and try accessing the admin spine charts."
else
    echo "❌ Import verification failed"
    exit 1
fi