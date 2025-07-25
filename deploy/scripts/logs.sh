#!/bin/bash
# Arrow Tuning Platform - Log Management Script

set -euo pipefail

# Configuration
LOG_DIR="/opt/arrowtuner/logs"
NGINX_LOG_DIR="/var/log/nginx"
SUPERVISOR_LOG_DIR="/var/log/supervisor"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    echo "Arrow Tuning Platform - Log Management"
    echo "======================================"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  tail      - Follow live logs (default)"
    echo "  show      - Show recent log entries"
    echo "  error     - Show recent errors"
    echo "  access    - Show nginx access logs"
    echo "  clean     - Clean old log files"
    echo "  size      - Show log file sizes"
    echo "  rotate    - Force log rotation"
    echo ""
    echo "Options:"
    echo "  -n NUM    - Number of lines to show (default: 50)"
    echo "  -f        - Follow logs (for show command)"
    echo "  -s        - Show system logs (supervisor/systemd)"
    echo ""
    echo "Examples:"
    echo "  $0 tail                 # Follow all application logs"
    echo "  $0 show -n 100         # Show last 100 lines"
    echo "  $0 error               # Show recent errors"
    echo "  $0 access -n 50        # Show last 50 access log entries"
    echo "  $0 size                # Show log file sizes"
}

# Function to follow live logs
tail_logs() {
    local lines="${1:-50}"
    
    echo -e "${GREEN}Following Arrow Tuning Platform logs...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to exit${NC}"
    echo ""
    
    # Build tail command for multiple files
    local log_files=()
    
    # Application logs
    [[ -f "$LOG_DIR/gunicorn.log" ]] && log_files+=("$LOG_DIR/gunicorn.log")
    [[ -f "$LOG_DIR/arrowtuner.log" ]] && log_files+=("$LOG_DIR/arrowtuner.log")
    
    # Nginx logs
    [[ -f "$NGINX_LOG_DIR/arrowtuner_error.log" ]] && log_files+=("$NGINX_LOG_DIR/arrowtuner_error.log")
    
    if [[ ${#log_files[@]} -gt 0 ]]; then
        tail -f "${log_files[@]}"
    else
        echo -e "${RED}No log files found${NC}"
        exit 1
    fi
}

# Function to show recent log entries
show_logs() {
    local lines="${1:-50}"
    local follow="${2:-false}"
    
    echo -e "${GREEN}Arrow Tuning Platform Logs (last $lines lines)${NC}"
    echo "=============================================="
    echo ""
    
    # Application logs
    if [[ -f "$LOG_DIR/gunicorn.log" ]]; then
        echo -e "${BLUE}Gunicorn Application Log:${NC}"
        if [[ "$follow" == "true" ]]; then
            tail -f -n "$lines" "$LOG_DIR/gunicorn.log"
        else
            tail -n "$lines" "$LOG_DIR/gunicorn.log"
        fi
        echo ""
    fi
    
    if [[ -f "$LOG_DIR/arrowtuner.log" ]]; then
        echo -e "${BLUE}Application Log:${NC}"
        if [[ "$follow" == "true" ]]; then
            tail -f -n "$lines" "$LOG_DIR/arrowtuner.log"
        else
            tail -n "$lines" "$LOG_DIR/arrowtuner.log"
        fi
        echo ""
    fi
    
    # System logs if requested
    if [[ "${3:-false}" == "true" ]]; then
        echo -e "${BLUE}System Logs:${NC}"
        if command -v supervisorctl >/dev/null 2>&1; then
            echo "Supervisor status:"
            supervisorctl status arrowtuner || true
            echo ""
        fi
        
        if systemctl is-active --quiet arrowtuner 2>/dev/null; then
            echo "Systemd journal (last $lines entries):"
            journalctl -u arrowtuner -n "$lines" --no-pager || true
            echo ""
        fi
    fi
}

# Function to show errors
show_errors() {
    local lines="${1:-50}"
    
    echo -e "${RED}Recent Errors and Warnings${NC}"
    echo "=========================="
    echo ""
    
    local log_files=(
        "$LOG_DIR/gunicorn.log"
        "$LOG_DIR/arrowtuner.log"
        "$NGINX_LOG_DIR/arrowtuner_error.log"
        "/var/log/supervisor/supervisord.log"
    )
    
    for log_file in "${log_files[@]}"; do
        if [[ -f "$log_file" ]]; then
            local errors
            errors=$(tail -n 1000 "$log_file" | grep -i "error\|exception\|critical\|warning" | tail -n "$lines" || true)
            
            if [[ -n "$errors" ]]; then
                echo -e "${BLUE}$(basename "$log_file"):${NC}"
                echo "$errors"
                echo ""
            fi
        fi
    done
    
    # Check system journal for errors
    if systemctl is-active --quiet arrowtuner 2>/dev/null; then
        local journal_errors
        journal_errors=$(journalctl -u arrowtuner -p err -n "$lines" --no-pager || true)
        if [[ -n "$journal_errors" ]]; then
            echo -e "${BLUE}Systemd Journal Errors:${NC}"
            echo "$journal_errors"
            echo ""
        fi
    fi
}

# Function to show access logs
show_access_logs() {
    local lines="${1:-50}"
    
    echo -e "${GREEN}Nginx Access Logs (last $lines entries)${NC}"
    echo "======================================="
    echo ""
    
    if [[ -f "$NGINX_LOG_DIR/arrowtuner_access.log" ]]; then
        tail -n "$lines" "$NGINX_LOG_DIR/arrowtuner_access.log"
    else
        echo -e "${YELLOW}No access log found at $NGINX_LOG_DIR/arrowtuner_access.log${NC}"
    fi
}

# Function to show log file sizes
show_sizes() {
    echo -e "${GREEN}Log File Sizes${NC}"
    echo "=============="
    echo ""
    
    # Application logs
    echo -e "${BLUE}Application Logs:${NC}"
    if [[ -d "$LOG_DIR" ]]; then
        find "$LOG_DIR" -name "*.log" -exec ls -lh {} \; 2>/dev/null | awk '{print $5, $9}' || echo "No application logs found"
    fi
    echo ""
    
    # Nginx logs
    echo -e "${BLUE}Nginx Logs:${NC}"
    if [[ -d "$NGINX_LOG_DIR" ]]; then
        find "$NGINX_LOG_DIR" -name "*arrowtuner*" -exec ls -lh {} \; 2>/dev/null | awk '{print $5, $9}' || echo "No nginx logs found"
    fi
    echo ""
    
    # Supervisor logs
    echo -e "${BLUE}Supervisor Logs:${NC}"
    if [[ -d "$SUPERVISOR_LOG_DIR" ]]; then
        find "$SUPERVISOR_LOG_DIR" -name "*arrowtuner*" -exec ls -lh {} \; 2>/dev/null | awk '{print $5, $9}' || echo "No supervisor logs found"
    fi
    echo ""
    
    # Total disk usage
    echo -e "${BLUE}Total Log Directory Sizes:${NC}"
    for dir in "$LOG_DIR" "$NGINX_LOG_DIR" "$SUPERVISOR_LOG_DIR"; do
        if [[ -d "$dir" ]]; then
            echo "$(du -sh "$dir" 2>/dev/null || echo "0B $dir")"
        fi
    done
}

# Function to clean old logs
clean_logs() {
    local days="${1:-30}"
    
    echo -e "${YELLOW}Cleaning logs older than $days days...${NC}"
    
    # Clean application logs
    if [[ -d "$LOG_DIR" ]]; then
        find "$LOG_DIR" -name "*.log.*" -mtime +$days -delete 2>/dev/null || true
        echo "✓ Cleaned old application logs"
    fi
    
    # Clean nginx logs (be careful with system logs)
    find "$NGINX_LOG_DIR" -name "*arrowtuner*.gz" -mtime +$days -delete 2>/dev/null || true
    echo "✓ Cleaned old nginx logs"
    
    # Clean supervisor logs
    find "$SUPERVISOR_LOG_DIR" -name "*arrowtuner*.log.*" -mtime +$days -delete 2>/dev/null || true
    echo "✓ Cleaned old supervisor logs"
    
    echo -e "${GREEN}Log cleanup completed${NC}"
}

# Function to force log rotation
rotate_logs() {
    echo -e "${YELLOW}Forcing log rotation...${NC}"
    
    # Rotate application logs manually
    if [[ -f "$LOG_DIR/arrowtuner.log" ]]; then
        mv "$LOG_DIR/arrowtuner.log" "$LOG_DIR/arrowtuner.log.$(date +%Y%m%d-%H%M%S)"
        touch "$LOG_DIR/arrowtuner.log"
        chown arrowtuner:arrowtuner "$LOG_DIR/arrowtuner.log"
        echo "✓ Rotated application log"
    fi
    
    # Force system logrotate
    if command -v logrotate >/dev/null 2>&1; then
        logrotate -f /etc/logrotate.d/arrowtuner 2>/dev/null || true
        echo "✓ Forced system log rotation"
    fi
    
    # Restart services to reopen log files
    if supervisorctl status arrowtuner >/dev/null 2>&1; then
        supervisorctl restart arrowtuner
        echo "✓ Restarted application service"
    elif systemctl is-active --quiet arrowtuner; then
        systemctl restart arrowtuner
        echo "✓ Restarted application service"
    fi
    
    echo -e "${GREEN}Log rotation completed${NC}"
}

# Parse command line arguments
COMMAND="${1:-tail}"
LINES=50
FOLLOW=false
SYSTEM=false

shift || true

while [[ $# -gt 0 ]]; do
    case $1 in
        -n)
            LINES="$2"
            shift 2
            ;;
        -f)
            FOLLOW=true
            shift
            ;;
        -s)
            SYSTEM=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Execute commands
case "$COMMAND" in
    "tail")
        tail_logs "$LINES"
        ;;
    "show")
        show_logs "$LINES" "$FOLLOW" "$SYSTEM"
        ;;
    "error"|"errors")
        show_errors "$LINES"
        ;;
    "access")
        show_access_logs "$LINES"
        ;;
    "clean")
        clean_logs
        ;;
    "size"|"sizes")
        show_sizes
        ;;
    "rotate")
        rotate_logs
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac