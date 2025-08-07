# Database Import System Documentation

## Overview

The Database Import System automatically imports arrow data from JSON files during server startup, ensuring the database always reflects the latest scraped data. This implements the user's requirement: "Always use the json files as main data for the database."

## Key Features

- **Automatic Import**: Runs during server startup to check for new JSON data
- **JSON-First Architecture**: JSON files are the authoritative data source
- **Smart Updates**: Only imports when JSON files are newer than database
- **Manufacturer-Level Replacement**: Updates data per manufacturer, not per arrow
- **Error Handling**: Continues processing other manufacturers if one fails
- **Comprehensive Logging**: Detailed progress and error reporting

## Components

### 1. Database Import Manager (`database_import_manager.py`)

Main component that handles:
- Scanning `data/processed/` for JSON files
- Comparing file timestamps with database modification time
- Importing arrow data and spine specifications
- Managing manufacturer-level data replacement

#### Key Methods:

- `run_startup_import()`: Main entry point for server startup
- `check_for_updates()`: Determines if database needs updating
- `import_all_json_files()`: Processes all JSON files and imports data
- `clear_manufacturer_data()`: Removes existing data before import
- `import_arrow_data()`: Imports arrows and spine specifications

### 2. Server Startup Integration (`start-api-robust.sh`)

Enhanced startup script includes new Step 4:
```bash
# Step 4: Database Import from JSON Files
run_database_import
```

The import process:
1. Checks if `database_import_manager.py` exists
2. Runs import with proper database and data directory paths
3. Logs success/failure status
4. Continues server startup regardless of import result

## Supported JSON File Formats

The system automatically detects and processes multiple JSON file naming patterns:

- `Manufacturer_Name_update_YYYYMMDD_HHMMSS.json` (full updates)
- `Manufacturer_Name_learn_YYYYMMDD_HHMMSS.json` (pattern learning)
- `Manufacturer_Name_test_YYYYMMDD_HHMMSS.json` (test data)

### Example JSON Structure:
```json
{
  "manufacturer": "DK Bow",
  "total_arrows": 4,
  "scraped_at": "2025-08-01T15:36:32.809002",
  "extraction_method": "comprehensive_update",
  "arrows": [
    {
      "manufacturer": "DK Bow",
      "model_name": "DK Cougar Carbon Arrow - ID 4.2",
      "spine_specifications": [
        {
          "spine": 600,
          "outer_diameter": 0.226,
          "gpi_weight": 7.14
        }
      ],
      "material": "hochmodulares Carbon",
      "arrow_type": "target",
      "description": "Arrow description...",
      "source_url": "https://example.com/arrow",
      "primary_image_url": "https://example.com/image.jpg"
    }
  ]
}
```

## Database Schema Compatibility

The import system maps JSON fields to database schema:

### Arrows Table:
- `manufacturer` → `manufacturer`
- `model_name` → `model_name`
- `material` → `material` (normalized)
- `arrow_type` → `arrow_type`
- `description` → `description`
- `source_url` → `source_url`
- `primary_image_url` → `image_url`

### Spine Specifications Table:
- `spine` → `spine`
- `outer_diameter` → `outer_diameter`
- `inner_diameter` → `inner_diameter`
- `gpi_weight` → `gpi_weight`

## Update Logic

### When Updates Occur:
1. **Database doesn't exist**: Creates new database from JSON files
2. **Database is empty**: Imports all JSON files to populate database
3. **JSON files newer than database**: Updates database with newer JSON data
4. **No JSON files found**: No update needed, uses existing database

### Update Process:
1. Scan `data/processed/` directory for JSON files
2. Group files by manufacturer (uses latest file per manufacturer)
3. For each manufacturer:
   - Clear existing arrows and spine specifications
   - Import new data from JSON file
   - Log success/failure status
4. Report final statistics

## Usage Examples

### Manual Testing:
```bash
# Check if updates are needed
python3 database_import_manager.py --check

# Force import all JSON files
python3 database_import_manager.py --import-all --force

# Run startup import (default mode)
python3 database_import_manager.py
```

### Server Startup Integration:
The import runs automatically during server startup via `start-api-robust.sh`:
```bash
./start-api-robust.sh
```

### Expected Output:
```
🔍 Step 4: Database Import from JSON Files
==========================================
📥 Running database import from JSON files...
🔄 Running database import manager...
📦 Starting database import from JSON files...
Found 12 manufacturers to import: ['DK Bow', 'Pandarus Archery', ...]
📋 Processing DK Bow from DK_Bow_update_20250801_153632.json
✅ Imported 4 arrows for DK Bow
...
🎯 Import complete: 12 files, 110 arrows, 12 manufacturers
✅ Database import completed successfully
```

## Error Handling

### Common Issues and Solutions:

1. **Missing JSON files**: System continues with existing database
2. **Invalid JSON format**: Skips file and logs warning
3. **Database schema mismatch**: Maps fields appropriately
4. **Duplicate arrow names**: Uses UNIQUE constraint, logs warning
5. **Import manager not found**: Skips import, logs warning

### Logging Levels:
- **INFO**: Normal operation progress
- **WARNING**: Non-critical issues (duplicate arrows, missing fields)
- **ERROR**: Critical failures that stop processing

## Performance Characteristics

### Typical Import Performance:
- **12 manufacturers**: ~3-5 seconds
- **110+ arrows**: Complete replacement
- **Database size**: ~500KB typical
- **Memory usage**: Minimal (processes one manufacturer at a time)

### Optimization Features:
- Uses latest file per manufacturer (ignores older files)
- Batch operations for spine specifications
- Efficient SQL queries with proper indexing
- Rollback on transaction failures

## Integration Benefits

1. **Data Consistency**: JSON files are always the source of truth
2. **No Server-Side Scraping**: Production servers never scrape websites
3. **Development Workflow**: Scrape locally → commit JSON → deploy
4. **Zero Downtime**: Import runs before server starts
5. **Fault Tolerance**: Server starts even if import fails
6. **Audit Trail**: Complete logging of all import operations

## Production Deployment

The system integrates seamlessly with the enhanced Docker deployment:

```bash
# Enhanced deployment automatically includes database import
./deploy-enhanced.sh docker-compose.enhanced-ssl.yml

# Import runs during container startup
# Check logs to verify import success
```

### Docker Integration:
- Import manager copied to `/app/database_import_manager.py`
- Data directory mounted at `/app/data/processed`
- Database path configured as `/app/arrow_database.db`
- Logs integrated with container logging system

## Monitoring and Maintenance

### Health Checks:
- Import success/failure logged during startup
- Database arrow count reported
- File processing statistics available
- Error conditions clearly identified

### Regular Maintenance:
- JSON files accumulate over time (consider archiving old files)
- Database grows with new manufacturers/arrows
- Log files may need rotation
- Backup database before major updates

## Conclusion

The Database Import System successfully implements the requirement to use JSON files as the main data source for the database. It provides automatic, reliable, and efficient import functionality that integrates seamlessly with the server startup process, ensuring data consistency and eliminating the need for server-side web scraping in production environments.