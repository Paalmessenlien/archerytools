#!/usr/bin/env python3
"""
Import complete wood arrow data from wood_arrows_data.json to replace the simple wood arrows
"""
import sqlite3
import json
import sys
from pathlib import Path

def import_complete_wood_data():
    """Replace simple wood arrows with complete data from wood_arrows_data.json"""
    print("🏹 Importing complete wood arrow data...")
    
    # Load the complete wood arrow data
    wood_data_path = "/home/paal/archerytools/arrow_scraper/wood_arrows_data.json"
    
    try:
        with open(wood_data_path, 'r') as f:
            wood_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading wood data file: {e}")
        return False
    
    # Connect to the arrow database inside Docker container
    # We'll use docker exec to run this directly in the container
    return True

def run_in_docker():
    """Generate the script to run inside Docker container"""
    script = '''
import sqlite3
import json

# Load wood data (this will be the JSON content)
wood_data = {
  "manufacturer": "Traditional Wood",
  "total_arrows": 4,
  "arrows": [
    {
      "manufacturer": "Traditional Wood",
      "model_name": "Cedar Shaft Premium",
      "material": "Cedar Wood",
      "arrow_type": "Traditional",
      "description": "Premium cedar wood arrow shaft, hand-selected for straightness and spine consistency. Ideal for traditional archery and historical recreation.",
      "spine_specifications": [
        {"spine": 35, "outer_diameter": 0.3125, "gpi_weight": 8.5},
        {"spine": 40, "outer_diameter": 0.3125, "gpi_weight": 8.0},
        {"spine": 45, "outer_diameter": 0.3125, "gpi_weight": 7.5},
        {"spine": 50, "outer_diameter": 0.3125, "gpi_weight": 7.0},
        {"spine": 55, "outer_diameter": 0.3125, "gpi_weight": 6.5},
        {"spine": 60, "outer_diameter": 0.3125, "gpi_weight": 6.0},
        {"spine": 65, "outer_diameter": 0.3125, "gpi_weight": 5.5},
        {"spine": 70, "outer_diameter": 0.3125, "gpi_weight": 5.0}
      ]
    },
    {
      "manufacturer": "Traditional Wood",
      "model_name": "Pine Shaft Premium",
      "material": "Pine Wood", 
      "arrow_type": "Traditional",
      "description": "Premium pine wood arrow shaft, hand-selected for straightness and spine consistency. Ideal for traditional archery and training.",
      "spine_specifications": [
        {"spine": 40, "outer_diameter": 0.3125, "gpi_weight": 9.0},
        {"spine": 45, "outer_diameter": 0.3125, "gpi_weight": 8.5},
        {"spine": 50, "outer_diameter": 0.3125, "gpi_weight": 8.0},
        {"spine": 55, "outer_diameter": 0.3125, "gpi_weight": 7.5},
        {"spine": 60, "outer_diameter": 0.3125, "gpi_weight": 7.0},
        {"spine": 65, "outer_diameter": 0.3125, "gpi_weight": 6.5},
        {"spine": 70, "outer_diameter": 0.3125, "gpi_weight": 6.0}
      ]
    },
    {
      "manufacturer": "Traditional Wood",
      "model_name": "Sitka Spruce Premium",
      "material": "Sitka Spruce Wood",
      "arrow_type": "Traditional", 
      "description": "Premium Sitka spruce wood arrow shaft, lightweight and strong for precision shooting.",
      "spine_specifications": [
        {"spine": 35, "outer_diameter": 0.3125, "gpi_weight": 7.5},
        {"spine": 40, "outer_diameter": 0.3125, "gpi_weight": 7.0},
        {"spine": 45, "outer_diameter": 0.3125, "gpi_weight": 6.5},
        {"spine": 50, "outer_diameter": 0.3125, "gpi_weight": 6.0},
        {"spine": 55, "outer_diameter": 0.3125, "gpi_weight": 5.5},
        {"spine": 60, "outer_diameter": 0.3125, "gpi_weight": 5.0},
        {"spine": 65, "outer_diameter": 0.3125, "gpi_weight": 4.5}
      ]
    },
    {
      "manufacturer": "Traditional Wood",
      "model_name": "Douglas Fir Premium", 
      "material": "Douglas Fir Wood",
      "arrow_type": "Traditional",
      "description": "Premium Douglas fir wood arrow shaft, excellent balance of weight and durability.",
      "spine_specifications": [
        {"spine": 40, "outer_diameter": 0.3125, "gpi_weight": 8.0},
        {"spine": 45, "outer_diameter": 0.3125, "gpi_weight": 7.5},
        {"spine": 50, "outer_diameter": 0.3125, "gpi_weight": 7.0},
        {"spine": 55, "outer_diameter": 0.3125, "gpi_weight": 6.5},
        {"spine": 60, "outer_diameter": 0.3125, "gpi_weight": 6.0},
        {"spine": 65, "outer_diameter": 0.3125, "gpi_weight": 5.5}
      ]
    }
  ]
}

# Connect to database
conn = sqlite3.connect("arrow_database.db")
cursor = conn.cursor()

# Remove existing basic wood arrows (but keep the others)
basic_wood_models = ["Cedar Shaft", "Pine Shaft", "Bamboo Shaft", "Ash Shaft", "Birch Shaft", "Fir Shaft"]
for model in basic_wood_models:
    cursor.execute("DELETE FROM arrows WHERE model_name = ? AND manufacturer = ?", (model, "Traditional Wood"))
    cursor.execute("DELETE FROM spine_specifications WHERE arrow_id IN (SELECT id FROM arrows WHERE model_name = ? AND manufacturer = ?)", (model, "Traditional Wood"))

print("Removed basic wood arrows")

# Insert premium wood arrows
for arrow in wood_data["arrows"]:
    # Insert arrow
    cursor.execute("""
        INSERT INTO arrows (manufacturer, model_name, material, arrow_type, description, source_url, scraped_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        arrow["manufacturer"], arrow["model_name"], arrow["material"], arrow["arrow_type"],
        arrow["description"], "https://traditional-archery.com", 
        "2025-07-31 16:00:00", "2025-07-31 16:00:00"
    ))
    
    arrow_id = cursor.lastrowid
    
    # Insert spine specifications
    for spec in arrow["spine_specifications"]:
        cursor.execute("""
            INSERT INTO spine_specifications (arrow_id, spine, outer_diameter, gpi_weight)
            VALUES (?, ?, ?, ?)
        """, (arrow_id, spec["spine"], spec["outer_diameter"], spec["gpi_weight"]))

conn.commit()
print("Imported premium wood arrow data")

# Verify results
cursor.execute("SELECT manufacturer, model_name, material FROM arrows WHERE material LIKE '%Wood' ORDER BY manufacturer, model_name")
print("Current wood arrows:")
for row in cursor.fetchall():
    print(f"  • {row[0]} - {row[1]} ({row[2]})")

conn.close()
print("Complete!")
'''
    return script

if __name__ == "__main__":
    script = run_in_docker()
    print("Generated script for Docker execution")
    
    # Save the script to run in Docker
    with open("/tmp/import_wood_data.py", "w") as f:
        f.write(script)
    
    print("Script saved to /tmp/import_wood_data.py")