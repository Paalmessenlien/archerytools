# Legacy Startup Scripts Archive

This directory contains legacy startup, deployment, and Docker management scripts that have been superseded by the unified `start-unified.sh` script.

## 🚨 DEPRECATED - USE `./start-unified.sh` INSTEAD

**All scripts in this directory are DEPRECATED and should not be used in production or development.**

**Use the unified startup script instead:**
```bash
# For development
./start-unified.sh dev start
./start-unified.sh dev stop

# For production testing
./start-unified.sh production start
./start-unified.sh production stop

# For SSL production
./start-unified.sh ssl yourdomain.com

# Get help
./start-unified.sh --help
```

## 📁 Archived Scripts

### Legacy Startup Scripts
- `start-docker-dev.sh.backup_*` - Old Docker development startup scripts
- `start-hybrid-dev.sh.backup_*` - Old hybrid development environment scripts
- `start-local-dev.sh.backup_*` - Old local development startup scripts  
- `start-unified.sh.backup_*` - Backup copies of start-unified.sh

### Docker Management Scripts
- `debug-docker-setup.sh` - Docker debugging utility
- `docker-backup-userdata.sh` - Legacy user data backup script
- `docker-migration-runner.sh` - Legacy migration runner (replaced by comprehensive-migration-runner.sh)
- `docker-production-setup.sh` - Legacy production setup script
- `nuclear-docker-reset.sh` - Aggressive Docker cleanup script
- `prepare-docker-data.sh` - Legacy data preparation script

### Fix and Production Scripts
- `fix-container-issues.sh` - Container issue resolution
- `fix-docker-config-error.sh` - Docker configuration fixes
- `fix-docker-issue.sh` - General Docker issue fixes
- `fix-docker-permissions.sh` - Docker permission fixes
- `fix-production-docker-conservative.sh` - Conservative production fixes
- `fix-production-docker-error.sh` - Production Docker error fixes
- `fix-production-unified.sh` - Legacy production unified fixes
- `fix-production-database.sh` - Legacy production database fixes
- `fix-production-git.sh` - Production Git fixes
- `production-database-fix.sh` - Production database issue fixes
- `quick-docker-spine-fix.sh` - Quick spine data fixes
- `quick-production-fix.sh` - Quick production fixes
- `revert-production-fix.sh` - Production fix reversal

## 🔄 Migration Path

If you were using any of these scripts, here's how to migrate:

### Old Development Workflow:
```bash
# OLD (don't use)
./start-hybrid-dev.sh start
./start-docker-dev.sh start
./start-local-dev.sh start
```

### New Unified Workflow:
```bash
# NEW (recommended)
./start-unified.sh dev start          # Local development
./start-unified.sh                    # Docker development
./start-unified.sh dev stop           # Stop development
```

### Old Production Workflow:
```bash
# OLD (don't use)
./docker-production-setup.sh
./fix-production-unified.sh
```

### New Unified Workflow:
```bash
# NEW (recommended)
./start-unified.sh production start   # Production testing
./start-unified.sh ssl yourdomain.com # Production SSL
./start-unified.sh production stop    # Stop production
```

## 📚 Documentation

For current documentation, see:
- **Main Documentation**: `/docs/DEVELOPMENT_GUIDE.md`
- **Current Help**: `./start-unified.sh --help`
- **Database Info**: `/docs/DATABASE_SCHEMA.md`
- **API Reference**: `/docs/API_ENDPOINTS.md`

## ⚠️ Important Notes

1. **Do NOT use these archived scripts** - they may contain outdated configurations
2. **Database paths may be incorrect** - these scripts use old database architecture
3. **Missing security updates** - unified script includes latest security features
4. **No migration support** - archived scripts don't include latest migration system
5. **Deprecated environment variables** - may use old environment variable names

## 🗑️ Cleanup

These scripts can be safely deleted in the future. They are kept for reference only.

**Archive Date**: August 19, 2025
**Superseded By**: `start-unified.sh` with comprehensive help system
**Migration System**: Unified database architecture with migration 033