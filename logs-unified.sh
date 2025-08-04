#!/bin/bash
#
# Unified Logs Script for ArrowTuner Platform
# View and manage logs from all services
#
# Usage:
#   ./logs-unified.sh              # Follow all logs
#   ./logs-unified.sh api          # Follow API logs only
#   ./logs-unified.sh frontend     # Follow frontend logs only
#   ./logs-unified.sh nginx        # Follow nginx logs only
#   ./logs-unified.sh --tail 100   # Show last 100 lines

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
SERVICE=""
TAIL_LINES="100"
FOLLOW=true
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
        --tail)
            TAIL_LINES="$2"
            shift 2
            ;;
        --no-follow)
            FOLLOW=false
            shift
            ;;
        --help)
            echo "Usage: $0 [SERVICE] [OPTIONS]"
            echo "Services:"
            echo "  api         View API logs"
            echo "  frontend    View frontend logs"
            echo "  nginx       View nginx logs"
            echo "  db-init     View database initialization logs"
            echo "Options:"
            echo "  --tail N    Show last N lines (default: 100)"
            echo "  --no-follow Don't follow log output"
            echo "  --help      Show this help message"
            exit 0
            ;;
        *)
            SERVICE="$1"
            shift
            ;;
    esac
done

# Build docker-compose command
build_logs_command() {
    local cmd="docker-compose -f $COMPOSE_FILE logs"
    
    # Add tail option
    cmd="$cmd --tail $TAIL_LINES"
    
    # Add follow option
    if [[ "$FOLLOW" == "true" ]]; then
        cmd="$cmd -f"
    fi
    
    # Add service if specified
    if [[ -n "$SERVICE" ]]; then
        cmd="$cmd $SERVICE"
    fi
    
    echo "$cmd"
}

# Main execution
main() {
    print_message "$GREEN" "🏹 ArrowTuner Unified Logs Viewer"
    print_message "$GREEN" "================================="
    
    # Check if services are running
    if ! docker-compose -f "$COMPOSE_FILE" ps 2>/dev/null | grep -q "Up"; then
        print_message "$YELLOW" "⚠️  No services are currently running"
        print_message "$YELLOW" "   Run ./start-unified.sh to start services"
        exit 0
    fi
    
    # Build and execute logs command
    LOGS_CMD=$(build_logs_command)
    
    if [[ -n "$SERVICE" ]]; then
        print_message "$BLUE" "📝 Showing logs for: $SERVICE"
    else
        print_message "$BLUE" "📝 Showing logs for all services"
    fi
    
    if [[ "$FOLLOW" == "true" ]]; then
        print_message "$YELLOW" "   Press Ctrl+C to exit"
    fi
    
    echo ""
    
    # Execute logs command
    eval "$LOGS_CMD"
}

# Run main function
main "$@"