#!/bin/bash
# Enhanced startup script for ArrowTuner API with comprehensive verification
# This script ensures both arrow database and user database are properly initialized

set -e

echo "🚀 Starting ArrowTuner API with Enhanced Verification..."
echo "=================================================="

# Function to verify database integrity
verify_database() {
    local db_file="$1"
    local db_name="$2"
    
    echo "🔍 Verifying $db_name database: $db_file"
    
    if [ ! -f "$db_file" ]; then
        echo "❌ $db_name database not found at $db_file"
        return 1
    fi
    
    # Check if database is readable and not corrupted
    if ! sqlite3 "$db_file" "PRAGMA integrity_check;" >/dev/null 2>&1; then
        echo "❌ $db_name database is corrupted or unreadable"
        return 1
    fi
    
    echo "✅ $db_name database file exists and is readable"
    return 0
}

# Function to get table count and record count
check_database_content() {
    local db_file="$1"
    local db_name="$2"
    
    echo "📊 Checking $db_name database content..."
    
    # Get table count
    local table_count=$(sqlite3 "$db_file" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    echo "   Tables: $table_count"
    
    # Check specific tables based on database type
    if [[ "$db_name" == "Arrow" ]]; then
        # Check arrow database tables
        local arrow_count=$(sqlite3 "$db_file" "SELECT COUNT(*) FROM arrows;" 2>/dev/null || echo "0")
        local spine_count=$(sqlite3 "$db_file" "SELECT COUNT(*) FROM spine_specifications;" 2>/dev/null || echo "0")
        echo "   Arrows: $arrow_count"
        echo "   Spine Specifications: $spine_count"
        
        if [ "$arrow_count" -lt 100 ]; then
            echo "⚠️  Warning: Low arrow count ($arrow_count), database may be incomplete"
        else
            echo "✅ Arrow database has good content volume"
        fi
    elif [[ "$db_name" == "User" ]]; then
        # Check user database tables
        local user_count=$(sqlite3 "$db_file" "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")
        local bow_count=$(sqlite3 "$db_file" "SELECT COUNT(*) FROM bow_setups;" 2>/dev/null || echo "0")
        local session_count=$(sqlite3 "$db_file" "SELECT COUNT(*) FROM guide_sessions;" 2>/dev/null || echo "0")
        echo "   Users: $user_count"
        echo "   Bow Setups: $bow_count"
        echo "   Guide Sessions: $session_count"
        echo "✅ User database structure verified"
    fi
}

# Function to initialize user database if needed
initialize_user_database() {
    local user_db_path="$1"
    
    echo "🔧 Initializing user database..."
    
    # Ensure user_data directory exists
    mkdir -p "$(dirname "$user_db_path")"
    
    # Initialize user database using Python
    python3 -c "
from user_database import UserDatabase
import os
print(f'Initializing user database at: $user_db_path')
user_db = UserDatabase('$user_db_path')
print('✅ User database initialized successfully')
"
}

# Function to run database migrations
run_migrations() {
    echo "📦 Running comprehensive database migrations..."
    
    # Set environment variables for migration system (use computed paths)
    export ARROW_DATABASE_PATH="${ARROW_DB}"
    export USER_DATABASE_PATH="${USER_DB}"
    
    # First try the comprehensive migration runner (preferred)
    if [ -f "/app/comprehensive-migration-runner.sh" ]; then
        echo "🎯 Using comprehensive migration runner..."
        chmod +x /app/comprehensive-migration-runner.sh
        
        # Ensure environment variables are properly set for migration
        export ARROW_DATABASE_PATH="${ARROW_DB}"
        export USER_DATABASE_PATH="${USER_DB}"
        
        # Run comprehensive migrations from /app directory (where migrations/ exists)
        if /app/comprehensive-migration-runner.sh docker; then
            echo "✅ Comprehensive migrations completed successfully"
            return 0
        else
            echo "⚠️  Comprehensive migrations failed, trying fallback..."
        fi
    else
        echo "⚠️  Comprehensive migration runner not found at /app/comprehensive-migration-runner.sh"
    fi
    
    # Fallback: Check for standard migration runner
    if [ -f "/app/run_migrations.py" ]; then
        echo "🔄 Using standard migration script..."
        python3 /app/run_migrations.py
    else
        echo "⚠️  Standard migration runner not found, running legacy migrations..."
        
        # Legacy fallback: Run individual migrations
        local migrations=(
            "migrate_remove_arrow_fields.py"
            "migrate_add_bow_info_fields.py" 
            "migrate_add_compound_model.py"
            "migrate_diameter_categories.py"
            "migrations/012_fix_pending_manufacturers_schema.py"
            "migrations/013_equipment_change_logging.py"
            "migrations/014_arrow_change_logging.py"
            "migrations/015_remove_setup_arrows_unique_constraint.py"
            "migrations/016_equipment_soft_delete_enhancement.py"
        )
        
        for migration in "${migrations[@]}"; do
            # Check both Docker and local paths
            local migration_path=""
            if [ -f "/app/$migration" ]; then
                migration_path="/app/$migration"
            elif [ -f "$migration" ]; then
                migration_path="$migration"
            fi
            
            if [ -n "$migration_path" ]; then
                echo "🔄 Running migration: $migration"
                python3 "$migration_path" || echo "⚠️  Migration $migration failed or already applied"
            else
                echo "⏭️  Migration $migration not found, skipping"
            fi
        done
    fi
}

# Function to run database import from JSON files
run_database_import() {
    # Skip import in production unless explicitly enabled
    if [ "$FLASK_ENV" = "production" ] && [ "$FORCE_DATABASE_IMPORT" != "true" ]; then
        echo "📥 Skipping database import in production environment"
        echo "    Use FORCE_DATABASE_IMPORT=true to enable import in production"
        echo "    Or use backup/restore scripts for production data management"
        return 0
    fi
    
    echo "📥 Running database import from JSON files..."
    
    # Check for database import manager
    local import_script=""
    if [ -f "/app/database_import_manager.py" ]; then
        import_script="/app/database_import_manager.py"
    elif [ -f "database_import_manager.py" ]; then
        import_script="database_import_manager.py"
    fi
    
    if [ -n "$import_script" ]; then
        echo "🔄 Running database import manager..."
        python3 "$import_script" --database="$ARROW_DB" --data-dir="data/processed"
        local import_result=$?
        
        if [ $import_result -eq 0 ]; then
            echo "✅ Database import completed successfully"
        else
            echo "⚠️  Database import completed with warnings or errors"
        fi
    else
        echo "⚠️  Database import manager not found, skipping JSON import"
        echo "    Arrow data will use existing database content"
    fi
}

# Main verification and startup process
echo "🔍 Step 1: Database Verification"
echo "================================"

# Database Path Resolution - Compatible with Production Docker Volumes
echo "🗄️  Configuring database paths for deployment environment"

# Use environment variables if set, otherwise detect environment and use appropriate defaults
ARROW_DB="${ARROW_DATABASE_PATH:-}"
USER_DB="${USER_DATABASE_PATH:-}"

if [ -d "/app" ] && [ -f "/app/api.py" ]; then
    # Docker environment - check for volume mounts and environment variables
    echo "🐳 Running in Docker environment"
    
    # Check if we have unified database environment variables (new architecture)
    if [ -n "$ARROW_DATABASE_PATH" ] && [ -n "$USER_DATABASE_PATH" ]; then
        echo "📁 Using environment-specified unified database paths"
        ARROW_DB="$ARROW_DATABASE_PATH"
        USER_DB="$USER_DATABASE_PATH"
        mkdir -p "$(dirname "$ARROW_DB")" "$(dirname "$USER_DB")"
    else
        # Production volume mount paths (existing working system)
        echo "📁 Using production Docker volume paths"
        ARROW_DB="/app/arrow_data/arrow_database.db"
        USER_DB="/app/user_data/user_data.db"
        
        # Ensure directories exist (Docker volumes)
        mkdir -p "/app/arrow_data" "/app/user_data"
    fi
    
    echo "📁 Arrow database: $ARROW_DB"
    echo "📁 User database: $USER_DB"
else
    # Local development environment
    echo "💻 Running in local development environment"
    
    # Check if we're in the arrow_scraper directory
    if [ ! -f "api.py" ] && [ -f "../arrow_scraper/api.py" ]; then
        cd ../arrow_scraper
        echo "📁 Changed to arrow_scraper directory"
    fi
    
    # Local development defaults (can be overridden by environment variables)
    if [ -z "$ARROW_DB" ]; then
        ARROW_DB="arrow_database.db"
    fi
    if [ -z "$USER_DB" ]; then
        USER_DB="user_data.db"
    fi
    
    echo "📁 Arrow database (local): $ARROW_DB"
    echo "📁 User database (local): $USER_DB"
fi

# Verify arrow database
if verify_database "$ARROW_DB" "Arrow"; then
    check_database_content "$ARROW_DB" "Arrow"
else
    echo "❌ Critical: Arrow database verification failed"
    
    # Try to rebuild from backup
    if [ -f "/app/arrow_database_backup.db" ]; then
        echo "🔄 Attempting to restore from backup..."
        cp "/app/arrow_database_backup.db" "$ARROW_DB"
        if verify_database "$ARROW_DB" "Arrow"; then
            echo "✅ Restored from backup successfully"
        else
            echo "❌ Backup restoration failed"
            exit 1
        fi
    else
        echo "⚠️  No backup available, attempting to create new database..."
        echo "    This will create an empty arrow database that can be populated later"
        
        # Ensure directory exists (permissions set by Docker volume)
        mkdir -p "$(dirname "$ARROW_DB")"
        
        echo "    Creating database at: $ARROW_DB"
        echo "    Directory: $(dirname "$ARROW_DB")"
        echo "    Permissions: $(ls -ld "$(dirname "$ARROW_DB")")"
        
        # Create minimal arrow database structure
        sqlite3 "$ARROW_DB" << 'EOF'
CREATE TABLE IF NOT EXISTS arrows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer TEXT NOT NULL,
    model_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS spine_specifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arrow_id INTEGER NOT NULL,
    spine INTEGER NOT NULL,
    outer_diameter REAL,
    gpi_weight REAL,
    FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE
);
EOF
        
        if verify_database "$ARROW_DB" "Arrow"; then
            echo "✅ Created new empty arrow database"
            echo "    Use backup/restore scripts or import tools to populate data"
        else
            echo "❌ Failed to create new arrow database"
            exit 1
        fi
    fi
fi

# Initialize and verify user database
echo ""
echo "🔍 Step 2: User Database Initialization"
echo "======================================"

if verify_database "$USER_DB" "User"; then
    echo "✅ User database already exists and is valid"
    check_database_content "$USER_DB" "User"
else
    echo "🔧 User database not found or invalid, initializing..."
    initialize_user_database "$USER_DB"
    
    if verify_database "$USER_DB" "User"; then
        echo "✅ User database initialized successfully"
        check_database_content "$USER_DB" "User"
    else
        echo "❌ Failed to initialize user database"
        exit 1
    fi
fi

# Run migrations
echo ""
echo "🔍 Step 3: Database Migrations"
echo "============================"
run_migrations

# Environment validation
echo ""
echo "🔍 Step 4: Environment Validation"
echo "================================"

# Check critical environment variables
REQUIRED_VARS=(
    "SECRET_KEY"
    "GOOGLE_CLIENT_SECRET"
    "NUXT_PUBLIC_GOOGLE_CLIENT_ID"
)

MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "not-set" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "⚠️  Warning: Missing or default environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo "   Application may not function correctly"
else
    echo "✅ All critical environment variables are set"
fi

# Final health check
echo ""
echo "🔍 Step 5: Pre-startup Health Check"
echo "=================================="

# Check Python imports
echo "🐍 Verifying Python dependencies..."
python3 -c "
import flask, sqlite3, requests, jwt
from user_database import UserDatabase
from arrow_database import ArrowDatabase
print('✅ All critical Python imports successful')
" || {
    echo "❌ Python dependency check failed"
    exit 1
}

# Check disk space
echo "💾 Checking disk space..."
if [ -d "/app" ]; then
    DISK_USAGE=$(df /app | tail -1 | awk '{print $5}' | sed 's/%//')
else
    DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
fi

if [ "$DISK_USAGE" -gt 90 ]; then
    echo "⚠️  Warning: Disk usage is high ($DISK_USAGE%)"
else
    echo "✅ Disk space OK ($DISK_USAGE% used)"
fi

# Run database migrations
echo ""
echo "🔄 Step 6: Database Migrations"
echo "=============================="
echo "🗄️ Running database migrations..."

# Set environment variables for migrations
export ARROW_DATABASE_PATH="$ARROW_DB"
export USER_DATABASE_PATH="$USER_DB"

# Run migrations if migration runner exists
if [ -f "run_migrations.py" ]; then
    echo "🔧 Running migrations with migration runner..."
    
    if python3 run_migrations.py --status-only > /dev/null 2>&1; then
        if python3 run_migrations.py; then
            echo "✅ Database migrations completed successfully"
        else
            echo "⚠️  Some migrations failed, but continuing startup"
        fi
    else
        echo "⚠️  Could not check migration status, but continuing startup"
    fi
else
    echo "⚠️  Migration runner not found, skipping migrations"
fi

# Start the application
echo ""
echo "🚀 Step 7: Starting Flask API Server"
echo "=================================="
echo "🌐 All checks passed, starting Flask API server..."
echo "📊 Arrow database: $ARROW_DB"
echo "👤 User database: $USER_DB"
echo "🔧 Environment: ${FLASK_ENV:-production}"
echo ""

# Set final environment variables for the application
export ARROW_DATABASE_PATH="$ARROW_DB"
export USER_DATABASE_PATH="$USER_DB"

# Start Flask with proper error handling
exec python3 api.py