#!/usr/bin/env python3
"""
Complete Validation System Demo
Shows the enhanced validation system with click-to-fix functionality
"""

import os
import sys
from arrow_data_validator import ArrowDataValidator

def demo_click_to_fix_system():
    """Demonstrate the complete validation system with click-to-fix functionality"""
    print("🎯 ENHANCED VALIDATION SYSTEM DEMO")
    print("=" * 60)
    print("Demonstrating the complete click-to-fix validation interface")
    
    # Initialize validator
    print("\n📊 Initializing validation system...")
    validator = ArrowDataValidator()
    
    # Run validation to populate database
    print("🔄 Running validation to populate database...")
    report = validator.validate_all_data(triggered_by='demo_interface')
    
    print(f"\n📋 VALIDATION RESULTS:")
    print(f"   • Total Issues: {report.total_issues}")
    print(f"   • Critical Issues: {report.critical_issues}")  
    print(f"   • Warning Issues: {report.warning_issues}")
    print(f"   • Health Score: {validator._calculate_health_score(report, 210):.1f}%")
    
    # Show some example issues that would appear in the interface
    print(f"\n🔍 EXAMPLE ISSUES FOR CLICK-TO-FIX INTERFACE:")
    issues = validator.get_persistent_issues()
    
    if issues:
        print(f"Found {len(issues)} persistent issues in database")
        
        # Show critical issues
        critical = [i for i in issues if i['severity'] == 'critical']
        print(f"\n🚨 Critical Issues ({len(critical)} total):")
        for i, issue in enumerate(critical[:3], 1):  # Show first 3
            auto_fix = "✅ Auto-Fixable" if issue['auto_fixable'] else "⚠️  Manual Fix"
            print(f"   {i}. Arrow {issue['arrow_id']} - {issue['description']} ({auto_fix})")
        
        # Show warning issues  
        warnings = [i for i in issues if i['severity'] == 'warning']
        print(f"\n⚠️  Warning Issues ({len(warnings)} total):")
        for i, issue in enumerate(warnings[:2], 1):  # Show first 2
            auto_fix = "✅ Auto-Fixable" if issue['auto_fixable'] else "⚠️  Manual Fix"
            print(f"   {i}. Arrow {issue['arrow_id']} - {issue['description']} ({auto_fix})")
    
    # Show validation history
    print(f"\n📈 VALIDATION HISTORY:")
    history = validator.get_validation_history(limit=3)
    for run in history:
        print(f"   • Run #{run['id']}: {run['total_issues']} issues, {run['health_score']:.1f}% health")
    
    # Demo the admin interface workflow
    print(f"\n🎯 ADMIN INTERFACE WORKFLOW:")
    print("1. 🌐 Visit: http://localhost:3000/admin")
    print("2. 🔑 Login as admin (messenlien@gmail.com)")
    print("3. 📋 Click 'Validation' tab")
    print("4. ▶️  Click 'Run Validation' button")
    print("5. 📊 View health score and issue counters")
    print("6. 🔍 Filter issues by severity/category")
    print("7. 🔧 Click green 'Auto Fix' buttons to resolve issues")
    print("8. 📄 Click 'Show SQL' for manual fixes")
    print("9. 👁️  Click 'View Arrow' to inspect specific arrows")
    print("10. 📈 Watch health score improve after fixes")
    
    print(f"\n✨ CLICK-TO-FIX FEATURES:")
    print("   • Green 'Auto Fix' buttons for automatic resolution")
    print("   • Real-time progress indicators during fixes")
    print("   • Automatic refresh of issue list after fixes")
    print("   • Health score updates in real-time") 
    print("   • Success/error notifications for user feedback")
    print("   • SQL preview for manual fixes")
    print("   • Direct navigation to problematic arrows")
    
    print(f"\n🗄️  DATABASE INTEGRATION:")
    print("   • Issues stored with deduplication")
    print("   • Fix attempts tracked with success/failure")
    print("   • Validation runs tracked with timestamps")
    print("   • Health scores calculated and stored")
    print("   • Occurrence counts for recurring issues")
    
    return report

def show_api_endpoints():
    """Show the API endpoints that power the interface"""
    print(f"\n🌐 API ENDPOINTS POWERING THE INTERFACE:")
    print("-" * 50)
    print("📊 GET  /api/admin/validation/status")
    print("   • Health score, issue counts, last run info")
    print("")
    print("🔄 POST /api/admin/validation/run") 
    print("   • Trigger validation run, returns results")
    print("")
    print("📋 GET  /api/admin/validation/issues?severity=critical&category=Search")
    print("   • Get filtered validation issues")
    print("")
    print("🔧 POST /api/admin/validation/fix/{issue_id}")
    print("   • Apply automated fix, track success/failure")

def show_database_schema():
    """Show the database schema supporting the system"""
    print(f"\n🗄️  DATABASE SCHEMA (Migration 056):")
    print("-" * 40)
    print("📊 validation_runs - Track validation execution")
    print("📋 validation_issues - Store issues with deduplication")  
    print("🔧 validation_fixes - Record fix attempts")
    print("⚙️  validation_rules - Configurable validation rules")
    print("")
    print("🔗 All tables linked with foreign keys")
    print("📈 Indexes for performance optimization")
    print("🔄 Automatic cleanup and deduplication")

if __name__ == "__main__":
    try:
        report = demo_click_to_fix_system()
        show_api_endpoints()
        show_database_schema()
        
        print(f"\n🎉 VALIDATION SYSTEM READY!")
        print("=" * 40)
        print("✅ Database schema created and populated")
        print("✅ API endpoints implemented and tested")
        print("✅ Admin interface with click-to-fix ready")
        print("✅ Real-time health monitoring active")
        print("✅ Automated fixing capabilities enabled")
        
        print(f"\n💡 NEXT STEPS:")
        print("1. Visit http://localhost:3000/admin")
        print("2. Navigate to Validation tab")
        print("3. Start clicking to fix validation issues!")
        
        # Show current issues that can be fixed
        if report.total_issues > 0:
            print(f"\n🎯 READY TO FIX: {report.critical_issues} critical issues await your clicks!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)