#!/usr/bin/env python3
"""
Build Database Script for Docker Image
Creates a database file that gets built into the Docker image
"""

import os
import sys
import sqlite3
from pathlib import Path
import json

def build_database_for_docker():
    """Build database for Docker image"""
    print("🏗️  Building database for Docker image...")
    
    # Target database path (will be in Docker image)
    db_path = "arrow_database.db"
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  Removed existing database: {db_path}")
    
    # Create database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    print("📋 Creating database tables...")
    
    # Arrows table - main arrow information
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS arrows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        manufacturer TEXT NOT NULL,
        model_name TEXT NOT NULL,
        material TEXT,
        arrow_type TEXT,
        carbon_content TEXT,
        recommended_use TEXT,
        price_range TEXT,
        straightness_tolerance TEXT,
        weight_tolerance TEXT,
        description TEXT,
        image_url TEXT,
        local_image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        min_spine INTEGER,
        max_spine INTEGER,
        min_gpi REAL,
        max_gpi REAL,
        min_outer_diameter REAL,
        max_outer_diameter REAL,
        min_inner_diameter REAL,
        max_inner_diameter REAL,
        length_options TEXT
    )
    ''')
    
    # Spine specifications table - detailed spine-specific data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS spine_specifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arrow_id INTEGER NOT NULL,
        spine INTEGER,
        outer_diameter REAL,
        inner_diameter REAL,
        gpi_weight REAL,
        wall_thickness REAL,
        insert_weight_range TEXT,
        nock_size TEXT,
        length_options TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE
    )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_arrows_manufacturer ON arrows (manufacturer)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_arrows_material ON arrows (material)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_arrows_spine_range ON arrows (min_spine, max_spine)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_spine_specs_arrow_id ON spine_specifications (arrow_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_spine_specs_spine ON spine_specifications (spine)')
    
    print("✅ Database tables created")
    
    # Load data from processed JSON files
    data_dir = Path("data/processed")
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        conn.close()
        return False
    
    json_files = list(data_dir.glob("*.json"))
    if not json_files:
        print(f"❌ No JSON files found in: {data_dir}")
        conn.close()
        return False
    
    print(f"📦 Loading data from {len(json_files)} JSON files...")
    
    total_arrows = 0
    total_spine_specs = 0
    
    for json_file in json_files:
        try:
            print(f"  📄 Processing: {json_file.name}")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            arrows_data = []
            if isinstance(data, dict):
                if 'arrows' in data:
                    arrows_data = data['arrows']
                elif 'extracted_data' in data:
                    arrows_data = data['extracted_data']
                else:
                    # Assume the dict itself contains arrow data
                    arrows_data = [data]
            elif isinstance(data, list):
                arrows_data = data
            
            for arrow_data in arrows_data:
                if not isinstance(arrow_data, dict):
                    continue
                
                # Extract basic arrow info
                manufacturer = arrow_data.get('manufacturer', 'Unknown')
                model_name = arrow_data.get('model_name', 'Unknown')
                
                if not model_name or model_name == 'Unknown':
                    continue
                
                # Calculate spine ranges
                spine_specs = arrow_data.get('spine_specifications', [])
                min_spine = None
                max_spine = None
                min_gpi = None
                max_gpi = None
                min_outer_diameter = None
                max_outer_diameter = None
                min_inner_diameter = None
                max_inner_diameter = None
                
                if spine_specs:
                    spines = [spec.get('spine') for spec in spine_specs if spec.get('spine') is not None]
                    gpis = [spec.get('gpi_weight') for spec in spine_specs if spec.get('gpi_weight') is not None]
                    outer_diameters = [spec.get('outer_diameter') for spec in spine_specs if spec.get('outer_diameter') is not None]
                    inner_diameters = [spec.get('inner_diameter') for spec in spine_specs if spec.get('inner_diameter') is not None]
                    
                    if spines:
                        min_spine = min(spines)
                        max_spine = max(spines)
                    if gpis:
                        min_gpi = min(gpis)
                        max_gpi = max(gpis)
                    if outer_diameters:
                        min_outer_diameter = min(outer_diameters)
                        max_outer_diameter = max(outer_diameters)
                    if inner_diameters:
                        min_inner_diameter = min(inner_diameters)
                        max_inner_diameter = max(inner_diameters)
                
                # Insert arrow record
                cursor.execute('''
                INSERT INTO arrows (
                    manufacturer, model_name, material, arrow_type, carbon_content,
                    recommended_use, price_range, straightness_tolerance, weight_tolerance,
                    description, image_url, local_image_path, length_options,
                    min_spine, max_spine, min_gpi, max_gpi,
                    min_outer_diameter, max_outer_diameter,
                    min_inner_diameter, max_inner_diameter
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    manufacturer,
                    model_name,
                    arrow_data.get('material'),
                    arrow_data.get('arrow_type'),
                    arrow_data.get('carbon_content'),
                    arrow_data.get('recommended_use'),
                    arrow_data.get('price_range'),
                    arrow_data.get('straightness_tolerance'),
                    arrow_data.get('weight_tolerance'),
                    arrow_data.get('description'),
                    arrow_data.get('image_url'),
                    arrow_data.get('local_image_path'), 
                    json.dumps(arrow_data.get('length_options', [])) if arrow_data.get('length_options') else None,
                    min_spine, max_spine, min_gpi, max_gpi,
                    min_outer_diameter, max_outer_diameter,
                    min_inner_diameter, max_inner_diameter
                ))
                
                arrow_id = cursor.lastrowid
                total_arrows += 1
                
                # Insert spine specifications
                for spec in spine_specs:
                    if not isinstance(spec, dict):
                        continue
                        
                    cursor.execute('''
                    INSERT INTO spine_specifications (
                        arrow_id, spine, outer_diameter, inner_diameter, gpi_weight,
                        wall_thickness, insert_weight_range, nock_size, length_options, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        arrow_id,
                        spec.get('spine'),
                        spec.get('outer_diameter'), 
                        spec.get('inner_diameter'),
                        spec.get('gpi_weight'),
                        spec.get('wall_thickness'),
                        spec.get('insert_weight_range'),
                        spec.get('nock_size'),
                        json.dumps(spec.get('length_options', [])) if spec.get('length_options') else None,
                        spec.get('notes')
                    ))
                    total_spine_specs += 1
            
        except Exception as e:
            print(f"  ❌ Error processing {json_file.name}: {e}")
            continue
    
    # Commit all changes
    conn.commit()
    
    # Get final statistics
    cursor.execute("SELECT COUNT(*) FROM arrows")
    final_arrow_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM spine_specifications") 
    final_spine_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT manufacturer) FROM arrows")
    manufacturer_count = cursor.fetchone()[0]
    
    conn.close()
    
    # Display summary
    print("\n🎉 Database Build Summary:")
    print("=" * 30)
    print(f"✅ Total arrows: {final_arrow_count}")
    print(f"✅ Total spine specs: {final_spine_count}")
    print(f"✅ Manufacturers: {manufacturer_count}")
    print(f"✅ Database file: {db_path}")
    
    # Show file size
    db_size = os.path.getsize(db_path)
    db_size_mb = db_size / (1024 * 1024)
    print(f"✅ Database size: {db_size_mb:.1f} MB")
    
    if final_arrow_count > 0:
        print("\n🚀 Database ready for Docker image!")
        return True
    else:
        print("\n❌ No arrows loaded - check data files")
        return False

if __name__ == "__main__":
    success = build_database_for_docker()
    sys.exit(0 if success else 1)