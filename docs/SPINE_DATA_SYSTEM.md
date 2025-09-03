# Spine Data System Documentation

## Overview

The Archery Tools platform includes a comprehensive spine calculation data system that provides multiple spine calculation methods, material properties, and tuning guidance. This system offers Universal Formula (default), German Industry Standard, and chart-based calculations with professional-grade data and admin-configurable parameters.

**🆕 Enhanced Features (September 2025):**
- **Material-Aware System Defaults**: Intelligent chart selection based on bow type AND arrow material preference
- **Complete Bow Type Coverage**: System defaults for compound, recurve, longbow, and traditional bows
- **Shooting Style Integration**: Dynamic spine adjustments based on archery discipline
- **Admin Management Interface**: Web-based system default configuration with visual indicators
- **Frontend Visual Indicators**: Comprehensive visual feedback showing system defaults and chart sources
- **Chart Source Display**: Real-time display of current spine chart in use on calculator page

For detailed information on the new system defaults functionality, see: **[Spine Chart System Defaults Documentation](SPINE_CHART_SYSTEM_DEFAULTS.md)**

For complete implementation details including visual enhancements, see: **[System Defaults Implementation Guide](SPINE_CHART_SYSTEM_DEFAULTS_IMPLEMENTATION.md)**

## Calculation Methods

### Universal Formula (Default)
- **Purpose**: Generic spine calculation compatible with all manufacturers
- **Formula**: `12.5 × draw_weight + bow_type_adjustments + length_adjustments`
- **Usage**: Default method for all bow types and manufacturers
- **Advantages**: Consistent, well-tested, works across all equipment

### German Industry Standard
- **Purpose**: Specialized formulas optimized for recurve and traditional bows
- **Formulas**: 
  - Recurve/Traditional: `1100 - (draw_weight × 10)`
  - Compound: `draw_weight × 12.5`
- **Usage**: Alternative method for European-style calculations
- **Advantages**: Optimized for traditional archery disciplines

### Chart-Based Calculation
- **Purpose**: Use manufacturer-specific spine charts for precise recommendations
- **Data Source**: Manufacturer spine chart database with real chart data
- **Usage**: When specific manufacturer charts are available
- **Advantages**: Most accurate for specific manufacturer/model combinations

## System Architecture

### Database Schema

The spine data system consists of 7 database tables that store calculation parameters, material properties, and tuning guidance:

#### Core Tables

1. **`calculation_parameters`** - Admin-configurable spine calculation parameters
   - `parameter_group` - Grouping (base_calculation, bow_adjustments, safety_factors, material_factors)
   - `parameter_name` - Name of the parameter
   - `parameter_value` - Numeric value
   - `parameter_unit` - Unit of measurement
   - `description` - Human-readable description
   - `updated_at` - Last modification timestamp
   - `last_modified_by` - User ID who last modified

2. **`arrow_material_properties`** - Arrow material specifications and characteristics
   - `material_name` - Material identifier (carbon, aluminum, wood, etc.)
   - `density` - Material density factor
   - `elasticity_modulus` - Elasticity coefficient
   - `strength_factor` - Structural strength multiplier
   - `spine_adjustment_factor` - Spine calculation adjustment factor
   - `temperature_coefficient` - Temperature sensitivity
   - `humidity_resistance_rating` - Moisture resistance (1-10 scale)
   - `description` - Material description
   - `typical_use` - Recommended applications

3. **`manufacturer_spine_charts`** - Brand-specific spine recommendations
   - `manufacturer` - Arrow manufacturer name
   - `bow_type` - Bow type (compound, recurve, traditional, longbow)
   - `draw_weight_min/max` - Draw weight range in pounds
   - `arrow_length_min/max` - Arrow length range in inches
   - `recommended_spine` - Recommended spine value
   - `point_weight_range` - Point weight range description
   - `confidence_rating` - Recommendation confidence (0-100)
   - `notes` - Additional guidance

#### Supporting Tables

4. **`spine_calculation_data`** - Raw calculation formulas and coefficients
   - Stores mathematical formulas and base calculation data
   - Used by the spine service for advanced calculations

5. **`flight_problem_diagnostics`** - Arrow flight issue troubleshooting
   - `problem_category` - Type of flight issue
   - `problem_name` - Specific problem name
   - `symptoms` - Observable symptoms
   - `root_causes` - Likely causes
   - `solutions` - Recommended fixes
   - `prevention_tips` - How to avoid the issue
   - `difficulty_level` - Complexity (beginner, intermediate, advanced)
   - `equipment_needed` - Required tools
   - `safety_warnings` - Safety considerations

6. **`tuning_methodologies`** - Step-by-step tuning procedures
   - `method_name` - Tuning method name
   - `method_category` - Category (sight, rest, form, etc.)
   - `bow_types_applicable` - Compatible bow types
   - `skill_level_required` - Required skill level
   - `time_estimate_minutes` - Estimated completion time
   - `equipment_needed` - Required equipment
   - `step_by_step_guide` - Detailed instructions
   - `expected_outcomes` - What to expect
   - `troubleshooting_tips` - Common issues and fixes
   - `safety_considerations` - Safety notes

7. **`component_spine_effects`** - How components affect spine calculations
   - `component_type` - Type (insert, nock, fletching, etc.)
   - `component_name` - Specific component name
   - `weight_grams` - Component weight
   - `spine_effect_factor` - How it affects spine calculations
   - `foc_contribution` - Front-of-center impact
   - `balance_point_shift` - Balance point change
   - `aerodynamic_impact` - Flight characteristics impact
   - `compatibility_notes` - Compatibility information
   - `manufacturer` - Component manufacturer
   - `typical_use` - Recommended applications

### File Structure

```
arrow_scraper/
├── spine_service.py              # Main spine calculation service
├── migrate_spine_calculation_data.py  # Database migration script
├── import_spine_calculator_data.py    # Data import script
├── spine_data_sample.json        # Sample spine calculation data
└── databases/
    └── arrow_database.db         # Contains spine calculation tables
```

## Usage in the Application

### 1. Admin Panel Integration

**Location**: `/admin/spine-data` (frontend/pages/admin/spine-data.vue)

**Features**:
- **Calculation Parameters Tab**: Admins can modify spine calculation coefficients
- **Material Properties Tab**: Manage arrow material characteristics
- **Testing Tab**: Test spine calculations with different parameters

**API Endpoints**:
```
GET    /api/admin/spine-data/parameters
PUT    /api/admin/spine-data/parameters/{group}/{name}
GET    /api/admin/spine-data/materials
PUT    /api/admin/spine-data/materials/{name}
POST   /api/admin/spine-data/materials
GET    /api/admin/spine-data/manufacturer-charts
POST   /api/admin/spine-data/test-calculation
```

### 2. Unified Spine Service

**Location**: `arrow_scraper/spine_service.py`

**Purpose**: Centralized spine calculation service that provides multiple calculation methods and consistent calculations across the entire system.

**Key Methods**:
- `calculate_spine()` - Multi-method spine calculation with calculation_method parameter
- `calculate_enhanced_spine()` - Advanced calculation with material factors
- `get_calculation_parameters()` - Retrieve admin-configurable parameters
- `get_material_properties()` - Get material characteristics
- `calculate_bow_setup_spine()` - Calculate spine for saved bow configurations
- `_lookup_chart_spine()` - Chart-based spine lookup from manufacturer databases

**Calculation Method Support**:
- **calculation_method='universal'**: Uses restored universal formula (default)
- **calculation_method='german_industry'**: Uses German Industry Standard formulas
- **manufacturer_chart + chart_id**: Uses chart-based lookup from database

**Integration**: Used by the main tuning API (`/api/tuning/calculate-spine`) to provide multiple calculation methods.

### 3. Frontend Integration

**Location**: `frontend/components/ManufacturerSpineChartSelector.vue`

The frontend provides a comprehensive interface for spine calculation method selection:

**Calculation Method Selection**:
- Dropdown interface for choosing calculation method
- Universal Formula (default) with generic spine charts
- German Industry Standard with specialized recurve/traditional formulas
- Chart-based selection with manufacturer spine chart database

**State Management** (`frontend/stores/bowConfig.ts`):
- `calculation_method` property in bow configuration
- `chart_selection` object for manufacturer chart parameters
- Automatic recalculation when method or chart selection changes
- Integration with `shouldRecalculate` computed property

**API Integration** (`frontend/utils/spineCalculation.ts`):
- `calculateSpineAPI()` function handles chart selection parameters
- Passes `manufacturer_chart` and `chart_id` to backend API
- Maintains consistency between frontend state and backend calculations

**Type Support** (`frontend/types/arrow.ts`):
- `BaseBowConfiguration` interface includes `calculation_method` and `chart_selection`
- TypeScript support for all calculation method parameters
- Type safety for chart selection object structure

### 4. Calculator Page Enhancement

**Location**: `frontend/pages/calculator.vue`

The spine data system enhances the calculator page by:
- Multiple calculation method selection via dropdown interface
- Using advanced calculation parameters instead of hardcoded values
- Applying material-specific adjustments and manufacturer charts
- Providing manufacturer-specific recommendations
- Offering more accurate spine calculations with method-specific ranges

### 4. Arrow Recommendations

**Location**: `arrow_scraper/arrow_matching_engine.py`

The spine data system improves arrow recommendations by:
- Using enhanced spine calculations for matching
- Considering material properties in scoring
- Applying manufacturer-specific adjustments
- Providing more accurate compatibility ratings

### 5. Tuning Guides

**Integration**: The tuning methodologies table provides data for:
- Step-by-step tuning instructions
- Equipment requirements
- Expected outcomes
- Troubleshooting guidance

## Data Sources and Content

### Sample Data Included

The system includes sample data with:
- **24 calculation parameters** across 4 groups
- **7 arrow materials** (Carbon, Aluminum, Wood, etc.)
- **3 manufacturer spine charts** 
- **2 flight problem diagnostics**
- **1 tuning methodology**

### Data Categories

**Calculation Parameters**:
- `base_calculation`: Core spine calculation coefficients
- `bow_adjustments`: Bow-specific adjustment factors
- `safety_factors`: Safety margins and tolerances
- `material_factors`: Material-specific multipliers

**Material Properties**:
- Carbon (high performance, temperature sensitive)
- Aluminum (consistent, durable)
- Wood (traditional, variable)
- Carbon/Aluminum hybrids
- Specialized competition materials

## Automatic Migration and Setup

### Migration Process

1. **Detection**: Startup scripts check for spine calculation tables
2. **Migration**: Runs `migrate_spine_calculation_data.py` if tables missing
3. **Data Import**: Imports sample data with `import_spine_calculator_data.py`
4. **Verification**: Confirms tables and data are properly created

### Startup Integration

**Production** (`./start-unified.sh ssl domain.com`):
```bash
# Automatic spine migration during startup
ensure_spine_data_migration() {
    # Check for required tables
    # Run migration if needed
    # Import sample data
}
```

**Local Development** (`./start-unified.sh dev start`):
```bash
# Spine migration before API start
ensure_spine_data_migration() {
    # Detect missing tables
    # Run migration and import
}
```

## API Integration

### Service Layer

The `UnifiedSpineService` provides a consistent interface:

```python
# Initialize service
spine_service = UnifiedSpineService()

# Basic calculation
result = spine_service.calculate_spine(
    draw_weight=50.0,
    arrow_length=29.0,
    point_weight=125.0,
    bow_type='compound'
)

# Enhanced calculation with materials
enhanced = spine_service.calculate_enhanced_spine(
    draw_weight=50.0,
    arrow_length=29.0,
    point_weight=125.0,
    bow_type='compound',
    material_preference='carbon'
)

# Get calculation parameters
params = spine_service.get_calculation_parameters('base_calculation')

# Get material properties
materials = spine_service.get_material_properties()
```

### Admin API Integration

Admin endpoints provide CRUD operations for spine data:

```javascript
// Frontend usage in admin panel
const api = useApi()

// Get calculation parameters
const params = await api.get('/admin/spine-data/parameters')

// Update parameter
await api.put('/admin/spine-data/parameters/base_calculation/draw_weight_factor', {
    value: 12.5
})

// Get materials
const materials = await api.get('/admin/spine-data/materials')

// Test calculation
const result = await api.post('/admin/spine-data/test-calculation', {
    draw_weight: 50,
    arrow_length: 29,
    point_weight: 125,
    bow_type: 'compound'
})
```

## Error Handling and Fallbacks

### Graceful Degradation

If spine data tables are missing or corrupted:
1. **Standard Calculations**: Falls back to basic spine calculator
2. **Default Parameters**: Uses hardcoded calculation constants
3. **Error Logging**: Logs issues for debugging
4. **User Experience**: Continues to function with basic features

### Migration Recovery

If migration fails:
1. **Warning Messages**: Logs migration failure details
2. **Continued Startup**: Server continues to start normally
3. **Manual Recovery**: Admin can run migration scripts manually
4. **API Fallback**: Spine service falls back to basic calculations

## Performance Considerations

### Caching

The `UnifiedSpineService` includes caching:
- **Parameter Cache**: Cached calculation parameters by group
- **Material Cache**: Cached material properties by material type
- **Cache Invalidation**: Clears cache when admin updates parameters

### Database Optimization

- **Indexes**: Performance indexes on frequently queried columns
- **Query Optimization**: Efficient queries for parameter retrieval
- **Connection Management**: Proper database connection handling

## Troubleshooting

### Common Issues

1. **Missing Tables**: Run migration script manually
2. **Empty Parameters**: Import sample data
3. **Calculation Errors**: Check for invalid parameter values
4. **Permission Issues**: Ensure database is writable

### Debug Commands

```bash
# Check if spine tables exist
sqlite3 databases/arrow_database.db "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%spine%' OR name LIKE '%calculation%' OR name LIKE '%material%';"

# Count records in each table
sqlite3 databases/arrow_database.db "SELECT 'calculation_parameters', COUNT(*) FROM calculation_parameters;"

# Manual migration
cd arrow_scraper
python migrate_spine_calculation_data.py
python import_spine_calculator_data.py

# Check API endpoint
curl http://localhost:5000/api/admin/spine-data/parameters
```

### Logs and Monitoring

- **Migration Logs**: Detailed migration progress and errors
- **API Logs**: Spine service initialization and errors
- **Admin Logs**: Parameter modification tracking
- **Calculation Logs**: Spine calculation requests and results

## Future Enhancements

### Planned Features

1. **Import/Export**: Backup and restore spine data configurations
2. **Manufacturer Integration**: Direct integration with manufacturer spine charts
3. **Machine Learning**: Adaptive spine calculations based on user feedback
4. **Advanced Diagnostics**: Automated flight problem detection
5. **Custom Materials**: User-defined arrow material properties

### Extension Points

- **Custom Calculation Methods**: Plugin system for alternative spine calculations
- **Material Database**: Extended material property database
- **Manufacturer API**: Integration with manufacturer data feeds
- **User Preferences**: Personalized calculation parameters
- **Historical Data**: Tracking of calculation accuracy over time

## Security Considerations

### Access Control

- **Admin Only**: Spine data modification requires admin privileges
- **Authentication**: JWT token authentication for all admin endpoints
- **Audit Trail**: Tracking of parameter changes with user attribution

### Data Validation

- **Parameter Validation**: Range checking for calculation parameters
- **SQL Injection Protection**: Parameterized queries throughout
- **Input Sanitization**: Validation of all admin inputs

### Backup and Recovery

- **Database Backups**: Regular backups include spine data tables
- **Migration Scripts**: Version-controlled migration procedures
- **Data Export**: Admin backup and restore functionality

---

*This documentation covers the comprehensive spine data system as implemented in August 2025. For additional technical details, see the source code in `arrow_scraper/spine_service.py` and related files.*