# Database Migrations System

This document provides comprehensive guidance on the database migration system used in the Archery Tools project, including how to create, apply, and manage database schema changes safely across different environments.

## Overview

The Archery Tools project uses a robust, versioned database migration system that ensures consistent database schema evolution across development, staging, and production environments. The system supports both arrow database (`arrow_database.db`) and user database (`user_data.db`) migrations with dependency management, rollback capabilities, and enhanced admin panel management.

## ⚠️ CRITICAL: Recommended Migration Format (August 2025)

**For reliable production deployment, use the CURSOR-BASED format that matches successful migrations like 036, 037:**

```python
#!/usr/bin/env python3
"""
Migration XXX: Brief Description
"""
import sqlite3
import sys
import os

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': XXX,
        'description': 'Brief description',
        'author': 'System', 
        'created_at': '2025-08-21'
    }

def migrate_up(cursor):
    """Apply the migration"""
    conn = cursor.connection
    try:
        print("🔧 Migration XXX: Description...")
        cursor.execute("CREATE TABLE ...")
        conn.commit()
        print("🎯 Migration XXX completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration XXX failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback the migration"""
    conn = cursor.connection
    try:
        cursor.execute("DROP TABLE ...")
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False

if __name__ == "__main__":
    # Test standalone
    db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db')
    conn = sqlite3.connect(db_path)
    try:
        success = migrate_up(conn.cursor())
        print("✅ Migration test completed successfully" if success else "❌ Migration test failed")
    finally:
        conn.close()
```

**✅ WHY THIS FORMAT WORKS:**
- **Proven in Production**: Migrations 036, 037 use this format successfully
- **Auto-Discovery**: Migration manager Method 4 detects `migrate_up(cursor)` functions
- **Database Management**: Uses cursor.connection for proper transaction handling
- **Error Handling**: Built-in rollback and error reporting
- **Standalone Testing**: Can be tested directly with `python migration_file.py`

**❌ AVOID - These formats cause production failures:**
```python
# BaseMigration class - complex path resolution issues
class Migration037(BaseMigration):
    def up(self, db_path: str, environment: str) -> bool: pass

# Wrong signatures - parameter mismatch errors  
def up(self): pass  # Missing parameters
def up(self, db_path: str, environment: str): pass  # Type hints cause issues
```

### Recent Enhancements (August 2025)

- **Dual Database Architecture**: Complete separation of arrow specifications and user data with targeted migration routing
- **Enhanced Admin Panel**: Visual database targeting with status indicators and comprehensive migration legends
- **Chronograph Data Integration**: Advanced arrow speed calculations with chronograph data priority system
- **String Equipment Enhancement**: String material speed modifiers and equipment management improvements
- **Migration Discovery Improvements**: Support for multiple migration patterns including cursor-based migrations

## Architecture

### Core Components

- **`DatabaseMigrationManager`** - Central migration orchestrator
- **`BaseMigration`** - Abstract base class for all migrations
- **Migration Files** - Individual migration implementations
- **Migration Table** - Tracks applied migrations and their status
- **Admin Interface** - Web-based migration management

### Database Targets

The system supports migrations for two separate databases with enhanced targeting and status tracking:

1. **Arrow Database** (`arrow_database.db`) - **Target: 'arrow'**
   - Arrow specifications and spine data
   - Equipment catalog and categories
   - Manufacturer data and spine charts
   - Chronograph data for speed calculations
   - String material speed modifiers

2. **User Database** (`user_data.db`) - **Target: 'user'**
   - User accounts and authentication
   - Bow setups and configurations  
   - Equipment assignments and tuning sessions
   - User equipment specifications
   - String equipment configurations

### Migration Targeting System

Each migration now includes a `target_database` field that determines which database it applies to:

```python
class Migration020StringEquipment(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "020"
        self.description = "Enhance string equipment fields for speed calculation"
        self.target_database = 'user'  # Routes to user database
        self.dependencies = ["008"]  # Equipment field standards dependency
```

**Migration Target Mapping** (as of August 2025):
- **Migrations 001-020**: User database (accounts, setups, equipment)
- **Migration spine_calc**: Arrow database (spine calculation tables)
- **Future migrations**: Explicitly specify target_database in migration class

### Database Paths in Different Environments

**Hybrid Development (Docker)**:
- Arrow Database: `/app/databases/arrow_database.db`
- User Database: `/app/databases/user_data.db`
- Volume: `arrowtuner-dev-databases`

**Local Development**:
- Arrow Database: `arrow_scraper/databases/arrow_database.db`
- User Database: `arrow_scraper/databases/user_data.db`

**Production**:
- Arrow Database: `/app/databases/arrow_database.db`
- User Database: `/app/databases/user_data.db`
- Volume: `arrowtuner-databases`

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
│   ├── 007_user_bow_equipment_table.py
│   ├── 008_equipment_field_standards.py
│   ├── 009_enhanced_equipment_system.py
│   ├── 010_equipment_manufacturer_linking.py
│   ├── 011_equipment_categories_expansion.py
│   ├── 012_fix_pending_manufacturers_schema.py
│   ├── 013_equipment_change_logging.py
│   ├── 014_arrow_change_logging.py
│   ├── 015_remove_setup_arrows_unique_constraint.py
│   ├── 016_equipment_soft_delete_enhancement.py
│   ├── 017_remove_setup_arrows_duplicate_constraint.py
│   ├── 018_make_equipment_id_nullable.py
│   ├── 019_add_chronograph_data.py
│   └── 020_enhance_string_equipment_fields.py
├── database_migration_manager.py
└── run_migrations.py
```

### Migration File Templates

#### 🚀 **Recommended: Cursor-Based Template (Production-Tested)**

This format is used by successful migrations like 036, 037 and works reliably in production:

```python
#!/usr/bin/env python3
"""
Migration XXX: [Brief Description]
[Detailed description of what this migration does]
"""

import sqlite3
import sys
import os

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': XXX,
        'description': '[Brief Description]',
        'author': 'System',
        'created_at': '2025-08-21'
    }

def migrate_up(cursor):
    """Apply the migration"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration XXX: [Description]...")
        
        # Your migration SQL here
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS new_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add indexes if needed
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_new_table_name 
            ON new_table (name)
        """)
        
        conn.commit()
        print("🎯 Migration XXX completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration XXX failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback the migration"""
    conn = cursor.connection
    
    try:
        print("🔄 Rolling back Migration XXX...")
        
        # Remove what was created
        cursor.execute("DROP TABLE IF EXISTS new_table")
        
        conn.commit()
        print("🔄 Migration XXX rollback completed")
        return True
        
    except Exception as e:
        print(f"❌ Migration XXX rollback failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Test the migration
    db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'down':
            success = migrate_down(conn.cursor())
        else:
            success = migrate_up(conn.cursor())
        
        if success:
            print("✅ Migration test completed successfully")
        else:
            print("❌ Migration test failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration test error: {e}")
        sys.exit(1)
    finally:
        conn.close()
```

#### 🏗️ **Alternative: Class-Based Template (Advanced)**

For more complex migrations that need dependency management:

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

## 📋 Complete Migration Template

**Copy this template for new migrations to ensure correct interface:**

```python
#!/usr/bin/env python3
"""
Migration XXX: [Brief Description]
Author: [Your Name]  
Date: [Date]
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import BaseMigration
sys.path.append(str(Path(__file__).parent.parent))
from database_migration_manager import BaseMigration

class MigrationXXX[DescriptiveName](BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "XXX"
        self.description = "Brief description of migration"
        self.dependencies = []  # ["XXX"] if depends on other migrations
        self.environments = ['all']  # ['all', 'development', 'production', 'docker']
        self.target_database = 'arrow'  # 'arrow' or 'user'
    
    def up(self, db_path, environment='development'):
        """Apply the migration - REQUIRED SIGNATURE"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print(f"🔧 Applying Migration XXX: [Description]...")
            
            # Your migration SQL here
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS new_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            print("✅ Migration XXX completed successfully")
            return True  # CRITICAL: Must return True
            
        except Exception as e:
            print(f"❌ Migration XXX failed: {e}")
            return False
    
    def down(self, db_path, environment='development'):
        """Rollback the migration - REQUIRED SIGNATURE"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("DROP TABLE IF EXISTS new_table")
            
            conn.commit()
            conn.close()
            
            return True  # CRITICAL: Must return True
            
        except Exception as e:
            print(f"❌ Migration XXX rollback failed: {e}")
            return False

# Create the migration instance for discovery
migration = MigrationXXX[DescriptiveName]()

if __name__ == "__main__":
    # For standalone testing
    from pathlib import Path
    db_path = Path(__file__).parent.parent / "databases" / "arrow_database.db"
    migration.up(str(db_path), 'development')
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
# Create new migration file (next available number after 020)
touch migrations/021_my_new_feature.py
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

### Hybrid Development Environment (Recommended)

When using the hybrid development environment with `./start-hybrid-dev.sh`, migrations are handled within the Docker container:

```bash
# Check migration status in Docker container
docker exec arrowtuner-api-dev python run_migrations.py --status

# Apply all pending migrations
docker exec arrowtuner-api-dev python run_migrations.py

# Apply migrations for specific environment
docker exec arrowtuner-api-dev python run_migrations.py --environment development

# Dry run (test without applying)
docker exec arrowtuner-api-dev python run_migrations.py --dry-run

# Apply specific migration
docker exec arrowtuner-api-dev python run_migrations.py --version 008

# Show detailed migration information
docker exec arrowtuner-api-dev python -c "from database_migration_manager import DatabaseMigrationManager; mgr = DatabaseMigrationManager('/app/databases/arrow_database.db'); print(mgr.get_migration_status())"
```

### Local Development

For local development without Docker:

```bash
cd arrow_scraper
source venv/bin/activate

# Apply all pending migrations
python run_migrations.py

# Apply migrations for specific environment
python run_migrations.py --environment development

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

Access the enhanced admin panel at `/admin` with admin privileges:

#### 🎯 **Database Migration Management**

1. **Migration Status Dashboard** - Visual overview with database targeting:
   - Total migrations count across both databases
   - Applied vs pending migrations with color coding
   - Environment detection (development/production/docker)
   - Database health integration

2. **Database Migration Legend** - Comprehensive explanation:
   - **Database Types**: Arrow DB (blue badges) vs User DB (purple badges)
   - **Status Indicators**: A/U badges showing applied status per database
   - **Target Database**: Visual indication of which database each migration affects

3. **Enhanced Migration Display**:
   - **Pending Migrations**: Shows target database badges and cross-database status
   - **Applied Migrations History**: Recent 10 migrations with database targeting
   - **Database Status Indicators**: A (Arrow DB) and U (User DB) status per migration
   - **Migration Descriptions**: Clear descriptions with target database context

4. **Migration Operations**:
   - **Refresh Status**: Real-time migration status updates across both databases
   - **Run Migrations**: Apply pending migrations with dry-run option
   - **Dual Database Support**: Automatic routing to correct database based on target
   - **Error Handling**: Comprehensive error reporting with database context

#### 🔧 **Advanced Features**

- **Cross-Database Status Tracking**: See which migrations are applied in which databases
- **Environment-Aware Display**: Different indicators for development vs production
- **Real-Time Updates**: Dynamic status updates without page refresh
- **Responsive Design**: Full mobile and tablet support with dark mode
- **Accessibility**: Screen reader support and keyboard navigation

## User Database Migrations

### Special Considerations

When creating migrations for the user database, follow these enhanced patterns with dual database support:

#### Dual Database Migration Runner

The system now includes separate migration runners for each database:

```bash
# Run arrow database migrations
python run_migrations.py

# Run user database migrations  
python run_user_migrations.py

# Both are automatically executed during startup via unified startup system
```

#### Database Path Resolution Enhancement (August 2025)

**Fixed Critical Issue**: DatabaseMigrationManager now properly respects database-specific paths:

```python
def _resolve_database_path(self, db_path: str) -> str:
    """Resolve database path with environment awareness"""
    # If an absolute path is provided, use it directly (highest priority)
    if Path(db_path).is_absolute():
        return db_path
    
    # Determine which environment variable to check based on the database path
    env_var = None
    if 'user' in db_path.lower() or 'user_data' in db_path.lower():
        env_var = 'USER_DATABASE_PATH'
    elif 'arrow' in db_path.lower() or db_path == 'arrow_database.db':
        env_var = 'ARROW_DATABASE_PATH'
    
    # Check for environment variable (Docker deployment)
    if env_var:
        env_db_path = os.environ.get(env_var)
        if env_db_path:
            return env_db_path
```

**Before Fix**: Both arrow and user migrations used arrow database path
**After Fix**: User migrations correctly target user database, arrow migrations target arrow database

#### Migration Discovery Patterns

The system now supports multiple migration patterns for backward compatibility:

**Method 1: Modern Class-Based (Recommended)**
```python
class Migration020StringEquipment(BaseMigration):
    def __init__(self):
        super().__init__()
        self.target_database = 'user'  # Explicitly specify target
    
    def up(self, db_path: str, environment: str) -> bool:
        # Migration implementation
        pass
```

**Method 2: Legacy Class-Based**
```python
class Migration:
    def __init__(self):
        self.version = "019"
        self.description = "Add chronograph data"
    
    def up(self, db_path: str, environment: str) -> bool:
        # Migration implementation
        pass
```

**Method 3: Function-Based**
```python
def migrate_up():
    # Legacy function-based migration
    pass

def migrate_down():
    # Rollback function
    pass
```

**Method 4: Cursor-Based (Recommended for Production - August 2025)**
```python
def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 37,
        'description': 'Fix Chronograph Integration - Setup arrow ID mapping',
        'author': 'System',
        'created_at': '2025-08-21'
    }

def migrate_up(cursor):
    """Migration using cursor parameter"""
    conn = cursor.connection
    try:
        print("🔧 Migration 037: Fixing chronograph integration...")
        cursor.execute("CREATE TABLE ...")
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    
def migrate_down(cursor):
    """Rollback using cursor parameter"""
    conn = cursor.connection
    try:
        cursor.execute("DROP TABLE ...")
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Test the migration
    db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db')
    conn = sqlite3.connect(db_path)
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'down':
            success = migrate_down(conn.cursor())
        else:
            success = migrate_up(conn.cursor())
        if success:
            print("✅ Migration test completed successfully")
    finally:
        conn.close()
```

#### Environment-Aware Database Path Resolution

Migrations now include sophisticated path resolution for different environments:

```python
def get_user_database_path():
    """Get the user database path with environment awareness"""
    # Check for environment variable first (Docker deployment)
    env_db_path = os.environ.get('USER_DATABASE_PATH')
    if env_db_path:
        return env_db_path
    
    # Try Docker container paths
    docker_paths = [
        "/app/databases/user_data.db",
        "/app/user_data.db",
        "/app/databases/user_database.db"
    ]
    
    # Try local development paths
    local_paths = [
        "databases/user_data.db",
        "user_data.db",
        "../databases/user_data.db"
    ]
    
    # Intelligent path resolution with fallbacks
    # ...
```

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

## Recent Improvements (August 2025)

### Dual Database Architecture Enhancement

**Complete Dual Database Migration System:**
- **Separate Migration Runners**: `run_migrations.py` for arrow database, `run_user_migrations.py` for user database
- **Migration Target Mapping**: Each migration explicitly targets arrow or user database
- **Enhanced Admin API**: `/api/admin/migrations/status` returns status for both databases
- **Cross-Database Status Tracking**: Visual indicators showing migration status across both databases

**Migration Target Assignment:**
```python
migration_targets = {
    '001': 'user', '002': 'user', '003': 'user', '004': 'user', '005': 'user',
    '006': 'user', '007': 'user', '008': 'user', '009': 'user', '010': 'user',
    '011': 'user', '012': 'user', '013': 'user', '014': 'user', '015': 'user',
    '016': 'user', '017': 'user', '018': 'user', '019': 'user', '020': 'user',
    'spine_calc': 'arrow'
}
```

### Chronograph Data Integration (Migration 019)

**Advanced Arrow Speed Calculation System:**
- **Migration 019**: Adds chronograph data tables for measured arrow speeds
- **Priority System**: Chronograph data → Enhanced calculations → Basic calculations
- **Database Schema**:
  ```sql
  CREATE TABLE chronograph_data (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      setup_id INTEGER NOT NULL,
      arrow_id INTEGER NOT NULL,
      measured_speed REAL NOT NULL,
      measurement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      conditions TEXT,
      FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
  )
  ```

**Speed Calculation Enhancement:**
- **Three-Tier System**: Measured speeds override calculated speeds for accuracy
- **Chronograph Integration**: Real measured arrow speeds stored and prioritized
- **API Enhancement**: `calculate_enhanced_arrow_speed_internal()` function with chronograph priority

### String Equipment Enhancement (Migration 020)

**String Material Speed Modifiers:**
- **Migration 020**: Enhanced string equipment fields for speed calculation
- **Material Speed Factors**:
  - Dacron: 0.92 (slowest, most forgiving)
  - FastFlight: 0.98 (standard)
  - Dyneema: 1.00 (baseline)
  - Vectran: 1.02 (fast)
  - SK75 Dyneema: 1.04 (fastest)

**Enhanced String Equipment Fields:**
```python
string_fields = [
    {
        'field_name': 'material',
        'field_type': 'dropdown',
        'field_options': ['Dacron', 'FastFlight', 'Dyneema', 'Vectran', 'SK75 Dyneema']
    },
    {
        'field_name': 'speed_rating', 
        'field_options': ['Slow (Dacron)', 'Standard (FastFlight)', 'Fast (Dyneema)', 
                         'Very Fast (Vectran)', 'Ultra Fast (SK75)']
    }
    # Additional fields: strand_count, serving_material, string_length, 
    # brace_height, estimated_shots
]
```

### Migration System Enhancements

**Logger Integration Fix:**
- **Issue**: Migration wrappers (`MigrationWrapper`, `FunctionWrapper`, `RunMigrationWrapper`) were missing logger access, causing `'MigrationWrapper' object has no attribute 'logger'` errors
- **Solution**: Added logger initialization to all wrapper classes by capturing and assigning the parent manager's logger
- **Implementation**: 
  ```python
  def _create_migration_wrapper(self, migration_instance, module, migration_file):
      manager_logger = self.logger  # Capture the manager's logger
      
      class MigrationWrapper(BaseMigration):
          def __init__(self, wrapped_migration):
              super().__init__()
              # ... other initialization ...
              self.logger = manager_logger  # Use the manager's logger
  ```

**Parameter Handling Enhancement:**
- **Issue**: Migration methods with different parameter signatures were not being called correctly, causing `up() missing 1 required positional argument: 'environment'` errors
- **Solution**: Enhanced parameter detection using `inspect.signature()` to support various migration method signatures
- **Supported Signatures**:
  - `up()` - Legacy migrations with no parameters
  - `up(db_path)` - Basic migrations with database path only  
  - `up(db_path, environment)` - Modern migrations with both database path and environment
- **Implementation**:
  ```python
  import inspect
  up_signature = inspect.signature(self.wrapped.up)
  param_count = len(up_signature.parameters)
  
  if param_count >= 2:
      result = self.wrapped.up(db_path, environment or 'development')
  elif param_count == 1:
      result = self.wrapped.up(db_path)
  else:
      result = self.wrapped.up()
  ```

**Admin Interface Reliability:**
- **Issue**: Admin frontend migration runner returning 500 Internal Server Error
- **Solution**: Fixed underlying logger and parameter issues, ensuring admin interface works correctly
- **Result**: Migration management through web interface now fully functional

**Migration State Management:**
- **Enhancement**: Improved handling of manually applied migrations through proper state recording
- **Feature**: Migrations can now be marked as applied programmatically after manual execution
- **Usage**:
  ```python
  manager._record_migration(migration_instance, success=True)
  ```

### Migration Wrapper Architecture

The migration system now uses a sophisticated wrapper architecture that handles different migration styles:

**1. Class-Based Migrations (Recommended)**
```python
class Migration017(BaseMigration):
    def up(self, db_path: str, environment: str) -> bool:
        # Modern migration with full parameter support
        pass
```

**2. Function-Based Migrations**
```python
def up(db_path):
    # Simple function-based migration
    pass
```

**3. Legacy Migrations**
```python
def run_migration():
    # Legacy migration with no parameters
    pass
```

### Troubleshooting New Issues

**Database Path Resolution Errors (August 2025):**
```bash
# Verify correct database paths are being used
python3 -c "
from database_migration_manager import DatabaseMigrationManager
from run_user_migrations import get_user_database_path

# Test arrow database manager
arrow_mgr = DatabaseMigrationManager('arrow_database.db')
print(f'Arrow DB path: {arrow_mgr.database_path}')

# Test user database manager
user_path = get_user_database_path()
user_mgr = DatabaseMigrationManager(user_path)
print(f'User DB path: {user_mgr.database_path}')

# Should show different paths
print(f'Paths different: {arrow_mgr.database_path != user_mgr.database_path}')
"
```

**Environment Variable Verification:**
```bash
# Check environment variables in production
echo "ARROW_DATABASE_PATH: $ARROW_DATABASE_PATH"
echo "USER_DATABASE_PATH: $USER_DATABASE_PATH"

# Should show:
# ARROW_DATABASE_PATH: /root/archerytools/databases/arrow_database.db
# USER_DATABASE_PATH: /root/archerytools/databases/user_data.db
```

**Migration Status Verification:**
```bash
# Check migration status for both databases
python3 run_migrations.py --status-only
python3 run_user_migrations.py --status-only

# Should show different database paths in output
```

**Logger-Related Errors:**
```python
# Verify logger is properly initialized
from database_migration_manager import DatabaseMigrationManager
manager = DatabaseMigrationManager()
migrations = manager.get_pending_migrations()
for migration in migrations:
    print(f"Migration {migration.version} has logger: {hasattr(migration, 'logger')}")
```

**Parameter Mismatch Errors:**
```python
# Debug parameter detection
import inspect
for migration in migrations:
    if hasattr(migration, 'wrapped'):
        sig = inspect.signature(migration.wrapped.up)
        print(f"Migration {migration.version} up() params: {len(sig.parameters)}")
```

**Manual Migration Recording:**
```python
# Record a manually applied migration
from database_migration_manager import DatabaseMigrationManager
manager = DatabaseMigrationManager()
pending = manager.get_pending_migrations()
migration_to_record = next((m for m in pending if m.version == "017"), None)
if migration_to_record:
    manager._record_migration(migration_to_record, success=True)
```

### Case Study: Recent Major Migrations

#### Critical Fix: Database Path Resolution (August 2025)

**Background**: User database migrations were incorrectly targeting the arrow database due to hardcoded path resolution.

**Issue**: `DatabaseMigrationManager` always checked `ARROW_DATABASE_PATH` environment variable regardless of the database type, causing both arrow and user migration runners to use the same database path.

**Symptoms**:
- Production logs showed both databases using same path: `/root/archerytools/databases/arrow_database.db`
- Admin panel not displaying user migrations correctly
- User database migrations not being applied to correct database

**Solution**: Enhanced `_resolve_database_path()` method to:
- Detect database type from path keywords (`user`, `user_data`, `arrow`)
- Use appropriate environment variable (`USER_DATABASE_PATH` vs `ARROW_DATABASE_PATH`)
- Support Docker container paths for both database types
- Prioritize absolute paths when provided directly

**Result**: User migrations now correctly target `/root/archerytools/databases/user_data.db`

#### Migration 017 - Arrow Duplication Fix

**Background**: Users were encountering 409 CONFLICT errors when trying to duplicate arrows due to a restrictive unique constraint on the `setup_arrows` table.

**Challenge**: Remove the unique constraint while preserving all existing data and maintaining data integrity.

#### Migration 019 - Chronograph Data Integration

**Background**: Need for advanced arrow speed calculations incorporating real measured chronograph data.

**Challenge**: Add chronograph data tables and integrate with existing speed calculation system.

**Implementation**:
```python
def migrate_up(cursor):
    """Add chronograph data tables for measured arrow speeds"""
    # Create chronograph_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chronograph_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setup_id INTEGER NOT NULL,
            arrow_id INTEGER NOT NULL,
            measured_speed REAL NOT NULL,
            measurement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            conditions TEXT,
            equipment_notes TEXT,
            FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_chronograph_setup_arrow 
        ON chronograph_data (setup_id, arrow_id)
    ''')
    
    print("✅ Added chronograph data table for measured arrow speeds")
```

**Integration**: Enhanced arrow speed API to prioritize chronograph data over calculations.

#### Migration 020 - String Equipment Enhancement

**Background**: Need for string material speed modifiers in arrow speed calculations.

**Challenge**: Add comprehensive string equipment fields while maintaining backward compatibility.

**Implementation**:
```python
def migrate_up(cursor):
    """Enhance string equipment fields for speed calculation"""
    string_fields = [
        {
            'category_name': 'String',
            'field_name': 'material',
            'field_type': 'dropdown',
            'field_options': json.dumps([
                'Dacron', 'FastFlight', 'Dyneema', 
                'Vectran', 'SK75 Dyneema', 'Custom Blend'
            ]),
            'help_text': 'String material affects bow speed - Dacron is slowest but most forgiving'
        }
        # Additional fields...
    ]
    
    for field in string_fields:
        # Insert or update string equipment fields
        cursor.execute('''
            INSERT OR REPLACE INTO equipment_field_standards 
            (category_name, field_name, field_type, label, field_options, help_text)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (field['category_name'], field['field_name'], field['field_type'],
              field['label'], field['field_options'], field['help_text']))
```

**Integration**: String material speed modifiers applied in enhanced arrow speed calculations.

#### Migration 055 - Journal Image Upload System (September 2025)

**Background**: Frontend image upload functionality was implemented but the database schema lacked an 'images' column in journal_entries table.

**Challenge**: Add images column to existing journal_entries table while preserving all data and foreign key constraints in SQLite.

**Issue**: SQLite doesn't support ALTER TABLE ADD COLUMN on tables with foreign key constraints, causing:
```
error in table journal_entries after add column: near 'FOREIGN': syntax error
```

**Solution**: Implemented table recreation approach:

**Implementation**:
```python
def migrate_up(cursor):
    """Add images column to journal_entries table for image upload functionality"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration 055: Adding images column to journal_entries table...")
        
        # Check if column already exists (idempotent)
        cursor.execute("PRAGMA table_info(journal_entries)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'images' in columns:
            print("✅ Images column already exists, skipping migration")
            return True
        
        # 1. Create new table with images column
        cursor.execute('''
            CREATE TABLE journal_entries_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bow_setup_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                entry_type TEXT NOT NULL DEFAULT 'general',
                tags TEXT,
                is_private BOOLEAN DEFAULT 0,
                images TEXT,  -- JSON array of image objects
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
            )
        ''')
        
        # 2. Copy all existing data
        cursor.execute('''
            INSERT INTO journal_entries_new 
            (id, user_id, bow_setup_id, title, content, entry_type, tags, is_private, created_at, updated_at)
            SELECT id, user_id, bow_setup_id, title, content, entry_type, tags, is_private, created_at, updated_at
            FROM journal_entries
        ''')
        
        # 3. Drop old table and rename new table
        cursor.execute("DROP TABLE journal_entries")
        cursor.execute("ALTER TABLE journal_entries_new RENAME TO journal_entries")
        
        conn.commit()
        print("🎯 Migration 055: Successfully added images column to journal_entries")
        return True
        
    except Exception as e:
        print(f"❌ Migration 055 failed: {e}")
        conn.rollback()
        return False
```

**Key Technical Details**:
- **Table Recreation**: Used CREATE TABLE + INSERT + DROP + RENAME pattern to work around SQLite ALTER TABLE limitations
- **Data Preservation**: All existing journal entries preserved during migration
- **Idempotent Design**: Checks if column exists before applying changes
- **Foreign Key Preservation**: Maintains all existing relationships and constraints
- **JSON Storage**: Images stored as JSON array enabling flexible image metadata

**Integration Impact**:
- **Frontend**: Journal entry forms and viewers now display uploaded images
- **Tuning Sessions**: Session images are properly stored and linked to journal entries
- **CDN Support**: Works with Cloudinary, AWS S3, BunnyCD, and other CDN services
- **Migration System**: Demonstrates proper SQLite constraint handling for future migrations

**Lessons Learned**:
- SQLite ALTER TABLE limitations require table recreation for complex constraint changes
- Always implement idempotent checks to prevent duplicate migration applications
- Preserve all existing data during schema changes to maintain system integrity
- Test migrations thoroughly in development before production deployment

## 🔧 Common Migration Errors & Solutions

### 1. **500 Error: "Some migrations failed"**

**Error**: API Error 500: {"error":"Some migrations failed"}

**Cause**: Incorrect migration format - using BaseMigration class instead of cursor-based format

**Solution**: Use the **cursor-based format** (like Migration 036, 037):
```python
# ✅ CORRECT - Cursor-based format (RECOMMENDED)
def get_migration_info():
    return {
        'version': 37,
        'description': 'Migration description',
        'author': 'System',
        'created_at': '2025-08-21',
        'target_database': 'arrow',  # REQUIRED: 'arrow' or 'user'
        'dependencies': [],          # Array of required migration versions
        'environments': ['all']      # Supported environments
    }

def migrate_up(cursor):
    conn = cursor.connection
    try:
        cursor.execute("CREATE TABLE ...")
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False

def migrate_down(cursor):
    # Similar pattern
    pass
```

**NOT these formats:**
```python
# ❌ BaseMigration class format - causes production failures
class Migration037(BaseMigration):
    def up(self, db_path: str, environment: str) -> bool:
        pass

# ❌ Wrong method signatures
def up(self):  # Missing parameters
def up(self, db_path: str, environment: str):  # Type hints cause issues
```

**Root Cause**: Migration discovery uses different methods. The cursor-based format (`migrate_up(cursor)`) is detected by Method 4 in the migration manager and works reliably in production.

### 2. **Migration Not Found/Discovered**

**Error**: Migration doesn't appear in admin panel

**Cause**: Incorrect file naming or missing migration instance

**Solution**: 
- File name must match pattern: `XXX_description.py`
- Must have migration instance at end: `migration = MigrationXXX()`

### 3. **Database Path Issues**

**Error**: "Could not find arrow database"

**Solution**: Use the path resolution in template or get path from parameters:
```python
def up(self, db_path, environment='development'):
    # Use the provided db_path parameter - don't resolve yourself
    conn = sqlite3.connect(db_path)
```

### 4. **Environment Targeting Issues**

**Error**: Migration runs in wrong environment

**Solution**: Set target database explicitly:
```python
def __init__(self):
    super().__init__()
    self.target_database = 'arrow'  # or 'user'
    self.environments = ['all']  # or ['production'] etc
```

### 5. **Return Value Issues**

**Error**: Migration marked as failed despite success

**Solution**: Always return True/False:
```python
def up(self, db_path, environment='development'):
    try:
        # ... migration code ...
        return True  # ✅ REQUIRED
    except Exception as e:
        print(f"❌ Error: {e}")
        return False  # ✅ REQUIRED
```

### 6. **Testing Migration Locally**

**Test standalone execution:**
```bash
cd arrow_scraper
python3 migrations/XXX_your_migration.py
```

**Test via migration manager:**
```bash
cd arrow_scraper
python3 -c "
from database_migration_manager import DatabaseMigrationManager
manager = DatabaseMigrationManager('databases/arrow_database.db')
manager.run_migrations(dry_run=True)
"
```

### 7. **Production Deployment Checklist**

Before deploying migration to production:

1. ✅ **Test locally**: Run migration on local development database
2. ✅ **Check signatures**: Verify `up(self, db_path, environment='development')` 
3. ✅ **Test rollback**: Ensure `down()` method works if needed
4. ✅ **Check return values**: Both methods return True/False
5. ✅ **Validate in admin**: Use admin panel migration dry-run
6. ✅ **Backup production**: Always backup before running in production
7. ✅ **Deploy with unified script**: Use `./start-unified.sh ssl archerytool.online`

This ensures migrations run automatically on production startup and prevents interface errors.

**Implementation**:
```python
class Migration:
    def up(self, db_path: str, environment: str) -> bool:
        """Remove unique constraint from setup_arrows to allow arrow duplication"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 1. Check if constraint exists (idempotent check)
            cursor.execute("PRAGMA index_list(setup_arrows)")
            indexes = cursor.fetchall()
            
            has_unique_constraint = False
            for index in indexes:
                if index[2] == 1:  # Check unique flag
                    # Verify it's the constraint we want to remove
                    cursor.execute(f"PRAGMA index_info({index[1]})")
                    index_columns = [col[2] for col in cursor.fetchall()]
                    if set(index_columns) == {'setup_id', 'arrow_id', 'arrow_length', 'point_weight'}:
                        has_unique_constraint = True
                        break
            
            if not has_unique_constraint:
                print("✅ No unique constraint found, migration not needed")
                return True
            
            # 2. Preserve existing data
            cursor.execute("SELECT * FROM setup_arrows")
            existing_data = cursor.fetchall()
            
            # 3. Recreate table without constraint
            cursor.execute('''
                CREATE TABLE setup_arrows_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id INTEGER NOT NULL,
                    arrow_id INTEGER NOT NULL,
                    arrow_length REAL NOT NULL,
                    point_weight REAL NOT NULL,
                    -- ... other columns ...
                    FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
                    -- Note: Removed UNIQUE constraint
                )
            ''')
            
            # 4. Copy all data
            if existing_data:
                cursor.executemany('''
                    INSERT INTO setup_arrows_new 
                    (id, setup_id, arrow_id, arrow_length, point_weight, ...)
                    VALUES (?, ?, ?, ?, ?, ...)
                ''', existing_data)
            
            # 5. Replace table atomically
            cursor.execute("DROP TABLE setup_arrows")
            cursor.execute("ALTER TABLE setup_arrows_new RENAME TO setup_arrows")
            
            conn.commit()
            print("✅ Successfully removed unique constraint")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
```

**Key Learnings from Recent Migrations**:
1. **Idempotent Design**: Always check current state before applying changes (Migration 017)
2. **Data Preservation**: Never assume data can be recreated - always preserve existing records
3. **Atomic Operations**: Use transactions to ensure consistency
4. **Error Handling**: Rollback on failures and provide clear error messages
5. **Constraint Management**: SQLite requires table recreation to remove constraints
6. **Cursor-Based Patterns**: Support for `migrate_up(cursor)` pattern for simpler migrations (019, 020)
7. **JSON Field Handling**: Proper JSON encoding for complex field options (Migration 020)
8. **Cross-Table Dependencies**: Consider equipment field standards when adding new categories
9. **Performance Indexing**: Add indexes for new tables to ensure query performance (Migration 019)
10. **Backward Compatibility**: New fields should not break existing functionality
11. **Database Path Resolution**: Ensure migration managers target correct databases in dual-database architecture
12. **Environment Variable Specificity**: Use database-specific environment variables (USER_DATABASE_PATH vs ARROW_DATABASE_PATH)
13. **Production Testing**: Always verify migration runners target correct databases in production
14. **Admin Panel Validation**: Check admin interface shows migrations for both databases correctly

### Best Practices for New Migrations

#### Migration Implementation
1. **Use Modern Signature**: Always implement `up(self, db_path: str, environment: str) -> bool`
2. **Include Logger Access**: Logger is automatically available as `self.logger` in wrapper classes
3. **Make Idempotent**: Check current state before applying changes (like Migration 017)
4. **Handle Errors Gracefully**: Use try/catch and return `False` on failures
5. **Test All Environments**: Verify migration works in development, staging, and production
6. **Preserve Data**: Always backup and preserve existing data during schema changes
7. **Use Transactions**: Wrap related operations in database transactions
8. **Provide Clear Output**: Include progress messages and success/failure indicators

#### Database Targeting
9. **Specify Target Database**: Always include `target_database = 'arrow'` or `'user'` in migration class
10. **Use Appropriate Runner**: Route user database migrations through `run_user_migrations.py`
11. **Consider Cross-Database Dependencies**: Some features span both databases
12. **Environment Path Resolution**: Use environment-aware path detection for Docker compatibility

#### Advanced Patterns
13. **JSON Field Handling**: Use `json.dumps()` for complex field options and validation rules
14. **Index Creation**: Add performance indexes for new tables and foreign keys
15. **Cursor Pattern Support**: Consider `migrate_up(cursor)` for simpler migrations
16. **Equipment Integration**: New equipment categories require equipment_field_standards entries
17. **Speed Calculation Integration**: Consider impact on arrow speed calculation system
18. **Chronograph Compatibility**: New speed-related fields should integrate with chronograph data

#### Testing and Validation
19. **Test Both Databases**: Verify migrations work correctly with dual database architecture
20. **Admin Panel Testing**: Ensure migrations display correctly in enhanced admin interface
21. **Cross-Platform Testing**: Test in hybrid development, local development, and production
22. **Migration Status Verification**: Confirm migrations show correct database targeting in admin panel

## Future Enhancements

### Planned Features

1. **Migration Branching** - Support for feature branch migrations with merge conflict resolution
2. **Schema Diffing** - Automatic migration generation from schema changes
3. **Data Validation** - Post-migration data integrity checks with rollback triggers
4. **Performance Profiling** - Migration execution time analysis and optimization recommendations
5. **Backup Integration** - Automatic pre-migration backups with CDN storage
6. **Migration Templates** - Code generation for common migration patterns
7. **Cross-Database Migrations** - Migrations that span both arrow and user databases
8. **Migration Dependencies Graph** - Visual dependency mapping in admin panel
9. **Automated Testing** - Unit test generation for new migrations
10. **Migration Rollback Chains** - Safe multi-migration rollback with dependency checking

### Recent Achievements (August 2025)

1. ✅ **Dual Database Architecture** - Complete separation with targeted migration routing
2. ✅ **Enhanced Admin Panel** - Visual database targeting with comprehensive status indicators
3. ✅ **Chronograph Data Integration** - Advanced arrow speed calculations with measured data priority
4. ✅ **String Equipment Enhancement** - Material speed modifiers and comprehensive equipment fields
5. ✅ **Migration Discovery Improvements** - Support for cursor-based and multiple migration patterns
6. ✅ **Cross-Database Status Tracking** - Real-time migration status across both databases
7. ✅ **Environment-Aware Path Resolution** - Docker and local development compatibility
8. ✅ **Migration Target Mapping** - Automated routing of migrations to correct database

### Recent Achievements (September 2025)

1. ✅ **Image Upload System Integration** - Complete image storage for journal entries with CDN support
2. ✅ **Session-Level Image Storage** - Tuning sessions now properly store and link images to journal entries
3. ✅ **Migration 055** - Added images column to journal_entries table with table recreation approach

### Contributing Guidelines

When adding new migration features:

1. **Follow existing patterns** in `DatabaseMigrationManager`
2. **Add comprehensive tests** for new functionality
3. **Update documentation** with examples
4. **Consider backward compatibility** with existing migrations
5. **Test across all environments** (development, production, Docker)

## Conclusion

The Archery Tools migration system provides a robust, dual-database foundation for evolving database schemas safely across environments. With the recent enhancements including chronograph data integration, string equipment management, and advanced admin panel features, the system now offers:

### 🎯 **Enterprise-Grade Migration Management**
- **Dual Database Architecture**: Separate arrow specifications and user data with intelligent routing
- **Enhanced Admin Interface**: Visual database targeting with comprehensive status tracking
- **Multiple Migration Patterns**: Support for class-based, function-based, and cursor-based migrations
- **Environment Awareness**: Seamless operation across development, staging, and production

### 🚀 **Advanced Features**
- **Chronograph Data Integration**: Real measured arrow speeds with priority calculation system
- **String Equipment Enhancement**: Material speed modifiers and comprehensive equipment management
- **Cross-Database Status Tracking**: Real-time migration status across both databases
- **Migration Target Mapping**: Automated routing ensuring migrations apply to correct database

### 🔧 **Developer Experience**
- **Comprehensive Documentation**: Detailed examples and troubleshooting guides
- **Visual Admin Panel**: Intuitive migration management with database targeting indicators
- **Error Handling**: Robust error reporting with database context
- **Testing Support**: Unit testing patterns and integration testing guidelines

By following the patterns and best practices outlined in this document, developers can confidently make database changes while maintaining data integrity, system reliability, and taking advantage of the latest enhancements like chronograph data integration and advanced string equipment management.

### 📞 **Support and Resources**

For questions or issues with migrations:
1. **Admin Panel**: Use `/admin` for real-time migration status and management
2. **Troubleshooting**: Refer to the comprehensive troubleshooting section above
3. **Recent Enhancements**: Review August 2025 improvements for latest features
4. **Migration Examples**: Study Migrations 019 and 020 for modern implementation patterns
5. **Database Health**: Use admin panel database health monitoring for performance insights