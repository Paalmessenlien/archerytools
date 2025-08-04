#!/bin/bash
#
# Unified Backup Script for ArrowTuner Platform
# Works with the unified architecture for all deployment modes
#
# Usage:
#   ./backup-unified.sh                    # Create backup with auto-generated name
#   ./backup-unified.sh --name my_backup   # Create backup with custom name
#   ./backup-unified.sh --cleanup          # Backup and cleanup old backups

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
BACKUP_NAME=""
CLEANUP=false
KEEP_COUNT=5
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
        --name)
            BACKUP_NAME="$2"
            shift 2
            ;;
        --cleanup)
            CLEANUP=true
            shift
            ;;
        --keep)
            KEEP_COUNT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --name NAME     Custom backup name"
            echo "  --cleanup       Remove old backups after creating new one"
            echo "  --keep COUNT    Number of backups to keep (default: 5)"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            print_message "$RED" "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Generate backup name if not provided
if [[ -z "$BACKUP_NAME" ]]; then
    BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
fi

# Function to check if services are running
check_services() {
    print_message "$BLUE" "🔍 Checking services..."
    
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_message "$YELLOW" "⚠️  Services not running. Starting them..."
        ./start-unified.sh
        sleep 5
    fi
    
    print_message "$GREEN" "✅ Services are running"
}

# Function to run backup
run_backup() {
    print_message "$BLUE" "🗄️  Creating backup: $BACKUP_NAME"
    
    # Run backup using the backup manager
    docker-compose -f "$COMPOSE_FILE" exec -T api python3 /app/backup_manager.py backup --name "$BACKUP_NAME"
    
    if [[ $? -eq 0 ]]; then
        print_message "$GREEN" "✅ Backup created successfully"
    else
        print_message "$RED" "❌ Backup failed"
        exit 1
    fi
}

# Function to cleanup old backups
cleanup_backups() {
    if [[ "$CLEANUP" == "true" ]]; then
        print_message "$BLUE" "🧹 Cleaning up old backups (keeping $KEEP_COUNT most recent)..."
        
        docker-compose -f "$COMPOSE_FILE" exec -T api python3 /app/backup_manager.py cleanup --keep "$KEEP_COUNT"
        
        print_message "$GREEN" "✅ Cleanup completed"
    fi
}

# Function to list backups
list_backups() {
    print_message "$BLUE" "📋 Available backups:"
    
    docker-compose -f "$COMPOSE_FILE" exec -T api python3 /app/backup_manager.py list
}

# Main execution
main() {
    print_message "$GREEN" "🏹 ArrowTuner Unified Backup Script"
    print_message "$GREEN" "==================================="
    
    # Check services
    check_services
    
    # Run backup
    run_backup
    
    # Cleanup if requested
    cleanup_backups
    
    # List backups
    list_backups
    
    print_message "$GREEN" "\n✅ Backup operation completed!"
}

# Run main function
main "$@"