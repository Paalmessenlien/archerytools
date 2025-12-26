#!/bin/bash
# Test Docker Build Process
# Verifies that the database is properly created in the Docker image

set -e

echo "🐳 Testing Docker Build Process"
echo "=" * 40

echo "📦 Building Docker image..."
docker build -f arrow_scraper/Dockerfile arrow_scraper/ -t arrowtuner-test

echo
echo "🔍 Inspecting built image for database files..."
docker run --rm arrowtuner-test ls -la /app/arrow*.db

echo
echo "📊 Checking database contents..."
docker run --rm arrowtuner-test python -c "
import sqlite3
import os
print('Current directory:', os.getcwd())
print('Files in /app:', os.listdir('/app'))

db_files = ['/app/arrow_database.db', '/app/arrow_database_backup.db']
for db_file in db_files:
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM arrows')
            count = cursor.fetchone()[0]
            print(f'{db_file}: {count} arrows')
            conn.close()
        except Exception as e:
            print(f'{db_file}: Error - {e}')
    else:
        print(f'{db_file}: Not found')
"

echo
echo "🚀 Testing API startup..."
# Start container briefly to test API
CONTAINER_ID=$(docker run -d -p 5001:5000 arrowtuner-test)
echo "Started container: $CONTAINER_ID"

sleep 10

echo "🩺 Testing API health..."
if curl -f -s "http://localhost:5001/api/health" | python3 -m json.tool; then
    echo "✅ API test passed"
else
    echo "❌ API test failed"
fi

echo
echo "🛑 Stopping test container..."
docker stop $CONTAINER_ID
docker rm $CONTAINER_ID

echo
echo "🧹 Cleaning up test image..."
docker rmi arrowtuner-test

echo "✅ Docker build test completed!"