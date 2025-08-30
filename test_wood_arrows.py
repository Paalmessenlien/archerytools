#!/usr/bin/env python3
"""
Test script to investigate wood arrows in database
"""

from arrow_scraper.unified_database import UnifiedDatabase

def investigate_wood_arrows():
    db = UnifiedDatabase()
    print('🔍 Investigating wood arrows in database...')

    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Look for Traditional Wood Arrows manufacturer
        cursor.execute('''
            SELECT a.id, a.manufacturer, a.model_name, a.material, a.description,
                   ss.spine, ss.outer_diameter, ss.gpi_weight, m.is_active
            FROM arrows a
            LEFT JOIN spine_specifications ss ON a.id = ss.arrow_id
            JOIN manufacturers m ON a.manufacturer = m.name
            WHERE a.manufacturer LIKE '%wood%' OR a.manufacturer LIKE '%cedar%' OR a.manufacturer LIKE '%traditional%'
            ORDER BY a.manufacturer, a.model_name, ss.spine
        ''')
        
        wood_arrows = cursor.fetchall()
        
        if wood_arrows:
            print(f'   Found {len(wood_arrows)} wood arrow specifications:')
            current_arrow = None
            for row in wood_arrows:
                arrow_id, manufacturer, model, material, description, spine, diameter, gpi, is_active = row
                
                if current_arrow != (arrow_id, manufacturer, model):
                    current_arrow = (arrow_id, manufacturer, model)
                    status = '🟢 Active' if is_active else '🔴 Inactive'
                    print(f'   {status} ID:{arrow_id} {manufacturer} - {model} (Material: {material})')
                    if description:
                        desc_short = description[:100] + '...' if len(description) > 100 else description
                        print(f'     Description: {desc_short}')
                
                if spine and diameter and gpi:
                    print(f'     Spine: {spine}, Diameter: {diameter}, GPI: {gpi}')
        else:
            print('   ❌ No wood arrows found in database')
        
        # Check all manufacturers to see what we have
        print(f'\n📊 All manufacturers in database:')
        cursor.execute('SELECT name, is_active FROM manufacturers ORDER BY is_active DESC, name')
        manufacturers = cursor.fetchall()
        
        for name, is_active in manufacturers:
            status = '🟢' if is_active else '🔴'
            print(f'   {status} {name}')
        
        # Check arrow materials to understand classification
        print(f'\n🏷️  Arrow materials in database:')
        cursor.execute('SELECT DISTINCT material, COUNT(*) as count FROM arrows GROUP BY material ORDER BY count DESC')
        materials = cursor.fetchall()
        
        for material, count in materials:
            print(f'   {material}: {count} arrows')

if __name__ == "__main__":
    investigate_wood_arrows()