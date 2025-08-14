# Migration Reference Guide

This document provides a complete reference for all database migrations in the ArrowTuner platform, making it easy to understand existing changes and create new migrations.

## Migration Overview

The ArrowTuner platform uses a sophisticated migration system with 16 migrations (as of August 2025) that handle both arrow database and user database schema evolution. Each migration is numbered sequentially and includes dependency management.

## Complete Migration Reference

### Migration 001: Spine Calculator Tables
**File:** `001_spine_calculator_tables.py`  
**Database:** Arrow Database  
**Purpose:** Foundational spine calculation system  

**What it creates:**
```sql
-- Core calculation parameters
CREATE TABLE calculation_parameters (
    id INTEGER PRIMARY KEY,
    parameter_name TEXT UNIQUE,
    parameter_value REAL,
    description TEXT
);

-- Arrow material properties for calculations
CREATE TABLE arrow_material_properties (
    id INTEGER PRIMARY KEY,
    material_type TEXT,
    elastic_modulus REAL,
    density REAL,
    description TEXT
);

-- Manufacturer-specific spine charts
CREATE TABLE manufacturer_spine_charts (
    id INTEGER PRIMARY KEY,
    manufacturer TEXT,
    chart_name TEXT,
    spine_value INTEGER,
    shaft_diameter REAL,
    weight_per_inch REAL
);
```

**Why needed:** Provides the mathematical foundation for professional spine calculations used throughout the platform.

---

### Migration 002: User Database Schema  
**File:** `002_user_database_schema.py`  
**Database:** User Database  
**Purpose:** Core user management and authentication system  

**What it creates:**
```sql
-- User accounts and authentication
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    google_id TEXT UNIQUE,
    is_admin BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- User bow setups/configurations
CREATE TABLE bow_setups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    bow_type TEXT NOT NULL,
    draw_weight REAL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- User arrow assignments to setups
CREATE TABLE setup_arrows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bow_setup_id INTEGER NOT NULL,
    arrow_id INTEGER NOT NULL,
    notes TEXT,
    is_primary BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
);
```

**Why needed:** Separates user data from arrow data, enabling personalized configurations while maintaining data integrity.

---

### Migration 003: JSON Data Import
**File:** `003_json_data_import.py`  
**Database:** Arrow Database  
**Purpose:** Import scraped arrow data from JSON files  

**What it does:**
- Imports arrow specifications from `data/processed/*.json` files
- Handles manufacturer data normalization
- Processes spine specifications with GPI weights and diameters
- Creates relationships between arrows and spine options

**Data flow:**
```
JSON Files (easton_arrows.json, goldtip_arrows.json, etc.)
    ↓
Arrow specifications with spine data
    ↓ 
Database tables (arrows, spine_specifications)
```

**Why needed:** Bridges the gap between web scraping output and database storage, ensuring consistent data import.

---

### Migration 004: Bow Equipment Schema
**File:** `004_bow_equipment_schema.py`  
**Database:** Arrow Database  
**Purpose:** Equipment catalog and categorization system  

**What it creates:**
```sql
-- Equipment categories (String, Sight, Rest, etc.)
CREATE TABLE equipment_categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    icon_class TEXT
);

-- Equipment field definitions for forms
CREATE TABLE equipment_field_standards (
    id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    field_type TEXT NOT NULL, -- 'text', 'number', 'dropdown', 'multiselect'
    is_required BOOLEAN DEFAULT 0,
    dropdown_options TEXT, -- JSON array for dropdown/multiselect
    validation_rules TEXT, -- JSON object
    help_text TEXT,
    FOREIGN KEY (category_id) REFERENCES equipment_categories (id)
);
```

**Why needed:** Provides the foundation for dynamic equipment forms and professional equipment management.

---

### Migration 005: Unified Manufacturers
**File:** `005_unified_manufacturers.py`  
**Database:** Arrow Database  
**Purpose:** Standardize manufacturer data across all equipment types  

**What it does:**
- Creates unified manufacturer table
- Normalizes manufacturer names (e.g., "Hoyt Archery" → "Hoyt")
- Links equipment to standardized manufacturers
- Handles manufacturer aliases and variations

**Before/After:**
```
Before: Equipment has text manufacturer field
After:  Equipment links to manufacturers table with standardized names
```

**Why needed:** Ensures consistent manufacturer data and enables better filtering and organization.

---

### Migration 006: Bow Limb Manufacturers
**File:** `006_bow_limb_manufacturers.py`  
**Database:** Arrow Database  
**Purpose:** Expand manufacturer support for recurve and traditional bows  

**What it adds:**
- Recurve riser manufacturers (Win&Win, Uukha, Bernardini, etc.)
- Recurve limb manufacturers (Border, SF Archery, Fivics, etc.)
- Traditional bow manufacturers (Black Widow, Bear Archery, etc.)
- Longbow makers (Howard Hill, Great Plains, etc.)

**Why needed:** Supports comprehensive bow type management beyond just compound bows.

---

### Migration 007: User Bow Equipment Table
**File:** `007_user_bow_equipment_table.py`  
**Database:** User Database  
**Purpose:** User-specific equipment assignments and configurations  

**What it creates:**
```sql
CREATE TABLE bow_equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bow_setup_id INTEGER NOT NULL,
    category TEXT NOT NULL, -- 'String', 'Sight', 'Rest', etc.
    manufacturer_name TEXT,
    model_name TEXT,
    specifications TEXT, -- JSON object with category-specific fields
    installation_notes TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
);
```

**Why needed:** Allows users to configure equipment on their bow setups with custom specifications.

---

### Migration 008: Custom Equipment Schema
**File:** `008_custom_equipment_schema.py`  
**Database:** Arrow Database  
**Purpose:** Enhanced equipment field definitions and validation  

**What it adds:**
- 30+ standardized equipment fields across 5 categories
- Validation rules and help text for each field
- Professional equipment specifications (draw length, brace height, etc.)
- Enhanced form generation capabilities

**Field examples:**
```json
{
  "String": ["material", "strand_count", "serving_material", "length"],
  "Sight": ["sight_type", "pin_count", "aperture_size", "adjustment_range"],
  "Stabilizer": ["length", "weight", "material", "vibration_dampening"]
}
```

**Why needed:** Provides professional-grade equipment specification tracking.

---

### Migration 009: User Custom Equipment Schema  
**File:** `009_user_custom_equipment_schema.py`  
**Database:** User Database  
**Purpose:** User equipment table enhancements for custom specifications  

**What it adds:**
- Custom specification storage as JSON
- Equipment metadata fields
- Installation tracking and notes
- Enhanced relationship management

**Why needed:** Enables users to store detailed equipment configurations with custom specifications.

---

### Migration 010: Complete Equipment Categories
**File:** `010_complete_equipment_categories.py`  
**Database:** Arrow Database  
**Purpose:** Expand to 8 complete equipment categories  

**Categories added:**
1. **String** - Bowstrings and serving materials
2. **Sight** - Bow sights and scopes  
3. **Scope** - Magnification and targeting scopes
4. **Stabilizer** - Stabilization and vibration damping
5. **Arrow Rest** - Arrow rests and launchers
6. **Plunger** - Plunger buttons and tuning aids
7. **Weight** - Additional weights and balance accessories
8. **Other** - Miscellaneous equipment

**Why needed:** Comprehensive equipment categorization for professional archery setups.

---

### Migration 011: Enhanced Manufacturer Workflow
**File:** `011_enhanced_manufacturer_workflow.py`  
**Database:** Arrow Database  
**Purpose:** Smart manufacturer detection and linking system  

**What it adds:**
- Fuzzy manufacturer name matching
- Auto-learning manufacturer suggestions
- Manufacturer linking and standardization
- Cross-category manufacturer support

**Features:**
```python
# Smart matching examples
"hoyt" → "Hoyt Archery"
"w&w" → "Win&Win"
"bear archery" → "Bear Archery"
```

**Why needed:** Improves user experience with intelligent manufacturer suggestions and data consistency.

---

### Migration 012: Fix Pending Manufacturers Schema
**File:** `012_fix_pending_manufacturers_schema.py`  
**Database:** Arrow Database  
**Purpose:** Bug fixes for manufacturer workflow  

**What it fixes:**
- Pending manufacturer table schema issues
- Foreign key constraint problems
- Manufacturer suggestion algorithm improvements
- Data consistency issues

**Why needed:** Resolves production issues with manufacturer detection and linking.

---

### Migration 013: Equipment Change Logging ⭐
**File:** `013_equipment_change_logging.py`  
**Database:** User Database  
**Purpose:** Comprehensive change tracking for equipment  

**What it creates:**
```sql
CREATE TABLE change_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bow_setup_id INTEGER NOT NULL,
    change_source TEXT NOT NULL, -- 'equipment', 'arrow', 'setup'
    change_type TEXT NOT NULL,   -- 'add', 'remove', 'modify'
    item_id INTEGER,             -- References equipment/arrow ID
    field_name TEXT,             -- Specific field that changed
    old_value TEXT,              -- Previous value
    new_value TEXT,              -- New value
    change_description TEXT NOT NULL,
    change_reason TEXT,          -- User-provided reason/note
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

**Why needed:** Provides complete audit trail for all equipment changes, enabling undo functionality and change tracking.

---

### Migration 014: Arrow Change Logging ⭐
**File:** `014_arrow_change_logging.py`  
**Database:** User Database  
**Purpose:** Change tracking for arrow assignments  

**What it adds:**
- Arrow addition/removal logging
- Arrow specification change tracking
- Integration with existing change log system
- User note support for arrow changes

**Change types tracked:**
- `arrow_added` - Arrow assigned to setup
- `arrow_removed` - Arrow removed from setup  
- `arrow_modified` - Arrow specifications changed
- `specifications_changed` - Arrow specs updated

**Why needed:** Completes the change tracking system to include arrow management alongside equipment changes.

---

### Migration 015: Remove Setup Arrows UNIQUE Constraint ⭐
**File:** `015_remove_setup_arrows_unique_constraint.py`  
**Database:** User Database  
**Purpose:** Fix production compatibility issue  

**What it fixes:**
```sql
-- Problem: UNIQUE constraint prevented multiple arrows of same type
-- Solution: Remove constraint, allow duplicate arrow assignments
DROP INDEX IF EXISTS idx_setup_arrows_unique;
```

**Scenarios enabled:**
- Multiple arrows with different spine weights
- Backup arrows of the same model
- Testing different configurations of same arrow

**Why needed:** Production environments encountered issues with the unique constraint preventing legitimate arrow assignments.

---

### Migration 016: Equipment Soft Delete Enhancement ⭐
**File:** `016_equipment_soft_delete_enhancement.py`  
**Database:** User Database  
**Purpose:** Non-destructive equipment deletion with restore capability  

**What it adds:**
```sql
-- Add soft delete tracking fields
ALTER TABLE bow_equipment ADD COLUMN deleted_at TIMESTAMP;
ALTER TABLE bow_equipment ADD COLUMN deleted_by INTEGER;

-- Performance index for deleted equipment queries
CREATE INDEX idx_bow_equipment_deleted ON bow_equipment (is_active, deleted_at DESC);

-- Update existing deleted equipment with timestamps
UPDATE bow_equipment SET deleted_at = CURRENT_TIMESTAMP WHERE is_active = 0;
```

**Features enabled:**
- **Soft Delete** - Equipment marked as deleted but preserved in database
- **Restore Capability** - Deleted equipment can be fully restored
- **User Tracking** - System tracks who deleted equipment and when
- **Change Integration** - All deletions/restorations logged in change history
- **Performance** - Indexed queries for deleted equipment management

**API Endpoints:**
- `DELETE /api/bow-setups/{id}/equipment/{id}` - Soft delete equipment
- `POST /api/bow-setups/{id}/equipment/{id}/restore` - Restore deleted equipment  
- `GET /api/bow-setups/{id}/equipment/deleted` - List deleted equipment

**Why needed:** Provides safety net for equipment management, preventing accidental data loss while maintaining clean user interfaces.

---

## Migration Dependencies

Understanding the dependency chain helps when creating new migrations:

```
001 (Spine Calculator) ← Independent foundation
├── 002 (User Database) ← Independent foundation  
├── 003 (JSON Import) ← Depends on 001
├── 004 (Equipment Schema) ← Depends on 001
├── 005 (Manufacturers) ← Depends on 004
├── 006 (Bow Manufacturers) ← Depends on 005
├── 007 (User Equipment) ← Depends on 002, 004
├── 008 (Custom Equipment) ← Depends on 007
├── 009 (User Custom) ← Depends on 008
├── 010 (Categories) ← Depends on 009
├── 011 (Enhanced Workflow) ← Depends on 010
├── 012 (Schema Fixes) ← Depends on 011
├── 013 (Equipment Logging) ← Depends on 007
├── 014 (Arrow Logging) ← Depends on 013
├── 015 (Constraint Fix) ← Depends on 007
└── 016 (Soft Delete) ← Depends on 013, 015
```

## Creating New Migrations

### Step 1: Determine Next Number
```bash
cd arrow_scraper
ls migrations/ | grep -E '^[0-9]{3}_' | sort | tail -1
# Result: 016_equipment_soft_delete_enhancement.py
# Next: 017
```

### Step 2: Choose Target Database
- **Arrow Database** - For arrow specs, equipment catalog, manufacturer data
- **User Database** - For user accounts, bow setups, user equipment, change logs

### Step 3: Migration Template

```python
#!/usr/bin/env python3
"""
Migration 017: [Your Feature Name]

[Detailed description of what this migration accomplishes]
- What tables/fields are added
- What data is migrated
- Why this change is needed
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

def get_database_path():
    """Get database path using same logic as other migrations"""
    possible_paths = [
        Path("/app/databases/[arrow_database.db|user_data.db]"),
        Path(__file__).parent.parent / "databases" / "[arrow_database.db|user_data.db]",
        # Add more paths as needed
    ]
    
    for p in possible_paths:
        if p.exists():
            return str(p)
    
    return str(possible_paths[0])  # Default for new installs

def up(db_path: str = None) -> bool:
    """Apply the migration"""
    if db_path is None:
        db_path = get_database_path()
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("🔄 Running Migration 017: [Your Feature Name]")
        print(f"📁 Database path: {db_path}")
        
        # Check if migration already applied
        # Your check logic here
        
        # Apply your changes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS your_new_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                -- your columns here
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_your_table_field 
            ON your_new_table (your_field)
        """)
        
        conn.commit()
        print("🎉 Migration 017 completed successfully!")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Migration 017 failed: {e}")
        conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def down(db_path: str = None) -> bool:
    """Rollback the migration (optional but recommended)"""
    # Implementation for rollback
    pass

def run_migration():
    """Execute the migration"""
    return up()

if __name__ == "__main__":
    run_migration()
```

### Step 4: Test Migration
```bash
# Test discovery
python -c "
from database_migration_manager import DatabaseMigrationManager
manager = DatabaseMigrationManager()
pending = manager.get_pending_migrations()
print([m.version for m in pending])
"

# Test application
python migrations/017_your_migration.py
```

## Best Practices Summary

### ✅ **Do:**
1. **Use sequential numbering** (001, 002, 003...)
2. **Include descriptive names** that explain the purpose
3. **Add comprehensive comments** explaining what and why
4. **Test rollback procedures** before production
5. **Use `IF NOT EXISTS`** for table creation
6. **Add proper indexes** for performance
7. **Handle existing data** gracefully
8. **Follow established patterns** from existing migrations

### ❌ **Don't:**
1. **Skip migration numbers** or reuse existing numbers
2. **Make destructive changes** without backup plans  
3. **Ignore foreign key constraints** and relationships
4. **Assume clean database state** - handle existing data
5. **Hardcode paths** - use path resolution functions
6. **Skip error handling** - always use try/catch blocks

## Migration System Architecture

The complete system includes:

- **`DatabaseMigrationManager`** - Core orchestration
- **`run_migrations.py`** - Command-line interface
- **`comprehensive-migration-runner.sh`** - Production automation
- **Admin Panel** - Web interface at `/admin` → Maintenance
- **Startup Integration** - Automatic execution on deployment

This documentation should be updated whenever new migrations are added to maintain a complete reference for the team.