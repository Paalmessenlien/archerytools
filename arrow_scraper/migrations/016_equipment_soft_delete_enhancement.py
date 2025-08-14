#!/usr/bin/env python3
"""
Migration 016: Equipment Soft Delete Enhancement

Enhances the existing soft delete system for equipment with:
- Deleted timestamp tracking
- User tracking for who deleted the equipment
- Improved change logging integration
- Restore functionality support
"""

import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the arrow_scraper directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_database_path():
    """Get the correct database path using the same logic as UserDatabase"""
    # Check for environment variable first (Docker deployment)
    env_db_path = os.environ.get('USER_DATABASE_PATH')
    if env_db_path:
        return env_db_path
    
    # Unified database paths - same as UserDatabase class
    possible_paths = [
        Path("/app/databases/user_data.db"),  # Docker path (highest priority)
        Path(__file__).parent.parent / "databases" / "user_data.db",  # Local development
        Path(__file__).parent.parent / "user_data.db",  # Legacy local path
    ]
    
    for p in possible_paths:
        if p.exists():
            return str(p)
    
    # Default to first option for new installations
    return str(possible_paths[0])

def up(db_path: str = None) -> bool:
    """Add soft delete enhancement fields to bow_equipment table"""
    if db_path is None:
        db_path = get_database_path()
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("🔄 Running Migration 016: Equipment Soft Delete Enhancement")
        print(f"📁 Database path: {db_path}")
        
        # Check if fields already exist
        cursor.execute("PRAGMA table_info(bow_equipment)")
        columns = [col[1] for col in cursor.fetchall()]
        
        fields_to_add = []
        if 'deleted_at' not in columns:
            fields_to_add.append(('deleted_at', 'TIMESTAMP'))
        if 'deleted_by' not in columns:
            fields_to_add.append(('deleted_by', 'INTEGER'))
        
        if not fields_to_add:
            print("⚠️  Migration 016 already applied - fields exist")
            return True
        
        print("🔧 Adding soft delete enhancement fields...")
        
        # Add new fields
        for field_name, field_type in fields_to_add:
            cursor.execute(f'''
                ALTER TABLE bow_equipment 
                ADD COLUMN {field_name} {field_type}
            ''')
            print(f"✅ Added {field_name} field")
        
        # Add foreign key constraint comment for deleted_by
        # (SQLite doesn't support adding FK constraints to existing tables easily)
        print("ℹ️  Note: deleted_by references users(id) - enforced at application level")
        
        # Create index for better performance on deleted equipment queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bow_equipment_deleted 
            ON bow_equipment (is_active, deleted_at DESC)
        ''')
        print("✅ Created performance index for deleted equipment")
        
        # Update existing deleted equipment to have deletion timestamp
        cursor.execute('''
            UPDATE bow_equipment 
            SET deleted_at = CURRENT_TIMESTAMP 
            WHERE is_active = 0 AND deleted_at IS NULL
        ''')
        updated_records = cursor.rowcount
        if updated_records > 0:
            print(f"📊 Updated {updated_records} existing deleted equipment records with timestamps")
        
        conn.commit()
        print("🎉 Migration 016 completed successfully!")
        print("📊 Equipment soft delete system enhanced with:")
        print("   • Deletion timestamp tracking (deleted_at)")
        print("   • User tracking for deletions (deleted_by)")
        print("   • Performance index for deleted equipment queries")
        print("   • Existing deleted equipment updated with timestamps")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Migration 016 failed: {e}")
        conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def down(db_path: str = None) -> bool:
    """Remove soft delete enhancement fields (not recommended)"""
    if db_path is None:
        db_path = get_database_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Reverting Migration 016: Equipment Soft Delete Enhancement")
        print("⚠️  Warning: This will remove deletion tracking data")
        
        # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
        # This is complex and risky, so we'll just warn for now
        print("❌ Reverting this migration requires table recreation")
        print("   Manual intervention required if rollback is necessary")
        
        return False
        
    except sqlite3.Error as e:
        print(f"❌ Migration 016 rollback failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

def run_migration():
    """Execute the migration"""
    return up()

if __name__ == "__main__":
    run_migration()