#!/usr/bin/env python3
"""
Parse wood arrow specifications from Wood arrows.txt and create database entries
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any

def parse_wood_arrow_chart() -> Dict[str, Any]:
    """Parse the wood arrow chart data and create structured database entries"""
    
    # Wood arrow data based on the chart from Wood arrows.txt
    wood_arrow_specs = [
        {
            "spine_range": "25-30",
            "diameter_inches": "5/16\"",
            "diameter_mm": 7.9,
            "length_range": "28\"-30\"",
            "wood_types": ["Cedar", "Pine"],
            "best_for": "Youth bows (20-30#)",
            "point_weight_range": "75-100gr"
        },
        {
            "spine_range": "30-35", 
            "diameter_inches": "5/16\" or 11/32\"",
            "diameter_mm": 8.3,
            "length_range": "28\"-31\"",
            "wood_types": ["Cedar", "Port Orford Cedar"],
            "best_for": "Light longbows (25-35#)",
            "point_weight_range": "100-125gr"
        },
        {
            "spine_range": "35-40",
            "diameter_inches": "11/32\"",
            "diameter_mm": 8.7,
            "length_range": "29\"-31\"",
            "wood_types": ["Cedar", "Douglas Fir"],
            "best_for": "Recurve (30-40#)",
            "point_weight_range": "125-150gr"
        },
        {
            "spine_range": "40-45",
            "diameter_inches": "11/32\" or 23/64\"",
            "diameter_mm": 9.0,
            "length_range": "30\"-32\"",
            "wood_types": ["Port Orford Cedar", "Cedar"],
            "best_for": "Hunting longbows (35-45#)",
            "point_weight_range": "150-175gr"
        },
        {
            "spine_range": "45-50",
            "diameter_inches": "23/64\"",
            "diameter_mm": 9.1,
            "length_range": "30\"-32\"",
            "wood_types": ["Ash", "Hickory"],
            "best_for": "Heavy recurves (40-50#)",
            "point_weight_range": "175-200gr"
        },
        {
            "spine_range": "50-55",
            "diameter_inches": "23/64\" or 3/8\"",
            "diameter_mm": 9.3,
            "length_range": "31\"-33\"",
            "wood_types": ["Ash", "Birch"],
            "best_for": "Warbows (50-60#)",
            "point_weight_range": "200-250gr"
        },
        {
            "spine_range": "55-60",
            "diameter_inches": "3/8\"",
            "diameter_mm": 9.5,
            "length_range": "32\"-34\"",
            "wood_types": ["Hickory", "Oak"],
            "best_for": "Medieval/war bows (55-70#)",
            "point_weight_range": "250-300gr"
        },
        {
            "spine_range": "60+",
            "diameter_inches": "3/8\" or thicker",
            "diameter_mm": 9.7,
            "length_range": "32\"-34\"",
            "wood_types": ["Hickory", "Bamboo"],
            "best_for": "Extreme heavy bows (70#+)",
            "point_weight_range": "300gr+"
        }
    ]
    
    return {
        "manufacturer": "Traditional Wood Arrows",
        "arrows": create_wood_arrow_entries(wood_arrow_specs),
        "extraction_timestamp": datetime.now().isoformat(),
        "source": "Wood arrows.txt chart",
        "notes": [
            "Spine vs Draw Weight: A 30-35# spine arrow bends correctly for a 30-35# bow at 28\"",
            "Add ±5# spine per inch over/under 28\" draw length",
            "Heavier points (150gr+) weaken spine (use stiffer spine arrow)",
            "Longer arrows act weaker (require stiffer spine)",
            "Wood types: Cedar (lightweight), Port Orford Cedar (durable), Ash/Hickory (heavy)"
        ]
    }

def create_wood_arrow_entries(wood_specs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create individual arrow entries for each wood type and spine range"""
    
    arrows = []
    
    for spec in wood_specs:
        # Parse spine range
        spine_parts = spec["spine_range"].replace("+", "").split("-")
        min_spine = int(spine_parts[0])
        max_spine = int(spine_parts[-1]) if len(spine_parts) > 1 else min_spine + 5
        
        # Parse point weight range
        point_weight_parts = spec["point_weight_range"].replace("gr", "").replace("+", "").split("-")
        min_point_weight = int(point_weight_parts[0])
        max_point_weight = int(point_weight_parts[-1]) if len(point_weight_parts) > 1 else min_point_weight + 25
        
        # Create an entry for each wood type in this spine range
        for wood_type in spec["wood_types"]:
            arrow_entry = {
                "model_name": f"{wood_type} Traditional Wood Arrow ({spec['spine_range']}#)",
                "material": f"{wood_type} Wood",
                "arrow_type": "Wood",
                "diameter": spec["diameter_mm"],
                "gpi_weight": estimate_gpi_for_wood(wood_type, spec["diameter_mm"]),
                "spine_options": f"{min_spine}-{max_spine}",
                "min_spine": min_spine,
                "max_spine": max_spine,
                "length_options": spec["length_range"],
                "recommended_use": spec["best_for"],
                "price_range": "$15-25",  # Typical wood arrow pricing
                "wood_type": wood_type,
                "diameter_inches": spec["diameter_inches"],
                "point_weight_range": spec["point_weight_range"],
                "spine_specifications": create_spine_specifications(min_spine, max_spine, spec["length_range"], min_point_weight, max_point_weight)
            }
            arrows.append(arrow_entry)
    
    return arrows

def estimate_gpi_for_wood(wood_type: str, diameter_mm: float) -> float:
    """Estimate grains per inch for different wood types and diameters"""
    
    # Wood density factors (relative to cedar = 1.0)
    wood_densities = {
        "Cedar": 1.0,
        "Pine": 0.9,
        "Port Orford Cedar": 1.1,
        "Douglas Fir": 1.2,
        "Ash": 1.6,
        "Hickory": 1.8,
        "Birch": 1.4,
        "Oak": 1.7,
        "Bamboo": 1.3
    }
    
    # Base GPI for cedar at 5/16" (7.9mm) ≈ 8-10 GPI
    base_gpi = 9.0
    
    # Adjust for wood type
    density_factor = wood_densities.get(wood_type, 1.0)
    
    # Adjust for diameter (cross-sectional area scales with diameter squared)
    diameter_factor = (diameter_mm / 7.9) ** 2
    
    estimated_gpi = base_gpi * density_factor * diameter_factor
    
    return round(estimated_gpi, 1)

def create_spine_specifications(min_spine: int, max_spine: int, length_range: str, min_point_weight: int, max_point_weight: int) -> List[Dict[str, Any]]:
    """Create spine specifications for the wood arrow"""
    
    # Parse length range
    length_parts = length_range.replace("\"", "").split("-")
    min_length = float(length_parts[0])
    max_length = float(length_parts[-1]) if len(length_parts) > 1 else min_length + 2
    
    specs = []
    
    # Create specs for different spine values in the range
    spine_values = []
    if min_spine == max_spine:
        spine_values = [min_spine]
    else:
        # Create 2-3 spine values in the range
        if max_spine - min_spine <= 10:
            spine_values = [min_spine, max_spine]
        else:
            mid_spine = (min_spine + max_spine) // 2
            spine_values = [min_spine, mid_spine, max_spine]
    
    for spine in spine_values:
        for length in [min_length, max_length]:
            # Calculate recommended point weight for this spine/length combo
            if spine <= 35:
                recommended_point_weight = min_point_weight
            elif spine >= 55:
                recommended_point_weight = max_point_weight
            else:
                # Linear interpolation
                weight_range = max_point_weight - min_point_weight
                spine_ratio = (spine - min_spine) / (max_spine - min_spine) if max_spine != min_spine else 0.5
                recommended_point_weight = int(min_point_weight + (weight_range * spine_ratio))
            
            spec = {
                "spine": spine,
                "length": length,
                "point_weight": recommended_point_weight,
                "total_weight": calculate_total_arrow_weight(spine, length, recommended_point_weight),
                "diameter": None,  # Will be filled from main arrow data
                "straightness": "±0.006\"",  # Typical for wood arrows
                "weight_tolerance": "±3 grains"  # Wood arrows have looser tolerances
            }
            specs.append(spec)
    
    return specs

def calculate_total_arrow_weight(spine: int, length: float, point_weight: int) -> int:
    """Estimate total arrow weight for wood arrows"""
    
    # Estimate shaft weight based on spine and length
    # Stiffer (lower spine number for wood) and longer arrows are heavier
    base_gpi = 12 - (spine / 10)  # Rough approximation
    shaft_weight = base_gpi * length
    
    # Add components
    nock_weight = 10  # Standard nock
    fletching_weight = 20  # Feather fletching is heavier
    
    total_weight = int(shaft_weight + point_weight + nock_weight + fletching_weight)
    
    return total_weight

def main():
    """Main function to parse and save wood arrow data"""
    
    print("🌲 Parsing wood arrow specifications from Wood arrows.txt...")
    
    # Parse the wood arrow data
    wood_data = parse_wood_arrow_chart()
    
    print(f"📊 Parsed wood arrow specifications:")
    print(f"   Total arrow models: {len(wood_data['arrows'])}")
    print(f"   Wood types covered: {len(set(arrow['wood_type'] for arrow in wood_data['arrows']))}")
    
    # Save to JSON file
    output_file = "comprehensive_wood_arrows.json"
    with open(output_file, 'w') as f:
        json.dump(wood_data, f, indent=2)
    
    print(f"✅ Wood arrow data saved to {output_file}")
    
    # Display summary
    print(f"\n🎯 Wood Arrow Models Created:")
    for arrow in wood_data['arrows']:
        spine_specs_count = len(arrow['spine_specifications'])
        print(f"   {arrow['model_name']}: {spine_specs_count} spine specs")
    
    print(f"\n📝 Key Features:")
    print(f"   • Spine ranges from 25# to 60+#")
    print(f"   • Diameters from 5/16\" to 3/8\"+")
    print(f"   • Wood types: Cedar, Pine, Port Orford Cedar, Douglas Fir, Ash, Hickory, Birch, Oak, Bamboo")
    print(f"   • Point weight ranges from 75gr to 300gr+")
    print(f"   • Length ranges from 28\" to 34\"")

if __name__ == "__main__":
    main()