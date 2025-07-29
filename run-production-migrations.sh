#\!/bin/bash

echo "🚀 Running database migrations on production..."

# Run the migrations inside the API container
echo "📦 Running migration to remove arrow fields..."
sudo docker exec arrowtuner-api python /app/migrate_remove_arrow_fields.py

echo "📦 Running migration to add bow info fields..."
sudo docker exec arrowtuner-api python /app/migrate_add_bow_info_fields.py

echo "📦 Running migration to add compound model field..."
sudo docker exec arrowtuner-api python /app/migrate_add_compound_model.py

echo "✅ All migrations completed\!"
echo "🔄 Restarting API container to ensure changes are loaded..."
sudo docker-compose -f docker-compose.ssl.yml restart api

echo "🎯 Production database migrations complete\!"
