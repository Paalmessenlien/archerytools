#!/usr/bin/env python3
"""
Migration 060: Create custom_spine_charts table

Creates the missing custom_spine_charts table that is referenced in the API
but was never created in the database schema.
"""

import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 60,
        'description': 'Create custom_spine_charts table for admin spine chart management',
        'author': 'System',
        'created_at': '2025-09-09',
        'target_database': 'arrow',
        'dependencies': [],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Create custom_spine_charts table for admin spine chart management"""
    conn = cursor.connection
    
    print("Creating custom_spine_charts table...")
    
    # Create custom_spine_charts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_spine_charts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_name TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            model TEXT NOT NULL,
            bow_type TEXT NOT NULL,
            grid_definition TEXT,
            spine_grid TEXT,
            spine_system TEXT,
            chart_notes TEXT,
            created_by INTEGER NOT NULL,
            overrides_manufacturer_chart INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            is_system_default INTEGER DEFAULT 0,
            calculation_priority INTEGER DEFAULT 100,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_custom_spine_charts_manufacturer 
        ON custom_spine_charts(manufacturer)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_custom_spine_charts_bow_type 
        ON custom_spine_charts(bow_type)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_custom_spine_charts_created_by 
        ON custom_spine_charts(created_by)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_custom_spine_charts_active 
        ON custom_spine_charts(is_active)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_custom_spine_charts_system_default 
        ON custom_spine_charts(is_system_default, calculation_priority)
    """)
    
    conn.commit()
    print("✅ Created custom_spine_charts table with indexes")

def migrate_down(cursor):
    """Rollback migration 060: Remove custom_spine_charts table"""
    conn = cursor.connection
    
    print("Dropping custom_spine_charts table...")
    
    # Drop indexes first
    cursor.execute("DROP INDEX IF EXISTS idx_custom_spine_charts_system_default")
    cursor.execute("DROP INDEX IF EXISTS idx_custom_spine_charts_active")
    cursor.execute("DROP INDEX IF EXISTS idx_custom_spine_charts_created_by")
    cursor.execute("DROP INDEX IF EXISTS idx_custom_spine_charts_bow_type")
    cursor.execute("DROP INDEX IF EXISTS idx_custom_spine_charts_manufacturer")
    
    # Drop table
    cursor.execute("DROP TABLE IF EXISTS custom_spine_charts")
    
    conn.commit()
    print("✅ Removed custom_spine_charts table and indexes")