# Chronograph Data System Documentation

## Overview

The Chronograph Data System provides comprehensive integration for storing, managing, and utilizing measured arrow speeds from chronographs. This system enhances arrow performance calculations by prioritizing real measured data over estimated calculations.

## Table of Contents

- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Frontend Components](#frontend-components)
- [Integration Points](#integration-points)
- [Data Flow](#data-flow)
- [Migration System](#migration-system)
- [Usage Examples](#usage-examples)

## Database Schema

### chronograph_data Table

Created by Migration 019, this table stores measured arrow speed data:

```sql
CREATE TABLE chronograph_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setup_id INTEGER NOT NULL,                    -- Links to bow_setups table
    arrow_id INTEGER,                             -- Links to arrows table (optional)
    setup_arrow_id INTEGER,                       -- Links to setup_arrows table (optional)
    measured_speed_fps REAL NOT NULL,             -- Measured speed in FPS
    arrow_weight_grains REAL NOT NULL,            -- Arrow weight during measurement
    temperature_f INTEGER,                        -- Environmental temperature
    humidity_percent INTEGER,                     -- Environmental humidity
    measurement_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    chronograph_model TEXT,                       -- Chronograph device model
    shot_count INTEGER DEFAULT 1,                 -- Number of shots in measurement
    std_deviation REAL,                           -- Standard deviation of shots
    min_speed_fps REAL,                          -- Minimum speed in series
    max_speed_fps REAL,                          -- Maximum speed in series
    verified BOOLEAN DEFAULT 0,                  -- Data verification flag
    notes TEXT,                                  -- Additional notes
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

Performance indexes are automatically created:
- `idx_chronograph_setup_id` - Fast lookup by bow setup
- `idx_chronograph_arrow_id` - Fast lookup by arrow
- `idx_chronograph_setup_arrow_id` - Fast lookup by setup arrow
- `idx_chronograph_verified` - Filter verified data
- `idx_chronograph_date` - Sort by measurement date

### Foreign Key Relationships

- `setup_id` → `bow_setups(id)` ON DELETE CASCADE
- `arrow_id` → `arrows(id)` ON DELETE SET NULL  
- `setup_arrow_id` → `setup_arrows(id)` ON DELETE CASCADE

## API Endpoints

### Create Chronograph Data
```http
POST /api/chronograph-data
Authorization: Bearer <token>
Content-Type: application/json

{
  "setup_id": 1,
  "setup_arrow_id": 5,
  "measured_speed_fps": 285.3,
  "arrow_weight_grains": 420,
  "temperature_f": 72,
  "humidity_percent": 45,
  "chronograph_model": "Competition Electronics ProChrono",
  "shot_count": 10,
  "std_deviation": 3.2,
  "min_speed_fps": 281.1,
  "max_speed_fps": 289.7,
  "notes": "Indoor range, consistent form"
}
```

**Response:** `201 Created` with created chronograph data object

### Get Chronograph Data for Setup
```http
GET /api/chronograph-data/setup/{setup_id}
Authorization: Bearer <token>
```

**Response:** Array of chronograph data with arrow information:
```json
[
  {
    "id": 1,
    "setup_id": 1,
    "arrow_id": 42,
    "setup_arrow_id": 5,
    "measured_speed_fps": 285.3,
    "arrow_weight_grains": 420,
    "temperature_f": 72,
    "humidity_percent": 45,
    "measurement_date": "2025-08-15T14:30:00Z",
    "chronograph_model": "Competition Electronics ProChrono",
    "shot_count": 10,
    "std_deviation": 3.2,
    "min_speed_fps": 281.1,
    "max_speed_fps": 289.7,
    "verified": 1,
    "notes": "Indoor range, consistent form",
    "arrow_name": "Easton X10",
    "arrow_length": 29.5,
    "point_weight": 120,
    "calculated_spine": 410
  }
]
```

### Update Chronograph Data
```http
PUT /api/chronograph-data/{data_id}
Authorization: Bearer <token>
Content-Type: application/json
```

**Response:** `200 OK` on success, `404 Not Found` if data doesn't exist

### Delete Chronograph Data
```http
DELETE /api/chronograph-data/{data_id}
Authorization: Bearer <token>
```

**Response:** `200 OK` on success, `404 Not Found` if data doesn't exist

### Arrow Speed Estimation (Enhanced)
```http
POST /api/calculator/arrow-speed-estimate
Content-Type: application/json

{
  "bow_ibo_speed": 320,
  "bow_draw_weight": 70,
  "bow_draw_length": 29,
  "bow_type": "compound",
  "arrow_weight_grains": 420,
  "string_material": "dyneema",
  "setup_id": 1,          // Optional: for chronograph data lookup
  "arrow_id": 42          // Optional: for chronograph data lookup
}
```

**Response with Chronograph Data:**
```json
{
  "estimated_speed_fps": 285.3,
  "calculation_method": "chronograph_data",
  "confidence_percent": 95,
  "chronograph_data": {
    "measured_speed_fps": 287.1,
    "measured_weight_grains": 425,
    "shot_count": 10,
    "std_deviation": 3.2
  },
  "string_material": "dyneema"
}
```

**Response with Estimation:**
```json
{
  "estimated_speed_fps": 282.4,
  "calculation_method": "compound_estimation_with_string_material",
  "confidence_percent": 75,
  "bow_ibo_speed": 320,
  "arrow_weight_grains": 420,
  "string_material": "dyneema",
  "factors": {
    "base_speed_estimate": 276.9,
    "string_modifier": 1.02,
    "string_speed_effect": "+2.0%",
    "bow_type": "compound"
  }
}
```

## Frontend Components

### ChronographDataEntry.vue

**Location:** `frontend/components/ChronographDataEntry.vue`

**Props:**
- `bowSetupId` (Number, required) - Bow setup ID
- `setupArrows` (Array, required) - Array of setup arrows for selection

**Events:**
- `@data-updated` - Emitted when chronograph data is created/updated/deleted
- `@speed-calculated` - Emitted when speed is calculated from chronograph data

**Features:**
- Collapsible data entry form
- Display of existing chronograph measurements
- Edit and delete functionality for existing data
- Real-time arrow weight calculation
- Environmental condition tracking
- Shot statistics (count, std deviation, min/max speeds)

**Usage Example:**
```vue
<template>
  <ChronographDataEntry
    :bow-setup-id="setupData.bow_setup.id"
    :setup-arrows="[setupData.setup_arrow]"
    @data-updated="handleChronographDataUpdate"
    @speed-calculated="handleSpeedCalculated"
  />
</template>

<script setup>
const handleChronographDataUpdate = (data) => {
  console.log('Chronograph data updated:', data)
  // Reload performance calculations
  loadSetupArrowDetails()
}

const handleSpeedCalculated = (speedData) => {
  console.log('Speed calculated:', speedData)
  showNotification(`Speed updated: ${speedData.speed} FPS`, 'success')
}
</script>
```

## Integration Points

### 1. Enhanced Arrow Speed Calculations

The chronograph data system integrates with `calculate_enhanced_arrow_speed_internal()` function:

**Priority Order:**
1. **Chronograph Data** (Highest Priority) - Uses measured speeds directly for exact arrow configurations
2. **IBO + String Material Estimation** - Enhanced calculations with string material modifiers
3. **Basic Calculation** (Fallback) - Simple draw weight based estimation

**Direct Speed Usage (August 2025 Update):**
Chronograph data represents the exact arrow configuration and is used directly without weight adjustments:
```
final_speed = measured_speed  // Direct usage for exact configuration
confidence = min(100, (shot_count * 10) + (85 if std_dev < 5 else 70))
```

**Previous Weight Adjustment (Deprecated):**
The system previously applied weight adjustments, but this was removed in August 2025 based on user feedback that chronograph data should represent the exact arrow configuration being used.

### 2. Performance Calculation Integration

Chronograph data automatically enhances these calculations:
- `add_arrow_to_setup()` - New arrow additions
- `calculate_setup_arrows_performance()` - Bulk performance calculations  
- `calculate_individual_arrow_performance()` - Individual arrow analysis

### 3. String Equipment Integration

Automatic string material detection from bow equipment:
```sql
SELECT specifications FROM bow_equipment 
WHERE setup_id = ? AND category = 'String'
```

If string equipment is configured, the material is used for speed calculations.

## Data Flow

### 1. Data Collection Flow
```
User → ChronographDataEntry Component → API → Database
  ↓
Performance Recalculation → Updated UI
```

### 2. Speed Calculation Flow
```
Speed Request → Check Chronograph Data → Found?
                        ↓                    ↓
                Use Measured Speed       Use Enhanced Estimation
                   (Direct Usage)           ↓
                        ↓              String Material Modifier
                        ↓                    ↓
                Final Speed ← ← ← ← ← ← ← ← ←
```

### 3. Performance Integration Flow
```
Arrow Performance Calculation Request
            ↓
Check for Chronograph Data (setup_id + arrow_id)
            ↓
Enhanced Speed Calculation (chronograph or estimation)
            ↓
Performance Metrics Calculation (FOC, KE, Momentum, etc.)
            ↓
Store Performance Data (JSON in setup_arrows.performance_data)
```

## Migration System

### Migration 019: Add Chronograph Data Table

**File:** `arrow_scraper/migrations/019_add_chronograph_data.py`

### Migration 037: Fix Chronograph Integration

**File:** `arrow_scraper/migrations/037_fix_chronograph_integration.py`

**Migration 019 Creates:**
- `chronograph_data` table with full schema
- Performance indexes for fast queries
- Foreign key relationships with proper cascading

**Migration 037 Fixes:**
- Setup arrow ID mapping consistency
- Chronograph data verification status
- Performance cache clearing for recalculation
- Database indexes for optimized queries

**Rollback Support:**
```bash
python arrow_scraper/migrations/019_add_chronograph_data.py /path/to/database.db --rollback
```

**Automatic Application:**
- Both migrations applied automatically during server startup via migration manager
- Safe to run multiple times (uses `IF NOT EXISTS` and proper checks)

## Usage Examples

### 1. Basic Chronograph Data Entry

```javascript
// Frontend: Add chronograph data
const chronographData = {
  setup_id: 1,
  setup_arrow_id: 5,
  measured_speed_fps: 285.3,
  arrow_weight_grains: 420,
  temperature_f: 72,
  humidity_percent: 45,
  chronograph_model: "Competition Electronics ProChrono",
  shot_count: 10,
  std_deviation: 3.2,
  notes: "Indoor range conditions"
}

const response = await api.post('/chronograph-data', chronographData)
```

### 2. Speed Calculation with Chronograph Priority

```python
# Backend: Enhanced speed calculation
enhanced_speed = calculate_enhanced_arrow_speed_internal(
    bow_ibo_speed=320,
    bow_draw_weight=70,
    bow_draw_length=29,
    bow_type='compound',
    arrow_weight_grains=420,
    string_material='dyneema',
    setup_id=1,        # Enables chronograph lookup
    arrow_id=42        # Specific arrow for chronograph data
)
```

### 3. Performance Calculation Integration

```python
# Automatic chronograph integration in performance calculations
performance_data = calculate_arrow_performance(
    archer_profile=mock_profile, 
    arrow_rec=mock_arrow, 
    estimated_speed=enhanced_speed  # Uses chronograph data when available
)
```

### 4. Frontend Component Integration

```vue
<template>
  <div class="arrow-setup-page">
    <!-- Arrow performance analysis -->
    <ArrowPerformanceAnalysis />
    
    <!-- Chronograph data entry -->
    <ChronographDataEntry
      :bow-setup-id="setupData.bow_setup.id"
      :setup-arrows="[setupData.setup_arrow]"
      @data-updated="reloadPerformance"
    />
  </div>
</template>
```

## Best Practices

### 1. Data Quality
- Always verify shot count ≥ 3 for reliable standard deviation
- Record environmental conditions for consistency
- Use verified chronograph models for accuracy
- Include notes about shooting conditions

### 2. Weight Consistency
- Record exact arrow weight during measurement
- Account for arrow modifications (different points, inserts) 
- Chronograph data represents exact configuration - no weight adjustments applied (August 2025 update)

### 3. Performance Integration
- Let system prioritize chronograph data automatically
- Recalculate performance when new measurements added
- Use confidence percentages to indicate data quality

### 4. Database Management
- Chronograph data cascades with bow setup deletion
- Arrow deletion sets chronograph arrow_id to NULL (preserves data)
- Use setup_arrow_id for specific arrow configuration tracking

## Troubleshooting

### Common Issues

**1. No Chronograph Data Found**
- Check `setup_id` and `arrow_id` parameters
- Verify data exists with `verified = 1`
- Check foreign key relationships

**2. Speed Calculation Fallback**
- System falls back to enhanced estimation if chronograph lookup fails
- Check database connectivity and table existence
- Verify migration 019 has been applied

**3. Direct Speed Usage (Updated)**
- Chronograph data is used directly without weight adjustments (August 2025)
- Verify measured speed is reasonable for arrow configuration
- Ensure chronograph data matches the exact arrow setup being calculated

**4. Component Integration**
- Ensure ChronographDataEntry component receives valid props
- Check API authentication for chronograph endpoints
- Verify setup_arrow_id relationships

### Performance Considerations

**1. Database Queries**
- Indexes optimize chronograph data lookups
- Use `LIMIT 1` for latest measurement queries
- Consider caching for frequently accessed data

**2. Calculation Overhead**
- Chronograph lookup adds minimal overhead (~1ms)
- Enhanced calculations are cached in performance_data
- String equipment lookup cached per calculation

**3. Frontend Responsiveness**
- ChronographDataEntry loads data on mount
- Real-time updates via event emission
- Optimistic UI updates for better UX

This documentation covers the complete chronograph data system implementation, providing both technical reference and practical usage guidance for developers and users.