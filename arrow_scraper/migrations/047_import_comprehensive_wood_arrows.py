#!/usr/bin/env python3
"""
Migration 047: Import Comprehensive Wood Arrow Specifications

Imports detailed wood arrow specifications from woodarrowdescriptions_en.md document
including 6 major wood species with ~63 spine specifications total:
- Port Orford Cedar (POC): 14 spine specifications
- Sitka Spruce: 13 spine specifications  
- Douglas Fir: 14 spine specifications
- Pine (Consolidated): 12 spine specifications
- Ash: 7 spine specifications
- Bamboo: 3 spine specifications

Data includes precise spine ranges, GPI weights, diameters, and technical specifications
for traditional archery applications.
"""

import sqlite3
import sys
import os
import json
from decimal import Decimal

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 47,
        'description': 'Import comprehensive wood arrow specifications from technical documentation',
        'author': 'System',
        'created_at': '2025-08-30',
        'target_database': 'arrow',
        'dependencies': [],
        'environments': ['all']
    }

def convert_fraction_to_decimal(fraction_str):
    """Convert fraction string to decimal inches"""
    fraction_map = {
        '5/16': 0.3125,
        '11/32': 0.34375,
        '23/64': 0.359375
    }
    return fraction_map.get(fraction_str, None)

def get_spine_midpoint(spine_range):
    """Convert spine range (e.g., '50-55') to midpoint (52.5)"""
    if '-' in spine_range:
        parts = spine_range.split('-')
        try:
            low = float(parts[0])
            high = float(parts[1])
            return (low + high) / 2
        except ValueError:
            return None
    elif spine_range.startswith('<'):
        # Handle '<30' as 25
        return 25.0
    elif spine_range.endswith('+'):
        # Handle '80+' as 85
        return float(spine_range.replace('+', '')) + 5
    else:
        try:
            return float(spine_range)
        except ValueError:
            return None

def get_gpi_midpoint(gpi_range):
    """Convert GPI range (e.g., '8.8-11.3') to midpoint"""
    if '-' in gpi_range:
        parts = gpi_range.split('-')
        try:
            low = float(parts[0])
            high = float(parts[1])
            return (low + high) / 2
        except ValueError:
            return None
    elif gpi_range.endswith('+'):
        return float(gpi_range.replace('+', '')) + 2
    else:
        try:
            return float(gpi_range)
        except ValueError:
            return None

def migrate_up(cursor):
    """Apply the migration"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration 047: Importing comprehensive wood arrow specifications...")
        
        # Wood arrow data extracted from woodarrowdescriptions_en.md Tables 3.1-3.6
        wood_species_data = [
            {
                'manufacturer': 'Port Orford Cedar Shafts',
                'model': 'POC Premium',
                'description': 'Port Orford Cedar (Chamaecyparis lawsoniana) - The traditional gold standard for wooden shafts with straight grain, good elasticity, and excellent weight-to-spine ratio.',
                'specifications': [
                    {'spine': '25-30', 'diameter': '5/16', 'gpi_range': '8.8-11.3'},
                    {'spine': '30-35', 'diameter': '5/16', 'gpi_range': '9.4-11.9'},
                    {'spine': '35-40', 'diameter': '5/16', 'gpi_range': '10.0-12.5'},
                    {'spine': '40-45', 'diameter': '5/16', 'gpi_range': '10.6-13.1'},
                    {'spine': '40-45', 'diameter': '11/32', 'gpi_range': '10.6-13.4'},
                    {'spine': '45-50', 'diameter': '11/32', 'gpi_range': '11.2-14.1'},
                    {'spine': '50-55', 'diameter': '11/32', 'gpi_range': '11.8-14.7'},
                    {'spine': '55-60', 'diameter': '11/32', 'gpi_range': '12.4-15.3'},
                    {'spine': '60-65', 'diameter': '11/32', 'gpi_range': '13.0-15.9'},
                    {'spine': '65-70', 'diameter': '11/32', 'gpi_range': '13.6-16.6'},
                    {'spine': '50-55', 'diameter': '23/64', 'gpi_range': '12.4-15.3'},
                    {'spine': '55-60', 'diameter': '23/64', 'gpi_range': '13.0-15.9'},
                    {'spine': '60-65', 'diameter': '23/64', 'gpi_range': '13.6-16.6'},
                    {'spine': '65-70', 'diameter': '23/64', 'gpi_range': '14.2-17.2'},
                    {'spine': '70-75', 'diameter': '23/64', 'gpi_range': '14.8-17.8'},
                    {'spine': '75-80', 'diameter': '23/64', 'gpi_range': '15.5-18.4'},
                ]
            },
            {
                'manufacturer': 'Sitka Spruce Shafts',
                'model': 'Sitka Premium',
                'description': 'Sitka spruce (Picea sitchensis) - Renowned for the highest strength-to-weight ratio of any wood. Lightweight performance king for target and 3D shooting.',
                'specifications': [
                    {'spine': '35-39', 'diameter': '11/32', 'gpi_range': '10.0-11.5'},
                    {'spine': '40-44', 'diameter': '11/32', 'gpi_range': '10.6-12.1'},
                    {'spine': '45-49', 'diameter': '11/32', 'gpi_range': '11.2-12.6'},
                    {'spine': '50-54', 'diameter': '11/32', 'gpi_range': '11.8-13.2'},
                    {'spine': '55-59', 'diameter': '11/32', 'gpi_range': '12.4-13.8'},
                    {'spine': '60-64', 'diameter': '11/32', 'gpi_range': '12.9-14.4'},
                    {'spine': '45-49', 'diameter': '23/64', 'gpi_range': '11.8-13.2'},
                    {'spine': '50-54', 'diameter': '23/64', 'gpi_range': '12.4-13.8'},
                    {'spine': '55-59', 'diameter': '23/64', 'gpi_range': '12.9-14.4'},
                    {'spine': '60-64', 'diameter': '23/64', 'gpi_range': '13.5-15.0'},
                    {'spine': '65-69', 'diameter': '23/64', 'gpi_range': '14.1-15.6'},
                    {'spine': '70-74', 'diameter': '23/64', 'gpi_range': '14.7-16.2'},
                    {'spine': '75-79', 'diameter': '23/64', 'gpi_range': '15.3-16.8'},
                ]
            },
            {
                'manufacturer': 'Douglas Fir Shafts',
                'model': 'Fir Classic',
                'description': 'Douglas fir (Pseudotsuga menziesii) - Dense, heavy, and robust hunting specialist. Excellent for big game with superior penetration through bone and thick tissue.',
                'specifications': [
                    {'spine': '30-35', 'diameter': '11/32', 'gpi_range': '10.3-11.9'},
                    {'spine': '35-40', 'diameter': '11/32', 'gpi_range': '10.6-11.9'},
                    {'spine': '40-45', 'diameter': '11/32', 'gpi_range': '10.9-12.5'},
                    {'spine': '45-50', 'diameter': '11/32', 'gpi_range': '11.3-12.8'},
                    {'spine': '50-55', 'diameter': '11/32', 'gpi_range': '11.6-13.1'},
                    {'spine': '55-60', 'diameter': '11/32', 'gpi_range': '11.9-13.4'},
                    {'spine': '60-65', 'diameter': '11/32', 'gpi_range': '12.5-14.1'},
                    {'spine': '65-70', 'diameter': '11/32', 'gpi_range': '12.8-14.4'},
                    {'spine': '70-75', 'diameter': '11/32', 'gpi_range': '13.4-15.0'},
                    {'spine': '75-80', 'diameter': '11/32', 'gpi_range': '13.8-15.3'},
                    {'spine': '80-85', 'diameter': '11/32', 'gpi_range': '14.7-16.3'},
                    {'spine': '85-90', 'diameter': '11/32', 'gpi_range': '15.0-16.6'},
                    {'spine': '90-95', 'diameter': '11/32', 'gpi_range': '15.6-16.9'},
                    {'spine': '95-100', 'diameter': '11/32', 'gpi_range': '15.9-17.2'},
                ]
            },
            {
                'manufacturer': 'Pine Shafts',
                'model': 'Premium Pine',
                'description': 'Pine species (Lodgepole, Scots, White) - Versatile workhorse providing reliable all-round performance. More affordable option suitable for training and general hunting.',
                'specifications': [
                    {'spine': '<30', 'diameter': '5/16', 'gpi_range': '9.4-12.0'},
                    {'spine': '30-35', 'diameter': '5/16', 'gpi_range': '10.0-11.9'},
                    {'spine': '35-40', 'diameter': '5/16', 'gpi_range': '10.6-12.5'},
                    {'spine': '40-45', 'diameter': '5/16', 'gpi_range': '11.3-13.1'},
                    {'spine': '45-50', 'diameter': '5/16', 'gpi_range': '11.9-13.8'},
                    {'spine': '40-45', 'diameter': '11/32', 'gpi_range': '11.6-13.4'},
                    {'spine': '45-50', 'diameter': '11/32', 'gpi_range': '12.2-14.1'},
                    {'spine': '50-55', 'diameter': '11/32', 'gpi_range': '12.8-14.7'},
                    {'spine': '55-60', 'diameter': '11/32', 'gpi_range': '13.4-15.3'},
                    {'spine': '60-65', 'diameter': '11/32', 'gpi_range': '14.1-15.9'},
                    {'spine': '65-70', 'diameter': '11/32', 'gpi_range': '14.7-16.6'},
                    {'spine': '70-75', 'diameter': '11/32', 'gpi_range': '15.3-17.2'},
                    {'spine': '80+', 'diameter': '11/32', 'gpi_range': '16.3+'},
                    {'spine': '65-70', 'diameter': '23/64', 'gpi_range': '15.0-16.9'},
                ]
            },
            {
                'manufacturer': 'Ash Shafts',
                'model': 'Ash Premium',
                'description': 'Ash (Fraxinus spp.) - Hardwood historically used for war arrows due to extreme durability and high mass. Best for high draw-weight bows where durability is paramount.',
                'specifications': [
                    {'spine': '45-50', 'diameter': '11/32', 'gpi_range': '14.1-16.3'},
                    {'spine': '50-55', 'diameter': '11/32', 'gpi_range': '14.7-16.9'},
                    {'spine': '55-60', 'diameter': '11/32', 'gpi_range': '15.3-17.5'},
                    {'spine': '60-65', 'diameter': '11/32', 'gpi_range': '15.9-18.1'},
                    {'spine': '65-70', 'diameter': '11/32', 'gpi_range': '16.6-18.8'},
                    {'spine': '70-75', 'diameter': '11/32', 'gpi_range': '17.2-19.4'},
                    {'spine': '75-80', 'diameter': '11/32', 'gpi_range': '17.8-20.0'},
                ]
            },
            {
                'manufacturer': 'Bamboo Shafts',
                'model': 'Natural Bamboo',
                'description': 'Natural bamboo (Tonkin) - Natural composite with remarkable strength, lightness, and spring. Naturally tapered structure creates unique ballistic characteristics.',
                'specifications': [
                    {'spine': '<40', 'diameter': '0.28-0.30', 'gpi_range': '7.6-10.6'},  # 7.0-7.5mm converted
                    {'spine': '45-60', 'diameter': '0.30-0.31', 'gpi_range': '10.6-14.5'},  # 7.5-8.0mm converted
                    {'spine': '65+', 'diameter': '0.31-0.34', 'gpi_range': '14.5-18.2+'},  # 8.0-8.7mm converted
                ]
            }
        ]
        
        print("   📊 Processing wood species data...")
        
        # Track created items for rollback
        created_manufacturers = []
        created_arrows = []
        created_specifications = []
        
        for species_data in wood_species_data:
            manufacturer = species_data['manufacturer']
            model = species_data['model']
            description = species_data['description']
            
            print(f"   🌲 Processing {manufacturer}...")
            
            # Create manufacturer entry if it doesn't exist
            cursor.execute("SELECT id FROM manufacturers WHERE name = ?", (manufacturer,))
            manufacturer_result = cursor.fetchone()
            
            if not manufacturer_result:
                cursor.execute("""
                    INSERT INTO manufacturers (name, country, website, description, arrow_types, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (manufacturer, 'Various', '', f'{manufacturer} - Traditional wood archery shafts', 'wood'))
                created_manufacturers.append(manufacturer)
                print(f"     ✅ Created manufacturer: {manufacturer}")
            
            # Create arrow entry (or update if exists)
            cursor.execute("""
                INSERT OR IGNORE INTO arrows (
                    manufacturer, model_name, material, description, arrow_type, created_at
                ) VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (
                manufacturer,
                model,
                'Wood',
                description,
                'wood'
            ))
            
            # Get arrow ID whether it was just created or already existed
            cursor.execute("SELECT id FROM arrows WHERE manufacturer = ? AND model_name = ?", (manufacturer, model))
            arrow_result = cursor.fetchone()
            arrow_id = arrow_result[0] if arrow_result else cursor.lastrowid
            created_arrows.append(arrow_id)
            print(f"     ✅ Created arrow model: {model} (ID: {arrow_id})")
            
            # Create spine specifications
            spec_count = 0
            for spec in species_data['specifications']:
                spine_value = get_spine_midpoint(spec['spine'])
                if spine_value is None:
                    print(f"     ⚠️  Skipping invalid spine: {spec['spine']}")
                    continue
                
                # Handle diameter - convert fractions or use direct decimal
                diameter_str = spec['diameter']
                if '/' in diameter_str:
                    outer_diameter = convert_fraction_to_decimal(diameter_str)
                else:
                    try:
                        outer_diameter = float(diameter_str.split('-')[0])  # Use lower bound for ranges
                    except:
                        outer_diameter = None
                
                if outer_diameter is None:
                    print(f"     ⚠️  Skipping invalid diameter: {diameter_str}")
                    continue
                
                # Calculate GPI midpoint
                gpi_weight = get_gpi_midpoint(spec['gpi_range'])
                if gpi_weight is None:
                    print(f"     ⚠️  Skipping invalid GPI: {spec['gpi_range']}")
                    continue
                
                # Inner diameter estimation (wood shafts are solid, so inner = 0)
                inner_diameter = 0.0
                
                # Length options - typical wood shaft lengths
                length_options = json.dumps(['28"', '29"', '30"', '31"', '32"'])
                
                # Create unique spine identifier including diameter for woods with multiple diameter options
                spine_identifier = f"{spine_value}@{diameter_str}"
                
                # Insert spine specification (replace if exists to update with new data)
                cursor.execute("""
                    INSERT OR REPLACE INTO spine_specifications (
                        arrow_id, spine, outer_diameter, inner_diameter, gpi_weight,
                        length_options, wall_thickness, insert_weight_range, nock_size,
                        notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    arrow_id,
                    spine_identifier,
                    outer_diameter,
                    inner_diameter,
                    gpi_weight,
                    length_options,
                    outer_diameter,  # Wall thickness = outer diameter for solid wood
                    '100-200gr',
                    'Standard',
                    f'Original spine range: {spec["spine"]}, GPI range: {spec["gpi_range"]}, Diameter: {diameter_str}'
                ))
                
                created_specifications.append(cursor.lastrowid)
                spec_count += 1
            
            print(f"     ✅ Created {spec_count} spine specifications for {model}")
        
        # Store created items for rollback
        rollback_data = {
            'manufacturers': created_manufacturers,
            'arrows': created_arrows,
            'specifications': created_specifications
        }
        
        # Store rollback data in a temporary table
        cursor.execute("""
            CREATE TEMPORARY TABLE IF NOT EXISTS migration_047_rollback (
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        """)
        
        cursor.execute("""
            INSERT INTO migration_047_rollback (data) VALUES (?)
        """, (json.dumps(rollback_data),))
        
        conn.commit()
        
        # Summary
        total_specs = sum([len(species['specifications']) for species in wood_species_data])
        print(f"   📈 Import Summary:")
        print(f"     • {len(wood_species_data)} wood species manufacturers created")
        print(f"     • {len(created_arrows)} arrow models created")
        print(f"     • {len(created_specifications)} spine specifications imported")
        print(f"     • Expected: ~{total_specs} specifications")
        
        print("🎯 Migration 047 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration 047 failed: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback the migration"""
    conn = cursor.connection
    
    try:
        print("🔄 Rolling back Migration 047...")
        
        # Get rollback data
        cursor.execute("SELECT data FROM migration_047_rollback ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        
        if not result:
            print("   ⚠️  No rollback data found, attempting generic cleanup...")
            
            # Generic cleanup - remove wood arrows created by this migration
            wood_manufacturers = [
                'Port Orford Cedar Shafts',
                'Sitka Spruce Shafts', 
                'Douglas Fir Shafts',
                'Pine Shafts',
                'Ash Shafts',
                'Bamboo Shafts'
            ]
            
            for manufacturer in wood_manufacturers:
                # Delete spine specifications first (foreign key constraint)
                cursor.execute("""
                    DELETE FROM spine_specifications 
                    WHERE arrow_id IN (
                        SELECT id FROM arrows WHERE manufacturer = ?
                    )
                """, (manufacturer,))
                
                # Delete arrows
                cursor.execute("DELETE FROM arrows WHERE manufacturer = ?", (manufacturer,))
                
                # Delete manufacturer if no other arrows exist
                cursor.execute("""
                    DELETE FROM manufacturers 
                    WHERE name = ? AND NOT EXISTS (
                        SELECT 1 FROM arrows WHERE manufacturer = ?
                    )
                """, (manufacturer, manufacturer))
                
                print(f"     🗑️  Cleaned up {manufacturer}")
        
        else:
            rollback_data = json.loads(result[0])
            
            # Delete spine specifications
            for spec_id in rollback_data['specifications']:
                cursor.execute("DELETE FROM spine_specifications WHERE id = ?", (spec_id,))
            
            # Delete arrows
            for arrow_id in rollback_data['arrows']:
                cursor.execute("DELETE FROM arrows WHERE id = ?", (arrow_id,))
            
            # Delete manufacturers
            for manufacturer in rollback_data['manufacturers']:
                cursor.execute("DELETE FROM manufacturers WHERE name = ?", (manufacturer,))
            
            print(f"     🗑️  Removed {len(rollback_data['specifications'])} spine specifications")
            print(f"     🗑️  Removed {len(rollback_data['arrows'])} arrow models")
            print(f"     🗑️  Removed {len(rollback_data['manufacturers'])} manufacturers")
        
        # Clean up temporary table
        cursor.execute("DROP TABLE IF EXISTS migration_047_rollback")
        
        conn.commit()
        print("🔄 Migration 047 rollback completed")
        return True
        
    except Exception as e:
        print(f"❌ Migration 047 rollback failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Test the migration - try multiple database paths
    possible_paths = [
        '/app/databases/arrow_database.db',  # Docker production
        '/root/archerytools/databases/arrow_database.db',  # Production host
        os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db'),  # Development
        'databases/arrow_database.db',  # Relative path
        'arrow_database.db'  # Current directory
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print(f"❌ Database not found in any location: {possible_paths}")
        sys.exit(1)
    
    print(f"📁 Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'down':
            success = migrate_down(conn.cursor())
        else:
            success = migrate_up(conn.cursor())
        
        if success:
            print("✅ Migration test completed successfully")
        else:
            print("❌ Migration test failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()