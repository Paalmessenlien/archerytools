#!/usr/bin/env python3
"""
Migration 064: Technical Tuning System

Creates tables for bow tuning configurations, parameter values, and change history.
Supports multiple tuning setups per bow with one marked as active.
All changes are tracked in a dedicated tuning change log.

Tables created:
- bow_tuning_configs: Main tuning configurations
- bow_tuning_values: Flexible key-value parameter storage
- tuning_change_log: History tracking for tuning changes
"""

import sqlite3
import sys
import os
from pathlib import Path

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 64,
        'description': 'Technical tuning system with configurations, values, and change history',
        'author': 'System',
        'created_at': '2025-11-29',
        'target_database': 'arrow',
        'dependencies': ['063'],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Create technical tuning tables"""
    conn = cursor.connection

    print("Creating technical tuning system tables...")

    # Drop old tuning_change_log table if it has incompatible schema
    # (from a previous migration with different structure)
    try:
        cursor.execute("SELECT tuning_config_id FROM tuning_change_log LIMIT 1")
    except sqlite3.OperationalError:
        # Column doesn't exist, need to drop and recreate
        print("Found old tuning_change_log with incompatible schema, dropping...")
        cursor.execute("DROP TABLE IF EXISTS tuning_change_log")
        cursor.execute("DROP INDEX IF EXISTS idx_tuning_change_log_setup")

    # Main tuning configurations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bow_tuning_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bow_setup_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bow_setup_id) REFERENCES bow_setups(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    print("✅ Created bow_tuning_configs table")

    # Tuning parameter values (flexible key-value storage)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bow_tuning_values (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tuning_config_id INTEGER NOT NULL,
            parameter_name TEXT NOT NULL,
            parameter_value TEXT,
            unit TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tuning_config_id) REFERENCES bow_tuning_configs(id) ON DELETE CASCADE,
            UNIQUE(tuning_config_id, parameter_name)
        )
    """)
    print("✅ Created bow_tuning_values table")

    # Tuning change log for history tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tuning_change_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bow_setup_id INTEGER NOT NULL,
            tuning_config_id INTEGER,
            user_id INTEGER NOT NULL,
            change_type TEXT NOT NULL,
            parameter_name TEXT,
            old_value TEXT,
            new_value TEXT,
            change_description TEXT,
            user_note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bow_setup_id) REFERENCES bow_setups(id) ON DELETE CASCADE,
            FOREIGN KEY (tuning_config_id) REFERENCES bow_tuning_configs(id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    print("✅ Created tuning_change_log table")

    # Create indexes for performance
    indexes = [
        ("idx_tuning_configs_setup", "bow_tuning_configs(bow_setup_id)"),
        ("idx_tuning_configs_active", "bow_tuning_configs(bow_setup_id, is_active)"),
        ("idx_tuning_configs_user", "bow_tuning_configs(user_id)"),
        ("idx_tuning_values_config", "bow_tuning_values(tuning_config_id)"),
        ("idx_tuning_values_param", "bow_tuning_values(tuning_config_id, parameter_name)"),
        ("idx_tuning_change_log_setup", "tuning_change_log(bow_setup_id)"),
        ("idx_tuning_change_log_config", "tuning_change_log(tuning_config_id)"),
        ("idx_tuning_change_log_user", "tuning_change_log(user_id)"),
        ("idx_tuning_change_log_date", "tuning_change_log(created_at)"),
    ]

    for index_name, index_def in indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}")
        except sqlite3.OperationalError as e:
            if "already exists" not in str(e):
                raise
    print("✅ Created indexes for tuning tables")

    conn.commit()
    print("✅ Migration 064 completed successfully")

    return True

def migrate_down(cursor):
    """Remove technical tuning tables"""
    conn = cursor.connection

    print("Removing technical tuning system tables...")

    # Drop indexes first
    indexes = [
        "idx_tuning_configs_setup",
        "idx_tuning_configs_active",
        "idx_tuning_configs_user",
        "idx_tuning_values_config",
        "idx_tuning_values_param",
        "idx_tuning_change_log_setup",
        "idx_tuning_change_log_config",
        "idx_tuning_change_log_user",
        "idx_tuning_change_log_date",
    ]

    for index_name in indexes:
        try:
            cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
        except sqlite3.OperationalError:
            pass

    # Drop tables in reverse order (due to foreign keys)
    cursor.execute("DROP TABLE IF EXISTS tuning_change_log")
    cursor.execute("DROP TABLE IF EXISTS bow_tuning_values")
    cursor.execute("DROP TABLE IF EXISTS bow_tuning_configs")

    conn.commit()
    print("✅ Technical tuning tables removed")

    return True

# Allow running directly for testing
if __name__ == '__main__':
    # Find database
    db_paths = [
        'databases/arrow_database.db',
        '../databases/arrow_database.db',
        'arrow_scraper/databases/arrow_database.db'
    ]

    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break

    if not db_path:
        print("❌ Could not find database")
        sys.exit(1)

    print(f"Using database: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    try:
        migrate_up(cursor)
        print("✅ Migration completed successfully")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()
