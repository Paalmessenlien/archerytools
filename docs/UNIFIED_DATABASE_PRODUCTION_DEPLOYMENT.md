# Unified Database Production Deployment Guide

Complete guide for deploying and managing the unified database architecture in production environments (August 2025).

## Overview

The unified database architecture represents a significant improvement from the legacy dual-database system, consolidating all data into a single `arrow_database.db` file for improved performance, simplified management, and enhanced reliability.

## Key Changes from Legacy System

### Before: Dual Database Architecture
```
├── arrow_database.db     # Arrow specifications, spine data, components
└── user_data.db          # User accounts, bow setups, sessions
```

### After: Unified Database Architecture (August 2025)
```
└── arrow_database.db     # ALL data: arrows, users, setups, sessions, components
```

### Benefits of Unified Architecture

**Performance Improvements:**
- **Simplified Queries**: No cross-database joins or complex data relationships
- **Reduced File I/O**: Single database file reduces filesystem overhead
- **Better Caching**: SQLite can optimize caching for single database more effectively
- **Faster Backups**: Single file backup and restore operations

**Management Simplification:**
- **Single Point of Truth**: All data in one location eliminates synchronization issues
- **Simplified Backup**: One database file to backup instead of coordinating multiple files
- **Easier Migration**: Schema changes only need to be applied to one database
- **Reduced Complexity**: Eliminates dual-database configuration and path management

---

## Production Deployment Process

### 1. Automatic Migration During Deployment

**Migration 023: Database Consolidation** runs automatically during startup:

```bash
# During startup sequence in start-unified.sh or Docker startup
echo "🔄 Checking database consolidation status..."
if ! sqlite3 /app/databases/arrow_database.db ".schema users" >/dev/null 2>&1; then
    echo "📋 Running database consolidation migration..."
    python3 /app/arrow_scraper/database_migration_manager.py --migrate-to-unified
fi
```

**Automatic Consolidation Process:**
1. **Detection**: Checks if user tables exist in arrow_database.db
2. **Backup**: Creates automatic backup before consolidation
3. **Data Migration**: Transfers all user data from user_data.db to arrow_database.db
4. **Table Creation**: Creates user tables (users, bow_setups, guide_sessions, etc.)
5. **Data Validation**: Verifies all data transferred successfully
6. **Cleanup**: Marks migration as complete in schema_migrations table

### 2. Production Environment Variables

**Required Environment Variables:**
```bash
# Database paths for unified architecture
ARROW_DATABASE_PATH=/app/databases/arrow_database.db
USER_DATABASE_PATH=/app/databases/arrow_database.db

# Backup and maintenance
BACKUP_RETENTION_DAYS=30
DATABASE_MAINTENANCE_SCHEDULE=weekly
```

**Docker Compose Configuration:**
```yaml
version: '3.8'
services:
  api:
    environment:
      - ARROW_DATABASE_PATH=/app/databases/arrow_database.db
      - USER_DATABASE_PATH=/app/databases/arrow_database.db
    volumes:
      # Unified database volume (replaces separate arrow/user volumes)
      - arrowtuner-databases:/app/databases/
      - arrowtuner-logs:/app/logs/

volumes:
  # Consolidated from arrowtuner-arrowdata + arrowtuner-userdata
  arrowtuner-databases:
    driver: local
  arrowtuner-logs:
    driver: local
```

---

## Deployment Scripts & Tools

### 1. Enhanced Startup Scripts

**Unified Startup Detection:**
```bash
# start-unified.sh enhancement for database consolidation
check_database_architecture() {
    local db_path="/app/databases/arrow_database.db"
    
    if [ -f "$db_path" ]; then
        # Check if unified (contains user tables)
        if docker exec arrowtuner-api sqlite3 "$db_path" ".schema users" >/dev/null 2>&1; then
            echo "✅ Unified database architecture detected"
            return 0
        else
            echo "🔄 Legacy database detected - consolidation required"
            return 1
        fi
    else
        echo "❌ Database not found at $db_path"
        return 2
    fi
}
```

### 2. Production Diagnostic Tools

**Robust Production Diagnostic Script** (`robust-diagnose-production.py`):
```python
def check_database_architecture():
    """Enhanced architecture detection for production environments"""
    
    # Check for unified architecture
    user_tables = ['users', 'bow_setups', 'guide_sessions', 'backup_metadata']
    arrow_tables = ['arrows', 'spine_specifications', 'manufacturers']
    
    user_tables_found = 0
    arrow_tables_found = 0
    
    for table in user_tables:
        if table_exists(cursor, table):
            user_tables_found += 1
    
    for table in arrow_tables:
        if table_exists(cursor, table):
            arrow_tables_found += 1
    
    if user_tables_found >= 3 and arrow_tables_found >= 2:
        return "UNIFIED"
    elif arrow_tables_found >= 2 and user_tables_found == 0:
        return "SEPARATE" 
    else:
        return "INCOMPLETE"
```

**Production Schema Fix Script** (`robust-fix-production.py`):
- **Automatic Backup**: Creates timestamped backup before any changes
- **Migration Table Repair**: Handles corrupted schema_migrations tables
- **Consolidation Migration**: Applies missing database consolidation
- **Column Addition**: Adds missing columns to existing tables
- **Verification**: Validates successful consolidation

### 3. Health Monitoring Integration

**Enhanced Database Health Checker:**
```python
class DatabaseHealthChecker:
    def check_unified_database(self):
        """Check if database is properly consolidated"""
        
        report = {
            'is_unified_database': False,
            'database_architecture': 'unknown',
            'user_table_count': 0,
            'arrow_table_count': 0,
            'consolidation_status': 'unknown'
        }
        
        # Detect architecture
        user_tables_found = self._count_user_tables()
        arrow_tables_found = self._count_arrow_tables()
        
        if user_tables_found >= 3 and arrow_tables_found >= 2:
            report['is_unified_database'] = True
            report['database_architecture'] = 'unified'
            report['consolidation_status'] = 'completed'
        elif arrow_tables_found >= 2 and user_tables_found == 0:
            report['database_architecture'] = 'separate'
            report['consolidation_status'] = 'pending'
        else:
            report['database_architecture'] = 'incomplete'
            report['consolidation_status'] = 'incomplete'
        
        return report
```

---

## Migration & Troubleshooting

### Common Production Issues

**1. Schema Verification Errors (27 missing columns)**

**Problem**: Production showing missing columns after deployment
```
❌ Missing columns detected:
   users.updated_at, users.last_login, users.picture
   bow_setups.created_at, bow_setups.updated_at
   manufacturers.website, manufacturers.established
```

**Solution**: Run consolidation migration
```bash
# Automated fix
docker exec arrowtuner-api python3 /app/robust-fix-production.py

# Manual verification
docker exec arrowtuner-api python3 /app/robust-diagnose-production.py
```

**2. Migration Status API 500 Errors**

**Problem**: Admin panel migration status returning "no such column: version"
```
❌ Internal Server Error - Migration status API failure
```

**Solution**: Enhanced migration manager with table structure detection
```python
def get_migration_status(self):
    """Handle different migration table schemas"""
    try:
        # Check table structure first
        cursor.execute('PRAGMA table_info(schema_migrations)')
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'version' in columns:
            return self._get_status_with_version_column()
        else:
            return self._recreate_migration_table()
    except sqlite3.OperationalError:
        return self._create_migration_table()
```

**3. Production Database Path Issues**

**Problem**: API container cannot find database files
```
❌ Database not found: /app/databases/arrow_database.db
```

**Solution**: Environment variable validation and path resolution
```python
class DatabasePathResolver:
    def resolve_database_path(self):
        """Resolve database path for different environments"""
        
        # Priority order for path resolution
        paths = [
            os.getenv('ARROW_DATABASE_PATH'),  # Explicit environment variable
            '/app/databases/arrow_database.db',  # Docker production
            './databases/arrow_database.db',     # Local development
            './arrow_database.db'                # Legacy fallback
        ]
        
        for path in paths:
            if path and os.path.exists(path):
                return path
        
        raise DatabaseError("No valid database path found")
```

### Migration Recovery Procedures

**Complete Production Recovery Process:**

1. **Stop Services**
   ```bash
   docker stop arrowtuner-api arrowtuner-frontend
   ```

2. **Backup Current State**
   ```bash
   docker run --rm -v arrowtuner-databases:/data -v $(pwd):/backup alpine \
     tar czf /backup/emergency-backup-$(date +%Y%m%d_%H%M%S).tar.gz /data
   ```

3. **Run Diagnostic**
   ```bash
   docker exec arrowtuner-api python3 /app/robust-diagnose-production.py > diagnosis.log
   ```

4. **Apply Fix**
   ```bash
   docker exec arrowtuner-api python3 /app/robust-fix-production.py
   ```

5. **Restart Services**
   ```bash
   docker restart arrowtuner-api
   sleep 10
   docker restart arrowtuner-frontend
   ```

6. **Verify Fix**
   ```bash
   curl -s http://localhost:5000/api/health | jq .
   curl -s http://localhost:5000/api/admin/database/health | jq .
   ```

---

## Performance Optimization

### Database Maintenance Schedule

**Automated Maintenance** (via admin panel):
- **Daily**: Health monitoring and performance checks
- **Weekly**: VACUUM operations for space reclamation
- **Monthly**: Complete REINDEX for optimal query performance
- **On-demand**: Post-migration verification and optimization

**Maintenance Commands:**
```bash
# Weekly VACUUM (automated via admin panel)
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:5000/api/admin/database/vacuum

# Monthly optimization (automated via admin panel)
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:5000/api/admin/database/optimize
```

### Performance Monitoring

**Key Performance Metrics:**
- **Database Size**: Monitor growth trends and storage usage
- **Query Performance**: Track average query response times
- **Index Effectiveness**: Monitor index usage and optimization
- **Health Score**: Maintain 90+ health score for optimal performance

**Performance Alerts:**
- Health score below 70: Investigate performance issues
- Database size growth >50% in 30 days: Review data retention
- Query response time >500ms: Consider index optimization
- Failed health checks: Immediate investigation required

---

## Backup & Recovery

### Unified Database Backup

**Simplified Backup Process:**
```bash
# Single database backup (replaces dual-database backup)
docker exec arrowtuner-api python3 /app/backup_manager.py backup \
  --name "production_unified_$(date +%Y%m%d)" \
  --type full
```

**CDN Backup Integration:**
- **Bunny CDN**: Primary backup storage with global distribution
- **Cloudinary**: Secondary backup provider with transformation capabilities
- **AWS S3**: Enterprise backup option with long-term retention
- **Local Storage**: Emergency backup for immediate recovery

### Recovery Procedures

**Complete System Recovery:**
1. **Download Backup**: Retrieve latest backup from CDN storage
2. **Stop Services**: Ensure no database connections during restore
3. **Replace Database**: Restore unified database file
4. **Restart Services**: Bring system back online
5. **Verify Restoration**: Confirm all data and functionality restored

**Selective Recovery:**
- **User Data Only**: Restore user tables while preserving arrow data
- **Arrow Data Only**: Update arrow specifications while preserving user accounts
- **Configuration Only**: Restore system settings and admin configurations

---

## Security Considerations

### Database Security

**Access Control:**
- **Admin Authentication**: JWT token validation for all admin operations
- **Google OAuth**: Secure authentication flow with identity verification
- **Permission Verification**: Double-checking admin privileges for sensitive operations

**Data Protection:**
- **Backup Encryption**: Secure transmission and storage of backup files
- **Transaction Safety**: All operations wrapped in database transactions
- **Audit Trail**: Complete logging of admin operations and database changes

### Production Security

**Container Security:**
- **Non-root User**: Database operations run as non-privileged user
- **Volume Permissions**: Proper file permissions for database files
- **Network Isolation**: Database access only through defined API endpoints

**Monitoring & Alerting:**
- **Failed Authentication**: Monitor and alert on authentication failures
- **Unusual Activity**: Detect abnormal database access patterns
- **Performance Degradation**: Alert on health score drops or performance issues

---

This unified database production deployment guide provides comprehensive coverage of deployment, migration, troubleshooting, and maintenance procedures for the enhanced database architecture implemented in August 2025.