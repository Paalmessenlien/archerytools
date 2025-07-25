#!/usr/bin/env python3
"""
Material Normalization for Arrow Database
Standardizes arrow material values to the four standard types:
- Carbon
- Carbon / Aluminum  
- Aluminum
- Wood
"""

import sqlite3
import re
from typing import Optional

def normalize_material(material: Optional[str], description: Optional[str] = None) -> str:
    """
    Normalize arrow material to one of the four standard types.
    
    Args:
        material: Raw material string from scraper
        description: Arrow description text (optional, for enhanced detection)
        
    Returns:
        Normalized material: "Carbon", "Carbon / Aluminum", "Aluminum", or "Wood"
    """
    # Combine material and description for analysis
    combined_text = ""
    
    if material:
        combined_text += material
    
    if description:
        combined_text += " " + description
    
    if not combined_text.strip():
        return "Carbon"  # Default for null/empty materials
    
    # Convert to lowercase for analysis
    material_lower = combined_text.lower()
    
    # Wood materials (check first - most specific)
    # Use word boundaries and exclude cosmetic descriptions
    
    # First check for carbon/aluminum indicators - if present, not wood
    if any(keyword in material_lower for keyword in ['carbon', 'aluminum', 'alloy', '100% carbon']):
        # Skip wood classification if it's clearly carbon/aluminum
        pass
    else:
        # Check for wood patterns but exclude cosmetic descriptions
        wood_patterns = [
            r'\bwood\b', r'\bcedar\b', r'\bpine\b', r'\boak\b', r'\bash\b', r'\bbirch\b', 
            r'\bhickory\b', r'\bbamboo\b', r'\bdouglas fir\b', r'\bsitka spruce\b', 
            r'\bport orford cedar\b'
        ]
        
        # Exclude cosmetic descriptions
        cosmetic_exclusions = [
            r'bamboo look', r'wood-grained', r'wood grain', r'cedar look', 
            r'wood appearance', r'wooden look', r'wood finish'
        ]
        
        # Check if it matches wood patterns but not cosmetic descriptions
        has_wood_pattern = any(re.search(pattern, material_lower) for pattern in wood_patterns)
        has_cosmetic_exclusion = any(re.search(exclusion, material_lower) for exclusion in cosmetic_exclusions)
        
        if has_wood_pattern and not has_cosmetic_exclusion:
            return "Wood"
    
    # Carbon/Aluminum composites (check before pure carbon)
    carbon_aluminum_keywords = [
        'carbon core with 7075 alloy jacket',
        'carbon-core with 7075-alloy metal jacket', 
        'carbon core with aluminum jacket',
        'carbon with aluminum jacket',
        'carbon fiber bonded to a 7075 alloy core',
        'carbon fiber bonded to a precision 7075 alloy core',
        'carbon and 7075 aluminum composited',
        'carbon and aluminum',
        'carbon fiber on a precision, thin-wall aluminum core',  # Easton X10 pattern
        'carbon fiber on aluminum core',  # Variations of the X10 pattern
        'carbon fiber on a aluminum core',
        'carbon on aluminum core',
        'carbon fiber with aluminum core',
        'fmj construction',  # FMJ typically means carbon core with aluminum jacket
        'fmj'
    ]
    
    if any(keyword in material_lower for keyword in carbon_aluminum_keywords):
        return "Carbon / Aluminum"
    
    # Pure Aluminum materials  
    aluminum_keywords = ['aluminum', 'aluminium', 'alloy', 'enaw', '7075', '7001']
    
    # Check if it's pure aluminum (has aluminum keywords but no carbon keywords)
    has_aluminum = any(keyword in material_lower for keyword in aluminum_keywords)
    has_carbon = any(keyword in material_lower for keyword in ['carbon', 'carb'])
    
    if has_aluminum and not has_carbon:
        return "Aluminum"
    
    # Carbon materials (default for most arrows)
    # Most modern arrows are carbon unless specifically mentioned otherwise
    return "Carbon"

def analyze_current_materials():
    """Analyze current materials in database and show normalization plan"""
    
    conn = sqlite3.connect('arrow_database.db')
    cursor = conn.cursor()
    
    # Get all arrows with materials and descriptions to analyze properly
    cursor.execute('SELECT material, description, COUNT(*) FROM arrows GROUP BY material, description ORDER BY COUNT(*) DESC')
    arrows = cursor.fetchall()
    
    print("Material Normalization Analysis:")
    print("=" * 80)
    print(f"{'Current Material':<25} {'Count':<6} {'→ Normalized':<20} {'Sample Description'}")
    print("-" * 80)
    
    normalization_counts = {"Carbon": 0, "Carbon / Aluminum": 0, "Aluminum": 0, "Wood": 0}
    material_summary = {}
    
    for material, description, count in arrows:
        normalized = normalize_material(material, description)
        normalization_counts[normalized] += count
        
        # Track changes for summary
        if material not in material_summary:
            material_summary[material] = {"count": 0, "normalized": normalized, "sample_desc": description}
        material_summary[material]["count"] += count
        
        # Truncate long descriptions for display
        sample_desc = description[:30] + "..." if description and len(description) > 30 else (description or "")
        display_material = material if material and len(material) <= 20 else (material[:17] + "..." if material else "NULL")
        
        # Only show first few entries per material type to avoid clutter
        if material_summary[material]["count"] <= count:  # First occurrence of this material
            print(f"{display_material:<25} {count:<6} → {normalized:<20} {sample_desc}")
    
    print("-" * 80)
    print("Summary by original material:")
    for material, info in material_summary.items():
        display_material = material if material and len(material) <= 30 else (material[:27] + "..." if material else "NULL")
        print(f"  {display_material:<35} {info['count']:<6} → {info['normalized']}")
    
    print("-" * 80)
    print("Final counts after normalization:")
    for norm_material, count in normalization_counts.items():
        print(f"  {norm_material}: {count} arrows")
    
    conn.close()
    return normalization_counts

def update_database_materials():
    """Update all materials in the database to normalized values"""
    
    conn = sqlite3.connect('arrow_database.db')
    cursor = conn.cursor()
    
    # Get all arrows with their current materials and descriptions
    cursor.execute('SELECT id, material, description FROM arrows')
    arrows = cursor.fetchall()
    
    updates = []
    for arrow_id, current_material, description in arrows:
        normalized_material = normalize_material(current_material, description)
        if current_material != normalized_material:
            updates.append((normalized_material, arrow_id))
    
    print(f"Updating {len(updates)} arrows with normalized materials...")
    
    # Update materials
    cursor.executemany('UPDATE arrows SET material = ? WHERE id = ?', updates)
    
    # Commit changes
    conn.commit()
    
    print(f"✅ Updated {len(updates)} arrow materials")
    
    # Verify final state
    cursor.execute('SELECT DISTINCT material, COUNT(*) FROM arrows GROUP BY material ORDER BY material')
    final_materials = cursor.fetchall()
    
    print("\nFinal material distribution:")
    for material, count in final_materials:
        print(f"  {material}: {count} arrows")
    
    conn.close()

if __name__ == "__main__":
    print("🎯 Arrow Material Normalization Tool")
    print("=" * 50)
    
    # Analyze current state
    analyze_current_materials()
    
    print("\n" + "=" * 50)
    choice = input("Proceed with material normalization? (y/N): ").lower().strip()
    
    if choice == 'y':
        update_database_materials()
        print("\n✅ Material normalization complete!")
    else:
        print("❌ Material normalization cancelled.")