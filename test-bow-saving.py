#!/usr/bin/env python3
"""
Test script to verify bow saving functionality in production environment.
This script tests the bow setup creation process to identify issues.
"""
import sqlite3
import os
import sys
import json
from pathlib import Path

def test_user_database_connection():
    """Test user database connection and schema."""
    print("🔍 Testing User Database Connection")
    print("=" * 40)
    
    # Try different possible paths for user database
    possible_paths = [
        "/app/user_data/user_data.db",  # Docker volume
        "/app/user_data.db",            # Fallback location
        "user_data.db",                 # Local development
        "arrow_scraper/user_data.db"    # Local development alternate
    ]
    
    user_db_path = None
    for path in possible_paths:
        if os.path.exists(path) or os.path.exists(os.path.dirname(path)):
            user_db_path = path
            print(f"📁 Using user database path: {path}")
            break
    
    if not user_db_path:
        print("❌ No suitable user database path found")
        return False
    
    try:
        # Try to initialize user database
        sys.path.append('/app')
        sys.path.append('.')
        sys.path.append('./arrow_scraper')
        
        from user_database import UserDatabase
        user_db = UserDatabase(user_db_path)
        
        # Test connection
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Check if bow_setups table exists and has correct schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='bow_setups'")
        table_schema = cursor.fetchone()
        
        if not table_schema:
            print("❌ bow_setups table does not exist")
            return False
        
        print("✅ bow_setups table exists")
        print(f"📋 Schema: {table_schema[0]}")
        
        # Check table columns
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📊 Columns ({len(column_names)}): {', '.join(column_names)}")
        
        # Check for required columns
        required_columns = [
            'id', 'user_id', 'name', 'bow_type', 'draw_weight', 'draw_length',
            'bow_usage', 'riser_model', 'limb_model', 'compound_model'
        ]
        
        missing_columns = [col for col in required_columns if col not in column_names]
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return False
        
        print("✅ All required columns present")
        
        # Test basic operations
        test_user_id = 1
        
        # Test insert
        try:
            cursor.execute("""
                INSERT INTO bow_setups 
                (user_id, name, bow_type, draw_weight, draw_length, bow_usage, riser_model, limb_model, compound_model)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (test_user_id, 'Test Bow', 'recurve', 30, 28, 'target', 'Test Riser', 'Test Limbs', None))
            
            test_setup_id = cursor.lastrowid
            print(f"✅ Test insert successful (ID: {test_setup_id})")
            
            # Test select
            cursor.execute("SELECT * FROM bow_setups WHERE id = ?", (test_setup_id,))
            test_setup = cursor.fetchone()
            
            if test_setup:
                print("✅ Test select successful")
                print(f"   Retrieved: {dict(test_setup)}")
            else:
                print("❌ Test select failed")
                return False
            
            # Cleanup test data
            cursor.execute("DELETE FROM bow_setups WHERE id = ?", (test_setup_id,))
            conn.commit()
            print("✅ Test cleanup successful")
            
        except Exception as e:
            print(f"❌ Database operation failed: {e}")
            return False
        
        conn.close()
        print("✅ User database test passed")
        return True
        
    except Exception as e:
        print(f"❌ User database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints if available."""
    print("\n🔍 Testing API Endpoints")
    print("=" * 40)
    
    try:
        import requests
        
        # Test health endpoint
        health_url = "http://localhost:5000/api/health"
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                print("✅ API health endpoint responding")
            else:
                print(f"⚠️  API health endpoint returned {response.status_code}")
        except Exception as e:
            print(f"❌ API health endpoint not reachable: {e}")
            return False
        
        # Test bow-setups endpoint (will require auth, but we can check if it's there)
        bow_setups_url = "http://localhost:5000/api/bow-setups"
        try:
            response = requests.get(bow_setups_url, timeout=5)
            # We expect 401 (unauthorized) if endpoint exists
            if response.status_code in [401, 403]:
                print("✅ Bow setups endpoint exists (requires auth)")
            elif response.status_code == 200:
                print("✅ Bow setups endpoint responding")
            else:
                print(f"⚠️  Bow setups endpoint returned {response.status_code}")
        except Exception as e:
            print(f"❌ Bow setups endpoint not reachable: {e}")
            return False
            
        return True
        
    except ImportError:
        print("⚠️  Requests library not available, skipping API tests")
        return True

def test_environment_variables():
    """Test critical environment variables."""
    print("\n🔍 Testing Environment Variables")
    print("=" * 40)
    
    env_vars = {
        'SECRET_KEY': os.environ.get('SECRET_KEY', ''),
        'GOOGLE_CLIENT_SECRET': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
        'NUXT_PUBLIC_GOOGLE_CLIENT_ID': os.environ.get('NUXT_PUBLIC_GOOGLE_CLIENT_ID', ''),
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'not-set'),
    }
    
    issues = []
    
    for var_name, value in env_vars.items():
        if not value or value in ['not-set', 'change-this-secret-key-in-production']:
            issues.append(f"❌ {var_name}: Not set or using default")
        else:
            print(f"✅ {var_name}: Set ({len(value)} characters)")
    
    if issues:
        for issue in issues:
            print(issue)
        print("⚠️  Some environment variables may cause authentication issues")
    else:
        print("✅ All environment variables properly set")
    
    return len(issues) == 0

def main():
    """Run all tests."""
    print("🧪 ArrowTuner Bow Saving Functionality Test")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: User database
    test_results.append(("User Database", test_user_database_connection()))
    
    # Test 2: API endpoints
    test_results.append(("API Endpoints", test_api_endpoints()))
    
    # Test 3: Environment variables
    test_results.append(("Environment", test_environment_variables()))
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bow saving functionality should work correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the issues above.")
        
        # Provide specific guidance
        print("\n🔧 Troubleshooting Guidance:")
        
        for test_name, result in test_results:
            if not result:
                if test_name == "User Database":
                    print("   • User database issue: Check if user_data.db exists and has correct schema")
                    print("   • Run: python -c \"from user_database import UserDatabase; UserDatabase()\"")
                elif test_name == "API Endpoints":
                    print("   • API not responding: Check if Flask server is running")
                    print("   • Run: python api.py")
                elif test_name == "Environment":
                    print("   • Environment variables missing: Check .env file")
                    print("   • Ensure SECRET_KEY and Google OAuth credentials are set")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)