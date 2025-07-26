#!/bin/bash
# Debug Database Issues
# Helps diagnose why the database isn't being created in Docker

echo "🔍 Database Debug Information"
echo "=" * 40

echo "📂 Current directory contents:"
ls -la

echo
echo "📁 Arrow scraper directory:"
ls -la arrow_scraper/

echo
echo "📊 Checking for processed data:"
if [ -d "arrow_scraper/data/processed" ]; then
    echo "✅ Processed data directory exists"
    echo "📄 JSON files found:"
    ls -la arrow_scraper/data/processed/*.json
    echo "📊 Total JSON files: $(ls arrow_scraper/data/processed/*.json | wc -l)"
else
    echo "❌ Processed data directory not found"
fi

echo
echo "🔧 Testing database build locally:"
cd arrow_scraper
if [ -f "build-database-robust.py" ]; then
    echo "✅ Build script exists"
    echo "🏗️  Running database build test..."
    python build-database-robust.py
    echo
    echo "📊 Database verification:"
    if [ -f "arrow_database.db" ]; then
        echo "✅ Database file created"
        ls -la arrow_database.db
        echo "📈 Arrow count:"
        python -c "import sqlite3; conn=sqlite3.connect('arrow_database.db'); print('Arrows:', conn.execute('SELECT COUNT(*) FROM arrows').fetchone()[0]); conn.close()"
    else
        echo "❌ Database file not created"
    fi
else
    echo "❌ Build script not found"
fi

echo
echo "🐳 Docker context check:"
echo "📁 Files that will be copied to Docker:"
cd ..
echo "📄 Dockerfile content (database build section):"
grep -A 5 -B 5 "build-database" arrow_scraper/Dockerfile

echo
echo "🎯 Recommended fixes:"
echo "1. Ensure processed data exists: ls arrow_scraper/data/processed/"
echo "2. Test build script locally: cd arrow_scraper && python build-database-robust.py"
echo "3. Check Docker build logs for database creation"
echo "4. Verify .dockerignore doesn't exclude data/ directory"