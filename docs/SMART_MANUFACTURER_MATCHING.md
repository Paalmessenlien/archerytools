# Smart Manufacturer Matching System

## Overview

The Smart Manufacturer Matching System provides intelligent linking between user-entered manufacturer names and existing manufacturers in the database. This system uses fuzzy matching, alias detection, and category specialization to automatically link custom equipment entries to known manufacturers, improving data consistency and quality.

## Features

### 🔍 Fuzzy String Matching
- **Multiple Algorithms**: Uses sequence matching, word overlap, and substring detection
- **Normalization**: Removes business suffixes (Inc, LLC, Archery, etc.) and punctuation
- **Confidence Scoring**: Returns match confidence scores from 0.0 to 1.0

### 📝 Manufacturer Aliases & Variations
The system recognizes common manufacturer name variations:

**Examples:**
- `easton` → `Easton Archery`
- `goldtip` → `Gold Tip`
- `carbonexpress` → `Carbon Express`
- `qad` → `Quality Archery Designs`
- `bstinger` → `B-Stinger`
- `blackgold` → `Black Gold`

### 🎯 Category Specialization
Manufacturers known for specific equipment categories get boosted confidence scores:

**Category Specialists:**
- **Strings**: BCY, Angel Majesty, Brownell, Dynasty
- **Sights**: Black Gold, Spot-Hogg, Axcel, Trophy Taker, Tight Spot
- **Stabilizers**: B-Stinger, Doinker, Fuse, Shrewd
- **Arrow Rests**: QAD, Trophy Taker, Vapor Trail, Hamskea
- **Weights**: B-Stinger, Shrewd, Doinker, Fuse

### 🔗 Smart Linking
- **High Confidence Threshold**: Only links manufacturers with >80% confidence
- **Preserves Original Name**: Stores the standardized manufacturer name while preserving user input context
- **Fallback Support**: Gracefully handles matching failures

## API Integration

### Equipment Addition Endpoint
**POST** `/api/bow-setups/<setup_id>/equipment`

When adding custom equipment, the system automatically:
1. Attempts to match the manufacturer name using fuzzy algorithms
2. Links to existing manufacturer if confidence ≥ 80%
3. Stores the standardized manufacturer name
4. Logs the linking decision with confidence score

**Example Log Output:**
```
🔗 Smart manufacturer linking: 'easton' → 'Easton Archery' (confidence: 0.95, alias)
🔗 Smart manufacturer linking: 'bstinger' → 'B-Stinger' (confidence: 0.95, alias)  
📝 No manufacturer match found for: 'Custom Bow Co' - storing as custom manufacturer
```

### Manufacturer Suggestions Endpoint
**GET** `/api/equipment/manufacturers/suggest?q=<query>&category=<category>`

Enhanced autocomplete suggestions that:
- **Prioritize Category Specialists**: Shows relevant manufacturers first
- **Smart Ranking**: Uses fuzzy matching for better suggestions
- **Fallback Support**: Provides basic suggestions if smart matching fails

**Parameters:**
- `q`: Search query (manufacturer name or partial name)
- `category`: Equipment category (String, Sight, Stabilizer, Arrow Rest, Weight)
- `limit`: Maximum suggestions to return (default: 20)

## Implementation Details

### Core Class: `ManufacturerMatcher`

Located in: `arrow_scraper/manufacturer_matcher.py`

**Key Methods:**
- `find_best_matches()`: Returns ranked matches with confidence scores
- `get_manufacturer_suggestions()`: Provides smart autocomplete suggestions
- `link_manufacturer()`: High-confidence manufacturer linking
- `is_category_specialist()`: Checks if manufacturer specializes in category

### Matching Algorithms

1. **Exact Alias Match**: Known variations → 95% confidence
2. **Fuzzy String Match**: Multiple similarity metrics → variable confidence
3. **Substring Match**: Partial matches → 80% confidence  
4. **Abbreviation Match**: Known abbreviations → 90% confidence

### Confidence Scoring

- **0.95**: Exact alias or abbreviation match
- **0.80-0.94**: High-quality fuzzy matches
- **0.60-0.79**: Medium-quality fuzzy matches
- **<0.60**: Low-quality matches (not used for linking)

## Usage Examples

### Frontend Integration
```javascript
// Get smart manufacturer suggestions
const response = await fetch('/api/equipment/manufacturers/suggest?q=easton&category=Sight');
const data = await response.json();
// Returns: [{"name": "Easton Archery", "country": "Unknown", "website": null}]
```

### Backend Usage
```python
from manufacturer_matcher import ManufacturerMatcher

matcher = ManufacturerMatcher()

# Find matches
matches = matcher.find_best_matches("goldtip", manufacturers, "String")
# Returns: [{"manufacturer": {...}, "confidence": 0.95, "match_type": "alias"}]

# Get suggestions  
suggestions = matcher.get_manufacturer_suggestions("bst", manufacturers, "Stabilizer")
# Returns: [{"name": "B-Stinger", ...}]
```

## Database Schema Impact

### Equipment Storage
Custom equipment entries automatically use standardized manufacturer names when high-confidence matches are found:

**Before Smart Matching:**
```
manufacturer_name: "easton"
```

**After Smart Matching:**  
```
manufacturer_name: "Easton Archery"  // Automatically standardized
```

### Manufacturer Linking
Equipment entries can be linked to existing manufacturer records when matches are found, enabling:
- **Consistent Data**: Unified manufacturer names across all equipment
- **Enhanced Search**: Better filtering and recommendation accuracy
- **Data Quality**: Reduced duplicate or variant manufacturer entries

## Testing

### Test Script
Run `python test_smart_manufacturer_linking.py` to verify functionality.

### Manual Testing
1. Navigate to bow setup management in the frontend
2. Add custom equipment with manufacturer variations:
   - `"easton"` should suggest `"Easton Archery"`
   - `"goldtip"` should suggest `"Gold Tip"`  
   - `"bstinger"` should suggest `"B-Stinger"`
3. Check API logs for linking messages

### Expected Results
- **Suggestions**: Relevant manufacturers appear in autocomplete
- **Linking**: High-confidence matches are automatically applied
- **Logging**: All linking decisions are logged with confidence scores

## Performance Considerations

- **Caching**: Manufacturer list is cached per request
- **Fallback**: Basic string matching fallback for robustness
- **Efficient**: O(n) complexity for most operations
- **Memory**: Minimal memory overhead with lazy loading

## Future Enhancements

- **Machine Learning**: Train on user selection patterns
- **Historical Data**: Learn from previous linking decisions  
- **User Feedback**: Allow manual manufacturer corrections
- **Category Detection**: Auto-detect equipment category from name/description
- **Brand Relationships**: Handle parent/subsidiary company relationships

---

This system significantly improves data quality and user experience by intelligently handling manufacturer name variations while maintaining full backward compatibility.