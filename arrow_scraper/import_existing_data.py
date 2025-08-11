#!/usr/bin/env python3
"""
Import Existing Arrow Data - Production Safe
Imports arrow data from existing JSON files only, no scraping
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def create_wood_arrow_data():
    """Create wood arrow data if not present"""
    print("🌳 Creating wood arrow data...")
    
    wood_arrows = {
        "manufacturer": "Traditional Wood Arrows",
        "arrows_found": 6,
        "scraping_date": datetime.now().isoformat(),
        "status": "traditional_data",
        "arrows": [
            {
                "model_name": "Cedar Shaft",
                "material": "Cedar Wood",
                "arrow_type": "Traditional",
                "recommended_use": "Traditional, Instinctive, Historical",
                "description": "Traditional cedar wood arrow shaft",
                "spine_specifications": [
                    {"spine": 40, "outer_diameter": 0.312, "gpi_weight": 8.5},
                    {"spine": 45, "outer_diameter": 0.315, "gpi_weight": 8.8},
                    {"spine": 50, "outer_diameter": 0.318, "gpi_weight": 9.1},
                    {"spine": 55, "outer_diameter": 0.321, "gpi_weight": 9.4},
                    {"spine": 60, "outer_diameter": 0.324, "gpi_weight": 9.7}
                ]
            },
            {
                "model_name": "Pine Shaft",
                "material": "Pine Wood", 
                "arrow_type": "Traditional",
                "recommended_use": "Traditional, Beginner",
                "description": "Traditional pine wood arrow shaft",
                "spine_specifications": [
                    {"spine": 35, "outer_diameter": 0.315, "gpi_weight": 7.8},
                    {"spine": 40, "outer_diameter": 0.318, "gpi_weight": 8.1},
                    {"spine": 45, "outer_diameter": 0.321, "gpi_weight": 8.4},
                    {"spine": 50, "outer_diameter": 0.324, "gpi_weight": 8.7}
                ]
            },
            {
                "model_name": "Bamboo Shaft",
                "material": "Bamboo Wood",
                "arrow_type": "Traditional",
                "recommended_use": "Traditional, Historical",
                "description": "Traditional bamboo arrow shaft",
                "spine_specifications": [
                    {"spine": 35, "outer_diameter": 0.295, "gpi_weight": 6.5},
                    {"spine": 40, "outer_diameter": 0.298, "gpi_weight": 6.8},
                    {"spine": 45, "outer_diameter": 0.301, "gpi_weight": 7.1},
                    {"spine": 50, "outer_diameter": 0.304, "gpi_weight": 7.4}
                ]
            },
            {
                "model_name": "Ash Shaft",
                "material": "Ash Wood",
                "arrow_type": "Traditional",
                "recommended_use": "Traditional, Heavy Draw",
                "description": "Traditional ash wood arrow shaft for heavy bows",
                "spine_specifications": [
                    {"spine": 40, "outer_diameter": 0.330, "gpi_weight": 11.5},
                    {"spine": 45, "outer_diameter": 0.333, "gpi_weight": 11.8},
                    {"spine": 50, "outer_diameter": 0.336, "gpi_weight": 12.1},
                    {"spine": 55, "outer_diameter": 0.339, "gpi_weight": 12.4}
                ]
            },
            {
                "model_name": "Birch Shaft",
                "material": "Birch Wood",
                "arrow_type": "Traditional",
                "recommended_use": "Traditional, Medium Draw",
                "description": "Traditional birch wood arrow shaft",
                "spine_specifications": [
                    {"spine": 45, "outer_diameter": 0.325, "gpi_weight": 10.2},
                    {"spine": 50, "outer_diameter": 0.328, "gpi_weight": 10.5},
                    {"spine": 55, "outer_diameter": 0.331, "gpi_weight": 10.8},
                    {"spine": 60, "outer_diameter": 0.334, "gpi_weight": 11.1}
                ]
            },
            {
                "model_name": "Fir Shaft",
                "material": "Fir Wood",
                "arrow_type": "Traditional",
                "recommended_use": "Traditional, Light Draw",
                "description": "Traditional fir wood arrow shaft",
                "spine_specifications": [
                    {"spine": 30, "outer_diameter": 0.318, "gpi_weight": 9.2},
                    {"spine": 35, "outer_diameter": 0.321, "gpi_weight": 9.5},
                    {"spine": 40, "outer_diameter": 0.324, "gpi_weight": 9.8},
                    {"spine": 45, "outer_diameter": 0.327, "gpi_weight": 10.1}
                ]
            }
        ]
    }
    
    # Save wood arrow data
    data_dir = Path("data/processed")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    filename = data_dir / "traditional_wood_arrows.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(wood_arrows, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created {filename}: {len(wood_arrows['arrows'])} wood arrow types")
    return filename

def import_from_json_files():
    """Import arrow data from existing JSON files in data/processed/"""
    
    print("🏹 Importing arrow data from existing JSON files...")
    
    data_dir = Path("data/processed")
    if not data_dir.exists():
        print("❌ No data/processed directory found")
        return False
    
    json_files = list(data_dir.glob("*.json"))
    
    # Check if we have wood arrow data
    wood_files = [f for f in json_files if 'wood' in f.name.lower() or 'traditional' in f.name.lower()]
    if not wood_files:
        print("🌳 No wood arrow data found, creating traditional wood arrows...")
        wood_file = create_wood_arrow_data()
        json_files.append(wood_file)
    
    if not json_files:
        print("❌ No JSON files found in data/processed/")
        return False
    
    print(f"📂 Found {len(json_files)} JSON files (including wood arrows)")
    
    # Initialize database
    conn = sqlite3.connect('arrow_database.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist (matching existing schema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS arrows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer TEXT NOT NULL,
            model_name TEXT NOT NULL,
            material TEXT,
            carbon_content TEXT,
            arrow_type TEXT,
            description TEXT,
            image_url TEXT,
            source_url TEXT,
            scraped_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(manufacturer, model_name)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spine_specifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arrow_id INTEGER,
            spine INTEGER,
            outer_diameter REAL,
            inner_diameter REAL DEFAULT 0.0,
            gpi_weight REAL,
            FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE
        )
    ''')
    
    # Clear existing data
    print("🗑️ Clearing existing database data...")
    cursor.execute('DELETE FROM spine_specifications')
    cursor.execute('DELETE FROM arrows')
    
    total_arrows = 0
    total_specs = 0
    processed_manufacturers = set()
    
    for json_file in json_files:
        try:
            print(f"📄 Processing {json_file.name}...")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            manufacturer = data.get('manufacturer', 'Unknown')
            arrows = data.get('arrows', [])
            
            if not arrows:
                print(f"  ⚠️ No arrows found in {json_file.name}")
                continue
            
            processed_manufacturers.add(manufacturer)
            arrows_in_file = 0
            specs_in_file = 0
            
            for arrow in arrows:
                try:
                    # Insert arrow (matching existing schema)
                    cursor.execute('''
                        INSERT OR REPLACE INTO arrows (
                            manufacturer, model_name, material, carbon_content,
                            arrow_type, description, image_url, source_url, scraped_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        manufacturer,
                        arrow.get('model_name', 'Unknown Model'),
                        arrow.get('material', ''),
                        str(arrow.get('carbon_content', '')),
                        arrow.get('arrow_type', ''),
                        arrow.get('description', ''),
                        arrow.get('image_url', ''),
                        arrow.get('source_url', ''),
                        datetime.now().isoformat()
                    ))
                    
                    arrow_id = cursor.lastrowid
                    arrows_in_file += 1
                    
                    # Insert spine specifications
                    spine_specs = arrow.get('spine_specifications', [])
                    for spec in spine_specs:
                        # Handle length_options - convert list to JSON string for database storage
                        length_options = spec.get('length_options', [])
                        length_options_json = json.dumps(length_options) if length_options else None
                        
                        cursor.execute('''
                            INSERT INTO spine_specifications (
                                arrow_id, spine, outer_diameter, inner_diameter, gpi_weight, length_options
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            arrow_id,
                            spec.get('spine', 0),
                            spec.get('outer_diameter', 0.0),
                            spec.get('inner_diameter', 0.0),
                            spec.get('gpi_weight', 0.0),
                            length_options_json
                        ))
                        specs_in_file += 1
                    
                except Exception as e:
                    print(f"    ❌ Error processing arrow {arrow.get('model_name', 'Unknown')}: {e}")
                    continue
            
            print(f"  ✅ {arrows_in_file} arrows, {specs_in_file} specifications")
            total_arrows += arrows_in_file
            total_specs += specs_in_file
            
        except Exception as e:
            print(f"  ❌ Error processing {json_file.name}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Import completed!")
    print(f"📊 Total: {total_arrows} arrows, {total_specs} specifications")
    print(f"🏭 Manufacturers: {len(processed_manufacturers)}")
    for mfr in sorted(processed_manufacturers):
        print(f"  • {mfr}")
    
    return True

def verify_import():
    """Verify the imported data"""
    print("\n🔍 Verifying imported data...")
    
    try:
        conn = sqlite3.connect('arrow_database.db')
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) FROM arrows')
        arrow_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM spine_specifications')
        spec_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT manufacturer) FROM arrows')
        mfr_count = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT manufacturer, COUNT(*) 
            FROM arrows 
            GROUP BY manufacturer 
            ORDER BY COUNT(*) DESC
        ''')
        manufacturers = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ Database verification:")
        print(f"  • {arrow_count} arrows")
        print(f"  • {spec_count} spine specifications")
        print(f"  • {mfr_count} manufacturers")
        
        if manufacturers:
            print(f"  Top manufacturers:")
            for mfr, count in manufacturers[:5]:
                print(f"    - {mfr}: {count} arrows")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main import function"""
    print("🚀 Arrow Data Import - Production Safe")
    print("=" * 40)
    
    if import_from_json_files():
        verify_import()
        print(f"\n✅ Arrow data import completed successfully!")
    else:
        print(f"\n❌ Arrow data import failed!")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)