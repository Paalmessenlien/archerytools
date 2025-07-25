#!/bin/bash
# Fix Docker Data Permissions Script
# Ensures proper ownership for Docker containers running as non-root

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    printf "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] %s${NC}\n" "$1"
}

success() {
    printf "${GREEN}✅ %s${NC}\n" "$1"
}

warning() {
    printf "${YELLOW}⚠️  %s${NC}\n" "$1"
}

error() {
    printf "${RED}❌ %s${NC}\n" "$1"
}

# Auto-detect project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCKER_DATA_DIR="$SCRIPT_DIR/docker-data"

# Get target user ID (default to 1000, or use environment variable)
TARGET_UID="${DOCKER_UID:-1000}"
TARGET_GID="${DOCKER_GID:-1000}"

log "Fixing Docker data permissions..."
log "Target UID:GID = $TARGET_UID:$TARGET_GID"

# Check if docker-data directory exists
if [ ! -d "$DOCKER_DATA_DIR" ]; then
    error "Docker data directory not found: $DOCKER_DATA_DIR"
    echo "Run ./prepare-docker-data.sh first to create the data volume"
    exit 1
fi

# Check if we need sudo
CURRENT_OWNER=$(stat -c '%u:%g' "$DOCKER_DATA_DIR" 2>/dev/null || echo "unknown")
log "Current ownership: $CURRENT_OWNER"

if [ "$CURRENT_OWNER" != "$TARGET_UID:$TARGET_GID" ]; then
    log "Changing ownership to $TARGET_UID:$TARGET_GID..."
    
    # Try without sudo first
    if chown -R "$TARGET_UID:$TARGET_GID" "$DOCKER_DATA_DIR" 2>/dev/null; then
        success "Ownership changed successfully"
    else
        # Try with sudo
        log "Permission denied, trying with sudo..."
        if command -v sudo >/dev/null 2>&1; then
            if sudo chown -R "$TARGET_UID:$TARGET_GID" "$DOCKER_DATA_DIR"; then
                success "Ownership changed successfully (with sudo)"
            else
                error "Failed to change ownership even with sudo"
                exit 1
            fi
        else
            error "Cannot change ownership and sudo is not available"
            exit 1
        fi
    fi
else
    success "Ownership already correct"
fi

# Ensure proper permissions
log "Setting proper permissions..."
chmod -R 755 "$DOCKER_DATA_DIR"
success "Permissions set to 755"

# Verify the changes
NEW_OWNER=$(stat -c '%u:%g' "$DOCKER_DATA_DIR" 2>/dev/null || echo "unknown")
NEW_PERMS=$(stat -c '%a' "$DOCKER_DATA_DIR" 2>/dev/null || echo "unknown")

echo
log "Permission Fix Summary:"
echo "======================="
success "Directory: $DOCKER_DATA_DIR"
success "Ownership: $NEW_OWNER"
success "Permissions: $NEW_PERMS"

# Check database file specifically
if [ -f "$DOCKER_DATA_DIR/arrow_database.db" ]; then
    DB_OWNER=$(stat -c '%u:%g' "$DOCKER_DATA_DIR/arrow_database.db" 2>/dev/null || echo "unknown")
    DB_PERMS=$(stat -c '%a' "$DOCKER_DATA_DIR/arrow_database.db" 2>/dev/null || echo "unknown")
    success "Database file ownership: $DB_OWNER"
    success "Database file permissions: $DB_PERMS"
fi

echo
log "Docker containers can now access the data volume as user $TARGET_UID:$TARGET_GID"
success "Permission fix completed!"

# Show usage information
echo
log "Usage Notes:"
echo "============"
echo "• Default Docker user: 1000:1000"
echo "• Custom user: DOCKER_UID=1001 DOCKER_GID=1001 $0"
echo "• Run before: docker-compose up"
echo "• Run after permission issues in containers"