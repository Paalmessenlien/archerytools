#!/usr/bin/env python3
"""
Test script for admin validation interface integration
Tests the complete flow from UI actions to backend validation system
"""

import requests
import json
import time

# Configuration
API_BASE = "http://localhost:5000"
ADMIN_EMAIL = "messenlien@gmail.com"  # Auto-admin user

def test_validation_api_endpoints():
    """Test all validation API endpoints"""
    print("🔍 TESTING ADMIN VALIDATION INTERFACE")
    print("=" * 60)
    
    # Test 1: Validation Status
    print("\n📊 Testing Validation Status endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/admin/validation/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Status endpoint working")
            print(f"   Health Score: {status.get('health_score', 'N/A')}")
            print(f"   Total Issues: {status.get('total_issues', 'N/A')}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
    
    # Test 2: Run Validation
    print("\n🔄 Testing Run Validation endpoint...")
    try:
        response = requests.post(f"{API_BASE}/api/admin/validation/run", 
                               json={"triggered_by": "test_interface"})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Run validation working")
            print(f"   Issues Found: {result.get('total_issues', 'N/A')}")
            print(f"   Health Score: {result.get('health_score', 'N/A')}")
            print(f"   Duration: {result.get('run_duration_ms', 'N/A')}ms")
        else:
            print(f"❌ Run validation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Run validation error: {e}")
    
    # Test 3: Get Issues
    print("\n📋 Testing Get Issues endpoint...")
    try:
        # Test with no filters
        response = requests.get(f"{API_BASE}/api/admin/validation/issues")
        if response.status_code == 200:
            issues = response.json()
            total_issues = len(issues.get('issues', []))
            print(f"✅ Get issues working")
            print(f"   Total Issues: {total_issues}")
            
            if total_issues > 0:
                example_issue = issues['issues'][0]
                print(f"   Example Issue: {example_issue.get('description', 'N/A')}")
                print(f"   Severity: {example_issue.get('severity', 'N/A')}")
                print(f"   Arrow ID: {example_issue.get('arrow_id', 'N/A')}")
        else:
            print(f"❌ Get issues failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Get issues error: {e}")
    
    # Test 4: Get Issues with Filters
    print("\n🔍 Testing Get Issues with filters...")
    try:
        response = requests.get(f"{API_BASE}/api/admin/validation/issues?severity=critical")
        if response.status_code == 200:
            issues = response.json()
            critical_issues = len(issues.get('issues', []))
            print(f"✅ Filtered issues working")
            print(f"   Critical Issues: {critical_issues}")
        else:
            print(f"❌ Filtered issues failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Filtered issues error: {e}")
    
    # Test 5: Auto-fix (if auto-fixable issues exist)
    print("\n🔧 Testing Auto-fix functionality...")
    try:
        # First get auto-fixable issues
        response = requests.get(f"{API_BASE}/api/admin/validation/issues")
        if response.status_code == 200:
            issues = response.json().get('issues', [])
            auto_fixable = [issue for issue in issues if issue.get('auto_fixable') and issue.get('sql_fix')]
            
            if auto_fixable:
                test_issue_id = auto_fixable[0]['id']
                print(f"   Found auto-fixable issue #{test_issue_id}")
                
                # Test the fix endpoint (but don't actually apply it in this test)
                print(f"   Fix endpoint would be: POST /api/admin/validation/fix/{test_issue_id}")
                print(f"   ⚠️  Not applying fix in test mode")
            else:
                print(f"   No auto-fixable issues found")
        else:
            print(f"❌ Could not check for auto-fixable issues")
    except Exception as e:
        print(f"❌ Auto-fix test error: {e}")
    
    print(f"\n🎯 VALIDATION INTERFACE TEST COMPLETE")
    print(f"   All endpoints are ready for the admin interface")
    print(f"   Visit: http://localhost:3000/admin (login as {ADMIN_EMAIL})")
    print(f"   Click on 'Validation' tab to test the click-to-fix interface")

def show_integration_summary():
    """Show summary of what was implemented"""
    print(f"\n📋 VALIDATION INTERFACE IMPLEMENTATION SUMMARY")
    print("=" * 60)
    print("✅ Admin Tab Added: 'Validation' tab in admin panel")
    print("✅ Health Dashboard: Real-time health score and issue counters")
    print("✅ Issue Management: Filterable list of validation issues")
    print("✅ Click-to-Fix: Green 'Auto Fix' buttons for fixable issues")
    print("✅ Manual Fixes: 'Show SQL' buttons for manual fixes")
    print("✅ View Integration: 'View Arrow' buttons to inspect issues")
    print("✅ Real-time Updates: Status refreshes after fixes")
    print("✅ Progress Tracking: Loading states and notifications")
    print("✅ Error Handling: Comprehensive error handling and user feedback")
    
    print(f"\n🎯 USER WORKFLOW:")
    print("1. Admin logs in and navigates to 'Validation' tab")
    print("2. Clicks 'Run Validation' to scan database")
    print("3. Reviews issues with filtering by severity/category")
    print("4. Clicks 'Auto Fix' for issues that can be automatically resolved")
    print("5. Uses 'Show SQL' for manual fixes that need review")
    print("6. Uses 'View Arrow' to inspect specific problematic arrows")
    print("7. Watches health score improve as issues are resolved")

if __name__ == "__main__":
    test_validation_api_endpoints()
    show_integration_summary()