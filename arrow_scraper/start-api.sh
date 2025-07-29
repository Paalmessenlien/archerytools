#!/bin/bash
# Startup script for ArrowTuner API

set -e

echo "🚀 Starting ArrowTuner API..."

# Check if database exists (built into image)
if [ -f "/app/arrow_database.db" ]; then
    echo "✅ Database found in image"
else
    echo "❌ Database not found - image may not have built correctly"
fi

# Run database migrations to ensure schema is up to date
echo "📦 Running database migrations..."
if [ -f "/app/run-migrations.py" ]; then
    python /app/run-migrations.py
else
    echo "⚠️  Migration runner not found, checking for individual migrations..."
    # Run migrations individually if the runner script is not available
    for migration in migrate_remove_arrow_fields.py migrate_add_bow_info_fields.py migrate_add_compound_model.py; do
        if [ -f "/app/$migration" ]; then
            echo "🔄 Running migration: $migration"
            python /app/$migration || echo "⚠️  Migration $migration failed or already applied"
        fi
    done
fi

# Start the Flask API
echo "🌐 Starting Flask API server..."
exec python api.py