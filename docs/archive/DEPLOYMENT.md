# ArrowTuner Production Deployment Guide

This guide covers deploying ArrowTuner to a production Ubuntu server with professional-grade security, monitoring, and performance optimization.

## 🏗️ Deployment Options

### Option 1: Docker Deployment (Recommended)
Quick and isolated deployment using Docker containers.

### Option 2: Manual Ubuntu Deployment  
Direct deployment to Ubuntu server with full system integration.

## 🐳 Docker Deployment

### Prerequisites
- Ubuntu 20.04+ server
- Docker and Docker Compose installed
- Domain name pointing to your server
- 4GB+ RAM, 2+ CPU cores

### Quick Start
```bash
# Clone repository
git clone <your-repo-url>
cd arrowtuner2

# Create environment file
cp .env.example .env
# Edit .env with your settings

# Deploy with Docker
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs
```

### Environment Configuration
Create `.env` file in root directory:
```env
# Security
SECRET_KEY=your-super-secret-key-change-this
DEEPSEEK_API_KEY=your-deepseek-api-key-here

# Domain
DOMAIN_NAME=yourdomain.com
SSL_EMAIL=admin@yourdomain.com

# Database
DB_PATH=/app/data/arrow_database.db
```

### SSL Setup (Docker)
```bash
# Install Certbot on host
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to SSL directory
sudo mkdir -p deploy/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deploy/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deploy/ssl/

# Restart nginx container
docker-compose restart nginx
```

## 🖥️ Manual Ubuntu Deployment

### Step 1: Server Setup
Run the automated server setup script:
```bash
# Download and run server setup
sudo ./deploy/server-setup.sh
```

This script installs and configures:
- Node.js 18+, Python 3.9+, Docker
- Nginx, PM2, fail2ban, UFW firewall
- SSL certificates with Let's Encrypt
- Monitoring and backup systems
- Security hardening

### Step 2: Application Deployment
Deploy the application:
```bash
# Run deployment script
sudo ./deploy/deploy.sh yourdomain.com admin@yourdomain.com
```

### Step 3: Environment Configuration
Update environment variables:
```bash
# Edit backend environment
sudo nano /var/www/arrowtuner/arrow_scraper/.env

# Edit frontend environment  
sudo nano /var/www/arrowtuner/frontend/.env
```

## 🔧 Configuration

### Backend Environment Variables
```env
# Required
SECRET_KEY=your-secret-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key

# Optional
FLASK_ENV=production
API_PORT=5000
DATABASE_PATH=arrow_database.db
LOG_LEVEL=INFO
```

### Frontend Environment Variables
```env
# Required
API_BASE_URL=https://yourdomain.com/api
NODE_ENV=production

# Optional
PORT=3000
```

### Nginx Configuration
The deployment automatically configures Nginx with:
- SSL termination and redirects
- Gzip compression
- Security headers
- Rate limiting
- Static asset caching
- Proxy configuration for API and frontend

## 🔐 Security Features

### Firewall (UFW)
```bash
# Check firewall status
sudo ufw status

# Allow additional ports if needed
sudo ufw allow 8080/tcp
```

### SSL Certificates
Automatic Let's Encrypt certificates with auto-renewal:
```bash
# Check certificate status
sudo certbot certificates

# Manual renewal
sudo certbot renew

# Auto-renewal is configured via cron
```

### Fail2ban
Automatic IP banning for suspicious activity:
```bash
# Check banned IPs
sudo fail2ban-client status

# Unban an IP
sudo fail2ban-client set sshd unbanip 1.2.3.4
```

## 📊 Monitoring

### System Status
```bash
# Quick status check
/opt/arrowtuner/status.sh

# Detailed health check
/opt/arrowtuner/health-check.sh
```

### Service Management
```bash
# API service
sudo systemctl status arrowtuner-api
sudo systemctl restart arrowtuner-api

# Frontend (PM2)
sudo -u arrowtuner pm2 status
sudo -u arrowtuner pm2 restart arrowtuner-frontend

# Nginx
sudo systemctl status nginx
sudo systemctl reload nginx
```

### Log Monitoring
```bash
# API logs
sudo journalctl -u arrowtuner-api -f

# Frontend logs
sudo -u arrowtuner pm2 logs arrowtuner-frontend

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo tail -f /var/log/arrowtuner/health-check.log
```

## 🔄 Backup & Recovery

### Automated Backups
Daily backups are automatically created at 2 AM:
```bash
# Manual backup
/opt/arrowtuner/backup.sh

# List backups
ls -la /opt/arrowtuner/backups/

# Restore from backup
tar -xzf /opt/arrowtuner/backups/arrowtuner_backup_20240101_020000.tar.gz -C /var/www/
```

### Database Backup
```bash
# Backup database
cp /var/www/arrowtuner/arrow_scraper/arrow_database.db /opt/arrowtuner/backups/

# Restore database
cp /opt/arrowtuner/backups/arrow_database.db /var/www/arrowtuner/arrow_scraper/
sudo systemctl restart arrowtuner-api
```

## 🚀 Performance Optimization

### System Tuning
The setup script automatically optimizes:
- File descriptor limits
- Network parameters
- Memory management
- Process scheduling

### Application Performance
```bash
# Frontend optimization
sudo -u arrowtuner pm2 restart arrowtuner-frontend --update-env

# API optimization (restart with fresh memory)
sudo systemctl restart arrowtuner-api

# Nginx optimization (reload config)
sudo nginx -s reload
```

### Database Performance
```bash
# Rebuild database with optimizations
cd /var/www/arrowtuner/arrow_scraper
sudo -u arrowtuner ../venv/bin/python arrow_database.py

# Update diameter categories
sudo -u arrowtuner ../venv/bin/python migrate_diameter_categories.py
```

## 🔄 Updates & Maintenance

### Application Updates
```bash
# Pull latest code
cd /var/www/arrowtuner
sudo -u arrowtuner git pull

# Update backend
cd arrow_scraper
sudo -u arrowtuner ../venv/bin/pip install -r requirements.txt
sudo systemctl restart arrowtuner-api

# Update frontend
cd ../frontend
sudo -u arrowtuner npm ci
sudo -u arrowtuner npm run build
sudo -u arrowtuner pm2 restart arrowtuner-frontend
```

### System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Node.js packages
sudo -u arrowtuner npm update -g

# Update Python packages
sudo -u arrowtuner /var/www/arrowtuner/venv/bin/pip install --upgrade pip
```

## 🐛 Troubleshooting

### Common Issues

**API not responding:**
```bash
# Check service status
sudo systemctl status arrowtuner-api

# Check logs
sudo journalctl -u arrowtuner-api --since "1 hour ago"

# Restart service
sudo systemctl restart arrowtuner-api
```

**Frontend not loading:**
```bash
# Check PM2 status
sudo -u arrowtuner pm2 status

# Check logs
sudo -u arrowtuner pm2 logs arrowtuner-frontend

# Restart frontend
sudo -u arrowtuner pm2 restart arrowtuner-frontend
```

**SSL certificate issues:**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew --force-renewal

# Update Nginx config
sudo nginx -t && sudo systemctl reload nginx
```

**Database errors:**
```bash
# Check database file
ls -la /var/www/arrowtuner/arrow_scraper/arrow_database.db

# Rebuild database
cd /var/www/arrowtuner/arrow_scraper
sudo -u arrowtuner ../venv/bin/python arrow_database.py
```

### Performance Issues
```bash
# Check system resources
htop
df -h
free -h

# Check service memory usage
sudo systemctl status arrowtuner-api
sudo -u arrowtuner pm2 monit

# Clear logs if disk is full
sudo journalctl --vacuum-time=7d
sudo -u arrowtuner pm2 flush
```

### Network Issues
```bash
# Check ports
sudo netstat -tlnp | grep -E "(3000|5000|80|443)"

# Test internal connectivity
curl http://localhost:5000/api/health
curl http://localhost:3000

# Check firewall
sudo ufw status verbose
```

## 📋 Maintenance Checklist

### Daily
- [ ] Check system status: `/opt/arrowtuner/status.sh`
- [ ] Monitor disk space: `df -h`
- [ ] Review error logs

### Weekly  
- [ ] Review security logs: `sudo fail2ban-client status`
- [ ] Check SSL certificate expiry: `sudo certbot certificates`
- [ ] Update system packages: `sudo apt update && sudo apt upgrade`

### Monthly
- [ ] Clean old backups: `find /opt/arrowtuner/backups -mtime +30 -delete`
- [ ] Rotate logs: `sudo logrotate -f /etc/logrotate.conf`
- [ ] Performance review and optimization

### Quarterly
- [ ] Security audit and updates
- [ ] Backup verification and recovery testing
- [ ] Performance benchmarking
- [ ] Review and update documentation

## 🆘 Emergency Procedures

### Service Recovery
```bash
# Complete service restart
sudo systemctl restart arrowtuner-api
sudo -u arrowtuner pm2 restart arrowtuner-frontend
sudo systemctl restart nginx

# Restore from backup
/opt/arrowtuner/backup.sh restore /opt/arrowtuner/backups/latest.tar.gz
```

### Database Recovery
```bash
# Restore database from backup
sudo systemctl stop arrowtuner-api
cp /opt/arrowtuner/backups/arrow_database.db /var/www/arrowtuner/arrow_scraper/
sudo systemctl start arrowtuner-api
```

### Complete System Recovery
```bash
# Re-run deployment script
cd /path/to/arrowtuner2
sudo ./deploy/deploy.sh yourdomain.com admin@yourdomain.com
```

---

## 📞 Support

For deployment issues:
1. Check logs first: `/opt/arrowtuner/status.sh`
2. Review this documentation
3. Check GitHub issues
4. Contact system administrator

**Remember:** Always test changes in a staging environment before applying to production!