#!/usr/bin/env python3
"""
Fix component categories to match existing component database schema
Maps our scraper categories to the existing system categories
"""

import json
from pathlib import Path

def fix_component_categories(input_file: str, output_file: str = None):
    """Fix component categories to match existing schema"""
    
    if not output_file:
        output_file = input_file.replace('.json', '_fixed.json')
    
    # Category mapping
    category_mapping = {
        'glue_points': 'points',  # Glue-on points are arrow points
        'screw_points': 'points', # Screw-in points are also arrow points
        'inserts': 'inserts',     # Direct match
        'nocks': 'nocks'          # Direct match
    }
    
    print(f"🔧 Fixing categories in {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Fix top-level categories
    fixed_categories = {}
    for old_cat, count in data.get('categories', {}).items():
        new_cat = category_mapping.get(old_cat, old_cat)
        fixed_categories[new_cat] = count
    
    data['categories'] = fixed_categories
    
    # Fix individual component categories
    fixed_count = 0
    for component in data.get('components', []):
        old_cat = component.get('category')
        if old_cat in category_mapping:
            component['category'] = category_mapping[old_cat]
            fixed_count += 1
    
    # Set component_type to match the expected schema
    data['component_type'] = 'mixed'  # Since we have multiple types
    
    print(f"   ✅ Fixed {fixed_count} component categories")
    print(f"   📊 Category mapping:")
    for old_cat, new_cat in category_mapping.items():
        if old_cat in data['categories']:
            print(f"      {old_cat} → {new_cat} ({data['categories'][new_cat]} components)")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"   💾 Saved fixed file: {output_file}")
    return output_file

if __name__ == "__main__":
    input_file = "data/processed/components/tophat_archery_components_20250801_213629.json"
    fixed_file = fix_component_categories(input_file)
    print(f"\n🎯 Component categories fixed! Use this file for import:")
    print(f"   {fixed_file}")