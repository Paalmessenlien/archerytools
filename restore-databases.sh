#!/bin/bash
# Database Restore Script for ArrowTuner Production System
# Restores databases from backup files

set -e

# Configuration
BACKUP_DIR="/app/backups"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_MANAGER="$SCRIPT_DIR/arrow_scraper/backup_manager.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 ArrowTuner Database Restore System${NC}"
echo "========================================"

# Check if running in Docker
if [ -f "/.dockerenv" ]; then
    echo -e "${BLUE}🐳 Running inside Docker container${NC}"
    IN_DOCKER=true
else
    echo -e "${BLUE}💻 Running on host system${NC}"
    IN_DOCKER=false
fi

# Function to run backup manager
run_backup_manager() {
    if [ "$IN_DOCKER" = true ]; then
        cd /app && python3 backup_manager.py "$@"
    else
        cd "$SCRIPT_DIR/arrow_scraper" && python3 backup_manager.py "$@"
    fi
}

# Parse command line arguments
BACKUP_FILE=""
ARROW_DB_ONLY=false
USER_DB_ONLY=false
FORCE=false
LIST_ONLY=false
VERIFY_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --file)
            BACKUP_FILE="$2"
            shift 2
            ;;
        --arrow-db-only)
            ARROW_DB_ONLY=true
            shift
            ;;
        --user-db-only)
            USER_DB_ONLY=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --list|-l)
            LIST_ONLY=true
            shift
            ;;
        --verify|-v)
            VERIFY_ONLY=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --file FILE          Backup file to restore from"
            echo "  --arrow-db-only      Restore only arrow database"
            echo "  --user-db-only       Restore only user database"
            echo "  --force              Skip confirmation prompt"
            echo "  --list, -l           List available backups"
            echo "  --verify, -v         Verify backup file integrity"
            echo "  --help, -h           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --list                                    # List available backups"
            echo "  $0 --file backup.tar.gz                     # Restore from specific file"
            echo "  $0 --file backup.tar.gz --user-db-only      # Restore only user data"
            echo "  $0 --file backup.tar.gz --force             # Restore without confirmation"
            echo "  $0 --verify --file backup.tar.gz            # Verify backup integrity"
            exit 0
            ;;
        *)
            if [ -z "$BACKUP_FILE" ] && [[ "$1" =~ \.tar\.gz$ ]]; then
                BACKUP_FILE="$1"
            else
                echo -e "${RED}❌ Unknown option: $1${NC}"
                echo "Use --help for usage information"
                exit 1
            fi
            shift
            ;;
    esac
done

# List backups if requested
if [ "$LIST_ONLY" = true ]; then
    echo -e "\n${BLUE}📋 Available backups:${NC}"
    run_backup_manager list
    exit 0
fi

# Verify backup if requested
if [ "$VERIFY_ONLY" = true ]; then
    if [ -z "$BACKUP_FILE" ]; then
        echo -e "${RED}❌ Please specify a backup file to verify with --file${NC}"
        exit 1
    fi
    
    echo -e "\n${YELLOW}🔍 Verifying backup file...${NC}"
    if run_backup_manager verify "$BACKUP_FILE"; then
        echo -e "\n${GREEN}✅ Backup verification passed!${NC}"
        exit 0
    else
        echo -e "\n${RED}❌ Backup verification failed!${NC}"
        exit 1
    fi
fi

# Check if backup file is specified
if [ -z "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Please specify a backup file to restore from${NC}"
    echo -e "${BLUE}💡 Use --list to see available backups${NC}"
    echo -e "${BLUE}💡 Use --file <backup.tar.gz> to specify a backup file${NC}"
    exit 1
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Backup file not found: $BACKUP_FILE${NC}"
    
    # Try to find it in backup directory
    BACKUP_BASENAME=$(basename "$BACKUP_FILE")
    BACKUP_IN_DIR="$BACKUP_DIR/$BACKUP_BASENAME"
    
    if [ -f "$BACKUP_IN_DIR" ]; then
        echo -e "${YELLOW}💡 Found backup in backup directory: $BACKUP_IN_DIR${NC}"
        BACKUP_FILE="$BACKUP_IN_DIR"
    else
        echo -e "${BLUE}💡 Use --list to see available backups${NC}"
        exit 1
    fi
fi

# Verify backup before restore
echo -e "\n${YELLOW}🔍 Verifying backup integrity...${NC}"
if ! run_backup_manager verify "$BACKUP_FILE"; then
    echo -e "\n${RED}❌ Backup verification failed! Restore aborted.${NC}"
    exit 1
fi

# Prepare restore arguments
RESTORE_ARGS="restore $BACKUP_FILE"
if [ "$ARROW_DB_ONLY" = true ]; then
    RESTORE_ARGS="$RESTORE_ARGS --arrow-db-only"
fi
if [ "$USER_DB_ONLY" = true ]; then
    RESTORE_ARGS="$RESTORE_ARGS --user-db-only"
fi
if [ "$FORCE" = true ]; then
    RESTORE_ARGS="$RESTORE_ARGS --force"
fi

# Show warning if not forced
if [ "$FORCE" != true ]; then
    echo -e "\n${YELLOW}⚠️  WARNING: This will overwrite existing databases!${NC}"
    if [ "$ARROW_DB_ONLY" != true ] && [ "$USER_DB_ONLY" != true ]; then
        echo -e "${YELLOW}   Both arrow and user databases will be replaced${NC}"
    elif [ "$ARROW_DB_ONLY" = true ]; then
        echo -e "${YELLOW}   Arrow database will be replaced${NC}"
    elif [ "$USER_DB_ONLY" = true ]; then
        echo -e "${YELLOW}   User database will be replaced${NC}"
    fi
    echo -e "\n${BLUE}💡 Existing databases will be backed up before restore${NC}"
    echo -e "${BLUE}💡 Use --force to skip this confirmation${NC}"
fi

# Execute restore
echo -e "\n${YELLOW}🔄 Starting restore process...${NC}"

if run_backup_manager $RESTORE_ARGS; then
    echo -e "\n${GREEN}✅ Restore completed successfully!${NC}"
    
    # Suggest restart if in Docker
    if [ "$IN_DOCKER" = true ]; then
        echo -e "\n${BLUE}💡 Consider restarting the application to ensure all components use the restored data${NC}"
    else
        echo -e "\n${BLUE}💡 Consider restarting Docker containers to ensure all components use the restored data${NC}"
        echo -e "${BLUE}   docker-compose restart${NC}"
    fi
else
    echo -e "\n${RED}❌ Restore failed!${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 Restore operation completed!${NC}"