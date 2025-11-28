#!/usr/bin/env python3

import json
import sys
sys.path.append('arrow_scraper')
from normalize_materials import normalize_material

# Load the Easton file with X10
with open('arrow_scraper/data/processed/Easton_Archery_000_023.json', 'r') as f:
    data = json.load(f)

print("Checking arrows in Easton_Archery_000_023.json:")
arrows_to_fix = []

for arrow in data.get('arrows', []):
    model = arrow.get('model_name', '')
    material = arrow.get('material', '')
    description = arrow.get('description', '')
    
    # Check current vs new material classification
    current_material = material
    new_material = normalize_material(material, description)
    
    if current_material != new_material:
        arrows_to_fix.append({
            'model': model,
            'current': current_material,
            'new': new_material,
            'description_sample': description[:100] + '...' if description else 'None'
        })

print(f"\nFound {len(arrows_to_fix)} arrows that need material correction:")
print("=" * 80)
for arrow in arrows_to_fix:
    print(f"Model: {arrow['model']}")
    print(f"Current: {arrow['current']} -> New: {arrow['new']}")
    print(f"Description: {arrow['description_sample']}")
    print("-" * 40)

# Now let's test specifically on the X10 description
x10_found = False
for arrow in data.get('arrows', []):
    if 'X10' in arrow.get('model_name', ''):
        x10_found = True
        model = arrow.get('model_name', '')
        material = arrow.get('material', '')
        description = arrow.get('description', '')
        
        print(f"\n🎯 Found X10 Arrow: {model}")
        print(f"Current Material: {material}")
        print(f"Description contains aluminum core: {'aluminum core' in description.lower()}")
        
        new_material = normalize_material(material, description)
        print(f"Updated Material: {new_material}")
        
        if material != new_material:
            print("✅ CORRECTION NEEDED!")
        else:
            print("❌ No change needed")

if not x10_found:
    print("\n❌ No X10 arrows found in this file")