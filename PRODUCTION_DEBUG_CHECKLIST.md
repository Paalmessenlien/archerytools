# Production Debug Checklist

## Issue Resolution Summary (August 12, 2025)
- **Problem**: ✅ RESOLVED - No spine charts available in production
- **Root Cause**: Production API container stopped 6 days ago (Exit code 137 - out of memory)
- **Solution Applied**: 
  - ✅ Containers restarted and running healthy
  - ✅ Spine data imported successfully (21 charts)
  - ✅ Added 2GB swap file to prevent future OOM kills
  - ✅ System fully operational
- **Key Learning**: No swap space was the primary cause of container deaths

## Container Status Diagnosis

### 1. Check Container Status
```bash
# Check all containers
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

# Expected issues:
# - arrowtuner-api: Exited (137) - MAIN PROBLEM
# - arrowtuner-frontend: Exited (0) 
# - arrowtuner-nginx: Restarting - trying to connect to dead API
```

### 2. Check Container Logs
```bash
# Check why API container died
docker logs arrowtuner-api --tail=50

# Check nginx restart loop
docker logs arrowtuner-nginx --tail=20

# Look for:
# - Out of memory errors
# - Database connection issues
# - Port binding problems
```

### 3. Check System Resources
```bash
# Check memory usage
free -h

# Check disk space
df -h

# Check if swap is enabled
swapon --show
```

## Migration System Status

### 4. Verify Migration Files
```bash
# Check migration files are present
ls -la arrow_scraper/run_migrations.py
ls -la arrow_scraper/migrations/
ls -la docker-migration-runner.sh

# Check spine data files
ls -la arrow_scraper/spinecalculatordata/
ls -la arrow_scraper/data/processed/
```

### 5. Check Database State (if API container runs)
```bash
# If API container is running:
docker exec arrowtuner-api sqlite3 /app/databases/arrow_database.db "SELECT COUNT(*) FROM manufacturer_spine_charts_enhanced" 2>/dev/null || echo "API container not accessible"

# Check migration table
docker exec arrowtuner-api sqlite3 /app/databases/arrow_database.db "SELECT version, applied_at FROM database_migrations ORDER BY applied_at" 2>/dev/null || echo "Cannot check migrations"
```

## Recovery Options

### Option 1: Full System Restart (Recommended)
```bash
# Stop all containers
docker-compose down

# Clean up any stuck containers
docker system prune -f

# Restart production with automatic migrations
./start-unified.sh ssl archerytool.online

# Wait for containers to start (2-3 minutes)
docker ps

# Test spine chart API
curl https://archerytool.online/api/spine-charts
```

### Option 2: Manual Container Recovery
```bash
# Start containers manually
docker-compose up -d

# Wait for containers to stabilize
sleep 30

# Check container health
docker ps

# Run migrations manually
./docker-migration-runner.sh migrate

# Verify spine charts
curl https://archerytool.online/api/spine-charts
```

### Option 3: Emergency Database Fix
If containers won't start, directly import spine data:
```bash
# Copy spine data to host
cp arrow_scraper/spinecalculatordata/spine_charts.json ./

# Manual database update (last resort)
# This requires API container to be running minimally
```

## System Health Checks

### 6. Verify Production Services
```bash
# Check API health
curl https://archerytool.online/api/health

# Check frontend access
curl -I https://archerytool.online

# Check spine chart endpoint specifically
curl https://archerytool.online/api/spine-charts

# Should return JSON with spine chart data, not 500 error
```

### 7. Memory and Resource Optimization
```bash
# If memory issues caused container deaths:

# Check current memory usage
docker stats --no-stream

# Add swap if needed (if root)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile  
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## Expected Success State

### 8. Verify Complete Fix
After recovery, verify:

```bash
# 1. All containers running
docker ps --format "table {{.Names}}\t{{.Status}}"

# 2. Migrations completed
./docker-migration-runner.sh status

# 3. Spine charts imported (should return 21)
docker exec arrowtuner-api sqlite3 /app/databases/arrow_database.db "SELECT COUNT(*) FROM manufacturer_spine_charts_enhanced"

# 4. API working
curl https://archerytool.online/api/spine-charts | head -50

# 5. Frontend accessible
curl -I https://archerytool.online
```

## Common Issues & Solutions

### Issue: Container Out of Memory (Exit 137)
**Solution**: Add swap space or increase server memory
```bash
# Quick swap addition
sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Issue: Port Already in Use
**Solution**: Kill processes using ports 80/443
```bash
sudo lsof -i :80
sudo lsof -i :443
# Kill any conflicting processes
```

### Issue: Database Locked
**Solution**: Restart API container
```bash
docker restart arrowtuner-api
```

### Issue: Nginx Can't Connect to API
**Solution**: Ensure API container starts first
```bash
docker-compose down
docker-compose up -d db-init  # Start database init first
sleep 10
docker-compose up -d api      # Start API second
sleep 10  
docker-compose up -d frontend nginx  # Start frontend services last
```

## Migration Debug Commands

### 9. Debug Migration System
```bash
# Test migration runner without running migrations
./docker-migration-runner.sh status

# Run migration with verbose output
docker exec arrowtuner-api python3 run_migrations.py --status-only

# Check individual migration files
docker exec arrowtuner-api ls -la /app/migrations/

# Test spine data import manually
docker exec arrowtuner-api python3 -c "
from spine_calculator_data_importer import SpineCalculatorDataImporter
importer = SpineCalculatorDataImporter('/app/databases/arrow_database.db')
try:
    importer.import_all_data()
    print('✅ Spine import successful')
except Exception as e:
    print(f'❌ Spine import failed: {e}')
"
```

## Final Verification Commands

### 10. Complete System Test
```bash
# Full system verification
echo "=== Container Status ==="
docker ps

echo "=== Migration Status ==="
./docker-migration-runner.sh status

echo "=== Spine Chart Count ==="
docker exec arrowtuner-api sqlite3 /app/databases/arrow_database.db "SELECT COUNT(*) FROM manufacturer_spine_charts_enhanced" 2>/dev/null || echo "Database not accessible"

echo "=== API Health Check ==="
curl -f https://archerytool.online/api/health

echo "=== Spine Chart API Test ==="
curl -f https://archerytool.online/api/spine-charts | head -100

echo "=== Frontend Access Test ==="
curl -I https://archerytool.online
```

## Success Criteria

✅ **All containers running** (docker ps shows all healthy)  
✅ **API accessible** (curl health endpoint succeeds)  
✅ **21 spine charts in database** (SQL count query returns 21)  
✅ **Spine chart API working** (/api/spine-charts returns data, not 500)  
✅ **Frontend loads** (website accessible)  
✅ **No restart loops** (containers stay running)

## Next Steps After Fix

1. **Monitor container stability** for 24 hours
2. **Set up automatic restart policies** if not already configured
3. **Consider memory/resource upgrades** if Exit 137 recurs
4. **Set up monitoring alerts** for container failures

## Emergency Contact

If production is completely broken and needs immediate recovery:
1. **Start basic service**: `docker-compose up -d api frontend nginx`
2. **Skip migrations temporarily**: Comment out migration calls in startup scripts
3. **Restore from backup**: Use backup/restore scripts if available
4. **Contact developer**: Share this checklist status and logs

---

## RESOLUTION LOG (August 12, 2025)

### What Actually Worked:
1. **Containers were already restarted** - System was running but spine data wasn't imported
2. **Manual spine data import**: `./docker-migration-runner.sh migrate` successfully imported 21 spine charts
3. **Added swap space**: `sudo fallocate -l 2G /swapfile && sudo swapon /swapfile` prevented future OOM
4. **Made swap permanent**: Added `/swapfile none swap sw 0 0` to `/etc/fstab`

### Final Status:
- ✅ All containers running healthy
- ✅ 21 spine charts imported successfully  
- ✅ API health check passing (`https://archerytool.online/api/health`)
- ✅ Frontend accessible (`https://archerytool.online`)
- ✅ 2GB swap active to prevent future memory issues

### Key Insight:
The spine chart endpoints are **admin-only** (`/api/admin/spine-charts`) - they require authentication and are not publicly accessible. The spine data is properly integrated and available through the admin interface.

---

*This checklist addressed the specific issue where production containers stopped running due to memory pressure, preventing the spine chart migration system from working properly. Issue resolved August 12, 2025.*