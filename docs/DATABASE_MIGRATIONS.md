# Database Migrations System

This document provides comprehensive guidance on the database migration system used in the Archery Tools project, including how to create, apply, and manage database schema changes safely across different environments.

## Overview

The Archery Tools project uses a robust, versioned database migration system that ensures consistent database schema evolution across development, staging, and production environments. The system supports both arrow database (`arrow_database.db`) and user database (`user_data.db`) migrations with dependency management and rollback capabilities.

## Architecture

### Core Components

- **`DatabaseMigrationManager`** - Central migration orchestrator
- **`BaseMigration`** - Abstract base class for all migrations
- **Migration Files** - Individual migration implementations
- **Migration Table** - Tracks applied migrations and their status
- **Admin Interface** - Web-based migration management

### Database Targets

The system supports migrations for two separate databases:

1. **Arrow Database** (`arrow_database.db`)
   - Arrow specifications and spine data
   - Equipment catalog and categories
   - Manufacturer data and spine charts

2. **User Database** (`user_data.db`)
   - User accounts and authentication
   - Bow setups and configurations
   - Equipment assignments and tuning sessions

## Migration File Structure

### Directory Layout

```
arrow_scraper/
├── migrations/
│   ├── __init__.py
│   ├── 001_spine_calculator_tables.py
│   ├── 002_user_database_schema.py
│   ├── 003_json_data_import.py
│   ├── 004_bow_equipment_schema.py
│   ├── 005_unified_manufacturers.py
│   ├── 006_bow_limb_manufacturers.py
│   └── 007_user_bow_equipment_table.py
├── database_migration_manager.py
└── run_migrations.py
```

### Migration File Template

```python
#!/usr/bin/env python3
"""
Migration XXX: [Description]
[Detailed description of what this migration does]
"""

import sqlite3
from database_migration_manager import BaseMigration

class MigrationXXX[DescriptiveName](BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "XXX"  # Zero-padded 3-digit version
        self.description = "Brief description of migration"
        self.dependencies = ["XXX"]  # List of required migrations
        self.environments = ['all']  # ['all', 'development', 'production', 'docker']
        self.target_database = 'arrow'  # 'arrow' or 'user'
    
    def up(self, db_path: str, environment: str) -> bool:
        """Apply the migration"""
        try:
            # Migration implementation
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Your migration SQL here
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS new_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    -- columns here
                )
            """)
            
            conn.commit()
            conn.close()
            
            print("✅ Migration XXX applied successfully")
            return True
            
        except Exception as e:
            print(f"❌ Migration XXX failed: {e}")
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback the migration"""
        try:
            # Rollback implementation
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("DROP TABLE IF EXISTS new_table")
            
            conn.commit()
            conn.close()
            
            print("✅ Migration XXX rolled back successfully")
            return True
            
        except Exception as e:
            print(f"❌ Migration XXX rollback failed: {e}")
            return False

# Create the migration instance for discovery
migration = MigrationXXX[DescriptiveName]()
```

## Creating New Migrations

### Step 1: Determine Migration Number

Find the next available migration number:

```bash
cd arrow_scraper
ls migrations/ | grep -E '^[0-9]{3}_' | sort | tail -1
# Returns: 007_user_bow_equipment_table.py
# Next number: 008
```

### Step 2: Create Migration File

```bash
# Create new migration file
touch migrations/008_my_new_feature.py
```

### Step 3: Implement Migration Class

```python
#!/usr/bin/env python3
"""
Migration 008: Add feature X
Adds new functionality for feature X with proper schema changes
"""

import sqlite3
from database_migration_manager import BaseMigration

class Migration008MyNewFeature(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "008"
        self.description = "Add feature X schema"
        self.dependencies = ["007"]  # Depends on previous migration
        self.environments = ['all']
        self.target_database = 'arrow'  # or 'user'
    
    def up(self, db_path: str, environment: str) -> bool:
        """Apply the migration"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Add your schema changes here
            cursor.execute("""
                ALTER TABLE existing_table 
                ADD COLUMN new_column TEXT DEFAULT NULL
            """)
            
            # Create indexes if needed
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_existing_table_new_column 
                ON existing_table (new_column)
            """)
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully added feature X schema")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add feature X schema: {e}")
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback the migration"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # SQLite doesn't support DROP COLUMN, so we'd need to:
            # 1. Create new table without the column
            # 2. Copy data
            # 3. Drop old table
            # 4. Rename new table
            
            # For this example, we'll just drop the index
            cursor.execute("DROP INDEX IF EXISTS idx_existing_table_new_column")
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully rolled back feature X schema")
            return True
            
        except Exception as e:
            print(f"❌ Failed to rollback feature X schema: {e}")
            return False

# Create the migration instance for discovery
migration = Migration008MyNewFeature()
```

### Step 4: Test Migration

```bash
cd arrow_scraper
source venv/bin/activate

# Test migration discovery
python -c "
from database_migration_manager import DatabaseMigrationManager
manager = DatabaseMigrationManager('databases/arrow_database.db')
pending = manager.get_pending_migrations()
print(f'Pending migrations: {[m.version for m in pending]}')
"

# Test dry run
python -c "
from database_migration_manager import DatabaseMigrationManager
manager = DatabaseMigrationManager('databases/arrow_database.db')
pending = manager.get_pending_migrations()
migration_008 = next((m for m in pending if m.version == '008'), None)
if migration_008:
    success = manager.apply_migration(migration_008, dry_run=True)
    print(f'Dry run result: {success}')
"
```

## Running Migrations

### Command Line Interface

```bash
cd arrow_scraper
source venv/bin/activate

# Apply all pending migrations
python run_migrations.py

# Apply migrations for specific environment
python run_migrations.py --environment production

# Dry run (test without applying)
python run_migrations.py --dry-run

# Apply specific migration
python run_migrations.py --version 008

# Rollback last migration
python run_migrations.py --rollback

# Show migration status
python run_migrations.py --status
```

### Programmatic Usage

```python
from database_migration_manager import DatabaseMigrationManager

# Initialize migration manager
manager = DatabaseMigrationManager('databases/arrow_database.db')

# Get migration status
status = manager.get_migration_status()
print(f"Applied: {status['applied_count']}")
print(f"Pending: {status['pending_count']}")

# Apply pending migrations
pending = manager.get_pending_migrations()
for migration in pending:
    success = manager.apply_migration(migration)
    if not success:
        print(f"Migration {migration.version} failed")
        break

# Rollback specific migration
migration = manager.get_migration_details("008")
if migration:
    manager.rollback_migration(migration)
```

### Admin Panel Interface

Access the admin panel at `/admin` with admin privileges:

1. **Migration Status** - View applied and pending migrations
2. **Run Migrations** - Apply pending migrations with dry-run option
3. **Migration History** - View detailed migration execution history
4. **Rollback** - Rollback specific migrations (with caution)

## User Database Migrations

### Special Considerations

When creating migrations for the user database, follow these patterns:

```python
class Migration00XUserFeature(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "00X"
        self.description = "Add user feature"
        self.dependencies = ["002"]  # User database schema
        self.environments = ['all']
        self.target_database = 'user'  # Important!
    
    def up(self, db_path: str, environment: str) -> bool:
        """Apply migration to user database"""
        try:
            # Get user database path
            user_db_path = self._get_user_database_path(db_path)
            if not user_db_path:
                print("❌ Could not find user database")
                return False
            
            conn = sqlite3.connect(user_db_path)
            cursor = conn.cursor()
            
            # Your user database changes here
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_feature (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    feature_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ User migration failed: {e}")
            return False
    
    def _get_user_database_path(self, arrow_db_path: str) -> str:
        """Helper to find user database path"""
        try:
            from user_database import UserDatabase
            user_db = UserDatabase()
            return user_db.db_path
        except Exception as e:
            print(f"⚠️ Error finding user database: {e}")
            return None
```

## Migration Best Practices

### Schema Changes

1. **Always use `IF NOT EXISTS`** for table creation
2. **Add indexes for foreign keys** to improve performance
3. **Use proper foreign key constraints** with CASCADE options
4. **Default values** for new columns to handle existing data
5. **Test rollback procedures** before applying to production

### Data Migrations

```python
def up(self, db_path: str, environment: str) -> bool:
    """Migration with data transformation"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Add new column
        cursor.execute("ALTER TABLE users ADD COLUMN new_field TEXT DEFAULT NULL")
        
        # 2. Migrate existing data
        cursor.execute("UPDATE users SET new_field = 'default_value' WHERE new_field IS NULL")
        
        # 3. Add constraints if needed
        # Note: SQLite has limited ALTER TABLE support
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Data migration failed: {e}")
        return False
```

### Environment-Specific Migrations

```python
def up(self, db_path: str, environment: str) -> bool:
    """Environment-aware migration"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if environment == 'production':
            # Production-specific changes
            cursor.execute("CREATE INDEX idx_production ON table_name (column)")
        elif environment == 'development':
            # Development-specific changes
            cursor.execute("INSERT INTO test_data VALUES (?)", ("dev_data",))
        
        # Common changes for all environments
        cursor.execute("CREATE TABLE common_table (...)")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Environment migration failed: {e}")
        return False
```

## Migration Dependencies

### Dependency Declaration

```python
class Migration010Feature(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "010"
        self.description = "Advanced feature"
        self.dependencies = ["008", "009"]  # Requires both migrations
        self.environments = ['all']
```

### Dependency Validation

The migration system automatically:

1. **Validates dependencies** before applying migrations
2. **Sorts migrations** by dependency order
3. **Prevents circular dependencies**
4. **Fails fast** if dependencies are missing

## Error Handling

### Migration Failures

```python
def up(self, db_path: str, environment: str) -> bool:
    """Migration with proper error handling"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Your migration steps here
        cursor.execute("CREATE TABLE new_table (...)")
        cursor.execute("INSERT INTO new_table SELECT * FROM old_table")
        cursor.execute("DROP TABLE old_table")
        cursor.execute("ALTER TABLE new_table RENAME TO old_table")
        
        # Commit transaction
        cursor.execute("COMMIT")
        
        print("✅ Migration completed successfully")
        return True
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"❌ SQLite error: {e}")
        return False
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Migration error: {e}")
        return False
    finally:
        if conn:
            conn.close()
```

### Rollback Safety

```python
def down(self, db_path: str, environment: str) -> bool:
    """Safe rollback implementation"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if rollback is safe
        cursor.execute("SELECT COUNT(*) FROM table_name WHERE condition")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"⚠️ Warning: {count} records will be affected by rollback")
            # In production, you might want to prevent rollback
            # return False
        
        # Perform rollback
        cursor.execute("DROP TABLE IF EXISTS new_table")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        return False
```

## Testing Migrations

### Unit Testing

```python
import unittest
import tempfile
import sqlite3
from pathlib import Path
from migrations.008_my_new_feature import Migration008MyNewFeature

class TestMigration008(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.migration = Migration008MyNewFeature()
        
        # Set up initial database state
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE existing_table (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()
    
    def tearDown(self):
        Path(self.db_path).unlink()
    
    def test_migration_up(self):
        """Test migration application"""
        result = self.migration.up(self.db_path, 'development')
        self.assertTrue(result)
        
        # Verify changes
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(existing_table)")
        columns = [col[1] for col in cursor.fetchall()]
        self.assertIn('new_column', columns)
        conn.close()
    
    def test_migration_down(self):
        """Test migration rollback"""
        # Apply migration first
        self.migration.up(self.db_path, 'development')
        
        # Then test rollback
        result = self.migration.down(self.db_path, 'development')
        self.assertTrue(result)
        
        # Verify rollback
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA index_list(existing_table)")
        indexes = cursor.fetchall()
        self.assertEqual(len(indexes), 0)  # Index should be removed
        conn.close()

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```bash
# Test migration in isolated environment
cd arrow_scraper
source venv/bin/activate

# Create test database
cp databases/arrow_database.db test_database.db

# Test migration
python -c "
from database_migration_manager import DatabaseMigrationManager
manager = DatabaseMigrationManager('test_database.db')
pending = manager.get_pending_migrations()
for migration in pending:
    if migration.version == '008':
        success = manager.apply_migration(migration, dry_run=False)
        print(f'Migration 008 result: {success}')
        
        # Test rollback
        rollback_success = manager.rollback_migration(migration)
        print(f'Rollback result: {rollback_success}')
        break
"

# Clean up
rm test_database.db
```

## Production Deployment

### Pre-deployment Checklist

1. **Test migrations in staging** environment
2. **Backup databases** before applying migrations
3. **Verify rollback procedures** work correctly
4. **Check migration dependencies** are satisfied
5. **Review migration SQL** for performance impact
6. **Plan maintenance window** if needed

### Deployment Process

```bash
# 1. Backup databases
./backup-databases.sh --name pre_migration_backup

# 2. Apply migrations
cd arrow_scraper
source venv/bin/activate
python run_migrations.py --environment production

# 3. Verify migration success
python -c "
from database_migration_manager import DatabaseMigrationManager
manager = DatabaseMigrationManager('databases/arrow_database.db')
status = manager.get_migration_status()
print(f'Migration status: {status}')
"

# 4. Test application functionality
python test-equipment-functionality.py

# 5. Monitor logs for errors
tail -f logs/api.log
```

### Rollback Procedure

```bash
# If migration fails, rollback
cd arrow_scraper
source venv/bin/activate

# Rollback specific migration
python run_migrations.py --rollback --version 008

# Or restore from backup
./restore-databases.sh --file pre_migration_backup.tar.gz
```

## Migration Monitoring

### Admin Panel Monitoring

The admin panel provides real-time migration monitoring:

1. **Migration Status Dashboard** - Shows applied/pending counts
2. **Migration History** - Detailed execution logs
3. **Performance Metrics** - Migration execution times
4. **Error Reporting** - Failed migration details

### API Endpoints

```bash
# Get migration status
curl http://localhost:5000/api/admin/migrations/status

# Get migration history
curl http://localhost:5000/api/admin/migrations/history

# Run pending migrations
curl -X POST http://localhost:5000/api/admin/migrations/run \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false}'
```

## Troubleshooting

### Common Issues

**Migration Not Discovered:**
```bash
# Check migration file naming
ls migrations/ | grep 008
# Should be: 008_migration_name.py

# Check class naming
grep "class Migration008" migrations/008_*.py
# Should match file number
```

**Dependency Errors:**
```bash
# Check dependencies exist
python -c "
from database_migration_manager import DatabaseMigrationManager
manager = DatabaseMigrationManager('databases/arrow_database.db')
result = manager.validate_migration_sequence()
print(result)
"
```

**User Database Path Issues:**
```python
# Debug user database path resolution
from user_database import UserDatabase
user_db = UserDatabase()
print(f"User DB path: {user_db.db_path}")
```

**Permission Errors:**
```bash
# Check database file permissions
ls -la databases/
# Should be writable by application user

# Check directory permissions
ls -la /app/databases/  # Docker deployment
```

### Debugging Migration Execution

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

from database_migration_manager import DatabaseMigrationManager
manager = DatabaseMigrationManager('databases/arrow_database.db')

# Get detailed migration info
migration = manager.get_migration_details("008")
print(f"Migration details: {migration}")

# Test migration step by step
pending = manager.get_pending_migrations()
migration_008 = next((m for m in pending if m.version == "008"), None)
if migration_008:
    print(f"Testing migration: {migration_008.description}")
    success = migration_008.up('databases/arrow_database.db', 'development')
    print(f"Result: {success}")
```

## Future Enhancements

### Planned Features

1. **Migration Branching** - Support for feature branch migrations
2. **Schema Diffing** - Automatic migration generation from schema changes
3. **Data Validation** - Post-migration data integrity checks
4. **Performance Profiling** - Migration execution time analysis
5. **Backup Integration** - Automatic pre-migration backups

### Contributing Guidelines

When adding new migration features:

1. **Follow existing patterns** in `DatabaseMigrationManager`
2. **Add comprehensive tests** for new functionality
3. **Update documentation** with examples
4. **Consider backward compatibility** with existing migrations
5. **Test across all environments** (development, production, Docker)

## Conclusion

The Archery Tools migration system provides a robust foundation for evolving database schemas safely across environments. By following the patterns and best practices outlined in this document, developers can confidently make database changes while maintaining data integrity and system reliability.

For questions or issues with migrations, refer to the troubleshooting section or consult the admin panel's migration management interface for real-time status and debugging information.