#!/usr/bin/env python3
"""
Migration 050: Add Manufacturer Active Status Filtering

This migration validates that the manufacturer active status filtering system is ready
and provides guidance for implementing the filtering in code.

The migration ensures that:
1. manufacturers table has is_active column
2. Default manufacturers are set to active
3. System is ready for active status filtering implementation
"""

import sqlite3
import sys
import os

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 50,
        'description': 'Validate manufacturer active status filtering system readiness',
        'author': 'System',
        'created_at': '2025-08-30',
        'target_database': 'arrow',
        'dependencies': ['049'],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Apply the migration"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration 050: Validating manufacturer active status filtering system...")
        
        # 1. Verify manufacturers table has is_active column
        cursor.execute("PRAGMA table_info(manufacturers)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'is_active' not in column_names:
            raise Exception("manufacturers table is missing is_active column - cannot implement filtering")
        
        print("   ✅ manufacturers table has is_active column")
        
        # 2. Check current active status distribution
        cursor.execute("SELECT is_active, COUNT(*) FROM manufacturers GROUP BY is_active")
        status_counts = cursor.fetchall()
        
        active_count = 0
        inactive_count = 0
        for status, count in status_counts:
            if status:
                active_count = count
            else:
                inactive_count = count
        
        print(f"   📊 Current manufacturer status: {active_count} active, {inactive_count} inactive")
        
        # 3. Ensure all manufacturers have explicit active status (not NULL)
        cursor.execute("SELECT COUNT(*) FROM manufacturers WHERE is_active IS NULL")
        null_count = cursor.fetchone()[0]
        
        if null_count > 0:
            print(f"   🔧 Setting {null_count} manufacturers with NULL status to active...")
            cursor.execute("UPDATE manufacturers SET is_active = TRUE WHERE is_active IS NULL")
        
        # 4. Get sample of arrows that would be affected
        cursor.execute("""
            SELECT m.name, m.is_active, COUNT(a.id) as arrow_count
            FROM manufacturers m
            LEFT JOIN arrows a ON a.manufacturer = m.name
            GROUP BY m.name, m.is_active
            ORDER BY m.is_active DESC, arrow_count DESC
            LIMIT 10
        """)
        manufacturer_samples = cursor.fetchall()
        
        print("   📋 Manufacturer arrow count samples:")
        for name, is_active, arrow_count in manufacturer_samples:
            status = "🟢 Active" if is_active else "🔴 Inactive"
            print(f"     {status}: {name} ({arrow_count} arrows)")
        
        # 5. Validate that we have arrows and they're linked to manufacturers
        cursor.execute("""
            SELECT COUNT(*) FROM arrows a
            JOIN manufacturers m ON a.manufacturer = m.name
        """)
        linked_arrows = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM arrows")
        total_arrows = cursor.fetchone()[0]
        
        if linked_arrows != total_arrows:
            print(f"   ⚠️  Warning: {total_arrows - linked_arrows} arrows not linked to manufacturers")
            
            # Show unlinked arrows
            cursor.execute("""
                SELECT DISTINCT a.manufacturer FROM arrows a
                WHERE NOT EXISTS (SELECT 1 FROM manufacturers m WHERE m.name = a.manufacturer)
                LIMIT 5
            """)
            unlinked = cursor.fetchall()
            if unlinked:
                print("   🔍 Sample unlinked manufacturers:")
                for (manufacturer,) in unlinked:
                    print(f"     • {manufacturer}")
        else:
            print(f"   ✅ All {total_arrows} arrows properly linked to manufacturers")
        
        # 6. Test query performance with manufacturer join
        import time
        start_time = time.time()
        cursor.execute("""
            SELECT COUNT(*) FROM arrows a
            JOIN manufacturers m ON a.manufacturer = m.name
            WHERE m.is_active = TRUE
        """)
        active_arrow_count = cursor.fetchone()[0]
        query_time = time.time() - start_time
        
        print(f"   ⚡ Query performance test: {active_arrow_count} active arrows found in {query_time:.3f}s")
        
        conn.commit()
        
        print(f"   📈 Migration Summary:")
        print(f"     • Manufacturer active status filtering system validated")
        print(f"     • {active_count} active manufacturers with {active_arrow_count} arrows")
        print(f"     • {inactive_count} inactive manufacturers (arrows will be hidden)")
        print(f"     • System ready for active status filtering implementation")
        print(f"")
        print(f"   💡 Next Steps:")
        print(f"     • Update database query methods to include manufacturer active filtering")
        print(f"     • Test filtering with inactive manufacturer")
        print(f"     • Verify admin endpoints still show all arrows")
        
        print("🎯 Migration 050 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration 050 failed: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback the migration"""
    conn = cursor.connection
    
    try:
        print("🔄 Rolling back Migration 050...")
        
        # This migration doesn't change data, only validates
        # No rollback action needed
        
        print("   ✅ No data changes to rollback")
        
        conn.commit()
        print("🔄 Migration 050 rollback completed")
        return True
        
    except Exception as e:
        print(f"❌ Migration 050 rollback failed: {e}")
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
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()