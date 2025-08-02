#!/usr/bin/env python3
"""
Length Fallback System for Arrow Database
Provides standard length_options when manufacturer data is missing
Based on Skylon Archery standard length table
"""

import json
import sqlite3
from typing import List, Optional, Dict, Any

class LengthFallbackSystem:
    """Manages fallback length options based on industry standards"""
    
    # Standard length mapping based on Skylon Archery table
    # Format: spine_range -> standard_length_inches
    STANDARD_LENGTH_MAP = {
        # Ultra stiff spines (1000, 900, 850, 800, 750, 700, 650) -> 30-31"
        (1000, float('inf')): [30.0],     # 1.000" spine -> 30"
        (900, 999): [30.0],               # 0.900" spine -> 30"
        (850, 899): [30.0],               # 0.850" spine -> 30"
        (800, 849): [31.0],               # 0.800" spine -> 31"
        (750, 799): [31.0],               # 0.750" spine -> 31"
        (700, 749): [31.0],               # 0.700" spine -> 31"
        (650, 699): [31.0],               # 0.650" spine -> 31"
        
        # Medium-stiff spines (600, 550, 500, 450, 400, 350) -> 32"
        (600, 649): [32.0],               # 0.600" spine -> 32"
        (550, 599): [32.0],               # 0.550" spine -> 32"
        (500, 549): [32.0],               # 0.500" spine -> 32"
        (450, 499): [32.0],               # 0.450" spine -> 32"
        (400, 449): [32.0],               # 0.400" spine -> 32"
        (350, 399): [32.0],               # 0.350" spine -> 32"
        
        # Softer spines and compounds -> 30-32" range
        (300, 349): [30.0, 31.0, 32.0],   # Common compound spine range
        (250, 299): [30.0, 31.0, 32.0],   # Common compound spine range
        (200, 249): [30.0, 31.0, 32.0],   # Compound range
        (0, 199): [30.0, 31.0, 32.0]      # Very soft or custom spines
    }
    
    def __init__(self, database_path: str = "arrow_database.db"):
        """Initialize with database path"""
        self.database_path = database_path
    
    def get_standard_length_for_spine(self, spine: int) -> List[float]:
        """
        Get standard length options for a given spine value
        
        Args:
            spine: Spine value (stiffness)
            
        Returns:
            List of standard length options in inches
        """
        for (min_spine, max_spine), lengths in self.STANDARD_LENGTH_MAP.items():
            if min_spine <= spine <= max_spine:
                return lengths
        
        # Fallback to common arrow lengths
        return [30.0, 31.0, 32.0]
    
    def apply_fallback_lengths(self, force_update: bool = False) -> Dict[str, int]:
        """
        Apply fallback length options to arrows missing length data
        
        Args:
            force_update: If True, update all arrows. If False, only update null/empty length_options
            
        Returns:
            Dictionary with statistics about updates
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        stats = {
            'arrows_checked': 0,
            'spine_specs_updated': 0,
            'manufacturers_affected': set()
        }
        
        try:
            # Get all spine specifications that need length_options
            if force_update:
                query = """
                    SELECT s.id, s.spine, a.manufacturer, a.model_name, s.length_options
                    FROM spine_specifications s
                    JOIN arrows a ON s.arrow_id = a.id
                """
            else:
                query = """
                    SELECT s.id, s.spine, a.manufacturer, a.model_name, s.length_options
                    FROM spine_specifications s
                    JOIN arrows a ON s.arrow_id = a.id
                    WHERE s.length_options IS NULL OR s.length_options = '[]' OR s.length_options = 'null'
                """
            
            cursor.execute(query)
            specs_to_update = cursor.fetchall()
            
            stats['arrows_checked'] = len(specs_to_update)
            
            # Update each specification
            for spec_id, spine, manufacturer, model_name, current_length_options in specs_to_update:
                # Skip if already has valid length_options (unless force_update)
                if not force_update and current_length_options:
                    try:
                        existing_lengths = json.loads(current_length_options)
                        if existing_lengths and len(existing_lengths) > 0:
                            continue
                    except (json.JSONDecodeError, TypeError):
                        pass  # Continue with update if JSON is invalid
                
                # Get standard lengths for this spine
                standard_lengths = self.get_standard_length_for_spine(spine)
                length_options_json = json.dumps(standard_lengths)
                
                # Update the database
                cursor.execute("""
                    UPDATE spine_specifications 
                    SET length_options = ?
                    WHERE id = ?
                """, (length_options_json, spec_id))
                
                stats['spine_specs_updated'] += 1
                stats['manufacturers_affected'].add(manufacturer)
                
                print(f"Updated {manufacturer} {model_name} spine {spine}: {standard_lengths}")
            
            conn.commit()
            
        except Exception as e:
            print(f"Error applying fallback lengths: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        # Convert set to list for JSON serialization
        stats['manufacturers_affected'] = list(stats['manufacturers_affected'])
        
        return stats
    
    def generate_length_report(self) -> Dict[str, Any]:
        """
        Generate a report on length_options coverage in the database
        
        Returns:
            Report with statistics on length data coverage
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        report = {
            'total_spine_specs': 0,
            'specs_with_lengths': 0,
            'specs_without_lengths': 0,
            'coverage_percentage': 0.0,
            'manufacturers': {}
        }
        
        try:
            # Get overall statistics
            cursor.execute("""
                SELECT COUNT(*) as total_specs,
                       SUM(CASE WHEN s.length_options IS NOT NULL 
                                AND s.length_options != '[]' 
                                AND s.length_options != 'null' 
                                AND s.length_options != '' 
                           THEN 1 ELSE 0 END) as specs_with_lengths
                FROM spine_specifications s
            """)
            
            total_specs, specs_with_lengths = cursor.fetchone()
            report['total_spine_specs'] = total_specs
            report['specs_with_lengths'] = specs_with_lengths
            report['specs_without_lengths'] = total_specs - specs_with_lengths
            
            if total_specs > 0:
                report['coverage_percentage'] = (specs_with_lengths / total_specs) * 100
            
            # Get per-manufacturer statistics
            cursor.execute("""
                SELECT a.manufacturer,
                       COUNT(*) as total_specs,
                       SUM(CASE WHEN s.length_options IS NOT NULL 
                                AND s.length_options != '[]' 
                                AND s.length_options != 'null' 
                                AND s.length_options != '' 
                           THEN 1 ELSE 0 END) as specs_with_lengths
                FROM spine_specifications s
                JOIN arrows a ON s.arrow_id = a.id
                GROUP BY a.manufacturer
                ORDER BY a.manufacturer
            """)
            
            for manufacturer, total_specs, specs_with_lengths in cursor.fetchall():
                coverage = (specs_with_lengths / total_specs) * 100 if total_specs > 0 else 0
                report['manufacturers'][manufacturer] = {
                    'total_specs': total_specs,
                    'specs_with_lengths': specs_with_lengths,
                    'specs_without_lengths': total_specs - specs_with_lengths,
                    'coverage_percentage': coverage
                }
            
        except Exception as e:
            print(f"Error generating length report: {e}")
        finally:
            conn.close()
        
        return report

def main():
    """Main function for testing the fallback system"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Length Fallback System for Arrow Database')
    parser.add_argument('--report', action='store_true', help='Generate length coverage report')
    parser.add_argument('--apply', action='store_true', help='Apply fallback lengths to missing data')
    parser.add_argument('--force', action='store_true', help='Force update all length_options (use with --apply)')
    parser.add_argument('--database', default='arrow_database.db', help='Database file path')
    
    args = parser.parse_args()
    
    fallback_system = LengthFallbackSystem(args.database)
    
    if args.report:
        print("=== Length Options Coverage Report ===")
        report = fallback_system.generate_length_report()
        
        print(f"Total spine specifications: {report['total_spine_specs']}")
        print(f"Specs with length data: {report['specs_with_lengths']}")
        print(f"Specs without length data: {report['specs_without_lengths']}")
        print(f"Coverage: {report['coverage_percentage']:.1f}%")
        print()
        
        print("Per-Manufacturer Coverage:")
        for manufacturer, stats in report['manufacturers'].items():
            print(f"  {manufacturer}: {stats['specs_with_lengths']}/{stats['total_specs']} ({stats['coverage_percentage']:.1f}%)")
    
    if args.apply:
        print("=== Applying Fallback Length Options ===")
        if args.force:
            print("⚠️  Force mode: Will update ALL spine specifications")
        else:
            print("📝 Standard mode: Will only update missing length_options")
        
        stats = fallback_system.apply_fallback_lengths(force_update=args.force)
        
        print(f"Checked: {stats['arrows_checked']} spine specifications")
        print(f"Updated: {stats['spine_specs_updated']} spine specifications")
        print(f"Manufacturers affected: {len(stats['manufacturers_affected'])}")
        if stats['manufacturers_affected']:
            print(f"  - {', '.join(stats['manufacturers_affected'])}")

if __name__ == "__main__":
    main()