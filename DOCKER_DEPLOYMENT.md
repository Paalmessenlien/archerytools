# Docker Deployment Guide for Archery Tools

## Overview

This guide covers the complete Docker deployment process for Archery Tools, a comprehensive arrow database and tuning calculator platform. The system uses a dual architecture with a Nuxt 3 frontend and Flask API backend.

## Prerequisites

- Docker and Docker Compose installed
- Domain name configured (for production)
- SSL certificates (for HTTPS deployment)
- Existing arrow data JSON files in `arrow_scraper/data/processed/`

## Quick Start

### Development Deployment

```bash
# Basic development deployment
docker-compose up -d --build

# With enhanced verification
./docker-deploy.sh
```

### Production Deployment

**⚠️ CRITICAL: Always import data BEFORE Docker build**

```bash
# Step 1: Import data FIRST (NO scraping on server)
./production-import-only.sh

# Step 2: Then deploy with enhanced verification
./deploy-enhanced.sh docker-compose.enhanced-ssl.yml

# Alternative: Use integrated setup (handles import automatically)
./docker-production-setup.sh docker-compose.enhanced-ssl.yml auto
```

## Architecture

### Container Structure

1. **Frontend Container** (`archerytools-frontend`)
   - Nuxt 3 application
   - Node.js 18+ runtime
   - Serves on port 3000

2. **API Container** (`archerytools-api`)
   - Flask REST API
   - Python 3.12 runtime
   - Serves on port 5000

3. **Nginx Container** (production only)
   - Reverse proxy
   - SSL termination
   - Serves on ports 80/443

### Data Persistence

All data is persisted using Docker volumes:

- `user-data`: User accounts and bow setups
- `arrow-data`: Arrow database (imported from JSON files)
- `nginx-logs`: Web server logs
- `ssl-certs`: SSL certificates

## Deployment Options

### 1. Simple Development

```bash
# API-only testing
docker-compose -f docker-compose.simple.yml up -d --build

# Access: http://localhost:5000
```

### 2. Full Development

```bash
# Frontend + API with hot reload
docker-compose up -d --build

# Access:
# - Frontend: http://localhost:3000
# - API: http://localhost:5000
```

### 3. Production (HTTP)

```bash
# Prepare data first (NO scraping)
./production-import-only.sh

# Deploy
docker-compose -f docker-compose.prod.yml up -d --build

# Access: http://yourdomain.com
```

### 4. Production (HTTPS)

```bash
# Option A: Automatic SSL detection and deployment (RECOMMENDED)
./check-ssl-and-deploy.sh docker-compose.enhanced-ssl.yml

# Option B: Manual SSL setup
# Prepare data and SSL certificates
./production-import-only.sh
sudo certbot certonly --standalone -d yourdomain.com

# Deploy with SSL
sudo docker-compose -f docker-compose.enhanced-ssl.yml up -d --build

# Access: https://yourdomain.com
```

## Data Management

### Important: No Server-Side Scraping

The production system **ONLY imports existing JSON data files**. No web scraping is performed on the production server.

### Importing Arrow Data

```bash
# Option 1: Clean import script (recommended)
./production-import-only.sh

# Option 2: Manual import
cd arrow_scraper
python import_existing_data.py
```

### Data Sources

Arrow data must be present in `arrow_scraper/data/processed/` as JSON files:
- Carbon arrow manufacturers (Easton, Gold Tip, Victory, etc.)
- European manufacturers (Nijora, DK Bow, Aurel, BigArchery)
- Traditional wood arrows (Cedar, Pine, Bamboo, Ash, Birch, Fir)

### Creating Sample Data

If no JSON files exist, the import script creates minimal sample data including:
- Sample carbon arrows
- Traditional wood arrows (6 types)
- Basic spine specifications

## Environment Configuration

### Required Environment Variables

Create `.env` file in project root:

```env
# API Configuration
SECRET_KEY=your-secret-key-here-change-this
API_PORT=5000
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com

# Frontend Configuration
FRONTEND_PORT=3000
NUXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
NODE_ENV=production
NUXT_PUBLIC_API_BASE=http://localhost:5000

# Production Domain
DOMAIN_NAME=yourdomain.com
SSL_EMAIL=admin@yourdomain.com
```

## Health Checks

### Container Health

```bash
# Check all containers
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f frontend

# Health endpoints
curl http://localhost:5000/api/health
curl http://localhost:3000
```

### Database Verification

```bash
# Check database contents
docker exec archerytools-api-1 python -c "
import sqlite3
conn = sqlite3.connect('/app/arrow_database.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM arrows')
print(f'Arrows: {cursor.fetchone()[0]}')
cursor.execute('SELECT COUNT(DISTINCT manufacturer) FROM arrows')
print(f'Manufacturers: {cursor.fetchone()[0]}')
"
```

## Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker-compose logs api
docker-compose logs frontend

# Rebuild from scratch
docker-compose down -v
./production-import-only.sh
docker-compose up -d --build
```

#### 2. Database Empty
```bash
# Re-import data
docker-compose down
./production-import-only.sh
docker-compose up -d
```

#### 3. Permission Errors
```bash
# Fix permissions
sudo chown -R $USER:$USER docker-volumes/
chmod -R 755 docker-volumes/
```

#### 4. Mixed Content (HTTPS)
```bash
# Update environment for HTTPS
NUXT_PUBLIC_API_BASE=https://yourdomain.com/api
# Rebuild frontend
docker-compose up -d --build frontend
```

## Maintenance

### Backup

```bash
# Backup databases
docker run --rm -v archerytools_user-data:/data -v $(pwd):/backup alpine tar czf /backup/user-data-backup.tar.gz -C /data .
docker run --rm -v archerytools_arrow-data:/data -v $(pwd):/backup alpine tar czf /backup/arrow-data-backup.tar.gz -C /data .
```

### Restore

```bash
# Restore databases
docker run --rm -v archerytools_user-data:/data -v $(pwd):/backup alpine tar xzf /backup/user-data-backup.tar.gz -C /data
docker run --rm -v archerytools_arrow-data:/data -v $(pwd):/backup alpine tar xzf /backup/arrow-data-backup.tar.gz -C /data
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose down
./production-import-only.sh
docker-compose up -d --build
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to git
2. **SSL Certificates**: Always use HTTPS in production
3. **Secrets**: Use strong SECRET_KEY values
4. **Firewall**: Only expose necessary ports (80/443)
5. **Updates**: Regularly update base images

## Performance Optimization

### Docker Resource Limits

```yaml
# In docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

### Scaling

```bash
# Scale API containers
docker-compose up -d --scale api=3
```

## Monitoring

### Simple Monitoring

```bash
# Resource usage
docker stats

# Container status
./docker-production-setup.sh status
```

### Log Management

```bash
# View logs
docker-compose logs --tail=100 -f

# Export logs
docker-compose logs > deployment.log
```

## Quick Reference

### Essential Commands

```bash
# Deploy production (no scraping)
./production-import-only.sh && docker-compose -f docker-compose.enhanced-ssl.yml up -d --build

# Stop all containers
docker-compose down

# Remove everything (including volumes)
docker-compose down -v

# Restart services
docker-compose restart

# View status
docker-compose ps
```

### File Structure

```
archerytools/
├── docker-compose.yml              # Development compose
├── docker-compose.enhanced-ssl.yml # Production HTTPS compose
├── docker-compose.prod.yml         # Production HTTP compose
├── docker-compose.simple.yml       # API-only compose
├── production-import-only.sh       # Data import script (NO scraping)
├── docker-production-setup.sh      # Automated deployment
├── deploy-enhanced.sh              # Enhanced deployment script
├── arrow_scraper/
│   ├── Dockerfile.enhanced         # API container
│   ├── import_existing_data.py     # Data import script
│   └── data/processed/            # JSON arrow data files
└── frontend/
    └── Dockerfile.enhanced         # Frontend container
```

## Support

For issues or questions:
- Check container logs: `docker-compose logs`
- Verify health endpoints: `/api/health`
- Ensure JSON data files exist in `data/processed/`
- Review environment variables in `.env`

Remember: **Production deployments do NOT perform web scraping** - only import existing JSON data.