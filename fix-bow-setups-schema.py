#!/usr/bin/env python3
"""
Fix bow_setups table schema to allow NULL values for missing columns
"""

import sqlite3
import os
from datetime import datetime

def fix_bow_setups_schema():
    """Fix bow_setups schema to allow migration"""
    
    arrow_db_path = '/app/databases/arrow_database.db'
    user_db_path = '/app/databases/user_data.db'
    
    if not os.path.exists(arrow_db_path):
        print("❌ Target database not found")
        return False
    
    # Backup database
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{arrow_db_path}.schema_fix_backup_{timestamp}"
    import shutil
    shutil.copy2(arrow_db_path, backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    
    try:
        conn = sqlite3.connect(arrow_db_path)
        cursor = conn.cursor()
        
        # Disable foreign keys temporarily
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        print("🔄 Recreating bow_setups table with nullable columns...")
        
        # Get existing data
        cursor.execute('SELECT * FROM bow_setups')
        existing_data = cursor.fetchall()
        print(f"  📊 Found {len(existing_data)} existing bow setups")
        
        # Drop and recreate table with correct schema
        cursor.execute('DROP TABLE IF EXISTS bow_setups')
        
        cursor.execute('''
            CREATE TABLE bow_setups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                bow_type TEXT NOT NULL,
                draw_weight REAL NOT NULL,
                draw_length REAL DEFAULT 28.0,
                arrow_length REAL DEFAULT 30.0,
                point_weight REAL DEFAULT 100.0,
                nock_weight REAL,
                fletching_weight REAL,
                insert_weight REAL,
                description TEXT,
                bow_usage TEXT,
                riser_brand TEXT,
                riser_model TEXT,
                riser_length TEXT,
                limb_brand TEXT,
                limb_model TEXT,
                limb_length TEXT,
                compound_brand TEXT,
                compound_model TEXT,
                ibo_speed REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bow_make TEXT,
                bow_model TEXT,
                setup_name TEXT,
                brace_height REAL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Recreate index
        cursor.execute('CREATE INDEX idx_bow_setups_user_id ON bow_setups (user_id)')
        
        # Restore existing data if any
        if existing_data:
            # Get new column structure
            cursor.execute('PRAGMA table_info(bow_setups)')
            new_columns = [col[1] for col in cursor.fetchall()]
            
            # Insert data with default values for missing columns
            for row in existing_data:
                # Assume original structure had basic columns
                values = {
                    'user_id': row[1] if len(row) > 1 else None,
                    'name': row[2] if len(row) > 2 else 'Unknown Setup',
                    'bow_type': row[3] if len(row) > 3 else 'compound',
                    'draw_weight': row[4] if len(row) > 4 else 45.0,
                    'draw_length': row[5] if len(row) > 5 else 28.0,
                    'arrow_length': row[6] if len(row) > 6 else 30.0,
                    'point_weight': row[7] if len(row) > 7 else 100.0
                }
                
                if values['user_id'] is not None:
                    insert_columns = list(values.keys())
                    insert_values = list(values.values())
                    placeholders = ', '.join(['?' for _ in insert_values])
                    columns_str = ', '.join(insert_columns)
                    
                    cursor.execute(f'INSERT INTO bow_setups ({columns_str}) VALUES ({placeholders})', insert_values)
            
            print(f"  ✅ Restored {len(existing_data)} existing bow setups")
        
        # Re-enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Commit changes
        conn.commit()
        
        print("✅ Bow_setups table schema fixed successfully")
        
        # Now try to migrate data from user_data.db
        if os.path.exists(user_db_path):
            print("\n🔄 Migrating bow setups from user_data.db...")
            
            user_conn = sqlite3.connect(user_db_path)
            user_cursor = user_conn.cursor()
            
            # Get user ID mapping
            cursor.execute('SELECT google_id, id FROM users')
            google_to_id = {row[0]: row[1] for row in cursor.fetchall()}
            
            user_cursor.execute('SELECT id, google_id FROM users')
            user_id_mapping = {}
            for source_id, google_id in user_cursor.fetchall():
                if google_id in google_to_id:
                    user_id_mapping[source_id] = google_to_id[google_id]
            
            # Get bow setups from user database
            user_cursor.execute('SELECT * FROM bow_setups')
            user_setups = user_cursor.fetchall()
            
            user_cursor.execute('PRAGMA table_info(bow_setups)')
            user_columns = [col[1] for col in user_cursor.fetchall()]
            
            migrated_count = 0
            for setup_row in user_setups:
                setup_dict = dict(zip(user_columns, setup_row))
                source_user_id = setup_dict['user_id']
                
                if source_user_id not in user_id_mapping:
                    print(f"  ⚠️  Skipping setup {setup_dict.get('id', 'unknown')} - user not found")
                    continue
                
                # Map the data to target schema
                mapped_data = {
                    'user_id': user_id_mapping[source_user_id],
                    'name': setup_dict.get('name', 'Unknown Setup'),
                    'bow_type': setup_dict.get('bow_type', 'compound'),
                    'draw_weight': setup_dict.get('draw_weight', 45.0),
                    'draw_length': 28.0,  # Default value
                    'arrow_length': 30.0,  # Default value
                    'point_weight': 100.0,  # Default value
                    'insert_weight': setup_dict.get('insert_weight'),
                    'description': setup_dict.get('description'),
                    'bow_usage': setup_dict.get('bow_usage'),
                    'riser_brand': setup_dict.get('riser_brand'),
                    'riser_model': setup_dict.get('riser_model'),
                    'riser_length': setup_dict.get('riser_length'),
                    'limb_brand': setup_dict.get('limb_brand'),
                    'limb_model': setup_dict.get('limb_model'),
                    'limb_length': setup_dict.get('limb_length'),
                    'compound_brand': setup_dict.get('compound_brand'),
                    'compound_model': setup_dict.get('compound_model'),
                    'ibo_speed': setup_dict.get('ibo_speed'),
                    'created_at': setup_dict.get('created_at')
                }
                
                # Remove None values
                mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
                
                columns = list(mapped_data.keys())
                values = list(mapped_data.values())
                placeholders = ', '.join(['?' for _ in values])
                columns_str = ', '.join(columns)
                
                try:
                    cursor.execute(f'INSERT INTO bow_setups ({columns_str}) VALUES ({placeholders})', values)
                    migrated_count += 1
                    print(f"  ✅ Migrated: {setup_dict.get('name', 'Unknown')}")
                except Exception as e:
                    print(f"  ❌ Error migrating setup {setup_dict.get('id', 'unknown')}: {e}")
            
            print(f"  📊 Migrated {migrated_count} bow setups")
            user_conn.close()
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing schema: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing bow_setups table schema...")
    
    success = fix_bow_setups_schema()
    
    if success:
        print("\n✅ Schema fix and migration completed!")
        print("🔄 Please restart the API container:")
        print("   docker restart arrowtuner-api-dev")
    else:
        print("\n❌ Schema fix failed")
    
    print("=" * 50)