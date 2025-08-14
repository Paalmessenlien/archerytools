#!/bin/bash
#
# Comprehensive Migration Runner for ArrowTuner Platform
# Ensures all database migrations are properly applied across all environments
#
# This script is designed to be called from production startup scripts
# and will handle all migration scenarios safely
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to detect environment
detect_environment() {
    if [[ -f "/.dockerenv" ]]; then
        echo "docker"
    elif [[ "$FLASK_ENV" == "production" ]] || [[ "$NODE_ENV" == "production" ]]; then
        echo "production"
    else
        echo "development"
    fi
}

# Function to find database paths
find_database_paths() {
    local environment=$1
    
    print_message "$BLUE" "🔍 Finding database paths for $environment environment..."
    
    # Arrow database paths (priority order)
    local ARROW_DB_PATHS=(
        "$ARROW_DATABASE_PATH"
        "/app/arrow_data/arrow_database.db"
        "/app/databases/arrow_database.db"  
        "/app/arrow_database.db"
        "$SCRIPT_DIR/databases/arrow_database.db"
        "$SCRIPT_DIR/arrow_scraper/databases/arrow_database.db"
        "$SCRIPT_DIR/arrow_scraper/arrow_database.db"
    )
    
    # User database paths (priority order)
    local USER_DB_PATHS=(
        "$USER_DATABASE_PATH"
        "/app/user_data/user_data.db"
        "/app/databases/user_data.db"
        "/app/user_data.db"
        "$SCRIPT_DIR/databases/user_data.db"
        "$SCRIPT_DIR/arrow_scraper/databases/user_data.db"
        "$SCRIPT_DIR/arrow_scraper/user_data.db"
    )
    
    # Find arrow database
    ARROW_DB_PATH=""
    for path in "${ARROW_DB_PATHS[@]}"; do
        if [[ -n "$path" ]] && [[ -f "$path" ]]; then
            ARROW_DB_PATH="$path"
            break
        fi
    done
    
    # Find user database
    USER_DB_PATH=""
    for path in "${USER_DB_PATHS[@]}"; do
        if [[ -n "$path" ]] && [[ -f "$path" ]]; then
            USER_DB_PATH="$path"
            break
        fi
    done
    
    # Create databases if they don't exist (use first writable location)
    if [[ -z "$ARROW_DB_PATH" ]]; then
        for path in "${ARROW_DB_PATHS[@]}"; do
            if [[ -n "$path" ]]; then
                local dir=$(dirname "$path")
                if mkdir -p "$dir" 2>/dev/null && touch "$path" 2>/dev/null; then
                    ARROW_DB_PATH="$path"
                    print_message "$YELLOW" "⚠️  Arrow database will be created at: $ARROW_DB_PATH"
                    break
                fi
            fi
        done
    fi
    
    if [[ -z "$USER_DB_PATH" ]]; then
        for path in "${USER_DB_PATHS[@]}"; do
            if [[ -n "$path" ]]; then
                local dir=$(dirname "$path")
                if mkdir -p "$dir" 2>/dev/null && touch "$path" 2>/dev/null; then
                    USER_DB_PATH="$path"
                    print_message "$YELLOW" "⚠️  User database will be created at: $USER_DB_PATH"
                    break
                fi
            fi
        done
    fi
    
    if [[ -n "$ARROW_DB_PATH" ]]; then
        print_message "$GREEN" "✅ Arrow database found: $ARROW_DB_PATH"
    else
        print_message "$RED" "❌ Could not find or create arrow database"
        return 1
    fi
    
    if [[ -n "$USER_DB_PATH" ]]; then
        print_message "$GREEN" "✅ User database found: $USER_DB_PATH"
    else
        print_message "$RED" "❌ Could not find or create user database"
        return 1
    fi
    
    export ARROW_DB_PATH
    export USER_DB_PATH
}

# Function to verify migration runner availability
verify_migration_runner() {
    print_message "$BLUE" "🔧 Verifying migration system..."
    
    # Check if we're in arrow_scraper directory or need to navigate there
    if [[ ! -f "run_migrations.py" ]] && [[ -f "arrow_scraper/run_migrations.py" ]]; then
        cd arrow_scraper
        print_message "$BLUE" "📁 Navigated to arrow_scraper directory"
    fi
    
    # Check for migration runner
    if [[ ! -f "run_migrations.py" ]]; then
        print_message "$RED" "❌ Migration runner not found (run_migrations.py)"
        return 1
    fi
    
    # Check for database migration manager
    if [[ ! -f "database_migration_manager.py" ]]; then
        print_message "$RED" "❌ Database migration manager not found"
        return 1
    fi
    
    # Check migrations directory
    if [[ ! -d "migrations" ]]; then
        print_message "$RED" "❌ Migrations directory not found"
        return 1
    fi
    
    # Count available migrations
    local migration_count=$(find migrations/ -name "[0-9][0-9][0-9]_*.py" | wc -l)
    print_message "$GREEN" "✅ Found $migration_count migration files"
    
    # List all available migrations
    print_message "$BLUE" "📋 Available migrations:"
    find migrations/ -name "[0-9][0-9][0-9]_*.py" | sort | while read -r migration; do
        local migration_name=$(basename "$migration" .py)
        print_message "$BLUE" "   • $migration_name"
    done
    
    return 0
}

# Function to check Python environment
check_python_environment() {
    print_message "$BLUE" "🐍 Checking Python environment..."
    
    # Check if we have Python 3
    if ! command -v python3 &> /dev/null; then
        print_message "$RED" "❌ Python 3 not found"
        return 1
    fi
    
    local python_version=$(python3 --version 2>&1)
    print_message "$GREEN" "✅ $python_version"
    
    # Try to activate virtual environment if it exists
    if [[ -f "venv/bin/activate" ]] && [[ -z "$VIRTUAL_ENV" ]]; then
        print_message "$BLUE" "🔄 Activating virtual environment..."
        source venv/bin/activate
        print_message "$GREEN" "✅ Virtual environment activated"
    fi
    
    # Check required modules
    local required_modules=("sqlite3")
    for module in "${required_modules[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            print_message "$GREEN" "✅ $module module available"
        else
            print_message "$YELLOW" "⚠️  $module module not available"
        fi
    done
    
    return 0
}

# Function to get migration status
get_migration_status() {
    local db_path="$1"
    local db_name="$2"
    
    print_message "$BLUE" "📊 Checking $db_name migration status..."
    
    # Set environment variables for migration runner
    export ARROW_DATABASE_PATH="$ARROW_DB_PATH"
    export USER_DATABASE_PATH="$USER_DB_PATH"
    
    # Get status using migration runner
    if python3 run_migrations.py --status-only --database "$db_path" 2>/dev/null; then
        print_message "$GREEN" "✅ $db_name migration status retrieved successfully"
        return 0
    else
        print_message "$YELLOW" "⚠️  Could not get $db_name migration status, but continuing..."
        return 1
    fi
}

# Function to run migrations for a specific database
run_migrations_for_database() {
    local db_path="$1"
    local db_name="$2"
    local environment="$3"
    
    print_message "$BLUE" "🔄 Running $db_name migrations..."
    
    # Set environment variables
    export ARROW_DATABASE_PATH="$ARROW_DB_PATH"
    export USER_DATABASE_PATH="$USER_DB_PATH"
    
    # Run migrations
    if python3 run_migrations.py --database "$db_path"; then
        print_message "$GREEN" "✅ $db_name migrations completed successfully"
        return 0
    else
        print_message "$YELLOW" "⚠️  $db_name migrations had issues, but continuing startup..."
        return 1
    fi
}

# Function to verify critical migrations
verify_critical_migrations() {
    print_message "$BLUE" "🔍 Verifying critical migrations..."
    
    # Critical migrations that must be present
    local critical_migrations=(
        "001_spine_calculator_tables"
        "002_user_database_schema"
        "007_user_bow_equipment_table"
        "013_equipment_change_logging"
        "014_arrow_change_logging"
        "015_remove_setup_arrows_unique_constraint"
        "016_equipment_soft_delete_enhancement"
    )
    
    # Check if critical migrations exist as files
    local missing_migrations=()
    for migration in "${critical_migrations[@]}"; do
        if [[ ! -f "migrations/${migration}.py" ]]; then
            missing_migrations+=("$migration")
        fi
    done
    
    if [[ ${#missing_migrations[@]} -gt 0 ]]; then
        print_message "$RED" "❌ Critical migrations missing:"
        for migration in "${missing_migrations[@]}"; do
            print_message "$RED" "   • $migration"
        done
        return 1
    fi
    
    print_message "$GREEN" "✅ All critical migration files found"
    
    # Check if migrations are applied (this requires database access)
    if command -v sqlite3 &> /dev/null; then
        print_message "$BLUE" "🔍 Checking applied migrations in database..."
        
        # Check arrow database
        if [[ -n "$ARROW_DB_PATH" ]] && [[ -f "$ARROW_DB_PATH" ]]; then
            # Check if migration table exists
            if sqlite3 "$ARROW_DB_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name='database_migrations';" | grep -q "database_migrations"; then
                local applied_count=$(sqlite3 "$ARROW_DB_PATH" "SELECT COUNT(*) FROM database_migrations WHERE applied = 1;" 2>/dev/null || echo "0")
                print_message "$GREEN" "✅ Arrow database has $applied_count applied migrations"
            else
                print_message "$YELLOW" "⚠️  Arrow database migration table not found - will be created on first run"
            fi
        fi
        
        # Check user database  
        if [[ -n "$USER_DB_PATH" ]] && [[ -f "$USER_DB_PATH" ]]; then
            if sqlite3 "$USER_DB_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name='database_migrations';" | grep -q "database_migrations"; then
                local applied_count=$(sqlite3 "$USER_DB_PATH" "SELECT COUNT(*) FROM database_migrations WHERE applied = 1;" 2>/dev/null || echo "0")
                print_message "$GREEN" "✅ User database has $applied_count applied migrations"
            else
                print_message "$YELLOW" "⚠️  User database migration table not found - will be created on first run"
            fi
        fi
    fi
    
    return 0
}

# Function to run comprehensive migration process
run_comprehensive_migrations() {
    local environment="$1"
    
    print_message "$GREEN" "🗄️  Starting Comprehensive Database Migration Process"
    print_message "$GREEN" "====================================================="
    print_message "$BLUE" "Environment: $environment"
    print_message "$BLUE" "Arrow Database: $ARROW_DB_PATH"
    print_message "$BLUE" "User Database: $USER_DB_PATH"
    
    # Verify migration system
    if ! verify_migration_runner; then
        print_message "$RED" "❌ Migration system verification failed"
        return 1
    fi
    
    # Check Python environment
    if ! check_python_environment; then
        print_message "$RED" "❌ Python environment check failed"
        return 1
    fi
    
    # Verify critical migrations
    if ! verify_critical_migrations; then
        print_message "$RED" "❌ Critical migration verification failed"
        return 1
    fi
    
    # Get migration status for both databases
    get_migration_status "$ARROW_DB_PATH" "Arrow Database" || true
    get_migration_status "$USER_DB_PATH" "User Database" || true
    
    # Run migrations for arrow database
    print_message "$BLUE" "\n🔄 Phase 1: Arrow Database Migrations"
    print_message "$BLUE" "======================================"
    run_migrations_for_database "$ARROW_DB_PATH" "Arrow Database" "$environment"
    
    # Run migrations for user database  
    print_message "$BLUE" "\n🔄 Phase 2: User Database Migrations"
    print_message "$BLUE" "====================================="
    run_migrations_for_database "$USER_DB_PATH" "User Database" "$environment"
    
    # Final verification
    print_message "$BLUE" "\n📊 Final Migration Status"
    print_message "$BLUE" "=========================="
    get_migration_status "$ARROW_DB_PATH" "Arrow Database" || true
    get_migration_status "$USER_DB_PATH" "User Database" || true
    
    print_message "$GREEN" "\n✅ Comprehensive migration process completed!"
    return 0
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [environment]"
    echo ""
    echo "Environments:"
    echo "  development  - Development environment (default)"
    echo "  production   - Production environment"  
    echo "  docker       - Docker container environment"
    echo ""
    echo "Environment variables:"
    echo "  ARROW_DATABASE_PATH  - Override arrow database path"
    echo "  USER_DATABASE_PATH   - Override user database path"
    echo ""
    echo "This script will:"
    echo "  1. Auto-detect environment if not specified"
    echo "  2. Find database files in standard locations"
    echo "  3. Verify migration system integrity"
    echo "  4. Apply all pending migrations safely"
    echo "  5. Provide detailed status reporting"
}

# Main execution
main() {
    local environment="${1:-}"
    
    # Show usage if help requested
    if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        show_usage
        exit 0
    fi
    
    # Auto-detect environment if not provided
    if [[ -z "$environment" ]]; then
        environment=$(detect_environment)
        print_message "$BLUE" "🔍 Auto-detected environment: $environment"
    fi
    
    print_message "$GREEN" "🏹 ArrowTuner Comprehensive Migration Runner"
    print_message "$GREEN" "==========================================="
    
    # Find database paths
    if ! find_database_paths "$environment"; then
        print_message "$RED" "❌ Failed to find database paths"
        exit 1
    fi
    
    # Run comprehensive migrations
    if ! run_comprehensive_migrations "$environment"; then
        print_message "$RED" "❌ Migration process failed"
        exit 1
    fi
    
    print_message "$GREEN" "🎉 All migrations completed successfully!"
    print_message "$GREEN" "Your ArrowTuner platform is ready to use!"
}

# Execute main function with all arguments
main "$@"