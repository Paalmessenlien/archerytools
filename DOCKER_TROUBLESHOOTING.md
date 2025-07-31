# Docker Deployment Troubleshooting Guide

## Current Issue: Enhanced Dockerfile Build Hanging

If your Docker build is hanging on the verification step:

```
Step 15/19 : RUN echo "🔍 Final build verification..." && python3 -c "import sys; import os; sys.path.append('/app'); exec('try:\\n    from user_database import UserDatabase\\n    from arrow_database import ArrowDatabase\\n    import flask, sqlite3, requests, jwt\\n    print(\"✅ All imports successful\")\\nexcept ImportError as e:\\n    print(f\"❌ Import failed: {e}\")\\n    exit(1)')" && echo "✅ Build
```

## Quick Solutions

### Solution 1: Use Quick Deploy (Recommended)
```bash
# Stop current build (Ctrl+C if needed)
# Use minimal configuration for fast deployment
./quick-deploy.sh
```

### Solution 2: Use Minimal Docker Compose
```bash
# Clean up first
docker-compose down --remove-orphans
docker system prune -f

# Import data
./production-import-only.sh

# Deploy with minimal config
docker-compose -f docker-compose.minimal.yml up -d --build
```

### Solution 3: Skip Enhanced Features
```bash
# Use fixed configuration without complex verification
./deploy-with-cleanup.sh docker-compose.fixed.yml
```

## Root Causes

1. **Enhanced Dockerfile Complexity**: The enhanced version includes extensive verification steps that can hang
2. **Missing Dependencies**: Python imports failing during build verification
3. **Resource Constraints**: Build process running out of memory or time
4. **Container Config Conflicts**: Cached configurations causing issues

## Available Deployment Options

### 🚀 Quick Deploy (Fastest)
- File: `docker-compose.minimal.yml`
- Features: Basic services, standard Dockerfiles, no complex verification
- Use: `./quick-deploy.sh`

### 🔒 Production SSL Deploy (Recommended for Production)
- File: `docker-compose.minimal-ssl.yml`
- Features: Fast deployment with SSL certificates and HTTPS
- Use: `./deploy-production-ssl.sh yourdomain.com`
- Alternative: `./quick-deploy.sh ssl yourdomain.com`

### 🔧 Fixed Deploy (Reliable)
- File: `docker-compose.fixed.yml`
- Features: Simplified enhanced features, better compatibility
- Use: `./deploy-with-cleanup.sh docker-compose.fixed.yml`

### 🛡️ Enhanced Deploy (Full Features)
- File: `docker-compose.enhanced-ssl.yml`
- Features: Full verification, SSL support, comprehensive health checks
- Use: `./check-ssl-and-deploy.sh` (only when enhanced build works)

## Troubleshooting Steps

### 1. Check Docker Resources
```bash
docker system df
docker stats
```

### 2. Check Build Progress
```bash
# In another terminal, check if containers are actually building
docker ps -a
docker logs <container-id>
```

### 3. Force Clean Rebuild
```bash
# Complete cleanup
./fix-docker-config-error.sh

# Then try quick deploy
./quick-deploy.sh
```

### 4. Check for Specific Errors
```bash
# Check Docker daemon logs (if needed)
sudo journalctl -u docker.service --since "1 hour ago"
```

## Prevention

1. **Always import data first**: `./production-import-only.sh`
2. **Use quick deploy for testing**: `./quick-deploy.sh`
3. **Only use enhanced for production**: After testing with minimal
4. **Clean up regularly**: Run cleanup scripts periodically

## Emergency Recovery

If nothing works:
```bash
# Nuclear option - complete Docker reset
docker system prune -a --volumes
docker container prune -f
docker image prune -a -f
docker network prune -f
docker volume prune -f

# Then restart Docker daemon
sudo systemctl restart docker

# Finally, try quick deploy
./production-import-only.sh
./quick-deploy.sh
```

## Success Indicators

After deployment, you should see:
- ✅ API responding at http://localhost:5000/api/simple-health
- ✅ Frontend responding at http://localhost:3000
- ✅ Nginx responding at http://localhost/health
- ✅ All containers showing as healthy in `docker-compose ps`

## Getting Help

If issues persist:
1. Check the service logs: `docker-compose logs -f`
2. Verify data import: Check if arrow_database.db exists and has data
3. Test individual services: Try API-only deployment first
4. Use minimal configuration until issues are resolved