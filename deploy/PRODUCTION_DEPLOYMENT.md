# Arrow Tuning Platform - Production Deployment Guide

This comprehensive guide covers deploying the Arrow Tuning Platform to a production Ubuntu server with enterprise-grade security, monitoring, and maintenance capabilities.

## 🚀 Quick Start

### Prerequisites
- Fresh Ubuntu 20.04+ LTS server
- Minimum 2GB RAM, 20GB storage
- Root/sudo access
- Domain name (recommended)
- Email for SSL certificates

### 1. Server Setup
```bash
# Download and run server setup
curl -sSL https://your-repo.com/deploy/scripts/server-setup.sh | sudo bash
# OR manually:
sudo ./deploy/scripts/server-setup.sh
```

### 2. Configure Environment
```bash
# Edit production configuration
nano deploy/config/production.env

# Required settings:
# - SECRET_KEY (generate strong random key)
# - DEEPSEEK_API_KEY (your API key)
# - DOMAIN_NAME (your domain)
# - SSL_EMAIL (for Let's Encrypt)
```

### 3. Deploy Application
```bash
sudo ./deploy/scripts/deploy.sh
```

### 4. Verify Deployment
```bash
# Check application health
curl https://yourdomain.com/health

# View service status
sudo supervisorctl status arrowtuner
# OR for systemd:
sudo systemctl status arrowtuner
```

## 📋 Detailed Deployment Process

### Server Requirements

**Minimum Specifications:**
- CPU: 2 cores
- RAM: 2GB
- Storage: 20GB SSD
- OS: Ubuntu 20.04+ LTS
- Network: 100Mbps connection

**Recommended Specifications:**
- CPU: 4 cores
- RAM: 4GB
- Storage: 50GB SSD
- OS: Ubuntu 22.04 LTS
- Network: 1Gbps connection

### System Components

The deployment installs and configures:

1. **Web Server**: Nginx (reverse proxy, SSL termination, static files)
2. **Application Server**: Gunicorn (WSGI server for Flask)
3. **Process Management**: Supervisor OR Systemd
4. **Database**: SQLite (with automatic backups)
5. **Security**: UFW firewall, fail2ban, SSL certificates
6. **Monitoring**: Health checks, log rotation, alerts

### Architecture Overview

```
Internet → Nginx (Port 80/443) → Gunicorn (Port 5000) → Flask App
                 ↓
            Static Files
                 ↓
            SSL/Security
```

## 🔧 Configuration Details

### Environment Variables

**Required:**
```bash
SECRET_KEY=your-secret-key-here-change-this
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DOMAIN_NAME=yourdomain.com
SSL_EMAIL=admin@yourdomain.com
```

**Optional:**
```bash
APP_PORT=5000
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
BACKUP_INTERVAL=86400
HEALTH_CHECK_INTERVAL=300
```

### Database Configuration

The platform uses SQLite for simplicity and reliability:

- **Location**: `/opt/arrowtuner/data/arrow_database.db`
- **Backups**: Daily automated backups to `/opt/arrowtuner/backups/`
- **Migration**: Automatic schema updates during deployment
- **Size**: Typical database ~50MB with 1000+ arrows

### Security Features

**Firewall (UFW):**
- SSH (22) - Limited to specific IPs (recommended)
- HTTP (80) - Redirects to HTTPS
- HTTPS (443) - Main application access

**Fail2Ban Protection:**
- SSH brute force protection
- Nginx rate limiting enforcement
- Automatic IP blocking for repeated violations

**SSL/TLS Security:**
- Let's Encrypt certificates (auto-renewal)
- TLS 1.2+ only
- Perfect Forward Secrecy
- HSTS headers

**Application Security:**
- Rate limiting (60 requests/minute default)
- CSRF protection
- Secure session cookies
- Input validation and sanitization

## 🛠️ Management Commands

### Service Management

**Using Supervisor:**
```bash
# Start/stop/restart
sudo supervisorctl start arrowtuner
sudo supervisorctl stop arrowtuner
sudo supervisorctl restart arrowtuner

# Check status
sudo supervisorctl status arrowtuner

# View logs
sudo supervisorctl tail arrowtuner
```

**Using Systemd (alternative):**
```bash
# Start/stop/restart
sudo systemctl start arrowtuner
sudo systemctl stop arrowtuner
sudo systemctl restart arrowtuner

# Check status
sudo systemctl status arrowtuner

# View logs
sudo journalctl -u arrowtuner -f
```

### Log Management

**View Logs:**
```bash
# All logs (follow mode)
./deploy/scripts/logs.sh tail

# Recent logs
./deploy/scripts/logs.sh show -n 100

# Error logs only
./deploy/scripts/logs.sh error

# Access logs
./deploy/scripts/logs.sh access

# Log file sizes
./deploy/scripts/logs.sh size
```

**Log Rotation:**
```bash
# Force log rotation
./deploy/scripts/logs.sh rotate

# Clean old logs
./deploy/scripts/logs.sh clean
```

### Health Monitoring

**Manual Health Checks:**
```bash
# Full health check
./deploy/scripts/health-check.sh

# Specific checks
./deploy/scripts/health-check.sh app      # Application response
./deploy/scripts/health-check.sh db       # Database connectivity
./deploy/scripts/health-check.sh disk     # Disk space
./deploy/scripts/health-check.sh memory   # Memory usage

# Status overview
./deploy/scripts/health-check.sh status
```

**Automated Monitoring:**
```bash
# Setup cron job for health checks (every 5 minutes)
echo "*/5 * * * * root /opt/arrowtuner/deploy/scripts/health-check.sh" >> /etc/crontab
```

### Backup Management

**Create Backup:**
```bash
# Manual backup
./deploy/scripts/backup.sh backup

# List existing backups
./deploy/scripts/backup.sh list

# Verify backup integrity
./deploy/scripts/backup.sh verify /path/to/backup.tar.gz
```

**Restore from Backup:**
```bash
# Restore from specific backup
./deploy/scripts/backup.sh restore /opt/arrowtuner/backups/arrowtuner-backup-20250722-120000.tar.gz
```

**Automated Backups:**
```bash
# Using systemd timer (recommended)
sudo systemctl enable arrowtuner-backup.timer
sudo systemctl start arrowtuner-backup.timer

# OR using cron
echo "0 2 * * * root /opt/arrowtuner/deploy/scripts/backup.sh backup" >> /etc/crontab
```

### Application Updates

**Check for Updates:**
```bash
# Check if updates available
./deploy/scripts/update.sh check

# Show current version
./deploy/scripts/update.sh version
```

**Apply Updates:**
```bash
# Update application (with automatic backup)
./deploy/scripts/update.sh update

# Rollback if needed
./deploy/scripts/update.sh rollback
```

## 🔍 Troubleshooting

### Common Issues

**Service Won't Start:**
```bash
# Check service status
sudo supervisorctl status arrowtuner

# Check logs for errors
./deploy/scripts/logs.sh error

# Check configuration
nginx -t
python3 -c "import sys; sys.path.append('/opt/arrowtuner/app'); import webapp"
```

**Database Issues:**
```bash
# Check database file
ls -la /opt/arrowtuner/data/arrow_database.db

# Test database connectivity
sudo -u arrowtuner sqlite3 /opt/arrowtuner/data/arrow_database.db "SELECT COUNT(*) FROM arrows;"

# Rebuild database
sudo -u arrowtuner python3 /opt/arrowtuner/app/arrow_database.py
```

**SSL Certificate Issues:**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew

# Test nginx configuration
sudo nginx -t
```

**Performance Issues:**
```bash
# Check system resources
./deploy/scripts/health-check.sh memory
./deploy/scripts/health-check.sh disk

# Monitor application
htop
iostat 1
```

### Debug Mode

**Enable Debug Logging:**
```bash
# Edit environment file
sudo nano /opt/arrowtuner/.env

# Change LOG_LEVEL=DEBUG
# Restart service
sudo supervisorctl restart arrowtuner
```

**Application Debug:**
```bash
# Test application directly
sudo -u arrowtuner /opt/arrowtuner/venv/bin/python /opt/arrowtuner/app/webapp.py

# Check Python imports
sudo -u arrowtuner /opt/arrowtuner/venv/bin/python -c "import webapp, models, arrow_database"
```

## 📊 Monitoring and Alerts

### Health Check Alerts

Configure email alerts for system issues:

```bash
# Install mail utilities
sudo apt install mailutils

# Configure alert email in health check
export ALERT_EMAIL="admin@yourdomain.com"
./deploy/scripts/health-check.sh
```

### Log Monitoring

**Real-time Monitoring:**
```bash
# Monitor all logs
tail -f /opt/arrowtuner/logs/*.log /var/log/nginx/arrowtuner*.log

# Monitor for errors
tail -f /opt/arrowtuner/logs/*.log | grep -i "error\|exception"
```

**Log Analysis:**
```bash
# Error summary (last 24 hours)
find /opt/arrowtuner/logs -name "*.log" -mtime -1 -exec grep -l "ERROR" {} \;

# Access log analysis
awk '{print $1}' /var/log/nginx/arrowtuner_access.log | sort | uniq -c | sort -nr | head -10
```

### Performance Monitoring

**System Metrics:**
```bash
# Memory usage
free -h

# Disk usage
df -h /opt/arrowtuner

# CPU usage
top -p $(pgrep -f gunicorn)

# Network connections
netstat -tulpn | grep :5000
```

**Application Metrics:**
```bash
# Response time test
time curl -s http://localhost:5000/health

# Database query performance
time sudo -u arrowtuner sqlite3 /opt/arrowtuner/data/arrow_database.db "SELECT COUNT(*) FROM arrows;"
```

## 🔐 Security Hardening

### Additional Security Measures

**SSH Hardening:**
```bash
# Disable password authentication (use keys only)
echo "PasswordAuthentication no" >> /etc/ssh/sshd_config
echo "PermitRootLogin no" >> /etc/ssh/sshd_config
systemctl restart sshd
```

**Firewall Rules:**
```bash
# Restrict SSH to specific IPs
sudo ufw delete allow ssh
sudo ufw allow from YOUR_IP to any port 22

# Rate limit HTTP/HTTPS
sudo ufw limit 80
sudo ufw limit 443
```

**File Permissions:**
```bash
# Secure sensitive files
chmod 600 /opt/arrowtuner/.env
chmod 700 /opt/arrowtuner/data
chmod 700 /opt/arrowtuner/backups
```

**Database Security:**
```bash
# Regular backup verification
./deploy/scripts/backup.sh verify $(ls -t /opt/arrowtuner/backups/*.tar.gz | head -1)

# Database integrity check
sudo -u arrowtuner sqlite3 /opt/arrowtuner/data/arrow_database.db "PRAGMA integrity_check;"
```

## 📈 Scaling and Optimization

### Performance Tuning

**Gunicorn Configuration:**
```bash
# Edit supervisor configuration
sudo nano /etc/supervisor/conf.d/arrowtuner.conf

# Optimize workers (2 * CPU cores + 1)
command=.../gunicorn --workers 4 --worker-connections 1000 ...
```

**Nginx Optimization:**
```bash
# Edit nginx configuration
sudo nano /etc/nginx/sites-available/arrowtuner

# Enable compression and caching
gzip_comp_level 6;
expires 1y;
```

**Database Optimization:**
```bash
# Vacuum database
sudo -u arrowtuner sqlite3 /opt/arrowtuner/data/arrow_database.db "VACUUM;"

# Create indexes for better performance
sudo -u arrowtuner sqlite3 /opt/arrowtuner/data/arrow_database.db "CREATE INDEX IF NOT EXISTS idx_arrows_manufacturer ON arrows(manufacturer);"
```

### Load Balancing (for multiple servers)

**Nginx Load Balancer:**
```nginx
upstream arrowtuner_cluster {
    server 10.0.1.10:5000;
    server 10.0.1.11:5000;
    server 10.0.1.12:5000;
}
```

**Database Synchronization:**
```bash
# Use shared storage or database replication
# Consider PostgreSQL for multi-server setups
```

## 📝 Maintenance Schedule

### Daily Tasks (Automated)
- Database backup
- Log rotation
- Health checks
- SSL certificate renewal check

### Weekly Tasks
- Review error logs
- Check disk space usage
- Verify backup integrity
- Security updates

### Monthly Tasks
- Performance analysis
- Clean old backups
- Review access logs
- System updates

### Quarterly Tasks
- Security audit
- Disaster recovery test
- Configuration review
- Performance optimization

## 🆘 Emergency Procedures

### Service Recovery

**Application Down:**
1. Check service status: `supervisorctl status arrowtuner`
2. Review error logs: `./deploy/scripts/logs.sh error`
3. Restart service: `supervisorctl restart arrowtuner`
4. If persistent, restore from backup: `./deploy/scripts/backup.sh restore`

**Database Corruption:**
1. Stop application
2. Restore database from backup
3. Verify database integrity
4. Restart application

**Server Compromise:**
1. Isolate server (firewall rules)
2. Analyze logs for intrusion
3. Restore from clean backup
4. Apply security updates
5. Change all credentials

### Contact Information

**Emergency Contacts:**
- System Administrator: admin@yourdomain.com
- Technical Support: support@yourdomain.com
- Security Team: security@yourdomain.com

**External Services:**
- Domain Registrar: [provider]
- SSL Certificate: Let's Encrypt
- Hosting Provider: [provider]

---

**Last Updated:** 2025-01-22  
**Version:** 1.0  
**Deployment Target:** Ubuntu 20.04+ LTS