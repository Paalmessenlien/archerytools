# Draw Length Architecture Documentation

## Overview

The Archery Tools platform handles draw length measurements in a sophisticated way to ensure accurate spine calculations and performance analysis. This document clarifies the purpose and usage of each draw length column in the database.

## Database Schema

### Users Table - Personal Draw Length (Fallback Only)

```sql
users.draw_length REAL DEFAULT 28.0        -- Legacy column (deprecated)
users.user_draw_length REAL DEFAULT 28.0   -- User's personal draw length measurement
```

**Purpose**: Stores the archer's personal draw length measurement as measured by a professional or self-measured.

**Usage**: 
- ✅ **Fallback only** when creating new bow setups without specific draw length data
- ✅ **Default value** for bow setup creation forms
- ❌ **NEVER** used directly in spine calculations or performance analysis
- ❌ **NEVER** used when bow setup draw length data exists

**Range**: 20-36 inches (validated in frontend)
**Default**: 28.0 inches

### Bow Setups Table - Equipment-Specific Draw Length (Primary)

```sql
bow_setups.draw_length REAL                -- Primary draw length for calculations
bow_setups.draw_length_module REAL         -- Compound bow cam/module setting
```

**draw_length Column**:
- **Purpose**: The actual measured draw length at the bow's specified draw weight
- **Usage**: 
  - ✅ **Primary source** for all spine calculations
  - ✅ **Primary source** for all performance analysis
  - ✅ **Primary source** for arrow speed calculations
  - ✅ Used for recurve, traditional, longbow, and compound bows
- **How it differs by bow type**:
  - **Compound**: Measured draw length at full draw (may differ from module setting)
  - **Recurve**: Measured draw length at specified draw weight
  - **Traditional/Longbow**: Measured draw length at specified draw weight

**draw_length_module Column (Compound Only)**:
- **Purpose**: The physical cam/module specification of compound bows
- **Usage**:
  - ✅ Equipment specification reference
  - ✅ May inform draw_length value but doesn't replace it
  - ❌ Not directly used in calculations
- **Range**: 24-34 inches (compound bow module specifications)

## Data Hierarchy for Calculations

### Primary Source (Always Use First)
```
bow_setups.draw_length
```

### Fallback Chain (Only if Primary Missing)
```
1. bow_setups.draw_length_module (compound bows only)
2. users.user_draw_length
3. 28.0 (system default)
```

## Implementation Rules

### ✅ Correct Usage Patterns

```python
# API: Get draw length for calculations
def get_bow_draw_length(bow_setup_id):
    bow_setup = get_bow_setup(bow_setup_id)
    if bow_setup.draw_length:
        return bow_setup.draw_length  # Primary source
    elif bow_setup.bow_type == 'compound' and bow_setup.draw_length_module:
        return bow_setup.draw_length_module  # Fallback for compounds
    else:
        user = get_user(bow_setup.user_id)
        return user.user_draw_length or 28.0  # Final fallback
```

```javascript
// Frontend: Display draw length source
const getDrawLengthSource = (bowSetup, user) => {
  if (bowSetup.draw_length) {
    return `Bow setup: ${bowSetup.draw_length}"`
  } else if (bowSetup.bow_type === 'compound' && bowSetup.draw_length_module) {
    return `Compound module: ${bowSetup.draw_length_module}"`
  } else {
    return `Personal measurement: ${user.user_draw_length || 28.0}"`
  }
}
```

### ❌ Incorrect Usage Patterns

```python
# WRONG: Using user draw length when bow setup exists
def calculate_spine(bow_setup, user):
    draw_length = user.user_draw_length  # ❌ WRONG
    return spine_calculation(bow_setup.draw_weight, draw_length, ...)

# WRONG: Using draw_length_module directly in calculations
def calculate_performance(bow_setup):
    draw_length = bow_setup.draw_length_module  # ❌ WRONG for calculations
    return performance_analysis(bow_setup.draw_weight, draw_length, ...)
```

## Frontend Form Guidelines

### User Profile Form
- **Label**: "Personal Draw Length (fallback measurement)"
- **Help Text**: "Your measured draw length. Used as default for new bow setups only."
- **Validation**: 20-36 inches

### Bow Setup Forms
- **Label**: "Draw Length at Draw Weight"
- **Help Text**: "Measured draw length at this bow's draw weight. Used for all calculations."
- **Priority**: Primary input field (more prominent than compound module)
- **Validation**: 24-34 inches

### Compound Bow Specific
- **Additional Field**: "Draw Length Module"
- **Help Text**: "Cam/module specification (for reference)"
- **Position**: Secondary to main draw length field

## Migration Requirements

To ensure data consistency, the following migration should be run:

1. **Populate missing bow_setups.draw_length values**:
   - For compound bows: Use draw_length_module if available
   - For all bows: Fall back to user.user_draw_length
   - Final fallback: 28.0

2. **Validate data integrity**:
   - Ensure all bow_setups have draw_length values
   - Flag any inconsistencies for review

3. **Update calculation functions**:
   - Modify all calculation endpoints to use bow_setups.draw_length
   - Remove direct usage of user.user_draw_length in calculations

## Testing Requirements

### Calculation Accuracy Tests
- Verify spine calculations use bow setup draw length
- Verify performance analysis uses bow setup draw length
- Verify arrow speed calculations use bow setup draw length

### Data Consistency Tests
- Test fallback hierarchy works correctly
- Test compound bow module vs draw length handling
- Test edge cases with missing data

### User Experience Tests
- Verify form labels and help text are clear
- Verify data sources are displayed to users
- Verify calculation results are consistent

## Common Issues and Solutions

### Issue: User Changes Profile Draw Length Expecting Calculation Changes
**Solution**: Display draw length source in calculation results to clarify which value is being used.

### Issue: Compound Bow Draw Length Module vs Actual Draw Length Confusion
**Solution**: Separate fields with clear labeling and help text explaining the difference.

### Issue: Inconsistent Calculation Results
**Solution**: Always use bow_setups.draw_length as primary source with clear fallback chain.

## Conclusion

This architecture ensures:
1. **Accurate calculations** by using equipment-specific draw lengths
2. **Clear data hierarchy** with proper fallback handling
3. **User understanding** through transparent draw length source display
4. **Data consistency** across all calculation endpoints

All future development should follow these guidelines to maintain calculation accuracy and user experience quality.