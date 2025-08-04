# 🏹 ArrowTuner Unified Architecture Migration Guide

## Overview

This guide helps you migrate from the old multi-configuration setup to the new unified architecture that provides consistent database paths and deployment configurations across all environments.

## 🚨 What's Changing

### Before (11 Docker Compose Files)
- `docker-compose.yml`
- `docker-compose.enhanced-ssl.yml`
- `docker-compose.prod.yml`
- `docker-compose.ssl.yml`
- `docker-compose.dev.yml`
- ... and 6 more variations

### After (1 Unified Configuration)
- `docker-compose.unified.yml` - Single configuration for ALL scenarios
- Environment-aware settings for development/production/SSL

### Database Path Changes

| Component | Old Path | New Unified Path |
|-----------|----------|------------------|
| Arrow Database (Docker) | `/app/arrow_database.db` or `/app/arrow_data/arrow_database.db` | `/app/databases/arrow_database.db` |
| User Database (Docker) | `/app/user_data.db` or `/app/user_data/user_data.db` | `/app/databases/user_data.db` |
| Arrow Database (Local) | `arrow_scraper/arrow_database.db` | `arrow_scraper/databases/arrow_database.db` |
| User Database (Local) | `arrow_scraper/user_data.db` | `arrow_scraper/databases/user_data.db` |

## 📋 Pre-Migration Checklist

1. **Backup Your Data**
   ```bash
   # If using old setup, backup first
   ./backup-databases.sh
   ```

2. **Note Your Current Setup**
   - Which docker-compose file are you using?
   - Are you running locally or in Docker?
   - Do you have SSL configured?

3. **Check Docker Volumes**
   ```bash
   docker volume ls | grep arrowtuner
   ```

## 🔄 Migration Steps

### Step 1: Stop Current Services

```bash
# Stop all running services
docker-compose down  # Add your specific compose file if not default

# Or if running multiple compose files
docker-compose -f docker-compose.enhanced-ssl.yml down
docker-compose -f docker-compose.prod.yml down
# etc.
```

### Step 2: Backup Existing Data

```bash
# Create a manual backup of databases
mkdir -p ~/arrowtuner-backup
cp arrow_scraper/arrow_database.db ~/arrowtuner-backup/ 2>/dev/null || true
cp arrow_scraper/user_data.db ~/arrowtuner-backup/ 2>/dev/null || true

# If using Docker volumes, export them
docker run --rm -v arrowtuner2_arrowtuner-userdata:/data -v $(pwd):/backup alpine tar czf /backup/userdata-backup.tar.gz -C /data .
```

### Step 3: Clean Up Old Containers (Optional)

```bash
# Remove old containers but keep volumes
docker container prune -f
docker image prune -f
```

### Step 4: Start Unified Setup

#### For Development
```bash
./start-unified.sh development
```

#### For Production (HTTP)
```bash
./start-unified.sh production yourdomain.com
```

#### For Production (HTTPS/SSL)
```bash
# Make sure SSL certificates are in place
mkdir -p deploy/ssl
cp /path/to/your/cert.pem deploy/ssl/
cp /path/to/your/key.pem deploy/ssl/

# Start with SSL
./start-unified.sh ssl yourdomain.com
```

### Step 5: Verify Migration

```bash
# Check services are running
docker-compose -f docker-compose.unified.yml ps

# Check logs
./logs-unified.sh

# Verify databases were migrated
docker-compose -f docker-compose.unified.yml exec api ls -la /app/databases/
```

## 🛠️ Using the New Unified Scripts

### Starting Services
```bash
# Development
./start-unified.sh

# Production
./start-unified.sh production yourdomain.com

# SSL/HTTPS
./start-unified.sh ssl yourdomain.com
```

### Managing Services
```bash
# View logs
./logs-unified.sh          # All services
./logs-unified.sh api      # API only
./logs-unified.sh frontend # Frontend only

# Stop services
./stop-unified.sh          # Stop only
./stop-unified.sh --remove # Stop and remove containers
./stop-unified.sh --clean  # Stop, remove containers AND volumes (careful!)

# Backup
./backup-unified.sh
./backup-unified.sh --name my_backup
./backup-unified.sh --cleanup --keep 5

# Restore
./restore-unified.sh --list
./restore-unified.sh --file backup_20240101_120000.tar.gz
```

## 🔧 Environment Variables

### Required in `.env` file:
```bash
# API Keys
DEEPSEEK_API_KEY=your_key_here
NUXT_PUBLIC_GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_secret

# Deployment (set these or use command line)
DEPLOYMENT_MODE=development  # or production, ssl
DOMAIN_NAME=localhost        # or yourdomain.com
```

### Automatically Set by Unified System:
```bash
# Database paths (DO NOT override these)
ARROW_DATABASE_PATH=/app/databases/arrow_database.db
USER_DATABASE_PATH=/app/databases/user_data.db
```

## 🚨 Troubleshooting

### Issue: Databases not found after migration
```bash
# The unified system will automatically migrate databases
# If it fails, check the init logs:
docker-compose -f docker-compose.unified.yml logs db-init
```

### Issue: Old containers interfering
```bash
# Clean up all old containers
./stop-unified.sh --clean
docker system prune -a  # Careful - removes all unused images
```

### Issue: Permission errors
```bash
# Fix permissions inside container
docker-compose -f docker-compose.unified.yml exec api chmod -R 775 /app/databases
```

### Issue: SSL not working
```bash
# Verify certificates are in place
ls -la deploy/ssl/
# Should show cert.pem and key.pem

# Check nginx logs
./logs-unified.sh nginx
```

## ✅ Post-Migration Cleanup

Once everything is working:

1. **Remove old compose files** (optional, keep for reference)
   ```bash
   mkdir old-configs
   mv docker-compose.*.yml old-configs/
   mv docker-compose.yml old-configs/
   # Keep only docker-compose.unified.yml
   ```

2. **Update your deployment scripts**
   - Replace any references to old compose files
   - Update CI/CD pipelines to use `start-unified.sh`

3. **Update documentation**
   - Update README.md to reference unified setup
   - Update any internal docs

## 📚 Benefits of Unified Architecture

1. **Consistency**: Same paths everywhere (local, Docker, production)
2. **Simplicity**: One configuration file instead of 11
3. **Flexibility**: Easy switching between dev/prod/SSL modes
4. **Maintainability**: Updates in one place affect all deployments
5. **Reliability**: Automatic database migration and verification
6. **Security**: Proper SSL handling and security headers

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `./logs-unified.sh`
2. Verify services: `docker-compose -f docker-compose.unified.yml ps`
3. Check this guide's troubleshooting section
4. Create an issue on GitHub with:
   - Your migration steps
   - Error messages
   - Output of `docker-compose -f docker-compose.unified.yml ps`
   - Relevant log entries

## 🎉 Migration Complete!

Your ArrowTuner platform is now running on the unified architecture. Enjoy the simplified management and consistent behavior across all environments!