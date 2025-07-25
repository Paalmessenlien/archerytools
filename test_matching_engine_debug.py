#!/usr/bin/env python3
import sys
sys.path.append('/home/paal/arrowtuner2/arrow_scraper')

from arrow_matching_engine import ArrowMatchingEngine
from arrow_database import ArrowDatabase

# Test the database directly first
print("=== Testing Database Directly ===")
db = ArrowDatabase()
results = db.search_arrows(material='Wood', spine_min=40, spine_max=60)
print(f"Direct database search found {len(results)} wood arrows")

if results:
    print("Sample wood arrows from database:")
    for arrow in results[:3]:
        print(f"- {arrow['manufacturer']} {arrow['model_name']} | Material: {arrow['material']}")
else:
    print("❌ No wood arrows found in database!")

# Test the matching engine method search specifically
print("\n=== Testing Matching Engine Database Access ===")
engine = ArrowMatchingEngine()
print(f"Engine database type: {type(engine.db)}")

# Test the specific method the engine uses
try:
    engine_results = engine.db.search_arrows(
        material='Wood',
        spine_min=40,
        spine_max=60,
        limit=50
    )
    print(f"Engine database search found {len(engine_results)} wood arrows")
    
    if engine_results:
        print("Sample wood arrows from engine:")
        for arrow in engine_results[:3]:
            print(f"- {arrow['manufacturer']} {arrow['model_name']} | Material: {arrow['material']}")
    else:
        print("❌ Engine found no wood arrows!")
        
except Exception as e:
    print(f"❌ Error with engine database: {e}")

print("\n=== Testing Material Case Sensitivity ===")
materials_to_test = ['Wood', 'wood', 'WOOD']
for material in materials_to_test:
    results = db.search_arrows(material=material, spine_min=45, spine_max=55)
    print(f"Material '{material}': {len(results)} arrows found")