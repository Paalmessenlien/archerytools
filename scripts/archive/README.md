# Archived Startup and Deployment Scripts

This folder contains legacy startup and deployment scripts that have been replaced by the unified `start-unified.sh` script.

## Archived Scripts

### Startup Scripts (Replaced by `start-unified.sh`)
- `start-fresh.sh` - Fresh startup script
- `restart-unified.sh` - Unified restart script  
- `start-docker-dev.sh` - Docker development startup
- `start-local-dev.sh` - Local development startup (functionality moved to `start-unified.sh dev`)
- `start-hybrid-dev.sh` - Hybrid development environment

### Deployment Scripts (Replaced by `start-unified.sh`)
- `deploy-production.sh` - Production deployment
- `docker-deploy.sh` - Docker deployment
- `deploy-enhanced.sh` - Enhanced deployment
- `docker-deploy-safe.sh` - Safe docker deployment
- `check-ssl-and-deploy.sh` - SSL deployment
- `deploy-with-cleanup.sh` - Deployment with cleanup
- `quick-deploy.sh` - Quick deployment
- `deploy-fresh.sh` - Fresh deployment
- `quick-deploy-production.sh` - Quick production deployment
- `deploy-production-ssl.sh` - Production SSL deployment
- `test-simple-deployment.sh` - Simple deployment test
- `test-deployment.sh` - Deployment test

### Docker Compose Files (Replaced by `docker-compose.unified.yml`)
- `docker-compose.yml` - Original compose file
- `docker-compose.enhanced-ssl.yml` - Enhanced SSL compose
- `docker-compose.dev.fallback.yml` - Development fallback
- `docker-compose.dev.yml` - Development compose

## New Unified Usage

All functionality has been consolidated into `start-unified.sh`:

```bash
# Local development (no Docker)
./start-unified.sh dev

# Stop local development
./start-unified.sh dev stop

# Docker development
./start-unified.sh development

# Production HTTP
./start-unified.sh production

# Production HTTPS
./start-unified.sh ssl yourdomain.com
```

These archived scripts are kept for reference and can be removed after confirming the unified script works correctly.