#!/bin/bash
# Prepare Docker Data Volume Script
# Ensures database and data files are available for Docker containers

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

# Auto-detect project root (directory containing this script)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
ARROW_SCRAPER_DIR="$PROJECT_ROOT/arrow_scraper"
DOCKER_DATA_DIR="$PROJECT_ROOT/docker-data"

# Auto-detect source database and data locations
find_source_database() {
    local potential_paths="
        $ARROW_SCRAPER_DIR/arrow_database.db
        $PROJECT_ROOT/arrow_database.db
        arrow_database.db
    "
    
    for path in $potential_paths; do
        if [ -f "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    return 1
}

find_source_data_dir() {
    local potential_paths="
        $ARROW_SCRAPER_DIR/data
        $PROJECT_ROOT/data
        data
    "
    
    for path in $potential_paths; do
        if [ -d "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    return 1
}

log "Preparing Docker data volume for ArrowTuner..."
log "Project root: $PROJECT_ROOT"

# Create docker data directory
mkdir -p "$DOCKER_DATA_DIR"
log "Created Docker data directory: $DOCKER_DATA_DIR"

# Find and copy source database
SOURCE_DB=$(find_source_database)
if [ $? -eq 0 ]; then
    log "Found source database: $SOURCE_DB"
    
    # Test database to ensure it has data
    if command -v sqlite3 >/dev/null 2>&1; then
        ARROW_COUNT=$(sqlite3 "$SOURCE_DB" "SELECT COUNT(*) FROM arrows;" 2>/dev/null || echo "0")
        if [ "$ARROW_COUNT" -gt 0 ]; then
            success "Found source database with $ARROW_COUNT arrows"
            
            # Copy database to docker data directory
            cp "$SOURCE_DB" "$DOCKER_DATA_DIR/arrow_database.db"
            success "Copied database to Docker data directory"
        else
            warning "Source database exists but appears empty"
        fi
    else
        warning "Cannot verify database contents (sqlite3 not available)"
        # Copy anyway
        cp "$SOURCE_DB" "$DOCKER_DATA_DIR/arrow_database.db"
        log "Copied database to Docker data directory (unverified)"
    fi
else
    warning "No source database found in any of the expected locations"
fi

# Find and copy data directory
SOURCE_DATA_DIR=$(find_source_data_dir)
if [ $? -eq 0 ]; then
    log "Found source data directory: $SOURCE_DATA_DIR"
    log "Copying data directory..."
    cp -r "$SOURCE_DATA_DIR" "$DOCKER_DATA_DIR/"
    
    # Count processed files
    PROCESSED_FILES=$(find "$DOCKER_DATA_DIR/data/processed" -name "*.json" 2>/dev/null | wc -l || echo "0")
    success "Copied data directory with $PROCESSED_FILES processed JSON files"
else
    warning "No source data directory found in any of the expected locations"
fi

# Set proper permissions for Docker containers
# Use 1000:1000 (typical Docker user) instead of root
if id 1000 >/dev/null 2>&1; then
    # Change ownership to user 1000 if it exists
    chown -R 1000:1000 "$DOCKER_DATA_DIR" 2>/dev/null || true
fi
chmod -R 755 "$DOCKER_DATA_DIR"
success "Set permissions on Docker data directory"

# Create volume mapping info
DB_ARROW_COUNT="N/A"
if [ -f "$DOCKER_DATA_DIR/arrow_database.db" ] && command -v sqlite3 >/dev/null 2>&1; then
    DB_ARROW_COUNT=$(sqlite3 "$DOCKER_DATA_DIR/arrow_database.db" "SELECT COUNT(*) FROM arrows;" 2>/dev/null || echo "N/A")
fi

PROCESSED_FILE_COUNT="0"
if [ -d "$DOCKER_DATA_DIR/data/processed" ]; then
    PROCESSED_FILE_COUNT=$(find "$DOCKER_DATA_DIR/data/processed" -name "*.json" 2>/dev/null | wc -l || echo "0")
fi

IMAGE_FILE_COUNT="0"
if [ -d "$DOCKER_DATA_DIR/data/images" ]; then
    IMAGE_FILE_COUNT=$(find "$DOCKER_DATA_DIR/data/images" \( -name "*.jpg" -o -name "*.png" -o -name "*.webp" \) 2>/dev/null | wc -l || echo "0")
fi

cat > "$DOCKER_DATA_DIR/README.md" << EOF
# Docker Data Volume

This directory contains data files for the ArrowTuner Docker containers.

## Contents

- \`arrow_database.db\` - SQLite database with arrow specifications
- \`data/\` - Data directory with processed JSON files and images

## Usage

This directory is mounted as a volume in Docker containers:

\`\`\`yaml
volumes:
  - ./docker-data:/app/data
\`\`\`

## Last Updated

$(date +'%Y-%m-%d %H:%M:%S')

## Statistics

- Database arrows: $DB_ARROW_COUNT
- Processed files: $PROCESSED_FILE_COUNT
- Image files: $IMAGE_FILE_COUNT

## Permissions

Files are owned by user 1000:1000 for Docker compatibility.
EOF

success "Created README.md with volume information"

# Update docker-compose files to use the prepared data
log "Updating docker-compose configurations..."

# Update docker-compose.yml
if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    # Check if volume mapping already exists
    if grep -q "docker-data" "$PROJECT_ROOT/docker-compose.yml"; then
        log "Docker compose already has docker-data volume mapping"
    else
        log "Consider updating docker-compose.yml to use ./docker-data:/app/data volume mapping"
    fi
fi

# Update docker-compose.ssl.yml  
if [ -f "$PROJECT_ROOT/docker-compose.ssl.yml" ]; then
    if grep -q "docker-data" "$PROJECT_ROOT/docker-compose.ssl.yml"; then
        log "Docker compose SSL already has docker-data volume mapping"
    else
        log "Consider updating docker-compose.ssl.yml to use ./docker-data:/app/data volume mapping"
    fi
fi

# Display summary
echo
log "Docker Data Preparation Summary:"
echo "================================"

if [ -f "$DOCKER_DATA_DIR/arrow_database.db" ]; then
    DB_SIZE=$(du -h "$DOCKER_DATA_DIR/arrow_database.db" 2>/dev/null | cut -f1 || echo "unknown")
    success "Database: $DB_SIZE"
else
    error "Database: Not found"
fi

if [ -d "$DOCKER_DATA_DIR/data" ]; then
    DATA_SIZE=$(du -sh "$DOCKER_DATA_DIR/data" 2>/dev/null | cut -f1 || echo "unknown")
    success "Data directory: $DATA_SIZE"
else
    error "Data directory: Not found"
fi

TOTAL_SIZE=$(du -sh "$DOCKER_DATA_DIR" 2>/dev/null | cut -f1 || echo "unknown")
success "Total volume size: $TOTAL_SIZE"

echo
log "Next Steps:"
echo "1. Update docker-compose.yml volume mappings if needed"
echo "2. Run: docker-compose up -d"
echo "3. Check container logs: docker-compose logs api"

echo
success "Docker data preparation completed!"