# String Equipment Integration Documentation

## Overview

The String Equipment Integration system provides comprehensive management of bowstring specifications and their impact on arrow speed calculations. This system enhances the equipment management with string-specific fields and automatically integrates string material data into arrow performance calculations.

## Table of Contents

- [Database Schema Enhancement](#database-schema-enhancement)
- [String Material Fields](#string-material-fields)
- [Speed Calculation Integration](#speed-calculation-integration)
- [Equipment Form Enhancement](#equipment-form-enhancement)
- [API Integration](#api-integration)
- [Frontend Integration](#frontend-integration)
- [Migration System](#migration-system)
- [Usage Examples](#usage-examples)

## Database Schema Enhancement

### Migration 020: Enhanced String Equipment Fields

The system adds comprehensive string equipment fields to the existing `equipment_field_standards` table:

**Migration File:** `arrow_scraper/migrations/020_enhance_string_equipment_fields.py`

**Enhanced Fields Added:**
1. `material` - String material type (primary speed factor)
2. `strand_count` - Number of strands in string
3. `serving_material` - Center and end serving material
4. `string_length` - Actual or AMO length measurement
5. `brace_height` - Distance from grip to string at rest
6. `estimated_shots` - Shot count tracking for string wear
7. `speed_rating` - Categorical speed classification

### String Category Field Schema

```sql
-- Example of material field definition
INSERT INTO equipment_field_standards VALUES (
    'String',                    -- category_name
    'material',                  -- field_name
    'dropdown',                  -- field_type
    'String Material',           -- label
    '',                         -- unit
    1,                          -- required (boolean)
    '{"required": true}',       -- validation_rules (JSON)
    '["Dacron", "FastFlight", "Dyneema", "Vectran", "SK75 Dyneema", "Custom Blend"]',  -- field_options (JSON)
    'Dacron',                   -- default_value
    'String material affects bow speed - Dacron is slowest but most forgiving',  -- help_text
    20                          -- display_order
);
```

## String Material Fields

### 1. Material (Primary Field)
- **Type:** Dropdown selection
- **Required:** Yes
- **Options:** Dacron, FastFlight, Dyneema, Vectran, SK75 Dyneema, Custom Blend
- **Impact:** Direct speed modifier (0.92 to 1.04)
- **Default:** Dacron (most conservative)

### 2. Speed Rating
- **Type:** Dropdown selection  
- **Options:** Slow (Dacron), Standard (FastFlight), Fast (Dyneema), Very Fast (Vectran), Ultra Fast (SK75), Unknown
- **Purpose:** User-friendly speed categorization
- **Integration:** Maps to material-based speed modifiers

### 3. Strand Count
- **Type:** Number input
- **Range:** 8-24 strands (typical)
- **Unit:** strands
- **Purpose:** String construction specification
- **Impact:** Affects durability and consistency

### 4. Serving Material
- **Type:** Dropdown selection
- **Options:** Monofilament, Braided, Halo, BCY 3D, Angel Majesty
- **Purpose:** Center and end serving specification
- **Impact:** Affects nocking point consistency

### 5. String Length
- **Type:** Text input
- **Unit:** inches
- **Format:** Actual measurement or AMO length
- **Purpose:** String specification tracking
- **Examples:** "58.5\"", "AMO 58\"", "58\" AMO"

### 6. Brace Height
- **Type:** Text input
- **Unit:** inches
- **Purpose:** Bow tuning reference
- **Impact:** Affects speed and forgiveness
- **Range:** Typically 6-9 inches

### 7. Estimated Shots
- **Type:** Number input
- **Unit:** shots
- **Purpose:** String wear tracking
- **Range:** 0+ (unlimited)
- **Usage:** String replacement planning

## Speed Calculation Integration

### Automatic Material Detection

The system automatically detects string material from equipment configuration:

```python
def get_string_material_for_setup(setup_id):
    """Get string material from bow equipment configuration"""
    try:
        cursor.execute('''
            SELECT specifications 
            FROM bow_equipment 
            WHERE setup_id = ? AND category = 'String'
            LIMIT 1
        ''', (setup_id,))
        
        string_equipment = cursor.fetchone()
        
        if string_equipment and string_equipment['specifications']:
            spec_data = json.loads(string_equipment['specifications'])
            return spec_data.get('material', 'dacron').lower()
            
    except Exception as e:
        print(f"String material detection error: {e}")
    
    return 'dacron'  # Conservative default
```

### Speed Modifier Application

String materials apply direct speed modifiers to calculated arrow speeds:

| Material | Speed Modifier | Speed Effect |
|----------|----------------|--------------|
| Dacron | 0.92 | -8% (safest) |
| FastFlight | 1.00 | Baseline |
| Dyneema | 1.02 | +2% |
| Vectran | 1.03 | +3% |
| SK75 Dyneema | 1.04 | +4% (fastest) |
| Custom Blend | 1.01 | +1% |

**Calculation Formula:**
```
final_speed = base_calculated_speed × string_modifier
```

### Integration Points

**1. Enhanced Speed Calculation Function**
```python
enhanced_speed = calculate_enhanced_arrow_speed_internal(
    bow_ibo_speed=320,
    bow_draw_weight=70,
    bow_draw_length=29,
    bow_type='compound',
    arrow_weight_grains=420,
    string_material='dyneema',  # Automatically detected
    setup_id=setup_id,
    arrow_id=arrow_id
)
```

**2. Calculator Page Integration**
```javascript
// Frontend automatically detects string equipment
const stringEquipment = await api.get(`/bow-setups/${setupId}/equipment/String`)
const stringMaterial = stringEquipment[0]?.specifications?.material || 'dacron'

const speedResponse = await api.post('/calculator/arrow-speed-estimate', {
    string_material: stringMaterial,
    // ... other parameters
})
```

**3. Performance Calculation Integration**
```python
# Automatic string material detection in performance calculations
string_material = get_string_material_for_setup(setup_id)
enhanced_speed = calculate_enhanced_arrow_speed_internal(
    string_material=string_material,
    # ... other parameters
)
performance_data = calculate_arrow_performance(..., estimated_speed=enhanced_speed)
```

## Equipment Form Enhancement

### Dynamic Form Generation

The string equipment category generates forms with enhanced fields:

**API Endpoint:** `/api/equipment/form-schema/String`

**Response Example:**
```json
{
  "category": "String",
  "fields": [
    {
      "field_name": "material",
      "field_type": "dropdown",
      "label": "String Material", 
      "required": true,
      "field_options": ["Dacron", "FastFlight", "Dyneema", "Vectran", "SK75 Dyneema", "Custom Blend"],
      "default_value": "Dacron",
      "help_text": "String material affects bow speed - Dacron is slowest but most forgiving",
      "display_order": 20
    },
    {
      "field_name": "speed_rating",
      "field_type": "dropdown",
      "label": "Speed Rating",
      "required": false,
      "field_options": ["Slow (Dacron)", "Standard (FastFlight)", "Fast (Dyneema)", "Very Fast (Vectran)", "Ultra Fast (SK75)", "Unknown"],
      "default_value": "Standard (FastFlight)",
      "help_text": "Relative speed category of string material",
      "display_order": 25
    }
    // ... additional fields
  ]
}
```

### Form Validation

**Material Field Validation:**
```json
{
  "validation_rules": {
    "required": true
  }
}
```

**Strand Count Validation:**
```json
{
  "validation_rules": {
    "min": 8,
    "max": 24
  }
}
```

**Shot Count Validation:**
```json
{
  "validation_rules": {
    "min": 0
  }
}
```

## API Integration

### Equipment Form Schema Endpoint

```http
GET /api/equipment/form-schema/String
```

**Response:** Dynamic form schema with string-specific fields

### Equipment Configuration Storage

```http
POST /api/bow-setups/{setup_id}/equipment
Content-Type: application/json

{
  "category": "String",
  "manufacturer": "BCY",
  "model": "Trophy",
  "specifications": {
    "material": "dyneema",
    "strand_count": 12,
    "serving_material": "BCY 3D",
    "string_length": "58.5",
    "brace_height": "7.25",
    "estimated_shots": 1500,
    "speed_rating": "Fast (Dyneema)"
  },
  "installation_notes": "Installed with center serving at 6 inches"
}
```

### Equipment Retrieval for Speed Calculation

```http
GET /api/bow-setups/{setup_id}/equipment/String
```

**Response:** Array of string equipment with specifications

## Frontend Integration

### CustomEquipmentForm.vue Enhancement

The string equipment form automatically includes enhanced fields:

```vue
<template>
  <div v-if="selectedCategory === 'String'" class="string-equipment-form">
    <!-- Material selection (required) -->
    <div class="form-field">
      <label class="required">String Material</label>
      <select v-model="formData.material" required>
        <option value="dacron">Dacron</option>
        <option value="fastflight">FastFlight</option>
        <option value="dyneema">Dyneema</option>
        <option value="vectran">Vectran</option>
        <option value="sk75_dyneema">SK75 Dyneema</option>
        <option value="custom_blend">Custom Blend</option>
      </select>
      <small class="help-text">
        String material affects bow speed - Dacron is slowest but most forgiving
      </small>
    </div>

    <!-- Speed rating (informational) -->
    <div class="form-field">
      <label>Speed Rating</label>
      <select v-model="formData.speed_rating">
        <option value="Slow (Dacron)">Slow (Dacron)</option>
        <option value="Standard (FastFlight)">Standard (FastFlight)</option>
        <option value="Fast (Dyneema)">Fast (Dyneema)</option>
        <option value="Very Fast (Vectran)">Very Fast (Vectran)</option>
        <option value="Ultra Fast (SK75)">Ultra Fast (SK75)</option>
      </select>
    </div>

    <!-- Additional string fields -->
    <!-- strand_count, serving_material, string_length, brace_height, estimated_shots -->
  </div>
</template>
```

### Calculator Page Integration

```vue
<template>
  <div class="calculator-page">
    <div class="speed-estimation">
      <!-- String material automatically detected from bow setup -->
      <div v-if="detectedStringMaterial" class="string-info">
        <i class="fas fa-info-circle"></i>
        Using {{ detectedStringMaterial }} string material for speed calculation
        <span class="speed-effect">({{ getSpeedEffect(detectedStringMaterial) }})</span>
      </div>
    </div>
  </div>
</template>

<script setup>
const getSpeedEffect = (material) => {
  const effects = {
    'dacron': '-8% speed (most forgiving)',
    'fastflight': 'standard speed',
    'dyneema': '+2% speed',
    'vectran': '+3% speed',
    'sk75_dyneema': '+4% speed (fastest)',
    'custom_blend': '+1% speed'
  }
  return effects[material.toLowerCase()] || 'unknown effect'
}
</script>
```

## Migration System

### Migration 020 Application

**Automatic Application:**
- Applied during server startup via migration manager
- Safe to run multiple times (checks for existing fields)
- Updates existing fields if they already exist

**Manual Application:**
```bash
# Apply migration
python arrow_scraper/migrations/020_enhance_string_equipment_fields.py /path/to/user_data.db

# Rollback migration
python arrow_scraper/migrations/020_enhance_string_equipment_fields.py /path/to/user_data.db --rollback
```

**Migration Verification:**
```sql
-- Check if string fields were added
SELECT field_name, label, field_type, required 
FROM equipment_field_standards 
WHERE category_name = 'String' 
ORDER BY display_order;
```

**Expected Results:**
```
field_name        | label               | field_type | required
------------------|---------------------|------------|----------
material          | String Material     | dropdown   | 1
speed_rating      | Speed Rating        | dropdown   | 0
strand_count      | Strand Count        | number     | 0
serving_material  | Serving Material    | dropdown   | 0
string_length     | String Length       | text       | 0
brace_height      | Brace Height        | text       | 0
estimated_shots   | Estimated Shot Count| number     | 0
```

## Usage Examples

### 1. Setting Up String Equipment

```javascript
// Frontend: Configure string equipment
const stringEquipment = {
  category: 'String',
  manufacturer: 'BCY',
  model: 'Trophy',
  specifications: {
    material: 'dyneema',
    speed_rating: 'Fast (Dyneema)',
    strand_count: 12,
    serving_material: 'BCY 3D',
    string_length: '58.5',
    brace_height: '7.25',
    estimated_shots: 1500
  },
  installation_notes: 'Professional installation, center serving 6"'
}

await api.post(`/bow-setups/${setupId}/equipment`, stringEquipment)
```

### 2. Automatic Speed Calculation Enhancement

```python
# Backend: Automatic string material detection
def calculate_arrow_performance_with_string_integration(setup_id, arrow_id):
    # Get string material from equipment
    string_material = get_string_material_for_setup(setup_id)
    
    # Enhanced speed calculation
    enhanced_speed = calculate_enhanced_arrow_speed_internal(
        bow_ibo_speed=320,
        bow_draw_weight=70,
        bow_draw_length=29,
        bow_type='compound',
        arrow_weight_grains=420,
        string_material=string_material,  # Automatically detected
        setup_id=setup_id,
        arrow_id=arrow_id
    )
    
    # Performance calculation with enhanced speed
    return calculate_arrow_performance(
        archer_profile=profile,
        arrow_rec=arrow,
        estimated_speed=enhanced_speed
    )
```

### 3. Frontend Speed Effect Display

```vue
<template>
  <div class="speed-calculation-display">
    <div class="calculation-breakdown">
      <div class="factor">
        <span class="label">Base Speed:</span>
        <span class="value">{{ baseSpeed }} FPS</span>
      </div>
      <div class="factor string-effect">
        <span class="label">String Effect:</span>
        <span class="value">{{ stringEffect }}</span>
        <small class="material">({{ stringMaterial }})</small>
      </div>
      <div class="factor final">
        <span class="label">Final Speed:</span>
        <span class="value">{{ finalSpeed }} FPS</span>
      </div>
    </div>
  </div>
</template>

<script setup>
const stringEffect = computed(() => {
  if (!speedData.value.factors) return 'N/A'
  return speedData.value.factors.string_speed_effect || '+0.0%'
})
</script>
```

## Performance Considerations

### 1. Database Performance
- **String Equipment Lookup:** Single query per setup
- **Field Standards Query:** Cached form schemas
- **Material Detection:** Fast JSON parsing

### 2. Calculation Performance
- **String Modifier:** Simple multiplication (~0.01ms)
- **Material Lookup:** Hash table lookup (~0.001ms)
- **Total Overhead:** Negligible impact

### 3. Caching Strategy
- **Form Schemas:** Cached after first request
- **Equipment Data:** Fresh lookup for accuracy
- **Material Modifiers:** Static constants

## Troubleshooting

### Common Issues

**1. String Material Not Detected**
- Check if string equipment exists: `SELECT * FROM bow_equipment WHERE setup_id = ? AND category = 'String'`
- Verify specifications JSON format: Valid JSON with `material` field
- Confirm material value matches expected options

**2. Speed Calculation Not Using String Material**
- Verify `string_material` parameter passed to calculation function
- Check material mapping in speed modifier dictionary
- Confirm default fallback to 'dacron' working

**3. Form Fields Not Appearing**
- Verify migration 020 applied: Check `equipment_field_standards` table
- Confirm API endpoint returns string fields: `/api/equipment/form-schema/String`
- Check frontend form schema processing

**4. Validation Errors**
- Confirm required field validation: `material` field must be selected
- Check number field ranges: `strand_count` (8-24), `estimated_shots` (≥0)
- Verify dropdown options match database field_options

### Debugging Queries

**1. Check String Equipment Configuration**
```sql
SELECT setup_id, manufacturer, model, specifications, installation_notes
FROM bow_equipment 
WHERE category = 'String' AND setup_id = 1;
```

**2. Verify String Field Standards**
```sql
SELECT field_name, field_type, label, required, field_options, default_value
FROM equipment_field_standards 
WHERE category_name = 'String' 
ORDER BY display_order;
```

**3. Test String Material Detection**
```python
import json
cursor.execute("SELECT specifications FROM bow_equipment WHERE setup_id = 1 AND category = 'String'")
specs = cursor.fetchone()
if specs:
    data = json.loads(specs[0])
    print(f"Detected material: {data.get('material', 'none')}")
```

This documentation provides comprehensive coverage of the string equipment integration system, enabling automatic speed calculation enhancement through string material detection and sophisticated equipment management.