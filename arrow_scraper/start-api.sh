#!/bin/bash
# Startup script for ArrowTuner API with database initialization

set -e

echo "🚀 Starting ArrowTuner API..."

# Initialize database if needed
echo "🔧 Checking database..."
python init-database.py

# Start the Flask API
echo "🌐 Starting Flask API server..."
exec python api.py