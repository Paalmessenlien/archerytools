#!/usr/bin/env python3
"""
Integration script to link components with compatible arrows
This creates compatibility relationships between scraped components and arrows
"""

import sqlite3
from typing import List, Dict, Any
from component_database import ComponentDatabase
from arrow_database import ArrowDatabase

class ComponentArrowIntegrator:
    """Integrate components with arrows based on specifications"""
    
    def __init__(self, db_path: str = "arrow_database.db"):
        self.db_path = db_path
        self.arrow_db = ArrowDatabase(db_path)
        self.component_db = ComponentDatabase(db_path)
    
    def find_compatible_arrows_for_component(self, component: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find arrows compatible with a component based on specifications"""
        compatible_arrows = []
        specs = component['specifications']
        
        # Get component dimensions
        component_inner_d = specs.get('inner_diameter_inch')
        component_outer_d = specs.get('outer_diameter_inch')
        
        if not component_inner_d and not component_outer_d:
            return compatible_arrows
        
        # Search arrows with compatible dimensions
        # For inserts: component outer diameter should fit arrow inner diameter
        # For points: component inner diameter should match arrow outer diameter
        
        if component['category_name'] == 'inserts':
            # Find arrows where insert outer diameter fits arrow inner diameter
            arrows = self.arrow_db.search_arrows(limit=1000)  # Get all arrows
            
            for arrow in arrows:
                arrow_details = self.arrow_db.get_arrow_details(arrow['id'])
                
                for spine_spec in arrow_details.get('spine_specifications', []):
                    arrow_inner_d = spine_spec.get('inner_diameter')
                    
                    if arrow_inner_d and component_outer_d:
                        # Insert fits if component OD is slightly smaller than arrow ID
                        tolerance = 0.005  # 0.005" tolerance
                        if component_outer_d <= (arrow_inner_d + tolerance):
                            compatibility_score = 1.0 - abs(component_outer_d - arrow_inner_d) / arrow_inner_d
                            compatible_arrows.append({
                                'arrow_id': arrow['id'],
                                'arrow_name': f"{arrow['manufacturer']} {arrow['model_name']}",
                                'spine': spine_spec['spine'],
                                'compatibility_score': min(compatibility_score, 1.0),
                                'notes': f"Insert OD {component_outer_d}\" fits Arrow ID {arrow_inner_d}\""
                            })
                            break  # One spine spec match is enough per arrow
        
        elif component['category_name'] == 'points':
            # For points, match based on compatibility info or diameter
            compatibility_info = specs.get('compatibility', [])
            
            # Try to extract diameter info from compatibility strings
            # e.g., "Full Bore (9.8/10.7)" -> inner/outer diameter in mm
            for compat_str in compatibility_info:
                if '(' in compat_str and ')' in compat_str:
                    # Extract dimensions from compatibility string
                    dimensions = compat_str.split('(')[1].split(')')[0]
                    if '/' in dimensions:
                        try:
                            inner_mm, outer_mm = dimensions.split('/')
                            inner_mm = float(inner_mm)
                            outer_mm = float(outer_mm)
                            
                            # Convert to inches for comparison
                            target_inner_inch = inner_mm / 25.4
                            target_outer_inch = outer_mm / 25.4
                            
                            # Find arrows with matching inner diameter
                            arrows = self.arrow_db.search_arrows(limit=1000)
                            
                            for arrow in arrows:
                                arrow_details = self.arrow_db.get_arrow_details(arrow['id'])
                                
                                for spine_spec in arrow_details.get('spine_specifications', []):
                                    arrow_inner_d = spine_spec.get('inner_diameter')
                                    
                                    if arrow_inner_d:
                                        tolerance = 0.010  # 0.010" tolerance for points
                                        if abs(arrow_inner_d - target_inner_inch) <= tolerance:
                                            compatibility_score = 1.0 - abs(arrow_inner_d - target_inner_inch) / target_inner_inch
                                            compatible_arrows.append({
                                                'arrow_id': arrow['id'],
                                                'arrow_name': f"{arrow['manufacturer']} {arrow['model_name']}",
                                                'spine': spine_spec['spine'],
                                                'compatibility_score': min(compatibility_score, 1.0),
                                                'notes': f"Point for {compat_str} matches Arrow ID {arrow_inner_d:.3f}\""
                                            })
                                            break
                        except ValueError:
                            continue
        
        return compatible_arrows
    
    def create_compatibility_relationships(self, dry_run: bool = True) -> Dict[str, Any]:
        """Create compatibility relationships between components and arrows"""
        
        print("🔗 Creating Component-Arrow Compatibility Relationships")
        print("=" * 60)
        
        # Get all components
        components = []
        for category in ['points', 'inserts', 'nocks']:
            category_components = self.component_db.get_components(category, limit=100)
            components.extend(category_components)
        
        total_relationships = 0
        component_matches = {}
        
        for component in components:
            print(f"\n📦 Analyzing: {component['manufacturer']} {component['model_name']}")
            
            compatible_arrows = self.find_compatible_arrows_for_component(component)
            
            if compatible_arrows:
                print(f"   ✅ Found {len(compatible_arrows)} compatible arrows")
                component_matches[component['id']] = {
                    'component_name': component['model_name'],
                    'category': component['category_name'],
                    'compatible_arrows': compatible_arrows
                }
                
                if not dry_run:
                    # Add compatibility relationships to database
                    for arrow_match in compatible_arrows[:5]:  # Limit to top 5 matches
                        success = self.component_db.add_compatibility(
                            arrow_id=arrow_match['arrow_id'],
                            component_id=component['id'],
                            compatibility_type='direct' if arrow_match['compatibility_score'] > 0.9 else 'universal',
                            score=arrow_match['compatibility_score'],
                            notes=arrow_match['notes']
                        )
                        if success:
                            total_relationships += 1
                
                # Show sample matches
                for match in compatible_arrows[:3]:
                    print(f"      • {match['arrow_name']} (spine {match['spine']}) - Score: {match['compatibility_score']:.2f}")
            else:
                print(f"   ⚠️  No compatible arrows found")
        
        print(f"\n📊 COMPATIBILITY ANALYSIS SUMMARY")
        print(f"   Components analyzed: {len(components)}")
        print(f"   Components with matches: {len(component_matches)}")
        
        if not dry_run:
            print(f"   Relationships created: {total_relationships}")
        else:
            print(f"   Potential relationships: {sum(len(c['compatible_arrows']) for c in component_matches.values())}")
            print(f"   (Run with dry_run=False to create relationships)")
        
        return {
            'total_components': len(components),
            'matched_components': len(component_matches),
            'component_matches': component_matches,
            'total_relationships': total_relationships
        }

def main():
    """Run component-arrow integration"""
    integrator = ComponentArrowIntegrator()
    
    print("🎯 Component-Arrow Integration Analysis")
    print("This will find compatibility relationships between Tophat components and arrows")
    print()
    
    # Run analysis in dry-run mode first
    results = integrator.create_compatibility_relationships(dry_run=True)
    
    print(f"\n💡 To create these relationships in the database, run:")
    print(f"   integrator.create_compatibility_relationships(dry_run=False)")

if __name__ == "__main__":
    main()