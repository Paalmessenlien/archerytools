#!/bin/bash
# Arrow Tuning Platform - System Status Dashboard

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Helper functions
status_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

status_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

status_error() {
    echo -e "${RED}✗${NC} $1"
}

status_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Header
show_header() {
    echo -e "${BOLD}${CYAN}"
    echo "========================================"
    echo "  Arrow Tuning Platform - System Status"
    echo "========================================"
    echo -e "${NC}"
    echo "Server: $(hostname)"
    echo "Time: $(date)"
    echo "Uptime: $(uptime -p)"
    echo ""
}

# Application Status
check_application_status() {
    echo -e "${BOLD}Application Status:${NC}"
    
    # Check if service is running
    if supervisorctl status arrowtuner >/dev/null 2>&1; then
        local supervisor_status
        supervisor_status=$(supervisorctl status arrowtuner | awk '{print $2}')
        if [[ "$supervisor_status" == "RUNNING" ]]; then
            status_ok "Supervisor service running"
        else
            status_error "Supervisor service not running ($supervisor_status)"
        fi
    elif systemctl is-active --quiet arrowtuner; then
        status_ok "Systemd service running"
    else
        status_error "Application service not running"
    fi
    
    # Health check
    if curl -s http://localhost:5000/health >/dev/null 2>&1; then
        local response_time
        response_time=$(curl -w '%{time_total}' -s -o /dev/null http://localhost:5000/health)
        status_ok "Application responding (${response_time}s)"
    else
        status_error "Application not responding"
    fi
    
    # Process information
    local gunicorn_processes
    gunicorn_processes=$(pgrep -f gunicorn | wc -l)
    if [[ $gunicorn_processes -gt 0 ]]; then
        status_info "$gunicorn_processes Gunicorn worker(s) running"
    else
        status_warn "No Gunicorn processes found"
    fi
    
    echo ""
}

# System Resources
check_system_resources() {
    echo -e "${BOLD}System Resources:${NC}"
    
    # CPU usage
    local cpu_usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    echo -e "  CPU Usage: ${cpu_usage}%"
    
    # Memory usage
    local mem_total mem_used mem_usage
    mem_total=$(free -m | awk 'NR==2{print $2}')
    mem_used=$(free -m | awk 'NR==2{print $3}')
    mem_usage=$((mem_used * 100 / mem_total))
    
    if [[ $mem_usage -lt 70 ]]; then
        status_ok "Memory: ${mem_used}MB/${mem_total}MB (${mem_usage}%)"
    elif [[ $mem_usage -lt 90 ]]; then
        status_warn "Memory: ${mem_used}MB/${mem_total}MB (${mem_usage}%)"
    else
        status_error "Memory: ${mem_used}MB/${mem_total}MB (${mem_usage}%)"
    fi
    
    # Disk usage
    local disk_usage
    disk_usage=$(df /opt/arrowtuner | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $disk_usage -lt 80 ]]; then
        status_ok "Disk: ${disk_usage}% used"
    elif [[ $disk_usage -lt 95 ]]; then
        status_warn "Disk: ${disk_usage}% used"
    else
        status_error "Disk: ${disk_usage}% used"
    fi
    
    # Load average
    local load_avg
    load_avg=$(uptime | awk -F'load average:' '{print $2}' | cut -d, -f1 | xargs)
    echo -e "  Load Average: $load_avg"
    
    echo ""
}

# Database Status
check_database_status() {
    echo -e "${BOLD}Database Status:${NC}"
    
    local db_path="/opt/arrowtuner/data/arrow_database.db"
    
    # Check if database file exists
    if [[ -f "$db_path" ]]; then
        local db_size
        db_size=$(du -h "$db_path" | cut -f1)
        status_ok "Database file exists ($db_size)"
        
        # Check database connectivity
        if sudo -u arrowtuner sqlite3 "$db_path" "SELECT 1;" >/dev/null 2>&1; then
            status_ok "Database connectivity verified"
            
            # Get arrow count
            local arrow_count
            arrow_count=$(sudo -u arrowtuner sqlite3 "$db_path" "SELECT COUNT(*) FROM arrows;" 2>/dev/null || echo "0")
            status_info "$arrow_count arrows in database"
            
            # Check last update
            local last_modified
            last_modified=$(stat -c %y "$db_path" | cut -d. -f1)
            echo -e "  Last Modified: $last_modified"
        else
            status_error "Database connectivity failed"
        fi
    else
        status_error "Database file not found"
    fi
    
    echo ""
}

# Web Server Status
check_webserver_status() {
    echo -e "${BOLD}Web Server Status:${NC}"
    
    # Nginx status
    if systemctl is-active --quiet nginx; then
        status_ok "Nginx running"
        
        # Check configuration
        if nginx -t >/dev/null 2>&1; then
            status_ok "Nginx configuration valid"
        else
            status_error "Nginx configuration invalid"
        fi
        
        # Check if site is accessible
        if curl -s -I http://localhost | grep -q "HTTP/"; then
            status_ok "HTTP accessible"
        else
            status_warn "HTTP not accessible"
        fi
        
        # Check SSL certificate
        if [[ -f "/etc/letsencrypt/live/$(grep server_name /etc/nginx/sites-enabled/* | head -1 | awk '{print $2}' | tr -d ';')/cert.pem" ]]; then
            status_ok "SSL certificate installed"
            
            # Check certificate expiry
            local cert_expiry
            cert_expiry=$(openssl x509 -in "/etc/letsencrypt/live/$(grep server_name /etc/nginx/sites-enabled/* | head -1 | awk '{print $2}' | tr -d ';')/cert.pem" -noout -enddate | cut -d= -f2)
            echo -e "  SSL Expires: $cert_expiry"
        else
            status_warn "SSL certificate not found"
        fi
    else
        status_error "Nginx not running"
    fi
    
    echo ""
}

# Security Status
check_security_status() {
    echo -e "${BOLD}Security Status:${NC}"
    
    # Firewall status
    if ufw status | grep -q "Status: active"; then
        status_ok "UFW firewall active"
    else
        status_warn "UFW firewall inactive"
    fi
    
    # Fail2ban status
    if systemctl is-active --quiet fail2ban; then
        status_ok "Fail2ban active"
        
        # Check banned IPs
        local banned_count
        banned_count=$(fail2ban-client status sshd 2>/dev/null | grep "Currently banned" | awk '{print $4}' || echo "0")
        if [[ $banned_count -gt 0 ]]; then
            status_info "$banned_count IP(s) currently banned"
        fi
    else
        status_warn "Fail2ban not active"
    fi
    
    # Check for security updates
    local security_updates
    security_updates=$(apt list --upgradable 2>/dev/null | grep -c "security" || echo "0")
    if [[ $security_updates -eq 0 ]]; then
        status_ok "No pending security updates"
    else
        status_warn "$security_updates pending security update(s)"
    fi
    
    echo ""
}

# Backup Status
check_backup_status() {
    echo -e "${BOLD}Backup Status:${NC}"
    
    local backup_dir="/opt/arrowtuner/backups"
    
    if [[ -d "$backup_dir" ]]; then
        # Find latest backup
        local latest_backup
        latest_backup=$(find "$backup_dir" -name "arrowtuner-backup-*.tar.gz" -printf "%T@ %p\n" | sort -nr | head -1 | cut -d' ' -f2-)
        
        if [[ -n "$latest_backup" ]]; then
            local backup_age backup_size
            backup_age=$((($(date +%s) - $(stat -c %Y "$latest_backup")) / 86400))
            backup_size=$(du -h "$latest_backup" | cut -f1)
            
            if [[ $backup_age -le 1 ]]; then
                status_ok "Latest backup: $(basename "$latest_backup") ($backup_size, ${backup_age}d old)"
            elif [[ $backup_age -le 7 ]]; then
                status_warn "Latest backup: $(basename "$latest_backup") ($backup_size, ${backup_age}d old)"
            else
                status_error "Latest backup: $(basename "$latest_backup") ($backup_size, ${backup_age}d old)"
            fi
            
            # Count total backups
            local backup_count
            backup_count=$(find "$backup_dir" -name "arrowtuner-backup-*.tar.gz" | wc -l)
            status_info "$backup_count total backup(s) available"
        else
            status_error "No backups found"
        fi
    else
        status_error "Backup directory not found"
    fi
    
    # Check backup timer/cron
    if systemctl is-active --quiet arrowtuner-backup.timer; then
        status_ok "Backup timer active"
    elif crontab -l 2>/dev/null | grep -q backup.sh; then
        status_ok "Backup cron job active"
    else
        status_warn "No automatic backup configured"
    fi
    
    echo ""
}

# Log Status
check_log_status() {
    echo -e "${BOLD}Log Status:${NC}"
    
    local log_dir="/opt/arrowtuner/logs"
    
    if [[ -d "$log_dir" ]]; then
        # Check log files
        local app_log="$log_dir/arrowtuner.log"
        local gunicorn_log="$log_dir/gunicorn.log"
        
        if [[ -f "$app_log" ]]; then
            local app_log_size
            app_log_size=$(du -h "$app_log" | cut -f1)
            status_ok "Application log: $app_log_size"
        else
            status_warn "Application log not found"
        fi
        
        if [[ -f "$gunicorn_log" ]]; then
            local gunicorn_log_size
            gunicorn_log_size=$(du -h "$gunicorn_log" | cut -f1)
            status_ok "Gunicorn log: $gunicorn_log_size"
        else
            status_warn "Gunicorn log not found"
        fi
        
        # Check for recent errors
        local error_count
        error_count=$(find "$log_dir" -name "*.log" -mtime -1 -exec grep -l "ERROR\|CRITICAL" {} \; | wc -l)
        if [[ $error_count -eq 0 ]]; then
            status_ok "No recent errors in logs"
        else
            status_warn "$error_count log file(s) with recent errors"
        fi
    else
        status_error "Log directory not found"
    fi
    
    echo ""
}

# Network Status
check_network_status() {
    echo -e "${BOLD}Network Status:${NC}"
    
    # Check listening ports
    local port_5000 port_80 port_443
    port_5000=$(netstat -ln | grep ":5000" | wc -l)
    port_80=$(netstat -ln | grep ":80" | wc -l)
    port_443=$(netstat -ln | grep ":443" | wc -l)
    
    if [[ $port_5000 -gt 0 ]]; then
        status_ok "Application port 5000 listening"
    else
        status_error "Application port 5000 not listening"
    fi
    
    if [[ $port_80 -gt 0 ]]; then
        status_ok "HTTP port 80 listening"
    else
        status_warn "HTTP port 80 not listening"
    fi
    
    if [[ $port_443 -gt 0 ]]; then
        status_ok "HTTPS port 443 listening"
    else
        status_warn "HTTPS port 443 not listening"
    fi
    
    # Check external connectivity
    if curl -s --max-time 5 http://google.com >/dev/null; then
        status_ok "External connectivity available"
    else
        status_warn "External connectivity issues"
    fi
    
    echo ""
}

# Performance Metrics
show_performance_metrics() {
    echo -e "${BOLD}Performance Metrics:${NC}"
    
    # Response times
    local health_time db_time
    health_time=$(curl -w '%{time_total}' -s -o /dev/null http://localhost:5000/health 2>/dev/null || echo "failed")
    
    if [[ "$health_time" != "failed" ]]; then
        echo -e "  Health endpoint: ${health_time}s"
    else
        echo -e "  Health endpoint: failed"
    fi
    
    # Database query time
    db_time=$(time -p sudo -u arrowtuner sqlite3 /opt/arrowtuner/data/arrow_database.db "SELECT COUNT(*) FROM arrows;" 2>&1 | grep real | awk '{print $2}' || echo "failed")
    echo -e "  Database query: ${db_time}s"
    
    # Recent traffic (if nginx logs available)
    if [[ -f "/var/log/nginx/arrowtuner_access.log" ]]; then
        local requests_1h requests_24h
        requests_1h=$(awk -v d1="$(date -d '1 hour ago' '+%d/%b/%Y:%H:%M:%S')" '$4 > "["d1 {i++} END {print i+0}' /var/log/nginx/arrowtuner_access.log)
        requests_24h=$(awk -v d1="$(date -d '24 hours ago' '+%d/%b/%Y:%H:%M:%S')" '$4 > "["d1 {i++} END {print i+0}' /var/log/nginx/arrowtuner_access.log)
        echo -e "  Requests (1h): $requests_1h"
        echo -e "  Requests (24h): $requests_24h"
    fi
    
    echo ""
}

# Quick Actions
show_quick_actions() {
    echo -e "${BOLD}Quick Actions:${NC}"
    echo "  Restart service:  sudo supervisorctl restart arrowtuner"
    echo "  View logs:        ./deploy/scripts/logs.sh tail"
    echo "  Health check:     ./deploy/scripts/health-check.sh"
    echo "  Create backup:    ./deploy/scripts/backup.sh"
    echo "  Update app:       ./deploy/scripts/update.sh"
    echo ""
}

# Main function
main() {
    case "${1:-all}" in
        "all")
            show_header
            check_application_status
            check_system_resources
            check_database_status
            check_webserver_status
            check_security_status
            check_backup_status
            check_log_status
            check_network_status
            show_performance_metrics
            show_quick_actions
            ;;
        "app"|"application")
            check_application_status
            ;;
        "system"|"resources")
            check_system_resources
            ;;
        "database"|"db")
            check_database_status
            ;;
        "web"|"nginx")
            check_webserver_status
            ;;
        "security")
            check_security_status
            ;;
        "backup"|"backups")
            check_backup_status
            ;;
        "logs")
            check_log_status
            ;;
        "network")
            check_network_status
            ;;
        "performance"|"perf")
            show_performance_metrics
            ;;
        "help"|"-h"|"--help")
            echo "Arrow Tuning Platform - Status Dashboard"
            echo ""
            echo "Usage: $0 [SECTION]"
            echo ""
            echo "Sections:"
            echo "  all         - Show complete status (default)"
            echo "  app         - Application status"
            echo "  system      - System resources"
            echo "  database    - Database status"
            echo "  web         - Web server status"
            echo "  security    - Security status"
            echo "  backup      - Backup status"
            echo "  logs        - Log status"
            echo "  network     - Network status"
            echo "  performance - Performance metrics"
            ;;
        *)
            echo "Unknown section: $1"
            echo "Use '$0 help' for available options"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"