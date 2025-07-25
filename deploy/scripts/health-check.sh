#!/bin/bash
# Arrow Tuning Platform - Health Check Script
# Monitors application health and sends alerts

set -euo pipefail

# Configuration
APP_URL="${APP_URL:-http://localhost:5000}"
HEALTH_ENDPOINT="$APP_URL/health"
LOG_FILE="/opt/arrowtuner/logs/health-check.log"
ALERT_EMAIL="${ALERT_EMAIL:-}"
MAX_RESPONSE_TIME=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

send_alert() {
    local status="$1"
    local message="$2"
    
    log "ALERT: $status - $message"
    
    if [[ -n "$ALERT_EMAIL" ]] && command -v mail >/dev/null 2>&1; then
        echo -e "$message\n\nTime: $(date)\nServer: $(hostname)" | \
            mail -s "Arrow Tuning Platform Alert: $status" "$ALERT_EMAIL"
    fi
}

# Function to check application health
check_application() {
    local start_time=$(date +%s)
    local http_code
    local response_time
    
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$MAX_RESPONSE_TIME" "$HEALTH_ENDPOINT" 2>/dev/null || echo "000")
    local end_time=$(date +%s)
    response_time=$((end_time - start_time))
    
    if [[ "$http_code" == "200" ]]; then
        if [[ $response_time -le $MAX_RESPONSE_TIME ]]; then
            log "✓ Application health check passed (${response_time}s)"
            return 0
        else
            send_alert "SLOW_RESPONSE" "Application responding slowly: ${response_time}s (max: ${MAX_RESPONSE_TIME}s)"
            return 1
        fi
    else
        send_alert "SERVICE_DOWN" "Application health check failed: HTTP $http_code"
        return 1
    fi
}

# Function to check database
check_database() {
    local db_path="/opt/arrowtuner/data/arrow_database.db"
    
    if [[ -f "$db_path" ]]; then
        if sqlite3 "$db_path" "SELECT COUNT(*) FROM arrows LIMIT 1;" >/dev/null 2>&1; then
            log "✓ Database check passed"
            return 0
        else
            send_alert "DATABASE_ERROR" "Database query failed"
            return 1
        fi
    else
        send_alert "DATABASE_MISSING" "Database file not found: $db_path"
        return 1
    fi
}

# Function to check disk space
check_disk_space() {
    local threshold=90
    local usage
    
    usage=$(df /opt/arrowtuner | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [[ $usage -lt $threshold ]]; then
        log "✓ Disk space check passed (${usage}% used)"
        return 0
    else
        send_alert "DISK_SPACE_LOW" "Disk space usage is ${usage}% (threshold: ${threshold}%)"
        return 1
    fi
}

# Function to check memory usage
check_memory() {
    local threshold=90
    local usage
    
    usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [[ $usage -lt $threshold ]]; then
        log "✓ Memory check passed (${usage}% used)"
        return 0
    else
        send_alert "MEMORY_HIGH" "Memory usage is ${usage}% (threshold: ${threshold}%)"
        return 1
    fi
}

# Function to check service status
check_service() {
    if supervisorctl status arrowtuner | grep -q "RUNNING"; then
        log "✓ Supervisor service check passed"
        return 0
    elif systemctl is-active --quiet arrowtuner; then
        log "✓ Systemd service check passed"
        return 0
    else
        send_alert "SERVICE_STOPPED" "Arrow Tuning service is not running"
        return 1
    fi
}

# Function to check log files for errors
check_logs() {
    local error_count
    local log_files=(
        "/opt/arrowtuner/logs/gunicorn.log"
        "/opt/arrowtuner/logs/arrowtuner.log"
        "/var/log/nginx/arrowtuner_error.log"
    )
    
    for log_file in "${log_files[@]}"; do
        if [[ -f "$log_file" ]]; then
            error_count=$(tail -100 "$log_file" | grep -i "error\|exception\|critical" | wc -l || echo "0")
            if [[ $error_count -gt 5 ]]; then
                send_alert "LOG_ERRORS" "High error count ($error_count) in $log_file"
                return 1
            fi
        fi
    done
    
    log "✓ Log file check passed"
    return 0
}

# Main health check function
main() {
    local overall_status=0
    
    log "Starting health check..."
    
    # Run all checks
    check_application || overall_status=1
    check_database || overall_status=1
    check_disk_space || overall_status=1
    check_memory || overall_status=1
    check_service || overall_status=1
    check_logs || overall_status=1
    
    if [[ $overall_status -eq 0 ]]; then
        log "✓ All health checks passed"
        exit 0
    else
        log "✗ Some health checks failed"
        exit 1
    fi
}

# Handle command line arguments
case "${1:-check}" in
    "check")
        main
        ;;
    "app"|"application")
        check_application
        ;;
    "db"|"database")
        check_database
        ;;
    "disk")
        check_disk_space
        ;;
    "memory")
        check_memory
        ;;
    "service")
        check_service
        ;;
    "logs")
        check_logs
        ;;
    "status")
        echo "Arrow Tuning Platform Health Status"
        echo "==================================="
        echo "Timestamp: $(date)"
        echo "Server: $(hostname)"
        echo ""
        
        # Quick status check
        if check_application &>/dev/null && check_service &>/dev/null; then
            echo -e "${GREEN}Status: HEALTHY${NC}"
        else
            echo -e "${RED}Status: UNHEALTHY${NC}"
        fi
        ;;
    *)
        echo "Usage: $0 [check|app|db|disk|memory|service|logs|status]"
        echo ""
        echo "Commands:"
        echo "  check     - Run all health checks (default)"
        echo "  app       - Check application response"
        echo "  db        - Check database connectivity"
        echo "  disk      - Check disk space"
        echo "  memory    - Check memory usage"
        echo "  service   - Check service status"
        echo "  logs      - Check for errors in logs"
        echo "  status    - Show quick status overview"
        exit 1
        ;;
esac