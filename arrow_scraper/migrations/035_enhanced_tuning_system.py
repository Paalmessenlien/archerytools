#!/usr/bin/env python3
"""
Migration 035: Enhanced Interactive Tuning System
- Creates comprehensive tables for permanent test result storage  
- Adds arrow-specific tuning history tracking
- Integrates equipment adjustment logging
- Enhances existing guide_sessions table
- Enables unlimited repeat testing with full history
"""

import sqlite3
import json
import sys
import os
from datetime import datetime

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 35,
        'description': 'Enhanced Interactive Tuning System with permanent test storage',
        'author': 'System',
        'created_at': '2025-08-20',
        'target_database': 'arrow',
        'dependencies': [],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Apply migration 035: Enhanced Interactive Tuning System"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration 035: Creating enhanced tuning system tables...")
        
        # Create tuning_test_results table for permanent test storage
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tuning_test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guide_session_id INTEGER, -- Can be NULL for standalone tests
                user_id INTEGER NOT NULL,
                bow_setup_id INTEGER NOT NULL,
                arrow_id INTEGER NOT NULL, -- PERMANENT LINK TO ARROW
                arrow_length REAL NOT NULL,
                point_weight REAL NOT NULL,
                test_type TEXT NOT NULL, -- "paper_tuning", "bareshaft_tuning", "walkback_tuning"
                test_data TEXT NOT NULL, -- JSON: test-specific measurements
                recommendations TEXT, -- JSON: generated recommendations
                environmental_conditions TEXT, -- JSON: weather data
                shooting_distance REAL,
                confidence_score REAL,
                test_number INTEGER NOT NULL, -- Sequential test number for this arrow
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                -- Foreign keys allow for historical access even if session is deleted
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE SET NULL,
                FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE
            )
        """)
        
        # Create index for fast arrow-based queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tuning_results_arrow 
            ON tuning_test_results(arrow_id, created_at)
        """)
        
        # Create index for test type queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tuning_results_test_type 
            ON tuning_test_results(arrow_id, test_type, created_at)
        """)
        
        # Create arrow_tuning_history table for aggregate tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS arrow_tuning_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bow_setup_id INTEGER NOT NULL,
                arrow_id INTEGER NOT NULL,
                arrow_length REAL NOT NULL,
                point_weight REAL NOT NULL,
                tuning_status TEXT DEFAULT 'in_progress', -- "in_progress", "completed", "needs_work"
                initial_test_date TIMESTAMP,
                last_test_date TIMESTAMP,
                total_test_sessions INTEGER DEFAULT 0,
                paper_tuning_count INTEGER DEFAULT 0,
                bareshaft_tuning_count INTEGER DEFAULT 0,
                walkback_tuning_count INTEGER DEFAULT 0,
                improvement_score REAL, -- Calculated improvement over time
                current_recommendations TEXT, -- JSON: latest recommendations
                success_indicators TEXT, -- JSON: metrics showing tuning success
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                -- Constraints
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE,
                UNIQUE(user_id, bow_setup_id, arrow_id, arrow_length, point_weight)
            )
        """)
        
        # Create equipment_adjustment_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment_adjustment_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tuning_test_result_id INTEGER NOT NULL,
                component_type TEXT NOT NULL, -- "rest", "plunger", "nocking_point", "sight"
                adjustment_type TEXT NOT NULL, -- "move_in", "move_out", "raise", "lower", "increase_tension"
                adjustment_amount TEXT, -- "0.3-0.6 mm", "+1/4 turn", "0.5mm"
                before_measurement TEXT, -- Previous setting (if known)
                after_measurement TEXT, -- New setting
                effectiveness_rating INTEGER, -- 1-5 user rating of adjustment effectiveness
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                -- Constraints
                FOREIGN KEY (tuning_test_result_id) REFERENCES tuning_test_results (id) ON DELETE CASCADE
            )
        """)
        
        # Create tuning_change_log table for system integration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tuning_change_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                arrow_id INTEGER NOT NULL,
                bow_setup_id INTEGER NOT NULL,
                test_result_id INTEGER NOT NULL,
                change_type TEXT NOT NULL, -- "test_completed", "adjustment_made", "improvement_noted"
                description TEXT NOT NULL,
                before_state TEXT, -- JSON: state before change
                after_state TEXT, -- JSON: state after change
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE,
                FOREIGN KEY (test_result_id) REFERENCES tuning_test_results (id) ON DELETE CASCADE
            )
        """)
        
        # Check if guide_sessions table needs enhancement
        cursor.execute("PRAGMA table_info(guide_sessions)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add new columns to guide_sessions if they don't exist
        if 'arrow_id' not in columns:
            cursor.execute("ALTER TABLE guide_sessions ADD COLUMN arrow_id INTEGER")
            
        if 'arrow_length' not in columns:
            cursor.execute("ALTER TABLE guide_sessions ADD COLUMN arrow_length REAL")
            
        if 'point_weight' not in columns:
            cursor.execute("ALTER TABLE guide_sessions ADD COLUMN point_weight REAL")
            
        if 'test_results_count' not in columns:
            cursor.execute("ALTER TABLE guide_sessions ADD COLUMN test_results_count INTEGER DEFAULT 0")
        
        # Create triggers to maintain arrow_tuning_history
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_arrow_tuning_history_after_test
            AFTER INSERT ON tuning_test_results
            BEGIN
                INSERT OR REPLACE INTO arrow_tuning_history (
                    user_id, bow_setup_id, arrow_id, arrow_length, point_weight,
                    initial_test_date, last_test_date, total_test_sessions,
                    paper_tuning_count, bareshaft_tuning_count, walkback_tuning_count,
                    updated_at
                ) VALUES (
                    NEW.user_id, NEW.bow_setup_id, NEW.arrow_id, NEW.arrow_length, NEW.point_weight,
                    COALESCE((SELECT initial_test_date FROM arrow_tuning_history 
                             WHERE user_id = NEW.user_id AND arrow_id = NEW.arrow_id 
                             AND bow_setup_id = NEW.bow_setup_id 
                             AND arrow_length = NEW.arrow_length 
                             AND point_weight = NEW.point_weight), NEW.created_at),
                    NEW.created_at,
                    COALESCE((SELECT total_test_sessions FROM arrow_tuning_history 
                             WHERE user_id = NEW.user_id AND arrow_id = NEW.arrow_id 
                             AND bow_setup_id = NEW.bow_setup_id 
                             AND arrow_length = NEW.arrow_length 
                             AND point_weight = NEW.point_weight), 0) + 1,
                    CASE WHEN NEW.test_type = 'paper_tuning' THEN 
                        COALESCE((SELECT paper_tuning_count FROM arrow_tuning_history 
                                 WHERE user_id = NEW.user_id AND arrow_id = NEW.arrow_id 
                                 AND bow_setup_id = NEW.bow_setup_id 
                                 AND arrow_length = NEW.arrow_length 
                                 AND point_weight = NEW.point_weight), 0) + 1
                    ELSE COALESCE((SELECT paper_tuning_count FROM arrow_tuning_history 
                                  WHERE user_id = NEW.user_id AND arrow_id = NEW.arrow_id 
                                  AND bow_setup_id = NEW.bow_setup_id 
                                  AND arrow_length = NEW.arrow_length 
                                  AND point_weight = NEW.point_weight), 0)
                    END,
                    CASE WHEN NEW.test_type = 'bareshaft_tuning' THEN 
                        COALESCE((SELECT bareshaft_tuning_count FROM arrow_tuning_history 
                                 WHERE user_id = NEW.user_id AND arrow_id = NEW.arrow_id 
                                 AND bow_setup_id = NEW.bow_setup_id 
                                 AND arrow_length = NEW.arrow_length 
                                 AND point_weight = NEW.point_weight), 0) + 1
                    ELSE COALESCE((SELECT bareshaft_tuning_count FROM arrow_tuning_history 
                                  WHERE user_id = NEW.user_id AND arrow_id = NEW.arrow_id 
                                  AND bow_setup_id = NEW.bow_setup_id 
                                  AND arrow_length = NEW.arrow_length 
                                  AND point_weight = NEW.point_weight), 0)
                    END,
                    CASE WHEN NEW.test_type = 'walkback_tuning' THEN 
                        COALESCE((SELECT walkback_tuning_count FROM arrow_tuning_history 
                                 WHERE user_id = NEW.user_id AND arrow_id = NEW.arrow_id 
                                 AND bow_setup_id = NEW.bow_setup_id 
                                 AND arrow_length = NEW.arrow_length 
                                 AND point_weight = NEW.point_weight), 0) + 1
                    ELSE COALESCE((SELECT walkback_tuning_count FROM arrow_tuning_history 
                                  WHERE user_id = NEW.user_id AND arrow_id = NEW.arrow_id 
                                  AND bow_setup_id = NEW.bow_setup_id 
                                  AND arrow_length = NEW.arrow_length 
                                  AND point_weight = NEW.point_weight), 0)
                    END,
                    CURRENT_TIMESTAMP
                );
            END;
        """)
        
        conn.commit()
        print("🎯 Migration 035 completed successfully!")
        print("📊 Created enhanced tuning system tables:")
        print("   - tuning_test_results: Permanent test storage with arrow linkage")
        print("   - arrow_tuning_history: Aggregate tracking and progress metrics")
        print("   - equipment_adjustment_log: Equipment change tracking")
        print("   - tuning_change_log: System integration and notifications")
        print("   - Enhanced guide_sessions: Arrow-specific session tracking")
        print("   - Indexes and triggers: Performance and data consistency")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 035 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback migration 035: Enhanced Interactive Tuning System"""
    conn = cursor.connection
    
    try:
        print("🔄 Rolling back Migration 035...")
        
        # Drop triggers first
        cursor.execute("DROP TRIGGER IF EXISTS update_arrow_tuning_history_after_test")
        
        # Drop new tables
        cursor.execute("DROP TABLE IF EXISTS tuning_change_log")
        cursor.execute("DROP TABLE IF EXISTS equipment_adjustment_log")
        cursor.execute("DROP TABLE IF EXISTS arrow_tuning_history")
        cursor.execute("DROP INDEX IF EXISTS idx_tuning_results_test_type")
        cursor.execute("DROP INDEX IF EXISTS idx_tuning_results_arrow")
        cursor.execute("DROP TABLE IF EXISTS tuning_test_results")
        
        # Note: SQLite doesn't support DROP COLUMN directly
        # guide_sessions columns are left for data preservation
        
        conn.commit()
        print("🔄 Migration 035 rollback completed")
        print("   Note: guide_sessions columns (arrow_id, arrow_length, point_weight, test_results_count)")
        print("         were left intact for data preservation")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 035 rollback failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Test the migration
    db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)
    
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