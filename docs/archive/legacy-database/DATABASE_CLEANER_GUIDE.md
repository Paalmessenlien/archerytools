# Database Cleaner Guide

## Overview

The Database Cleaner is a comprehensive maintenance tool for managing your arrow database. It provides powerful features for manufacturer management, data cleaning, and database integrity validation.

## Key Features

### 🏭 **Manufacturer Management**
- **Rename manufacturers** - Fix naming inconsistencies
- **Merge manufacturers** - Combine duplicate manufacturers  
- **Remove manufacturers** - Delete unwanted data
- **Export manufacturer data** - Backup before changes

### 🧹 **Data Cleaning**
- **Find duplicates** - Identify duplicate arrows
- **Clean duplicates** - Remove duplicates automatically
- **Validate database** - Check for integrity issues
- **Backup system** - Automatic backups before destructive operations

## Command Reference

### Basic Operations

```bash
# List all manufacturers with statistics
python database_cleaner.py --list-manufacturers

# List arrows for specific manufacturer
python database_cleaner.py --list-arrows "Gold Tip"

# Validate database integrity
python database_cleaner.py --validate
```

### Manufacturer Operations

```bash
# Rename manufacturer
python database_cleaner.py --rename-manufacturer "BigArchery" "Cross-X"

# Merge manufacturers (combines source into target)
python database_cleaner.py --merge-manufacturers "BigArchery" "Cross-X"

# Remove manufacturer completely
python database_cleaner.py --remove-manufacturer "Test Manufacturer"

# Save manufacturer data before changes
python database_cleaner.py --save-manufacturer "BigArchery" --output backup.json
```

### Data Cleaning

```bash
# Find potential duplicate arrows
python database_cleaner.py --find-duplicates

# Remove duplicates (keeps most complete version)
python database_cleaner.py --clean-duplicates

# Preview changes without making them
python database_cleaner.py --merge-manufacturers "Source" "Target" --dry-run
```

### Full Database Cleaning

```bash
# Show database statistics
python database_cleaner.py --stats

# Clean database completely (removes ALL data)
python database_cleaner.py --clean-all --dry-run  # Preview first
python database_cleaner.py --clean-all

# Clean database but keep specific manufacturers
python database_cleaner.py --clean-keep "Easton" "Gold Tip" --dry-run
python database_cleaner.py --clean-keep "Easton" "Gold Tip"

# Reset database schema (DANGER: removes ALL data and recreates tables)
python database_cleaner.py --reset-schema --dry-run
python database_cleaner.py --reset-schema
```

## Real-World Examples

### Example 1: Fix BigArchery → Cross-X Naming

**Problem**: BigArchery and Cross-X are the same manufacturer but appear as separate entries.

**Solution**:
```bash
# Step 1: Check current state
python database_cleaner.py --list-manufacturers | grep -E "(BigArchery|Cross-X)"

# Step 2: Preview the merge
python database_cleaner.py --merge-manufacturers "BigArchery" "Cross-X" --dry-run

# Step 3: Save backup (optional)
python database_cleaner.py --save-manufacturer "BigArchery" --output bigarchery_backup.json

# Step 4: Execute merge
python database_cleaner.py --merge-manufacturers "BigArchery" "Cross-X"

# Step 5: Verify result
python database_cleaner.py --list-arrows "Cross-X"
```

**Result**: All BigArchery arrows now appear under Cross-X manufacturer.

### Example 2: Clean Up Test Data

**Problem**: Development testing left "Test Manufacturer" in the database.

**Solution**:
```bash
# Remove test manufacturer completely
python database_cleaner.py --remove-manufacturer "Test Manufacturer"
```

### Example 3: Standardize Easton Naming

**Problem**: Both "Easton" and "Easton Archery" exist as separate manufacturers.

**Solution**:
```bash
# Check arrow counts
python database_cleaner.py --list-arrows "Easton" | tail -1
python database_cleaner.py --list-arrows "Easton Archery" | tail -1

# Merge into standard "Easton Archery"
python database_cleaner.py --merge-manufacturers "Easton" "Easton Archery"
```

### Example 4: Database Health Check

**Problem**: Need to verify database integrity after imports.

**Solution**:
```bash
# Full database validation
python database_cleaner.py --validate

# Find and clean duplicates
python database_cleaner.py --find-duplicates
python database_cleaner.py --clean-duplicates
```

### Example 5: Complete Database Reset

**Problem**: Need to start fresh with a clean database schema.

**Solution**:
```bash
# Preview what would be deleted
python database_cleaner.py --stats

# Reset database schema (complete wipe)
python database_cleaner.py --reset-schema --dry-run
python database_cleaner.py --reset-schema

# Re-import fresh data
./production-import-only.sh
```

**Result**: Clean database with fresh schema ready for new data.

### Example 6: Selective Database Cleaning

**Problem**: Want to keep only specific manufacturers and remove everything else.

**Solution**:
```bash
# Preview selective cleaning
python database_cleaner.py --clean-keep "Easton" "Gold Tip" "Victory" --dry-run

# Execute selective clean
python database_cleaner.py --clean-keep "Easton" "Gold Tip" "Victory"

# Verify result
python database_cleaner.py --list-manufacturers
```

**Result**: Database contains only arrows from the specified manufacturers.

## Understanding Operations

### Rename vs Merge

**Rename**: Changes manufacturer name but ignores existing entries with target name
```bash
# If "Cross-X" already exists, this creates conflicts
python database_cleaner.py --rename-manufacturer "BigArchery" "Cross-X"
```

**Merge**: Combines manufacturers, moving all arrows to target manufacturer
```bash
# This safely combines BigArchery into existing Cross-X
python database_cleaner.py --merge-manufacturers "BigArchery" "Cross-X"
```

**Recommendation**: Use **merge** when target manufacturer already exists.

### Dry Run Mode

Always test destructive operations first:
```bash
# Preview what would happen
python database_cleaner.py --remove-manufacturer "BigArchery" --dry-run

# Execute if satisfied with preview
python database_cleaner.py --remove-manufacturer "BigArchery"
```

## Data Export Format

When saving manufacturer data, the script creates JSON files with this structure:

```json
{
  "export_metadata": {
    "manufacturer": "BigArchery",
    "export_date": "2025-08-03T09:45:00",
    "arrow_count": 35,
    "total_spine_specs": 175,
    "database_file": "arrow_database.db"
  },
  "arrows": [
    {
      "id": 1611,
      "manufacturer": "BigArchery",
      "model_name": "CROSS-X SHAFT AMBITION GOLD ED.",
      "material": "Carbon",
      "arrow_type": "target",
      "description": "Premium target arrow...",
      "spine_specifications": [
        {
          "id": 8234,
          "arrow_id": 1611,
          "spine": "500",
          "outer_diameter": 0.246,
          "inner_diameter": 0.166,
          "gpi_weight": 8.5,
          "length_options": "[\"30\", \"31\", \"32\"]"
        }
      ]
    }
  ]
}
```

## Database Validation Issues

The validator checks for common problems:

### Orphaned Spine Specifications
**Issue**: Spine specs referencing deleted arrows  
**Cause**: Incomplete deletion operations  
**Fix**: Automatic cleanup or manual review

### Arrows Without Spine Specs
**Issue**: Arrows with no spine data  
**Cause**: Import errors or incomplete data  
**Fix**: Add missing spine data or remove arrows

### Invalid Spine Values
**Issue**: Spine values outside normal range (100-2000)  
**Cause**: Data entry errors or import issues  
**Fix**: Correct spine values manually

### Missing Required Fields
**Issue**: Arrows without manufacturer or model name  
**Cause**: Import errors  
**Fix**: Fill missing data or remove invalid arrows

## Safety Features

### Automatic Backups
Before destructive operations, the script automatically creates timestamped backups:
```
arrow_database.db.backup_20250803_094530
```

### Dry Run Mode
All destructive operations support `--dry-run` for safe preview.

### Transaction Safety
All operations use database transactions - if an operation fails, no partial changes are applied.

## Full Database Operations

### Database Statistics
Get comprehensive database health metrics:
```bash
python database_cleaner.py --stats
```

**Output includes**:
- Total arrows, spine specifications, and manufacturers
- Data completeness percentages for descriptions, images, and materials
- Duplicate arrow group counts
- Missing data statistics

### Complete Database Wipe
Remove all arrow data while preserving schema:
```bash
# Preview first (ALWAYS recommended)
python database_cleaner.py --clean-all --dry-run

# Execute complete wipe
python database_cleaner.py --clean-all
```

**When to use**: Starting over with completely new data, removing all test data.

### Selective Database Cleaning
Keep only specific manufacturers:
```bash
# Preview selective cleaning
python database_cleaner.py --clean-keep "Easton" "Gold Tip" "Victory" --dry-run

# Execute selective clean
python database_cleaner.py --clean-keep "Easton" "Gold Tip" "Victory"
```

**When to use**: Focusing on specific manufacturers, removing low-quality data sources.

### Schema Reset (DANGEROUS)
Completely reset database structure:
```bash
# Preview schema reset
python database_cleaner.py --reset-schema --dry-run

# Execute schema reset (requires 'RESET' confirmation)
python database_cleaner.py --reset-schema
```

**When to use**: Database corruption, major schema changes, complete fresh start.

## Common Workflows

### Monthly Database Maintenance
```bash
# 1. Check database statistics
python database_cleaner.py --stats

# 2. Validate database health
python database_cleaner.py --validate

# 3. Find and clean duplicates
python database_cleaner.py --find-duplicates
python database_cleaner.py --clean-duplicates

# 4. Review manufacturer list
python database_cleaner.py --list-manufacturers
```

### After Data Import
```bash
# 1. Check for new duplicates
python database_cleaner.py --find-duplicates

# 2. Standardize manufacturer names
python database_cleaner.py --merge-manufacturers "Imported Name" "Standard Name"

# 3. Validate final state
python database_cleaner.py --validate
```

### Before Production Deployment
```bash
# 1. Clean all duplicates
python database_cleaner.py --clean-duplicates

# 2. Remove test data
python database_cleaner.py --remove-manufacturer "Test Manufacturer"

# 3. Final validation
python database_cleaner.py --validate
```

## Troubleshooting

### Operation Failed - Restore from Backup
```bash
# Restore from most recent backup
cp arrow_database.db.backup_YYYYMMDD_HHMMSS arrow_database.db
```

### Large Merge Operations
For manufacturers with 100+ arrows, operations may take time. The script provides progress updates.

### Foreign Key Constraints
The script handles foreign key relationships automatically:
1. Removes spine specifications before removing arrows
2. Updates relationships during merges
3. Validates referential integrity

## Integration with Other Tools

### With TopHat Import
```bash
# After TopHat import, standardize manufacturer names
python tophat_data_import.py --add-new-manufacturers
python database_cleaner.py --merge-manufacturers "Carbon" "Carbon Express"
python database_cleaner.py --merge-manufacturers "Gold" "Gold Tip"
```

### With Production Import
```bash
# Clean database before production import
python database_cleaner.py --clean-duplicates
./production-import-only.sh
```

## Advanced Usage

### Batch Operations Script
Create custom scripts for repeated operations:

```bash
#!/bin/bash
# batch_clean.sh - Standardize manufacturer names

echo "Standardizing manufacturer names..."
python database_cleaner.py --merge-manufacturers "BigArchery" "Cross-X"
python database_cleaner.py --merge-manufacturers "Carbon" "Carbon Express"  
python database_cleaner.py --merge-manufacturers "Gold" "Gold Tip"
python database_cleaner.py --merge-manufacturers "Black" "Black Eagle"

echo "Cleaning duplicates..."
python database_cleaner.py --clean-duplicates

echo "Final validation..."
python database_cleaner.py --validate

echo "Database cleaning complete!"
```

### Manufacturer Audit Report
```bash
# Generate comprehensive manufacturer report
python database_cleaner.py --list-manufacturers > manufacturer_report.txt
python database_cleaner.py --find-duplicates >> manufacturer_report.txt
python database_cleaner.py --validate >> manufacturer_report.txt
```

## Conclusion

The Database Cleaner provides essential tools for maintaining a high-quality arrow database. Regular use of validation and cleaning features ensures optimal performance of your archery tools platform.

For questions or issues, refer to the script's built-in help:
```bash
python database_cleaner.py --help
```