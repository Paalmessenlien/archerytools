#!/bin/bash
#
# Docker Migration Runner for ArrowTuner Production
# Runs database migrations inside Docker containers
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to find API container
find_api_container() {
    local containers=$(docker ps --format "{{.Names}}" 2>/dev/null || echo "")
    
    if [ -z "$containers" ]; then
        echo ""
        return 1
    fi
    
    # Look for API container patterns
    for pattern in "api" "arrowtuner" "archery"; do
        for container in $containers; do
            if echo "$container" | grep -i "$pattern" > /dev/null; then
                echo "$container"
                return 0
            fi
        done
    done
    
    # Return first container if no specific match
    echo "$containers" | head -1
    return 0
}

# Function to copy migration files to container
copy_migrations_to_container() {
    local container_name="$1"
    
    print_message "$BLUE" "📁 Copying migration files to container..."
    
    # Copy migrations directory
    if [ -d "./arrow_scraper/migrations" ]; then
        docker cp ./arrow_scraper/migrations "$container_name:/app/" || {
            print_message "$RED" "❌ Failed to copy migrations directory"
            return 1
        }
    fi
    
    # Copy migration runner
    if [ -f "./arrow_scraper/run_migrations.py" ]; then
        docker cp ./arrow_scraper/run_migrations.py "$container_name:/app/" || {
            print_message "$RED" "❌ Failed to copy migration runner"
            return 1
        }
    fi
    
    # Copy database migration manager
    if [ -f "./arrow_scraper/database_migration_manager.py" ]; then
        docker cp ./arrow_scraper/database_migration_manager.py "$container_name:/app/" || {
            print_message "$RED" "❌ Failed to copy migration manager"
            return 1
        }
    fi
    
    # Copy spine calculator data importer if it exists
    if [ -f "./arrow_scraper/spine_calculator_data_importer.py" ]; then
        docker cp ./arrow_scraper/spine_calculator_data_importer.py "$container_name:/app/" || {
            print_message "$YELLOW" "⚠️  Could not copy spine calculator importer"
        }
    fi
    
    # Copy spine calculator data directory if it exists
    if [ -d "./arrow_scraper/spinecalculatordata" ]; then
        docker cp ./arrow_scraper/spinecalculatordata "$container_name:/app/" || {
            print_message "$YELLOW" "⚠️  Could not copy spine calculator data"
        }
    fi
    
    print_message "$GREEN" "✅ Migration files copied to container"
    return 0
}

# Function to run migrations in container
run_migrations_in_container() {
    local container_name="$1"
    local command="$2"
    
    print_message "$BLUE" "🔄 Running migrations in container..."
    
    # Set environment variables for container
    docker exec "$container_name" sh -c "
        export ARROW_DATABASE_PATH=/app/databases/arrow_database.db
        export USER_DATABASE_PATH=/app/databases/user_data.db
        cd /app
        python3 run_migrations.py $command
    " || {
        print_message "$RED" "❌ Migration execution failed"
        return 1
    }
    
    return 0
}

# Function to show migration status
show_migration_status() {
    local container_name="$1"
    
    print_message "$BLUE" "📊 Checking migration status in container..."
    
    if run_migrations_in_container "$container_name" "--status-only"; then
        print_message "$GREEN" "✅ Migration status retrieved successfully"
        return 0
    else
        print_message "$RED" "❌ Could not get migration status"
        return 1
    fi
}

# Main function
main() {
    print_message "$GREEN" "🐳 Docker Migration Runner for ArrowTuner"
    print_message "$GREEN" "============================================"
    
    # Parse command line arguments
    local command="$1"
    local dry_run=""
    
    case "$command" in
        "status")
            command="--status-only"
            ;;
        "migrate")
            command=""
            ;;
        "dry-run")
            command="--dry-run"
            ;;
        "")
            # Default to migration
            command=""
            ;;
        *)
            echo "Usage: $0 [status|migrate|dry-run]"
            echo "  status   - Show migration status"
            echo "  migrate  - Run pending migrations (default)"
            echo "  dry-run  - Preview migrations without applying"
            exit 1
            ;;
    esac
    
    # Find API container
    print_message "$BLUE" "🔍 Finding API container..."
    
    container_name=$(find_api_container)
    if [ -z "$container_name" ]; then
        print_message "$RED" "❌ No Docker containers found!"
        print_message "$YELLOW" "   Make sure your ArrowTuner containers are running"
        print_message "$YELLOW" "   Run: docker ps"
        exit 1
    fi
    
    print_message "$GREEN" "✅ Found container: $container_name"
    
    # Copy migration files to container
    if ! copy_migrations_to_container "$container_name"; then
        exit 1
    fi
    
    # Run migrations or show status
    if [ "$command" = "--status-only" ]; then
        if show_migration_status "$container_name"; then
            print_message "$GREEN" "✅ Migration status check completed"
        else
            exit 1
        fi
    else
        print_message "$BLUE" "🎯 Running database migrations in container..."
        
        if run_migrations_in_container "$container_name" "$command"; then
            print_message "$GREEN" "✅ Database migrations completed successfully!"
            print_message "$BLUE" "   Your production spine chart system should now work"
            print_message "$BLUE" "   Refresh your browser to see the changes"
        else
            print_message "$RED" "❌ Migration execution failed"
            print_message "$YELLOW" "   Check container logs: docker logs $container_name"
            exit 1
        fi
    fi
}

# Run main function with all arguments
main "$@"