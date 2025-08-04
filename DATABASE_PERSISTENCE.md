# Database Persistence & Backup System

This document describes the comprehensive database persistence and backup system implemented for the ArrowTuner platform.

## Overview

The ArrowTuner system uses two separate SQLite databases:
- **Arrow Database** (`arrow_database.db`) - Arrow specifications, spine data, and component information
- **User Database** (`user_data.db`) - User accounts, bow setups, guide sessions, and user-specific data

Both databases are now fully persistent across Docker container restarts and include comprehensive backup/restore capabilities.

## Database Persistence Architecture

### Docker Volume Configuration

The system uses Docker volumes to ensure data persistence:

```yaml
volumes:
  arrowtuner-userdata:/app/user_data    # User database persistence
  arrowtuner-arrowdata:/app/arrow_data  # Arrow database persistence
  arrowtuner-logs:/app/logs             # Log file persistence
```

### Database Path Resolution

Both database classes (`ArrowDatabase` and `UserDatabase`) prioritize environment variables for path resolution:

1. **Environment Variable Check**: `ARROW_DATABASE_PATH` and `USER_DATABASE_PATH`
2. **Docker Volume Paths**: `/app/arrow_data/` and `/app/user_data/`
3. **Fallback Paths**: Development and local paths

### Startup Process

The enhanced startup script (`start-api-robust.sh`) handles database initialization:

1. **Environment Detection**: Determines Docker vs local environment
2. **Volume Setup**: Creates and configures database directories
3. **Database Verification**: Checks database integrity
4. **Auto-Creation**: Creates empty databases if missing (production-safe)
5. **Import Control**: Skips automatic imports in production environments

## Production Import Control

### Security Enhancement

**Problem Solved**: Automatic database imports were running in production, potentially overwriting production data.

**Solution**: Production imports are now **disabled by default**:

```bash
# Production behavior (FLASK_ENV=production)
📥 Skipping database import in production environment
    Use FORCE_DATABASE_IMPORT=true to enable import in production
    Or use backup/restore scripts for production data management
```

### Manual Override

To force imports in production (not recommended):
```bash
FORCE_DATABASE_IMPORT=true docker-compose up -d
```

**Recommended**: Use backup/restore scripts for production data management.

## Comprehensive Backup System

### Backup Manager (`arrow_scraper/backup_manager.py`)

Professional-grade backup system with the following features:

#### Core Functionality
- **SQLite Backup API**: Uses SQLite's native backup mechanism for consistency
- **Compressed Archives**: Creates tar.gz files with metadata
- **Selective Backups**: Arrow-only, user-only, or full backups
- **Integrity Verification**: Validates backup files before operations
- **Metadata Tracking**: Includes database statistics and creation info

#### Backup Features
```python
# Full backup
backup_manager.create_backup(backup_name="production_backup")

# Selective backup
backup_manager.create_backup(include_arrow_db=True, include_user_db=False)

# With metadata
{
  "backup_name": "production_backup",
  "created_at": "2025-08-04T16:38:29.591353",
  "version": "1.0.0",
  "includes": {"arrow_database": true, "user_database": true},
  "arrow_db_stats": {"table_count": 4, "file_size_mb": 2.1},
  "user_db_stats": {"table_count": 7, "file_size_mb": 0.5}
}
```

### User-Friendly Scripts

#### Backup Creation (`backup-databases.sh`)

```bash
# Full backup with auto-generated name
./backup-databases.sh

# Custom backup name
./backup-databases.sh --name production_backup_2025_08_04

# User database only
./backup-databases.sh --user-db-only

# Full backup with cleanup (keep 5 most recent)
./backup-databases.sh --cleanup --keep 5

# Arrow database only
./backup-databases.sh --arrow-db-only
```

**Features:**
- Auto-generated timestamps in backup names
- Cleanup of old backups with configurable retention
- Color-coded output for easy status tracking
- Works both inside Docker containers and on host system

#### Backup Restoration (`restore-databases.sh`)

```bash
# List available backups
./restore-databases.sh --list

# Restore full backup (with confirmation)
./restore-databases.sh --file backup.tar.gz

# Restore user database only
./restore-databases.sh --file backup.tar.gz --user-db-only

# Force restore without confirmation
./restore-databases.sh --file backup.tar.gz --force

# Verify backup integrity
./restore-databases.sh --verify --file backup.tar.gz
```

**Safety Features:**
- Pre-restore database backups (automatic safety net)
- Confirmation prompts unless `--force` is used
- Backup verification before restoration
- Detailed operation logging

### Backup Directory Structure

```
/app/backups/
├── archerytools_backup_20250804_163829.tar.gz
├── production_backup.tar.gz
└── user_data_only_20250804_140000.tar.gz

# Each backup contains:
backup.tar.gz/
├── backup_metadata.json    # Backup info and statistics
├── arrow_database.db      # Arrow data (if included)
└── user_data.db          # User data (if included)
```

## Database Management Commands

### Direct Backup Manager Usage

```bash
# Inside Docker container
docker exec arrowtuner-api-enhanced python3 /app/backup_manager.py backup --name test_backup
docker exec arrowtuner-api-enhanced python3 /app/backup_manager.py list
docker exec arrowtuner-api-enhanced python3 /app/backup_manager.py restore backup.tar.gz
docker exec arrowtuner-api-enhanced python3 /app/backup_manager.py verify backup.tar.gz
docker exec arrowtuner-api-enhanced python3 /app/backup_manager.py cleanup --keep 10
```

### Host System Usage

```bash
# From project root
./backup-databases.sh --name weekly_backup
./restore-databases.sh --list
./restore-databases.sh --file weekly_backup.tar.gz
```

## Development & Testing

### Demo Data Population

For development and testing environments:

```bash
# Populate with demo arrow data
./populate-demo-data.sh

# Contents include:
# - Easton Archery arrows (Axis 5mm, Carbon One)
# - Gold Tip arrows (Hunter XT, Velocity)  
# - Victory Archery arrows (VAP TKO, RIP XV)
# - Carbon Express arrows (Maxima RED, PileDriver)
```

### Persistence Testing

```bash
# Test database persistence
python3 test-db-persistence.py

# Expected output:
✅ API is healthy
✅ Database accessible - Found X arrows
✅ User database is accessible (401 = no auth, expected)
✅ Arrow database baseline: X arrows
🎉 Database persistence test completed successfully!
```

## Production Deployment

### Initial Setup

1. **Deploy System**: Use enhanced Docker configuration
   ```bash
   docker-compose -f docker-compose.enhanced-ssl.yml up -d --build
   ```

2. **Import Data**: Either restore from backup or import from JSON
   ```bash
   # Restore from backup (recommended)
   ./restore-databases.sh --file production_backup.tar.gz
   
   # OR force import from JSON (if needed)
   FORCE_DATABASE_IMPORT=true docker-compose restart api
   ```

3. **Verify Persistence**: Test that data survives container restarts
   ```bash
   python3 test-db-persistence.py
   docker-compose restart api
   python3 test-db-persistence.py
   ```

### Ongoing Maintenance

#### Regular Backups
```bash
# Daily backup with cleanup
./backup-databases.sh --name daily_$(date +%Y%m%d) --cleanup --keep 7

# Weekly full backup
./backup-databases.sh --name weekly_$(date +%Y%m%d) --cleanup --keep 4
```

#### Data Updates
```bash
# Update arrow data (development)
cd arrow_scraper && python main.py --update-all

# Deploy updated data to production
git add data/processed/ && git commit -m "Update arrow database"
git push

# On production server
git pull
FORCE_DATABASE_IMPORT=true docker-compose restart api
./backup-databases.sh --name post_update_$(date +%Y%m%d)
```

#### Disaster Recovery
```bash
# List available backups
./restore-databases.sh --list

# Restore from most recent backup
./restore-databases.sh --file latest_backup.tar.gz

# Verify restoration
python3 test-db-persistence.py
```

## Troubleshooting

### Common Issues

#### Database Not Found
```bash
# Check volume mounts
docker-compose -f docker-compose.enhanced-ssl.yml config

# Check container logs
docker logs arrowtuner-api-enhanced --tail 50

# Manually create database structure
docker exec arrowtuner-api-enhanced sqlite3 /app/arrow_data/arrow_database.db "CREATE TABLE IF NOT EXISTS arrows (id INTEGER PRIMARY KEY, manufacturer TEXT, model_name TEXT);"
```

#### Permission Issues
```bash
# Check directory permissions in container
docker exec arrowtuner-api-enhanced ls -la /app/

# Rebuild with proper permissions
docker-compose -f docker-compose.enhanced-ssl.yml up -d --build
```

#### Backup/Restore Issues
```bash
# Verify backup integrity
./restore-databases.sh --verify --file backup.tar.gz

# Check backup contents
docker exec arrowtuner-api-enhanced python3 /app/backup_manager.py list

# Manual backup verification
tar -tzf backup.tar.gz
```

### Log Analysis

#### Startup Logs
```bash
# Check database initialization
docker logs arrowtuner-api-enhanced | grep -E "(database|Database|📊|👤|🔧)"

# Check import status
docker logs arrowtuner-api-enhanced | grep -E "(import|Import|📥)"
```

#### Database Path Resolution
```bash
# Check path resolution
docker logs arrowtuner-api-enhanced | grep -E "(Using.*database|Resolved.*database|ARROW_DATABASE_PATH|USER_DATABASE_PATH)"
```

## Security Considerations

### Production Safety
- ✅ No automatic imports in production environments
- ✅ Confirmation prompts for destructive operations
- ✅ Pre-restore backups created automatically
- ✅ Backup verification before restoration
- ✅ Environment variable isolation

### Data Protection
- ✅ SQLite backup API ensures consistency
- ✅ Compressed archives reduce storage requirements
- ✅ Metadata tracking for audit trails
- ✅ Configurable backup retention policies
- ✅ Docker volume persistence across container lifecycles

## Future Enhancements

### Planned Features
- [ ] Automated backup scheduling with cron
- [ ] Remote backup storage (S3, Google Cloud)
- [ ] Database encryption at rest
- [ ] Backup deduplication
- [ ] Web-based backup management interface

### Performance Optimizations
- [ ] Incremental backup support
- [ ] Backup compression optimization
- [ ] Database vacuum automation
- [ ] Health monitoring dashboards

## Related Documentation

- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Docker deployment guide
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) - Production server setup
- [CLAUDE.md](CLAUDE.md) - Complete project documentation

---

**Status**: ✅ Production Ready  
**Last Updated**: August 4, 2025  
**Version**: 1.0.0