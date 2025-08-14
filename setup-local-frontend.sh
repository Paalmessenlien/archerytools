#!/bin/bash
# Setup local frontend dependencies to avoid Docker native binding issues
# This builds node_modules on the host then mounts it into the container

set -e

echo "🏗️  Local Frontend Dependencies Setup"
echo "====================================="

cd frontend

echo "📦 Installing dependencies locally..."
echo "This will build native bindings on your host system"

# Clean existing installation
if [ -d "node_modules" ]; then
    echo "🧹 Removing existing node_modules..."
    rm -rf node_modules
fi

if [ -f "package-lock.json" ]; then
    echo "🧹 Removing existing package-lock.json..."
    rm -f package-lock.json
fi

# Clear npm cache
echo "🧹 Clearing npm cache..."
npm cache clean --force

# Install dependencies
echo "📦 Installing dependencies with legacy peer deps..."
npm install --legacy-peer-deps

# Test that it works (postinstall already ran nuxt prepare)
echo "🧪 Checking if Nuxt preparation was successful..."
if [ -d ".nuxt" ] && [ -f ".nuxt/nuxt.d.ts" ]; then
    echo "✅ Local frontend setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Update docker-compose to use prebuilt approach"
    echo "2. Start development environment: ./start-docker-dev.sh start"
    echo ""
    echo "💡 This approach uses host-built node_modules to avoid container native binding issues"
else
    echo "❌ Nuxt preparation failed on host system"
    echo "Missing .nuxt directory or TypeScript definitions"
    echo ""
    echo "🔧 Troubleshooting options:"
    echo "1. Try different Node.js version (nvm use 16 or nvm use 20)"
    echo "2. Check for global package conflicts"
    echo "3. Try: npm install --force"
    echo "4. Manual fix: npm run postinstall"
    exit 1
fi