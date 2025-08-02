# Production Reset Scripts Guide

This guide provides comprehensive scripts for completely resetting and rebuilding your production environment from scratch.

## 🚀 Quick Start

### Complete Production Reset (Recommended)
```bash
# Complete reset with SSL for your domain
./production-reset-complete.sh yourdomain.com

# Complete reset HTTP-only (no domain)
./production-reset-complete.sh
```

### Individual Components

#### 1. Database Only Reset
```bash
# Rebuild just the databases
./production-database-rebuild.sh
```

#### 2. Quick Deployment
```bash
# Deploy with SSL
./quick-deploy-production.sh --domain yourdomain.com

# Deploy HTTP-only
./quick-deploy-production.sh --http
```

## 📋 Script Overview

### `production-reset-complete.sh`
**Complete production environment reset**
- ✅ Complete Docker cleanup (containers, images, volumes)
- ✅ Database removal and rebuild
- ✅ Fresh data import from JSON files
- ✅ Clean deployment with SSL support
- ✅ Health verification and status reporting

**Usage:**
```bash
./production-reset-complete.sh [domain.com]
```

### `production-database-rebuild.sh`
**Database-only rebuild**
- ✅ Removes all existing database files
- ✅ Imports latest arrow data from JSON files
- ✅ Applies all database migrations
- ✅ Verifies database integrity
- ✅ Creates user database with latest schema

**Usage:**
```bash
./production-database-rebuild.sh
```

### `quick-deploy-production.sh`
**Fast deployment for existing databases**
- ✅ Cleans up existing containers
- ✅ Updates environment configuration
- ✅ Deploys with appropriate SSL/HTTP configuration
- ✅ Health checks and status reporting

**Usage:**
```bash
./quick-deploy-production.sh [options] [domain]

Options:
  --domain DOMAIN    Deploy with SSL for specified domain
  --ssl              Enable SSL mode (will prompt for domain)
  --http             Force HTTP-only deployment
```

## 🗄️ Database Information

### What Gets Reset
- **Arrow Database** (`arrow_database.db`): All arrow specifications and spine data
- **User Database** (`user_data.db`): User accounts, bow setups, guide sessions
- **Component Database** (`component_database.db`): Arrow components (if exists)
- **Log Files**: All application logs

### What Gets Imported
- **Arrow Data**: From `data/processed/*.json` files (excluding `*learn*` files)
- **Component Data**: From `data/processed/components/*.json` files (if available)
- **Database Schema**: Latest migrations and schema updates

### Data Sources
The scripts import data from:
```
arrow_scraper/data/processed/
├── Easton_Archery_update_*.json
├── Gold_Tip_update_*.json
├── Victory_Archery_update_*.json
├── Carbon_Express_update_*.json
└── components/
    └── tophat_archery_components_*.json
```

## 🐳 Docker Configuration

### Deployment Options

#### SSL Deployment (Production)
Uses `docker-compose.enhanced-ssl.yml` or `docker-compose.ssl.yml`:
- Nginx reverse proxy with SSL termination
- HTTPS redirects
- Security headers
- Production-optimized settings

#### HTTP Deployment (Development/Testing)
Uses `docker-compose.fresh.yml`:
- Simple HTTP configuration
- Direct port access
- Development-friendly setup

### Container Names
Fresh deployment uses unique container names to avoid conflicts:
- `fresh-archery-api`
- `fresh-archery-frontend`
- `fresh-archery-nginx`

## 🔧 Environment Configuration

### Required Environment Variables
Create or update `.env` file:
```bash
# API Configuration
SECRET_KEY=your-secret-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key-here
API_PORT=5000

# Frontend Configuration
FRONTEND_PORT=3000
NODE_ENV=production
NUXT_PUBLIC_API_BASE=https://yourdomain.com/api  # or http://localhost:5000/api

# Google OAuth
NUXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com  # or http://localhost
```

## 🔍 Troubleshooting

### Common Issues

#### Database Empty After Reset
- **Cause**: No JSON update files found in `data/processed/`
- **Solution**: Ensure JSON files exist or run scraper locally first

#### Container Conflicts
- **Cause**: Existing containers with same names
- **Solution**: Use `./nuclear-docker-reset.sh` for complete cleanup

#### SSL Certificate Issues
- **Cause**: DNS not pointing to server or certbot not installed
- **Solution**: Configure DNS first, then run `sudo certbot certonly --standalone -d yourdomain.com`

#### API/Frontend Not Responding
- **Cause**: Services still starting up or database connection issues
- **Solution**: Wait 2-3 minutes, check logs with `docker-compose logs`

### Health Check Commands
```bash
# Check API
curl https://yourdomain.com/api/simple-health

# Check database stats
curl https://yourdomain.com/api/database-stats

# Check container status
docker ps

# View logs
docker-compose logs -f
```

## 📊 Success Verification

After running any reset script, verify:

1. **API Health**: Should return HTTP 200
2. **Database Content**: Should show 100+ arrows from 10+ manufacturers
3. **Frontend Access**: Should load without errors
4. **User Registration**: Should work with Google OAuth

### Expected Results
```
📊 System Status:
  API Status: HTTP 200
  Frontend Status: HTTP 200
  Database: 147 arrows from 13 manufacturers

🌐 Access URLs:
  Main Site: https://yourdomain.com
  API: https://yourdomain.com/api
```

## 🚨 Important Notes

1. **Data Loss Warning**: These scripts completely remove all user data, bow setups, and arrow assignments
2. **Production Use**: Always backup important data before running reset scripts
3. **SSL Setup**: Ensure DNS is configured before attempting SSL deployment
4. **Docker Requirements**: Requires Docker and Docker Compose to be installed
5. **Environment Variables**: Update `.env` file with your actual API keys and domains

## 🔄 Workflow Examples

### New Server Setup
```bash
# 1. Clone repository
git clone https://github.com/Paalmessenlien/archerytools.git
cd archerytools

# 2. Complete reset with SSL
./production-reset-complete.sh yourdomain.com
```

### Existing Server Refresh
```bash
# 1. Pull latest changes
git pull origin main

# 2. Quick reset and deploy
./production-reset-complete.sh yourdomain.com
```

### Database Issues Only
```bash
# 1. Rebuild databases only
./production-database-rebuild.sh

# 2. Quick deploy without full reset
./quick-deploy-production.sh --domain yourdomain.com
```

---

**Need Help?** Check the logs with `docker-compose logs` or create an issue in the repository.