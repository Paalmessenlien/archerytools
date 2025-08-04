#!/bin/bash
#
# Unified Stop Script for ArrowTuner Platform
# Gracefully stop all services
#
# Usage:
#   ./stop-unified.sh              # Stop all services
#   ./stop-unified.sh --remove     # Stop and remove containers
#   ./stop-unified.sh --clean      # Stop, remove containers and volumes

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
REMOVE_CONTAINERS=false
CLEAN_VOLUMES=false
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
        --remove)
            REMOVE_CONTAINERS=true
            shift
            ;;
        --clean)
            REMOVE_CONTAINERS=true
            CLEAN_VOLUMES=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --remove    Stop and remove containers"
            echo "  --clean     Stop, remove containers and volumes (DATA WILL BE LOST!)"
            echo "  --help      Show this help message"
            exit 0
            ;;
        *)
            print_message "$RED" "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to confirm clean operation
confirm_clean() {
    if [[ "$CLEAN_VOLUMES" == "true" ]]; then
        print_message "$RED" "⚠️  WARNING: This will DELETE ALL DATA including databases!"
        print_message "$YELLOW" "   Make sure you have backups if needed."
        read -p "Are you absolutely sure? Type 'DELETE' to confirm: " -r
        echo
        if [[ "$REPLY" != "DELETE" ]]; then
            print_message "$YELLOW" "Operation cancelled"
            exit 0
        fi
    fi
}

# Function to stop services
stop_services() {
    print_message "$BLUE" "⏹️  Stopping services..."
    
    # Check if compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        print_message "$RED" "❌ Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    # Stop services
    docker-compose -f "$COMPOSE_FILE" stop
    
    print_message "$GREEN" "✅ Services stopped"
}

# Function to remove containers
remove_containers() {
    if [[ "$REMOVE_CONTAINERS" == "true" ]]; then
        print_message "$BLUE" "🗑️  Removing containers..."
        
        docker-compose -f "$COMPOSE_FILE" down --remove-orphans
        
        print_message "$GREEN" "✅ Containers removed"
    fi
}

# Function to clean volumes
clean_volumes() {
    if [[ "$CLEAN_VOLUMES" == "true" ]]; then
        print_message "$BLUE" "🗑️  Removing volumes..."
        
        docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans
        
        print_message "$GREEN" "✅ Volumes removed"
    fi
}

# Function to show status
show_status() {
    print_message "$BLUE" "\n📊 Current status:"
    
    # Check for running containers
    if docker-compose -f "$COMPOSE_FILE" ps 2>/dev/null | grep -q "Up"; then
        print_message "$YELLOW" "Some services may still be running:"
        docker-compose -f "$COMPOSE_FILE" ps
    else
        print_message "$GREEN" "All services are stopped"
    fi
    
    # Check for volumes if not cleaned
    if [[ "$CLEAN_VOLUMES" == "false" ]]; then
        print_message "$BLUE" "\n💾 Data volumes (preserved):"
        docker volume ls | grep -E "arrowtuner|databases|logs|backups" || echo "  No ArrowTuner volumes found"
    fi
}

# Main execution
main() {
    print_message "$GREEN" "🏹 ArrowTuner Unified Stop Script"
    print_message "$GREEN" "================================="
    
    # Confirm clean operation if requested
    confirm_clean
    
    # Stop services
    stop_services
    
    # Remove containers if requested
    remove_containers
    
    # Clean volumes if requested
    clean_volumes
    
    # Show status
    show_status
    
    print_message "$GREEN" "\n✅ Operation completed!"
}

# Run main function
main "$@"