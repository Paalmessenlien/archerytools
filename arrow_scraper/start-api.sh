#!/bin/bash
# Startup script for ArrowTuner API

set -e

echo "🚀 Starting ArrowTuner API..."

# Check if database exists (built into image)
if [ -f "/app/arrow_database.db" ]; then
    echo "✅ Database found in image"
else
    echo "❌ Database not found - image may not have built correctly"
fi

# Start the Flask API
echo "🌐 Starting Flask API server..."
exec python api.py