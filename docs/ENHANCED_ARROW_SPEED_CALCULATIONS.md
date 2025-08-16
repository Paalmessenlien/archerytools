# Enhanced Arrow Speed Calculations Documentation

## Overview

The Enhanced Arrow Speed Calculations system provides sophisticated arrow velocity estimation using multiple data sources, string material factors, and bow type efficiency considerations. This system prioritizes measured chronograph data while providing accurate estimations when measured data is unavailable.

## Table of Contents

- [Calculation Hierarchy](#calculation-hierarchy)
- [String Material Speed Modifiers](#string-material-speed-modifiers)
- [Bow Type Efficiency Factors](#bow-type-efficiency-factors)
- [IBO-Based Speed Calculations](#ibo-based-speed-calculations)
- [Weight Adjustment Formulas](#weight-adjustment-formulas)
- [API Integration](#api-integration)
- [Implementation Details](#implementation-details)
- [Usage Examples](#usage-examples)
- [Performance Considerations](#performance-considerations)

## Calculation Hierarchy

The system uses a prioritized approach to arrow speed calculation:

### 1. Chronograph Data (Highest Priority)
- **Confidence:** 85-100%
- **Source:** Measured speeds from chronograph devices
- **Accuracy:** Most accurate when available
- **Weight Adjustment:** Uses kinetic energy conservation for different arrow weights

### 2. Enhanced IBO Estimation (Medium Priority)  
- **Confidence:** 75%
- **Source:** IBO speed + string material + bow type factors
- **Accuracy:** Good estimation based on manufacturer specifications
- **Adjustments:** Draw weight, draw length, arrow weight, string material

### 3. Basic Calculation (Fallback)
- **Confidence:** 50-60%
- **Source:** Simple draw weight based formula
- **Accuracy:** Basic estimation for system reliability
- **Usage:** Error handling and legacy compatibility

## String Material Speed Modifiers

String materials significantly affect arrow speed through energy transfer efficiency:

### Material Speed Factors

| Material | Speed Modifier | Characteristics | Typical Use |
|----------|----------------|-----------------|-------------|
| **Dacron** | 0.92 (-8%) | Slowest, most forgiving | Traditional bows, beginners |
| **FastFlight** | 1.00 (baseline) | Standard modern string | General compound/recurve |
| **Dyneema** | 1.02 (+2%) | Faster, low stretch | Performance shooting |
| **Vectran** | 1.03 (+3%) | High performance | Competition shooting |
| **SK75 Dyneema** | 1.04 (+4%) | Premium racing strings | Elite competition |
| **Custom Blend** | 1.01 (+1%) | Custom materials | Specialized applications |

### Speed Impact Calculation

```
final_speed = base_calculated_speed × string_modifier
```

**Example:**
- Base calculated speed: 280 FPS
- String material: Dyneema (1.02 modifier)
- Final speed: 280 × 1.02 = 285.6 FPS (+5.6 FPS increase)

## Bow Type Efficiency Factors

Different bow types have varying energy transfer efficiency:

### Bow Type Efficiency Factors

| Bow Type | Efficiency Factor | Energy Transfer | Characteristics |
|----------|------------------|-----------------|-----------------|
| **Compound** | 0.95 | Highest | Cam systems, let-off |
| **Recurve** | 0.85 | High | Traditional recurve design |
| **Barebow** | 0.80 | Medium-High | Recurve without accessories |
| **Longbow** | 0.75 | Medium | Traditional straight limbs |
| **Traditional** | 0.70 | Lower | Historical designs |

### Efficiency Impact

```
bow_adjusted_speed = calculated_speed × bow_efficiency_factor
```

The efficiency factor accounts for:
- **Cam Systems:** Compound bows store and release energy more efficiently
- **Limb Design:** Recurve tips provide additional energy storage
- **String Angle:** Affects energy transfer efficiency
- **Weight Distribution:** Affects dynamic efficiency

## IBO-Based Speed Calculations

### IBO Standard Reference

The International Bowhunting Organization (IBO) standard provides baseline measurements:
- **Arrow Weight:** 350 grains (5 grains per pound of draw weight)
- **Draw Length:** 30 inches
- **Draw Weight:** 70 pounds
- **Result:** Manufacturer's rated IBO speed

### Enhanced IBO Formula

```
adjusted_speed = (ibo_speed + weight_adjustment + length_adjustment) 
                × weight_ratio × string_modifier × bow_efficiency
```

#### Weight Adjustment
```
weight_adjustment = (actual_draw_weight - 70) × 10
```
- **Rule:** ±10 FPS per pound of draw weight difference
- **Example:** 60 lb bow = -100 FPS adjustment vs 70 lb standard

#### Length Adjustment  
```
length_adjustment = (actual_draw_length - 30) × 10
```
- **Rule:** ±10 FPS per inch of draw length difference
- **Example:** 28" draw = -20 FPS adjustment vs 30" standard

#### Weight Ratio (Kinetic Energy Conservation)
```
weight_ratio = (350 / actual_arrow_weight) ^ 0.5
```
- **Physics:** Kinetic energy = ½mv², so speed ∝ 1/√mass
- **Example:** 420 grain arrow = (350/420)^0.5 = 0.913 ratio

### Bounds and Safety Limits

```python
final_speed = max(150, min(450, calculated_speed))
```
- **Minimum:** 150 FPS (safety floor)
- **Maximum:** 450 FPS (reasonable ceiling)

## Weight Adjustment Formulas

### Kinetic Energy Conservation Method

When adjusting speeds for different arrow weights:

```
adjusted_speed = original_speed × (original_weight / new_weight) ^ 0.5
```

**Physics Background:**
- Kinetic Energy: KE = ½mv²
- Energy conservation: KE₁ = KE₂
- Solving for v₂: v₂ = v₁ × √(m₁/m₂)

**Practical Example:**
- Chronograph measured: 285 FPS at 425 grains
- Calculate for: 400 grains
- Adjusted speed: 285 × √(425/400) = 285 × 1.031 = 293.8 FPS

### Weight Sensitivity Analysis

| Weight Change | Speed Impact | Typical Scenario |
|---------------|--------------|------------------|
| +50 grains | -7.4% speed | Heavier points |
| +25 grains | -3.6% speed | Insert change |
| -25 grains | +3.8% speed | Lighter points |
| -50 grains | +7.9% speed | Aluminum arrows |

## API Integration

### Enhanced Speed Calculation Function

```python
def calculate_enhanced_arrow_speed_internal(
    bow_ibo_speed,      # IBO rated speed
    bow_draw_weight,    # Actual draw weight  
    bow_draw_length,    # Actual draw length
    bow_type,           # Bow type string
    arrow_weight_grains,# Target arrow weight
    string_material,    # String material
    setup_id=None,      # For chronograph lookup
    arrow_id=None       # For chronograph lookup
):
```

### Integration Points

**1. Arrow Performance Calculations**
```python
performance_data = calculate_arrow_performance(
    archer_profile, arrow_rec, estimated_speed=enhanced_speed
)
```

**2. Calculator API Endpoint**
```http
POST /api/calculator/arrow-speed-estimate
```

**3. Setup Arrow Performance**
```python
enhanced_speed = calculate_enhanced_arrow_speed_internal(...)
performance = calculate_arrow_performance(..., estimated_speed=enhanced_speed)
```

## Implementation Details

### Database Integration

**Chronograph Data Lookup:**
```sql
SELECT measured_speed_fps, arrow_weight_grains, std_deviation, shot_count
FROM chronograph_data 
WHERE setup_id = ? AND arrow_id = ? AND verified = 1
ORDER BY measurement_date DESC
LIMIT 1
```

**String Equipment Lookup:**
```sql
SELECT specifications 
FROM bow_equipment 
WHERE setup_id = ? AND category = 'String'
LIMIT 1
```

### Confidence Scoring

**Chronograph Data Confidence:**
```python
confidence = min(100, (shot_count * 10) + (85 if std_dev < 5 else 70))
```
- **Base:** 70% for single shot, 85% for low deviation
- **Shot Count Bonus:** +10% per shot
- **Maximum:** 100% confidence
- **Standard Deviation:** <5 FPS adds bonus

**Estimation Confidence:**
- **Enhanced IBO:** 75% (good estimation)
- **Basic Calculation:** 50-60% (fallback only)

### Error Handling

**Graceful Degradation:**
1. Chronograph lookup fails → Continue with estimation
2. String equipment lookup fails → Use Dacron default (conservative)
3. All calculations fail → Use basic draw weight formula
4. Invalid inputs → Apply safety bounds (150-450 FPS)

## Usage Examples

### 1. Frontend Speed Estimation

```javascript
// Calculator page integration
const response = await api.post('/calculator/arrow-speed-estimate', {
  bow_ibo_speed: 320,
  bow_draw_weight: 70,
  bow_draw_length: 29,
  bow_type: 'compound',
  arrow_weight_grains: 420,
  string_material: 'dyneema',
  setup_id: 1,          // Enables chronograph lookup
  arrow_id: 42          // Specific arrow data
})

console.log(`Speed: ${response.estimated_speed_fps} FPS`)
console.log(`Method: ${response.calculation_method}`)
console.log(`Confidence: ${response.confidence_percent}%`)
```

### 2. Backend Performance Calculation

```python
# Enhanced speed for arrow performance analysis
enhanced_speed = calculate_enhanced_arrow_speed_internal(
    bow_ibo_speed=bow_setup.get('ibo_speed', 320),
    bow_draw_weight=bow_setup.get('draw_weight', 50),
    bow_draw_length=bow_setup.get('draw_length', 29),
    bow_type=bow_setup.get('bow_type', 'compound'),
    arrow_weight_grains=total_arrow_weight,
    string_material=detected_string_material,
    setup_id=setup_id,
    arrow_id=arrow_id
)

# Use enhanced speed in performance calculations
performance = calculate_arrow_performance(
    archer_profile=profile,
    arrow_rec=arrow,
    estimated_speed=enhanced_speed
)
```

### 3. Automatic String Material Detection

```python
# Get string equipment for enhanced calculation
string_material = 'dacron'  # Conservative default
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
        if spec_data.get('material'):
            string_material = spec_data['material'].lower()
except Exception:
    pass  # Use default material
```

## Performance Considerations

### 1. Calculation Speed
- **Chronograph Lookup:** ~1ms database query
- **Enhanced Calculation:** ~0.1ms mathematical operations
- **Total Overhead:** Minimal impact on performance calculations

### 2. Caching Strategy
- **Performance Data:** Cached in `setup_arrows.performance_data` JSON column
- **String Equipment:** Cached per calculation request
- **Chronograph Data:** Fresh lookup for accuracy

### 3. Database Optimization
- **Indexes:** Chronograph data indexed by setup_id, arrow_id
- **Query Limits:** Use `LIMIT 1` for latest measurements
- **Connection Reuse:** Database connections pooled efficiently

### 4. Memory Usage
- **Minimal Overhead:** Calculations use primitive data types
- **No Caching:** Results calculated fresh for accuracy
- **Garbage Collection:** Temporary variables cleaned automatically

## Validation and Testing

### 1. Calculation Accuracy Tests
```python
# Test weight adjustment accuracy
original_speed = 285
original_weight = 425
new_weight = 400
expected_speed = 285 * (425/400)**0.5  # 293.8 FPS

calculated_speed = calculate_enhanced_arrow_speed_internal(...)
assert abs(calculated_speed - expected_speed) < 0.1
```

### 2. String Material Effect Tests
```python
# Test string material modifiers
base_speed = calculate_speed_with_material('dacron')      # 276.0 FPS
dyneema_speed = calculate_speed_with_material('dyneema')  # 281.5 FPS
speed_increase = (dyneema_speed - base_speed) / base_speed * 100
assert abs(speed_increase - 2.0) < 0.1  # Should be ~2% increase
```

### 3. Chronograph Priority Tests
```python
# Test chronograph data priority
chronograph_speed = 285.3
estimated_speed = 278.5

# With chronograph data
speed_with_chrono = calculate_enhanced_arrow_speed_internal(
    setup_id=1, arrow_id=42, ...
)
assert speed_with_chrono == chronograph_speed

# Without chronograph data  
speed_without_chrono = calculate_enhanced_arrow_speed_internal(
    setup_id=None, arrow_id=None, ...
)
assert abs(speed_without_chrono - estimated_speed) < 5.0
```

## Troubleshooting

### Common Issues

**1. Inconsistent Speed Results**
- Check string material detection accuracy
- Verify bow type mapping (compound/recurve/traditional)
- Confirm IBO speed values are realistic (280-370 FPS typical)

**2. Chronograph Data Not Used**
- Verify `setup_id` and `arrow_id` parameters provided
- Check chronograph data exists with `verified = 1`
- Confirm foreign key relationships intact

**3. Unrealistic Speed Calculations**
- Check safety bounds application (150-450 FPS)
- Verify arrow weight values are reasonable (200-800 grains)
- Confirm draw weight and length values are valid

**4. String Material Default Usage**
- Verify string equipment exists in database
- Check JSON specifications format validity
- Confirm material field mapping in equipment data

### Performance Debugging

**1. Speed Calculation Logging**
```python
print(f"Enhanced speed calculation:")
print(f"  Base IBO: {bow_ibo_speed} FPS")
print(f"  Weight adjustment: {weight_adjustment} FPS")
print(f"  Length adjustment: {length_adjustment} FPS")
print(f"  Weight ratio: {weight_ratio:.3f}")
print(f"  String modifier: {string_modifier:.3f}")
print(f"  Bow efficiency: {bow_efficiency:.3f}")
print(f"  Final speed: {final_speed:.1f} FPS")
```

**2. Chronograph Data Verification**
```sql
SELECT * FROM chronograph_data 
WHERE setup_id = 1 AND arrow_id = 42 
ORDER BY measurement_date DESC;
```

**3. String Equipment Verification**
```sql
SELECT category, specifications 
FROM bow_equipment 
WHERE setup_id = 1 AND category = 'String';
```

This documentation provides comprehensive coverage of the enhanced arrow speed calculation system, enabling accurate velocity estimation with multiple data sources and sophisticated modeling factors.