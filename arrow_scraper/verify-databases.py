#!/usr/bin/env python3
"""
Comprehensive database verification script for ArrowTuner production deployment.
This script validates both arrow database and user database integrity.
"""
import sqlite3
import os
import sys
from pathlib import Path
import json
from datetime import datetime

def verify_arrow_database(db_path):
    """Verify arrow database structure and content."""
    print(f"🔍 Verifying Arrow Database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Arrow database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check database integrity
        cursor.execute("PRAGMA integrity_check;")
        integrity_result = cursor.fetchone()[0]
        if integrity_result != "ok":
            print(f"❌ Database integrity check failed: {integrity_result}")
            return False
        
        # Check for required tables
        required_tables = ['arrows', 'spine_specifications']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        if missing_tables:
            print(f"❌ Missing required tables: {missing_tables}")
            return False
        
        # Check content volume
        cursor.execute("SELECT COUNT(*) FROM arrows")
        arrow_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM spine_specifications")
        spine_count = cursor.fetchone()[0]
        
        print(f"📊 Arrow Database Statistics:")
        print(f"   Tables: {len(existing_tables)}")
        print(f"   Arrows: {arrow_count}")
        print(f"   Spine Specifications: {spine_count}")
        
        # Check for minimum expected content
        if arrow_count < 50:
            print(f"⚠️  Warning: Low arrow count ({arrow_count})")
        
        # Check for required columns in arrows table
        cursor.execute("PRAGMA table_info(arrows)")
        arrow_columns = [col[1] for col in cursor.fetchall()]
        required_arrow_columns = ['id', 'manufacturer', 'model_name', 'material']
        
        missing_columns = [col for col in required_arrow_columns if col not in arrow_columns]
        if missing_columns:
            print(f"❌ Missing required columns in arrows table: {missing_columns}")
            return False
        
        # Sample data verification
        cursor.execute("SELECT manufacturer, COUNT(*) FROM arrows GROUP BY manufacturer")
        manufacturers = cursor.fetchall()
        print(f"   Manufacturers: {len(manufacturers)}")
        for mfg, count in manufacturers[:5]:  # Show first 5
            print(f"      {mfg}: {count} arrows")
        if len(manufacturers) > 5:
            print(f"      ... and {len(manufacturers) - 5} more")
        
        conn.close()
        print("✅ Arrow database verification successful")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying arrow database: {e}")
        return False

def verify_user_database(db_path):
    """Verify user database structure and initialize if needed."""
    print(f"🔍 Verifying User Database: {db_path}")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        # Try to initialize/verify user database
        from user_database import UserDatabase
        user_db = UserDatabase(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check database integrity
        cursor.execute("PRAGMA integrity_check;")
        integrity_result = cursor.fetchone()[0]
        if integrity_result != "ok":
            print(f"❌ User database integrity check failed: {integrity_result}")
            return False
        
        # Check for required tables
        required_tables = ['users', 'bow_setups', 'guide_sessions', 'guide_step_results', 'tuning_history']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        if missing_tables:
            print(f"⚠️  Some tables missing (will be created on demand): {missing_tables}")
        
        # Check content
        user_count = 0
        bow_count = 0
        session_count = 0
        
        if 'users' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
        
        if 'bow_setups' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM bow_setups")
            bow_count = cursor.fetchone()[0]
        
        if 'guide_sessions' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM guide_sessions")
            session_count = cursor.fetchone()[0]
        
        print(f"📊 User Database Statistics:")
        print(f"   Tables: {len(existing_tables)}")
        print(f"   Users: {user_count}")
        print(f"   Bow Setups: {bow_count}")
        print(f"   Guide Sessions: {session_count}")
        
        conn.close()
        print("✅ User database verification successful")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying user database: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_environment():
    """Check critical environment variables."""
    print("🔍 Checking Environment Variables")
    
    required_vars = {
        'SECRET_KEY': 'Application secret key',
        'GOOGLE_CLIENT_SECRET': 'Google OAuth client secret',
        'NUXT_PUBLIC_GOOGLE_CLIENT_ID': 'Google OAuth client ID'
    }
    
    issues = []
    
    for var_name, description in required_vars.items():
        value = os.environ.get(var_name, '')
        if not value or value in ['not-set', 'change-this-secret-key-in-production']:
            issues.append(f"   ❌ {var_name}: {description} not set or using default")
        else:
            print(f"   ✅ {var_name}: Set ({len(value)} characters)")
    
    if issues:
        print("⚠️  Environment issues found:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("✅ All environment variables properly configured")
        return True

def generate_verification_report():
    """Generate a verification report."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'verification_results': {},
        'recommendations': []
    }
    
    # Determine database paths
    arrow_db_path = "/app/arrow_database.db"
    user_db_paths = [
        "/app/user_data/user_data.db",  # Docker volume
        "/app/user_data.db"             # Fallback
    ]
    
    # Find user database
    user_db_path = None
    for path in user_db_paths:
        if os.path.exists(os.path.dirname(path)):
            user_db_path = path
            break
    
    if not user_db_path:
        user_db_path = user_db_paths[0]  # Use first as default
    
    print("🔍 ArrowTuner Database Verification")
    print("=" * 50)
    
    # Verify arrow database
    arrow_db_ok = verify_arrow_database(arrow_db_path)
    report['verification_results']['arrow_database'] = {
        'path': arrow_db_path,
        'status': 'passed' if arrow_db_ok else 'failed'
    }
    
    print()
    
    # Verify user database
    user_db_ok = verify_user_database(user_db_path)
    report['verification_results']['user_database'] = {
        'path': user_db_path,
        'status': 'passed' if user_db_ok else 'failed'
    }
    
    print()
    
    # Check environment
    env_ok = check_environment()
    report['verification_results']['environment'] = {
        'status': 'passed' if env_ok else 'failed'
    }
    
    print()
    
    # Overall status
    all_ok = arrow_db_ok and user_db_ok and env_ok
    report['overall_status'] = 'passed' if all_ok else 'failed'
    
    if all_ok:
        print("🎉 All verifications passed! System ready for production.")
    else:
        print("❌ Some verifications failed. Check the issues above.")
        
        if not arrow_db_ok:
            report['recommendations'].append("Rebuild arrow database or restore from backup")
        if not user_db_ok:
            report['recommendations'].append("Initialize user database or check user_database.py")
        if not env_ok:
            report['recommendations'].append("Set missing environment variables")
    
    # Save report
    report_path = "/app/verification_report.json"
    try:
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📝 Verification report saved to {report_path}")
    except Exception as e:
        print(f"⚠️  Could not save verification report: {e}")
    
    return all_ok

if __name__ == "__main__":
    success = generate_verification_report()
    sys.exit(0 if success else 1)