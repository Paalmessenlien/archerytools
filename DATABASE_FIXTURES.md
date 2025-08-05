# Database Fixtures System

This document describes the database fixture system for consistent development and production setup.

## Overview

Instead of committing binary database files to git, we use a fixture-based approach:
- **Fixtures**: JSON files containing database schema and data
- **Initialization**: Scripts to create databases from fixtures
- **Version Control**: Only fixtures (JSON) are committed, not databases

## Files

### Core Scripts
- `create-database-fixtures.py` - Export existing databases to JSON fixtures
- `init-databases-from-fixtures.py` - Initialize clean databases from fixtures

### Fixture Files (database_fixtures/)
- `arrow_database_fixtures.json` - Complete arrow database with all specifications
- `user_database_schema.json` - User database schema with sample admin user

## Usage

### Creating Fixtures (Development)
```bash
# Export current databases to fixtures
python3 create-database-fixtures.py

# Creates:
# - database_fixtures/arrow_database_fixtures.json
# - database_fixtures/user_database_schema.json
```

### Initializing from Fixtures (Development/Production)
```bash
# Initialize both databases
python3 init-databases-from-fixtures.py

# Initialize specific database only
python3 init-databases-from-fixtures.py --arrow-only
python3 init-databases-from-fixtures.py --user-only

# Custom directories
python3 init-databases-from-fixtures.py --fixtures-dir fixtures --output-dir /app
```

## Benefits

### Security & Privacy
- ✅ No user data in git (user fixtures contain only schema + sample admin)
- ✅ Only public arrow specifications committed
- ✅ Email addresses anonymized in any sample data

### Consistency
- ✅ Same database content across dev/prod environments
- ✅ Clean database initialization for new deployments
- ✅ Reproducible database state for testing

### Git Efficiency
- ✅ Text-based JSON files (diffable, mergeable)
- ✅ Much smaller than binary databases
- ✅ Version history of data changes

## Database Content

### Arrow Database (arrow_database_fixtures.json)
Contains complete public data:
- 206 arrows across 13 manufacturers
- 1,001 spine specifications
- 90 components (inserts, nocks, points)
- 7 component categories
- Full database schema

### User Database (user_database_schema.json)
Contains only schema + minimal sample:
- Database schema for users and bow_setups tables
- Single sample admin user (admin@example.com)
- No actual user data for privacy

## Production Deployment

### Docker Integration
The initialization script detects environment:
```bash
# In Docker containers
python3 init-databases-from-fixtures.py --output-dir /app

# Local development
python3 init-databases-from-fixtures.py --output-dir arrow_scraper
```

### Startup Integration
Add to startup scripts:
```bash
# Initialize databases if fixtures are newer
if [ -f "database_fixtures/arrow_database_fixtures.json" ]; then
    python3 init-databases-from-fixtures.py --output-dir /app
fi
```

## Maintenance

### Updating Fixtures
1. Make changes to databases locally
2. Export new fixtures: `python3 create-database-fixtures.py`
3. Review changes: `git diff database_fixtures/`
4. Commit: `git add database_fixtures/ && git commit -m "Update database fixtures"`

### Data Migration
1. Old approach: Copy binary database files
2. New approach: Update fixtures and run initialization

## File Sizes
- arrow_database_fixtures.json: ~2MB (vs 15MB binary database)
- user_database_schema.json: <1KB (vs 32KB binary database)
- Total fixtures: ~2MB (vs 15MB+ for binary databases)

## Verification
Initialization script includes verification:
- Arrow database: Counts arrows and manufacturers
- User database: Counts users
- Schema validation: Ensures all tables created correctly

## Backward Compatibility
- Existing database scripts continue to work
- Fixtures provide additional deployment option
- No breaking changes to current workflows