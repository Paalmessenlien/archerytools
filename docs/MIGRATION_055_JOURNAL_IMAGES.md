# Migration 055: Journal Images Column

## Overview

Migration 055 adds an `images` column to the `journal_entries` table to support direct JSON storage of image arrays. This migration was created to support the enhanced image upload functionality in journal entries and tuning sessions.

## Changes Made

### Database Schema Changes

1. **Added `images` column to `journal_entries` table**
   - Type: `TEXT` (stores JSON array)
   - Purpose: Store image objects directly in journal entries
   - Format: JSON array of image objects

2. **Created performance index**
   - Index: `idx_journal_entries_with_images`
   - Optimizes queries for entries with images

3. **Migration of existing data**
   - Automatically migrates existing `journal_attachments` to the new `images` column
   - Preserves backward compatibility with the existing attachment system

### Image Object Structure

Each image object in the JSON array contains:
```json
{
  "url": "https://cdn.example.com/image.jpg",
  "alt": "Descriptive text",
  "uploadedAt": "2025-09-10T14:30:00.000Z",
  "originalFilename": "test_shot.jpg",
  "fileType": "image",
  "fileSize": 245760,
  "isPrimary": false
}
```

### Enhanced Tuning Session Support

The migration specifically supports the enhanced tuning session functionality:

- **Paper Tuning**: Images labeled with test numbers and tear patterns
- **Bareshaft Tuning**: Images labeled with test numbers and impact patterns  
- **Walkback Tuning**: Images labeled with test numbers and distances

## Deployment

### Manual Deployment

Run the migration directly:
```bash
cd arrow_scraper/migrations
python 055_add_journal_images_column.py
```

### Automated Deployment

Use the deployment script:
```bash
./deploy_migrations.sh
```

### Production Deployment

The migration is designed to run safely in production:

1. **Zero-downtime**: Uses table recreation for schema changes
2. **Data preservation**: All existing journal entries are preserved
3. **Backward compatibility**: Existing `journal_attachments` continue to work
4. **Automatic migration**: Existing attachments are automatically migrated to the new format

## Technical Details

### Migration Process

1. **Schema Update**: Recreates the `journal_entries` table with the new `images` column
2. **Data Migration**: Copies all existing data to the new table structure
3. **Index Creation**: Adds performance indexes for image queries
4. **Trigger Restoration**: Restores full-text search triggers
5. **Attachment Migration**: Converts existing `journal_attachments` to JSON format

### Error Handling

- **Rollback Support**: Full transaction rollback on any error
- **Validation**: Checks for existing columns before making changes
- **Graceful Degradation**: Continues if some optional steps fail

### Performance Considerations

- **Indexed Queries**: New index optimizes image-related queries
- **JSON Storage**: Efficient storage of image metadata
- **Query Optimization**: Supports `WHERE images IS NOT NULL` queries efficiently

## Benefits

### For Users

1. **Integrated Image Display**: Images appear directly in journal entries
2. **Tuning Documentation**: Visual documentation of tuning sessions
3. **Enhanced UI**: Improved journal viewing experience

### For Developers

1. **Simplified Access**: Direct JSON access to image arrays
2. **Frontend Integration**: Easy integration with Vue components
3. **API Consistency**: Unified image handling across all journal types

## Compatibility

### Backward Compatibility

- ✅ Existing journal entries continue to work
- ✅ Existing `journal_attachments` are preserved
- ✅ API endpoints remain functional
- ✅ No breaking changes to existing functionality

### Forward Compatibility

- ✅ Supports future image enhancement features
- ✅ Extensible JSON structure for additional metadata
- ✅ Compatible with CDN integration
- ✅ Supports multiple image formats

## Testing

### Validation Steps

1. **Schema Validation**: Confirm `images` column exists
2. **Data Integrity**: Verify all existing data is preserved
3. **Index Performance**: Test query performance with new indexes
4. **Migration Verification**: Confirm attachment migration completed

### Test Commands

```bash
# Check schema
sqlite3 databases/arrow_database.db "PRAGMA table_info(journal_entries);"

# Verify images column
sqlite3 databases/arrow_database.db "SELECT COUNT(*) FROM journal_entries WHERE images IS NOT NULL;"

# Test performance
sqlite3 databases/arrow_database.db ".explain SELECT * FROM journal_entries WHERE images IS NOT NULL;"
```

## Troubleshooting

### Common Issues

1. **Migration Fails**: Check database permissions and disk space
2. **Data Loss**: Migration includes full rollback on any error
3. **Performance**: New indexes may take time to build on large databases

### Recovery

If migration fails:
```bash
# Run downgrade migration
cd arrow_scraper/migrations
python 055_add_journal_images_column.py down
```

## Related Files

### Migration Files
- `arrow_scraper/migrations/055_add_journal_images_column.py` - Main migration
- `deploy_migrations.sh` - Deployment script

### Frontend Files
- `frontend/pages/tuning-session/paper/[sessionId].vue` - Paper tuning images
- `frontend/pages/tuning-session/bareshaft/[sessionId].vue` - Bareshaft tuning images  
- `frontend/pages/tuning-session/walkback/[sessionId].vue` - Walkback tuning images
- `frontend/components/JournalEntryViewer.vue` - Image display
- `frontend/components/JournalEntryDialog.vue` - Image upload

### Backend Files
- `arrow_scraper/api.py` - Journal entry API endpoints

## Version Information

- **Migration Version**: 055
- **Created**: September 10, 2025
- **Dependencies**: Migration 038 (Journal System), Migration 041 (Image Upload System)
- **Target**: Unified Database (`arrow_database.db`)
- **Environment**: All (development, staging, production)