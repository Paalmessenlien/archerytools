#!/bin/bash

# ArrowTuner User Data Backup Script
# Creates timestamped backups of user data before deployments

set -e

echo "🔐 ArrowTuner User Data Backup"
echo "============================"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if volume exists
if ! docker volume ls | grep -q "arrowtuner-userdata"; then
    echo "⚠️  No user data volume found. Nothing to backup."
    exit 0
fi

# Create backup directory
BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/userdata_backup_$TIMESTAMP.tar.gz"

# Create backup
echo "📦 Creating backup: $BACKUP_FILE"
docker run --rm \
    -v arrowtuner-userdata:/data \
    -v "$(pwd)/$BACKUP_DIR":/backup \
    alpine \
    tar czf "/backup/userdata_backup_$TIMESTAMP.tar.gz" -C /data .

# Verify backup
if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
    echo "✅ Backup created successfully: $BACKUP_FILE ($SIZE)"
    
    # List contents
    echo ""
    echo "📄 Backup contents:"
    tar -tzf "$BACKUP_FILE" | head -10
    echo "..."
    
    # Keep only last 5 backups
    echo ""
    echo "🧹 Cleaning old backups (keeping last 5)..."
    ls -t "$BACKUP_DIR"/userdata_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm -v
    
    echo ""
    echo "📁 Current backups:"
    ls -lh "$BACKUP_DIR"/userdata_backup_*.tar.gz 2>/dev/null || echo "  No backups found"
else
    echo "❌ Backup failed!"
    exit 1
fi

echo ""
echo "📝 To restore from this backup later:"
echo "   docker run --rm -v arrowtuner-userdata:/data -v \"$(pwd)/$BACKUP_FILE\":/backup.tar.gz alpine sh -c 'cd /data && tar xzf /backup.tar.gz'"