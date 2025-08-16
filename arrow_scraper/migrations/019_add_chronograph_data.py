#!/usr/bin/env python3
"""
Migration 019: Add chronograph data table for storing measured arrow speeds
Created: 2025-08-15
"""

import sqlite3
import sys
import os
from pathlib import Path

def migrate_up(cursor):
    """Apply the migration - create chronograph_data table"""
    
    # Create chronograph_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chronograph_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setup_id INTEGER NOT NULL,
            arrow_id INTEGER,
            setup_arrow_id INTEGER,
            measured_speed_fps REAL NOT NULL,
            arrow_weight_grains REAL NOT NULL,
            temperature_f INTEGER,
            humidity_percent INTEGER,
            measurement_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            chronograph_model TEXT,
            shot_count INTEGER DEFAULT 1,
            std_deviation REAL,
            min_speed_fps REAL,
            max_speed_fps REAL,
            verified BOOLEAN DEFAULT 0,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (setup_id) REFERENCES bow_setups(id) ON DELETE CASCADE,
            FOREIGN KEY (arrow_id) REFERENCES arrows(id) ON DELETE SET NULL,
            FOREIGN KEY (setup_arrow_id) REFERENCES setup_arrows(id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chronograph_setup_id ON chronograph_data(setup_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chronograph_arrow_id ON chronograph_data(arrow_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chronograph_setup_arrow_id ON chronograph_data(setup_arrow_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chronograph_verified ON chronograph_data(verified)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chronograph_date ON chronograph_data(measurement_date)')
    
    print("✅ Created chronograph_data table with indexes")

def migrate_down(cursor):
    """Rollback the migration - remove chronograph_data table"""
    cursor.execute('DROP TABLE IF EXISTS chronograph_data')
    print("✅ Removed chronograph_data table")

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 19,
        'description': 'Add chronograph data table for storing measured arrow speeds',
        'dependencies': []  # No dependencies on other migrations
    }

def main():
    """Main function for standalone execution"""
    if len(sys.argv) < 2:
        print("Usage: python 019_add_chronograph_data.py <database_path> [--rollback]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    rollback = '--rollback' in sys.argv
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        sys.exit(1)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if rollback:
            print("🔄 Rolling back migration 019...")
            migrate_down(cursor)
        else:
            print("🚀 Applying migration 019...")
            migrate_up(cursor)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        action = "rolled back" if rollback else "applied"
        print(f"✅ Migration 019 {action} successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()