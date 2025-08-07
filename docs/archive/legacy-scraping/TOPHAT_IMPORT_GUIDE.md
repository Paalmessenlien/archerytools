# TopHat Archery Data Import Guide

## Overview

The TopHat Data Import Script is a smart arrow database enhancement tool that intelligently matches and imports missing data from the comprehensive TopHat Archery scraper results into your existing arrow database. It prioritizes TopHat data as the authoritative source for length_options and can add new arrows and manufacturers based on configuration.

## Key Features

### 🎯 Intelligent Arrow Matching
- **Smart Manufacturer Normalization**: Handles manufacturer name variations (e.g., "Gold" → "Gold Tip", "Carbon" → "Carbon Express")
- **Fuzzy Model Name Matching**: Uses advanced similarity scoring to find matches even with slight name differences
- **Multi-Strategy Matching**: Attempts exact matches, partial matches, and normalized name matches
- **Configurable Match Threshold**: 75% similarity threshold ensures high-quality matches

### 🔄 Comprehensive Data Updates
- **Length Options Priority**: Always uses TopHat data as master source for arrow length specifications
- **Missing Data Enhancement**: Fills in gaps for outer_diameter, inner_diameter, gpi_weight, and other specifications
- **New Spine Specifications**: Adds spine options not present in the existing database
- **Image URL Updates**: Populates missing product images from TopHat data

### ⚙️ Flexible Import Options
- **Update Existing Only**: Default mode that only enhances existing arrows
- **Add New Arrows**: Option to import arrows from known manufacturers
- **Add New Manufacturers**: Option to import completely new manufacturers and their arrow lines
- **Dry Run Mode**: Preview what changes would be made without modifying the database

## Installation & Setup

### Prerequisites
```bash
# Ensure you have the TopHat scraper results
ls data/processed/extra/tophat_archery_arrows.json

# Make sure the import script is executable
chmod +x tophat_data_import.py
```

### Database Backup (Recommended)
```bash
# Always backup your database before importing
cp arrow_database.db arrow_database.db.backup
```

## Usage Examples

### 1. Preview Changes (Dry Run)
```bash
# See what would be updated without making changes
python tophat_data_import.py --dry-run

# Preview with all import options enabled
python tophat_data_import.py --dry-run --add-new-arrows --add-new-manufacturers
```

### 2. Update Existing Arrows (Recommended)
```bash
# Update existing arrows with missing data (default behavior)
python tophat_data_import.py

# Explicit update existing command
python tophat_data_import.py --update-existing
```

### 3. Add New Arrows from Known Manufacturers
```bash
# Add new arrow models from manufacturers already in database
python tophat_data_import.py --add-new-arrows
```

### 4. Full Import (New Manufacturers + Arrows)
```bash
# Import everything including new manufacturers
python tophat_data_import.py --add-new-arrows --add-new-manufacturers
```

### 5. Custom File Paths
```bash
# Use custom database or TopHat file
python tophat_data_import.py --database custom_arrows.db --tophat-file custom_tophat.json
```

## Matching Algorithm

### Manufacturer Name Normalization

The script handles common manufacturer name variations automatically:

| TopHat Name | Database Name | Match Type |
|------------|---------------|------------|
| Gold | Gold Tip | Normalized |
| Carbon | Carbon Express | Normalized |
| Black | Black Eagle | Normalized |
| Nijora | Nijora Archery | Partial |
| Skylon | Skylon Archery | Partial |
| OK | OK Archery | Partial |

### Model Name Matching

Uses sophisticated fuzzy matching with:
- **Exact Match Priority**: Direct string matches get highest scores
- **Normalized Comparison**: Removes suffixes like "arrow", "shaft", trademark symbols
- **Similarity Scoring**: SequenceMatcher algorithm for fuzzy matching
- **Combined Scoring**: 70% model name + 30% manufacturer name

### Match Threshold

- **Minimum Score**: 75% similarity required for a match
- **High Confidence**: 85%+ matches are considered excellent
- **Manual Review**: 75-84% matches should be reviewed for accuracy

## Import Results Interpretation

### Successful Import Example
```
============================================================
TopHat Data Import Summary
============================================================
Total arrows processed: 299
Matched arrows: 13
Updated arrows: 13
New arrows added: 0
Updated spine specs: 43
New spine specs added: 49
Length options updated: 38
============================================================
```

### Key Metrics Explained

- **Total arrows processed**: All arrows found in TopHat data
- **Matched arrows**: Existing database arrows that matched TopHat data
- **Updated arrows**: Arrows that received data updates
- **Updated spine specs**: Existing spine specifications enhanced with missing data
- **New spine specs added**: Completely new spine options added to existing arrows
- **Length options updated**: Critical metric showing TopHat length data applied

## Data Priority Rules

### TopHat Data Always Wins For:
1. **Length Options**: TopHat is the authoritative source
2. **Image URLs**: Higher quality 1280x1280 images from TopHat
3. **Translated Descriptions**: Professional English translations

### Database Data Preserved For:
1. **Existing Specifications**: Only fills missing data, doesn't overwrite
2. **User Preferences**: Maintains any manual customizations
3. **Relationship Data**: Preserves database relationships and IDs

## Manufacturer Coverage

### Currently Matched Manufacturers
Based on the database and TopHat data comparison:

**Existing in Database:**
- Aurel Archery → Aurel (16 TopHat arrows)
- Gold Tip → Gold (26 TopHat arrows)  
- Carbon Express → Carbon (54 TopHat arrows)
- Nijora Archery → Nijora (28 TopHat arrows)
- Skylon Archery → Skylon (18 TopHat arrows)
- Easton Archery → Easton (62 TopHat arrows)

**New Manufacturers Available:**
- OK Archery (5 arrows)
- Black Eagle (58 arrows)
- Cross-X (19 arrows)
- DK Bow (3 arrows)
- Bearpaw (10 arrows)

## Best Practices

### 1. Incremental Import Strategy
```bash
# Step 1: Preview changes
python tophat_data_import.py --dry-run

# Step 2: Update existing arrows
python tophat_data_import.py

# Step 3: Add new arrows from known manufacturers
python tophat_data_import.py --add-new-arrows

# Step 4: Add new manufacturers (if desired)
python tophat_data_import.py --add-new-arrows --add-new-manufacturers
```

### 2. Quality Assurance
```bash
# Always backup before major imports
cp arrow_database.db arrow_database.db.$(date +%Y%m%d_%H%M%S)

# Verify import results
python show_available_data.py

# Test arrow search functionality
python test_arrow_search.py
```

### 3. Length Options Validation
The most critical update is length_options. Review changes like:
```
Updated length_options for Gold Tip Hunter Pro spine 300: [30.0, 31.0, 32.0] -> ['32"']
```

This shows TopHat data providing more specific length information.

## Troubleshooting

### Common Issues

**1. No Matches Found**
```
Matched arrows: 0
```
- Check manufacturer name variations in the script
- Verify TopHat data quality
- Consider lowering match threshold for testing

**2. Database Lock Errors**
```
sqlite3.OperationalError: database is locked
```
- Close any other applications using the database
- Ensure no other import processes are running

**3. Missing TopHat File**
```
Failed to load TopHat data: [Errno 2] No such file or directory
```
- Verify TopHat scraper has run successfully
- Check file path: `data/processed/extra/tophat_archery_arrows.json`

### Debug Mode

For detailed matching information:
```python
# Edit tophat_data_import.py
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed match scoring for troubleshooting.

## Advanced Configuration

### Custom Match Threshold
Edit the script to adjust the minimum match score:
```python
if combined_score > best_score and combined_score >= 0.75:  # Change this value
```

### Additional Manufacturer Mappings
Add new manufacturer name variations:
```python
normalizations = {
    'your_tophat_name': 'your_database_name',
    # Add more mappings here
}
```

## Integration with Production

### Production Import Workflow
```bash
# 1. Import TopHat enhancements
python tophat_data_import.py --add-new-arrows

# 2. Run production import to update main database
./production-import-only.sh

# 3. Deploy updated database
sudo docker-compose -f docker-compose.enhanced-ssl.yml up -d --build
```

### Automated Import
Consider adding to your update workflow:
```bash
#!/bin/bash
# Enhanced update script
cd arrow_scraper
python tophat_data_import.py --add-new-arrows
./production-import-only.sh
echo "Database enhanced with TopHat data"
```

## Command Reference

### Full Command Syntax
```bash
python tophat_data_import.py [OPTIONS]

Options:
  --database PATH          Path to arrow database (default: arrow_database.db)
  --tophat-file PATH       Path to TopHat JSON file (default: data/processed/extra/tophat_archery_arrows.json)
  --update-existing        Update existing arrows with missing data (default: True)
  --add-new-arrows         Add new arrows from existing manufacturers
  --add-new-manufacturers  Add arrows from new manufacturers (requires --add-new-arrows)
  --dry-run               Show what would be done without making changes
  --help                  Show help message
```

### Common Command Combinations
```bash
# Conservative update (recommended for production)
python tophat_data_import.py

# Full preview
python tophat_data_import.py --dry-run --add-new-arrows --add-new-manufacturers

# Progressive import
python tophat_data_import.py --add-new-arrows

# Complete import
python tophat_data_import.py --add-new-arrows --add-new-manufacturers
```

## Success Metrics

A successful TopHat import should show:
- ✅ **Match Rate**: 5-15% of TopHat arrows matching existing database
- ✅ **Length Updates**: 30+ length_options updated (critical improvement)
- ✅ **New Spine Specs**: 40+ new spine specifications added
- ✅ **Zero Errors**: No database corruption or import failures

## Conclusion

The TopHat Data Import Script provides a sophisticated way to enhance your arrow database with high-quality European manufacturer data. By using TopHat as the authoritative source for length_options and providing intelligent matching, it significantly improves the completeness and accuracy of your arrow specifications database.

For questions or issues, refer to the script's detailed logging output or examine the matching algorithm for specific manufacturer/model combinations that need attention.