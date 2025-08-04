#!/bin/bash
#
# Unified Restore Script for ArrowTuner Platform
# Works with the unified architecture for all deployment modes
#
# Usage:
#   ./restore-unified.sh --list                    # List available backups
#   ./restore-unified.sh --file backup.tar.gz      # Restore from specific backup
#   ./restore-unified.sh --verify --file backup.tar.gz  # Verify backup integrity

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Default values
ACTION=""
BACKUP_FILE=""
FORCE=false
USER_DB_ONLY=false
COMPOSE_FILE="docker-compose.unified.yml"

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --list)
            ACTION="list"
            shift
            ;;
        --file)
            ACTION="restore"
            BACKUP_FILE="$2"
            shift 2
            ;;
        --verify)
            ACTION="verify"
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --user-db-only)
            USER_DB_ONLY=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --list          List available backups"
            echo "  --file FILE     Restore from specific backup file"
            echo "  --verify        Verify backup integrity (use with --file)"
            echo "  --force         Skip confirmation prompt"
            echo "  --user-db-only  Restore only user database"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            print_message "$RED" "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to check services
check_services() {
    print_message "$BLUE" "🔍 Checking services..."
    
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_message "$YELLOW" "⚠️  Services not running. Starting them..."
        ./start-unified.sh
        sleep 5
    fi
    
    print_message "$GREEN" "✅ Services are running"
}

# Function to list backups
list_backups() {
    print_message "$BLUE" "📋 Available backups:"
    
    docker-compose -f "$COMPOSE_FILE" exec -T api python3 /app/backup_manager.py list
}

# Function to verify backup
verify_backup() {
    print_message "$BLUE" "🔍 Verifying backup: $BACKUP_FILE"
    
    docker-compose -f "$COMPOSE_FILE" exec -T api python3 /app/backup_manager.py verify "$BACKUP_FILE"
    
    if [[ $? -eq 0 ]]; then
        print_message "$GREEN" "✅ Backup is valid"
    else
        print_message "$RED" "❌ Backup verification failed"
        exit 1
    fi
}

# Function to confirm restore
confirm_restore() {
    if [[ "$FORCE" == "false" ]]; then
        print_message "$YELLOW" "⚠️  WARNING: This will replace current databases!"
        read -p "Are you sure you want to restore from $BACKUP_FILE? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_message "$YELLOW" "Restore cancelled"
            exit 0
        fi
    fi
}

# Function to restore backup
restore_backup() {
    print_message "$BLUE" "🔄 Restoring from backup: $BACKUP_FILE"
    
    # Stop services to avoid database locks
    print_message "$YELLOW" "⏸️  Stopping services..."
    docker-compose -f "$COMPOSE_FILE" stop api frontend
    
    # Run restore
    RESTORE_CMD="docker-compose -f $COMPOSE_FILE run --rm api python3 /app/backup_manager.py restore $BACKUP_FILE"
    
    if [[ "$USER_DB_ONLY" == "true" ]]; then
        RESTORE_CMD="$RESTORE_CMD --user-db-only"
    fi
    
    $RESTORE_CMD
    
    if [[ $? -eq 0 ]]; then
        print_message "$GREEN" "✅ Restore completed successfully"
    else
        print_message "$RED" "❌ Restore failed"
        exit 1
    fi
    
    # Restart services
    print_message "$BLUE" "▶️  Restarting services..."
    docker-compose -f "$COMPOSE_FILE" start api frontend
    
    # Wait for services to be healthy
    sleep 5
    
    # Verify services are running
    docker-compose -f "$COMPOSE_FILE" ps
}

# Main execution
main() {
    print_message "$GREEN" "🏹 ArrowTuner Unified Restore Script"
    print_message "$GREEN" "===================================="
    
    # Check services
    check_services
    
    # Execute action
    case "$ACTION" in
        "list")
            list_backups
            ;;
        "verify")
            if [[ -z "$BACKUP_FILE" ]]; then
                print_message "$RED" "❌ Please specify backup file with --file"
                exit 1
            fi
            verify_backup
            ;;
        "restore")
            if [[ -z "$BACKUP_FILE" ]]; then
                print_message "$RED" "❌ Please specify backup file with --file"
                exit 1
            fi
            confirm_restore
            restore_backup
            ;;
        *)
            print_message "$RED" "❌ Please specify an action: --list, --file, or --verify"
            exit 1
            ;;
    esac
    
    print_message "$GREEN" "\n✅ Operation completed!"
}

# Run main function
main "$@"