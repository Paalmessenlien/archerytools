#!/usr/bin/env python3
"""
Migration 003: Bow Equipment Management Schema
Creates tables for managing bow equipment (strings, sights, stabilizers, arrow rests, weights)
"""

import sqlite3
import json
from datetime import datetime
from database_migration_manager import BaseMigration

class Migration004BowEquipmentSchema(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "004"
        self.description = "Create bow equipment management schema"
        self.dependencies = ["003"]
        self.environments = ['all']
    
    def up(self, db_path: str, environment: str) -> bool:
        """Create equipment management tables"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Equipment Categories table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                icon TEXT,  -- Font Awesome icon class
                specifications_schema TEXT,  -- JSON schema for this category
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Equipment table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                manufacturer TEXT NOT NULL,
                model_name TEXT NOT NULL,
                specifications TEXT,  -- JSON field for category-specific specs
                compatibility_rules TEXT,  -- JSON field for compatibility logic
                weight_grams REAL,  -- Equipment weight in grams
                price_range TEXT,
                image_url TEXT,
                local_image_path TEXT,
                description TEXT,
                source_url TEXT,
                scraped_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES equipment_categories (id),
                UNIQUE(manufacturer, model_name, category_id)
            )
            ''')
            
            # Bow Equipment (junction table linking bow setups to equipment)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS bow_equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bow_setup_id INTEGER NOT NULL,
                equipment_id INTEGER NOT NULL,
                installation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                installation_notes TEXT,
                custom_specifications TEXT,  -- JSON for user-customized specs
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                FOREIGN KEY (equipment_id) REFERENCES equipment (id),
                UNIQUE(bow_setup_id, equipment_id)
            )
            ''')
            
            # Insert default equipment categories
            categories = [
                {
                    'name': 'String',
                    'description': 'Bowstrings and cables for compound and traditional bows',
                    'icon': 'fas fa-link',
                    'schema': {
                        'properties': {
                            'material': {'type': 'string', 'enum': ['BCY-X', 'D97', '452X', '8125G', 'Dacron', 'FastFlight']},
                            'strand_count': {'type': 'integer', 'minimum': 12, 'maximum': 24},
                            'length_inches': {'type': 'number', 'minimum': 40, 'maximum': 120},
                            'serving_material': {'type': 'string'},
                            'loop_type': {'type': 'string', 'enum': ['flemish', 'endless', 'loop']},
                            'bow_weight_range': {'type': 'string'}
                        }
                    }
                },
                {
                    'name': 'Sight',
                    'description': 'Bow sights for aiming and accuracy',
                    'icon': 'fas fa-crosshairs',
                    'schema': {
                        'properties': {
                            'sight_type': {'type': 'string', 'enum': ['multi-pin', 'single-pin', 'scope', 'instinctive']},
                            'pin_count': {'type': 'integer', 'minimum': 1, 'maximum': 7},
                            'adjustment_type': {'type': 'string', 'enum': ['micro', 'standard', 'toolless']},
                            'mounting_type': {'type': 'string', 'enum': ['dovetail', 'weaver', 'proprietary']},
                            'light_options': {'type': 'array', 'items': {'type': 'string'}},
                            'max_range_yards': {'type': 'integer'}
                        }
                    }
                },
                {
                    'name': 'Stabilizer',
                    'description': 'Stabilizers and weights for bow balance and vibration dampening',
                    'icon': 'fas fa-balance-scale',
                    'schema': {
                        'properties': {
                            'stabilizer_type': {'type': 'string', 'enum': ['front', 'side', 'back', 'v-bar', 'offset']},
                            'length_inches': {'type': 'number', 'minimum': 4, 'maximum': 36},
                            'weight_ounces': {'type': 'number', 'minimum': 1, 'maximum': 32},
                            'thread_size': {'type': 'string', 'enum': ['5/16-24', '1/4-20', '8-32']},
                            'material': {'type': 'string', 'enum': ['carbon', 'aluminum', 'steel']},
                            'dampening_type': {'type': 'string', 'enum': ['rubber', 'foam', 'gel', 'none']}
                        }
                    }
                },
                {
                    'name': 'Arrow Rest',
                    'description': 'Arrow rests and launchers for arrow support and guidance',
                    'icon': 'fas fa-hand-paper',
                    'schema': {
                        'properties': {
                            'rest_type': {'type': 'string', 'enum': ['drop-away', 'blade', 'launcher', 'shelf', 'whisker-biscuit']},
                            'activation_type': {'type': 'string', 'enum': ['cable-driven', 'limb-driven', 'magnetic', 'manual']},
                            'adjustment_features': {'type': 'array', 'items': {'type': 'string'}},
                            'arrow_containment': {'type': 'string', 'enum': ['full', 'partial', 'none']},
                            'mounting_type': {'type': 'string', 'enum': ['berger-hole', 'plunger', 'adhesive']},
                            'arrow_diameter_range': {'type': 'string'}
                        }
                    }
                },
                {
                    'name': 'Weight',
                    'description': 'Additional weights for bow tuning and balance',
                    'icon': 'fas fa-weight-hanging',
                    'schema': {
                        'properties': {
                            'weight_ounces': {'type': 'number', 'minimum': 0.5, 'maximum': 16},
                            'mounting_location': {'type': 'string', 'enum': ['stabilizer', 'riser', 'limb', 'string']},
                            'weight_type': {'type': 'string', 'enum': ['stainless-steel', 'tungsten', 'brass', 'lead']},
                            'thread_size': {'type': 'string', 'enum': ['5/16-24', '1/4-20', '8-32']},
                            'shape': {'type': 'string', 'enum': ['cylinder', 'donut', 'disc', 'custom']},
                            'purpose': {'type': 'string', 'enum': ['balance', 'dampening', 'tuning', 'momentum']}
                        }
                    }
                }
            ]
            
            for category in categories:
                cursor.execute('''
                    INSERT OR IGNORE INTO equipment_categories (name, description, icon, specifications_schema)
                    VALUES (?, ?, ?, ?)
                ''', (
                    category['name'],
                    category['description'],
                    category['icon'],
                    json.dumps(category['schema'])
                ))
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully created bow equipment management schema")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create equipment schema: {e}")
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Remove equipment management tables"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Drop tables in reverse order due to foreign key constraints
            cursor.execute('DROP TABLE IF EXISTS bow_equipment')
            cursor.execute('DROP TABLE IF EXISTS equipment')
            cursor.execute('DROP TABLE IF EXISTS equipment_categories')
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully removed bow equipment management schema")
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove equipment schema: {e}")
            return False

# Create the migration instance for discovery
migration = Migration004BowEquipmentSchema()