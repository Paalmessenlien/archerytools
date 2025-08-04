# 🔧 Production Fixes Guide

This document addresses specific production issues found in the logs and provides solutions.

## 🚨 Current Production Issues

### **Issue 1: Development Server Warning**
**Log Entry:**
```
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
```

**Root Cause:**
- Flask development server is being used in production
- Not suitable for production traffic and performance

**Solution:**
Add Gunicorn WSGI server to the production API container.

### **Issue 2: Database Schema Missing Columns**
**Log Entry:**
```
⚠  Could not create indexes (database may be read-only): no such column: arrow_type
```

**Root Cause:**
- Database schema is outdated and missing newer columns like `arrow_type`
- Index creation failing due to missing columns

**Solution:**
Update database schema to include all required columns.

### **Issue 3: Database Path Inconsistency**
**Log Entry:**
```
📊 Arrow database: /app/arrow_data/arrow_database.db
👤 User database: /app/user_data/user_data.db
```

**Expected:**
```
📊 Arrow database: /app/arrow_database.db
👤 User database: /app/user_data/user_data.db
```

**Root Cause:**
- Production is using old Docker volume paths instead of unified paths
- Environment variables not properly set

## 🛠️ Quick Production Fixes

### **Fix 1: Add Production WSGI Server**

**On Production Server:**
```bash
# 1. Update requirements.txt to include gunicorn
docker-compose -f docker-compose.unified.yml exec api pip install gunicorn

# 2. Create production startup command
docker-compose -f docker-compose.unified.yml exec api bash -c "
cat > /app/start-production.sh << 'EOF'
#!/bin/bash
echo '🚀 Starting ArrowTuner API with Gunicorn (Production WSGI Server)...'
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class sync --timeout 120 --keep-alive 5 --max-requests 1000 --preload api:app
EOF
chmod +x /app/start-production.sh
"

# 3. Restart with production server
docker-compose -f docker-compose.unified.yml restart api
```

### **Fix 2: Update Database Schema**

**On Production Server:**
```bash
# 1. Fix database schema by running migration
docker-compose -f docker-compose.unified.yml exec api python3 -c "
import sqlite3
import os

# Connect to arrow database
db_path = os.environ.get('ARROW_DATABASE_PATH', '/app/arrow_database.db')
if not os.path.exists(db_path):
    db_path = '/app/arrow_data/arrow_database.db'  # Fallback to old path

print(f'Updating database schema: {db_path}')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add missing columns if they don't exist
    try:
        cursor.execute('ALTER TABLE arrows ADD COLUMN arrow_type TEXT')
        print('✅ Added arrow_type column')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print('✅ arrow_type column already exists')
        else:
            print(f'⚠️  Could not add arrow_type column: {e}')
    
    # Add other potentially missing columns
    missing_columns = [
        ('carbon_content', 'TEXT'),
        ('straightness_tolerance', 'TEXT'),
        ('weight_tolerance', 'TEXT'),
        ('source_url', 'TEXT'),
        ('scraped_at', 'TEXT'),
        ('primary_image_url', 'TEXT')
    ]
    
    for column_name, column_type in missing_columns:
        try:
            cursor.execute(f'ALTER TABLE arrows ADD COLUMN {column_name} {column_type}')
            print(f'✅ Added {column_name} column')
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e):
                print(f'✅ {column_name} column already exists')
            else:
                print(f'⚠️  Could not add {column_name} column: {e}')
    
    # Create missing indexes
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_arrows_arrow_type ON arrows(arrow_type)',
        'CREATE INDEX IF NOT EXISTS idx_arrows_material ON arrows(material)',
        'CREATE INDEX IF NOT EXISTS idx_arrows_manufacturer ON arrows(manufacturer)',
        'CREATE INDEX IF NOT EXISTS idx_arrows_model ON arrows(model_name)'
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
            print(f'✅ Created index: {index_sql.split()[-1]}')
        except sqlite3.OperationalError as e:
            print(f'⚠️  Could not create index: {e}')
    
    conn.commit()
    conn.close()
    print('✅ Database schema update completed')
    
except Exception as e:
    print(f'❌ Database schema update failed: {e}')
"
```

### **Fix 3: Correct Database Paths**

**Option A: Update Environment Variables**
```bash
# Edit docker-compose.unified.yml to use correct paths
docker-compose -f docker-compose.unified.yml down

# Edit the environment variables in docker-compose.unified.yml:
# Change:
#   - ARROW_DATABASE_PATH=/app/arrow_data/arrow_database.db
# To:
#   - ARROW_DATABASE_PATH=/app/arrow_database.db

docker-compose -f docker-compose.unified.yml --profile with-nginx up -d
```

**Option B: Create Symlinks (Quick Fix)**
```bash
# Create symlinks to maintain compatibility
docker-compose -f docker-compose.unified.yml exec api bash -c "
if [ -f /app/arrow_data/arrow_database.db ] && [ ! -f /app/arrow_database.db ]; then
    ln -sf /app/arrow_data/arrow_database.db /app/arrow_database.db
    echo '✅ Created symlink for arrow database'
fi
"
```

## 🏭 Complete Production Dockerfile Fix

Create an enhanced production Dockerfile that includes Gunicorn:

**File: `arrow_scraper/Dockerfile.production`**
```dockerfile
# Production ArrowTuner API Backend with Gunicorn WSGI Server
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=api.py
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        sqlite3 \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/processed /app/data/raw /app/logs /app/user_data /app/arrow_data /app/backups

# Create production startup script
RUN cat > /app/start-production.sh << 'EOF' && \
    chmod +x /app/start-production.sh
#!/bin/bash
echo "🚀 Starting ArrowTuner API with Gunicorn (Production WSGI Server)..."
echo "=================================================="

# Database verification
python3 /app/verify-databases.py

# Start Gunicorn with production configuration
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    api:app
EOF

# Create non-root user
RUN addgroup --gid 1000 appgroup && \
    adduser --disabled-password --gecos '' --uid 1000 --gid 1000 appuser && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:5000/api/simple-health || exit 1

# Expose port
EXPOSE 5000

# Use production startup script
CMD ["./start-production.sh"]
```

## 🚀 Updated Production Deployment

To use the production fixes, update your deployment:

**File: `docker-compose.production.yml`**
```yaml
services:
  api:
    build:
      context: ./arrow_scraper
      dockerfile: Dockerfile.production
    environment:
      # Correct unified paths
      - ARROW_DATABASE_PATH=/app/arrow_database.db
      - USER_DATABASE_PATH=/app/user_data/user_data.db
      - FLASK_ENV=production
    volumes:
      # Map to correct paths
      - ./arrow_scraper/arrow_database.db:/app/arrow_database.db:ro
      - arrowtuner-userdata:/app/user_data
```

**Deploy with:**
```bash
# Build and deploy production version
docker-compose -f docker-compose.production.yml --profile with-nginx up -d --build
```

## 📊 Verification Commands

After applying fixes, verify the production deployment:

```bash
# 1. Check that Gunicorn is running (not Flask dev server)
docker-compose -f docker-compose.unified.yml logs api | grep -i gunicorn

# 2. Verify database schema
docker-compose -f docker-compose.unified.yml exec api sqlite3 /app/arrow_database.db ".schema arrows" | grep arrow_type

# 3. Check database paths
docker-compose -f docker-compose.unified.yml exec api python3 -c "
import os
print('ARROW_DATABASE_PATH:', os.environ.get('ARROW_DATABASE_PATH'))
print('USER_DATABASE_PATH:', os.environ.get('USER_DATABASE_PATH'))
"

# 4. Test API performance
curl -w "@curl-format.txt" -o /dev/null -s https://archerytool.online/api/health

# 5. Check server info
curl -I https://archerytool.online/ | grep -i server
```

## 🎯 Expected Results After Fixes

**API Logs Should Show:**
```
🚀 Starting ArrowTuner API with Gunicorn (Production WSGI Server)...
📊 Arrow database: /app/arrow_database.db
👤 User database: /app/user_data/user_data.db
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:5000 (1)
[INFO] Using worker: sync
[INFO] Booting worker with pid: 8
✅ Database initialized: /app/arrow_database.db
```

**No More Warnings:**
- ❌ ~~WARNING: This is a development server~~
- ❌ ~~Could not create indexes (database may be read-only): no such column: arrow_type~~

**Performance Improvements:**
- Multiple worker processes for better concurrent request handling
- Production-optimized request/response handling
- Proper database schema with all required columns and indexes

## 🔗 Related Documentation

- [PRODUCTION_TROUBLESHOOTING.md](PRODUCTION_TROUBLESHOOTING.md) - General production issues
- [DATABASE_CLEANER_GUIDE.md](DATABASE_CLEANER_GUIDE.md) - Database maintenance
- [UNIFIED_MIGRATION_GUIDE.md](UNIFIED_MIGRATION_GUIDE.md) - Architecture migration