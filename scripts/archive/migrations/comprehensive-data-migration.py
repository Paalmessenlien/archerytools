#!/usr/bin/env python3
"""
Comprehensive Data Migration Script
Migrates all user data from separate user_data.db into unified arrow_database.db
"""

import sqlite3
import os
import sys
import shutil
from datetime import datetime

def backup_databases():
    """Create backups of both databases before migration"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Backup unified database
    arrow_db_path = '/app/databases/arrow_database.db'
    if os.path.exists(arrow_db_path):
        backup_path = f"{arrow_db_path}.pre_data_migration_{timestamp}"
        shutil.copy2(arrow_db_path, backup_path)
        print(f"✅ Arrow database backed up to: {backup_path}")
    
    # Backup user database
    user_db_path = '/app/databases/user_data.db'
    if os.path.exists(user_db_path):
        backup_path = f"{user_db_path}.pre_migration_{timestamp}"
        shutil.copy2(user_db_path, backup_path)
        print(f"✅ User database backed up to: {backup_path}")
        return user_db_path
    
    return None

def migrate_table_data(source_cursor, target_cursor, table_name, id_mapping=None):
    """Migrate data from source table to target table"""
    try:
        # Get source table structure
        source_cursor.execute(f'PRAGMA table_info({table_name})')
        source_columns = [col[1] for col in source_cursor.fetchall()]
        
        # Get target table structure
        target_cursor.execute(f'PRAGMA table_info({table_name})')
        target_columns = [col[1] for col in target_cursor.fetchall()]
        
        # Find common columns
        common_columns = [col for col in source_columns if col in target_columns]
        
        if not common_columns:
            print(f"  ⚠️  No common columns found for {table_name}")
            return 0
        
        # Get data from source
        columns_str = ', '.join(common_columns)
        source_cursor.execute(f'SELECT {columns_str} FROM {table_name}')
        rows = source_cursor.fetchall()
        
        if not rows:
            print(f"  ℹ️  No data in {table_name}")
            return 0
        
        # Prepare insert statement for target
        placeholders = ', '.join(['?' for _ in common_columns])
        insert_sql = f'INSERT OR REPLACE INTO {table_name} ({columns_str}) VALUES ({placeholders})'
        
        # Apply ID mapping if provided (for foreign key consistency)
        if id_mapping and table_name in ['bow_setups', 'guide_sessions', 'bow_equipment', 'setup_arrows']:
            processed_rows = []
            for row in rows:
                row_dict = dict(zip(common_columns, row))
                if 'user_id' in row_dict and row_dict['user_id'] in id_mapping:
                    row_dict['user_id'] = id_mapping[row_dict['user_id']]
                processed_rows.append(tuple(row_dict[col] for col in common_columns))
            rows = processed_rows
        
        # Insert data into target
        target_cursor.executemany(insert_sql, rows)
        
        print(f"  ✅ Migrated {len(rows)} rows from {table_name}")
        return len(rows)
        
    except Exception as e:
        print(f"  ❌ Error migrating {table_name}: {e}")
        return 0

def migrate_users_with_id_mapping(source_cursor, target_cursor):
    """Migrate users and return ID mapping for foreign key consistency"""
    try:
        # Get existing users in target to avoid conflicts
        target_cursor.execute('SELECT google_id, id FROM users')
        existing_users = {row[0]: row[1] for row in target_cursor.fetchall()}
        
        # Get users from source
        source_cursor.execute('SELECT * FROM users')
        source_users = source_cursor.fetchall()
        
        # Get column names
        source_cursor.execute('PRAGMA table_info(users)')
        column_names = [col[1] for col in source_cursor.fetchall()]
        
        id_mapping = {}
        migrated_count = 0
        
        for user_row in source_users:
            user_dict = dict(zip(column_names, user_row))
            source_id = user_dict['id']
            google_id = user_dict['google_id']
            
            if google_id in existing_users:
                # User already exists, use existing ID
                id_mapping[source_id] = existing_users[google_id]
                print(f"  ℹ️  User {google_id} already exists, using existing ID {existing_users[google_id]}")
            else:
                # Insert new user (without original ID to avoid conflicts)
                insert_columns = [col for col in column_names if col != 'id']
                insert_values = [user_dict[col] for col in insert_columns]
                
                placeholders = ', '.join(['?' for _ in insert_columns])
                columns_str = ', '.join(insert_columns)
                
                target_cursor.execute(f'INSERT INTO users ({columns_str}) VALUES ({placeholders})', insert_values)
                new_id = target_cursor.lastrowid
                id_mapping[source_id] = new_id
                migrated_count += 1
                
                print(f"  ✅ Migrated user {google_id}: {source_id} -> {new_id}")
        
        print(f"  📊 User migration complete: {migrated_count} new users, {len(id_mapping)} total ID mappings")
        return id_mapping
        
    except Exception as e:
        print(f"  ❌ Error migrating users: {e}")
        return {}

def comprehensive_data_migration():
    """Main migration function"""
    print("🔄 Comprehensive Data Migration Script")
    print("=" * 50)
    
    # Check if running in Docker container
    if os.path.exists('/.dockerenv'):
        print("🐳 Running inside Docker container")
    
    # Create backups
    user_db_path = backup_databases()
    if not user_db_path:
        print("❌ No user database found to migrate from")
        return False
    
    arrow_db_path = '/app/databases/arrow_database.db'
    if not os.path.exists(arrow_db_path):
        print("❌ Target unified database not found")
        return False
    
    try:
        # Connect to both databases
        user_conn = sqlite3.connect(user_db_path)
        user_cursor = user_conn.cursor()
        
        arrow_conn = sqlite3.connect(arrow_db_path)
        arrow_cursor = arrow_conn.cursor()
        
        # Enable foreign keys
        arrow_cursor.execute("PRAGMA foreign_keys = ON")
        
        print(f"\n🔍 Analyzing source database: {user_db_path}")
        
        # Get list of tables to migrate
        user_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        user_tables = [row[0] for row in user_cursor.fetchall()]
        
        # Tables that need special handling or should be migrated in order
        migration_order = [
            'users',                    # Must be first for ID mapping
            'bow_setups',              # Depends on users
            'guide_sessions',          # Depends on users and bow_setups
            'setup_arrows',            # Depends on bow_setups
            'bow_equipment',           # Depends on bow_setups
            'backup_metadata',         # Administrative data
            'equipment_field_standards', # Configuration data
            'manufacturer_equipment_categories', # Configuration data
        ]
        
        # Add any other tables found in user database
        other_tables = [table for table in user_tables if table not in migration_order and 
                       table not in ['schema_migrations', 'database_migrations', 'sqlite_sequence']]
        migration_order.extend(other_tables)
        
        print(f"📋 Tables to migrate: {len([t for t in migration_order if t in user_tables])}")
        
        total_migrated = 0
        id_mapping = {}
        
        # Migrate tables in order
        for table_name in migration_order:
            if table_name not in user_tables:
                continue
                
            print(f"\n🔄 Migrating {table_name}...")
            
            if table_name == 'users':
                # Special handling for users to maintain referential integrity
                id_mapping = migrate_users_with_id_mapping(user_cursor, arrow_cursor)
                if id_mapping:
                    total_migrated += len(id_mapping)
            else:
                # Regular table migration
                migrated = migrate_table_data(user_cursor, arrow_cursor, table_name, id_mapping)
                total_migrated += migrated
        
        # Commit changes
        arrow_conn.commit()
        print(f"\n✅ Migration completed successfully!")
        print(f"📊 Total records migrated: {total_migrated}")
        
        # Verify migration
        print(f"\n🔍 Verifying migration...")
        
        # Check user count
        arrow_cursor.execute('SELECT COUNT(*) FROM users')
        user_count = arrow_cursor.fetchone()[0]
        print(f"  👥 Total users in unified database: {user_count}")
        
        # Check bow setups
        arrow_cursor.execute('SELECT COUNT(*) FROM bow_setups')
        setup_count = arrow_cursor.fetchone()[0]
        print(f"  🏹 Total bow setups: {setup_count}")
        
        # Check equipment
        arrow_cursor.execute('SELECT COUNT(*) FROM bow_equipment')
        equipment_count = arrow_cursor.fetchone()[0]
        print(f"  ⚙️  Total equipment entries: {equipment_count}")
        
        user_conn.close()
        arrow_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Starting comprehensive data migration...")
    
    success = comprehensive_data_migration()
    
    if success:
        print("\n🎉 Data migration completed successfully!")
        print("🔄 Please restart the API container:")
        print("   docker restart arrowtuner-api-dev")
        print("\n🔍 After restart, verify data in admin panel")
        print("\n📁 Consider removing user_data.db after verification:")
        print("   docker exec arrowtuner-api-dev mv /app/databases/user_data.db /app/databases/user_data.db.archived")
    else:
        print("\n❌ Data migration failed. Check the logs and restore from backup if needed.")
    
    print("=" * 50)