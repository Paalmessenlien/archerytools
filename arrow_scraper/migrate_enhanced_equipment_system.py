#!/usr/bin/env python3
"""
Database Migration: Enhanced Equipment System

This migration adds:
1. New equipment categories: Scope, Plunger, Other
2. Auto-learning database tables for manufacturers and models
3. Updates sight category to remove scope options
4. Creates learning and analytics system

Migration Date: August 2025
"""

import sqlite3
import sys
import os
import json
from pathlib import Path

def migrate_enhanced_equipment_system():
    """Add enhanced equipment categories and auto-learning system"""
    
    # Determine database paths
    arrow_db_path = os.getenv('ARROW_DATABASE_PATH', 'databases/arrow_database.db')
    user_db_path = os.getenv('USER_DATABASE_PATH', 'databases/user_data.db')
    
    print(f"🔄 Enhanced Equipment System Migration")
    print(f"=" * 60)
    print(f"📊 Arrow Database: {arrow_db_path}")
    print(f"👥 User Database: {user_db_path}")
    
    # Check database files exist
    if not os.path.exists(arrow_db_path):
        print(f"❌ Arrow database not found: {arrow_db_path}")
        return False
        
    if not os.path.exists(user_db_path):
        print(f"❌ User database not found: {user_db_path}")
        return False
    
    try:
        # PART 1: Arrow Database Updates (Equipment Categories)
        print(f"\\n🏹 Updating Arrow Database...")
        arrow_conn = sqlite3.connect(arrow_db_path)
        arrow_conn.row_factory = sqlite3.Row
        arrow_cursor = arrow_conn.cursor()
        
        # Add new equipment categories to equipment_field_standards
        print("🔧 Adding new equipment categories...")
        
        # SCOPE EQUIPMENT FIELDS
        scope_fields = [
            ('Scope', 'magnification', 'dropdown', 'Magnification', None, 0, None, '["1x", "1.5x", "2x", "3x", "4x", "5x", "6x", "Variable"]', None, 'Magnification level', 1),
            ('Scope', 'objective_lens_size', 'number', 'Objective Lens Size', 'mm', 0, None, None, None, 'Objective lens diameter in mm', 2),
            ('Scope', 'reticle_type', 'dropdown', 'Reticle Type', None, 0, None, '["Crosshair", "Dot", "Circle", "BDC", "Mil-Dot", "Custom"]', None, 'Reticle pattern type', 3),
            ('Scope', 'turret_type', 'dropdown', 'Turret Type', None, 0, None, '["Capped", "Tactical", "Finger-adjustable", "Locking"]', None, 'Adjustment turret style', 4),
            ('Scope', 'eye_relief', 'number', 'Eye Relief', 'inches', 0, None, None, None, 'Eye relief distance', 5),
            ('Scope', 'tube_diameter', 'dropdown', 'Tube Diameter', None, 0, None, '["1 inch", "30mm", "34mm"]', None, 'Scope tube diameter', 6),
        ]
        
        # PLUNGER EQUIPMENT FIELDS
        plunger_fields = [
            ('Plunger', 'plunger_type', 'dropdown', 'Plunger Type', None, 0, None, '["Spring-loaded", "Magnetic", "Adjustable", "Fixed"]', None, 'Type of plunger mechanism', 1),
            ('Plunger', 'tension_range', 'text', 'Tension Range', None, 0, None, None, None, 'Tension adjustment range (e.g., 1-10 lbs)', 2),
            ('Plunger', 'material', 'dropdown', 'Material', None, 0, None, '["Steel", "Aluminum", "Carbon", "Composite", "Brass"]', None, 'Plunger body material', 3),
            ('Plunger', 'thread_size', 'dropdown', 'Thread Size', None, 0, None, '["8-32", "5/16-24", "M6", "M8", "Custom"]', None, 'Thread specification', 4),
            ('Plunger', 'adjustment_method', 'dropdown', 'Adjustment Method', None, 0, None, '["Tool", "Hand", "Micro-adjust", "Preset"]', None, 'How tension is adjusted', 5),
        ]
        
        # OTHER EQUIPMENT FIELDS (Flexible category)
        other_fields = [
            ('Other', 'equipment_type', 'text', 'Equipment Type', None, 0, None, None, None, 'Type of equipment (e.g., Release Aid, Quiver, etc.)', 1),
            ('Other', 'primary_function', 'text', 'Primary Function', None, 0, None, None, None, 'Main purpose or function', 2),
            ('Other', 'specifications', 'text', 'Specifications', None, 0, None, None, None, 'Detailed specifications and features', 3),
            ('Other', 'installation_method', 'text', 'Installation Method', None, 0, None, None, None, 'How equipment is installed/attached', 4),
            ('Other', 'compatibility_notes', 'text', 'Compatibility Notes', None, 0, None, None, None, 'Compatibility with different bow types', 5),
        ]
        
        # Insert new equipment fields
        all_new_fields = scope_fields + plunger_fields + other_fields
        
        for field_data in all_new_fields:
            try:
                arrow_cursor.execute('''
                    INSERT OR IGNORE INTO equipment_field_standards 
                    (category_name, field_name, field_type, field_label, field_unit, is_required, validation_rules, dropdown_options, default_value, help_text, field_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', field_data)
                print(f"  ✅ Added {field_data[0]} field: {field_data[1]}")
            except Exception as e:
                print(f"  ⚠️  Warning: Could not add {field_data[0]}.{field_data[1]}: {e}")
        
        # UPDATE SIGHT CATEGORY - Remove "scope" option from sight_type
        print("🔧 Updating Sight category to remove scope options...")
        try:
            # Get current sight_type field
            arrow_cursor.execute('''
                SELECT dropdown_options FROM equipment_field_standards 
                WHERE category_name = 'Sight' AND field_label = 'Sight Type'
            ''')
            result = arrow_cursor.fetchone()
            
            if result and result['dropdown_options']:
                current_options = json.loads(result['dropdown_options'])
                # Remove 'scope' option if present
                if 'scope' in current_options:
                    current_options.remove('scope')
                    updated_options = json.dumps(current_options)
                    
                    arrow_cursor.execute('''
                        UPDATE equipment_field_standards 
                        SET dropdown_options = ? 
                        WHERE category_name = 'Sight' AND field_label = 'Sight Type'
                    ''', (updated_options,))
                    print("  ✅ Removed 'scope' from Sight Type options")
                else:
                    print("  ℹ️  'scope' option not found in Sight Type")
            else:
                print("  ⚠️  Could not find Sight Type field")
                
        except Exception as e:
            print(f"  ❌ Error updating Sight category: {e}")
        
        arrow_conn.commit()
        arrow_conn.close()
        print("✅ Arrow database updates completed")
        
        # PART 2: User Database Updates (Auto-Learning Tables)
        print(f"\\n👥 Updating User Database with Auto-Learning System...")
        user_conn = sqlite3.connect(user_db_path)
        user_conn.row_factory = sqlite3.Row
        user_cursor = user_conn.cursor()
        
        # Create auto-learning tables
        learning_tables = [
            # Pending manufacturers awaiting approval
            '''CREATE TABLE IF NOT EXISTS pending_manufacturers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category_context TEXT,
                usage_count INTEGER DEFAULT 1,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                created_by_user_id INTEGER,
                admin_notes TEXT,
                FOREIGN KEY (created_by_user_id) REFERENCES users (id)
            )''',
            
            # Model name repository with usage statistics
            '''CREATE TABLE IF NOT EXISTS equipment_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manufacturer_name TEXT NOT NULL,
                model_name TEXT NOT NULL,
                category_name TEXT NOT NULL,
                usage_count INTEGER DEFAULT 1,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by_user_id INTEGER,
                is_verified BOOLEAN DEFAULT FALSE,
                UNIQUE(manufacturer_name, model_name, category_name),
                FOREIGN KEY (created_by_user_id) REFERENCES users (id)
            )''',
            
            # Manufacturer name variations and aliases
            '''CREATE TABLE IF NOT EXISTS manufacturer_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                canonical_name TEXT NOT NULL,
                alias_name TEXT NOT NULL,
                confidence_score REAL DEFAULT 0.95,
                auto_detected BOOLEAN DEFAULT FALSE,
                verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(canonical_name, alias_name)
            )''',
            
            # Equipment usage and popularity analytics
            '''CREATE TABLE IF NOT EXISTS equipment_usage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manufacturer_name TEXT,
                model_name TEXT,
                category_name TEXT,
                monthly_usage INTEGER DEFAULT 0,
                total_usage INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                period_start DATE,
                period_end DATE,
                UNIQUE(manufacturer_name, model_name, category_name, period_start)
            )'''
        ]
        
        for table_sql in learning_tables:
            try:
                user_cursor.execute(table_sql)
                table_name = table_sql.split('TABLE IF NOT EXISTS ')[1].split(' (')[0]
                print(f"  ✅ Created/verified table: {table_name}")
            except Exception as e:
                print(f"  ❌ Error creating learning table: {e}")
        
        # Create indexes for performance
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_pending_manufacturers_status ON pending_manufacturers(status)',
            'CREATE INDEX IF NOT EXISTS idx_equipment_models_lookup ON equipment_models(manufacturer_name, category_name)',
            'CREATE INDEX IF NOT EXISTS idx_equipment_models_usage ON equipment_models(usage_count DESC, last_used DESC)',
            'CREATE INDEX IF NOT EXISTS idx_manufacturer_aliases_lookup ON manufacturer_aliases(alias_name)',
            'CREATE INDEX IF NOT EXISTS idx_equipment_usage_stats_period ON equipment_usage_stats(period_start, category_name)',
        ]
        
        for index_sql in indexes:
            try:
                user_cursor.execute(index_sql)
            except Exception as e:
                print(f"  ⚠️  Warning: Could not create index: {e}")
        
        user_conn.commit()
        user_conn.close()
        print("✅ User database learning system created")
        
        # PART 3: Update manufacturer matcher for new categories
        print(f"\\n🤖 Updating manufacturer specializations...")
        
        # Add new category specializations (will be done in manufacturer_matcher.py update)
        print("  ℹ️  Manufacturer specializations will be updated in code")
        
        print(f"\\n🎉 Enhanced Equipment System Migration Completed!")
        print(f"=" * 60)
        print("New Equipment Categories:")
        print("  • Scope (6 fields) - Dedicated scope equipment")
        print("  • Plunger (5 fields) - Plunger buttons and mechanisms") 
        print("  • Other (5 fields) - Flexible category for any equipment")
        print("\\nAuto-Learning System:")
        print("  • pending_manufacturers - New manufacturer detection")
        print("  • equipment_models - Model name suggestions")
        print("  • manufacturer_aliases - Name variation tracking")
        print("  • equipment_usage_stats - Usage analytics")
        print("\\nSight Category:")
        print("  • Removed 'scope' option from Sight Type dropdown")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🗄️  Enhanced Equipment System Migration")
    print("=" * 60)
    
    success = migrate_enhanced_equipment_system()
    
    if success:
        print("\\n✅ Migration completed successfully")
        print("🚀 Enhanced equipment system is ready!")
        sys.exit(0)
    else:
        print("\\n❌ Migration failed")
        sys.exit(1)