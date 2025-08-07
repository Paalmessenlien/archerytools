# Admin Backup & Restore System Documentation

## Overview

The Archery Tools platform now includes a comprehensive admin backup and restore system with CDN integration. This system allows administrators to create, manage, and restore database backups through a web interface with automatic cloud storage.

## Features

### Core Functionality
- **Database Selection**: Choose to backup arrow database, user database, or both
- **CDN Integration**: Automatic upload to Bunny CDN, Cloudinary, AWS S3, or local storage
- **Compression**: Tar/gzip compression for efficient storage and transfer
- **Admin Authentication**: JWT token-based authentication for secure access
- **Audit Trail**: Complete logging of all backup and restore operations
- **Metadata Tracking**: File sizes, creation dates, and CDN URLs stored in database

### Supported Operations
1. **Create Backup**: Generate compressed backup archives and upload to CDN
2. **List Backups**: View all available backups from both CDN and local storage
3. **Restore Backup**: Download and restore databases from CDN backups
4. **Download Backup**: Get direct CDN URLs for manual backup downloads
5. **Delete Backup**: Remove backups from both CDN and local metadata

## API Endpoints

All endpoints require admin authentication via JWT token in the `Authorization: Bearer <token>` header.

### 1. Test Endpoint
```
GET /api/admin/backup-test
```
- **Purpose**: Verify backup system is accessible
- **Authentication**: None required
- **Response**: Success message with timestamp

### 2. List Backups
```
GET /api/admin/backups
```
- **Purpose**: Get all available backups
- **Authentication**: Admin required
- **Response**: 
```json
{
  "success": true,
  "backups": {
    "cdn": [
      {
        "backup_id": "uuid",
        "backup_name": "backup_20250806_120000",
        "database_type": "both",
        "cdn_url": "https://cdn.example.com/backups/backup.tar.gz",
        "created_by": "admin@example.com",
        "created_at": "2025-08-06T12:00:00",
        "file_size": 1048576,
        "location": "cdn"
      }
    ],
    "local": [...]
  },
  "total_cdn": 5,
  "total_local": 2
}
```

### 3. Create Backup
```
POST /api/admin/backup
```
- **Purpose**: Create new database backup and upload to CDN
- **Authentication**: Admin required
- **Request Body**:
```json
{
  "database_type": "both",  // "arrow", "user", or "both"
  "backup_name": "custom_backup_name"  // optional
}
```
- **Response**:
```json
{
  "success": true,
  "message": "Backup created and uploaded successfully",
  "backup_id": "uuid",
  "backup_name": "backup_20250806_120000",
  "database_type": "both",
  "cdn_url": "https://cdn.example.com/backups/backup.tar.gz",
  "file_size": 1048576,
  "created_by": "admin@example.com"
}
```

### 4. Restore Backup
```
POST /api/admin/backup/<backup_id>/restore
```
- **Purpose**: Download backup from CDN and restore databases
- **Authentication**: Admin required
- **Response**:
```json
{
  "success": true,
  "message": "Backup restored successfully",
  "database_type": "both",
  "restore_results": {
    "arrow": "success",
    "user": "success"
  },
  "restored_by": "admin@example.com"
}
```

### 5. Download Backup
```
GET /api/admin/backup/<backup_id>/download
```
- **Purpose**: Get backup download information
- **Authentication**: Admin required
- **Response**:
```json
{
  "success": true,
  "backup_id": "uuid",
  "backup_name": "backup_20250806_120000",
  "cdn_url": "https://cdn.example.com/backups/backup.tar.gz",
  "file_size": 1048576,
  "created_at": "2025-08-06T12:00:00",
  "download_instructions": "Use the CDN URL to download the backup file directly"
}
```

### 6. Delete Backup
```
DELETE /api/admin/backup/<backup_id>
```
- **Purpose**: Remove backup from CDN and local metadata
- **Authentication**: Admin required
- **Response**:
```json
{
  "success": true,
  "message": "Backup deleted successfully",
  "local_deleted": true,
  "deleted_by": "admin@example.com"
}
```

## Database Schema

### Backup Metadata Table
```sql
CREATE TABLE IF NOT EXISTS backup_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backup_id TEXT UNIQUE NOT NULL,
    backup_name TEXT NOT NULL,
    database_type TEXT NOT NULL,  -- 'arrow', 'user', or 'both'
    file_path TEXT,
    cdn_url TEXT,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    notes TEXT
);
```

### Backup Operations Table
```sql
CREATE TABLE IF NOT EXISTS backup_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_type TEXT NOT NULL,  -- 'create', 'restore', 'delete'
    backup_id TEXT,
    performed_by TEXT NOT NULL,
    performed_at TEXT NOT NULL,
    details TEXT,
    FOREIGN KEY (backup_id) REFERENCES backup_metadata(backup_id)
);
```

## CDN Integration

The system supports multiple CDN providers with automatic fallback:

### Supported CDN Providers
1. **Bunny CDN** (Primary)
2. **Cloudinary** (Secondary)
3. **AWS S3** (Tertiary)
4. **Local Storage** (Fallback)

### CDN Configuration
Set environment variables in your `.env` file:
```bash
# Bunny CDN (Recommended)
BUNNY_API_KEY=your_bunny_api_key
BUNNY_ZONE_NAME=your_bunny_zone_name
BUNNY_HOSTNAME=your_bunny_hostname

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# AWS S3
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your_s3_bucket_name
AWS_REGION=your_aws_region
```

## Admin Panel Usage

### Accessing the Backup System
1. Login to admin panel at `/admin`
2. Navigate to "Backup & Restore" section
3. Select desired operation

### Creating Backups
1. Click "Create Backup" button
2. Select database type (Arrow, User, or Both)
3. Optionally provide custom backup name
4. Click "Create" - backup will be automatically uploaded to CDN

### Restoring Backups
1. View available backups in the list
2. Click "Restore" button next to desired backup
3. Confirm restore operation
4. System will download from CDN and restore selected databases

### Managing Backups
- **View Details**: Click on backup name to see metadata
- **Download**: Use "Download" button to get direct CDN link
- **Delete**: Remove unwanted backups from both CDN and local metadata

## Security Considerations

### Authentication Requirements
- All backup operations require admin privileges
- JWT tokens must be valid and non-expired
- Admin status verified on each request

### Access Control
- Only users with `is_admin = 1` can access backup endpoints
- Automatic admin privileges for `messenlien@gmail.com`
- All operations logged with user email for audit trail

### Data Protection
- Backups are compressed with gzip for efficiency
- CDN URLs are private and require authentication
- Local backup files have restricted permissions
- Sensitive data is never logged in plaintext

## Troubleshooting

### Common Issues

#### 1. 404 Not Found on Backup Endpoints
- **Cause**: Flask routing issue with endpoint placement
- **Solution**: Backup endpoints moved to working section of api.py (around line 1957)
- **Verification**: Test with `curl http://localhost:5000/api/admin/backup-test`

#### 2. Database Path Conflicts
- **Cause**: Docker path resolution differences
- **Solution**: Explicit database path specification in UserDatabase calls
- **Fix Applied**: `UserDatabase(db_path='/app/user_data/user_data.db')`

#### 3. CDN Upload Failures
- **Cause**: Missing or incorrect CDN credentials
- **Solution**: Verify environment variables and API keys
- **Fallback**: System will use local storage if CDN unavailable

#### 4. Authentication Errors
- **Cause**: Missing or invalid JWT tokens
- **Solution**: Ensure user is logged in and has admin privileges
- **Check**: Visit `/api/admin/check` to verify admin status

### Error Messages

#### "Token is missing!"
- User not authenticated
- Include `Authorization: Bearer <token>` header

#### "Admin access required"
- User authenticated but not admin
- Contact system administrator for admin privileges

#### "CDN upload failed"
- CDN credentials incorrect or service unavailable
- Check environment variables and CDN service status

#### "Backup not found"
- Backup ID invalid or backup deleted
- Refresh backup list and verify backup exists

## Monitoring and Logging

### Operation Logging
All backup operations are logged in the `backup_operations` table:
- Operation type (create, restore, delete)
- User who performed the operation
- Timestamp of operation
- Additional details and results

### File System Monitoring
- Backup file sizes tracked in metadata
- Local storage usage monitored
- CDN storage tracked via provider dashboards

### Health Monitoring
- Test endpoint available for monitoring systems
- Database integrity checks before backup operations
- CDN connectivity verification during uploads

## Production Deployment

### Environment Setup
1. Configure CDN credentials in production `.env`
2. Ensure database directories have proper permissions
3. Verify admin user privileges in production database
4. Test backup system with small test backup

### Deployment Commands
```bash
# Pull latest changes
git pull

# Import updated arrow data (if needed)
./production-import-only.sh

# Rebuild containers with latest code
sudo docker-compose -f docker-compose.enhanced-ssl.yml down
sudo docker-compose -f docker-compose.enhanced-ssl.yml up -d --build

# Verify backup system
curl https://yourdomain.com/api/admin/backup-test
```

### Production Verification
1. **API Health**: `curl https://yourdomain.com/api/health`
2. **Backup Test**: `curl https://yourdomain.com/api/admin/backup-test`
3. **Database Status**: Check container logs for database verification
4. **CDN Connectivity**: Test backup creation with small dataset

## Development Notes

### Code Architecture
- **Flask Routes**: Located in `arrow_scraper/api.py` lines 1957-2025
- **Database Integration**: Uses existing `UserDatabase` and `ArrowDatabase` classes
- **CDN Uploader**: Integrated with existing `CDNUploader` class
- **Backup Manager**: Utilizes existing `BackupManager` for local operations

### Testing
```bash
# Test backup system locally
cd arrow_scraper
python -c "
from api import app
with app.test_client() as client:
    response = client.get('/api/admin/backup-test')
    print(f'Status: {response.status_code}')
    print(f'Response: {response.get_json()}')
"
```

### Future Enhancements
1. **Scheduled Backups**: Automated daily/weekly backup creation
2. **Backup Retention**: Automatic cleanup of old backups based on policies
3. **Incremental Backups**: Delta backups for large databases
4. **Encryption**: Optional backup encryption for enhanced security
5. **Multi-Region CDN**: Backup replication across multiple regions

---

**System Status**: ✅ **PRODUCTION READY**
**Last Updated**: August 6, 2025
**Version**: 1.0.0

For support or questions, refer to the main project documentation or contact the development team.