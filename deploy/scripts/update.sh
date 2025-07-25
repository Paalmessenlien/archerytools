#!/bin/bash
# Arrow Tuning Platform - Application Update Script

set -euo pipefail

# Configuration
APP_DIR="/opt/arrowtuner"
APP_USER="arrowtuner"
SERVICE_NAME="arrowtuner"
BACKUP_ENABLED=true
GIT_REPO="${GIT_REPO:-}"
GIT_BRANCH="${GIT_BRANCH:-main}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
LOG_FILE="/opt/arrowtuner/logs/update.log"
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root (use sudo)"
fi

# Pre-update backup
create_backup() {
    if [[ "$BACKUP_ENABLED" == "true" ]]; then
        log "Creating pre-update backup..."
        if [[ -f "/opt/arrowtuner/deploy/scripts/backup.sh" ]]; then
            /opt/arrowtuner/deploy/scripts/backup.sh backup
            log "Pre-update backup completed"
        else
            warn "Backup script not found - skipping backup"
        fi
    else
        warn "Backup disabled - skipping pre-update backup"
    fi
}

# Download and prepare new version
prepare_update() {
    local update_dir="/tmp/arrowtuner-update-$(date +%Y%m%d-%H%M%S)"
    
    log "Preparing update in $update_dir"
    mkdir -p "$update_dir"
    
    if [[ -n "$GIT_REPO" ]]; then
        # Update from Git repository
        log "Cloning from Git repository: $GIT_REPO"
        git clone --branch "$GIT_BRANCH" --depth 1 "$GIT_REPO" "$update_dir"
    else
        # Manual update - user should place files in update directory
        error "No update source configured. Set GIT_REPO environment variable or place update files in $update_dir"
    fi
    
    echo "$update_dir"
}

# Validate update package
validate_update() {
    local update_dir="$1"
    
    log "Validating update package..."
    
    # Check required files
    local required_files=(
        "arrow_scraper/webapp.py"
        "arrow_scraper/models.py"
        "arrow_scraper/requirements.txt"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$update_dir/$file" ]]; then
            error "Required file missing in update: $file"
        fi
    done
    
    # Check Python syntax
    if ! python3 -m py_compile "$update_dir/arrow_scraper/webapp.py"; then
        error "Python syntax error in webapp.py"
    fi
    
    log "Update package validation passed"
}

# Stop services
stop_services() {
    log "Stopping services..."
    
    if supervisorctl status arrowtuner >/dev/null 2>&1; then
        supervisorctl stop arrowtuner
        log "Stopped supervisor service"
    elif systemctl is-active --quiet arrowtuner; then
        systemctl stop arrowtuner
        log "Stopped systemd service"
    else
        warn "No running service found"
    fi
}

# Start services
start_services() {
    log "Starting services..."
    
    if [[ -f "/etc/supervisor/conf.d/arrowtuner.conf" ]]; then
        supervisorctl start arrowtuner
        log "Started supervisor service"
    elif [[ -f "/etc/systemd/system/arrowtuner.service" ]]; then
        systemctl start arrowtuner
        log "Started systemd service"
    else
        error "No service configuration found"
    fi
}

# Apply update
apply_update() {
    local update_dir="$1"
    
    log "Applying update..."
    
    # Backup current application
    local backup_app_dir="$APP_DIR/backups/app-pre-update-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_app_dir"
    cp -r "$APP_DIR/app" "$backup_app_dir/"
    log "Current application backed up to $backup_app_dir"
    
    # Copy new application files
    cp -r "$update_dir/arrow_scraper/." "$APP_DIR/app/"
    
    # Copy updated Crawl4AI if present
    if [[ -d "$update_dir/crawl4ai" ]]; then
        cp -r "$update_dir/crawl4ai" "$APP_DIR/"
        log "Updated Crawl4AI library"
    fi
    
    # Set correct permissions
    chown -R $APP_USER:$APP_USER "$APP_DIR/app"
    chown -R $APP_USER:$APP_USER "$APP_DIR/crawl4ai" 2>/dev/null || true
    
    log "Application files updated"
}

# Update dependencies
update_dependencies() {
    log "Updating Python dependencies..."
    
    # Activate virtual environment and update packages
    sudo -u $APP_USER "$APP_DIR/venv/bin/pip" install --upgrade pip
    
    if [[ -f "$APP_DIR/app/requirements.txt" ]]; then
        sudo -u $APP_USER "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/app/requirements.txt" --upgrade
        log "Dependencies updated from requirements.txt"
    else
        warn "No requirements.txt found - skipping dependency update"
    fi
}

# Database migration
migrate_database() {
    log "Checking for database migrations..."
    
    # Check if database migration script exists
    if [[ -f "$APP_DIR/app/migrate_database.py" ]]; then
        log "Running database migration..."
        sudo -u $APP_USER "$APP_DIR/venv/bin/python" "$APP_DIR/app/migrate_database.py"
        log "Database migration completed"
    else
        log "No database migration needed"
    fi
    
    # Rebuild database from processed data if needed
    if [[ -f "$APP_DIR/app/arrow_database.py" ]]; then
        sudo -u $APP_USER "$APP_DIR/venv/bin/python" "$APP_DIR/app/arrow_database.py" --update
        log "Database updated from processed data"
    fi
}

# Test update
test_update() {
    log "Testing updated application..."
    
    # Wait for service to start
    sleep 10
    
    # Health check
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -s http://localhost:5000/health >/dev/null; then
            log "✓ Application health check passed"
            return 0
        fi
        
        ((attempt++))
        sleep 2
    done
    
    error "✗ Application health check failed after update"
}

# Rollback update
rollback_update() {
    local backup_app_dir="$1"
    
    warn "Rolling back update..."
    
    # Stop services
    stop_services
    
    # Restore previous version
    rm -rf "$APP_DIR/app"
    cp -r "$backup_app_dir/app" "$APP_DIR/"
    chown -R $APP_USER:$APP_USER "$APP_DIR/app"
    
    # Start services
    start_services
    
    # Test rollback
    sleep 10
    if curl -s http://localhost:5000/health >/dev/null; then
        log "✓ Rollback successful - application is running"
    else
        error "✗ Rollback failed - manual intervention required"
    fi
}

# Check for updates
check_updates() {
    if [[ -z "$GIT_REPO" ]]; then
        error "No Git repository configured for update checking"
    fi
    
    log "Checking for updates..."
    
    # Get current commit hash
    local current_commit=""
    if [[ -f "$APP_DIR/.git_commit" ]]; then
        current_commit=$(cat "$APP_DIR/.git_commit")
    fi
    
    # Get latest commit from remote
    local latest_commit
    latest_commit=$(git ls-remote "$GIT_REPO" "$GIT_BRANCH" | cut -f1)
    
    if [[ "$current_commit" == "$latest_commit" ]]; then
        log "Application is up to date"
        echo "No updates available"
    else
        log "Update available: $current_commit -> $latest_commit"
        echo "Update available"
        echo "Current: $current_commit"
        echo "Latest: $latest_commit"
    fi
}

# Show current version info
show_version() {
    log "Arrow Tuning Platform Version Information"
    echo "========================================"
    
    # Git commit info
    if [[ -f "$APP_DIR/.git_commit" ]]; then
        echo "Git Commit: $(cat "$APP_DIR/.git_commit")"
    else
        echo "Git Commit: Unknown"
    fi
    
    # Deployment info
    if [[ -f "$APP_DIR/deployment-info.txt" ]]; then
        echo ""
        echo "Deployment Information:"
        cat "$APP_DIR/deployment-info.txt"
    fi
    
    # Application status
    echo ""
    echo "Service Status:"
    if supervisorctl status arrowtuner >/dev/null 2>&1; then
        supervisorctl status arrowtuner
    elif systemctl is-active --quiet arrowtuner; then
        systemctl status arrowtuner --no-pager -l
    else
        echo "Service not running"
    fi
    
    # Database info
    if [[ -f "$APP_DIR/data/arrow_database.db" ]]; then
        local arrow_count
        arrow_count=$(sudo -u $APP_USER sqlite3 "$APP_DIR/data/arrow_database.db" "SELECT COUNT(*) FROM arrows;" 2>/dev/null || echo "Unknown")
        echo ""
        echo "Database Info:"
        echo "Arrows in database: $arrow_count"
        echo "Database size: $(du -h "$APP_DIR/data/arrow_database.db" | cut -f1)"
    fi
}

# Main update function
perform_update() {
    log "Starting Arrow Tuning Platform update..."
    
    # Create backup
    create_backup
    
    # Prepare update
    local update_dir
    update_dir=$(prepare_update)
    
    # Validate update
    validate_update "$update_dir"
    
    # Stop services
    stop_services
    
    # Apply update
    apply_update "$update_dir"
    
    # Update dependencies
    update_dependencies
    
    # Database migration
    migrate_database
    
    # Start services
    start_services
    
    # Test update
    if ! test_update; then
        # Rollback on failure
        local backup_app_dir
        backup_app_dir=$(find "$APP_DIR/backups" -name "app-pre-update-*" -type d | sort | tail -1)
        rollback_update "$backup_app_dir"
        error "Update failed and was rolled back"
    fi
    
    # Record successful update
    if [[ -n "$GIT_REPO" ]]; then
        git -C "$update_dir" rev-parse HEAD > "$APP_DIR/.git_commit"
    fi
    
    # Cleanup
    rm -rf "$update_dir"
    
    log "Update completed successfully!"
    
    # Show new version info
    show_version
}

# Show help
show_help() {
    echo "Arrow Tuning Platform - Update Management"
    echo "========================================"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  update     - Perform application update (default)"
    echo "  check      - Check for available updates"
    echo "  version    - Show current version information"
    echo "  rollback   - Rollback to previous version"
    echo ""
    echo "Examples:"
    echo "  $0 update                    # Update application"
    echo "  $0 check                     # Check for updates"
    echo "  $0 version                   # Show version info"
    echo ""
    echo "Environment Variables:"
    echo "  GIT_REPO      - Git repository URL for updates"
    echo "  GIT_BRANCH    - Git branch to use (default: main)"
    echo "  BACKUP_ENABLED - Create backup before update (default: true)"
}

# Parse command line arguments
COMMAND="${1:-update}"

case "$COMMAND" in
    "update")
        perform_update
        ;;
    "check")
        check_updates
        ;;
    "version"|"info")
        show_version
        ;;
    "rollback")
        # Find most recent backup
        local latest_backup
        latest_backup=$(find "$APP_DIR/backups" -name "app-pre-update-*" -type d | sort | tail -1)
        if [[ -n "$latest_backup" ]]; then
            rollback_update "$(dirname "$latest_backup")"
        else
            error "No backup found for rollback"
        fi
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        error "Unknown command: $COMMAND"
        ;;
esac