# Migration Quick Reference

## 🚀 Quick Start

### Check Current Status
```bash
cd arrow_scraper
python run_migrations.py --status-only
```

### Apply All Pending
```bash
python run_migrations.py
```

### Create New Migration
```bash
# 1. Find next number
ls migrations/ | grep -E '^[0-9]{3}_' | sort | tail -1

# 2. Create file: migrations/017_your_feature.py
# 3. Use template from MIGRATION_REFERENCE.md
# 4. Test: python migrations/017_your_feature.py
```

## 📋 All Current Migrations (001-016)

| # | Name | Database | Purpose |
|---|------|----------|---------|
| 001 | Spine Calculator Tables | Arrow | Mathematical foundation for spine calculations |
| 002 | User Database Schema | User | Core user accounts and bow setups |
| 003 | JSON Data Import | Arrow | Import scraped arrow data from JSON files |
| 004 | Bow Equipment Schema | Arrow | Equipment categories and field definitions |
| 005 | Unified Manufacturers | Arrow | Standardized manufacturer data |
| 006 | Bow Limb Manufacturers | Arrow | Recurve/traditional bow manufacturer support |
| 007 | User Bow Equipment Table | User | User-specific equipment assignments |
| 008 | Custom Equipment Schema | Arrow | Enhanced equipment field definitions (30+ fields) |
| 009 | User Custom Equipment Schema | User | User equipment table enhancements |
| 010 | Complete Equipment Categories | Arrow | 8 equipment categories (String, Sight, Rest, etc.) |
| 011 | Enhanced Manufacturer Workflow | Arrow | Smart manufacturer detection and linking |
| 012 | Fix Pending Manufacturers Schema | Arrow | Bug fixes for manufacturer workflow |
| **013** | **Equipment Change Logging** ⭐ | User | **Comprehensive change tracking for equipment** |
| **014** | **Arrow Change Logging** ⭐ | User | **Change tracking for arrow assignments** |
| **015** | **Remove UNIQUE Constraint** ⭐ | User | **Fix production compatibility issue** |
| **016** | **Equipment Soft Delete** ⭐ | User | **Non-destructive deletion with restore** |

*⭐ = Recent migrations (August 2025)*

## 🎯 Common Migration Patterns

### Add New Table
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS new_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_id) REFERENCES parent_table (id) ON DELETE CASCADE
    )
""")
```

### Add New Column
```python
# Check if column exists first
cursor.execute("PRAGMA table_info(existing_table)")
columns = [col[1] for col in cursor.fetchall()]

if 'new_column' not in columns:
    cursor.execute("ALTER TABLE existing_table ADD COLUMN new_column TEXT DEFAULT NULL")
```

### Add Index
```python
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_table_column 
    ON table_name (column_name)
""")
```

### Migrate Existing Data
```python
# Update existing records
cursor.execute("UPDATE users SET new_field = 'default_value' WHERE new_field IS NULL")

# Transform data
cursor.execute("""
    UPDATE equipment 
    SET specifications = json_object('old_field', old_field_value)
    WHERE specifications IS NULL
""")
```

## 🔧 Admin Panel Usage

1. Navigate to `/admin` in your browser
2. Go to **Maintenance** tab
3. **Migration Status** - View applied/pending migrations
4. **Run Migrations** - Apply pending migrations manually
5. **Migration History** - View execution logs

## 🏗️ Database Architecture

### Two Separate Databases:
- **Arrow Database** (`arrow_database.db`) - Arrow specs, equipment catalog, manufacturers
- **User Database** (`user_data.db`) - User accounts, bow setups, equipment assignments, change logs

### Migration Tracking:
```sql
-- Migration status stored in database_migrations table
CREATE TABLE database_migrations (
    id INTEGER PRIMARY KEY,
    version TEXT UNIQUE NOT NULL,
    applied BOOLEAN DEFAULT 0,
    applied_at TIMESTAMP,
    execution_time_ms INTEGER
);
```

## 🚨 Production Checklist

Before deploying migrations:
- ✅ Test in development environment
- ✅ Backup databases (`./backup-databases.sh`)
- ✅ Review migration SQL for performance impact
- ✅ Verify rollback procedure works
- ✅ Plan maintenance window if needed

## 🆘 Troubleshooting

### Migration Not Found
```bash
# Check file naming: must be XXX_name.py
ls migrations/
```

### Permission Errors
```bash
# Check database file permissions
ls -la databases/
# Docker: ls -la /app/databases/
```

### Dependency Issues
```bash
# Validate migration sequence
python -c "
from database_migration_manager import DatabaseMigrationManager
manager = DatabaseMigrationManager()
print(manager.validate_migration_sequence())
"
```

### View Migration Details
```bash
# Get specific migration info
python -c "
from database_migration_manager import DatabaseMigrationManager
manager = DatabaseMigrationManager()
migration = manager.get_migration_details('016')
print(migration)
"
```

## 📞 Need Help?

1. Check **MIGRATION_REFERENCE.md** for detailed documentation
2. Use **Admin Panel** → Maintenance tab for status
3. Test with `--dry-run` flag before applying
4. Always backup before major changes