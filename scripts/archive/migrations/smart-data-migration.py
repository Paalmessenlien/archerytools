#!/usr/bin/env python3
"""
Smart Data Migration Script
Intelligently migrates user data handling schema differences
"""

import sqlite3
import os
import sys
import shutil
from datetime import datetime

def add_missing_columns(cursor, table_name, required_columns):
    """Add missing columns to target table"""
    try:
        cursor.execute(f'PRAGMA table_info({table_name})')
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        for col_name, col_def in required_columns.items():
            if col_name not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}')
                    print(f"  ✅ Added column {table_name}.{col_name}")
                except Exception as e:
                    print(f"  ⚠️  Could not add {table_name}.{col_name}: {e}")
        
    except Exception as e:
        print(f"  ❌ Error adding columns to {table_name}: {e}")

def migrate_users_smart(source_cursor, target_cursor):
    """Smart user migration with schema adaptation"""
    print("🔄 Smart user migration...")
    
    # First, add missing columns to users table in target
    required_columns = {
        'draw_length': 'REAL DEFAULT 28.0',
        'skill_level': 'TEXT DEFAULT "intermediate"',
        'shooting_style': 'TEXT DEFAULT "target"',
        'preferred_manufacturers': 'TEXT',
        'notes': 'TEXT'
    }
    
    add_missing_columns(target_cursor, 'users', required_columns)
    
    # Get source users
    source_cursor.execute('SELECT * FROM users')
    source_users = source_cursor.fetchall()
    
    source_cursor.execute('PRAGMA table_info(users)')
    source_columns = [col[1] for col in source_cursor.fetchall()]
    
    if not source_users:
        print("  ℹ️  No users to migrate")
        return {}
    
    # Get target table structure
    target_cursor.execute('PRAGMA table_info(users)')
    target_columns = [col[1] for col in target_cursor.fetchall()]
    
    # Get existing users in target
    target_cursor.execute('SELECT google_id, id FROM users')
    existing_users = {row[0]: row[1] for row in target_cursor.fetchall()}
    
    id_mapping = {}
    migrated_count = 0
    
    for user_row in source_users:
        user_dict = dict(zip(source_columns, user_row))
        source_id = user_dict['id']
        google_id = user_dict['google_id']
        
        if google_id in existing_users:
            id_mapping[source_id] = existing_users[google_id]
            print(f"  ℹ️  User {google_id} already exists")
            continue
        
        # Build insert with only common columns
        common_columns = [col for col in source_columns if col in target_columns and col != 'id']
        values = [user_dict[col] for col in common_columns]
        
        # Add default values for new required columns
        if 'draw_length' not in source_columns and 'draw_length' in target_columns:
            common_columns.append('draw_length')
            values.append(28.0)  # Default draw length
        
        placeholders = ', '.join(['?' for _ in values])
        columns_str = ', '.join(common_columns)
        
        try:
            target_cursor.execute(f'INSERT INTO users ({columns_str}) VALUES ({placeholders})', values)
            new_id = target_cursor.lastrowid
            id_mapping[source_id] = new_id
            migrated_count += 1
            print(f"  ✅ Migrated user {google_id}: {source_id} -> {new_id}")
        except Exception as e:
            print(f"  ❌ Error migrating user {google_id}: {e}")
    
    print(f"  📊 Migrated {migrated_count} users")
    return id_mapping

def migrate_bow_setups_smart(source_cursor, target_cursor, id_mapping):
    """Smart bow setup migration with schema adaptation"""
    print("🔄 Smart bow setup migration...")
    
    # Add missing columns to bow_setups table
    required_columns = {
        'draw_length': 'REAL DEFAULT 28.0',
        'point_weight': 'REAL DEFAULT 100.0',
        'nock_weight': 'REAL DEFAULT 8.0',
        'fletching_weight': 'REAL DEFAULT 24.0',
        'insert_weight': 'REAL DEFAULT 12.0',
        'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'bow_make': 'TEXT',
        'bow_model': 'TEXT',
        'setup_name': 'TEXT',
        'brace_height': 'REAL'
    }
    
    add_missing_columns(target_cursor, 'bow_setups', required_columns)
    
    # Get source bow setups
    source_cursor.execute('SELECT * FROM bow_setups')
    source_setups = source_cursor.fetchall()
    
    if not source_setups:
        print("  ℹ️  No bow setups to migrate")
        return
    
    source_cursor.execute('PRAGMA table_info(bow_setups)')
    source_columns = [col[1] for col in source_cursor.fetchall()]
    
    target_cursor.execute('PRAGMA table_info(bow_setups)')
    target_columns = [col[1] for col in target_cursor.fetchall()]
    
    migrated_count = 0
    
    for setup_row in source_setups:
        setup_dict = dict(zip(source_columns, setup_row))
        source_user_id = setup_dict['user_id']
        
        # Map user ID
        if source_user_id not in id_mapping:
            print(f"  ⚠️  Skipping setup {setup_dict.get('id', 'unknown')} - user {source_user_id} not mapped")
            continue
        
        target_user_id = id_mapping[source_user_id]
        setup_dict['user_id'] = target_user_id
        
        # Build insert with available columns and defaults
        insert_data = {}
        
        # Copy available columns
        for col in target_columns:
            if col == 'id':
                continue  # Skip ID, let it auto-increment
            elif col in setup_dict and setup_dict[col] is not None:
                insert_data[col] = setup_dict[col]
            elif col == 'draw_length' and col not in setup_dict:
                insert_data[col] = 28.0  # Default draw length
            elif col == 'point_weight' and col not in setup_dict:
                insert_data[col] = 100.0  # Default point weight
            elif col in ['nock_weight', 'fletching_weight', 'insert_weight'] and col not in setup_dict:
                insert_data[col] = {'nock_weight': 8.0, 'fletching_weight': 24.0, 'insert_weight': 12.0}[col]
            elif col == 'setup_name' and col not in setup_dict:
                insert_data[col] = setup_dict.get('name', f"Setup {setup_dict.get('id', 'Unknown')}")
        
        if 'bow_type' not in insert_data or 'draw_weight' not in insert_data:
            print(f"  ⚠️  Skipping setup {setup_dict.get('id', 'unknown')} - missing required fields")
            continue
        
        columns = list(insert_data.keys())
        values = list(insert_data.values())
        placeholders = ', '.join(['?' for _ in values])
        columns_str = ', '.join(columns)
        
        try:
            target_cursor.execute(f'INSERT INTO bow_setups ({columns_str}) VALUES ({placeholders})', values)
            migrated_count += 1
            print(f"  ✅ Migrated bow setup: {setup_dict.get('name', 'Unknown')}")
        except Exception as e:
            print(f"  ❌ Error migrating setup {setup_dict.get('id', 'unknown')}: {e}")
    
    print(f"  📊 Migrated {migrated_count} bow setups")

def migrate_equipment_smart(source_cursor, target_cursor):
    """Smart equipment migration"""
    print("🔄 Smart equipment migration...")
    
    # Check if equipment tables exist and have data
    try:
        source_cursor.execute('SELECT COUNT(*) FROM bow_equipment')
        equipment_count = source_cursor.fetchone()[0]
        
        if equipment_count == 0:
            print("  ℹ️  No equipment to migrate")
            return
        
        # Add missing columns to bow_equipment table
        required_columns = {
            'setup_id': 'INTEGER',
            'installed_at': 'TIMESTAMP',
            'manufacturer': 'TEXT',
            'category': 'TEXT',
            'model': 'TEXT',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'specifications': 'TEXT'
        }
        
        add_missing_columns(target_cursor, 'bow_equipment', required_columns)
        
        # Get equipment data and migrate with available columns
        source_cursor.execute('SELECT * FROM bow_equipment')
        equipment_rows = source_cursor.fetchall()
        
        source_cursor.execute('PRAGMA table_info(bow_equipment)')
        source_columns = [col[1] for col in source_cursor.fetchall()]
        
        target_cursor.execute('PRAGMA table_info(bow_equipment)')
        target_columns = [col[1] for col in target_cursor.fetchall()]
        
        migrated_count = 0
        for equipment_row in equipment_rows:
            equipment_dict = dict(zip(source_columns, equipment_row))
            
            # Map columns
            insert_data = {}
            for col in target_columns:
                if col == 'id':
                    continue
                elif col in equipment_dict and equipment_dict[col] is not None:
                    insert_data[col] = equipment_dict[col]
                elif col == 'manufacturer' and 'manufacturer_name' in equipment_dict:
                    insert_data[col] = equipment_dict['manufacturer_name']
                elif col == 'category' and 'category_name' in equipment_dict:
                    insert_data[col] = equipment_dict['category_name']
                elif col == 'model' and 'model_name' in equipment_dict:
                    insert_data[col] = equipment_dict['model_name']
            
            if insert_data:
                columns = list(insert_data.keys())
                values = list(insert_data.values())
                placeholders = ', '.join(['?' for _ in values])
                columns_str = ', '.join(columns)
                
                try:
                    target_cursor.execute(f'INSERT INTO bow_equipment ({columns_str}) VALUES ({placeholders})', values)
                    migrated_count += 1
                except Exception as e:
                    print(f"  ⚠️  Could not migrate equipment record: {e}")
        
        print(f"  📊 Migrated {migrated_count} equipment records")
        
    except Exception as e:
        print(f"  ❌ Error migrating equipment: {e}")

def smart_data_migration():
    """Main smart migration function"""
    print("🧠 Smart Data Migration Script")
    print("=" * 50)
    
    # Backup databases
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    arrow_db_path = '/app/databases/arrow_database.db'
    user_db_path = '/app/databases/user_data.db'
    
    if not os.path.exists(user_db_path):
        print("❌ No user database found to migrate from")
        return False
    
    # Create backup
    backup_path = f"{arrow_db_path}.smart_migration_backup_{timestamp}"
    shutil.copy2(arrow_db_path, backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    
    try:
        # Connect to databases
        user_conn = sqlite3.connect(user_db_path)
        user_cursor = user_conn.cursor()
        
        arrow_conn = sqlite3.connect(arrow_db_path)
        arrow_cursor = arrow_conn.cursor()
        
        # Enable foreign keys but disable for migration
        arrow_cursor.execute("PRAGMA foreign_keys = OFF")
        
        print(f"\n📊 Starting smart migration...")
        
        # Step 1: Migrate users with ID mapping
        id_mapping = migrate_users_smart(user_cursor, arrow_cursor)
        
        # Step 2: Migrate bow setups
        migrate_bow_setups_smart(user_cursor, arrow_cursor, id_mapping)
        
        # Step 3: Migrate equipment
        migrate_equipment_smart(user_cursor, arrow_cursor)
        
        # Step 4: Migrate any other compatible data
        compatible_tables = ['backup_metadata', 'equipment_field_standards']
        for table in compatible_tables:
            try:
                # Check if table exists in both databases
                user_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if user_cursor.fetchone():
                    arrow_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    if arrow_cursor.fetchone():
                        user_cursor.execute(f'SELECT COUNT(*) FROM {table}')
                        count = user_cursor.fetchone()[0]
                        if count > 0:
                            print(f"\n🔄 Migrating {table}...")
                            user_cursor.execute(f'SELECT * FROM {table}')
                            rows = user_cursor.fetchall()
                            
                            user_cursor.execute(f'PRAGMA table_info({table})')
                            columns = [col[1] for col in user_cursor.fetchall()]
                            
                            # Simple replace migration for configuration tables
                            arrow_cursor.execute(f'DELETE FROM {table}')  # Clear existing
                            
                            placeholders = ', '.join(['?' for _ in columns])
                            columns_str = ', '.join(columns)
                            
                            arrow_cursor.executemany(f'INSERT INTO {table} ({columns_str}) VALUES ({placeholders})', rows)
                            print(f"  ✅ Migrated {len(rows)} rows from {table}")
            except Exception as e:
                print(f"  ⚠️  Could not migrate {table}: {e}")
        
        # Re-enable foreign keys
        arrow_cursor.execute("PRAGMA foreign_keys = ON")
        
        # Commit changes
        arrow_conn.commit()
        
        # Verification
        print(f"\n🔍 Verifying migration...")
        
        arrow_cursor.execute('SELECT COUNT(*) FROM users')
        user_count = arrow_cursor.fetchone()[0]
        print(f"  👥 Total users: {user_count}")
        
        arrow_cursor.execute('SELECT COUNT(*) FROM bow_setups')
        setup_count = arrow_cursor.fetchone()[0]
        print(f"  🏹 Total bow setups: {setup_count}")
        
        arrow_cursor.execute('SELECT COUNT(*) FROM bow_equipment')
        equipment_count = arrow_cursor.fetchone()[0]
        print(f"  ⚙️  Total equipment: {equipment_count}")
        
        user_conn.close()
        arrow_conn.close()
        
        print(f"\n✅ Smart migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = smart_data_migration()
    
    if success:
        print("\n🎉 Smart data migration completed!")
        print("🔄 Please restart the API container:")
        print("   docker restart arrowtuner-api-dev")
    else:
        print("\n❌ Migration failed. Check logs and restore from backup if needed.")
    
    print("=" * 50)