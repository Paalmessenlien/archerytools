#!/bin/bash
# Production Database Fix Script
# Run this script on your production server to fix the schema issues

echo "🔧 Production Database Fix Script"
echo "=================================="

# Check if running as root or with docker access
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Cannot access Docker. Please run with sudo or add user to docker group."
    exit 1
fi

echo "✅ Docker access confirmed"

# Copy diagnostic scripts to the container
echo "📋 Copying diagnostic scripts to container..."
docker cp diagnose-production-schema.py arrowtuner-api:/app/
docker cp fix-production-schema.py arrowtuner-api:/app/

# Run diagnostic first
echo "🔍 Running database diagnostic..."
docker exec arrowtuner-api python3 /app/diagnose-production-schema.py

echo ""
echo "🤔 Do you want to proceed with the automatic fix? (y/N)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "🔧 Applying database fix..."
    docker exec arrowtuner-api python3 /app/fix-production-schema.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Database fix completed successfully!"
        echo "🔄 Restarting API container..."
        docker restart arrowtuner-api
        
        # Wait for container to restart
        echo "⏳ Waiting for container to restart..."
        sleep 10
        
        # Check health
        echo "🏥 Checking API health..."
        curl -s http://localhost:5000/api/health || echo "❌ API health check failed"
        
        echo ""
        echo "🎯 Next steps:"
        echo "1. Check the admin panel schema verification"
        echo "2. Verify that migration status API works"
        echo "3. Test database operations"
        
    else
        echo "❌ Database fix failed. Check the logs:"
        echo "   docker logs arrowtuner-api"
    fi
else
    echo "ℹ️  Fix cancelled. You can run the fix manually:"
    echo "   docker exec arrowtuner-api python3 /app/fix-production-schema.py"
fi

echo ""
echo "🔍 Checking current container logs (last 20 lines):"
docker logs --tail 20 arrowtuner-api

echo ""
echo "=================================="
echo "Fix script completed"