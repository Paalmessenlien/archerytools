#!/usr/bin/env python3
"""
TopHat Archery Data Import Script
Intelligently matches and imports missing data from TopHat scraper results
Priority: Always use TopHat data as master for length_options
"""

import json
import sqlite3
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import re
from difflib import SequenceMatcher

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TopHatDataImporter:
    """Import and match TopHat Archery data with existing database"""
    
    def __init__(self, database_path: str = "arrow_database.db", 
                 tophat_file: str = "data/processed/extra/tophat_archery_arrows.json"):
        self.database_path = database_path
        self.tophat_file = tophat_file
        self.conn = None
        self.stats = {
            'total_arrows': 0,
            'matched_arrows': 0,
            'updated_arrows': 0,
            'new_arrows': 0,
            'new_manufacturers': 0,
            'updated_spine_specs': 0,
            'new_spine_specs': 0,
            'length_updates': 0
        }
        
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.database_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def load_tophat_data(self) -> Dict[str, Any]:
        """Load TopHat arrow data from JSON file"""
        try:
            with open(self.tophat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data['arrows'])} arrows from TopHat data")
            return data
        except Exception as e:
            logger.error(f"Failed to load TopHat data: {e}")
            return None
    
    def normalize_model_name(self, model_name: str) -> str:
        """Normalize model name for better matching"""
        # Remove extra spaces and convert to lowercase
        normalized = ' '.join(model_name.split()).lower()
        
        # Remove common suffixes that might differ
        suffixes_to_remove = [
            'arrow', 'arrows', 'shaft', 'shafts', '™', '®', '©'
        ]
        for suffix in suffixes_to_remove:
            normalized = normalized.replace(suffix, '')
        
        # Normalize separators
        normalized = normalized.replace('-', ' ').replace('_', ' ')
        normalized = ' '.join(normalized.split())  # Remove extra spaces again
        
        return normalized.strip()
    
    def calculate_match_score(self, model1: str, model2: str) -> float:
        """Calculate similarity score between two model names"""
        # Normalize both names
        norm1 = self.normalize_model_name(model1)
        norm2 = self.normalize_model_name(model2)
        
        # Direct match after normalization
        if norm1 == norm2:
            return 1.0
        
        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def normalize_manufacturer_name(self, manufacturer: str) -> str:
        """Normalize manufacturer name for better matching"""
        # Handle common manufacturer name variations
        manufacturer = manufacturer.lower().strip()
        
        # Common manufacturer normalization patterns
        normalizations = {
            'gold tip': 'goldtip',
            'gold': 'goldtip',  # TopHat uses "Gold" for "Gold Tip"
            'carbon express': 'carbonexpress',
            'carbon': 'carbonexpress',  # TopHat uses "Carbon" for "Carbon Express"
            'black eagle': 'blackeagle',
            'black': 'blackeagle',  # TopHat uses "Black" for "Black Eagle"
            'victory archery': 'victory',
            'easton archery': 'easton',
            'skylon archery': 'skylon',
            'ok archery': 'ok',
            'ok': 'ok archery',  # Could match either way
            'cross-x': 'cross x',
            'dk bow factory': 'dk bow',
            'dk': 'dk bow',
            'carbon tech': 'carbon tech',
            'carbon impact': 'carbon impact'
        }
        
        # Apply normalizations
        normalized = normalizations.get(manufacturer, manufacturer)
        return normalized

    def find_matching_arrow(self, tophat_arrow: Dict) -> Optional[Tuple[int, float]]:
        """Find matching arrow in database, returns (arrow_id, match_score) or None"""
        cursor = self.conn.cursor()
        
        # Normalize TopHat manufacturer name
        tophat_mfr = self.normalize_manufacturer_name(tophat_arrow['manufacturer'])
        
        # Try multiple manufacturer matching strategies
        manufacturer_queries = [
            # 1. Exact match with normalized name
            ('''SELECT id, manufacturer, model_name FROM arrows WHERE LOWER(manufacturer) = ?''', [tophat_mfr]),
            # 2. Partial match in both directions
            ('''SELECT id, manufacturer, model_name FROM arrows WHERE 
                LOWER(manufacturer) LIKE ? OR ? LIKE '%' || LOWER(manufacturer) || '%' ''', 
             [f"%{tophat_mfr}%", tophat_mfr]),
            # 3. Alternative manufacturer names (Gold -> Gold Tip, etc.)
            ('''SELECT id, manufacturer, model_name FROM arrows WHERE 
                LOWER(manufacturer) = ? OR LOWER(manufacturer) = ?''', 
             ['gold tip' if tophat_arrow['manufacturer'].lower() == 'gold' else tophat_arrow['manufacturer'].lower(),
              'carbon express' if tophat_arrow['manufacturer'].lower() == 'carbon' else 
              'black eagle' if tophat_arrow['manufacturer'].lower() == 'black' else
              'nijora archery' if tophat_arrow['manufacturer'].lower() == 'nijora' else
              'skylon archery' if tophat_arrow['manufacturer'].lower() == 'skylon' else
              tophat_mfr]),
        ]
        
        candidates = []
        for query, params in manufacturer_queries:
            # Filter out empty parameters
            filtered_params = [p for p in params if p]
            if filtered_params:
                cursor.execute(query, filtered_params)
                candidates.extend(cursor.fetchall())
                if candidates:  # Found some candidates, no need to try more queries
                    break
        
        if not candidates:
            return None
        
        # Find best match by model name
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            model_score = self.calculate_match_score(
                tophat_arrow['model_name'], 
                candidate['model_name']
            )
            
            # Calculate manufacturer match score
            mfr_score = self.calculate_match_score(
                tophat_arrow['manufacturer'],
                candidate['manufacturer']
            )
            
            # Combined score: 70% model name, 30% manufacturer
            combined_score = (model_score * 0.7) + (mfr_score * 0.3)
            
            # Debug logging for high scores
            if combined_score >= 0.75:
                logger.debug(f"Potential match: {tophat_arrow['manufacturer']} {tophat_arrow['model_name']} -> "
                           f"{candidate['manufacturer']} {candidate['model_name']} "
                           f"(model: {model_score:.2f}, mfr: {mfr_score:.2f}, combined: {combined_score:.2f})")
            
            if combined_score > best_score and combined_score >= 0.75:  # Lowered threshold
                best_score = combined_score
                best_match = (candidate['id'], combined_score)
        
        return best_match
    
    def update_arrow_data(self, arrow_id: int, tophat_arrow: Dict) -> Dict[str, int]:
        """Update existing arrow with TopHat data"""
        cursor = self.conn.cursor()
        updates = {'spine_specs_updated': 0, 'spine_specs_added': 0, 'length_updates': 0}
        
        # Update arrow metadata if missing
        cursor.execute('SELECT * FROM arrows WHERE id = ?', (arrow_id,))
        existing_arrow = cursor.fetchone()
        
        update_fields = []
        update_values = []
        
        # Update image if missing
        if not existing_arrow['image_url'] and tophat_arrow.get('image_url'):
            update_fields.append('image_url = ?')
            update_values.append(tophat_arrow['image_url'])
        
        # Update description if missing
        if not existing_arrow['description'] and tophat_arrow.get('description'):
            update_fields.append('description = ?')
            update_values.append(tophat_arrow['description'])
        
        # Update arrow type if missing
        if not existing_arrow['arrow_type'] and tophat_arrow.get('arrow_type'):
            update_fields.append('arrow_type = ?')
            update_values.append(tophat_arrow['arrow_type'])
        
        if update_fields:
            update_values.append(arrow_id)
            cursor.execute(f'''
                UPDATE arrows 
                SET {', '.join(update_fields)}
                WHERE id = ?
            ''', update_values)
        
        # Update spine specifications
        for tophat_spec in tophat_arrow['spine_specifications']:
            # Check if this spine spec exists
            cursor.execute('''
                SELECT id, length_options 
                FROM spine_specifications 
                WHERE arrow_id = ? AND spine = ?
            ''', (arrow_id, tophat_spec['spine']))
            
            existing_spec = cursor.fetchone()
            
            if existing_spec:
                # Update existing spine spec - ALWAYS use TopHat length_options as master
                update_spec_fields = []
                update_spec_values = []
                
                # Always update length_options from TopHat (master source)
                if tophat_spec.get('length_options'):
                    update_spec_fields.append('length_options = ?')
                    update_spec_values.append(json.dumps(tophat_spec['length_options']))
                    
                    # Check if length actually changed
                    existing_lengths = json.loads(existing_spec['length_options'] or '[]')
                    if set(existing_lengths) != set(tophat_spec['length_options']):
                        updates['length_updates'] += 1
                        logger.info(f"Updated length_options for {tophat_arrow['manufacturer']} {tophat_arrow['model_name']} spine {tophat_spec['spine']}: {existing_lengths} -> {tophat_spec['length_options']}")
                
                # Update other fields if missing in database
                cursor.execute('SELECT * FROM spine_specifications WHERE id = ?', (existing_spec['id'],))
                full_spec = cursor.fetchone()
                
                if not full_spec['outer_diameter'] and tophat_spec.get('outer_diameter'):
                    update_spec_fields.append('outer_diameter = ?')
                    update_spec_values.append(tophat_spec['outer_diameter'])
                
                if not full_spec['inner_diameter'] and tophat_spec.get('inner_diameter'):
                    update_spec_fields.append('inner_diameter = ?')
                    update_spec_values.append(tophat_spec['inner_diameter'])
                
                if not full_spec['gpi_weight'] and tophat_spec.get('gpi_weight'):
                    update_spec_fields.append('gpi_weight = ?')
                    update_spec_values.append(tophat_spec['gpi_weight'])
                
                if update_spec_fields:
                    update_spec_values.append(existing_spec['id'])
                    cursor.execute(f'''
                        UPDATE spine_specifications 
                        SET {', '.join(update_spec_fields)}
                        WHERE id = ?
                    ''', update_spec_values)
                    updates['spine_specs_updated'] += 1
            
            else:
                # Add new spine specification
                cursor.execute('''
                    INSERT INTO spine_specifications
                    (arrow_id, spine, outer_diameter, inner_diameter, gpi_weight, length_options)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    arrow_id,
                    tophat_spec['spine'],
                    tophat_spec.get('outer_diameter'),
                    tophat_spec.get('inner_diameter'),
                    tophat_spec.get('gpi_weight'),
                    json.dumps(tophat_spec.get('length_options', []))
                ))
                updates['spine_specs_added'] += 1
                logger.info(f"Added new spine spec for {tophat_arrow['manufacturer']} {tophat_arrow['model_name']} spine {tophat_spec['spine']}")
        
        self.conn.commit()
        return updates
    
    def add_new_arrow(self, tophat_arrow: Dict) -> int:
        """Add a completely new arrow to the database"""
        cursor = self.conn.cursor()
        
        # Insert arrow
        cursor.execute('''
            INSERT INTO arrows (manufacturer, model_name, material, arrow_type, 
                              description, image_url, recommended_use, 
                              straightness_tolerance, weight_tolerance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tophat_arrow['manufacturer'],
            tophat_arrow['model_name'],
            tophat_arrow.get('material', 'Carbon'),
            tophat_arrow.get('arrow_type'),
            tophat_arrow.get('description'),
            tophat_arrow.get('image_url'),
            tophat_arrow.get('recommended_use'),
            tophat_arrow.get('straightness_tolerance'),
            tophat_arrow.get('weight_tolerance')
        ))
        
        arrow_id = cursor.lastrowid
        
        # Add spine specifications
        for spec in tophat_arrow['spine_specifications']:
            cursor.execute('''
                INSERT INTO spine_specifications
                (arrow_id, spine, outer_diameter, inner_diameter, gpi_weight, length_options)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                arrow_id,
                spec['spine'],
                spec.get('outer_diameter'),
                spec.get('inner_diameter'),
                spec.get('gpi_weight'),
                json.dumps(spec.get('length_options', []))
            ))
        
        self.conn.commit()
        logger.info(f"Added new arrow: {tophat_arrow['manufacturer']} {tophat_arrow['model_name']}")
        return arrow_id
    
    def check_new_manufacturer(self, manufacturer: str) -> bool:
        """Check if this is a new manufacturer"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM arrows 
            WHERE LOWER(manufacturer) = LOWER(?)
        ''', (manufacturer,))
        
        result = cursor.fetchone()
        return result['count'] == 0
    
    def import_data(self, update_existing: bool = True, add_new_arrows: bool = False,
                   add_new_manufacturers: bool = False, dry_run: bool = False):
        """Import TopHat data with specified options"""
        
        # Load TopHat data
        tophat_data = self.load_tophat_data()
        if not tophat_data:
            return
        
        # Connect to database
        self.connect()
        
        # Track new manufacturers
        new_manufacturers = set()
        
        # Process each arrow
        for tophat_arrow in tophat_data['arrows']:
            self.stats['total_arrows'] += 1
            
            # Find matching arrow in database
            match_result = self.find_matching_arrow(tophat_arrow)
            
            if match_result:
                arrow_id, match_score = match_result
                self.stats['matched_arrows'] += 1
                
                logger.info(f"Matched: {tophat_arrow['manufacturer']} {tophat_arrow['model_name']} "
                          f"(score: {match_score:.2f})")
                
                if update_existing and not dry_run:
                    updates = self.update_arrow_data(arrow_id, tophat_arrow)
                    if any(updates.values()):
                        self.stats['updated_arrows'] += 1
                        self.stats['updated_spine_specs'] += updates['spine_specs_updated']
                        self.stats['new_spine_specs'] += updates['spine_specs_added']
                        self.stats['length_updates'] += updates['length_updates']
            
            else:
                # No match found
                is_new_manufacturer = self.check_new_manufacturer(tophat_arrow['manufacturer'])
                
                if is_new_manufacturer:
                    new_manufacturers.add(tophat_arrow['manufacturer'])
                
                if add_new_arrows and (not is_new_manufacturer or add_new_manufacturers):
                    if not dry_run:
                        self.add_new_arrow(tophat_arrow)
                        self.stats['new_arrows'] += 1
                        logger.info(f"Added new arrow: {tophat_arrow['manufacturer']} {tophat_arrow['model_name']}")
                    else:
                        logger.info(f"Would add new arrow: {tophat_arrow['manufacturer']} {tophat_arrow['model_name']}")
                else:
                    logger.warning(f"No match found for: {tophat_arrow['manufacturer']} {tophat_arrow['model_name']}")
                    if is_new_manufacturer and not add_new_manufacturers:
                        logger.info(f"  -> New manufacturer '{tophat_arrow['manufacturer']}' (skipped)")
        
        # Update new manufacturer count
        self.stats['new_manufacturers'] = len(new_manufacturers)
        
        # Close connection
        self.conn.close()
        
        # Print summary
        self.print_summary(new_manufacturers, dry_run)
    
    def print_summary(self, new_manufacturers: set, dry_run: bool):
        """Print import summary"""
        print("\n" + "="*60)
        print("TopHat Data Import Summary" + (" (DRY RUN)" if dry_run else ""))
        print("="*60)
        print(f"Total arrows processed: {self.stats['total_arrows']}")
        print(f"Matched arrows: {self.stats['matched_arrows']}")
        print(f"Updated arrows: {self.stats['updated_arrows']}")
        print(f"New arrows added: {self.stats['new_arrows']}")
        print(f"Updated spine specs: {self.stats['updated_spine_specs']}")
        print(f"New spine specs added: {self.stats['new_spine_specs']}")
        print(f"Length options updated: {self.stats['length_updates']}")
        
        if new_manufacturers:
            print(f"\nNew manufacturers found ({len(new_manufacturers)}):")
            for mfr in sorted(new_manufacturers):
                print(f"  - {mfr}")
        
        print("="*60)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Import TopHat Archery data into existing database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be updated
  python tophat_data_import.py --dry-run
  
  # Update existing arrows only (default)
  python tophat_data_import.py
  
  # Update existing and add new arrows from known manufacturers
  python tophat_data_import.py --add-new-arrows
  
  # Full import including new manufacturers
  python tophat_data_import.py --add-new-arrows --add-new-manufacturers
  
  # Custom paths
  python tophat_data_import.py --database my_arrows.db --tophat-file custom_tophat.json
        """
    )
    
    parser.add_argument('--database', default='arrow_database.db',
                      help='Path to arrow database (default: arrow_database.db)')
    parser.add_argument('--tophat-file', default='data/processed/extra/tophat_archery_arrows.json',
                      help='Path to TopHat JSON file')
    parser.add_argument('--update-existing', action='store_true', default=True,
                      help='Update existing arrows with missing data (default: True)')
    parser.add_argument('--add-new-arrows', action='store_true',
                      help='Add new arrows from existing manufacturers')
    parser.add_argument('--add-new-manufacturers', action='store_true',
                      help='Add arrows from new manufacturers (requires --add-new-arrows)')
    parser.add_argument('--dry-run', action='store_true',
                      help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.add_new_manufacturers and not args.add_new_arrows:
        parser.error("--add-new-manufacturers requires --add-new-arrows")
    
    # Create importer
    importer = TopHatDataImporter(
        database_path=args.database,
        tophat_file=args.tophat_file
    )
    
    # Run import
    importer.import_data(
        update_existing=args.update_existing,
        add_new_arrows=args.add_new_arrows,
        add_new_manufacturers=args.add_new_manufacturers,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()