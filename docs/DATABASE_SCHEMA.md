# Database Schema Documentation

This document provides comprehensive documentation of the Archery Tools database architecture, including table structures, relationships, and data types.

## Overview

The system uses a dual-database architecture:
- **Arrow Database** (`arrow_database.db`) - Arrow specifications, spine data, components
- **User Database** (`user_data.db`) - User accounts, bow setups, sessions, preferences

## Database Locations

### Development Environment
- Arrow Database: `/home/paal/archerytools/arrow_scraper/databases/arrow_database.db`
- User Database: `/home/paal/archerytools/arrow_scraper/databases/user_data.db`

### Docker Production Environment
- Arrow Database: `/app/databases/arrow_database.db` (Docker volume: `arrowtuner-arrowdata`)
- User Database: `/app/databases/user_data.db` (Docker volume: `arrowtuner-userdata`)

---

## Arrow Database (`arrow_database.db`)

Contains all arrow specifications, components, and manufacturer data. This database is read-only in production and populated from JSON files during deployment.

### Tables

#### `arrows`
Main arrow specifications table containing base arrow information.

```sql
CREATE TABLE arrows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer TEXT NOT NULL,
    model_name TEXT NOT NULL,
    material TEXT,                    -- Normalized: "Carbon", "Carbon / Aluminum", "Aluminum", "Wood"
    description TEXT,
    recommended_use TEXT,            -- "target", "hunting", "field", "3d"
    arrow_type TEXT,                 -- "carbon", "aluminum", "wood", "fiberglass"
    carbon_content REAL,             -- Percentage of carbon content (0-100)
    straightness_tolerance TEXT,     -- e.g., "+/- 0.001", "+/- 0.003"
    weight_tolerance TEXT,           -- e.g., "+/- 1.0 grain", "+/- 2.0 grain"
    price_range TEXT,               -- e.g., "$50-80", "$100-150"
    image_url TEXT,                 -- Primary product image URL
    local_image_path TEXT,          -- Local cached image path
    secondary_images TEXT,          -- JSON array of additional image URLs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    diameter_category TEXT,         -- Classified diameter category
    -- Constraints
    UNIQUE(manufacturer, model_name)
);
```

**Key Fields:**
- `material`: Normalized to standard categories for filtering
- `diameter_category`: Auto-classified based on inner diameter ranges
- `image_url`: CDN or local image URL for display
- `recommended_use`: Archery discipline recommendations

#### `spine_specifications`
Detailed spine specifications for each arrow model. One arrow can have multiple spine options.

```sql
CREATE TABLE spine_specifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arrow_id INTEGER NOT NULL,
    spine TEXT NOT NULL,                -- Spine value (e.g., "400", "500", "60#")
    outer_diameter REAL,               -- Outer diameter in inches
    inner_diameter REAL,               -- Inner diameter in inches
    gpi_weight REAL,                   -- Grains per inch
    length_options TEXT,               -- Available lengths (JSON array)
    wall_thickness REAL,               -- Wall thickness in inches
    insert_weight_range TEXT,          -- Compatible insert weights
    nock_size TEXT,                    -- Nock size compatibility
    notes TEXT,                        -- Additional specifications
    straightness_tolerance TEXT,       -- Specific to this spine
    weight_tolerance TEXT,             -- Weight tolerance for this spine
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE,
    UNIQUE(arrow_id, spine)
);
```

**Key Fields:**
- `spine`: Core specification for arrow matching
- `gpi_weight`: Used for total arrow weight calculations
- `inner_diameter`: Used for automatic diameter classification
- `length_options`: JSON array of available cut lengths

#### `components`
Arrow components (nocks, inserts, points, etc.) with compatibility data.

```sql
CREATE TABLE components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer TEXT NOT NULL,
    model_name TEXT NOT NULL,
    component_type TEXT NOT NULL,      -- "nock", "insert", "point", "fletching"
    description TEXT,
    weight_grains REAL,               -- Component weight in grains
    diameter_compatibility TEXT,       -- Compatible arrow diameters (JSON)
    material TEXT,                    -- Component material
    color_options TEXT,               -- Available colors (JSON)
    price_range TEXT,
    image_url TEXT,
    specifications TEXT,              -- Additional specs (JSON)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    UNIQUE(manufacturer, model_name, component_type)
);
```

#### `component_categories`
Categories for organizing components.

```sql
CREATE TABLE component_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,        -- "Points", "Nocks", "Inserts", "Fletching"
    description TEXT,
    display_order INTEGER DEFAULT 0
);
```

---

## User Database (`user_data.db`)

Contains all user-specific data including accounts, bow configurations, and session tracking.

### Tables

#### `users`
User account information and preferences.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    google_id TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    profile_picture_url TEXT,
    is_admin BOOLEAN DEFAULT 0,       -- Admin privileges flag
    draw_length REAL DEFAULT 28.0,    -- User's draw length
    skill_level TEXT DEFAULT 'intermediate',  -- "beginner", "intermediate", "advanced", "expert"
    shooting_style TEXT DEFAULT 'target',     -- "target", "hunting", "field", "3d"
    preferred_manufacturers TEXT,      -- JSON array of preferred manufacturers
    notes TEXT,                       -- User notes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Fields:**
- `google_id`: Unique identifier from Google OAuth
- `is_admin`: Automatic admin privileges for messenlien@gmail.com
- `draw_length`: Used as default in bow configurations
- `preferred_manufacturers`: JSON array for filtering preferences

#### `bow_setups`
User's bow configurations and equipment setups.

```sql
CREATE TABLE bow_setups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,               -- User-defined setup name
    bow_type TEXT NOT NULL,           -- "compound", "recurve", "traditional", "longbow"
    draw_weight REAL NOT NULL,        -- Bow's draw weight in pounds
    arrow_length REAL,               -- Arrow length in inches
    point_weight REAL,               -- Point weight in grains
    insert_weight REAL,              -- Insert weight in grains
    nock_weight REAL,                -- Nock weight in grains
    fletching_weight REAL,           -- Total fletching weight in grains
    description TEXT,
    bow_usage TEXT,                  -- JSON array: ["target", "hunting", "field", "3d"]
    
    -- Compound Bow Specific
    compound_brand TEXT,
    compound_model TEXT,
    ibo_speed INTEGER,               -- IBO speed rating
    
    -- Recurve/Traditional Specific
    riser_brand TEXT,
    riser_model TEXT,
    riser_length TEXT,               -- "23\", "25\", etc.
    limb_brand TEXT,
    limb_model TEXT,
    limb_length TEXT,                -- "short", "medium", "long"
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

**Key Fields:**
- `bow_type`: Determines calculation methods and UI display
- `draw_weight`: Core value for spine calculations
- `ibo_speed`: Used for compound bow performance calculations
- `bow_usage`: JSON array for multi-purpose setups

#### `setup_arrows`
Junction table linking bow setups to selected arrows with configuration.

```sql
CREATE TABLE setup_arrows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setup_id INTEGER NOT NULL,
    arrow_id INTEGER NOT NULL,        -- References arrows.id
    arrow_length REAL,               -- Specific length for this setup
    point_weight REAL,               -- Specific point weight for this setup
    calculated_spine TEXT,           -- Calculated spine value
    compatibility_score REAL,       -- Match confidence (0-100)
    nock_weight REAL,               -- Component weights for this configuration
    insert_weight REAL,
    bushing_weight REAL,
    fletching_weight REAL,
    notes TEXT,                     -- User notes for this arrow selection
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
    FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE,
    UNIQUE(setup_id, arrow_id)
);
```

#### `tuning_sessions`
Archery tuning session tracking for progress monitoring.

```sql
CREATE TABLE tuning_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    setup_id INTEGER,               -- Optional: linked bow setup
    session_name TEXT,
    bow_config TEXT NOT NULL,       -- JSON: complete bow configuration
    recommended_spine TEXT,         -- Spine recommendation for session
    recommended_arrows TEXT,        -- JSON: recommended arrows list
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE SET NULL
);
```

#### `guide_sessions`
Interactive tuning guide session tracking.

```sql
CREATE TABLE guide_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    guide_type TEXT NOT NULL,        -- "paper_tuning", "sight_setup", "center_shot"
    status TEXT DEFAULT 'active',   -- "active", "paused", "completed"
    current_step INTEGER DEFAULT 0, -- Current step number
    total_steps INTEGER,            -- Total steps in guide
    session_data TEXT,              -- JSON: session progress data
    bow_config TEXT,                -- JSON: bow configuration for session
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

#### `backup_metadata`
Admin backup system tracking.

```sql
CREATE TABLE backup_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backup_name TEXT NOT NULL,
    file_path TEXT,                 -- Local file path
    cdn_url TEXT,                   -- CDN storage URL
    file_size INTEGER,              -- File size in bytes
    backup_type TEXT DEFAULT 'full', -- "full", "user_only", "arrow_only"
    include_arrow_db BOOLEAN DEFAULT 1,
    include_user_db BOOLEAN DEFAULT 1,
    arrow_db_stats TEXT,            -- JSON: arrow database statistics
    user_db_stats TEXT,             -- JSON: user database statistics
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,             -- Admin user ID
    -- Constraints
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
);
```

---

## Data Relationships

### Arrow → Spine Specifications (1:Many)
- One arrow model can have multiple spine options
- Each spine has unique diameter and weight specifications

### User → Bow Setups (1:Many)
- Users can have multiple bow configurations
- Each setup is tied to specific equipment specifications

### Bow Setup → Selected Arrows (Many:Many via setup_arrows)
- Users can select multiple arrows for each bow setup
- Junction table tracks specific configuration for each selection

### User → Sessions (1:Many)
- Users can have multiple tuning and guide sessions
- Sessions can optionally link to specific bow setups

---

## Indexes and Performance

### Arrow Database Indexes
```sql
CREATE INDEX idx_arrows_manufacturer ON arrows(manufacturer);
CREATE INDEX idx_arrows_material ON arrows(material);
CREATE INDEX idx_arrows_diameter_category ON arrows(diameter_category);
CREATE INDEX idx_spine_specs_arrow_id ON spine_specifications(arrow_id);
CREATE INDEX idx_spine_specs_spine ON spine_specifications(spine);
```

### User Database Indexes
```sql
CREATE INDEX idx_bow_setups_user_id ON bow_setups(user_id);
CREATE INDEX idx_setup_arrows_setup_id ON setup_arrows(setup_id);
CREATE INDEX idx_setup_arrows_arrow_id ON setup_arrows(arrow_id);
CREATE INDEX idx_sessions_user_id ON tuning_sessions(user_id);
```

---

## Data Types and Formats

### JSON Fields
- `bow_usage`: `["target", "hunting", "field"]`
- `length_options`: `["28", "29", "30", "31", "32"]`
- `preferred_manufacturers`: `["Easton", "Gold Tip", "Victory"]`
- `bow_config`: Complete bow configuration object
- `session_data`: Session progress and step data

### Normalized Values
- **Materials**: `"Carbon"`, `"Carbon / Aluminum"`, `"Aluminum"`, `"Wood"`
- **Bow Types**: `"compound"`, `"recurve"`, `"traditional"`, `"longbow"`
- **Diameter Categories**: `"Ultra-thin"`, `"Thin"`, `"Small hunting"`, `"Standard target"`, `"Standard hunting"`, `"Large hunting"`, `"Heavy hunting"`

### Measurement Units
- **Lengths**: Inches (REAL)
- **Weights**: Grains (REAL)
- **Diameters**: Inches (REAL)
- **Spine**: String values (accommodate both numeric and traditional formats)

---

## Migration and Backup

### Migration Scripts
- `migrate_diameter_categories.py` - Adds diameter classification
- `migrate_spine_specifications.py` - Updates spine table schema

### Backup System
- Full database backups via admin panel
- Selective backup (arrow-only or user-only)
- CDN storage integration for production backups
- Restore functionality with verification

This schema supports the complete archery tools workflow from arrow browsing to personalized recommendations and tuning session tracking.