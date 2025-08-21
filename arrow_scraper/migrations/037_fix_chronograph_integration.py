#!/usr/bin/env python3
"""
Migration 037: Fix Chronograph Integration
Fix: Setup arrow ID mapping and performance calculation priority

This migration ensures chronograph data has correct setup_arrow_id mappings
and performance calculations prioritize measured speeds correctly.
"""

import sqlite3
import sys
import os

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 37,
        'description': 'Fix Chronograph Integration - Setup arrow ID mapping and performance calculation priority',
        'author': 'System',
        'created_at': '2025-08-21',
        'target_database': 'arrow',
        'dependencies': [],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Apply the migration"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration 037: Fixing chronograph integration...")
        
        # Check if chronograph_data table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chronograph_data'")
        chronograph_table_exists = cursor.fetchone() is not None
        
        if not chronograph_table_exists:
            print("   ⚠️  chronograph_data table does not exist, skipping chronograph-specific fixes")
            print("   ✅ Migration completed (no chronograph data to fix)")
            return True
        
        # 1. Check for chronograph data with mismatched setup_arrow_id
        print("   1. Checking for chronograph data consistency...")
        cursor.execute('''
            SELECT cd.id, cd.setup_id, cd.arrow_id, cd.setup_arrow_id, cd.measured_speed_fps,
                   sa.id as actual_setup_arrow_id
            FROM chronograph_data cd
            LEFT JOIN setup_arrows sa ON cd.setup_id = sa.setup_id AND cd.arrow_id = sa.arrow_id
            WHERE cd.setup_arrow_id != sa.id OR sa.id IS NULL
        ''')
        
        mismatched_records = cursor.fetchall()
        
        if mismatched_records:
            print(f"      Found {len(mismatched_records)} chronograph records with incorrect setup_arrow_id")
            
            for record in mismatched_records:
                if record[5]:  # actual_setup_arrow_id
                    print(f"      Fixing record {record[0]}: setup_arrow_id {record[3]} → {record[5]}")
                    cursor.execute('''
                        UPDATE chronograph_data 
                        SET setup_arrow_id = ? 
                        WHERE id = ?
                    ''', (record[5], record[0]))
                else:
                    print(f"      ⚠️  Record {record[0]} has no matching setup arrow - keeping as is")
        else:
            print("      ✅ All chronograph records have correct setup_arrow_id")
        
        # 2. Ensure all chronograph data has verified = 1
        print("   2. Ensuring chronograph data is marked as verified...")
        cursor.execute('''
            UPDATE chronograph_data 
            SET verified = 1 
            WHERE verified IS NULL OR verified = 0
        ''')
        updated_verified = cursor.rowcount
        if updated_verified > 0:
            print(f"      ✅ Updated {updated_verified} chronograph records to verified=1")
        else:
            print("      ✅ All chronograph data already verified")
        
        # 3. Clear cached performance data to force recalculation
        print("   3. Clearing cached performance data to force recalculation...")
        cursor.execute('''
            UPDATE setup_arrows 
            SET performance_data = NULL 
            WHERE performance_data IS NOT NULL
        ''')
        cleared_performance = cursor.rowcount
        if cleared_performance > 0:
            print(f"      ✅ Cleared {cleared_performance} cached performance calculations")
        else:
            print("      ✅ No cached performance data to clear")
        
        # 4. Add index on chronograph_data for faster lookups
        print("   4. Adding database indexes for faster chronograph lookups...")
        try:
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_chronograph_setup_arrow 
                ON chronograph_data(setup_id, arrow_id, verified, measurement_date DESC)
            ''')
            print("      ✅ Created index on chronograph_data")
        except sqlite3.OperationalError as e:
            print(f"      ⚠️  Index creation skipped: {e}")
        
        conn.commit()
        print("🎯 Migration 037 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration 037 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback the migration"""
    conn = cursor.connection
    
    try:
        print("🔄 Rolling back Migration 037...")
        
        # Remove the index we created
        cursor.execute('DROP INDEX IF EXISTS idx_chronograph_setup_arrow')
        print("   ✅ Removed chronograph index")
        
        conn.commit()
        print("🔄 Migration 037 rollback completed")
        return True
        
    except Exception as e:
        print(f"❌ Migration 037 rollback failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Test the migration - try multiple database paths
    possible_paths = [
        '/app/databases/arrow_database.db',  # Docker production
        '/root/archerytools/databases/arrow_database.db',  # Production host
        os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db'),  # Development
        'databases/arrow_database.db',  # Relative path
        'arrow_database.db'  # Current directory
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print(f"❌ Database not found in any location: {possible_paths}")
        sys.exit(1)
    
    print(f"📁 Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'down':
            success = migrate_down(conn.cursor())
        else:
            success = migrate_up(conn.cursor())
        
        if success:
            print("✅ Migration test completed successfully")
        else:
            print("❌ Migration test failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration test error: {e}")
        sys.exit(1)
    finally:
        conn.close()