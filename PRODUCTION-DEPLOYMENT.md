# ArrowTuner Production Deployment Guide

This guide covers the complete production deployment process for ArrowTuner with HTTPS support.

## 🚀 Quick Start

### Prerequisites
- Ubuntu/Debian server with Docker and Docker Compose
- Domain name pointing to your server
- Root/sudo access

### One-Command Deployment
```bash
git clone https://github.com/Paalmessenlien/archerytools.git
cd archerytools
./deploy-production.sh
```

## 📋 Step-by-Step Production Setup

### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Logout and login to apply docker group
```

### 2. Application Deployment
```bash
# Clone repository
git clone https://github.com/Paalmessenlien/archerytools.git
cd archerytools

# Configure environment (optional)
cp .env.example .env
# Edit .env with your specific settings

# Deploy with HTTP (initial setup)
./deploy-production.sh
```

### 3. DNS Configuration
Configure your domain registrar to point to your server:
```
Type: A
Name: @ (or your domain)
Value: YOUR_SERVER_IP
TTL: 300
```

Test DNS propagation:
```bash
nslookup yourdomain.com
```

### 4. SSL Certificate Setup
```bash
# Install Certbot
sudo apt install certbot

# Stop Docker containers temporarily
sudo docker-compose down

# Obtain SSL certificate
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email admin@yourdomain.com \
  --agree-tos

# Copy certificates to project
./enable-https.sh
```

### 5. HTTPS Deployment
```bash
# Deploy with SSL
sudo docker-compose -f docker-compose.ssl.yml up -d --build

# Fix mixed content issues (if upgrading from HTTP)
./fix-mixed-content.sh
```

## 🐳 Docker Compose Configurations

### Available Configurations

| File | Purpose | Nginx | SSL | Use Case |
|------|---------|-------|-----|----------|
| `docker-compose.simple.yml` | API testing | ❌ | ❌ | Development API testing |
| `docker-compose.prod.yml` | Direct access | ❌ | ❌ | Testing without domain |
| `docker-compose.yml` | HTTP production | ✅ | ❌ | Initial production setup |
| `docker-compose.ssl.yml` | HTTPS production | ✅ | ✅ | Final production with SSL |

### Environment Variables

#### Required for Production
```env
# API Configuration
SECRET_KEY=your-secure-secret-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key

# Domain Configuration (for SSL deployment)
DOMAIN_NAME=yourdomain.com
SSL_EMAIL=admin@yourdomain.com
```

#### Frontend Configuration
- **HTTP**: `NUXT_PUBLIC_API_BASE=http://api:5000/api`
- **HTTPS**: `NUXT_PUBLIC_API_BASE=https://yourdomain.com/api`

## 🔧 Automated Scripts

### Deployment Scripts
- **`deploy-production.sh`** - Complete production deployment automation
- **`enable-https.sh`** - SSL certificate setup and HTTPS enablement
- **`fix-mixed-content.sh`** - Fix HTTP/HTTPS mixed content issues

### Diagnostic Scripts
- **`diagnose-domain-access.sh`** - Domain and networking diagnostics
- **`test-container-network.sh`** - Container connectivity testing

## 🩺 Health Checks & Monitoring

### Manual Health Checks
```bash
# API Health
curl https://yourdomain.com/api/health

# Frontend Health
curl https://yourdomain.com

# Container Status
sudo docker ps

# Container Logs
sudo docker-compose logs -f
```

### Automated Monitoring
The deployment includes built-in health checks:
- **API**: `/api/health` endpoint with database status
- **Frontend**: HTTP response check
- **Nginx**: SSL certificate and proxy health

## 🔒 Security Features

### SSL/TLS Configuration
- **TLS 1.2/1.3 only** - Modern encryption protocols
- **HSTS headers** - Force HTTPS for enhanced security
- **Security headers** - XSS protection, content type sniffing prevention
- **Perfect Forward Secrecy** - RSA and ECDHE cipher suites

### Container Security
- **Non-root containers** - All services run as unprivileged users
- **Read-only filesystems** - Where applicable
- **Health checks** - Automatic restart on failure
- **Resource limits** - Prevent resource exhaustion

## 🔄 Maintenance & Updates

### Application Updates
```bash
# Pull latest changes
git pull

# Rebuild and deploy
sudo docker-compose -f docker-compose.ssl.yml up -d --build
```

### SSL Certificate Renewal
```bash
# Manual renewal
sudo certbot renew

# Restart nginx to load new certificates
sudo docker-compose restart nginx

# Automated renewal (add to crontab)
0 12 * * * /usr/bin/certbot renew --quiet --post-hook "docker-compose restart nginx"
```

### Backup & Recovery
```bash
# Backup database
sudo docker exec arrowtuner-api sqlite3 /app/arrow_database.db ".backup /app/backup.db"
sudo docker cp arrowtuner-api:/app/backup.db ./backup-$(date +%Y%m%d).db

# Backup SSL certificates
sudo cp -r /etc/letsencrypt/live/yourdomain.com ./ssl-backup-$(date +%Y%m%d)
```

## 🐛 Common Issues & Solutions

### Container Issues
```bash
# Frontend "nuxt: not found"
# Solution: Ensure using production Docker Compose files
sudo docker-compose -f docker-compose.ssl.yml up -d --build

# API database errors
# Solution: Check database schema compatibility
curl https://yourdomain.com/api/health

# Mixed content errors
# Solution: Update API base URL for HTTPS
./fix-mixed-content.sh
```

### Network Issues
```bash
# Domain not accessible
# Check DNS, nginx, and firewall
./diagnose-domain-access.sh

# SSL certificate errors
# Verify certificates and nginx configuration
sudo docker-compose logs nginx
```

### Permission Issues
```bash
# Docker permission denied
sudo usermod -aG docker $USER
newgrp docker

# SSL certificate access
sudo chown $USER:$USER ./deploy/ssl/*.pem
```

## 📊 Performance Optimization

### Production Settings
- **Database**: Embedded SQLite with 152+ arrows pre-loaded
- **Frontend**: Nuxt 3 with SSR and static generation
- **Caching**: Nginx static file caching
- **Compression**: Gzip compression for text content

### Scaling Considerations
- **Load Balancing**: Use multiple frontend containers with nginx upstream
- **Database**: Consider PostgreSQL for high-traffic deployments
- **CDN**: Serve static assets through CDN for global performance

## 🎯 Success Metrics

After successful deployment, verify:
- ✅ **HTTPS access**: https://yourdomain.com loads without errors
- ✅ **API health**: https://yourdomain.com/api/health returns healthy status
- ✅ **Arrow data**: Database shows 152+ arrows from 13+ manufacturers
- ✅ **SSL rating**: A+ rating on SSL Labs test
- ✅ **Performance**: Page load times under 2 seconds

## 🆘 Support & Troubleshooting

### Log Analysis
```bash
# View all container logs
sudo docker-compose logs

# View specific service logs
sudo docker-compose logs frontend
sudo docker-compose logs api
sudo docker-compose logs nginx

# Follow live logs
sudo docker-compose logs -f
```

### Debug Mode
```bash
# Enable debug mode for troubleshooting
export FLASK_DEBUG=true
sudo docker-compose -f docker-compose.ssl.yml up -d --build
```

For additional support, check the main documentation in `CLAUDE.md` or create an issue in the repository.