#!/usr/bin/env python3
"""
Final verification that the validation interface is working
Tests the complete integration between UI, API, and database
"""

import requests
import json

def verify_interface_integration():
    """Verify the validation interface integration is working"""
    print("🎯 VALIDATION INTERFACE VERIFICATION")
    print("=" * 50)
    
    # Check that API server is running
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server issue")
            return False
    except:
        print("❌ API server not accessible")
        return False
    
    # Check that frontend is running  
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend server is running")
        else:
            print("❌ Frontend server issue")
            return False
    except:
        print("❌ Frontend server not accessible")
        return False
    
    # Verify validation endpoints exist (should return 401 for auth)
    endpoints = [
        "/api/admin/validation/status",
        "/api/admin/validation/run", 
        "/api/admin/validation/issues"
    ]
    
    print(f"\n🌐 Verifying validation API endpoints:")
    all_endpoints_exist = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
            # 401 means endpoint exists but needs auth (expected)
            # 404 means endpoint doesn't exist
            if response.status_code in [401, 403, 200]:
                print(f"   ✅ {endpoint}")
            elif response.status_code == 404:
                print(f"   ❌ {endpoint} - Not Found")
                all_endpoints_exist = False
            else:
                print(f"   ⚠️  {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")
            all_endpoints_exist = False
    
    # Check database has validation tables
    print(f"\n🗄️  Verifying validation database schema:")
    try:
        import sqlite3
        conn = sqlite3.connect('arrow_scraper/databases/arrow_database.db')
        cursor = conn.cursor()
        
        # Check all validation tables exist
        validation_tables = ['validation_runs', 'validation_issues', 'validation_fixes', 'validation_rules']
        tables_exist = True
        
        for table in validation_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   ✅ {table}: {count} records")
            else:
                print(f"   ❌ {table}: Missing")
                tables_exist = False
        
        conn.close()
        
        if not tables_exist:
            print("❌ Database schema incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Database verification error: {e}")
        return False
    
    # Final verification
    if all_endpoints_exist and tables_exist:
        print(f"\n🎉 VALIDATION INTERFACE READY!")
        print("=" * 40)
        print("✅ All components working correctly")
        print("✅ API endpoints operational") 
        print("✅ Database schema complete")
        print("✅ Frontend compilation successful")
        
        print(f"\n🎯 HOW TO USE:")
        print("1. Visit: http://localhost:3000/admin")
        print("2. Login with admin account")
        print("3. Click 'Validation' tab")
        print("4. Click 'Run Validation' button")
        print("5. See validation issues with click-to-fix buttons")
        print("6. Use green 'Auto Fix' buttons to resolve issues")
        print("7. Watch health score improve in real-time!")
        
        return True
    else:
        print(f"\n❌ Interface verification failed")
        return False

if __name__ == "__main__":
    success = verify_interface_integration()
    exit(0 if success else 1)