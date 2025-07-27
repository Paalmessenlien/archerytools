#!/bin/bash
# Arrow Tuning Platform - Backup Script

set -euo pipefail

# Configuration
BACKUP_DIR="/opt/arrowtuner/backups"
DATA_DIR="/opt/arrowtuner/data"
APP_DIR="/opt/arrowtuner/app"
LOG_FILE="/opt/arrowtuner/logs/backup.log"
RETENTION_DAYS=30
COMPRESSION_LEVEL=6

# Remote backup configuration (optional)
REMOTE_BACKUP_ENABLED="${REMOTE_BACKUP_ENABLED:-false}"
REMOTE_HOST="${REMOTE_HOST:-}"
REMOTE_USER="${REMOTE_USER:-}"
REMOTE_PATH="${REMOTE_PATH:-}"
AWS_S3_BUCKET="${AWS_S3_BUCKET:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local message="[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$message" | tee -a "$LOG_FILE"
}

error() {
    log "${RED}ERROR: $1${NC}"
    exit 1
}

warn() {
    log "${YELLOW}WARNING: $1${NC}"
}

info() {
    log "${BLUE}INFO: $1${NC}"
}

success() {
    log "${GREEN}SUCCESS: $1${NC}"
}

# Create backup directory structure
create_backup_structure() {
    local timestamp="$1"
    local backup_path="$BACKUP_DIR/$timestamp"
    
    mkdir -p "$backup_path"/{database,config,logs,data}
    echo "$backup_path"
}

# Backup database
backup_database() {
    local backup_path="$1"
    local arrow_db_file="$DATA_DIR/arrow_database.db"
    local user_db_file="$APP_DIR/arrow_scraper/user_data.db"
    
    info "Backing up databases..."
    
    # Backup arrow_database.db
    if [[ -f "$arrow_db_file" ]]; then
        info "  - Backing up arrow_database.db..."
        sqlite3 "$arrow_db_file" ".dump" | gzip -"$COMPRESSION_LEVEL" > "$backup_path/database/arrow_database.sql.gz"
        cp "$arrow_db_file" "$backup_path/database/"
        gzip -"$COMPRESSION_LEVEL" "$backup_path/database/arrow_database.db"
        success "  - arrow_database.db backup completed"
    else
        warn "  - arrow_database.db not found: $arrow_db_file"
    fi

    # Backup user_data.db
    if [[ -f "$user_db_file" ]]; then
        info "  - Backing up user_data.db..."
        sqlite3 "$user_db_file" ".dump" | gzip -"$COMPRESSION_LEVEL" > "$backup_path/database/user_data.sql.gz"
        cp "$user_db_file" "$backup_path/database/"
        gzip -"$COMPRESSION_LEVEL" "$backup_path/database/user_data.db"
        success "  - user_data.db backup completed"
    else
        warn "  - user_data.db not found: $user_db_file"
    fi
        
    # Database statistics
    local arrow_table_count
    local arrow_count
    local arrow_db_size
    local user_count
    local user_db_size
    
    arrow_table_count=$(sqlite3 "$arrow_db_file" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null || echo "0")
    arrow_count=$(sqlite3 "$arrow_db_file" "SELECT COUNT(*) FROM arrows;" 2>/dev/null || echo "0")
    arrow_db_size=$(du -h "$arrow_db_file" | cut -f1 2>/dev/null || echo "N/A")

    user_count=$(sqlite3 "$user_db_file" "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")
    user_db_size=$(du -h "$user_db_file" | cut -f1 2>/dev/null || echo "N/A")
        
    cat > "$backup_path/database/stats.txt" << EOF
Database Backup Statistics
=========================
Backup Date: $(date)

Arrow Database (arrow_database.db):
  Size: $arrow_db_size
  Table Count: $arrow_table_count
  Arrow Count: $arrow_count

User Database (user_data.db):
  Size: $user_db_size
  User Count: $user_count

Backup Method: SQL dump + Binary copy
Compression: gzip level $COMPRESSION_LEVEL
EOF
    
    success "Database backup process completed"
}

# Backup configuration files
backup_config() {
    local backup_path="$1"
    
    info "Backing up configuration files..."
    
    # Application configuration
    if [[ -f "$APP_DIR/config_production.py" ]]; then
        cp "$APP_DIR/config_production.py" "$backup_path/config/"
    fi
    
    # Environment file (excluding sensitive data)
    if [[ -f "/opt/arrowtuner/.env" ]]; then
        grep -v "SECRET_KEY\|API_KEY\|PASSWORD" "/opt/arrowtuner/.env" > "$backup_path/config/env_sanitized.txt" || true
    fi
    
    # Nginx configuration
    if [[ -f "/etc/nginx/sites-available/arrowtuner" ]]; then
        cp "/etc/nginx/sites-available/arrowtuner" "$backup_path/config/nginx.conf"
    fi
    
    # Supervisor configuration
    if [[ -f "/etc/supervisor/conf.d/arrowtuner.conf" ]]; then
        cp "/etc/supervisor/conf.d/arrowtuner.conf" "$backup_path/config/supervisor.conf"
    fi
    
    # Systemd service files
    if [[ -f "/etc/systemd/system/arrowtuner.service" ]]; then
        cp "/etc/systemd/system/arrowtuner.service" "$backup_path/config/systemd.service"
    fi
    
    success "Configuration backup completed"
}

# Backup application data
backup_app_data() {
    local backup_path="$1"
    
    info "Backing up application data..."
    
    # Processed arrow data
    if [[ -d "$DATA_DIR" ]]; then
        find "$DATA_DIR" -name "*.json" -exec cp {} "$backup_path/data/" \; 2>/dev/null || true
    fi
    
    # Images (sample only due to size)
    if [[ -d "$APP_DIR/data/images" ]]; then
        # Create a list of images instead of copying all
        find "$APP_DIR/data/images" -name "*.jpg" -o -name "*.png" -o -name "*.webp" | head -100 > "$backup_path/data/image_list.txt"
        warn "Image files listed but not backed up due to size (see image_list.txt)"
    fi
    
    # Tuning sessions
    if [[ -d "$APP_DIR" ]]; then
        find "$APP_DIR" -name "*tuning*.json" -exec cp {} "$backup_path/data/" \; 2>/dev/null || true
    fi
    
    success "Application data backup completed"
}

# Backup logs
backup_logs() {
    local backup_path="$1"
    
    info "Backing up recent logs..."
    
    # Application logs (last 7 days)
    find "/opt/arrowtuner/logs" -name "*.log" -mtime -7 -exec cp {} "$backup_path/logs/" \; 2>/dev/null || true
    
    # Nginx logs (last 7 days)
    find "/var/log/nginx" -name "*arrowtuner*" -mtime -7 -exec cp {} "$backup_path/logs/" \; 2>/dev/null || true
    
    # Compress log files
    find "$backup_path/logs" -name "*.log" -exec gzip -"$COMPRESSION_LEVEL" {} \; 2>/dev/null || true
    
    success "Log backup completed"
}

# Create backup archive
create_archive() {
    local backup_path="$1"
    local timestamp="$2"
    local archive_name="arrowtuner-backup-$timestamp.tar.gz"
    local archive_path="$BACKUP_DIR/$archive_name"
    
    info "Creating backup archive..."
    
    cd "$BACKUP_DIR"
    tar -czf "$archive_name" "$timestamp/"
    
    # Remove uncompressed backup directory
    rm -rf "$backup_path"
    
    # Calculate archive size and checksums
    local archive_size
    local md5_hash
    local sha256_hash
    
    archive_size=$(du -h "$archive_path" | cut -f1)
    md5_hash=$(md5sum "$archive_path" | cut -d' ' -f1)
    sha256_hash=$(sha256sum "$archive_path" | cut -d' ' -f1)
    
    # Create checksum file
    cat > "$archive_path.checksums" << EOF
Archive: $archive_name
Size: $archive_size
MD5: $md5_hash
SHA256: $sha256_hash
Created: $(date)
EOF
    
    success "Backup archive created: $archive_name ($archive_size)"
    echo "$archive_path"
}

# Upload to remote storage
upload_remote() {
    local archive_path="$1"
    local archive_name="$(basename "$archive_path")"
    
    if [[ "$REMOTE_BACKUP_ENABLED" != "true" ]]; then
        return 0
    fi
    
    info "Uploading backup to remote storage..."
    
    # SSH/SCP upload
    if [[ -n "$REMOTE_HOST" && -n "$REMOTE_USER" && -n "$REMOTE_PATH" ]]; then
        if command -v scp >/dev/null 2>&1; then
            if scp "$archive_path" "$archive_path.checksums" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/"; then
                success "Backup uploaded via SCP to $REMOTE_HOST"
            else
                warn "SCP upload failed"
            fi
        else
            warn "SCP not available for remote backup"
        fi
    fi
    
    # AWS S3 upload
    if [[ -n "$AWS_S3_BUCKET" ]] && command -v aws >/dev/null 2>&1; then
        if aws s3 cp "$archive_path" "s3://$AWS_S3_BUCKET/arrowtuner-backups/"; then
            aws s3 cp "$archive_path.checksums" "s3://$AWS_S3_BUCKET/arrowtuner-backups/"
            success "Backup uploaded to S3 bucket: $AWS_S3_BUCKET"
        else
            warn "S3 upload failed"
        fi
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    info "Cleaning up old backups (older than $RETENTION_DAYS days)..."
    
    # Local cleanup
    find "$BACKUP_DIR" -name "arrowtuner-backup-*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "*.checksums" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    # Remote cleanup (if configured)
    if [[ "$REMOTE_BACKUP_ENABLED" == "true" && -n "$REMOTE_HOST" && -n "$REMOTE_USER" && -n "$REMOTE_PATH" ]]; then
        ssh "$REMOTE_USER@$REMOTE_HOST" "find '$REMOTE_PATH' -name 'arrowtuner-backup-*.tar.gz' -mtime +$RETENTION_DAYS -delete" 2>/dev/null || warn "Remote cleanup failed"
    fi
    
    success "Old backup cleanup completed"
}

# List existing backups
list_backups() {
    info "Existing backups:"
    echo ""
    
    if [[ -d "$BACKUP_DIR" ]]; then
        find "$BACKUP_DIR" -name "arrowtuner-backup-*.tar.gz" -printf "%T@ %p\n" | sort -nr | head -20 | while read timestamp path; do
            local date_str
            local size
            date_str=$(date -d "@$timestamp" '+%Y-%m-%d %H:%M:%S')
            size=$(du -h "$path" | cut -f1)
            echo "  $date_str - $(basename "$path") ($size)"
        done
    else
        echo "  No backups found"
    fi
    echo ""
}

# Restore from backup
restore_backup() {
    local backup_file="$1"
    
    if [[ ! -f "$backup_file" ]]; then
        error "Backup file not found: $backup_file"
    fi
    
    warn "This will restore from backup and may overwrite current data!"
    read -p "Are you sure you want to continue? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        info "Restore cancelled"
        exit 0
    fi
    
    info "Restoring from backup: $(basename "$backup_file")"
    
    # Stop services
    supervisorctl stop arrowtuner 2>/dev/null || systemctl stop arrowtuner || true
    
    # Extract backup
    local temp_dir
    temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir"
    
    # Find extracted directory
    local extracted_dir
    extracted_dir=$(find "$temp_dir" -maxdepth 1 -type d -name "20*" | head -1)
    
    if [[ -z "$extracted_dir" ]]; then
        error "Could not find extracted backup directory"
    fi
    
    # Restore arrow_database.db
    if [[ -f "$extracted_dir/database/arrow_database.db.gz" ]]; then
        gunzip -c "$extracted_dir/database/arrow_database.db.gz" > "$DATA_DIR/arrow_database.db"
        chown arrowtuner:arrowtuner "$DATA_DIR/arrow_database.db"
        success "Arrow database restored"
    fi

    # Restore user_data.db
    local user_db_file="$APP_DIR/arrow_scraper/user_data.db"
    if [[ -f "$extracted_dir/database/user_data.db.gz" ]]; then
        gunzip -c "$extracted_dir/database/user_data.db.gz" > "$user_db_file"
        chown arrowtuner:arrowtuner "$user_db_file"
        success "User database restored"
    fi
    
    # Restore configuration (manual review recommended)
    if [[ -d "$extracted_dir/config" ]]; then
        cp -r "$extracted_dir/config" "$BACKUP_DIR/restored-config-$(date +%Y%m%d)"
        warn "Configuration files copied to $BACKUP_DIR/restored-config-$(date +%Y%m%d) for manual review"
    fi
    
    # Cleanup
    rm -rf "$temp_dir"
    
    # Start services
    supervisorctl start arrowtuner 2>/dev/null || systemctl start arrowtuner || true
    
    success "Restore completed"
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"
    
    if [[ ! -f "$backup_file" ]]; then
        error "Backup file not found: $backup_file"
    fi
    
    info "Verifying backup integrity: $(basename "$backup_file")"
    
    # Check if checksums file exists
    local checksum_file="$backup_file.checksums"
    if [[ -f "$checksum_file" ]]; then
        local stored_md5
        local stored_sha256
        local current_md5
        local current_sha256
        
        stored_md5=$(grep "MD5:" "$checksum_file" | cut -d' ' -f2)
        stored_sha256=$(grep "SHA256:" "$checksum_file" | cut -d' ' -f2)
        current_md5=$(md5sum "$backup_file" | cut -d' ' -f1)
        current_sha256=$(sha256sum "$backup_file" | cut -d' ' -f1)
        
        if [[ "$stored_md5" == "$current_md5" && "$stored_sha256" == "$current_sha256" ]]; then
            success "Backup integrity verified - checksums match"
        else
            error "Backup integrity check failed - checksums do not match"
        fi
    else
        warn "No checksum file found - performing basic archive test"
    fi
    
    # Test archive extraction
    if tar -tzf "$backup_file" >/dev/null 2>&1; then
        success "Archive structure is valid"
    else
        error "Archive appears to be corrupted"
    fi
}

# Main backup function
perform_backup() {
    local timestamp
    timestamp=$(date +%Y%m%d-%H%M%S)
    
    info "Starting backup process..."
    info "Timestamp: $timestamp"
    
    # Ensure backup directory exists
    mkdir -p "$BACKUP_DIR"
    
    # Create backup structure
    local backup_path
    backup_path=$(create_backup_structure "$timestamp")
    
    # Perform backups
    backup_database "$backup_path"
    backup_config "$backup_path"
    backup_app_data "$backup_path"
    backup_logs "$backup_path"
    
    # Create archive
    local archive_path
    archive_path=$(create_archive "$backup_path" "$timestamp")
    
    # Upload to remote storage
    upload_remote "$archive_path"
    
    # Cleanup old backups
    cleanup_old_backups
    
    success "Backup process completed successfully"
    info "Backup location: $archive_path"
}

# Show help
show_help() {
    echo "Arrow Tuning Platform - Backup Management"
    echo "========================================"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  backup    - Create new backup (default)"
    echo "  list      - List existing backups"
    echo "  restore   - Restore from backup file"
    echo "  verify    - Verify backup integrity"
    echo "  cleanup   - Remove old backups"
    echo ""
    echo "Examples:"
    echo "  $0 backup                                    # Create new backup"
    echo "  $0 list                                      # List all backups"
    echo "  $0 restore /path/to/backup.tar.gz          # Restore from backup"
    echo "  $0 verify /path/to/backup.tar.gz           # Verify backup"
    echo "  $0 cleanup                                   # Clean old backups"
    echo ""
    echo "Environment Variables:"
    echo "  REMOTE_BACKUP_ENABLED  - Enable remote backup (true/false)"
    echo "  REMOTE_HOST           - SSH hostname for remote backup"
    echo "  REMOTE_USER           - SSH username for remote backup"
    echo "  REMOTE_PATH           - Remote path for backups"
    echo "  AWS_S3_BUCKET         - S3 bucket for backup storage"
}

# Parse command line arguments
COMMAND="${1:-backup}"

case "$COMMAND" in
    "backup")
        perform_backup
        ;;
    "list")
        list_backups
        ;;
    "restore")
        if [[ -z "${2:-}" ]]; then
            error "Please specify backup file to restore from"
        fi
        restore_backup "$2"
        ;;
    "verify")
        if [[ -z "${2:-}" ]]; then
            error "Please specify backup file to verify"
        fi
        verify_backup "$2"
        ;;
    "cleanup")
        cleanup_old_backups
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        error "Unknown command: $COMMAND"
        ;;
esac