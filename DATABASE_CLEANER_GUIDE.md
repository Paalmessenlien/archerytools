# 🧹 Database Cleaner Guide

This guide explains how to use the `database_cleaner.py` script for maintaining and cleaning the arrow database in the ArrowTuner system.

## 📋 Overview

The `database_cleaner.py` is a comprehensive database maintenance tool that provides:
- Manufacturer management (rename, remove, merge)
- Duplicate detection and removal (with fuzzy matching)
- Database validation and statistics
- Data export and backup functionality
- Complete database cleaning options

## 🐳 Docker vs Local Usage

### ⚠️ **Important Note**
The `database_cleaner.py` script **does NOT work directly** on the database running inside Docker containers. The script connects to SQLite files using local file paths, but the Docker database is isolated inside the container.

### 🛠️ **Solution Options**

#### **Option 1: Run Inside Docker Container (Recommended)**
```bash
# Basic syntax
docker-compose -f docker-compose.unified.yml exec api python3 /app/database_cleaner.py [OPTIONS]

# Specify database path explicitly
docker-compose -f docker-compose.unified.yml exec api python3 /app/database_cleaner.py --database /app/arrow_database.db [OPTIONS]

# For user database operations
docker-compose -f docker-compose.unified.yml exec api python3 /app/database_cleaner.py --database /app/user_data/user_data.db [OPTIONS]
```

#### **Option 2: Copy Database to Host**
```bash
# Copy database from container to host
docker cp arrowtuner-api:/app/arrow_database.db ./arrow_database.db

# Run cleaner locally
cd arrow_scraper
python database_cleaner.py --list-manufacturers

# Copy cleaned database back (if changes were made)
docker cp ./arrow_database.db arrowtuner-api:/app/arrow_database.db

# Restart API to pick up changes
docker-compose -f docker-compose.unified.yml restart api
```

#### **Option 3: Temporary Volume Mount**
```bash
# Stop services first
docker-compose -f docker-compose.unified.yml down

# Run with temporary mount
docker-compose -f docker-compose.unified.yml run --rm \
  -v $(pwd)/arrow_scraper:/host \
  api python3 /host/database_cleaner.py --database /app/arrow_database.db [OPTIONS]

# Restart services
docker-compose -f docker-compose.unified.yml up -d
```

## 🎯 Common Operations

### **List All Manufacturers**
```bash
# Docker method
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db --list-manufacturers

# Local method (if database copied)
cd arrow_scraper
python database_cleaner.py --list-manufacturers
```

### **Find Duplicate Arrows**
```bash
# Find duplicates using fuzzy matching (recommended)
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db --find-duplicates

# Find duplicates for specific manufacturer only
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --find-duplicates --manufacturer-filter "Easton Archery"

# Use exact matching instead of fuzzy
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --find-duplicates --exact-match

# Adjust fuzzy matching sensitivity (0.0-1.0, default: 0.85)
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --find-duplicates --similarity-threshold 0.90
```

### **Clean Duplicate Arrows**
```bash
# Always run dry-run first to preview changes
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --clean-duplicates --dry-run

# Actually clean duplicates (creates backup automatically)
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --clean-duplicates

# Clean duplicates for specific manufacturer only
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --clean-duplicates --manufacturer-filter "Gold Tip"
```

### **Manufacturer Management**
```bash
# List arrows for specific manufacturer
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --list-arrows "Gold Tip"

# Rename manufacturer
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --rename-manufacturer "BigArchery" "Cross-X" --dry-run

# Remove manufacturer completely (with backup)
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --save-manufacturer "Test Manufacturer" --output /app/backup_test_mfr.json

docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --remove-manufacturer "Test Manufacturer"

# Merge manufacturers
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --merge-manufacturers "BigArchery" "Cross-X" --dry-run
```

### **Database Validation & Statistics**
```bash
# Validate database integrity
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db --validate

# Show comprehensive statistics
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db --stats
```

### **Database Cleaning Operations**
```bash
# Clean database but keep specific manufacturers
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --clean-keep "Easton Archery" "Gold Tip" "Victory Archery" --dry-run

# Complete database wipe (DANGER!)
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --clean-all --dry-run

# Reset database schema (removes ALL data and recreates tables)
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --reset-schema --dry-run
```

## 🗄️ Database Paths in Docker

The unified Docker architecture uses these database paths:

| Database | Docker Path | Purpose |
|----------|-------------|---------|
| Arrow Database | `/app/arrow_database.db` | Arrow specifications, spine data, components |
| User Database | `/app/user_data/user_data.db` | User accounts, bow setups, sessions |

## 🔒 Safety Features

### **Automatic Backups**
- Destructive operations automatically create backups (unless `--no-backup` is used)
- Backups are timestamped: `arrow_database.db.backup_20250804_143022`

### **Dry Run Mode**
- Always use `--dry-run` first to preview changes
- Shows exactly what would be changed without making modifications

### **Confirmation Prompts**
- Dangerous operations require explicit confirmation
- Type 'YES' for database cleaning, 'RESET' for schema reset

## 📊 Fuzzy Matching Features

### **How It Works**
- Normalizes model names (removes common words, special characters)
- Uses SequenceMatcher for similarity calculation
- Default threshold: 0.85 (85% similarity)
- Only matches within same manufacturer

### **Adjusting Sensitivity**
```bash
# More strict (fewer matches)
--similarity-threshold 0.95

# More lenient (more matches)
--similarity-threshold 0.75
```

### **Example Fuzzy Matches**
- "Victory VAP-TKO Elite" ↔ "Victory VAP TKO Elite" (punctuation difference)
- "Easton Axis 5mm Traditional" ↔ "Easton Axis Traditional 5mm" (word order)
- "Gold Tip Hunter XT" ↔ "Gold Tip Hunter Extreme" (abbreviation)

## 🚨 Important Notes

### **Docker Container Requirements**
- Services must be running: `docker-compose -f docker-compose.unified.yml up -d`
- API container must be healthy
- Database files must be accessible inside container

### **Data Safety**
- Always run `--dry-run` first for destructive operations
- Automatic backups are created before changes
- User database operations should be done carefully as they affect user accounts

### **Performance Considerations**
- Fuzzy matching can be slow on large databases
- Use `--manufacturer-filter` to limit scope
- Exact matching (`--exact-match`) is faster than fuzzy matching

## 📝 Example Maintenance Workflow

```bash
# 1. Check database health
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db --stats

# 2. Validate integrity
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db --validate

# 3. Find duplicates
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db --find-duplicates

# 4. Clean duplicates (preview first)
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db \
  --clean-duplicates --dry-run

# 5. Actually clean if satisfied
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db --clean-duplicates

# 6. Verify results
docker-compose -f docker-compose.unified.yml exec api \
  python3 /app/database_cleaner.py --database /app/arrow_database.db --stats
```

## 🔧 Troubleshooting

### **Permission Errors**
```bash
# If you get permission errors, try:
docker-compose -f docker-compose.unified.yml exec api chmod 775 /app/arrow_database.db
```

### **Database Locked Errors**
```bash
# Stop API temporarily to release database locks
docker-compose -f docker-compose.unified.yml stop api
# Run your database operation
# Restart API
docker-compose -f docker-compose.unified.yml start api
```

### **Script Not Found**
```bash
# Make sure you're in the project root directory
cd /home/paal/arrowtuner2

# Verify container is running
docker-compose -f docker-compose.unified.yml ps
```

## 🔗 Related Documentation

- [UNIFIED_MIGRATION_GUIDE.md](UNIFIED_MIGRATION_GUIDE.md) - Unified architecture setup
- [DATABASE_PERSISTENCE.md](DATABASE_PERSISTENCE.md) - Database persistence and backup
- [CLAUDE.md](CLAUDE.md) - Complete project documentation