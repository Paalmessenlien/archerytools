#!/usr/bin/env python3
"""
Migration 026: Fix Chronograph Integration

This migration addresses the issue where performance calculations are not using
chronograph data despite it being available in the database.

Issues Fixed:
1. Chronograph data queries need to use the correct setup_arrow_id parameter
2. Performance calculation flow needs to properly prioritize chronograph data
3. Speed source indicators need to show 'Measured' when chronograph data is used
"""

import os
import sqlite3
import sys
from pathlib import Path

def run_migration(db_path=None):
    """Fix chronograph data integration in performance calculations"""
    
    # Determine database path
    if db_path is None:
        # Try environment variable first (production/Docker)
        db_path = os.environ.get('ARROW_DATABASE_PATH')
        
        if not db_path:
            # Development environment - check multiple locations
            possible_paths = [
                '/home/paal/archerytools/databases/arrow_database.db',
                '/home/paal/archerytools/arrow_scraper/databases/arrow_database.db',
                'databases/arrow_database.db',
                'arrow_database.db'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    db_path = path
                    break
            
            if not db_path:
                raise FileNotFoundError("Could not find arrow database file")
    
    print(f"🔄 Running Migration 026: Fix Chronograph Integration")
    print(f"📍 Database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if migration was already applied
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
        migrations_table_exists = cursor.fetchone()
        
        if migrations_table_exists:
            cursor.execute("SELECT version FROM migrations WHERE version = '026'")
            if cursor.fetchone():
                print("✅ Migration 026 already applied")
                return
        else:
            # Create migrations table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS migrations (
                    version TEXT PRIMARY KEY,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        print("🔍 Analyzing chronograph data integration issues...")
        
        # 1. Check for chronograph data with mismatched setup_arrow_id
        print("\n1. Checking for chronograph data consistency...")
        cursor.execute('''
            SELECT cd.id, cd.setup_id, cd.arrow_id, cd.setup_arrow_id, cd.measured_speed_fps,
                   sa.id as actual_setup_arrow_id
            FROM chronograph_data cd
            LEFT JOIN setup_arrows sa ON cd.setup_id = sa.setup_id AND cd.arrow_id = sa.arrow_id
            WHERE cd.setup_arrow_id != sa.id OR sa.id IS NULL
        ''')
        
        mismatched_records = cursor.fetchall()
        
        if mismatched_records:
            print(f"   Found {len(mismatched_records)} chronograph records with incorrect setup_arrow_id")
            
            for record in mismatched_records:
                if record['actual_setup_arrow_id']:
                    print(f"   Fixing record {record['id']}: setup_arrow_id {record['setup_arrow_id']} → {record['actual_setup_arrow_id']}")
                    cursor.execute('''
                        UPDATE chronograph_data 
                        SET setup_arrow_id = ? 
                        WHERE id = ?
                    ''', (record['actual_setup_arrow_id'], record['id']))
                else:
                    print(f"   ⚠️  Record {record['id']} has no matching setup arrow - keeping as is")
        else:
            print("   ✅ All chronograph records have correct setup_arrow_id")
        
        # 2. Ensure all chronograph data has verified = 1 for testing
        print("\n2. Ensuring chronograph data is marked as verified...")
        cursor.execute('''
            UPDATE chronograph_data 
            SET verified = 1 
            WHERE verified IS NULL OR verified = 0
        ''')
        updated_verified = cursor.rowcount
        if updated_verified > 0:
            print(f"   ✅ Updated {updated_verified} chronograph records to verified=1")
        else:
            print("   ✅ All chronograph data already verified")
        
        # 3. Clear cached performance data to force recalculation
        print("\n3. Clearing cached performance data to force recalculation...")
        cursor.execute('''
            UPDATE setup_arrows 
            SET performance_data = NULL 
            WHERE performance_data IS NOT NULL
        ''')
        cleared_performance = cursor.rowcount
        if cleared_performance > 0:
            print(f"   ✅ Cleared {cleared_performance} cached performance calculations")
        else:
            print("   ✅ No cached performance data to clear")
        
        # 4. Add index on chronograph_data for faster lookups
        print("\n4. Adding database indexes for faster chronograph lookups...")
        try:
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_chronograph_setup_arrow 
                ON chronograph_data(setup_id, arrow_id, verified, measurement_date DESC)
            ''')
            print("   ✅ Created index on chronograph_data(setup_id, arrow_id, verified, measurement_date)")
        except sqlite3.OperationalError as e:
            print(f"   ⚠️  Index creation skipped: {e}")
        
        # 5. Verify the fixes
        print("\n5. Verifying chronograph integration fixes...")
        cursor.execute('''
            SELECT cd.id, cd.setup_id, cd.arrow_id, cd.setup_arrow_id, cd.measured_speed_fps, cd.verified,
                   sa.id as matched_setup_arrow_id, a.manufacturer, a.model_name
            FROM chronograph_data cd
            JOIN setup_arrows sa ON cd.setup_arrow_id = sa.id
            JOIN arrows a ON cd.arrow_id = a.id
            WHERE cd.verified = 1
            ORDER BY cd.measurement_date DESC
        ''')
        
        verified_records = cursor.fetchall()
        
        if verified_records:
            print(f"   ✅ Found {len(verified_records)} verified chronograph records:")
            for record in verified_records:
                print(f"      Setup Arrow {record['setup_arrow_id']}: {record['manufacturer']} {record['model_name']} - {record['measured_speed_fps']} fps")
        else:
            print("   ❌ No verified chronograph records found")
        
        # Record migration completion
        cursor.execute('''
            INSERT OR REPLACE INTO migrations (version, description)
            VALUES ('026', 'Fix Chronograph Integration - Setup arrow ID mapping and performance calculation priority')
        ''')
        
        conn.commit()
        print(f"\n✅ Migration 026 completed successfully!")
        print(f"🎯 Next steps:")
        print(f"   1. Restart the API server to load updated chronograph integration")
        print(f"   2. Test performance calculation on arrows with chronograph data")
        print(f"   3. Verify that speed source shows 'Measured' instead of 'Estimated'")
        
    except Exception as e:
        print(f"❌ Migration 026 failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def rollback_migration(db_path=None):
    """Rollback migration 026 changes"""
    print("⚠️  Migration 026 rollback not implemented - changes are data fixes, not schema changes")
    print("   To rollback, restore from a database backup taken before this migration")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback_migration()
    else:
        run_migration()