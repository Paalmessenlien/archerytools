#!/usr/bin/env python3
"""
Detailed Arrow Validation Issues Report
Shows all warning issues with specific arrow details and problems
"""

import sqlite3
import json
from arrow_data_validator import ArrowDataValidator
from arrow_scraper.unified_database import UnifiedDatabase

def display_detailed_issues():
    """Display all validation issues with detailed arrow information"""
    
    print("🏹 DETAILED ARROW VALIDATION ISSUES REPORT")
    print("=" * 60)
    
    # Run validation
    validator = ArrowDataValidator()
    report = validator.validate_all_data()
    
    if not validator.validation_issues:
        print("✅ No issues found - database is in excellent condition!")
        return
    
    # Group issues by category
    issues_by_category = {}
    for issue in validator.validation_issues:
        if issue.category not in issues_by_category:
            issues_by_category[issue.category] = []
        issues_by_category[issue.category].append(issue)
    
    # Display issues by category
    for category, issues in issues_by_category.items():
        print(f"\n📋 {category.upper()} ({len(issues)} issues)")
        print("-" * 50)
        
        for i, issue in enumerate(issues, 1):
            severity_icon = "🚨" if issue.severity == "critical" else "⚠️" if issue.severity == "warning" else "ℹ️"
            
            print(f"\n{severity_icon} Issue #{i} ({issue.severity.upper()})")
            print(f"  Arrow ID: {issue.arrow_id}")
            print(f"  Manufacturer: {issue.manufacturer}")
            print(f"  Model: {issue.model_name}")
            print(f"  Field: {issue.field}")
            print(f"  Problem: {issue.issue}")
            print(f"  Current Value: {issue.current_value}")
            print(f"  Suggested Fix: {issue.suggested_fix}")
            if issue.sql_fix:
                print(f"  SQL Fix: {issue.sql_fix}")
    
    # Summary statistics
    print(f"\n📊 SUMMARY STATISTICS")
    print("=" * 30)
    print(f"Total Issues: {len(validator.validation_issues)}")
    
    severity_counts = {}
    for issue in validator.validation_issues:
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
    
    for severity, count in severity_counts.items():
        icon = "🚨" if severity == "critical" else "⚠️" if severity == "warning" else "ℹ️"
        print(f"{icon} {severity.title()}: {count}")

def display_spine_range_issues():
    """Display specific details about spine range validation issues"""
    
    print("\n🎯 SPINE RANGE VALIDATION DETAILS")
    print("=" * 40)
    
    db = UnifiedDatabase()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get spine issues with full details
        cursor.execute('''
            SELECT 
                ss.id as spine_spec_id,
                ss.arrow_id,
                a.manufacturer, 
                a.model_name, 
                a.material,
                ss.spine,
                ss.length_options
            FROM spine_specifications ss
            JOIN arrows a ON ss.arrow_id = a.id
            WHERE 
                (a.material = 'Wood' AND (ss.spine < 25 OR ss.spine > 85)) OR
                (a.material != 'Wood' AND (ss.spine < 150 OR ss.spine > 2000))
            ORDER BY a.manufacturer, a.model_name, ss.spine
        ''')
        
        spine_issues = cursor.fetchall()
        
        if not spine_issues:
            print("✅ No spine range issues found!")
            return
        
        print(f"Found {len(spine_issues)} spine range issues:\n")
        
        for i, row in enumerate(spine_issues, 1):
            material = row['material'] or 'Unknown'
            expected_range = "25-85 lbs" if material == 'Wood' else "150-2000"
            
            print(f"⚠️  Issue #{i}")
            print(f"   Spine Spec ID: {row['spine_spec_id']}")
            print(f"   Arrow ID: {row['arrow_id']}")
            print(f"   Manufacturer: {row['manufacturer']}")
            print(f"   Model: {row['model_name']}")
            print(f"   Material: {material}")
            print(f"   Current Spine: {row['spine']}")
            print(f"   Expected Range: {expected_range}")
            print(f"   Length Options: {row['length_options']}")
            print()

if __name__ == "__main__":
    display_detailed_issues()
    display_spine_range_issues()