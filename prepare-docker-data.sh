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
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Configuration
PROJECT_ROOT="/home/paal/arrowtuner2"
ARROW_SCRAPER_DIR="$PROJECT_ROOT/arrow_scraper"
DOCKER_DATA_DIR="$PROJECT_ROOT/docker-data"
SOURCE_DB="$ARROW_SCRAPER_DIR/arrow_database.db"
SOURCE_DATA_DIR="$ARROW_SCRAPER_DIR/data"

log "Preparing Docker data volume for ArrowTuner..."

# Create docker data directory
mkdir -p "$DOCKER_DATA_DIR"
log "Created Docker data directory: $DOCKER_DATA_DIR"

# Check if source database exists
if [[ -f "$SOURCE_DB" ]]; then
    # Test database to ensure it has data
    if command -v sqlite3 &> /dev/null; then
        ARROW_COUNT=$(sqlite3 "$SOURCE_DB" "SELECT COUNT(*) FROM arrows;" 2>/dev/null || echo "0")
        if [[ $ARROW_COUNT -gt 0 ]]; then
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
    warning "No source database found at $SOURCE_DB"
fi

# Copy data directory if it exists
if [[ -d "$SOURCE_DATA_DIR" ]]; then
    log "Copying data directory..."
    cp -r "$SOURCE_DATA_DIR" "$DOCKER_DATA_DIR/"
    
    # Count processed files
    PROCESSED_FILES=$(find "$DOCKER_DATA_DIR/data/processed" -name "*.json" 2>/dev/null | wc -l)
    success "Copied data directory with $PROCESSED_FILES processed JSON files"
else
    warning "No source data directory found at $SOURCE_DATA_DIR"
fi

# Set proper permissions
chmod -R 755 "$DOCKER_DATA_DIR"
success "Set permissions on Docker data directory"

# Create volume mapping info
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

- Database arrows: $(sqlite3 "$DOCKER_DATA_DIR/arrow_database.db" "SELECT COUNT(*) FROM arrows;" 2>/dev/null || echo "N/A")
- Processed files: $(find "$DOCKER_DATA_DIR/data/processed" -name "*.json" 2>/dev/null | wc -l || echo "0")
- Image files: $(find "$DOCKER_DATA_DIR/data/images" -name "*.jpg" -o -name "*.png" -o -name "*.webp" 2>/dev/null | wc -l || echo "0")
EOF

success "Created README.md with volume information"

# Update docker-compose files to use the prepared data
log "Updating docker-compose configurations..."

# Update docker-compose.yml
if [[ -f "$PROJECT_ROOT/docker-compose.yml" ]]; then
    # Check if volume mapping already exists
    if grep -q "docker-data" "$PROJECT_ROOT/docker-compose.yml"; then
        log "Docker compose already has docker-data volume mapping"
    else
        log "Consider updating docker-compose.yml to use ./docker-data:/app/data volume mapping"
    fi
fi

# Update docker-compose.ssl.yml  
if [[ -f "$PROJECT_ROOT/docker-compose.ssl.yml" ]]; then
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

if [[ -f "$DOCKER_DATA_DIR/arrow_database.db" ]]; then
    DB_SIZE=$(du -h "$DOCKER_DATA_DIR/arrow_database.db" | cut -f1)
    success "Database: $DB_SIZE"
else
    error "Database: Not found"
fi

if [[ -d "$DOCKER_DATA_DIR/data" ]]; then
    DATA_SIZE=$(du -sh "$DOCKER_DATA_DIR/data" | cut -f1)
    success "Data directory: $DATA_SIZE"
else
    error "Data directory: Not found"
fi

TOTAL_SIZE=$(du -sh "$DOCKER_DATA_DIR" | cut -f1)
success "Total volume size: $TOTAL_SIZE"

echo
log "Next Steps:"
echo "1. Update docker-compose.yml volume mappings if needed"
echo "2. Run: docker-compose up -d"
echo "3. Check container logs: docker-compose logs api"

echo
success "Docker data preparation completed!"