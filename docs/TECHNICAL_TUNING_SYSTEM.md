# Technical Tuning System Documentation

## Overview

The Technical Tuning System allows archers to register and track base tuning configurations for their bow setups. Users can maintain multiple tuning configurations per bow (e.g., "Indoor Setup", "Outdoor Setup"), with one marked as active. All changes are tracked in a dedicated tuning change history.

## Features

### Core Functionality
- **Multiple Configurations**: Create unlimited tuning configurations per bow setup
- **Active Configuration**: Mark one configuration as "active" for quick reference
- **Bow-Type Specific Parameters**: Different parameters shown based on bow type (compound, recurve, traditional, longbow)
- **Change History**: All tuning changes are logged with timestamps
- **Configuration Comparison**: Side-by-side comparison of two configurations
- **Duplicate Configurations**: Quickly create new configs based on existing ones

### Supported Parameters

#### Compound Bow Parameters
- **Basic Measurements**: Brace Height, Axle-to-Axle, Draw Weight (Actual), Nocking Point Height, Cable Guard Position
- **String Setup**: String Material (BCY 452X, BCY X99, etc.)
- **Rest & Plunger**: Rest Centershot, Rest Height
- **Sight Setup**: Peep Height
- **Cam Setup**: Let-off %, Cam Timing (Synced, Advanced, etc.), Cam Lean

#### Recurve Bow Parameters
- **Basic Measurements**: Brace Height, Tiller (Top/Bottom), Nocking Point, Arrow Pass Position
- **String Setup**: String Material, String Strands
- **Rest & Plunger**: Plunger Pressure, Plunger Position
- **Sight Setup**: Clicker Position, Sight Pin Position

#### Traditional/Longbow Parameters
- **Basic Measurements**: Brace Height, Nocking Point
- **String Setup**: String Material, String Strands
- **Rest Setup**: Arrow Pass Position

## Database Schema

### Tables

#### bow_tuning_configs
Main tuning configurations table.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| bow_setup_id | INTEGER | Foreign key to bow_setups |
| user_id | INTEGER | Foreign key to users |
| name | TEXT | Configuration name |
| description | TEXT | Optional description |
| is_active | BOOLEAN | Whether this is the active config |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

#### bow_tuning_values
Flexible key-value parameter storage.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| tuning_config_id | INTEGER | Foreign key to bow_tuning_configs |
| parameter_name | TEXT | Parameter identifier (e.g., "brace_height") |
| parameter_value | TEXT | The value |
| unit | TEXT | Unit of measurement |
| notes | TEXT | Optional notes for this parameter |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

#### tuning_change_log
History tracking for all tuning changes.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| bow_setup_id | INTEGER | Foreign key to bow_setups |
| tuning_config_id | INTEGER | Foreign key to bow_tuning_configs |
| user_id | INTEGER | Foreign key to users |
| change_type | TEXT | Type: config_created, config_updated, config_deleted, config_activated, value_changed |
| parameter_name | TEXT | Which parameter changed (for value_changed) |
| old_value | TEXT | Previous value |
| new_value | TEXT | New value |
| change_description | TEXT | Human-readable description |
| user_note | TEXT | Optional user-provided note |
| created_at | TIMESTAMP | When the change occurred |

## API Endpoints

### List Tuning Configurations
```
GET /api/bow-setups/<bow_setup_id>/tuning-configs
```
Returns all tuning configurations for a bow setup with their values.

### Create Tuning Configuration
```
POST /api/bow-setups/<bow_setup_id>/tuning-configs
Content-Type: application/json

{
  "name": "Competition Setup",
  "description": "Indoor tournament settings",
  "is_active": true,
  "values": {
    "brace_height": { "value": "7.25", "unit": "inches", "notes": "" },
    "axle_to_axle": { "value": "36", "unit": "inches", "notes": "" }
  }
}
```

### Get Single Configuration
```
GET /api/tuning-configs/<config_id>
```

### Update Configuration
```
PUT /api/tuning-configs/<config_id>
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description",
  "values": { ... }
}
```

### Delete Configuration
```
DELETE /api/tuning-configs/<config_id>
```

### Activate Configuration
```
POST /api/tuning-configs/<config_id>/activate
```
Sets this configuration as active and deactivates all others for the same bow setup.

### Duplicate Configuration
```
POST /api/tuning-configs/<config_id>/duplicate
Content-Type: application/json

{
  "name": "Copy of Competition Setup"
}
```

### Get Tuning History
```
GET /api/bow-setups/<bow_setup_id>/tuning-history
```
Returns all tuning change log entries for the bow setup.

## Frontend Components

### BowTuningManager.vue
Main component that displays:
- Tab navigation (Configurations / Tuning History)
- List of configuration cards with expandable details
- Add Configuration button
- Compare Configurations button (when 2+ configs exist)

### TuningConfigModal.vue
Modal for creating/editing tuning configurations:
- Configuration name and description
- "Set as active" checkbox
- Dynamic form fields based on bow type
- Parameter groups (Basic, String, Rest, Sight, Cam)
- Notes field for each parameter

### TuningCompareModal.vue
Side-by-side comparison modal:
- Dropdown selectors for two configurations
- Color-coded differences (green=higher, red=lower, yellow=text difference)
- Shows difference values with arrows (↑/↓)
- Legend explaining the colors

## Usage

### Creating a Configuration
1. Navigate to a bow setup page
2. Expand the "Technical Tuning" accordion
3. Click "Add Configuration" or "Create Configuration"
4. Fill in the name and desired parameters
5. Optionally check "Set as active configuration"
6. Click "Create Configuration"

### Comparing Configurations
1. Create at least 2 tuning configurations
2. Click "Compare Configurations" button
3. Select two configurations from the dropdowns
4. Review the side-by-side comparison

### Viewing History
1. Click the "Tuning History" tab
2. View all changes with timestamps
3. Each entry shows what was changed and when

## Migration

The Technical Tuning System was added in migration 064:
```
arrow_scraper/migrations/064_technical_tuning_system.py
```

To apply the migration:
```bash
cd arrow_scraper
python run_migrations.py
```

## Related Documentation
- [Database Schema](DATABASE_SCHEMA.md)
- [API Endpoints](API_ENDPOINTS.md)
- [Journal and Tuning System](JOURNAL_AND_TUNING_SYSTEM.md)
