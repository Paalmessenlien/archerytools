# Database Migration System

## Overview

The Database Migration System provides robust, versioned database schema and data migrations with environment awareness for ArrowTuner. It ensures consistent database state across development, production, and Docker environments with automatic migration execution on startup.

## Table of Contents

- [Architecture](#architecture)
- [Usage](#usage)
- [Migration Development](#migration-development)
- [Production Deployment](#production-deployment)
- [Docker Integration](#docker-integration)
- [Troubleshooting](#troubleshooting)

## Architecture

### Core Components

1. **`DatabaseMigrationManager`** - Central migration orchestrator
2. **`BaseMigration`** - Abstract base class for all migrations
3. **Migration Registry** - Version tracking in `database_migrations` table
4. **Environment Detection** - Automatic Docker/host/production detection
5. **Path Resolution** - Smart database path detection across environments

### Migration Versioning

Migrations use a simple numeric versioning system:
- `001_spine_calculator_tables.py` - Version 001
- `002_user_database_schema.py` - Version 002
- `003_json_data_import.py` - Version 003

### Environment Awareness

The system automatically detects and adapts to different environments:
- **Docker**: Uses `/app/databases/` paths and container-specific logic
- **Production**: Uses production database paths and safety measures
- **Development**: Uses local relative paths and development features

## Usage

### Command Line Interface

#### Show Migration Status
```bash
# Show current migration status
python3 run_migrations.py --status-only

# Using migration manager directly
python3 database_migration_manager.py status
```

#### Run Migrations
```bash
# Run all pending migrations
python3 run_migrations.py

# Run migrations with dry-run (preview only)
python3 run_migrations.py --dry-run

# Run up to specific version
python3 run_migrations.py --target 002
```

#### Docker Integration
```bash
# Run migrations in Docker container (automatic container detection)
./docker-migration-runner.sh migrate

# Show status in Docker container
./docker-migration-runner.sh status

# Dry-run in Docker container
./docker-migration-runner.sh dry-run
```

### Automatic Startup Integration

Migrations run automatically on startup via:
- `start-unified.sh` - Unified startup script for all environments
- `start-api-robust.sh` - API startup script with migration integration
- Docker containers - Automatic migration on container start

## Migration Development

### Creating a New Migration

1. **Create Migration File**:
```python
# arrow_scraper/migrations/004_example_migration.py

import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database_migration_manager import BaseMigration

class ExampleMigration(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "004"
        self.description = "Example migration description"
        self.dependencies = ["001", "002"]  # Depends on these migrations
        self.environments = ['all']  # Or ['development', 'production', 'docker']
    
    def up(self, db_path: str, environment: str) -> bool:
        """Apply the migration"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS example_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            print("✅ Example table created")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create example table: {e}")
            if 'conn' in locals():
                conn.close()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback the migration"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("DROP TABLE IF EXISTS example_table")
            
            conn.commit()
            conn.close()
            
            print("✅ Example table dropped")
            return True
            
        except Exception as e:
            print(f"❌ Failed to drop example table: {e}")
            if 'conn' in locals():
                conn.close()
            return False
```

2. **Test Migration**:
```bash
# Test migration locally
cd arrow_scraper
python3 run_migrations.py --dry-run

# Apply migration
python3 run_migrations.py
```

### Migration Types

#### Schema Migrations
Create/alter database tables, indexes, constraints:
```python
def up(self, db_path: str, environment: str) -> bool:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("ALTER TABLE arrows ADD COLUMN new_field TEXT")
    cursor.execute("CREATE INDEX idx_arrows_new_field ON arrows(new_field)")
    
    conn.commit()
    conn.close()
    return True
```

#### Data Migrations
Import data, transform existing data:
```python
def up(self, db_path: str, environment: str) -> bool:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Import data from JSON files
    data_dir = Path(__file__).parent.parent / "data" / "processed"
    for json_file in data_dir.glob("*.json"):
        # Import logic here
        pass
    
    conn.commit()
    conn.close()
    return True
```

#### Environment-Specific Migrations
```python
def up(self, db_path: str, environment: str) -> bool:
    if environment == "production":
        # Production-specific logic
        self._production_migration(db_path)
    elif environment == "docker":
        # Docker-specific logic
        self._docker_migration(db_path)
    else:
        # Development logic
        self._development_migration(db_path)
    
    return True
```

## Production Deployment

### Automatic Migration on Deployment

When deploying to production with `./start-unified.sh ssl archerytool.online`:

1. **Migration Check**: System checks for pending migrations
2. **Backup Creation**: Automatic database backup before migrations
3. **Migration Execution**: Runs pending migrations in dependency order
4. **Verification**: Confirms migration success before starting services
5. **Service Startup**: Starts services with updated database schema

### Manual Production Migration

For urgent production fixes:

```bash
# On production server
cd /root/archerytools

# Check migration status
./docker-migration-runner.sh status

# Run migrations in production containers
./docker-migration-runner.sh migrate

# Restart services
./start-unified.sh ssl archerytool.online
```

### Production Safety Features

- **Automatic Backups**: Database backed up before migrations
- **Rollback Support**: Migration rollback capabilities (limited)
- **Non-blocking Failures**: Failed migrations don't prevent service startup
- **Environment Detection**: Production-specific migration behavior

## Docker Integration

### Container Migration Workflow

1. **Container Detection**: Automatically finds API container
2. **File Copy**: Copies migration files into container
3. **In-Container Execution**: Runs migrations inside container with correct paths
4. **Verification**: Confirms migration success

### Docker Migration Commands

```bash
# Basic migration run
./docker-migration-runner.sh

# Show detailed status
./docker-migration-runner.sh status

# Preview changes without applying
./docker-migration-runner.sh dry-run
```

### Container Path Resolution

The system automatically resolves database paths for containers:
- `/app/databases/arrow_database.db` - Primary container path
- `/app/arrow_database.db` - Alternative container path
- Environment variable override support

## Current Migrations

### 001 - Spine Calculator Tables
- **Purpose**: Creates enhanced spine calculation tables
- **Tables**: `manufacturer_spine_charts_enhanced`, `custom_spine_charts`, `spine_conversion_tables`, `spine_calculation_adjustments`
- **Data Import**: Imports spine calculator data from JSON files
- **Status**: ✅ Complete

### 002 - User Database Schema
- **Purpose**: Ensures user database tables exist
- **Tables**: `users`, `bow_setups`, `setup_arrows`, `guide_sessions`, `backup_metadata`
- **Target**: User database (separate from arrow database)
- **Status**: ✅ Complete

### 003 - JSON Data Import
- **Purpose**: Imports arrow data from processed JSON files
- **Source**: `data/processed/*.json` files
- **Features**: Timestamp-based import detection, manufacturer-specific imports
- **Status**: ✅ Complete

## Troubleshooting

### Common Issues

#### Migration Runner Not Found
**Symptom**: `Migration runner not found, falling back to legacy migration`
**Solution**: Ensure `run_migrations.py` exists in `arrow_scraper/` directory

#### Database Path Issues
**Symptom**: `Database not found` or permission errors
**Solution**: Check environment variables:
```bash
echo $ARROW_DATABASE_PATH
echo $USER_DATABASE_PATH
```

#### Container Migration Failures
**Symptom**: Docker migration fails with path errors
**Solution**: Use Docker-specific migration runner:
```bash
./docker-migration-runner.sh status
```

#### Missing Dependencies
**Symptom**: `Circular dependency or missing migrations`
**Solution**: Check migration dependencies and ensure all required migrations exist

### Debug Commands

```bash
# Check database tables
sqlite3 databases/arrow_database.db ".tables"

# Check migration history
sqlite3 databases/arrow_database.db "SELECT * FROM database_migrations ORDER BY applied_at"

# Verify migration files
ls -la arrow_scraper/migrations/

# Check container databases
docker exec <container> ls -la /app/databases/
```

### Migration Logs

Migration logs are output to:
- Console during startup
- Container logs: `docker logs <container-name>`
- Application logs (if configured)

## Best Practices

### Migration Development
1. **Test Locally First**: Always test migrations in development
2. **Use Dry-Run**: Preview migrations with `--dry-run` flag
3. **Handle Errors Gracefully**: Include proper error handling in migrations
4. **Document Changes**: Include clear migration descriptions

### Production Deployment
1. **Backup Before Migration**: System creates automatic backups
2. **Monitor Migration Logs**: Watch for errors during deployment
3. **Test After Migration**: Verify application functionality post-migration
4. **Have Rollback Plan**: Know how to restore from backup if needed

### Docker Considerations
1. **Container Persistence**: Ensure database volumes persist across container restarts
2. **Path Consistency**: Use consistent database paths across environments
3. **Resource Limits**: Ensure containers have sufficient resources for migrations

## Future Enhancements

- **Interactive Rollback**: GUI for migration rollback selection
- **Migration Scheduling**: Time-based migration execution
- **Multi-Database Support**: Concurrent migration across multiple databases
- **Migration Templates**: Code generators for common migration patterns
- **Advanced Dependency Resolution**: Complex dependency graphs