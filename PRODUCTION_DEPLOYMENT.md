# Production Deployment Guide for archerytool.online

## Prerequisites

1. **Ubuntu 20.04+ Server** with root access
2. **Domain Setup**: Point `archerytool.online` and `www.archerytool.online` to your server IP
3. **API Keys**: Get DeepSeek API key from https://deepseek.com

## Quick Deployment

### 1. Server Setup
```bash
# Clone the repository
git clone https://github.com/Paalmessenlien/archerytools.git
cd archerytools

# Run server setup (installs dependencies, configures firewall, etc.)
sudo ./deploy/scripts/server-setup.sh
```

### 2. Configure Environment
```bash
# Edit production configuration
sudo nano deploy/config/production.env

# Update these key settings:
SECRET_KEY=your-strong-secret-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DOMAIN_NAME=archerytool.online
SSL_EMAIL=admin@archerytool.online
```

### 3. Deploy Application
```bash
# Deploy the application
sudo ./deploy/scripts/deploy.sh

# The script will:
# - Copy application files
# - Build database from processed arrow data (400+ arrows)
# - Configure nginx with SSL certificates
# - Start services with supervisor
# - Verify deployment
```

## Post-Deployment

### Verify Installation
```bash
# Check service status
sudo supervisorctl status arrowtuner

# View logs
sudo tail -f /opt/arrowtuner/logs/gunicorn.log

# Test API health
curl https://archerytool.online/health
```

### Management Commands
```bash
# Restart application
sudo supervisorctl restart arrowtuner

# Check deployment status
sudo /opt/arrowtuner/scripts/status.sh

# Create backup
sudo /opt/arrowtuner/scripts/backup.sh

# View live logs
sudo /opt/arrowtuner/scripts/logs.sh tail
```

## Key Features

✅ **Complete Arrow Database**: 400+ arrows from 13 manufacturers  
✅ **Professional Tuning Calculations**: Spine, FOC, kinetic energy  
✅ **SSL Security**: Let's Encrypt certificates with auto-renewal  
✅ **Rate Limiting**: API protection and DDoS mitigation  
✅ **Automated Backups**: Daily database and application backups  
✅ **Health Monitoring**: Automatic service restart on failure  
✅ **Performance Optimized**: Nginx caching and compression  

## Architecture

- **Domain**: `archerytool.online` (with www redirect)
- **SSL**: Let's Encrypt certificates with HTTP/2
- **Backend**: Flask API server on port 5000
- **Database**: SQLite with 400+ arrow specifications
- **Web Server**: Nginx reverse proxy with rate limiting
- **Process Manager**: Supervisor for service management
- **Security**: UFW firewall, fail2ban, security headers

## Database

The production database is built from processed manufacturer data:
- **13 Manufacturers**: Easton, Gold Tip, Victory, Nijora, Pandarus, etc.
- **400+ Arrows**: Complete specifications with spine, GPI, diameter
- **Product Images**: Visual browsing with manufacturer photos
- **No Scraping Required**: Database built from versioned data

## Monitoring

Access logs and monitoring:
```bash
# Application logs
tail -f /opt/arrowtuner/logs/gunicorn.log

# Nginx access logs  
tail -f /var/log/nginx/arrowtuner_access.log

# System health check
/opt/arrowtuner/health-check.sh
```

## Support

- **Health Check**: `https://archerytool.online/health`
- **API Documentation**: `https://archerytool.online/api/`
- **Database Stats**: `https://archerytool.online/api/database/stats`

The deployment creates a production-ready arrow tuning platform at `https://archerytool.online` with comprehensive arrow database and professional tuning calculations.