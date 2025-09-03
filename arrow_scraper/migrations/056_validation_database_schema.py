#!/usr/bin/env python3
"""
Migration 056: Validation Database Schema
Adds tables for tracking validation runs, issues, and fixes to enable historical monitoring of data quality
"""
import sqlite3
import sys
import os

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 56,
        'description': 'Validation database schema - add tables for tracking validation runs and issues',
        'author': 'System', 
        'created_at': '2025-09-03',
        'target_database': 'arrow',  # Unified database - all data in arrow_database.db
        'dependencies': ['055'],  # Depends on previous migration
        'environments': ['all']
    }

def migrate_up(cursor):
    """Apply the migration"""
    conn = cursor.connection
    try:
        print("🔧 Migration 056: Adding validation database schema tables...")
        
        # Create validation_runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_issues INTEGER DEFAULT 0,
                critical_issues INTEGER DEFAULT 0,
                warning_issues INTEGER DEFAULT 0,
                info_issues INTEGER DEFAULT 0,
                health_score REAL DEFAULT 0.0,
                run_duration_ms INTEGER DEFAULT 0,
                triggered_by TEXT DEFAULT 'system',
                validation_version TEXT DEFAULT '1.0',
                database_version TEXT,
                total_arrows_checked INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created validation_runs table")
        
        # Create validation_issues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validation_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                issue_hash TEXT UNIQUE,  -- Hash of issue content for deduplication
                category TEXT NOT NULL,
                severity TEXT NOT NULL CHECK (severity IN ('critical', 'warning', 'info')),
                arrow_id INTEGER,
                manufacturer TEXT,
                model_name TEXT,
                field TEXT,
                issue_description TEXT NOT NULL,
                current_value TEXT,
                suggested_fix TEXT,
                sql_fix TEXT,
                is_resolved BOOLEAN DEFAULT FALSE,
                resolved_at DATETIME,
                resolved_by TEXT,
                auto_fixable BOOLEAN DEFAULT FALSE,
                first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                occurrence_count INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES validation_runs(id) ON DELETE CASCADE
            )
        """)
        print("✅ Created validation_issues table")
        
        # Create validation_fixes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validation_fixes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue_id INTEGER NOT NULL,
                fix_attempt_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                fix_method TEXT NOT NULL,  -- 'manual', 'automated', 'sql'
                fix_description TEXT,
                sql_executed TEXT,
                success BOOLEAN DEFAULT FALSE,
                error_message TEXT,
                applied_by TEXT,
                rollback_sql TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (issue_id) REFERENCES validation_issues(id) ON DELETE CASCADE
            )
        """)
        print("✅ Created validation_fixes table")
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_validation_runs_timestamp ON validation_runs(run_timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_validation_issues_run_id ON validation_issues(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_validation_issues_severity ON validation_issues(severity)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_validation_issues_category ON validation_issues(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_validation_issues_arrow_id ON validation_issues(arrow_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_validation_issues_resolved ON validation_issues(is_resolved)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_validation_issues_hash ON validation_issues(issue_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_validation_fixes_issue_id ON validation_fixes(issue_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_validation_fixes_timestamp ON validation_fixes(fix_attempt_timestamp)")
        print("✅ Created database indexes for validation tables")
        
        # Create validation_rules configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT UNIQUE NOT NULL,
                rule_category TEXT NOT NULL,
                rule_type TEXT NOT NULL CHECK (rule_type IN ('required', 'range', 'format', 'reference', 'business')),
                target_table TEXT,
                target_field TEXT,
                rule_config TEXT,  -- JSON configuration for rule parameters
                is_enabled BOOLEAN DEFAULT TRUE,
                severity TEXT DEFAULT 'warning' CHECK (severity IN ('critical', 'warning', 'info')),
                auto_fixable BOOLEAN DEFAULT FALSE,
                description TEXT,
                fix_template TEXT,  -- Template for automatic fix SQL
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created validation_rules table")
        
        # Add default validation rules
        default_rules = [
            ('spine_range_carbon', 'Data Range', 'range', 'spine_specifications', 'spine', '{"min": 150, "max": 2000, "material": "Carbon"}', True, 'warning', False, 'Carbon arrows should have spine values between 150-2000'),
            ('spine_range_wood', 'Data Range', 'range', 'spine_specifications', 'spine', '{"min": 25, "max": 85, "material": "Wood"}', True, 'warning', False, 'Wood arrows should have spine values between 25-85 pounds'),
            ('diameter_positive', 'Data Range', 'range', 'spine_specifications', 'outer_diameter', '{"min": 0.1, "max": 15.0}', True, 'critical', False, 'Outer diameter must be positive and reasonable (0.1-15.0mm)'),
            ('gpi_weight_positive', 'Data Range', 'range', 'spine_specifications', 'gpi_weight', '{"min": 1, "max": 100}', True, 'critical', False, 'GPI weight must be positive and reasonable (1-100 grains)'),
            ('arrow_material_required', 'Required Fields', 'required', 'arrows', 'material', '{}', True, 'critical', False, 'Arrow material is required'),
            ('manufacturer_required', 'Required Fields', 'required', 'arrows', 'manufacturer', '{}', True, 'critical', False, 'Manufacturer is required'),
            ('model_name_required', 'Required Fields', 'required', 'arrows', 'model_name', '{}', True, 'critical', False, 'Model name is required'),
            ('search_visibility', 'System Integrity', 'business', 'arrows', 'search_visibility', '{}', True, 'critical', False, 'Arrow must appear in database search results'),
            ('spine_specifications_exist', 'Reference Integrity', 'reference', 'arrows', 'spine_specifications', '{}', True, 'warning', False, 'Arrow should have at least one spine specification')
        ]
        
        cursor.execute("SELECT COUNT(*) FROM validation_rules")
        existing_rules_count = cursor.fetchone()[0]
        
        if existing_rules_count == 0:
            for rule in default_rules:
                cursor.execute("""
                    INSERT INTO validation_rules 
                    (rule_name, rule_category, rule_type, target_table, target_field, rule_config, 
                     is_enabled, severity, auto_fixable, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, rule)
            print(f"✅ Added {len(default_rules)} default validation rules")
        else:
            print(f"ℹ️ Validation rules already exist ({existing_rules_count} rules)")
        
        # Create index for validation_rules
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_validation_rules_category ON validation_rules(rule_category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_validation_rules_enabled ON validation_rules(is_enabled)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_validation_rules_severity ON validation_rules(severity)")
        
        conn.commit()
        print("🎯 Migration 056 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration 056 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback the migration"""
    conn = cursor.connection
    try:
        print("🔄 Rolling back Migration 056...")
        
        # Drop tables in reverse order (respecting foreign keys)
        cursor.execute("DROP TABLE IF EXISTS validation_fixes")
        cursor.execute("DROP TABLE IF EXISTS validation_issues") 
        cursor.execute("DROP TABLE IF EXISTS validation_rules")
        cursor.execute("DROP TABLE IF EXISTS validation_runs")
        
        conn.commit()
        print("✅ Migration 056 rollback completed")
        return True
        
    except Exception as e:
        print(f"❌ Migration 056 rollback failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Test standalone
    db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db')
    
    # For testing, use a temporary database
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        db_path = "test_migration_056.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            
        # Create minimal test database structure
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create basic tables for testing
        cursor.execute("""
            CREATE TABLE arrows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manufacturer TEXT,
                model_name TEXT,
                material TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE spine_specifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arrow_id INTEGER,
                spine REAL,
                outer_diameter REAL,
                gpi_weight REAL,
                FOREIGN KEY (arrow_id) REFERENCES arrows(id)
            )
        """)
        
        # Insert test data
        cursor.execute("INSERT INTO arrows (manufacturer, model_name, material) VALUES ('Test Mfg', 'Test Arrow', 'Carbon')")
        cursor.execute("INSERT INTO spine_specifications (arrow_id, spine, outer_diameter, gpi_weight) VALUES (1, 340, 6.2, 8.5)")
        
        conn.commit()
    else:
        # Use actual database for standalone execution
        conn = sqlite3.connect(db_path)
    
    try:
        success = migrate_up(conn.cursor())
        print("✅ Migration test completed successfully" if success else "❌ Migration test failed")
        
        if success and len(sys.argv) > 1 and sys.argv[1] == "test":
            # Verify test results
            cursor = conn.cursor()
            
            # Check tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'validation_%'")
            tables = cursor.fetchall()
            print(f"📊 Created {len(tables)} validation tables: {[t[0] for t in tables]}")
            
            # Check default rules
            cursor.execute("SELECT COUNT(*) FROM validation_rules")
            rules_count = cursor.fetchone()[0]
            print(f"📋 Created {rules_count} default validation rules")
                    
    finally:
        conn.close()
        if len(sys.argv) > 1 and sys.argv[1] == "test" and os.path.exists("test_migration_056.db"):
            os.remove("test_migration_056.db")