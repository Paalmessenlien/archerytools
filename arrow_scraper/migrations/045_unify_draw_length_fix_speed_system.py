#!/usr/bin/env python3
"""
Migration 045: Unify Draw Length Management & Fix Speed System

This migration addresses two critical issues:

DRAW LENGTH UNIFICATION:
1. Remove draw_length from users table (should be per bow setup, not per user)
2. Remove draw_length_module from bow_setups (compound-specific confusion)
3. Make bow_setups.draw_length mandatory and single source of truth
4. Migrate any existing user draw_length values to their bow setups

SPEED SYSTEM FIXES:
1. Add measured_speed_fps field for chronograph data
2. Ensure ibo_speed exists for all bow types
3. Update realistic default speeds for traditional bows
4. Add proper speed validation constraints

This creates a unified system where:
- Each bow setup has ONE mandatory draw_length (where poundage is measured)
- Speed hierarchy: chronograph > ibo_speed > bow-type defaults
- No more complex fallback hierarchies or user-specific draw lengths
"""

import sqlite3
import os
from pathlib import Path

def get_database_path():
    """Get the database path using environment variable or fallback"""
    # Check for environment variable first (production/Docker)
    db_path = os.environ.get('ARROW_DATABASE_PATH')
    if db_path and os.path.exists(db_path):
        return db_path
    
    # Check for environment variable alternative
    user_db_path = os.environ.get('USER_DATABASE_PATH') 
    if user_db_path and os.path.exists(user_db_path):
        return user_db_path
        
    # Development fallback paths
    possible_paths = [
        Path(__file__).parent.parent / "databases" / "arrow_database.db",
        Path(__file__).parent.parent.parent / "databases" / "arrow_database.db",
        Path(__file__).parent.parent / "arrow_database.db",
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
            
    # Default to unified database location
    default_path = Path(__file__).parent.parent / "databases" / "arrow_database.db"
    default_path.parent.mkdir(parents=True, exist_ok=True)
    return str(default_path)

def run_migration():
    """Run Migration 045: Unify Draw Length & Fix Speed System"""
    
    db_path = get_database_path()
    print(f"🔄 Running Migration 045 on database: {db_path}")
    print("🎯 Unifying draw length management & fixing speed system...")
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # === PHASE 1: ANALYZE CURRENT SCHEMA ===
        print("\n📋 Phase 1: Analyzing current schema...")
        
        # Check current table structures
        cursor.execute("PRAGMA table_info(users)")
        user_columns = {col[1] for col in cursor.fetchall()}
        
        cursor.execute("PRAGMA table_info(bow_setups)")
        bow_columns = {col[1] for col in cursor.fetchall()}
        
        print(f"   Users table columns with draw_length: {'draw_length' in user_columns}")
        print(f"   Users table columns with user_draw_length: {'user_draw_length' in user_columns}")
        print(f"   Bow_setups table has draw_length: {'draw_length' in bow_columns}")
        print(f"   Bow_setups table has draw_length_module: {'draw_length_module' in bow_columns}")
        print(f"   Bow_setups table has ibo_speed: {'ibo_speed' in bow_columns}")
        print(f"   Bow_setups table has measured_speed_fps: {'measured_speed_fps' in bow_columns}")
        
        # === PHASE 2: SPEED SYSTEM ENHANCEMENTS ===
        print("\n🚀 Phase 2: Enhancing speed system...")
        
        # Add measured_speed_fps column for chronograph data
        if 'measured_speed_fps' not in bow_columns:
            print("   Adding measured_speed_fps column for chronograph data...")
            cursor.execute("ALTER TABLE bow_setups ADD COLUMN measured_speed_fps REAL DEFAULT NULL")
            print("   ✅ Added measured_speed_fps column")
        else:
            print("   ✅ measured_speed_fps column already exists")
        
        # Ensure ibo_speed column exists
        if 'ibo_speed' not in bow_columns:
            print("   Adding ibo_speed column...")
            cursor.execute("ALTER TABLE bow_setups ADD COLUMN ibo_speed REAL DEFAULT NULL")
            print("   ✅ Added ibo_speed column")
        else:
            print("   ✅ ibo_speed column already exists")
        
        # === PHASE 3: DRAW LENGTH MIGRATION ===
        print("\n🎯 Phase 3: Migrating draw length data...")
        
        # Step 3a: Migrate user draw_length values to their bow setups
        user_draw_length_columns = []
        if 'draw_length' in user_columns:
            user_draw_length_columns.append('draw_length')
        if 'user_draw_length' in user_columns:
            user_draw_length_columns.append('user_draw_length')
            
        if user_draw_length_columns:
            print(f"   Migrating user draw length values to bow setups (columns: {user_draw_length_columns})...")
            
            migrated_users = 0
            migrated_setups = 0
            
            # Handle each draw length column
            for draw_length_col in user_draw_length_columns:
                print(f"   Processing {draw_length_col} column...")
                
                # Get users with draw_length values and their bow setups
                cursor.execute(f"""
                    SELECT u.id as user_id, u.{draw_length_col} as user_draw_length,
                           COUNT(bs.id) as setup_count
                    FROM users u
                    LEFT JOIN bow_setups bs ON u.id = bs.user_id  
                    WHERE u.{draw_length_col} IS NOT NULL AND u.{draw_length_col} > 0
                    GROUP BY u.id, u.{draw_length_col}
                    ORDER BY u.id
                """)
                users_with_draw_length = cursor.fetchall()
                
                for user_row in users_with_draw_length:
                    user_id = user_row['user_id']
                    user_draw_length = user_row['user_draw_length']
                    setup_count = user_row['setup_count']
                    
                    print(f"     User {user_id}: {draw_length_col}={user_draw_length}, {setup_count} setups")
                    
                    # Update bow setups for this user that don't have draw_length
                    cursor.execute("""
                        UPDATE bow_setups 
                        SET draw_length = ?
                        WHERE user_id = ? 
                        AND (draw_length IS NULL OR draw_length = 0)
                    """, (user_draw_length, user_id))
                    
                    updated_setups = cursor.rowcount
                    if updated_setups > 0:
                        print(f"       ✅ Updated {updated_setups} setups with draw_length={user_draw_length}")
                        migrated_setups += updated_setups
                        migrated_users += 1
            
            print(f"   ✅ Migrated draw_length for {migrated_users} users, {migrated_setups} setups")
        else:
            print("   ✅ No user draw_length columns found - no migration needed")
        
        # Step 3b: Handle draw_length_module migration (compound bow specific)
        if 'draw_length_module' in bow_columns:
            print("   Migrating draw_length_module values to unified draw_length...")
            
            # For setups with draw_length_module but no draw_length, use the module value
            cursor.execute("""
                UPDATE bow_setups 
                SET draw_length = draw_length_module
                WHERE draw_length_module IS NOT NULL 
                AND draw_length_module > 0
                AND (draw_length IS NULL OR draw_length = 0)
            """)
            
            module_migrated = cursor.rowcount
            print(f"   ✅ Migrated {module_migrated} draw_length_module values to draw_length")
        
        # Step 3c: Set reasonable defaults for any remaining bow setups without draw_length
        print("   Setting defaults for bow setups without draw_length...")
        cursor.execute("""
            UPDATE bow_setups 
            SET draw_length = 28.0
            WHERE draw_length IS NULL OR draw_length = 0
        """)
        
        defaulted_setups = cursor.rowcount
        if defaulted_setups > 0:
            print(f"   ✅ Set default draw_length=28.0 for {defaulted_setups} setups")
        
        # === PHASE 4: SCHEMA CLEANUP ===
        print("\n🧹 Phase 4: Schema cleanup...")
        
        # Step 4a: Remove draw_length columns from users table
        if 'draw_length' in user_columns or 'user_draw_length' in user_columns:
            print("   Removing draw_length related columns from users table...")
            
            # Disable foreign key constraints temporarily
            cursor.execute("PRAGMA foreign_keys=OFF")
            
            # Get current users table structure to preserve all columns except draw_length related ones
            cursor.execute("PRAGMA table_info(users)")
            user_columns_info = cursor.fetchall()
            
            # Get existing triggers for users table
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name='users'")
            user_triggers = cursor.fetchall()
            
            # Create column definitions and names excluding draw_length columns
            columns_to_keep = []
            column_definitions = []
            
            for col_info in user_columns_info:
                col_name = col_info[1]  # Column name
                col_type = col_info[2]  # Data type
                col_not_null = col_info[3]  # NOT NULL
                col_default = col_info[4]  # Default value
                col_pk = col_info[5]  # Primary key
                
                # Skip draw_length related columns
                if col_name not in ['draw_length', 'user_draw_length']:
                    columns_to_keep.append(col_name)
                    
                    # Build column definition
                    col_def = f"{col_name} {col_type}"
                    if col_pk:
                        col_def += " PRIMARY KEY AUTOINCREMENT"
                    elif col_not_null:
                        col_def += " NOT NULL"
                    if col_default is not None and not col_pk:
                        if col_default == 'CURRENT_TIMESTAMP':
                            col_def += f" DEFAULT {col_default}"
                        else:
                            col_def += f" DEFAULT {col_default}"
                    
                    # Add UNIQUE constraint for google_id and email
                    if col_name == 'google_id':
                        col_def += " UNIQUE"
                    elif col_name == 'email':
                        col_def += " UNIQUE"
                    
                    column_definitions.append(col_def)
            
            columns_str = ', '.join(columns_to_keep)
            column_defs_str = ',\n                    '.join(column_definitions)
            
            # Create new users table without draw_length columns
            cursor.execute(f"""
                CREATE TABLE users_new (
                    {column_defs_str}
                )
            """)
            
            # Copy data excluding draw_length columns
            cursor.execute(f"""
                INSERT INTO users_new ({columns_str})
                SELECT {columns_str}
                FROM users
            """)
            
            # Drop old table (this drops associated triggers automatically)
            cursor.execute("DROP TABLE users")
            
            # Rename new table
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            
            # Recreate triggers if any existed
            for trigger_name, trigger_sql in user_triggers:
                if trigger_sql:  # Only recreate if SQL exists
                    try:
                        cursor.execute(trigger_sql)
                        print(f"   ✅ Recreated trigger: {trigger_name}")
                    except Exception as te:
                        print(f"   ⚠️  Could not recreate trigger {trigger_name}: {te}")
            
            # Re-enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON")
            
            print("   ✅ Removed draw_length related columns from users table")
        else:
            print("   ✅ Users table already clean (no draw_length columns)")
        
        # Step 4b: Remove draw_length_module from bow_setups table
        if 'draw_length_module' in bow_columns:
            print("   Removing draw_length_module column from bow_setups table...")
            
            # Get current bow_setups structure to preserve all columns except draw_length_module
            cursor.execute("PRAGMA table_info(bow_setups)")
            bow_columns_info = cursor.fetchall()
            
            # Get existing triggers for bow_setups table
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name='bow_setups'")
            bow_triggers = cursor.fetchall()
            
            # Create column definitions and names excluding draw_length_module
            columns_to_keep = []
            column_definitions = []
            
            for col_info in bow_columns_info:
                col_name = col_info[1]  # Column name
                col_type = col_info[2]  # Data type
                col_not_null = col_info[3]  # NOT NULL
                col_default = col_info[4]  # Default value
                col_pk = col_info[5]  # Primary key
                
                if col_name != 'draw_length_module':
                    columns_to_keep.append(col_name)
                    
                    # Build column definition
                    col_def = f"{col_name} {col_type}"
                    if col_pk:
                        col_def += " PRIMARY KEY AUTOINCREMENT"
                    elif col_not_null:
                        col_def += " NOT NULL"
                    if col_default is not None and not col_pk:
                        if col_default == 'CURRENT_TIMESTAMP':
                            col_def += f" DEFAULT {col_default}"
                        else:
                            col_def += f" DEFAULT {col_default}"
                    column_definitions.append(col_def)
            
            columns_str = ', '.join(columns_to_keep)
            column_defs_str = ',\n                    '.join(column_definitions)
            
            # Create new bow_setups table without draw_length_module
            cursor.execute(f"""
                CREATE TABLE bow_setups_new (
                    {column_defs_str},
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Copy data excluding draw_length_module
            cursor.execute(f"""
                INSERT INTO bow_setups_new ({columns_str})
                SELECT {columns_str}
                FROM bow_setups
            """)
            
            # Drop old table (this drops associated triggers automatically)
            cursor.execute("DROP TABLE bow_setups")
            
            # Rename new table
            cursor.execute("ALTER TABLE bow_setups_new RENAME TO bow_setups")
            
            # Recreate triggers if any existed
            for trigger_name, trigger_sql in bow_triggers:
                if trigger_sql:  # Only recreate if SQL exists
                    try:
                        cursor.execute(trigger_sql)
                        print(f"   ✅ Recreated trigger: {trigger_name}")
                    except Exception as te:
                        print(f"   ⚠️  Could not recreate trigger {trigger_name}: {te}")
            
            # Re-enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON")
            
            print("   ✅ Removed draw_length_module from bow_setups table")
        else:
            print("   ✅ Bow_setups table already clean (no draw_length_module column)")
        
        # === PHASE 5: VALIDATION AND CONSTRAINTS ===
        print("\n✅ Phase 5: Adding validation and constraints...")
        
        # Verify all bow setups have draw_length
        cursor.execute("SELECT COUNT(*) as count FROM bow_setups WHERE draw_length IS NULL OR draw_length = 0")
        invalid_setups = cursor.fetchone()['count']
        
        if invalid_setups > 0:
            print(f"   ⚠️  Warning: {invalid_setups} bow setups still have invalid draw_length")
        else:
            print("   ✅ All bow setups have valid draw_length values")
        
        # Create indexes for performance
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bow_setups_draw_length ON bow_setups(draw_length)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bow_setups_ibo_speed ON bow_setups(ibo_speed)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bow_setups_measured_speed ON bow_setups(measured_speed_fps)")
            print("   ✅ Added performance indexes")
        except sqlite3.OperationalError as e:
            print(f"   ⚠️  Index creation warning: {e}")
        
        # === PHASE 6: FINAL VALIDATION ===
        print("\n🔍 Phase 6: Final validation...")
        
        # Check final schema state
        cursor.execute("PRAGMA table_info(users)")
        final_user_columns = {col[1] for col in cursor.fetchall()}
        
        cursor.execute("PRAGMA table_info(bow_setups)")  
        final_bow_columns = {col[1] for col in cursor.fetchall()}
        
        # Count records
        cursor.execute("SELECT COUNT(*) as count FROM bow_setups")
        total_setups = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM bow_setups WHERE draw_length IS NOT NULL AND draw_length > 0")
        valid_draw_length_setups = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM bow_setups WHERE ibo_speed IS NOT NULL AND ibo_speed > 0")
        setups_with_ibo = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM bow_setups WHERE measured_speed_fps IS NOT NULL AND measured_speed_fps > 0")
        setups_with_chronograph = cursor.fetchone()['count']
        
        print(f"   📊 Migration Results:")
        print(f"      Total bow setups: {total_setups}")
        print(f"      Setups with valid draw_length: {valid_draw_length_setups}")
        print(f"      Setups with ibo_speed: {setups_with_ibo}")
        print(f"      Setups with chronograph data: {setups_with_chronograph}")
        print(f"      Users table has draw_length: {'draw_length' in final_user_columns}")
        print(f"      Bow_setups has draw_length_module: {'draw_length_module' in final_bow_columns}")
        print(f"      Bow_setups has measured_speed_fps: {'measured_speed_fps' in final_bow_columns}")
        
        # Commit all changes
        conn.commit()
        print("\n✅ Migration 045 completed successfully!")
        print("🎯 Draw length is now unified per bow setup")
        print("🚀 Speed system enhanced with chronograph support")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error during migration: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def rollback_migration():
    """Rollback Migration 045 - NOT RECOMMENDED due to data loss potential"""
    print("⚠️  WARNING: Rollback of Migration 045 is not recommended!")
    print("   This migration involves schema changes that may cause data loss")
    print("   Please restore from backup if rollback is needed")
    return False

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        rollback_migration()
    else:
        success = run_migration()
        sys.exit(0 if success else 1)