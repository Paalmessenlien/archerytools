#!/usr/bin/env python3
"""
Arrow Database Cleaning Script
Comprehensive tool for database maintenance and manufacturer management
"""

import sqlite3
import argparse
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import shutil
import difflib
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseCleaner:
    """Comprehensive database cleaning and maintenance tool"""
    
    def __init__(self, database_path: str = "arrow_database.db", similarity_threshold: float = 0.85):
        self.database_path = database_path
        self.conn = None
        self.similarity_threshold = similarity_threshold
        
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.database_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def normalize_model_name(self, model_name: str) -> str:
        """Normalize model name for better comparison"""
        if not model_name:
            return ""
        
        # Convert to lowercase
        normalized = model_name.lower().strip()
        
        # Remove common prefixes/suffixes that might cause false negatives
        # Remove trademark symbols and other special characters
        normalized = re.sub(r'[™®©]', '', normalized)
        
        # Normalize spacing and punctuation
        normalized = re.sub(r'[_\-\s]+', ' ', normalized)
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Remove common archery terms that add noise
        noise_words = ['arrow', 'shaft', 'hunting', 'target', 'carbon', 'aluminum', 'wood']
        words = normalized.split()
        words = [word for word in words if word not in noise_words]
        
        return ' '.join(words).strip()
    
    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity score between two model names"""
        norm1 = self.normalize_model_name(name1)
        norm2 = self.normalize_model_name(name2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # Use SequenceMatcher for similarity calculation
        similarity = difflib.SequenceMatcher(None, norm1, norm2).ratio()
        
        # Boost score for exact matches after normalization
        if norm1 == norm2:
            similarity = 1.0
        
        return similarity
    
    def are_similar_arrows(self, arrow1: Dict[str, Any], arrow2: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Check if two arrows are similar enough to be considered duplicates
        Returns (is_similar, similarity_score)
        """
        # Must be same manufacturer (exact match)
        if arrow1['manufacturer'].lower() != arrow2['manufacturer'].lower():
            return False, 0.0
        
        # Calculate model name similarity
        model_similarity = self.calculate_similarity(arrow1['model_name'], arrow2['model_name'])
        
        # Check if similarity exceeds threshold
        is_similar = model_similarity >= self.similarity_threshold
        
        return is_similar, model_similarity
    
    def backup_database(self) -> str:
        """Create a backup of the database before making changes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.database_path}.backup_{timestamp}"
        shutil.copy2(self.database_path, backup_path)
        logger.info(f"Database backed up to: {backup_path}")
        return backup_path
    
    def list_manufacturers(self) -> List[Dict[str, Any]]:
        """List all manufacturers with arrow counts"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT manufacturer, 
                   COUNT(*) as arrow_count,
                   COUNT(DISTINCT s.spine) as spine_count,
                   MIN(s.spine) as min_spine,
                   MAX(s.spine) as max_spine
            FROM arrows a
            LEFT JOIN spine_specifications s ON a.id = s.arrow_id
            GROUP BY manufacturer
            ORDER BY manufacturer
        ''')
        
        manufacturers = []
        for row in cursor.fetchall():
            manufacturers.append({
                'manufacturer': row['manufacturer'],
                'arrow_count': row['arrow_count'],
                'spine_count': row['spine_count'] or 0,
                'min_spine': row['min_spine'],
                'max_spine': row['max_spine']
            })
        
        return manufacturers
    
    def list_arrows_by_manufacturer(self, manufacturer: str) -> List[Dict[str, Any]]:
        """List all arrows for a specific manufacturer"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT a.id, a.manufacturer, a.model_name, a.material, a.arrow_type,
                   COUNT(s.id) as spine_count,
                   GROUP_CONCAT(DISTINCT s.spine ORDER BY s.spine) as spines
            FROM arrows a
            LEFT JOIN spine_specifications s ON a.id = s.arrow_id
            WHERE LOWER(a.manufacturer) = LOWER(?)
            GROUP BY a.id, a.manufacturer, a.model_name, a.material, a.arrow_type
            ORDER BY a.model_name
        ''', (manufacturer,))
        
        arrows = []
        for row in cursor.fetchall():
            arrows.append({
                'id': row['id'],
                'manufacturer': row['manufacturer'],
                'model_name': row['model_name'],
                'material': row['material'],
                'arrow_type': row['arrow_type'],
                'spine_count': row['spine_count'],
                'spines': row['spines'].split(',') if row['spines'] else []
            })
        
        return arrows
    
    def rename_manufacturer(self, old_name: str, new_name: str, dry_run: bool = False) -> Dict[str, int]:
        """Rename a manufacturer across the database"""
        cursor = self.conn.cursor()
        
        # First, check how many arrows will be affected
        cursor.execute('SELECT COUNT(*) as count FROM arrows WHERE LOWER(manufacturer) = LOWER(?)', (old_name,))
        arrow_count = cursor.fetchone()['count']
        
        if arrow_count == 0:
            logger.warning(f"No arrows found for manufacturer '{old_name}'")
            return {'arrows_updated': 0, 'spine_specs_updated': 0}
        
        if dry_run:
            logger.info(f"DRY RUN: Would rename '{old_name}' to '{new_name}' for {arrow_count} arrows")
            return {'arrows_updated': arrow_count, 'spine_specs_updated': 0}
        
        # Update arrows table
        cursor.execute('''
            UPDATE arrows 
            SET manufacturer = ?
            WHERE LOWER(manufacturer) = LOWER(?)
        ''', (new_name, old_name))
        
        arrows_updated = cursor.rowcount
        
        # Check if there are any direct manufacturer references in spine_specifications
        # (This shouldn't normally happen, but let's be thorough)
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM spine_specifications s
            JOIN arrows a ON s.arrow_id = a.id
            WHERE LOWER(a.manufacturer) = LOWER(?)
        ''', (new_name,))
        spine_specs_count = cursor.fetchone()['count']
        
        if not dry_run:
            self.conn.commit()
            logger.info(f"Successfully renamed '{old_name}' to '{new_name}'")
            logger.info(f"  - Updated {arrows_updated} arrows")
            logger.info(f"  - Associated with {spine_specs_count} spine specifications")
        
        return {
            'arrows_updated': arrows_updated,
            'spine_specs_updated': spine_specs_count
        }
    
    def remove_manufacturer(self, manufacturer: str, dry_run: bool = False) -> Dict[str, int]:
        """Remove all arrows and data for a manufacturer"""
        cursor = self.conn.cursor()
        
        # Get arrow IDs for this manufacturer
        cursor.execute('SELECT id FROM arrows WHERE LOWER(manufacturer) = LOWER(?)', (manufacturer,))
        arrow_ids = [row['id'] for row in cursor.fetchall()]
        
        if not arrow_ids:
            logger.warning(f"No arrows found for manufacturer '{manufacturer}'")
            return {'arrows_removed': 0, 'spine_specs_removed': 0}
        
        # Count spine specifications
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM spine_specifications 
            WHERE arrow_id IN ({})
        '''.format(','.join('?' * len(arrow_ids))), arrow_ids)
        spine_specs_count = cursor.fetchone()['count']
        
        if dry_run:
            logger.info(f"DRY RUN: Would remove manufacturer '{manufacturer}'")
            logger.info(f"  - {len(arrow_ids)} arrows")
            logger.info(f"  - {spine_specs_count} spine specifications")
            return {'arrows_removed': len(arrow_ids), 'spine_specs_removed': spine_specs_count}
        
        # Remove spine specifications first (foreign key constraint)
        cursor.execute('''
            DELETE FROM spine_specifications 
            WHERE arrow_id IN ({})
        '''.format(','.join('?' * len(arrow_ids))), arrow_ids)
        
        spine_specs_removed = cursor.rowcount
        
        # Remove arrows
        cursor.execute('DELETE FROM arrows WHERE LOWER(manufacturer) = LOWER(?)', (manufacturer,))
        arrows_removed = cursor.rowcount
        
        self.conn.commit()
        logger.info(f"Successfully removed manufacturer '{manufacturer}'")
        logger.info(f"  - Removed {arrows_removed} arrows")
        logger.info(f"  - Removed {spine_specs_removed} spine specifications")
        
        return {
            'arrows_removed': arrows_removed,
            'spine_specs_removed': spine_specs_removed
        }
    
    def save_manufacturer_data(self, manufacturer: str, output_file: str = None) -> str:
        """Save all data for a manufacturer to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = manufacturer.replace(' ', '_').replace('/', '_')
            output_file = f"data/backup/{safe_name}_{timestamp}.json"
        
        # Ensure backup directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        cursor = self.conn.cursor()
        
        # Get all arrows for this manufacturer
        cursor.execute('''
            SELECT a.*, 
                   GROUP_CONCAT(s.id) as spine_spec_ids
            FROM arrows a
            LEFT JOIN spine_specifications s ON a.id = s.arrow_id
            WHERE LOWER(a.manufacturer) = LOWER(?)
            GROUP BY a.id
        ''', (manufacturer,))
        
        arrows_data = []
        for arrow_row in cursor.fetchall():
            arrow_dict = dict(arrow_row)
            arrow_id = arrow_dict['id']
            
            # Get spine specifications for this arrow
            cursor.execute('SELECT * FROM spine_specifications WHERE arrow_id = ?', (arrow_id,))
            spine_specs = [dict(row) for row in cursor.fetchall()]
            
            arrow_dict['spine_specifications'] = spine_specs
            arrows_data.append(arrow_dict)
        
        # Create export data structure
        export_data = {
            'export_metadata': {
                'manufacturer': manufacturer,
                'export_date': datetime.now().isoformat(),
                'arrow_count': len(arrows_data),
                'total_spine_specs': sum(len(arrow['spine_specifications']) for arrow in arrows_data),
                'database_file': self.database_path
            },
            'arrows': arrows_data
        }
        
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Manufacturer '{manufacturer}' data saved to: {output_file}")
        logger.info(f"  - {len(arrows_data)} arrows exported")
        logger.info(f"  - {export_data['export_metadata']['total_spine_specs']} spine specifications")
        
        return output_file
    
    def merge_manufacturers(self, source_manufacturer: str, target_manufacturer: str, dry_run: bool = False) -> Dict[str, int]:
        """Merge one manufacturer into another"""
        cursor = self.conn.cursor()
        
        # Check if both manufacturers exist
        cursor.execute('SELECT COUNT(*) as count FROM arrows WHERE LOWER(manufacturer) = LOWER(?)', (source_manufacturer,))
        source_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM arrows WHERE LOWER(manufacturer) = LOWER(?)', (target_manufacturer,))
        target_count = cursor.fetchone()['count']
        
        if source_count == 0:
            logger.warning(f"Source manufacturer '{source_manufacturer}' not found")
            return {'arrows_merged': 0}
        
        if target_count == 0:
            logger.warning(f"Target manufacturer '{target_manufacturer}' not found")
            logger.info(f"This will effectively rename '{source_manufacturer}' to '{target_manufacturer}'")
        
        if dry_run:
            logger.info(f"DRY RUN: Would merge '{source_manufacturer}' into '{target_manufacturer}'")
            logger.info(f"  - {source_count} arrows would be moved")
            return {'arrows_merged': source_count}
        
        # Update the manufacturer name
        cursor.execute('''
            UPDATE arrows 
            SET manufacturer = ?
            WHERE LOWER(manufacturer) = LOWER(?)
        ''', (target_manufacturer, source_manufacturer))
        
        arrows_merged = cursor.rowcount
        self.conn.commit()
        
        logger.info(f"Successfully merged '{source_manufacturer}' into '{target_manufacturer}'")
        logger.info(f"  - {arrows_merged} arrows moved")
        
        return {'arrows_merged': arrows_merged}
    
    def find_duplicates(self, use_fuzzy: bool = True) -> List[Dict[str, Any]]:
        """Find potential duplicate arrows using fuzzy matching on model names"""
        cursor = self.conn.cursor()
        
        if not use_fuzzy:
            # Fall back to exact matching
            cursor.execute('''
                SELECT manufacturer, model_name, COUNT(*) as count,
                       GROUP_CONCAT(id) as arrow_ids,
                       GROUP_CONCAT(material) as materials,
                       GROUP_CONCAT(arrow_type) as arrow_types
                FROM arrows 
                GROUP BY LOWER(manufacturer), LOWER(model_name)
                HAVING COUNT(*) > 1
                ORDER BY manufacturer, model_name
            ''')
            
            duplicates = []
            for row in cursor.fetchall():
                duplicates.append({
                    'manufacturer': row['manufacturer'],
                    'model_name': row['model_name'],
                    'count': row['count'],
                    'arrow_ids': [int(id) for id in row['arrow_ids'].split(',')],
                    'materials': row['materials'].split(','),
                    'arrow_types': row['arrow_types'].split(','),
                    'similarity_scores': [1.0] * row['count'],  # Exact matches
                    'match_type': 'exact'
                })
            
            return duplicates
        
        # Get all arrows for fuzzy comparison
        cursor.execute('''
            SELECT id, manufacturer, model_name, material, arrow_type
            FROM arrows 
            ORDER BY manufacturer, model_name
        ''')
        
        all_arrows = [dict(row) for row in cursor.fetchall()]
        
        # Group arrows by manufacturer first (for efficiency)
        manufacturer_groups = {}
        for arrow in all_arrows:
            mfr = arrow['manufacturer'].lower()
            if mfr not in manufacturer_groups:
                manufacturer_groups[mfr] = []
            manufacturer_groups[mfr].append(arrow)
        
        duplicate_groups = []
        processed_ids = set()
        
        # For each manufacturer, find similar arrows
        for manufacturer, arrows in manufacturer_groups.items():
            for i, arrow1 in enumerate(arrows):
                if arrow1['id'] in processed_ids:
                    continue
                
                # Find all similar arrows to this one
                similar_group = [arrow1]
                similarity_scores = [1.0]  # Self-similarity is 1.0
                
                for j, arrow2 in enumerate(arrows[i+1:], i+1):
                    if arrow2['id'] in processed_ids:
                        continue
                    
                    is_similar, similarity = self.are_similar_arrows(arrow1, arrow2)
                    if is_similar:
                        similar_group.append(arrow2)
                        similarity_scores.append(similarity)
                        processed_ids.add(arrow2['id'])
                
                # If we found duplicates, add to results
                if len(similar_group) > 1:
                    processed_ids.add(arrow1['id'])
                    
                    duplicate_groups.append({
                        'manufacturer': arrow1['manufacturer'],
                        'model_name': arrow1['model_name'],  # Use first arrow's name as representative
                        'count': len(similar_group),
                        'arrow_ids': [arrow['id'] for arrow in similar_group],
                        'materials': [arrow['material'] for arrow in similar_group],
                        'arrow_types': [arrow['arrow_type'] for arrow in similar_group],
                        'model_names': [arrow['model_name'] for arrow in similar_group],
                        'similarity_scores': similarity_scores,
                        'match_type': 'fuzzy'
                    })
        
        return duplicate_groups
    
    def clean_duplicate_arrows(self, dry_run: bool = False, use_fuzzy: bool = True) -> Dict[str, int]:
        """Remove duplicate arrows, keeping the one with most spine specifications"""
        duplicates = self.find_duplicates(use_fuzzy=use_fuzzy)
        
        if not duplicates:
            logger.info("No duplicate arrows found")
            return {'duplicates_removed': 0}
        
        removed_count = 0
        cursor = self.conn.cursor()
        
        for duplicate in duplicates:
            arrow_ids = duplicate['arrow_ids']
            
            # Find which arrow has the most spine specifications
            spine_counts = []
            for arrow_id in arrow_ids:
                cursor.execute('SELECT COUNT(*) as count FROM spine_specifications WHERE arrow_id = ?', (arrow_id,))
                spine_counts.append((arrow_id, cursor.fetchone()['count']))
            
            # Sort by spine count (descending), keep the first one
            spine_counts.sort(key=lambda x: x[1], reverse=True)
            keep_arrow_id = spine_counts[0][0]
            remove_ids = [id for id, _ in spine_counts[1:]]
            
            # Enhanced logging for fuzzy matches
            if duplicate.get('match_type') == 'fuzzy':
                logger.info(f"Fuzzy duplicate: {duplicate['manufacturer']}")
                for i, (model_name, similarity) in enumerate(zip(duplicate['model_names'], duplicate['similarity_scores'])):
                    status = "KEEP" if duplicate['arrow_ids'][i] == keep_arrow_id else "REMOVE"
                    logger.info(f"  [{status}] ID {duplicate['arrow_ids'][i]}: '{model_name}' (similarity: {similarity:.2f})")
                logger.info(f"  Keeping arrow ID {keep_arrow_id} ({spine_counts[0][1]} spine specs)")
            else:
                logger.info(f"Exact duplicate: {duplicate['manufacturer']} {duplicate['model_name']}")
                logger.info(f"  Keeping arrow ID {keep_arrow_id} ({spine_counts[0][1]} spine specs)")
                logger.info(f"  Removing IDs: {remove_ids}")
            
            if not dry_run:
                # Remove spine specifications for arrows we're deleting
                for remove_id in remove_ids:
                    cursor.execute('DELETE FROM spine_specifications WHERE arrow_id = ?', (remove_id,))
                    cursor.execute('DELETE FROM arrows WHERE id = ?', (remove_id,))
                
                removed_count += len(remove_ids)
        
        if not dry_run:
            self.conn.commit()
            logger.info(f"Removed {removed_count} duplicate arrows using {'fuzzy' if use_fuzzy else 'exact'} matching")
        else:
            total_would_remove = sum(len(dup['arrow_ids']) - 1 for dup in duplicates)
            logger.info(f"DRY RUN: Would remove {total_would_remove} duplicate arrows using {'fuzzy' if use_fuzzy else 'exact'} matching")
        
        return {'duplicates_removed': removed_count}
    
    def validate_database(self) -> Dict[str, Any]:
        """Validate database integrity and return issues"""
        cursor = self.conn.cursor()
        issues = {
            'orphaned_spine_specs': [],
            'arrows_without_spine_specs': [],
            'invalid_spine_values': [],
            'missing_required_fields': []
        }
        
        # Check for orphaned spine specifications
        cursor.execute('''
            SELECT s.id, s.arrow_id 
            FROM spine_specifications s
            LEFT JOIN arrows a ON s.arrow_id = a.id
            WHERE a.id IS NULL
        ''')
        issues['orphaned_spine_specs'] = [dict(row) for row in cursor.fetchall()]
        
        # Check for arrows without spine specifications
        cursor.execute('''
            SELECT a.id, a.manufacturer, a.model_name
            FROM arrows a
            LEFT JOIN spine_specifications s ON a.id = s.arrow_id
            WHERE s.id IS NULL
        ''')
        issues['arrows_without_spine_specs'] = [dict(row) for row in cursor.fetchall()]
        
        # Check for invalid spine values
        cursor.execute('''
            SELECT s.id, s.arrow_id, s.spine, a.manufacturer, a.model_name
            FROM spine_specifications s
            JOIN arrows a ON s.arrow_id = a.id
            WHERE s.spine IS NULL OR s.spine < 100 OR s.spine > 2000
        ''')
        issues['invalid_spine_values'] = [dict(row) for row in cursor.fetchall()]
        
        # Check for missing required fields
        cursor.execute('''
            SELECT id, manufacturer, model_name
            FROM arrows
            WHERE manufacturer IS NULL OR manufacturer = '' 
               OR model_name IS NULL OR model_name = ''
        ''')
        issues['missing_required_fields'] = [dict(row) for row in cursor.fetchall()]
        
        return issues
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get comprehensive database statistics"""
        cursor = self.conn.cursor()
        
        # Total counts
        cursor.execute('SELECT COUNT(*) as count FROM arrows')
        total_arrows = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM spine_specifications')
        total_spine_specs = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(DISTINCT manufacturer) as count FROM arrows')
        total_manufacturers = cursor.fetchone()['count']
        
        # Data quality stats
        cursor.execute('SELECT COUNT(*) as count FROM arrows WHERE description IS NULL OR description = ""')
        arrows_missing_description = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM arrows WHERE image_url IS NULL OR image_url = ""')
        arrows_missing_images = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM arrows WHERE material IS NULL OR material = ""')
        arrows_missing_material = cursor.fetchone()['count']
        
        # Duplicates count
        cursor.execute('''
            SELECT COUNT(*) as count FROM (
                SELECT manufacturer, model_name, COUNT(*) as cnt
                FROM arrows 
                GROUP BY LOWER(manufacturer), LOWER(model_name)
                HAVING COUNT(*) > 1
            )
        ''')
        duplicate_groups = cursor.fetchone()['count']
        
        return {
            'total_arrows': total_arrows,
            'total_spine_specs': total_spine_specs,
            'total_manufacturers': total_manufacturers,
            'arrows_missing_description': arrows_missing_description,
            'arrows_missing_images': arrows_missing_images,
            'arrows_missing_material': arrows_missing_material,
            'duplicate_groups': duplicate_groups
        }
    
    def clean_database_fully(self, dry_run: bool = False, keep_manufacturers: List[str] = None) -> Dict[str, int]:
        """Comprehensive database cleaning - removes all data or keeps specified manufacturers"""
        cursor = self.conn.cursor()
        
        if keep_manufacturers:
            keep_manufacturers = [mfr.lower() for mfr in keep_manufacturers]
            
        # Get current stats
        stats_before = self.get_database_stats()
        
        if dry_run:
            if keep_manufacturers:
                logger.info(f"DRY RUN: Would clean database keeping manufacturers: {keep_manufacturers}")
                cursor.execute('''
                    SELECT COUNT(*) as count FROM arrows 
                    WHERE LOWER(manufacturer) NOT IN ({})
                '''.format(','.join('?' * len(keep_manufacturers))), keep_manufacturers)
                arrows_to_remove = cursor.fetchone()['count']
                
                cursor.execute('''
                    SELECT COUNT(*) as count FROM spine_specifications s
                    JOIN arrows a ON s.arrow_id = a.id
                    WHERE LOWER(a.manufacturer) NOT IN ({})
                '''.format(','.join('?' * len(keep_manufacturers))), keep_manufacturers)
                spine_specs_to_remove = cursor.fetchone()['count']
            else:
                logger.info("DRY RUN: Would completely clean database (remove ALL arrow data)")
                arrows_to_remove = stats_before['total_arrows']
                spine_specs_to_remove = stats_before['total_spine_specs']
            
            return {
                'arrows_removed': arrows_to_remove,
                'spine_specs_removed': spine_specs_to_remove,
                'manufacturers_kept': len(keep_manufacturers) if keep_manufacturers else 0
            }
        
        # Execute the cleaning
        if keep_manufacturers:
            # Remove arrows NOT in the keep list
            logger.info(f"Cleaning database, keeping manufacturers: {keep_manufacturers}")
            
            # Get arrow IDs to remove
            cursor.execute('''
                SELECT id FROM arrows 
                WHERE LOWER(manufacturer) NOT IN ({})
            '''.format(','.join('?' * len(keep_manufacturers))), keep_manufacturers)
            arrow_ids_to_remove = [row['id'] for row in cursor.fetchall()]
            
            if arrow_ids_to_remove:
                # Remove spine specifications first
                cursor.execute('''
                    DELETE FROM spine_specifications 
                    WHERE arrow_id IN ({})
                '''.format(','.join('?' * len(arrow_ids_to_remove))), arrow_ids_to_remove)
                spine_specs_removed = cursor.rowcount
                
                # Remove arrows
                cursor.execute('''
                    DELETE FROM arrows 
                    WHERE LOWER(manufacturer) NOT IN ({})
                '''.format(','.join('?' * len(keep_manufacturers))), keep_manufacturers)
                arrows_removed = cursor.rowcount
            else:
                arrows_removed = 0
                spine_specs_removed = 0
                
            logger.info(f"Partial database clean completed:")
            logger.info(f"  - Kept {len(keep_manufacturers)} manufacturers")
            logger.info(f"  - Removed {arrows_removed} arrows")
            logger.info(f"  - Removed {spine_specs_removed} spine specifications")
            
        else:
            # Complete database wipe
            logger.warning("COMPLETE DATABASE WIPE - Removing ALL arrow data")
            
            # Remove all spine specifications
            cursor.execute('DELETE FROM spine_specifications')
            spine_specs_removed = cursor.rowcount
            
            # Remove all arrows
            cursor.execute('DELETE FROM arrows')
            arrows_removed = cursor.rowcount
            
            # Reset auto-increment counters
            cursor.execute('DELETE FROM sqlite_sequence WHERE name IN ("arrows", "spine_specifications")')
            
            logger.info(f"Complete database clean completed:")
            logger.info(f"  - Removed {arrows_removed} arrows")
            logger.info(f"  - Removed {spine_specs_removed} spine specifications")
            logger.info(f"  - Reset ID counters")
        
        self.conn.commit()
        
        return {
            'arrows_removed': arrows_removed,
            'spine_specs_removed': spine_specs_removed,
            'manufacturers_kept': len(keep_manufacturers) if keep_manufacturers else 0
        }
    
    def reset_database_schema(self, dry_run: bool = False) -> bool:
        """Reset database to fresh schema (removes ALL data and recreates tables)"""
        if dry_run:
            logger.info("DRY RUN: Would completely reset database schema")
            logger.info("  - All tables would be dropped and recreated")
            logger.info("  - ALL DATA WOULD BE LOST")
            return True
        
        cursor = self.conn.cursor()
        
        logger.warning("COMPLETE DATABASE SCHEMA RESET - ALL DATA WILL BE LOST")
        
        try:
            # Drop existing tables
            cursor.execute('DROP TABLE IF EXISTS spine_specifications')
            cursor.execute('DROP TABLE IF EXISTS arrows')
            cursor.execute('DELETE FROM sqlite_sequence')
            
            # Recreate arrows table
            cursor.execute('''
                CREATE TABLE arrows (
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
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Recreate spine_specifications table
            cursor.execute('''
                CREATE TABLE spine_specifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arrow_id INTEGER,
                    spine INTEGER,
                    outer_diameter REAL,
                    inner_diameter REAL,
                    gpi_weight REAL,
                    length_options TEXT,
                    wall_thickness REAL,
                    insert_weight_range TEXT,
                    nock_size TEXT,
                    notes TEXT,
                    straightness_tolerance TEXT,
                    weight_tolerance TEXT,
                    diameter_category TEXT,
                    FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX idx_arrows_manufacturer ON arrows(manufacturer)')
            cursor.execute('CREATE INDEX idx_arrows_model ON arrows(model_name)')
            cursor.execute('CREATE INDEX idx_spine_arrow_id ON spine_specifications(arrow_id)')
            cursor.execute('CREATE INDEX idx_spine_value ON spine_specifications(spine)')
            
            self.conn.commit()
            logger.info("Database schema reset completed successfully")
            logger.info("  - All tables recreated with fresh schema")
            logger.info("  - Indexes created")
            logger.info("  - Database is now empty and ready for imports")
            
            return True
            
        except Exception as e:
            logger.error(f"Schema reset failed: {e}")
            self.conn.rollback()
            return False


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="Arrow Database Cleaning and Maintenance Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all manufacturers
  python database_cleaner.py --list-manufacturers
  
  # Rename manufacturer
  python database_cleaner.py --rename-manufacturer "BigArchery" "Cross-X"
  
  # Preview rename (dry run)
  python database_cleaner.py --rename-manufacturer "BigArchery" "Cross-X" --dry-run
  
  # Remove manufacturer completely
  python database_cleaner.py --remove-manufacturer "Test Manufacturer"
  
  # Save manufacturer data before removing
  python database_cleaner.py --save-manufacturer "BigArchery" --output bigarchery_backup.json
  
  # List arrows for specific manufacturer
  python database_cleaner.py --list-arrows "Gold Tip"
  
  # Find and clean duplicates (uses fuzzy matching by default)
  python database_cleaner.py --find-duplicates
  python database_cleaner.py --clean-duplicates
  
  # Use exact matching only
  python database_cleaner.py --find-duplicates --exact-match
  python database_cleaner.py --clean-duplicates --exact-match
  
  # Adjust fuzzy matching sensitivity (0.0-1.0, default: 0.85)
  python database_cleaner.py --find-duplicates --similarity-threshold 0.75
  python database_cleaner.py --clean-duplicates --similarity-threshold 0.90
  
  # Merge manufacturers
  python database_cleaner.py --merge-manufacturers "BigArchery" "Cross-X"
  
  # Validate database integrity
  python database_cleaner.py --validate
  
  # Show comprehensive database statistics
  python database_cleaner.py --stats
  
  # Clean database completely (removes ALL data)
  python database_cleaner.py --clean-all --dry-run  # Preview first
  python database_cleaner.py --clean-all
  
  # Clean database but keep specific manufacturers
  python database_cleaner.py --clean-keep "Easton" "Gold Tip" --dry-run
  python database_cleaner.py --clean-keep "Easton" "Gold Tip"
  
  # Reset database schema (DANGER: removes all data and recreates tables)
  python database_cleaner.py --reset-schema --dry-run
  python database_cleaner.py --reset-schema
        """
    )
    
    parser.add_argument('--database', default='arrow_database.db',
                      help='Path to arrow database (default: arrow_database.db)')
    
    # Manufacturer operations
    parser.add_argument('--list-manufacturers', action='store_true',
                      help='List all manufacturers with statistics')
    parser.add_argument('--list-arrows', metavar='MANUFACTURER',
                      help='List all arrows for a specific manufacturer')
    parser.add_argument('--rename-manufacturer', nargs=2, metavar=('OLD_NAME', 'NEW_NAME'),
                      help='Rename a manufacturer')
    parser.add_argument('--remove-manufacturer', metavar='MANUFACTURER',
                      help='Remove all data for a manufacturer')
    parser.add_argument('--save-manufacturer', metavar='MANUFACTURER',
                      help='Save manufacturer data to JSON file')
    parser.add_argument('--merge-manufacturers', nargs=2, metavar=('SOURCE', 'TARGET'),
                      help='Merge source manufacturer into target manufacturer')
    
    # Data cleaning operations
    parser.add_argument('--find-duplicates', action='store_true',
                      help='Find potential duplicate arrows using fuzzy matching')
    parser.add_argument('--clean-duplicates', action='store_true',
                      help='Remove duplicate arrows (keeps most complete)')
    parser.add_argument('--validate', action='store_true',
                      help='Validate database integrity')
    parser.add_argument('--stats', action='store_true',
                      help='Show comprehensive database statistics')
    
    # Fuzzy matching options
    parser.add_argument('--exact-match', action='store_true',
                      help='Use exact matching instead of fuzzy matching for duplicates')
    parser.add_argument('--similarity-threshold', type=float, default=0.85,
                      help='Similarity threshold for fuzzy matching (0.0-1.0, default: 0.85)')
    
    # Full database cleaning operations
    parser.add_argument('--clean-all', action='store_true',
                      help='Remove ALL arrow data from database')
    parser.add_argument('--clean-keep', nargs='+', metavar='MANUFACTURER',
                      help='Remove all data EXCEPT specified manufacturers')
    parser.add_argument('--reset-schema', action='store_true',
                      help='Reset database schema (removes ALL data and recreates tables)')
    
    # Options
    parser.add_argument('--dry-run', action='store_true',
                      help='Show what would be done without making changes')
    parser.add_argument('--output', metavar='FILE',
                      help='Output file for save operations')
    parser.add_argument('--backup', action='store_true', default=True,
                      help='Create backup before destructive operations (default: True)')
    parser.add_argument('--no-backup', action='store_true',
                      help='Skip creating backup')
    
    args = parser.parse_args()
    
    # Create cleaner instance with similarity threshold
    cleaner = DatabaseCleaner(args.database, similarity_threshold=args.similarity_threshold)
    cleaner.connect()
    
    # Determine if we need a backup
    destructive_ops = [
        args.rename_manufacturer, args.remove_manufacturer, 
        args.merge_manufacturers, args.clean_duplicates,
        args.clean_all, args.clean_keep, args.reset_schema
    ]
    needs_backup = any(destructive_ops) and not args.dry_run and not args.no_backup
    
    if needs_backup:
        cleaner.backup_database()
    
    try:
        # Execute requested operations
        if args.list_manufacturers:
            manufacturers = cleaner.list_manufacturers()
            print("\n" + "="*80)
            print("MANUFACTURERS IN DATABASE")
            print("="*80)
            print(f"{'Manufacturer':<25} {'Arrows':<8} {'Spines':<8} {'Spine Range':<15}")
            print("-"*80)
            for mfr in manufacturers:
                spine_range = ""
                if mfr['min_spine'] and mfr['max_spine']:
                    spine_range = f"{mfr['min_spine']}-{mfr['max_spine']}"
                print(f"{mfr['manufacturer']:<25} {mfr['arrow_count']:<8} {mfr['spine_count']:<8} {spine_range:<15}")
            print("="*80)
            print(f"Total manufacturers: {len(manufacturers)}")
        
        elif args.list_arrows:
            arrows = cleaner.list_arrows_by_manufacturer(args.list_arrows)
            print(f"\n" + "="*80)
            print(f"ARROWS FOR: {args.list_arrows}")
            print("="*80)
            if arrows:
                print(f"{'ID':<6} {'Model Name':<25} {'Material':<12} {'Spines':<15}")
                print("-"*80)
                for arrow in arrows:
                    spines_str = ','.join(arrow['spines'][:5])  # Show first 5 spines
                    if len(arrow['spines']) > 5:
                        spines_str += "..."
                    print(f"{arrow['id']:<6} {arrow['model_name']:<25} {arrow['material'] or 'N/A':<12} {spines_str:<15}")
                print("="*80)
                print(f"Total arrows: {len(arrows)}")
            else:
                print(f"No arrows found for manufacturer '{args.list_arrows}'")
        
        elif args.rename_manufacturer:
            old_name, new_name = args.rename_manufacturer
            result = cleaner.rename_manufacturer(old_name, new_name, args.dry_run)
            print(f"\nRename operation completed:")
            print(f"  Arrows updated: {result['arrows_updated']}")
        
        elif args.remove_manufacturer:
            result = cleaner.remove_manufacturer(args.remove_manufacturer, args.dry_run)
            print(f"\nRemove operation completed:")
            print(f"  Arrows removed: {result['arrows_removed']}")
            print(f"  Spine specs removed: {result['spine_specs_removed']}")
        
        elif args.save_manufacturer:
            output_file = cleaner.save_manufacturer_data(args.save_manufacturer, args.output)
            print(f"\nManufacturer data saved to: {output_file}")
        
        elif args.merge_manufacturers:
            source, target = args.merge_manufacturers
            result = cleaner.merge_manufacturers(source, target, args.dry_run)
            print(f"\nMerge operation completed:")
            print(f"  Arrows merged: {result['arrows_merged']}")
        
        elif args.find_duplicates:
            use_fuzzy = not args.exact_match
            duplicates = cleaner.find_duplicates(use_fuzzy=use_fuzzy)
            if duplicates:
                print(f"\n" + "="*80)
                print("POTENTIAL DUPLICATE ARROWS")
                print("="*80)
                for dup in duplicates:
                    print(f"{dup['manufacturer']} - {dup['model_name']}")
                    print(f"  Count: {dup['count']} | Match Type: {dup.get('match_type', 'exact').upper()}")
                    print(f"  IDs: {dup['arrow_ids']}")
                    
                    if dup.get('match_type') == 'fuzzy' and 'model_names' in dup:
                        print(f"  Model variations:")
                        for i, (model_name, similarity) in enumerate(zip(dup['model_names'], dup['similarity_scores'])):
                            print(f"    ID {dup['arrow_ids'][i]}: '{model_name}' (similarity: {similarity:.2f})")
                    
                    materials = set(filter(None, dup['materials']))  # Remove None/empty values
                    if materials:
                        print(f"  Materials: {materials}")
                    print()
                print(f"Total duplicate groups: {len(duplicates)}")
                
                # Summary by match type
                exact_count = sum(1 for dup in duplicates if dup.get('match_type') == 'exact')
                fuzzy_count = sum(1 for dup in duplicates if dup.get('match_type') == 'fuzzy')
                print(f"Exact matches: {exact_count}, Fuzzy matches: {fuzzy_count}")
                if use_fuzzy:
                    print(f"Similarity threshold: {args.similarity_threshold}")
            else:
                match_type = "exact" if args.exact_match else "fuzzy"
                print(f"\nNo duplicate arrows found using {match_type} matching.")
        
        elif args.clean_duplicates:
            use_fuzzy = not args.exact_match
            result = cleaner.clean_duplicate_arrows(args.dry_run, use_fuzzy=use_fuzzy)
            print(f"\nDuplicate cleaning completed:")
            print(f"  Duplicates removed: {result['duplicates_removed']}")
        
        elif args.validate:
            issues = cleaner.validate_database()
            print(f"\n" + "="*60)
            print("DATABASE VALIDATION RESULTS")
            print("="*60)
            
            total_issues = sum(len(issue_list) for issue_list in issues.values())
            
            if total_issues == 0:
                print("✅ Database validation passed - no issues found!")
            else:
                print(f"❌ Found {total_issues} issues:")
                
                if issues['orphaned_spine_specs']:
                    print(f"\n🔸 Orphaned spine specifications: {len(issues['orphaned_spine_specs'])}")
                    for spec in issues['orphaned_spine_specs'][:5]:
                        print(f"    Spec ID {spec['id']} references missing arrow {spec['arrow_id']}")
                
                if issues['arrows_without_spine_specs']:
                    print(f"\n🔸 Arrows without spine specs: {len(issues['arrows_without_spine_specs'])}")
                    for arrow in issues['arrows_without_spine_specs'][:5]:
                        print(f"    {arrow['manufacturer']} {arrow['model_name']} (ID: {arrow['id']})")
                
                if issues['invalid_spine_values']:
                    print(f"\n🔸 Invalid spine values: {len(issues['invalid_spine_values'])}")
                    for spec in issues['invalid_spine_values'][:5]:
                        print(f"    {spec['manufacturer']} {spec['model_name']} - spine: {spec['spine']}")
                
                if issues['missing_required_fields']:
                    print(f"\n🔸 Missing required fields: {len(issues['missing_required_fields'])}")
                    for arrow in issues['missing_required_fields'][:5]:
                        print(f"    ID {arrow['id']}: manufacturer='{arrow['manufacturer']}' model='{arrow['model_name']}'")
        
        elif args.stats:
            stats = cleaner.get_database_stats()
            print(f"\n" + "="*60)
            print("DATABASE STATISTICS")
            print("="*60)
            print(f"Total arrows: {stats['total_arrows']}")
            print(f"Total spine specifications: {stats['total_spine_specs']}")
            print(f"Total manufacturers: {stats['total_manufacturers']}")
            print(f"Arrows missing description: {stats['arrows_missing_description']}")
            print(f"Arrows missing images: {stats['arrows_missing_images']}")
            print(f"Arrows missing material: {stats['arrows_missing_material']}")
            print(f"Duplicate arrow groups: {stats['duplicate_groups']}")
            print("="*60)
            
            # Calculate completeness percentages
            if stats['total_arrows'] > 0:
                desc_pct = ((stats['total_arrows'] - stats['arrows_missing_description']) / stats['total_arrows']) * 100
                img_pct = ((stats['total_arrows'] - stats['arrows_missing_images']) / stats['total_arrows']) * 100
                mat_pct = ((stats['total_arrows'] - stats['arrows_missing_material']) / stats['total_arrows']) * 100
                
                print(f"\nData Completeness:")
                print(f"Descriptions: {desc_pct:.1f}%")
                print(f"Images: {img_pct:.1f}%")
                print(f"Materials: {mat_pct:.1f}%")
        
        elif args.clean_all:
            if not args.dry_run:
                print("\n⚠️  WARNING: This will remove ALL arrow data from the database!")
                response = input("Are you sure you want to continue? Type 'YES' to confirm: ")
                if response != 'YES':
                    print("Operation cancelled.")
                    return 0
            
            result = cleaner.clean_database_fully(args.dry_run)
            print(f"\nDatabase cleaning completed:")
            print(f"  Arrows removed: {result['arrows_removed']}")
            print(f"  Spine specs removed: {result['spine_specs_removed']}")
        
        elif args.clean_keep:
            if not args.dry_run:
                print(f"\n⚠️  WARNING: This will remove all data EXCEPT for manufacturers: {args.clean_keep}")
                response = input("Are you sure you want to continue? Type 'YES' to confirm: ")
                if response != 'YES':
                    print("Operation cancelled.")
                    return 0
            
            result = cleaner.clean_database_fully(args.dry_run, keep_manufacturers=args.clean_keep)
            print(f"\nSelective database cleaning completed:")
            print(f"  Manufacturers kept: {result['manufacturers_kept']}")
            print(f"  Arrows removed: {result['arrows_removed']}")
            print(f"  Spine specs removed: {result['spine_specs_removed']}")
        
        elif args.reset_schema:
            if not args.dry_run:
                print("\n⚠️  DANGER: This will completely reset the database schema!")
                print("ALL DATA WILL BE PERMANENTLY LOST!")
                response = input("Are you absolutely sure? Type 'RESET' to confirm: ")
                if response != 'RESET':
                    print("Operation cancelled.")
                    return 0
            
            success = cleaner.reset_database_schema(args.dry_run)
            if success:
                print("\nDatabase schema reset completed successfully.")
            else:
                print("\n❌ Schema reset failed. Check logs for details.")
                return 1
        
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return 1
    
    finally:
        if cleaner.conn:
            cleaner.conn.close()
    
    return 0


if __name__ == "__main__":
    exit(main())