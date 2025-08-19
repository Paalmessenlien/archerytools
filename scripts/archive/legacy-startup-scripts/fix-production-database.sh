#!/bin/bash

echo "🔧 Fixing production database schema..."

# Create a temporary fix script that will run inside the container
cat > /tmp/fix-db.py << 'EOF'
#!/usr/bin/env python3
import sqlite3
import os

# Try different possible paths for user_data.db
paths_to_try = [
    "/app/user_data/user_data.db",
    "/app/user_data.db",
    "user_data.db"
]

db_path = None
for path in paths_to_try:
    if os.path.exists(path):
        db_path = path
        print(f"✅ Found database at: {path}")
        break

if not db_path:
    print("❌ Could not find user_data.db")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute("PRAGMA table_info(bow_setups)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Add missing columns
    missing_columns = []
    
    if 'bow_usage' not in columns:
        cursor.execute("ALTER TABLE bow_setups ADD COLUMN bow_usage TEXT")
        missing_columns.append('bow_usage')
        
    if 'riser_model' not in columns:
        cursor.execute("ALTER TABLE bow_setups ADD COLUMN riser_model TEXT")
        missing_columns.append('riser_model')
        
    if 'limb_model' not in columns:
        cursor.execute("ALTER TABLE bow_setups ADD COLUMN limb_model TEXT")
        missing_columns.append('limb_model')
        
    if 'compound_model' not in columns:
        cursor.execute("ALTER TABLE bow_setups ADD COLUMN compound_model TEXT")
        missing_columns.append('compound_model')
    
    if missing_columns:
        conn.commit()
        print(f"✅ Added missing columns: {missing_columns}")
    else:
        print("✅ All columns already exist")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
EOF

# Copy and run the fix script in the container
echo "📦 Copying fix script to container..."
sudo docker cp /tmp/fix-db.py arrowtuner-api:/tmp/fix-db.py

echo "🔄 Running database fix..."
sudo docker exec arrowtuner-api python /tmp/fix-db.py

echo "🔄 Restarting API container..."
sudo docker-compose -f docker-compose.ssl.yml restart api

echo "✅ Database fix complete!"
echo "🧹 Cleaning up..."
rm /tmp/fix-db.py

echo "
📌 Next steps:
1. Test creating a bow setup to verify the fix worked
2. Pull the latest code: git pull
3. Rebuild with persistent volume: sudo ./docker-deploy.sh docker-compose.ssl.yml -d --build
"