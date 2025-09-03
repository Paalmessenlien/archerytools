#!/usr/bin/env python3
"""
Data Formatting Issues Report
Shows specific examples of problematic data formatting that breaks calculator logic
"""

from arrow_data_validator import ArrowDataValidator

def show_formatting_examples():
    """Show examples of data formatting issues"""
    
    print("🔧 DATA FORMATTING ISSUES EXAMPLES")
    print("=" * 50)
    
    validator = ArrowDataValidator()
    report = validator.validate_all_data()
    
    # Filter for formatting issues only
    formatting_issues = [issue for issue in validator.validation_issues if issue.category == "Data Field Formatting"]
    
    print(f"Found {len(formatting_issues)} data formatting issues\n")
    
    # Show first 20 examples by issue type
    length_issues = [issue for issue in formatting_issues if issue.field == "length_options"]
    diameter_issues = [issue for issue in formatting_issues if issue.field == "outer_diameter"]
    weight_issues = [issue for issue in formatting_issues if issue.field == "gpi_weight"]
    
    if length_issues:
        print("📏 LENGTH_OPTIONS FORMATTING ISSUES (showing first 10):")
        print("-" * 45)
        for i, issue in enumerate(length_issues[:10], 1):
            print(f"{i}. Arrow ID {issue.arrow_id} ({issue.manufacturer} {issue.model_name})")
            print(f"   Problem: {issue.issue}")
            print(f"   Current: {issue.current_value}")
            print()
    
    if diameter_issues:
        print("\n📐 OUTER_DIAMETER ISSUES (showing first 10):")
        print("-" * 35)
        for i, issue in enumerate(diameter_issues[:10], 1):
            print(f"{i}. Arrow ID {issue.arrow_id} ({issue.manufacturer} {issue.model_name})")
            print(f"   Problem: {issue.issue}")
            print(f"   Current: {issue.current_value}")
            print()
    
    if weight_issues:
        print("\n⚖️  GPI_WEIGHT ISSUES (showing first 10):")
        print("-" * 30)
        for i, issue in enumerate(weight_issues[:10], 1):
            print(f"{i}. Arrow ID {issue.arrow_id} ({issue.manufacturer} {issue.model_name})")
            print(f"   Problem: {issue.issue}")
            print(f"   Current: {issue.current_value}")
            print()
    
    # Summary by field type
    print(f"📊 FORMATTING ISSUES SUMMARY:")
    print(f"   Length Options: {len(length_issues)} issues")
    print(f"   Outer Diameter: {len(diameter_issues)} issues") 
    print(f"   GPI Weight: {len(weight_issues)} issues")
    print(f"   Total: {len(formatting_issues)} issues")

if __name__ == "__main__":
    show_formatting_examples()