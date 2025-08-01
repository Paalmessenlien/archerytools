# Safe Production Deployment Guide

This guide ensures user data is preserved during Docker deployments.

## 😨 Problem

The original `docker-deploy.sh` script calls `docker-cleanup.sh` which uses the `--volumes` flag, causing all user data to be wiped on every deployment.

## ✅ Solution

We've created safe deployment scripts that preserve user data volumes:

1. **Fixed `docker-cleanup.sh`** - Removed the `--volumes` flag
2. **Created `docker-deploy-safe.sh`** - Safe deployment script
3. **Created `docker-backup-userdata.sh`** - Backup script for user data

## 🚀 Production Deployment (Preserving User Data)

### Option 1: Using the Safe Deployment Script (Recommended)

```bash
# For HTTPS production deployment
./docker-deploy-safe.sh docker-compose.ssl.yml --build

# For enhanced production deployment
./docker-deploy-safe.sh docker-compose.enhanced-ssl.yml --build
```

### Option 2: Manual Safe Deployment

```bash
# 1. Backup user data first (optional but recommended)
./docker-backup-userdata.sh

# 2. Stop containers WITHOUT removing volumes
docker-compose -f docker-compose.ssl.yml down

# 3. Rebuild and start
docker-compose -f docker-compose.ssl.yml up -d --build
```

## 💾 Backup and Restore

### Create Backup

```bash
# Creates timestamped backup in ./backups/
./docker-backup-userdata.sh
```

### Restore from Backup

```bash
# Replace TIMESTAMP with actual backup timestamp
docker run --rm \
  -v arrowtuner-userdata:/data \
  -v "$(pwd)/backups/userdata_backup_TIMESTAMP.tar.gz":/backup.tar.gz \
  alpine sh -c 'cd /data && tar xzf /backup.tar.gz'
```

## 🔍 Verify User Data Persistence

```bash
# Check if user data volume exists
docker volume ls | grep arrowtuner-userdata

# Inspect volume contents
docker run --rm -v arrowtuner-userdata:/data alpine ls -la /data/
```

## ⚠️  Important Notes

1. **Never use** `docker-compose down -v` or `--volumes` flag in production
2. **Always backup** before major updates
3. **Test locally** before deploying to production
4. The user database is stored at `/app/user_data/user_data.db` inside the container
5. The volume `arrowtuner-userdata` persists this data between deployments

## 🔄 Migration from Old Setup

If you've been using the old deployment method and lost user data:

1. Deploy using the safe method going forward
2. Users will need to re-register (one-time inconvenience)
3. Consider implementing a data migration strategy if you have backups

## 📋 Deployment Checklist

- [ ] Backup existing user data with `./docker-backup-userdata.sh`
- [ ] Use `docker-deploy-safe.sh` instead of `docker-deploy.sh`
- [ ] Verify volumes are preserved after deployment
- [ ] Test user login to confirm data persistence
- [ ] Monitor logs for any database errors