# Spine Chart System Defaults Documentation

## Overview

The Enhanced Spine Chart System provides intelligent default chart selection for all bow types and arrow materials, ensuring users get appropriate spine calculations automatically while maintaining full manual override capabilities.

## System Architecture

### Core Components

1. **Database Layer**
   - `manufacturer_spine_charts_enhanced` table with `is_system_default` and `calculation_priority` fields
   - Support for 21+ spine charts across 4 bow types and 3 material types
   - Material-aware chart classification system

2. **API Layer**
   - Enhanced `/api/calculator/system-default` endpoint with material preference support
   - Admin endpoints for setting system defaults via web interface
   - Intelligent fallback system for chart selection

3. **Frontend Layer**
   - `ManufacturerSpineChartSelector` component with auto-loading defaults
   - Material-aware chart selection and filtering
   - Real-time updates when bow type or material changes

## Bow Type and Material Compatibility

### Available Combinations

```
📊 SPINE CHART COVERAGE BY BOW TYPE AND MATERIAL:

🏹 COMPOUND BOWS:
  📦 Carbon: 7 charts (Easton Target ⭐, Victory, Gold Tip, Skylon, Generic)
  📦 Aluminum: 1 chart (Easton XX75/XX78)
  📦 Carbon-Aluminum: 1 chart (Easton A/C series)

🏹 RECURVE BOWS:
  📦 Carbon: 5 charts (Easton Target ⭐, Victory, Gold Tip, Skylon, Generic)
  📦 Wood: 4 charts (Port Orford Cedar, Douglas Fir, Pine, Birch)
  📦 Aluminum: 1 chart (Easton XX75/XX78)

🏹 LONGBOW:
  📦 Carbon: 1 chart (Generic Carbon ⭐ for carbon preference)
  📦 Wood: 1 chart (Port Orford Cedar ⭐ default)

🏹 TRADITIONAL:
  📦 Carbon: 1 chart (Generic Carbon ⭐ for carbon preference)
  📦 Wood: 1 chart (Port Orford Cedar ⭐ default)
```

### System Defaults

**Base Defaults (no material preference):**
- **Compound**: Easton Target A/C All-Carbon (most popular target chart)
- **Recurve**: Easton Target A/C All-Carbon (competition standard)
- **Longbow**: Port Orford Cedar Traditional Wood Arrows (traditional choice)
- **Traditional**: Port Orford Cedar Traditional Wood Arrows (authentic traditional)

**Material-Aware Defaults:**
- **Any Bow + Carbon**: Prioritizes carbon charts, falls back to Generic Carbon
- **Any Bow + Wood**: Prioritizes wood species charts for traditional archery
- **Any Bow + Aluminum**: Prioritizes aluminum charts (Easton XX75/XX78 series)

## API Usage

### Basic System Default
```bash
GET /api/calculator/system-default?bow_type=compound
```

### Material-Aware System Default
```bash
GET /api/calculator/system-default?bow_type=longbow&material=carbon
GET /api/calculator/system-default?bow_type=traditional&material=wood
```

### Response Format
```json
{
  "default_chart": {
    "id": 1,
    "manufacturer": "Easton",
    "model": "Target A/C All-Carbon",
    "bow_type": "compound",
    "spine_system": "standard_deflection",
    "chart_notes": ""
  },
  "bow_type": "compound",
  "material_preference": "carbon"
}
```

## Shooting Style Integration

### Design Philosophy
- **Session-Only Parameter**: Shooting styles are not stored in bow setups
- **Real-Time Calculation**: Applied during spine calculation, not configuration
- **Bow Type Specific**: Available options change based on selected bow type

### Shooting Style Mappings

```
🎯 SHOOTING STYLES BY BOW TYPE:

🏹 RECURVE:
  ✓ Standard (baseline calculation)
  ✓ Barebow (5% stiffer for string walking)
  ✓ Olympic (3% weaker for competition stability)
  ✓ Hunting (5% weaker for broadhead compatibility)

🏹 COMPOUND:
  ✓ Standard (baseline calculation)
  ✓ Target (same as standard, competition focus)
  ✓ Hunting (5% weaker for broadhead compatibility)

🏹 LONGBOW/TRADITIONAL:
  ✓ Standard (baseline calculation)
  ✓ Traditional Instinctive (2% weaker for forgiving flight)
  ✓ Hunting (5% weaker for broadhead compatibility)
```

### Calculation Impact
- **Spine Multipliers**: Applied in `spine_service.py` during calculation
- **Notes System**: Provides explanation for adjustments to users
- **Professional Mode**: Integrates with advanced bow speed and release type settings

## Admin Management

### Setting System Defaults

**Web Interface:**
1. Navigate to Admin Panel → Spine Chart Library
2. Click ⭐ "Set Default" button next to desired chart
3. System automatically clears previous defaults for that bow type
4. Yellow star badge indicates current system default

**Database Direct:**
```sql
-- Set chart as system default
UPDATE manufacturer_spine_charts_enhanced 
SET is_system_default = 1, calculation_priority = 1 
WHERE id = ?;

-- Clear other defaults for same bow type
UPDATE manufacturer_spine_charts_enhanced 
SET is_system_default = 0 
WHERE bow_type = ? AND id != ?;
```

### Chart Management Features

- **Duplication**: Create test variations of existing charts
- **Custom Charts**: User-created charts with same default capability
- **Priority System**: Control which chart loads when multiple defaults exist
- **Material Classification**: Automatic detection of chart material type

## Frontend Integration

### ManufacturerSpineChartSelector Component

**Enhanced Props:**
```typescript
interface Props {
  bowType?: string           // Required: compound/recurve/longbow/traditional
  materialPreference?: string // Optional: carbon/wood/aluminum/carbon-aluminum
  onSelectionChange?: Function
}
```

**Auto-Loading Behavior:**
- **Mount**: Loads system default for current bow type
- **Bow Type Change**: Reloads appropriate default for new bow type
- **Material Change**: Switches to material-appropriate chart if available
- **Fallback**: Shows all charts if no material-specific default exists

### Calculator Page Integration

**Material Awareness:**
```vue
<ManufacturerSpineChartSelector
  :bow-type="bowConfig.bow_type"
  :material-preference="bowConfig.arrow_material"
  @selection-change="handleSpineChartSelection"
/>
```

**Dynamic Options:**
- Shooting style options filter based on bow type
- Material options show all available types
- Professional mode settings integrate with chart calculations

## Benefits

### User Experience
- **Automatic Defaults**: Appropriate charts load automatically
- **Material Intelligence**: System understands carbon vs wood vs aluminum preferences
- **Progressive Enhancement**: Works without manual chart selection, enhanced with it
- **Shooting Style Integration**: Context-aware calculation adjustments

### Professional Features
- **Chart Override**: Manual selection overrides system defaults
- **Calculation Notes**: Explains why specific adjustments were made
- **Session Persistence**: Selections maintained during calculator session
- **Admin Control**: Easy system default management via web interface

### Technical Benefits
- **Performance**: Indexed queries for fast default lookup
- **Scalability**: Supports unlimited custom charts and manufacturers
- **Flexibility**: Material-aware but not material-restricted
- **Maintainability**: Clear separation of concerns between defaults and user choice

## Migration Notes

**Database Changes:**
- Added `is_system_default` and `calculation_priority` columns
- Populated 21 spine charts from comprehensive JSON data
- Created traditional carbon chart for complete material coverage

**API Enhancements:**
- Enhanced system default endpoint with material preference support
- Maintained backward compatibility with existing calls
- Added intelligent fallback system for chart selection

**Frontend Updates:**
- Enhanced component props for material awareness
- Added watchers for real-time default updates
- Integrated with existing calculation flow

---

*Last Updated: September 2025*
*Related Documentation: [Spine Data System](SPINE_DATA_SYSTEM.md), [API Endpoints](API_ENDPOINTS.md)*