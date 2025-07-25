#!/usr/bin/env python3

import sys
sys.path.append('arrow_scraper')
from normalize_materials import normalize_material
import sqlite3

conn = sqlite3.connect('arrow_database.db')
cursor = conn.cursor()

# Find arrows that will change from Carbon to Carbon/Aluminum
cursor.execute('''SELECT manufacturer, model_name, material, description 
                  FROM arrows WHERE material = "Carbon"''')
arrows = cursor.fetchall()

changes = []
for manufacturer, model, current_material, description in arrows:
    new_material = normalize_material(current_material, description)
    if new_material != current_material:
        changes.append((manufacturer, model, current_material, new_material))

print(f'Found {len(changes)} arrows that will change classification:')
print('=' * 80)
for manufacturer, model, old, new in changes[:15]:  # Show first 15
    print(f'{manufacturer:<20} {model:<30} {old} -> {new}')

if len(changes) > 15:
    print(f'... and {len(changes) - 15} more')

conn.close()