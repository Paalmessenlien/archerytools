#!/usr/bin/env python3
import sys
sys.path.append('arrow_scraper')
from arrow_database import normalize_material
import sqlite3

# Connect to database
conn = sqlite3.connect('arrow_scraper/arrow_database.db')
cursor = conn.cursor()

# Get arrows that are currently classified as Wood but might be wrong
cursor.execute('SELECT id, manufacturer, model_name, material, description FROM arrows WHERE material = "Wood"')
arrows = cursor.fetchall()

updates = []
for arrow_id, manufacturer, model_name, current_material, description in arrows:
    # Re-classify using improved logic
    new_material = normalize_material(current_material, description)
    if new_material != current_material:
        updates.append((new_material, arrow_id, manufacturer, model_name, current_material))

print(f'Found {len(updates)} arrows needing material correction:')
for new_material, arrow_id, manufacturer, model_name, old_material in updates:
    print(f'  {manufacturer} - {model_name}: {old_material} → {new_material}')

# Apply updates
for new_material, arrow_id, _, _, _ in updates:
    cursor.execute('UPDATE arrows SET material = ? WHERE id = ?', (new_material, arrow_id))

conn.commit()
print(f'\nUpdated {len(updates)} arrows with corrected material classifications')
conn.close()