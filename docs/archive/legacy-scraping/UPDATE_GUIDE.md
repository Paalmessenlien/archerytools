# Arrow Database Update Guide

## Overview

The Arrow Tuning System now supports comprehensive manufacturer updates through the enhanced scraping system. This allows you to keep the arrow database current with the latest specifications from all supported manufacturers.

## Supported Manufacturers

The update system supports 9+ manufacturers:

### Primary Manufacturers (from config/settings.py)
- **Easton Archery** - Full category scraping
- **Gold Tip** - Hunting and target arrows  
- **Victory Archery** - Hunting and target arrows
- **Skylon Archery** - Premium target arrows

### Comprehensive Manufacturers (from scrape_all_manufacturers.py)
- **Nijora Archery** - European traditional and modern arrows
- **DK Bow** - German precision arrows
- **Pandarus Archery** - Competition target arrows  
- **BigArchery** - Wide range of arrow types
- **Carbon Express** - Popular hunting arrows

## Update Commands

### Method 1: Using main.py (Recommended)

```bash
# Update all manufacturers (skip existing data)
python main.py --update-all

# Force update all manufacturers (overwrites existing data)
python main.py --update-all --force

# Update single manufacturer
python main.py easton
python main.py goldtip

# List available manufacturers
python main.py --list-manufacturers

# Get help
python main.py --help
```

### Method 2: Using update_all.py (Simple wrapper)

```bash
# Interactive update with confirmation
python update_all.py

# Force update (overwrites existing)
python update_all.py --force

# Get help
python update_all.py --help
```

## Requirements

### 1. Environment Setup
Create a `.env` file in the scraper directory:
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 2. Python Dependencies
```bash
pip install crawl4ai python-dotenv asyncio aiohttp
```

### 3. Virtual Environment (Recommended)
```bash
source venv/bin/activate  # If using the existing venv
```

## Update Process

The update system follows this process:

1. **Initialize**: Load API keys and database connections
2. **Check Existing**: For each manufacturer, check if data already exists
3. **Scrape**: Extract arrow specifications from manufacturer websites
4. **Process**: Normalize and validate arrow data
5. **Update**: Add new arrows to the database
6. **Summary**: Report results and statistics

### Typical Update Flow

```
🚀 Starting comprehensive manufacturer update...
========================================================
📊 Updating 9 manufacturers...
🔄 Force update: No

[1/9] 🏹 Processing: Easton Archery
----------------------------------------
✅ Easton Archery: 15 arrows processed
⏱️  Waiting 5 seconds...

[2/9] 🏹 Processing: Gold Tip  
----------------------------------------
ℹ️  Found 12 existing arrows - skipping
   Use --force to update existing data

... (continues for all manufacturers)

========================================================
📋 UPDATE SUMMARY
========================================================
⏱️  Total time: 325.6 seconds
🏢 Manufacturers processed: 6/9
🏹 Total arrows found: 127
✅ Success rate: 66.7%

💾 Database now contains:
   • 289 arrows
   • 9 manufacturers

🎯 Update completed successfully!
```

## Update Strategies

### 1. Regular Updates (Default)
- Skips manufacturers that already have data
- Adds only new manufacturers
- Fast and safe for routine updates
- Recommended frequency: Weekly

```bash
python main.py --update-all
```

### 2. Force Updates  
- Updates all manufacturers regardless of existing data
- Overwrites existing arrow specifications
- Slower but ensures latest data
- Recommended frequency: Monthly

```bash
python main.py --update-all --force
```

### 3. Selective Updates
- Update specific manufacturers only
- Useful for testing or targeted updates

```bash
python main.py easton       # Update Easton only
python main.py goldtip      # Update Gold Tip only
```

## Database Integration

Updated arrows are automatically integrated with the existing database:

- **Arrow Database**: `arrow_database.db` - SQLite database with all specifications
- **Web Interface**: Updated data appears immediately in the web interface
- **Tuning System**: New arrows available for tuning recommendations
- **Search System**: Enhanced search with updated arrow data

## Error Handling

The update system includes comprehensive error handling:

- **Network Issues**: Automatic retries with backoff
- **API Limits**: Respectful delays between requests  
- **Data Validation**: Ensures arrow specifications are complete
- **Database Conflicts**: Handles duplicate entries gracefully

### Common Issues

1. **API Key Missing**
   ```
   Error: DEEPSEEK_API_KEY not set
   Solution: Add key to .env file
   ```

2. **Network Timeout**
   ```
   Error: Failed to fetch category page
   Solution: Check internet connection, try again
   ```

3. **Database Lock**
   ```
   Error: SQLite objects created in thread
   Solution: Ensure no other processes accessing database
   ```

## Performance Considerations

- **Time**: Full update takes 10-15 minutes
- **Rate Limiting**: 5-second delays between manufacturers
- **Memory**: ~50MB peak memory usage
- **Storage**: ~2MB additional database size per update

## Monitoring Updates

### Real-time Progress
The update system provides detailed progress information:
- Current manufacturer being processed
- Number of arrows found per manufacturer  
- Time estimates and completion percentage
- Error notifications with context

### Post-Update Verification
After updates, verify results:

```bash
# Check database statistics
python -c "
from arrow_database import ArrowDatabase
db = ArrowDatabase()
print(f'Total arrows: {db.get_total_arrow_count()}')
print(f'Manufacturers: {len(db.get_unique_manufacturers())}')
"

# Check web interface
python start_server.py  # Then visit http://localhost:5000
```

## Integration with Web Interface

Updated arrows are immediately available in the web interface:

- **Homepage**: Updated statistics and counts
- **Arrow Database**: Browse new and updated arrows
- **Search System**: Find arrows with latest specifications
- **Tuning Wizard**: Get recommendations with updated data
- **Comparison Tool**: Compare arrows using latest specs

## Best Practices

1. **Backup Database**: Backup `arrow_database.db` before major updates
2. **Test Updates**: Use single manufacturer updates to test functionality
3. **Monitor Logs**: Check console output for errors or warnings
4. **Verify Results**: Check web interface after updates
5. **Schedule Updates**: Set up regular update schedule

## Troubleshooting

### Debug Mode
Enable verbose logging for troubleshooting:

```bash
export PYTHONPATH=/home/paal/arrowtuner2/arrow_scraper
python -u main.py --update-all --force 2>&1 | tee update.log
```

### Manual Database Check
Verify database integrity:

```python
import sqlite3
conn = sqlite3.connect('arrow_database.db')
cursor = conn.cursor()

# Check arrow count
cursor.execute('SELECT COUNT(*) FROM arrows')
print(f"Total arrows: {cursor.fetchone()[0]}")

# Check manufacturers
cursor.execute('SELECT DISTINCT manufacturer FROM arrows')
manufacturers = [row[0] for row in cursor.fetchall()]
print(f"Manufacturers: {manufacturers}")
```

## Support

For issues with the update system:

1. Check this guide for common solutions
2. Review console output for specific errors
3. Verify API key and network connectivity
4. Test with single manufacturer updates first

The update system is designed to be robust and handle most common issues automatically. Regular updates will keep your arrow database current with the latest manufacturer specifications.