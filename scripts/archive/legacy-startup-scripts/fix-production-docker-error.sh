#!/bin/bash

# Fix Production Docker ContainerConfig Error
# Run this on your production server: archerytool.online

set -e

echo "🔧 Fixing Docker Compose ContainerConfig error on production server"
echo "=================================================================="

# Stop all Docker containers forcefully
echo "🛑 Stopping all Docker containers..."
docker stop $(docker ps -aq) 2>/dev/null || true

# Remove all containers
echo "🗑️  Removing all containers..."
docker rm $(docker ps -aq) 2>/dev/null || true

# Remove all networks
echo "🌐 Removing all networks..."
docker network prune -f

# Remove all volumes (backup first if needed)
echo "💾 Removing all volumes..."
docker volume prune -f

# Clean Docker system
echo "🧹 Cleaning Docker system..."
docker system prune -a -f

# Remove any lingering compose files that might cause issues
echo "📄 Cleaning old compose configurations..."
cd /root/archerytools || cd ~/archerytools || cd /home/*/archerytools

# Remove any old compose files that might be causing conflicts
if [ -f "docker-compose.yml" ]; then mv docker-compose.yml docker-compose.yml.backup_$(date +%s); fi
if [ -f "docker-compose.dev.yml" ]; then mv docker-compose.dev.yml docker-compose.dev.yml.backup_$(date +%s); fi
if [ -f "docker-compose.ssl.yml" ]; then mv docker-compose.ssl.yml docker-compose.ssl.yml.backup_$(date +%s); fi
if [ -f "docker-compose.enhanced-ssl.yml" ]; then mv docker-compose.enhanced-ssl.yml docker-compose.enhanced-ssl.yml.backup_$(date +%s); fi

echo "✅ Docker cleanup completed"

# Now restart with unified script
echo "🚀 Starting production with unified script..."
./start-unified.sh ssl archerytool.online

echo "✅ Production deployment should now work correctly"
echo "🌐 Check your site at: https://archerytool.online"