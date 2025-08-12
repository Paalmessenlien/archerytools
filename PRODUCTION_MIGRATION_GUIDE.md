# Production Migration Guide

## Overview

This guide explains how to deploy the database migration system to your production server and resolve the spine chart system issues.

## Problem Summary

The original issue was that spine chart data was not available in production because:
1. Migration system was running on the host instead of inside Docker containers
2. Production databases are located inside Docker containers at `/app/databases/`
3. Host-based migrations couldn't access the actual production database

## Solution

The enhanced migration system now:
- ✅ **Detects Docker environment** automatically
- ✅ **Runs migrations inside containers** where the production database exists
- ✅ **Copies all migration dependencies** to containers automatically
- ✅ **Imports 21 spine charts** and arrow specification data
- ✅ **Resolves API 500 errors** for spine chart endpoints

## Deployment Steps

### Step 1: Update Production Code

On your production server:

```bash
# Navigate to project directory
cd /root/archerytools  # or your project path

# Pull latest changes
git pull

# Verify migration files are present
ls -la docker-migration-runner.sh
ls -la arrow_scraper/run_migrations.py
ls -la arrow_scraper/migrations/
```

### Step 2: Test Docker Migration System

Run the test script to verify everything is configured correctly:

```bash
# Test Docker migration integration
./test-docker-migrations.sh
```

This will:
- Check Docker access and running containers
- Verify database connectivity inside containers  
- Test migration status checking
- Confirm the system is ready for migration

### Step 3: Run Migrations Manually (Recommended)

For the initial deployment, run migrations manually to see the process:

```bash
# Check current migration status
./docker-migration-runner.sh status

# Run migrations (this will import spine chart data)
./docker-migration-runner.sh migrate
```

Expected output:
```
✅ Created spine calculator tables
🔄 Importing spine calculator data...
✓ Imported 21 new spine charts, updated 0 existing charts
✅ JSON data import completed
```

### Step 4: Restart Production System (Alternative)

Alternatively, restart your production system to run migrations automatically:

```bash
# This will automatically run migrations during startup
./start-unified.sh ssl yourdomain.com
```

The startup script will:
1. Detect Docker environment
2. Run `docker-migration-runner.sh` automatically
3. Import all spine chart data
4. Start services with working spine chart system

### Step 5: Verify Resolution

After migrations complete, verify the fix:

1. **Check API Health:**
   ```bash
   curl https://yourdomain.com/api/health
   ```

2. **Test Spine Chart Endpoint:**
   ```bash
   curl https://yourdomain.com/api/spine-charts
   ```
   Should return spine chart data instead of 500 error

3. **Check Database:**
   ```bash
   # Inside container
   docker exec <container-name> sqlite3 /app/databases/arrow_database.db "SELECT COUNT(*) FROM manufacturer_spine_charts_enhanced"
   ```
   Should return `21`

4. **Test Frontend:**
   - Visit your spine chart management page
   - Should show 21 spine charts available
   - No more "Failed to get spine charts" errors

## Migration System Features

### Automatic Docker Detection

The system automatically detects when running in Docker environment:

```bash
# In start-unified.sh
if command -v docker &> /dev/null && docker ps &> /dev/null; then
    echo "🐳 Detected Docker environment, using Docker migration runner..."
    ./docker-migration-runner.sh migrate
fi
```

### Container File Management

The migration system automatically copies all required files to containers:

- Migration scripts and dependencies
- Spine calculator data (21 charts)
- Arrow specification JSON files
- Database import managers

### Fallback System

If Docker migrations fail, the system gracefully falls back to host-based migration attempts.

## Migration Data

The migration system imports:

### Spine Chart Data (21 Charts)
- Birch Laminated Wood Arrows (recurve)
- Douglas Fir Traditional Wood Arrows (recurve)  
- Easton Aluminum Arrows XX75/XX78 (compound and recurve)
- Easton Hunting arrows (compound)
- Plus 17 additional manufacturer-specific spine charts

### Arrow Specifications
- Gold Tip: 20 arrow models
- Easton: 25+ arrow models
- Victory, Carbon Express, Nijora, etc.
- Traditional wood arrows (Cedar, Pine, Birch, Fir)

## Troubleshooting

### Migration Status Check Fails

```bash
# Check container logs
docker logs <container-name>

# Manually copy files and test
./docker-migration-runner.sh status
```

### Container Not Found

```bash
# List running containers
docker ps

# Start containers if needed
./start-unified.sh ssl yourdomain.com
```

### Database Permission Errors

```bash
# Check database files in container
docker exec <container> ls -la /app/databases/

# Verify database integrity
docker exec <container> sqlite3 /app/databases/arrow_database.db "PRAGMA integrity_check"
```

### API Still Returns 500 Errors

1. **Check migration completion:**
   ```bash
   ./docker-migration-runner.sh status
   ```

2. **Verify spine chart table exists:**
   ```bash
   docker exec <container> sqlite3 /app/databases/arrow_database.db ".tables" | grep spine
   ```

3. **Restart API service:**
   ```bash
   docker restart <container-name>
   ```

## Future Deployments

After the initial setup, future deployments with database changes will automatically run migrations:

```bash
# Standard deployment process
git pull
./start-unified.sh ssl yourdomain.com
# Migrations run automatically during startup
```

The robust migration system ensures consistent database state across all future deployments.

## Success Verification

✅ **Migration system working:** `./docker-migration-runner.sh status` succeeds  
✅ **Spine charts imported:** 21 charts in `manufacturer_spine_charts_enhanced` table  
✅ **API functional:** `/api/spine-charts` returns data instead of 500 error  
✅ **Frontend working:** Spine chart management page displays charts  
✅ **Production ready:** Automatic migrations on deployment restart  

Your spine chart system should now be fully functional in production!