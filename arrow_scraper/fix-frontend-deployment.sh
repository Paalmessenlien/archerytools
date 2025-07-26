#\!/bin/bash

echo "🎯 Frontend Deployment Fix"
echo "=========================="
echo ""

echo "The issue: docker-compose.override.yml runs frontend in development mode"
echo "This requires 'nuxt' CLI which isn't available in production builds."
echo ""

echo "💡 Solutions:"
echo ""

echo "Option 1: Use production Docker Compose (Recommended)"
echo "----------------------------------------------------"
echo "# Stop current deployment"
echo "docker-compose down"
echo ""
echo "# Deploy with production configuration (no override)"
echo "docker-compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "# Test both services"
echo "curl http://localhost:5000/api/health"
echo "curl http://localhost:3000"
echo ""

echo "Option 2: Temporarily rename override file"
echo "-----------------------------------------"
echo "mv docker-compose.override.yml docker-compose.override.yml.disabled"
echo "docker-compose up -d --build"
echo "# When done, restore: mv docker-compose.override.yml.disabled docker-compose.override.yml"
echo ""

echo "Option 3: API-only deployment (for testing)"
echo "------------------------------------------"
echo "docker-compose -f docker-compose.simple.yml up -d --build"
echo ""

echo "📋 The docker-compose.override.yml file automatically overrides settings"
echo "   for development, which conflicts with production builds."
