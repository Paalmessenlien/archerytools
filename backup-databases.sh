#!/bin/bash
# Database Backup Script for ArrowTuner Production System
# Creates comprehensive backups of both arrow and user databases

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

echo -e "${BLUE}🗄️  ArrowTuner Database Backup System${NC}"
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
COMMAND="backup"
BACKUP_NAME=""
ARROW_DB_ONLY=false
USER_DB_ONLY=false
CLEANUP_AFTER=false
KEEP_COUNT=10

while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            BACKUP_NAME="$2"
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
        --cleanup)
            CLEANUP_AFTER=true
            shift
            ;;
        --keep)
            KEEP_COUNT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --name NAME          Custom backup name"
            echo "  --arrow-db-only      Backup only arrow database"
            echo "  --user-db-only       Backup only user database"
            echo "  --cleanup            Cleanup old backups after creating new one"
            echo "  --keep COUNT         Number of backups to keep during cleanup (default: 10)"
            echo "  --help, -h           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                              # Full backup with auto-generated name"
            echo "  $0 --name production_backup     # Full backup with custom name"
            echo "  $0 --user-db-only              # Backup only user data"
            echo "  $0 --cleanup --keep 5          # Full backup and keep only 5 most recent"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Create backup
echo -e "\n${YELLOW}📦 Creating backup...${NC}"

BACKUP_ARGS="backup"
if [ -n "$BACKUP_NAME" ]; then
    BACKUP_ARGS="$BACKUP_ARGS --name $BACKUP_NAME"
fi
if [ "$ARROW_DB_ONLY" = true ]; then
    BACKUP_ARGS="$BACKUP_ARGS --arrow-db-only"
fi
if [ "$USER_DB_ONLY" = true ]; then
    BACKUP_ARGS="$BACKUP_ARGS --user-db-only"
fi

# Execute backup
if run_backup_manager $BACKUP_ARGS; then
    echo -e "\n${GREEN}✅ Backup completed successfully!${NC}"
else
    echo -e "\n${RED}❌ Backup failed!${NC}"
    exit 1
fi

# Cleanup old backups if requested
if [ "$CLEANUP_AFTER" = true ]; then
    echo -e "\n${YELLOW}🗑️  Cleaning up old backups...${NC}"
    if run_backup_manager cleanup --keep $KEEP_COUNT; then
        echo -e "${GREEN}✅ Cleanup completed${NC}"
    else
        echo -e "${YELLOW}⚠️  Cleanup had issues but backup was successful${NC}"
    fi
fi

# List current backups
echo -e "\n${BLUE}📋 Current backups:${NC}"
run_backup_manager list

echo -e "\n${GREEN}🎉 Backup operation completed!${NC}"