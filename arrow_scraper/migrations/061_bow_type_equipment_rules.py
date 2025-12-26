#!/usr/bin/env python3
"""
Migration 061: Bow Type Equipment Rules

Creates the bow_type_equipment_rules table for admin-configurable equipment
filtering based on bow type. This allows admins to specify which equipment
categories are available for each bow type (compound, recurve, barebow,
longbow, traditional).
"""

import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 61,
        'description': 'Create bow_type_equipment_rules table for equipment filtering by bow type',
        'author': 'System',
        'created_at': '2025-11-29',
        'target_database': 'arrow',
        'dependencies': ['060'],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Create bow_type_equipment_rules table with sensible defaults"""
    conn = cursor.connection

    print("Creating bow_type_equipment_rules table...")

    # Create bow_type_equipment_rules table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bow_type_equipment_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bow_type TEXT NOT NULL,
            equipment_category TEXT NOT NULL,
            is_allowed BOOLEAN DEFAULT 1,
            is_common BOOLEAN DEFAULT 0,
            notes TEXT,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(bow_type, equipment_category),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    # Create indexes for better performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bow_type_equipment_rules_bow_type
        ON bow_type_equipment_rules(bow_type)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bow_type_equipment_rules_category
        ON bow_type_equipment_rules(equipment_category)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bow_type_equipment_rules_allowed
        ON bow_type_equipment_rules(bow_type, is_allowed)
    """)

    print("✅ Created bow_type_equipment_rules table with indexes")

    # Insert default rules based on real archery equipment standards
    # Equipment categories: String, Sight, Scope, Stabilizer, Arrow Rest, Plunger, Weight, Other

    default_rules = [
        # Compound - all equipment except plunger (uses cable/rest system instead)
        ('compound', 'String', True, True, 'Essential for all bows'),
        ('compound', 'Sight', True, True, 'Standard competition equipment'),
        ('compound', 'Scope', True, True, 'Magnified aiming for target archery'),
        ('compound', 'Stabilizer', True, True, 'Standard for balance and vibration'),
        ('compound', 'Arrow Rest', True, True, 'Drop-away or blade rest common'),
        ('compound', 'Plunger', False, False, 'Not used - compound uses cable-driven rest'),
        ('compound', 'Weight', True, True, 'Stabilizer weights for balance'),
        ('compound', 'Other', True, False, 'Miscellaneous accessories'),

        # Recurve (Olympic) - all except scope
        ('recurve', 'String', True, True, 'Essential for all bows'),
        ('recurve', 'Sight', True, True, 'Standard Olympic recurve equipment'),
        ('recurve', 'Scope', False, False, 'Not allowed in Olympic recurve'),
        ('recurve', 'Stabilizer', True, True, 'Long rod and side rods'),
        ('recurve', 'Arrow Rest', True, True, 'Blade or magnetic rest'),
        ('recurve', 'Plunger', True, True, 'Essential for recurve tuning'),
        ('recurve', 'Weight', True, True, 'Stabilizer and riser weights'),
        ('recurve', 'Other', True, False, 'Clicker, finger tab, etc.'),

        # Barebow - no sights, scopes, or stabilizers per competition rules
        ('barebow', 'String', True, True, 'Essential for all bows'),
        ('barebow', 'Sight', False, False, 'Not allowed in barebow competition'),
        ('barebow', 'Scope', False, False, 'Not allowed in barebow competition'),
        ('barebow', 'Stabilizer', False, False, 'Not allowed in barebow competition'),
        ('barebow', 'Arrow Rest', True, True, 'Simple rest or shelf'),
        ('barebow', 'Plunger', True, True, 'Allowed for tuning'),
        ('barebow', 'Weight', True, True, 'Riser weights allowed for balance'),
        ('barebow', 'Other', True, False, 'Finger tab, string walking aids'),

        # Longbow - minimal equipment, traditional style
        ('longbow', 'String', True, True, 'Essential for all bows'),
        ('longbow', 'Sight', False, False, 'Not used on traditional longbows'),
        ('longbow', 'Scope', False, False, 'Not used on traditional longbows'),
        ('longbow', 'Stabilizer', False, False, 'Not used on traditional longbows'),
        ('longbow', 'Arrow Rest', True, False, 'Optional - many shoot off hand'),
        ('longbow', 'Plunger', False, False, 'Not typically used'),
        ('longbow', 'Weight', False, False, 'Not used on traditional longbows'),
        ('longbow', 'Other', True, False, 'Arm guard, finger tab/glove'),

        # Traditional (general traditional recurve) - basic equipment only
        ('traditional', 'String', True, True, 'Essential for all bows'),
        ('traditional', 'Sight', False, False, 'Not typically used in traditional'),
        ('traditional', 'Scope', False, False, 'Not used in traditional'),
        ('traditional', 'Stabilizer', False, False, 'Not typically used in traditional'),
        ('traditional', 'Arrow Rest', True, True, 'Simple rest or shelf'),
        ('traditional', 'Plunger', True, False, 'Optional for tuning'),
        ('traditional', 'Weight', False, False, 'Not typically used'),
        ('traditional', 'Other', True, False, 'Arm guard, finger tab/glove'),
    ]

    print("Inserting default equipment rules...")

    for bow_type, category, is_allowed, is_common, notes in default_rules:
        cursor.execute("""
            INSERT INTO bow_type_equipment_rules
            (bow_type, equipment_category, is_allowed, is_common, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (bow_type, category, is_allowed, is_common, notes))

    conn.commit()
    print(f"✅ Inserted {len(default_rules)} default equipment rules for 5 bow types")

def migrate_down(cursor):
    """Rollback migration 061: Remove bow_type_equipment_rules table"""
    conn = cursor.connection

    print("Dropping bow_type_equipment_rules table...")

    # Drop indexes first
    cursor.execute("DROP INDEX IF EXISTS idx_bow_type_equipment_rules_allowed")
    cursor.execute("DROP INDEX IF EXISTS idx_bow_type_equipment_rules_category")
    cursor.execute("DROP INDEX IF EXISTS idx_bow_type_equipment_rules_bow_type")

    # Drop table
    cursor.execute("DROP TABLE IF EXISTS bow_type_equipment_rules")

    conn.commit()
    print("✅ Removed bow_type_equipment_rules table and indexes")
