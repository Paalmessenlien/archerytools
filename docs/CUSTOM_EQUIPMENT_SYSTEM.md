# Custom Equipment Management System

This document provides comprehensive documentation for the custom equipment management system that transforms equipment handling from pre-chosen selection to dynamic form-based entry.

## Overview

The custom equipment management system allows users to add and configure archery equipment using dynamic forms instead of selecting from pre-defined equipment lists. This provides flexibility for users to input their specific equipment specifications, manufacturers, and custom configurations.

## Architecture

### Database Schema

#### Arrow Database (`arrow_database.db`)

**equipment_field_standards Table**
```sql
CREATE TABLE equipment_field_standards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL,
    field_name TEXT NOT NULL,
    field_type TEXT NOT NULL CHECK (field_type IN ('text', 'number', 'dropdown', 'multi-select')),
    label TEXT NOT NULL,
    required BOOLEAN DEFAULT FALSE,
    help_text TEXT,
    unit TEXT,
    default_value TEXT,
    validation_rules TEXT,
    field_options TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (category_name, field_name)
);
```

Contains 30 standardized field definitions across 5 equipment categories, defining the form structure and validation rules for each equipment type.

#### User Database (`user_data.db`)

**Enhanced bow_equipment Table**
```sql
-- Original columns maintained for backward compatibility
CREATE TABLE bow_equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bow_setup_id INTEGER NOT NULL,
    equipment_id INTEGER,  -- Now nullable for custom equipment
    installation_date TEXT DEFAULT CURRENT_TIMESTAMP,
    installation_notes TEXT,
    custom_specifications TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- New custom equipment columns (Migration 009)
    manufacturer_name TEXT,
    model_name TEXT,
    category_name TEXT,
    weight_grams REAL,
    description TEXT,
    image_url TEXT,
    is_custom BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
);
```

### API Endpoints

#### Equipment Form Schema API
```
GET /api/equipment/form-schema/<category>
```

**Purpose**: Returns dynamic form field definitions for a specific equipment category.

**Parameters**:
- `category`: Equipment category name (String, Sight, Stabilizer, Arrow Rest, Weight)

**Response Format**:
```json
{
  "category": "String",
  "fields": [
    {
      "name": "material",
      "type": "dropdown",
      "label": "Material",
      "required": true,
      "options": ["BCY-X", "D97", "452X", "8125G", "Dacron", "FastFlight"],
      "order": 1,
      "unit": null,
      "validation": null,
      "help": null
    },
    {
      "name": "strand_count",
      "type": "number",
      "label": "Strand Count",
      "required": false,
      "unit": "strands",
      "validation": {"min": 12, "max": 24},
      "order": 2
    }
  ]
}
```

#### Manufacturer Suggestions API
```
GET /api/equipment/manufacturers/suggest?q=<query>&category=<category>
```

**Purpose**: Provides intelligent manufacturer autocomplete with category filtering.

**Parameters**:
- `q`: Search query string (minimum 2 characters)
- `category`: Equipment category for filtering manufacturers

**Response Format**:
```json
{
  "manufacturers": [
    {
      "name": "Easton",
      "website": null,
      "country": null
    },
    {
      "name": "Easton Archery", 
      "website": null,
      "country": null
    }
  ]
}
```

**Category Mapping**:
- Frontend categories are automatically mapped to database categories:
  - "String" → "strings"
  - "Sight" → "sights"
  - "Stabilizer" → "stabilizers"
  - "Arrow Rest" → "arrow_rests"
  - "Weight" → "weights"

#### Enhanced Equipment CRUD APIs

**Get Bow Equipment**
```
GET /api/bow-setups/<setup_id>/equipment
Authorization: Bearer <token>
```

Returns all equipment for a bow setup, supporting both custom and pre-chosen equipment with unified formatting.

**Add Custom Equipment**
```
POST /api/bow-setups/<setup_id>/equipment
Authorization: Bearer <token>
Content-Type: application/json

{
  "manufacturer_name": "Easton",
  "model_name": "X10 Parallel Pro",
  "category_name": "String",
  "description": "High-performance bowstring",
  "installation_notes": "Installed with 20 twists",
  "specifications": {
    "material": "BCY-X",
    "strand_count": 18,
    "length_inches": 58,
    "serving_material": "BCY Halo",
    "loop_type": "flemish"
  }
}
```

## Equipment Categories

### 1. String Equipment

**Core Fields**:
- **Material** (dropdown, required): BCY-X, D97, 452X, 8125G, Dacron, FastFlight
- **Strand Count** (number): 12-24 strands with validation
- **Length** (number): 40-120 inches
- **Serving Material** (text): Custom serving material specification
- **Loop Type** (dropdown): flemish, endless, loop
- **Bow Weight Range** (text): Compatible bow weight range (e.g., "40-50 lbs")

### 2. Sight Equipment

**Core Fields**:
- **Sight Type** (dropdown, required): multi-pin, single-pin, scope, instinctive
- **Pin Count** (number): 1-7 pins with validation
- **Adjustment Type** (dropdown): micro, standard, toolless
- **Mounting Type** (dropdown): dovetail, weaver, proprietary
- **Light Options** (multi-select): LED, Fiber Optic, Tritium, None
- **Max Range** (number): Maximum effective range in yards

### 3. Stabilizer Equipment

**Core Fields**:
- **Stabilizer Type** (dropdown, required): front, side, back, v-bar, offset
- **Length** (number): 4-36 inches with validation
- **Weight** (number): 1-32 ounces with validation
- **Thread Size** (dropdown): 5/16-24, 1/4-20, 8-32
- **Material** (dropdown): carbon, aluminum, steel
- **Dampening Type** (dropdown): rubber, foam, gel, none

### 4. Arrow Rest Equipment

**Core Fields**:
- **Rest Type** (dropdown, required): drop-away, blade, launcher, shelf, whisker-biscuit
- **Activation Type** (dropdown): cable-driven, limb-driven, magnetic, manual
- **Adjustment Features** (multi-select): Windage, Elevation, Center Shot, Timing
- **Arrow Containment** (dropdown): full, partial, none
- **Mounting Type** (dropdown): berger-hole, plunger, adhesive
- **Arrow Diameter Range** (text): Compatible diameter range (e.g., ".204-.340 inches")

### 5. Weight Equipment

**Core Fields**:
- **Weight** (number, required): 0.5-16 ounces with validation
- **Mounting Location** (dropdown): stabilizer, riser, limb, string
- **Weight Type** (dropdown): stainless-steel, tungsten, brass, lead
- **Thread Size** (dropdown): 5/16-24, 1/4-20, 8-32
- **Shape** (dropdown): cylinder, donut, disc, custom
- **Purpose** (dropdown): balance, dampening, tuning, momentum

## Frontend Components

### CustomEquipmentForm.vue

**Location**: `/frontend/components/CustomEquipmentForm.vue`  
**Size**: 450+ lines  
**Purpose**: Complete form-based equipment entry system

**Key Features**:
- **Dynamic Form Generation**: Automatically generates forms based on API schemas
- **Category Tabs**: Material Design 3 tabs for equipment categories
- **Manufacturer Autocomplete**: Intelligent suggestions with category filtering
- **Form Validation**: Real-time validation with visual feedback
- **Multi-field Types**: Support for text, number, dropdown, and multi-select fields
- **Installation Notes**: Custom installation and configuration notes
- **Responsive Design**: Mobile-first approach with Tailwind CSS

**Props**:
```typescript
interface Props {
  bowSetup: {
    id: number;
    name: string;
    // ... other bow setup properties
  };
}
```

**Events**:
```typescript
interface Events {
  'equipment-added': (equipment: EquipmentItem) => void;
  'cancel': () => void;
}
```

**State Management**:
```typescript
const formData = ref({
  manufacturer_name: '',
  model_name: '',
  category_name: 'String',
  description: '',
  installation_notes: '',
  specifications: {}
});
```

### BowEquipmentManager.vue

**Location**: `/frontend/components/BowEquipmentManager.vue`  
**Purpose**: Equipment list management and integration point

**Key Updates**:
- Integrated `CustomEquipmentForm` instead of `EquipmentSelector`
- Enhanced equipment display for custom equipment
- Support for `manufacturer_name` and custom specifications
- Improved categorization and organization

**Equipment Display**:
```vue
<h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 truncate">
  {{ equipmentItem.manufacturer_name || equipmentItem.manufacturer }} 
  {{ equipmentItem.model_name }}
</h4>
```

### EquipmentEditModal.vue

**Location**: `/frontend/components/EquipmentEditModal.vue`  
**Purpose**: Edit existing equipment configurations

**Key Updates**:
- Updated manufacturer display for custom equipment compatibility
- Enhanced field mapping for new schema structure
- Support for editing custom specifications

## Usage Examples

### Adding Custom String Equipment

1. **Open Equipment Manager**: Navigate to bow setup and click "Add Equipment"
2. **Select Category**: Click on "String" tab
3. **Fill Form Fields**:
   - Manufacturer: "Easton" (with autocomplete)
   - Model Name: "X10 String"
   - Material: Select "BCY-X" from dropdown
   - Strand Count: Enter "18"
   - Length: Enter "58" inches
   - Serving Material: "BCY Halo"
   - Loop Type: Select "flemish"
   - Bow Weight Range: "45-55 lbs"
4. **Add Installation Notes**: "Installed with 20 twists, tuned for 50# bow"
5. **Submit**: Click "Add Equipment"

### API Integration Example

```javascript
// Load form schema
const loadFormSchema = async (category) => {
  try {
    const response = await api.get(`/equipment/form-schema/${category}`);
    return response;
  } catch (error) {
    console.error('Failed to load form schema:', error);
  }
};

// Get manufacturer suggestions
const searchManufacturers = async (query, category) => {
  try {
    const response = await api.get(
      `/equipment/manufacturers/suggest?q=${encodeURIComponent(query)}&category=${category}`
    );
    return response.manufacturers || [];
  } catch (error) {
    console.error('Failed to get manufacturer suggestions:', error);
    return [];
  }
};

// Submit custom equipment
const submitEquipment = async (bowSetupId, equipmentData) => {
  try {
    const response = await api.post(`/bow-setups/${bowSetupId}/equipment`, {
      manufacturer_name: equipmentData.manufacturer_name,
      model_name: equipmentData.model_name,
      category_name: equipmentData.category_name,
      description: equipmentData.description,
      installation_notes: equipmentData.installation_notes,
      specifications: equipmentData.specifications
    });
    return response;
  } catch (error) {
    console.error('Failed to add equipment:', error);
    throw error;
  }
};
```

## Database Migrations

### Migration 008: Arrow Database Schema

**File**: `/arrow_scraper/migrations/008_custom_equipment_schema.py`  
**Target**: Arrow database (`arrow_database.db`)  
**Purpose**: Create equipment field standards and update equipment schema

**Key Changes**:
- Creates `equipment_field_standards` table
- Inserts 30 field definitions across 5 categories
- Establishes validation rules and field metadata

### Migration 009: User Database Schema

**File**: `/arrow_scraper/migrations/009_user_custom_equipment_schema.py`  
**Target**: User database (`user_data.db`)  
**Purpose**: Extend bow_equipment table for custom equipment support

**Key Changes**:
- Adds 7 new columns to `bow_equipment` table
- Maintains backward compatibility with existing data
- Updates existing records with proper `is_custom` flags

**Migration Commands**:
```bash
# Check migration status
python run_migrations.py --status

# Apply pending migrations
python run_migrations.py

# Apply specific migration
python run_migrations.py --version 008
```

## Testing and Validation

### API Endpoint Testing

```bash
# Test form schema endpoints
curl -s http://localhost:5000/api/equipment/form-schema/String
curl -s http://localhost:5000/api/equipment/form-schema/Sight
curl -s http://localhost:5000/api/equipment/form-schema/Stabilizer
curl -s "http://localhost:5000/api/equipment/form-schema/Arrow%20Rest"
curl -s http://localhost:5000/api/equipment/form-schema/Weight

# Test manufacturer suggestions
curl -s "http://localhost:5000/api/equipment/manufacturers/suggest?q=eas&category=String"
```

### Database Validation

```python
# Verify equipment_field_standards table
import sqlite3
conn = sqlite3.connect('databases/arrow_database.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM equipment_field_standards')
count = cursor.fetchone()[0]
print(f'Field standards count: {count}')  # Should be 30

# Verify bow_equipment schema
cursor.execute('PRAGMA table_info(bow_equipment)')
columns = cursor.fetchall()
print(f'bow_equipment columns: {len(columns)}')  # Should be 15
```

## Troubleshooting

### Common Issues

**1. Form Schema Returns Empty**
- **Cause**: Database migration not applied or table empty
- **Solution**: Run migrations and verify `equipment_field_standards` table has 30 records

**2. Manufacturer Suggestions Not Working**
- **Cause**: Category name mismatch or missing manufacturer data
- **Solution**: Check category mapping and verify `manufacturers` table has data

**3. Equipment Not Saving**
- **Cause**: Missing authentication or database schema issues
- **Solution**: Verify JWT token and check `bow_equipment` table schema

**4. 500 Internal Server Errors**
- **Cause**: API server not running or database connection issues
- **Solution**: Restart API server and check database paths

### Debug Commands

```bash
# Check API status
curl -s http://localhost:5000/api/health

# Check migration status
python run_migrations.py --status

# View API logs
tail -f api.log

# Test database connection
python -c "
from database_migration_manager import DatabaseMigrationManager
manager = DatabaseMigrationManager('databases/arrow_database.db')
status = manager.get_migration_status()
print(f'Applied: {status[\"applied_count\"]}, Pending: {status[\"pending_count\"]}')
"
```

## Future Enhancements

### Planned Features

1. **Smart Manufacturer Detection**: Fuzzy matching for manufacturer names
2. **Equipment Templates**: Save and reuse common equipment configurations
3. **Equipment Categories**: Expand to include more archery equipment types
4. **Image Upload**: Support for custom equipment images
5. **Equipment Sharing**: Share equipment configurations between users
6. **Compatibility Checking**: Validate equipment compatibility with bow setups

### Extension Points

- **Field Types**: Add new field types (date, color, file upload)
- **Validation Rules**: Enhanced validation with custom regex patterns
- **Localization**: Multi-language support for field labels and options
- **Import/Export**: Bulk equipment data import from CSV/JSON
- **Equipment Database**: Integration with external equipment databases

## Security Considerations

- **Authentication**: All equipment endpoints require valid JWT tokens
- **Authorization**: Users can only access their own bow setups and equipment
- **Input Validation**: All form data validated on both client and server
- **SQL Injection**: Parameterized queries prevent SQL injection attacks
- **XSS Protection**: All user input sanitized before display

## Performance Notes

- **Database Indexing**: Proper indexes on `bow_setup_id` and `category_name`
- **API Caching**: Form schemas cached to reduce database queries
- **Lazy Loading**: Equipment lists loaded on demand
- **Optimistic Updates**: UI updates immediately with server validation

---

This custom equipment management system provides a flexible, user-friendly way to manage archery equipment while maintaining professional data standards and providing comprehensive customization options.