#!/usr/bin/env python3
"""
Database Fixtures Creator
Creates anonymized database fixtures for consistent development/production setup
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
import hashlib

def anonymize_email(email):
    """Create anonymized version of email for fixtures"""
    if not email:
        return None
    # Create consistent hash-based anonymous email
    hash_obj = hashlib.md5(email.encode())
    return f"user_{hash_obj.hexdigest()[:8]}@example.com"

def export_arrow_database(db_path, output_dir):
    """Export arrow database to JSON fixtures (no PII)"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    fixtures = {}
    
    # Export arrow-related tables (public data)
    public_tables = [
        'arrows', 
        'spine_specifications', 
        'components', 
        'component_categories',
        'arrow_component_compatibility',
        'compatibility_rules'
    ]
    
    for table in public_tables:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            fixtures[table] = [dict(row) for row in rows]
            print(f"✅ Exported {len(rows)} rows from {table}")
        except sqlite3.OperationalError as e:
            print(f"⚠️  Skipped {table}: {e}")
    
    # Export schema information
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    schema_rows = cursor.fetchall()
    fixtures['schema'] = [row[0] for row in schema_rows if row[0]]
    
    conn.close()
    
    # Save fixtures
    fixture_file = output_dir / "arrow_database_fixtures.json"
    with open(fixture_file, 'w') as f:
        json.dump(fixtures, f, indent=2, default=str)
    
    print(f"💾 Arrow database fixtures saved to {fixture_file}")
    return fixture_file

def export_user_database_schema(db_path, output_dir):
    """Export user database schema (no actual data for privacy)"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Export only schema, not data (for privacy)
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    schema_rows = cursor.fetchall()
    
    schema_data = {
        'schema': [row[0] for row in schema_rows if row[0]],
        'sample_data': {
            'users': [{
                'id': 1,
                'email': 'admin@example.com',
                'name': 'Admin User',
                'is_admin': True,
                'created_at': datetime.now().isoformat()
            }]
        }
    }
    
    conn.close()
    
    # Save schema
    schema_file = output_dir / "user_database_schema.json"
    with open(schema_file, 'w') as f:
        json.dump(schema_data, f, indent=2, default=str)
    
    print(f"💾 User database schema saved to {schema_file}")
    return schema_file

def create_database_from_fixtures(fixture_file, output_db_path):
    """Create database from fixtures"""
    with open(fixture_file, 'r') as f:
        fixtures = json.load(f)
    
    # Remove existing database
    if os.path.exists(output_db_path):
        os.remove(output_db_path)
    
    conn = sqlite3.connect(output_db_path)
    cursor = conn.cursor()
    
    # Create tables from schema
    for sql in fixtures.get('schema', []):
        if sql and sql.strip():
            try:
                cursor.execute(sql)
                print(f"✅ Created table from: {sql[:50]}...")
            except sqlite3.Error as e:
                print(f"⚠️  Schema error: {e}")
    
    # Insert data
    for table, rows in fixtures.items():
        if table == 'schema':
            continue
            
        if not rows:
            continue
            
        try:
            # Get column names from first row
            columns = list(rows[0].keys())
            placeholders = ','.join(['?' for _ in columns])
            
            insert_sql = f"INSERT OR REPLACE INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
            
            for row in rows:
                values = [row[col] for col in columns]
                cursor.execute(insert_sql, values)
            
            print(f"✅ Inserted {len(rows)} rows into {table}")
            
        except sqlite3.Error as e:
            print(f"⚠️  Insert error for {table}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"💾 Database created at {output_db_path}")

def main():
    print("🏹 Database Fixtures Creator")
    print("=" * 50)
    
    # Create fixtures directory
    fixtures_dir = Path("database_fixtures")
    fixtures_dir.mkdir(exist_ok=True)
    
    # Check if we're in Docker or local
    if os.path.exists("/app/arrow_database.db"):
        # In Docker
        arrow_db = "/app/arrow_database.db"
        user_db = "/app/user_data/user_data.db"
        print("🐳 Running in Docker environment")
    else:
        # Local
        arrow_db = "arrow_scraper/arrow_database.db"
        user_db = "arrow_scraper/user_data.db"
        print("💻 Running in local environment")
    
    # Export arrow database fixtures
    if os.path.exists(arrow_db):
        arrow_fixture = export_arrow_database(arrow_db, fixtures_dir)
        
        # Create test database from fixtures
        test_db = fixtures_dir / "test_arrow_database.db"
        create_database_from_fixtures(arrow_fixture, test_db)
        print(f"✅ Test database created at {test_db}")
    
    # Export user database schema
    if os.path.exists(user_db):
        user_schema = export_user_database_schema(user_db, fixtures_dir)
    else:
        print("⚠️  User database not found, creating minimal schema")
        # Create minimal user schema
        minimal_schema = {
            'schema': [
                '''CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )''',
                '''CREATE TABLE bow_setups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    bow_type TEXT,
                    draw_weight REAL,
                    draw_length REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )'''
            ],
            'sample_data': {
                'users': [{
                    'id': 1,
                    'email': 'admin@example.com',
                    'name': 'Admin User',
                    'is_admin': True,
                    'created_at': datetime.now().isoformat()
                }]
            }
        }
        
        user_schema = fixtures_dir / "user_database_schema.json"
        with open(user_schema, 'w') as f:
            json.dump(minimal_schema, f, indent=2, default=str)
    
    print("\n" + "=" * 50)
    print("✅ Database fixtures created successfully!")
    print(f"📁 Fixtures location: {fixtures_dir.absolute()}")
    print("\nFiles created:")
    for file in fixtures_dir.glob("*"):
        print(f"  - {file.name}")
    
    print("\n📋 Next steps:")
    print("1. Review fixtures for any sensitive data")
    print("2. Commit fixtures to git (NOT the actual databases)")
    print("3. Use fixtures to initialize clean databases in dev/prod")

if __name__ == "__main__":
    main()