# Unified Database Architecture Documentation

## Overview

As of August 2025, the Archery Tools platform has migrated from a dual-database architecture to a unified single-database architecture. All data (arrow specifications, user accounts, bow setups, etc.) is now stored in a single `arrow_database.db` file.

## Migration History

### Previous Architecture (Deprecated)
- **arrow_database.db**: Arrow specifications, spine data, components, manufacturers
- **user_data.db**: User accounts, bow setups, guide sessions, equipment

### Current Architecture (Unified)
- **arrow_database.db**: All data consolidated into single database
- **UnifiedDatabase class**: Single interface for all database operations

## Migration Process

The consolidation was performed through two migrations:

### Migration 023: Consolidate User Database
- Migrates all user tables from `user_data.db` into `arrow_database.db`
- Creates backup of user database before migration
- Preserves all foreign key relationships and data integrity
- Handles missing columns gracefully with defaults

### Migration 024: Fix Bow Setups Schema
- Resolves schema conflicts between different bow_setups table versions
- Renames old bow_setups to bow_setups_old
- Creates new bow_setups with unified schema
- Migrates data from old table format

## Database Schema

### User-Related Tables (Migrated)
```sql
-- Users table with extended profile fields
users (
    id INTEGER PRIMARY KEY,
    google_id TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    profile_picture_url TEXT,
    is_admin BOOLEAN DEFAULT 0,
    draw_length REAL DEFAULT 28.0,
    skill_level TEXT DEFAULT 'intermediate',
    shooting_style TEXT DEFAULT 'target',
    preferred_manufacturers TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Bow setups with comprehensive configuration
bow_setups (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    bow_type TEXT NOT NULL,
    draw_weight REAL NOT NULL,
    insert_weight REAL,
    description TEXT,
    bow_usage TEXT,
    riser_brand TEXT,
    riser_model TEXT,
    riser_length TEXT,
    limb_brand TEXT,
    limb_model TEXT,
    limb_length TEXT,
    compound_brand TEXT,
    compound_model TEXT,
    ibo_speed REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
)

-- Setup arrows linking bow setups to arrow database
setup_arrows (
    id INTEGER PRIMARY KEY,
    setup_id INTEGER NOT NULL,
    arrow_id INTEGER NOT NULL,
    arrow_length REAL NOT NULL,
    point_weight REAL NOT NULL,
    calculated_spine INTEGER,
    compatibility_score INTEGER,
    notes TEXT,
    performance_data TEXT,
    nock_weight REAL DEFAULT 0.0,
    insert_weight REAL DEFAULT 0.0,
    wrap_weight REAL DEFAULT 0.0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
    FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE
)
```

### Additional Migrated Tables
- guide_sessions: Tuning guide progress tracking
- guide_step_results: Individual guide step results
- bow_equipment: Equipment attached to bow setups
- tuning_history: Historical tuning adjustments
- backup_metadata: Backup system metadata
- backup_restore_log: Backup restoration history
- user_pending_manufacturers: Equipment learning system
- equipment_usage_stats: Equipment usage tracking
- equipment_models: User-specific equipment models
- chronograph_data: Measured arrow speed data
- Various change log tables for audit trails

## Code Updates

### UnifiedDatabase Class (`unified_database.py`)
```python
from unified_database import UnifiedDatabase

# Initialize unified database
db = UnifiedDatabase()

# User operations
user = db.get_user_by_email("user@example.com")
db.update_user(user_id, name="New Name")

# Bow setup operations
setups = db.get_user_bow_setups(user_id)
setup_id = db.create_bow_setup(user_id, **setup_data)

# Arrow operations (enhanced)
arrows = db.search_arrows(manufacturer="Easton", spine_min=300)
db.add_arrow_to_setup(setup_id, arrow_id, arrow_length, point_weight)

# Statistics
stats = db.get_database_stats()
```

### API Updates
All API endpoints now use the UnifiedDatabase class:
- `auth.py`: Updated to use UnifiedDatabase for user authentication
- `api.py`: All endpoints updated to use unified database
- Removed all references to separate UserDatabase class

## Benefits of Unified Architecture

1. **Simplified Development**: Single database connection and management
2. **Better Performance**: No cross-database joins or multiple connections
3. **Easier Backups**: Single database file to backup/restore
4. **Improved Data Integrity**: Proper foreign key constraints across all tables
5. **Reduced Complexity**: Single migration system for all schema changes

## Migration Verification

After migration, the unified database contains:
- 262 arrows with 1544 spine specifications
- 38 manufacturers with equipment categories
- 1 user account with profile data
- 2 bow setups with configurations
- 3 setup arrows linking bows to arrows
- All supporting tables for equipment, guides, and tracking

## Rollback Procedure

If needed, migrations can be rolled back:
```bash
# Rollback Migration 024 (restore old bow_setups schema)
python migrations/024_fix_bow_setups_schema.py /path/to/db --rollback

# Rollback Migration 023 (WARNING: removes all user tables)
python migrations/023_consolidate_user_database.py /path/to/db --rollback
```

## Future Considerations

- All new features should use the UnifiedDatabase class
- No new tables should be created in separate databases
- Migration system continues to work with unified database
- Backup systems should backup the single arrow_database.db file