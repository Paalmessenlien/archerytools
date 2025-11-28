#!/usr/bin/env python3
"""
Database Initialization from Fixtures
Initializes clean databases from JSON fixtures for consistent dev/prod setup
"""

import sqlite3
import json
import os
import sys
from pathlib import Path
from datetime import datetime

def init_arrow_database(fixture_file, output_path):
    """Initialize arrow database from fixtures"""
    print(f"🏹 Initializing arrow database from {fixture_file}")
    
    if not os.path.exists(fixture_file):
        print(f"❌ Fixture file not found: {fixture_file}")
        return False
    
    with open(fixture_file, 'r') as f:
        fixtures = json.load(f)
    
    # Remove existing database
    if os.path.exists(output_path):
        backup_path = f"{output_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(output_path, backup_path)
        print(f"📋 Backed up existing database to {backup_path}")
    
    conn = sqlite3.connect(output_path)
    cursor = conn.cursor()
    
    # Create tables from schema
    print("🏗️  Creating database schema...")
    for sql in fixtures.get('schema', []):
        if sql and sql.strip():
            try:
                cursor.execute(sql)
            except sqlite3.Error as e:
                print(f"⚠️  Schema error: {e}")
    
    # Insert data
    print("📊 Inserting data...")
    for table, rows in fixtures.items():
        if table == 'schema' or not rows:
            continue
            
        try:
            # Get column names from first row
            columns = list(rows[0].keys())
            placeholders = ','.join(['?' for _ in columns])
            
            insert_sql = f"INSERT OR REPLACE INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
            
            for row in rows:
                values = [row[col] for col in columns]
                cursor.execute(insert_sql, values)
            
            print(f"  ✅ {table}: {len(rows)} rows")
            
        except sqlite3.Error as e:
            print(f"  ⚠️  {table}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Arrow database initialized: {output_path}")
    return True

def init_user_database(schema_file, output_path):
    """Initialize user database from schema"""
    print(f"👤 Initializing user database from {schema_file}")
    
    if not os.path.exists(schema_file):
        print(f"❌ Schema file not found: {schema_file}")
        return False
    
    with open(schema_file, 'r') as f:
        schema_data = json.load(f)
    
    # Remove existing database
    if os.path.exists(output_path):
        backup_path = f"{output_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(output_path, backup_path)
        print(f"📋 Backed up existing database to {backup_path}")
    
    conn = sqlite3.connect(output_path)
    cursor = conn.cursor()
    
    # Create tables from schema
    print("🏗️  Creating user database schema...")
    for sql in schema_data.get('schema', []):
        if sql and sql.strip():
            try:
                cursor.execute(sql)
            except sqlite3.Error as e:
                print(f"⚠️  Schema error: {e}")
    
    # Insert sample data if provided
    sample_data = schema_data.get('sample_data', {})
    if sample_data:
        print("📊 Inserting sample data...")
        for table, rows in sample_data.items():
            if not rows:
                continue
                
            try:
                columns = list(rows[0].keys())
                placeholders = ','.join(['?' for _ in columns])
                
                insert_sql = f"INSERT OR REPLACE INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
                
                for row in rows:
                    values = [row[col] for col in columns]
                    cursor.execute(insert_sql, values)
                
                print(f"  ✅ {table}: {len(rows)} rows")
                
            except sqlite3.Error as e:
                print(f"  ⚠️  {table}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ User database initialized: {output_path}")
    return True

def verify_database(db_path, db_type):
    """Verify database was created correctly"""
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        if db_type == "arrow":
            cursor.execute("SELECT COUNT(*) FROM arrows")
            arrow_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT manufacturer) FROM arrows")
            mfr_count = cursor.fetchone()[0]
            print(f"✅ Arrow database verified: {arrow_count} arrows, {mfr_count} manufacturers")
            
        elif db_type == "user":
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"✅ User database verified: {user_count} users")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database verification failed: {e}")
        conn.close()
        return False

def main():
    print("🏹 Database Initialization from Fixtures")
    print("=" * 50)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Initialize databases from fixtures")
    parser.add_argument("--fixtures-dir", default="database_fixtures", help="Fixtures directory")
    parser.add_argument("--output-dir", default=".", help="Output directory for databases")
    parser.add_argument("--arrow-only", action="store_true", help="Initialize only arrow database")
    parser.add_argument("--user-only", action="store_true", help="Initialize only user database")
    
    args = parser.parse_args()
    
    fixtures_dir = Path(args.fixtures_dir)
    output_dir = Path(args.output_dir)
    
    if not fixtures_dir.exists():
        print(f"❌ Fixtures directory not found: {fixtures_dir}")
        sys.exit(1)
    
    success = True
    
    # Initialize arrow database
    if not args.user_only:
        arrow_fixture = fixtures_dir / "arrow_database_fixtures.json"
        arrow_db = output_dir / "arrow_database.db"
        
        if init_arrow_database(arrow_fixture, arrow_db):
            verify_database(arrow_db, "arrow")
        else:
            success = False
    
    # Initialize user database
    if not args.arrow_only:
        user_schema = fixtures_dir / "user_database_schema.json"
        user_db = output_dir / "user_data.db"
        
        if init_user_database(user_schema, user_db):
            verify_database(user_db, "user")
        else:
            success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Database initialization completed successfully!")
        print(f"📁 Databases created in: {output_dir.absolute()}")
        
        print("\n📋 Usage:")
        print("- Copy databases to your development environment")
        print("- Use in Docker containers for consistent data")
        print("- Version control the fixtures (JSON), not the databases")
    else:
        print("❌ Database initialization had errors")
        sys.exit(1)

if __name__ == "__main__":
    main()