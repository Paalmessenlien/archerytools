# Production Server Deployment Guide

## Overview

This guide covers deploying Archery Tools to a production server environment. The system is designed for easy deployment with minimal dependencies and no server-side web scraping.

## Server Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 10GB minimum, 20GB recommended
- **CPU**: 2 cores minimum
- **Network**: Public IP address and domain name

### Required Software
- Docker 20.10+
- Docker Compose 2.0+
- Git
- SSL certificates (Let's Encrypt recommended)

## Quick Production Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install -y docker-compose

# Install Git and other utilities
sudo apt install -y git curl wget nginx-common certbot
```

### 2. Clone Repository

```bash
# Clone the repository
git clone https://github.com/Paalmessenlien/archerytools.git
cd archerytools

# Set permissions
chmod +x *.sh
chmod +x arrow_scraper/*.py
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```env
# API Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
API_PORT=5000
GOOGLE_CLIENT_SECRET=your-google-oauth-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com

# Frontend Configuration
FRONTEND_PORT=3000
NUXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-oauth-client-id
NODE_ENV=production
NUXT_PUBLIC_API_BASE=https://yourdomain.com/api

# Production Settings
DOMAIN_NAME=yourdomain.com
SSL_EMAIL=admin@yourdomain.com
```

### 4. Import Arrow Data

**Important**: The production system does NOT perform web scraping. It only imports existing JSON data files.

```bash
# Import arrow data from existing JSON files
./production-import-only.sh
```

This will:
- Import all existing arrow data from `arrow_scraper/data/processed/`
- Create traditional wood arrows if missing
- Set up databases with 158+ arrows and 961+ specifications
- Prepare Docker volumes

### 5. Deploy to Production

```bash
# Option 1: HTTP deployment (initial setup)
docker-compose -f docker-compose.prod.yml up -d --build

# Option 2: HTTPS deployment (with SSL certificates)
# First, set up SSL certificates
sudo certbot certonly --standalone -d yourdomain.com

# Then deploy with HTTPS
sudo docker-compose -f docker-compose.enhanced-ssl.yml up -d --build
```

## SSL Certificate Setup

### Using Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt install -y certbot

# Stop any running web servers temporarily
sudo docker-compose down

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com

# Verify certificate files
sudo ls -la /etc/letsencrypt/live/yourdomain.com/
```

### Certificate Renewal

```bash
# Set up automatic renewal
sudo crontab -e

# Add this line for automatic renewal
0 2 * * 1 /usr/bin/certbot renew --quiet && docker-compose -f /path/to/archerytools/docker-compose.enhanced-ssl.yml restart nginx
```

## Production Configurations

### Docker Compose Files

1. **docker-compose.enhanced-ssl.yml** - Production HTTPS (recommended)
   - Nginx reverse proxy with SSL
   - Health checks and monitoring
   - Production optimizations

2. **docker-compose.prod.yml** - Production HTTP
   - For initial setup or HTTP-only deployments
   - Basic reverse proxy

3. **docker-compose.yml** - Development
   - Hot reload enabled
   - Development configurations

### Nginx Configuration

The system includes production-ready Nginx configuration with:
- SSL termination
- Security headers
- Compression
- Rate limiting
- Static file serving

## Monitoring and Maintenance

### Health Checks

```bash
# Check container status
docker-compose ps

# Check service health
curl https://yourdomain.com/api/health
curl https://yourdomain.com

# Check database statistics
docker exec archerytools-api-1 python -c "
import sqlite3
conn = sqlite3.connect('/app/arrow_database.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM arrows')
print(f'Total arrows: {cursor.fetchone()[0]}')
cursor.execute('SELECT COUNT(DISTINCT manufacturer) FROM arrows')
print(f'Manufacturers: {cursor.fetchone()[0]}')
"
```

### Log Management

```bash
# View application logs
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f nginx

# Export logs for analysis
docker-compose logs --since 24h > production.log
```

### Performance Monitoring

```bash
# Check resource usage
docker stats

# Monitor disk usage
df -h
du -sh /var/lib/docker/

# Check memory usage
free -h
```

## Backup and Recovery

### Database Backup

```bash
# Create backup directory
mkdir -p ~/backups

# Backup user database
docker run --rm -v archerytools_user-data:/data -v ~/backups:/backup alpine tar czf /backup/user-data-$(date +%Y%m%d).tar.gz -C /data .

# Backup arrow database
docker run --rm -v archerytools_arrow-data:/data -v ~/backups:/backup alpine tar czf /backup/arrow-data-$(date +%Y%m%d).tar.gz -C /data .

# Backup environment and configuration
cp .env ~/backups/
cp docker-compose.enhanced-ssl.yml ~/backups/
```

### Automated Backup Script

```bash
# Create backup script
cat > ~/backup-archerytools.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups/archerytools
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup databases
docker run --rm -v archerytools_user-data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/user-data-$DATE.tar.gz -C /data .
docker run --rm -v archerytools_arrow-data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/arrow-data-$DATE.tar.gz -C /data .

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x ~/backup-archerytools.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * ~/backup-archerytools.sh
```

### Recovery Process

```bash
# Stop services
docker-compose down

# Restore databases
docker run --rm -v archerytools_user-data:/data -v ~/backups:/backup alpine tar xzf /backup/user-data-YYYYMMDD.tar.gz -C /data
docker run --rm -v archerytools_arrow-data:/data -v ~/backups:/backup alpine tar xzf /backup/arrow-data-YYYYMMDD.tar.gz -C /data

# Restart services
docker-compose -f docker-compose.enhanced-ssl.yml up -d
```

## Updates and Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull

# Stop services
docker-compose down

# Rebuild and restart
./production-import-only.sh  # Re-import data if needed
docker-compose -f docker-compose.enhanced-ssl.yml up -d --build
```

### Security Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose -f docker-compose.enhanced-ssl.yml up -d --build

# Renew SSL certificates
sudo certbot renew
```

## Troubleshooting

### Common Issues

#### 1. Services Won't Start
```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Check memory usage
free -h

# Restart services
docker-compose restart
```

#### 2. Database Issues
```bash
# Re-import data
docker-compose down
./production-import-only.sh
docker-compose up -d
```

#### 3. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew --force-renewal

# Restart nginx
docker-compose restart nginx
```

#### 4. Performance Issues
```bash
# Check resource limits
docker stats

# Optimize database
docker exec archerytools-api-1 python -c "
import sqlite3
conn = sqlite3.connect('/app/arrow_database.db')
conn.execute('VACUUM')
conn.execute('ANALYZE')
conn.close()
"

# Clear Docker system cache
docker system prune -a
```

## Security Best Practices

### Firewall Configuration

```bash
# Install UFW
sudo apt install -y ufw

# Configure firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### System Hardening

```bash
# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Enable automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Environment Security

- Never commit `.env` files to version control
- Use strong, unique passwords and secrets
- Regularly rotate API keys and secrets
- Monitor access logs for suspicious activity
- Keep all software updated

## Performance Optimization

### Resource Allocation

```yaml
# In docker-compose.enhanced-ssl.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Database Optimization

```bash
# Regular database maintenance
docker exec archerytools-api-1 python -c "
import sqlite3
conn = sqlite3.connect('/app/arrow_database.db')
conn.execute('PRAGMA optimize')
cursor = conn.cursor()
cursor.execute('VACUUM')
cursor.execute('ANALYZE')
conn.close()
print('Database optimized')
"
```

## Scaling

### Horizontal Scaling

```bash
# Scale API containers
docker-compose up -d --scale api=3

# Use load balancer (nginx configuration)
# Add upstream block to nginx.conf for multiple API containers
```

### Vertical Scaling

```bash
# Increase container resources
# Edit docker-compose file to increase memory/CPU limits
# Restart containers
docker-compose up -d --force-recreate
```

## Support and Maintenance

### Log Locations

- Application logs: `docker-compose logs`
- Nginx logs: `/var/log/nginx/` (in nginx container)
- System logs: `/var/log/syslog`

### Monitoring Checklist

- [ ] Service health endpoints responding
- [ ] SSL certificates valid and not expiring
- [ ] Database integrity check
- [ ] Backup process working
- [ ] Log rotation configured
- [ ] Resource usage within limits

### Emergency Procedures

1. **Service Down**: Check logs, restart containers
2. **Database Corruption**: Restore from backup
3. **SSL Expired**: Renew certificates, restart nginx
4. **High Resource Usage**: Scale containers or optimize

Remember: **Production deployments only import JSON data - no web scraping is performed on the server.**