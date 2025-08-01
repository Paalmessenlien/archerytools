# Production Database Migration Instructions

## Issue
Production is showing error: `table bow_setups has no column named riser_brand`

This means the production database is missing columns that were added in recent updates.

## Solution

### Method 1: Run Migration Script (Recommended)

1. **Upload migration script to production server:**
   ```bash
   scp migrate_bow_setups_columns.py user@your-server:/path/to/arrowtuner/
   ```

2. **Run migration on production server:**
   ```bash
   cd /path/to/arrowtuner
   python migrate_bow_setups_columns.py
   ```

3. **Restart the application:**
   ```bash
   sudo docker-compose -f docker-compose.ssl.yml restart
   ```

### Method 2: Manual Column Addition

If you prefer to run the SQL manually:

```sql
-- Connect to the production database
sqlite3 arrow_scraper/user_data.db

-- Add missing columns
ALTER TABLE bow_setups ADD COLUMN riser_brand TEXT;
ALTER TABLE bow_setups ADD COLUMN riser_length TEXT;
ALTER TABLE bow_setups ADD COLUMN limb_brand TEXT;
ALTER TABLE bow_setups ADD COLUMN limb_length TEXT;
ALTER TABLE bow_setups ADD COLUMN compound_brand TEXT;

-- Verify columns exist
.schema bow_setups

-- Exit
.quit
```

### Method 3: Deploy Latest Code (Includes Migration)

1. **Pull latest changes:**
   ```bash
   git pull
   ```

2. **Rebuild containers:**
   ```bash
   sudo docker-compose -f docker-compose.ssl.yml down
   sudo docker-compose -f docker-compose.ssl.yml up -d --build
   ```

## Verification

After running any method, verify the fix works:

```bash
# Check that the application starts without errors
sudo docker-compose -f docker-compose.ssl.yml logs api

# Test the bow setup functionality
curl https://yourdomain.com/api/health
```

## What This Fixes

The migration adds these missing columns to the `bow_setups` table:
- `riser_brand` - For recurve/traditional bow riser manufacturers
- `riser_length` - For custom riser lengths
- `limb_brand` - For recurve/traditional bow limb manufacturers  
- `limb_length` - For custom limb lengths
- `compound_brand` - For compound bow manufacturers

These columns were added in recent updates but the production database wasn't migrated.

## Prevention

This issue has been fixed in the codebase - the `user_database.py` now includes all required columns in the initial table creation, so future deployments won't have this problem.