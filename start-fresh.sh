#!/bin/bash

# Kill any existing processes
pkill -f "node" || true
pkill -f "npm" || true
pkill -f "python.*api" || true

echo "Starting ArrowTuner with GitHub Issue #16 Fixes..."

# Start Flask API
cd /home/paal/archerytools/arrow_scraper
echo "Installing Python dependencies..."
pip install flask flask-cors python-dotenv pyjwt google-auth requests 2>/dev/null || true
echo "Starting API backend..."
python api.py &
API_PID=$!
echo "API started with PID: $API_PID"

# Wait for API to be ready
sleep 3

# Start Frontend in dev mode
cd /home/paal/archerytools/frontend
echo "Starting frontend in development mode..."
NODE_ENV=development npm run dev &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

echo ""
echo "==================================="
echo "ArrowTuner is starting up..."
echo "==================================="
echo ""
echo "Frontend: http://localhost:3000"
echo "API: http://localhost:5000"
echo ""
echo "GitHub Issue #16 Fixes:"
echo "1. Draw weight: 0.5 increments"
echo "2. Point weight: Starts at 40, 0.5 increments, shows gn (gr)"
echo "3. Spine display: Shows single values, not ranges"
echo "4. Bow setup saving: Fixed database fields"
echo "5. Bow usage tags: Target, Field, 3D, Hunting"
echo "6. Merged pages: Database and Calculator tabs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill $API_PID $FRONTEND_PID; exit" INT
wait