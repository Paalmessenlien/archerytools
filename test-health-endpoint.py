#!/usr/bin/env python3
"""
Test Health Endpoint
Reproduces the health endpoint logic to identify the error
"""

import sys
import os
sys.path.append('arrow_scraper')

from datetime import datetime
import sqlite3
from pathlib import Path

def test_database_connection():
    """Test the exact database connection logic from the API"""
    print("🧪 Testing Database Connection Logic")
    print("=" * 40)
    
    # Try the database paths from the API
    db_paths = [
        '/app/arrow_database.db',          # Primary location
        '/app/arrow_database_backup.db',   # Backup location
        'arrow_database.db',               # Development location
    ]
    
    # Add the actual local path
    if os.path.exists('arrow_scraper/arrow_database.db'):
        db_paths.append('arrow_scraper/arrow_database.db')
    
    database_path = None
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                print(f"🔍 Checking: {db_path}")
                # Quick check if database has data
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM arrows")
                count = cursor.fetchone()[0]
                conn.close()
                
                if count > 0:
                    print(f"✅ Using database: {db_path} ({count} arrows)")
                    database_path = db_path
                    break
                else:
                    print(f"⚠️  Database exists but empty: {db_path}")
            except Exception as e:
                print(f"⚠️  Database check failed for {db_path}: {e}")
                continue
        else:
            print(f"❌ Database not found: {db_path}")
    
    if not database_path:
        print("💥 No valid database found in any location")
        return None
    
    # Test ArrowDatabase initialization
    try:
        print(f"\n🏗️  Testing ArrowDatabase initialization...")
        
        # Import ArrowDatabase
        from arrow_database import ArrowDatabase
        
        db = ArrowDatabase(database_path)
        print("✅ ArrowDatabase initialized successfully")
        
        # Test get_statistics
        print("📊 Testing get_statistics...")
        stats = db.get_statistics()
        
        if stats:
            print("✅ get_statistics succeeded")
            print(f"   Total arrows: {stats.get('total_arrows', 0)}")
            print(f"   Total manufacturers: {stats.get('total_manufacturers', 0)}")
            return stats
        else:
            print("❌ get_statistics returned None")
            return None
            
    except Exception as e:
        print(f"❌ ArrowDatabase error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_health_endpoint_logic():
    """Test the exact health endpoint logic"""
    print("\n🩺 Testing Health Endpoint Logic")
    print("=" * 40)
    
    try:
        stats = test_database_connection()
        
        if stats:
            db_status = "healthy" if stats else "error"
            db_stats = {
                'total_arrows': stats.get('total_arrows', 0),
                'total_manufacturers': stats.get('total_manufacturers', 0)
            }
        else:
            db_status = "error"
            db_stats = {'total_arrows': 0, 'total_manufacturers': 0}
        
        # Create the response
        response = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'database_status': db_status,
            'database_stats': db_stats
        }
        
        print("✅ Health endpoint logic succeeded")
        print("📄 Response:")
        import json
        print(json.dumps(response, indent=2))
        
        return response
        
    except Exception as e:
        print(f"❌ Health endpoint logic failed: {e}")
        import traceback
        traceback.print_exc()
        
        error_response = {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        
        print("📄 Error Response:")
        import json
        print(json.dumps(error_response, indent=2))
        
        return error_response

if __name__ == "__main__":
    test_health_endpoint_logic()