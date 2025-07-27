#!/usr/bin/env python3
"""
Component-Arrow Compatibility Matching Engine
Determines compatibility between arrows and components using rule-based matching
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import re
import threading

@dataclass
class CompatibilityRule:
    """Represents a compatibility rule"""
    category: str
    rule_name: str
    conditions: Dict[str, Any]
    compatibility_type: str
    score: float
    description: str

@dataclass
class CompatibilityResult:
    """Result of compatibility check"""
    component_id: int
    arrow_id: int
    compatibility_type: str
    score: float
    matching_rules: List[str]
    notes: str

class CompatibilityEngine:
    """Engine for determining arrow-component compatibility"""
    
    def __init__(self, db_path: str = "arrow_database.db"):
        self.db_path = Path(db_path)
        self.local = threading.local()
        self.rules = {}
        self.load_compatibility_rules()
    
    def get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, 'conn') or self.local.conn is None:
            self.local.conn = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,
                timeout=30.0
            )
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn
    
    def load_compatibility_rules(self):
        """Load compatibility rules from database and define built-in rules"""
        
        # Define built-in compatibility rules
        self.built_in_rules = {
            'points': [
                CompatibilityRule(
                    category='points',
                    rule_name='thread_compatibility',
                    conditions={'thread_match': True},
                    compatibility_type='direct',
                    score=0.95,
                    description='Point thread matches arrow insert thread'
                ),
                CompatibilityRule(
                    category='points',
                    rule_name='weight_range',
                    conditions={'weight_in_range': True},
                    compatibility_type='direct',
                    score=0.90,
                    description='Point weight within recommended range for arrow'
                ),
                CompatibilityRule(
                    category='points',
                    rule_name='universal_thread',
                    conditions={'universal_thread': True},
                    compatibility_type='universal',
                    score=0.85,
                    description='Universal thread type (8-32 standard)'
                )
            ],
            'nocks': [
                CompatibilityRule(
                    category='nocks',
                    rule_name='diameter_match',
                    conditions={'diameter_match': True},
                    compatibility_type='direct',
                    score=0.95,
                    description='Nock size matches arrow shaft diameter'
                ),
                CompatibilityRule(
                    category='nocks',
                    rule_name='fit_type_compatible',
                    conditions={'fit_compatible': True},
                    compatibility_type='direct',
                    score=0.90,
                    description='Nock fit type compatible with arrow shaft'
                ),
                CompatibilityRule(
                    category='nocks',
                    rule_name='universal_fit',
                    conditions={'universal_fit': True},
                    compatibility_type='universal',
                    score=0.80,
                    description='Universal push-in nock'
                )
            ],
            'inserts': [
                CompatibilityRule(
                    category='inserts',
                    rule_name='outer_diameter_match',
                    conditions={'outer_diameter_match': True},
                    compatibility_type='direct',
                    score=0.95,
                    description='Insert outer diameter matches arrow inner diameter'
                ),
                CompatibilityRule(
                    category='inserts',
                    rule_name='thread_compatibility',
                    conditions={'thread_compatible': True},
                    compatibility_type='direct',
                    score=0.90,
                    description='Insert thread compatible with points'
                ),
                CompatibilityRule(
                    category='inserts',
                    rule_name='manufacturer_match',
                    conditions={'manufacturer_match': True},
                    compatibility_type='direct',
                    score=0.85,
                    description='Same manufacturer as arrow'
                )
            ],
            'fletchings': [
                CompatibilityRule(
                    category='fletchings',
                    rule_name='universal_adhesive',
                    conditions={'adhesive_type': 'adhesive'},
                    compatibility_type='universal',
                    score=0.90,
                    description='Adhesive vanes work with all carbon/aluminum arrows'
                ),
                CompatibilityRule(
                    category='fletchings',
                    rule_name='material_compatible',
                    conditions={'material_compatible': True},
                    compatibility_type='direct',
                    score=0.85,
                    description='Fletching material compatible with arrow material'
                ),
                CompatibilityRule(
                    category='fletchings',
                    rule_name='diameter_appropriate',
                    conditions={'diameter_appropriate': True},
                    compatibility_type='direct',
                    score=0.80,
                    description='Fletching size appropriate for arrow diameter'
                )
            ]
        }
        
        # Load custom rules from database if available
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT category_name, rule_name, rule_logic, priority, description
                FROM compatibility_rules 
                WHERE active = TRUE
                ORDER BY priority DESC
            """)
            
            for row in cursor.fetchall():
                category = row['category_name']
                if category not in self.rules:
                    self.rules[category] = []
                
                try:
                    rule_logic = json.loads(row['rule_logic'])
                    rule = CompatibilityRule(
                        category=category,
                        rule_name=row['rule_name'],
                        conditions=rule_logic.get('conditions', {}),
                        compatibility_type=rule_logic.get('compatibility_type', 'direct'),
                        score=rule_logic.get('score', 0.5),
                        description=row['description']
                    )
                    self.rules[category].append(rule)
                except json.JSONDecodeError:
                    print(f"⚠️  Invalid rule logic for {row['rule_name']}")
                    
        except Exception as e:
            print(f"⚠️  Could not load custom rules: {e}")
        
        # Combine built-in and custom rules
        for category, rules in self.built_in_rules.items():
            if category not in self.rules:
                self.rules[category] = []
            self.rules[category].extend(rules)
    
    def check_compatibility(self, arrow_id: int, component_id: int) -> CompatibilityResult:
        """Check compatibility between arrow and component"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get arrow data
            cursor.execute("""
                SELECT a.*, s.spine, s.outer_diameter, s.gpi_weight, s.inner_diameter
                FROM arrows a
                JOIN spine_specifications s ON a.id = s.arrow_id
                WHERE a.id = ?
                LIMIT 1
            """, (arrow_id,))
            arrow_row = cursor.fetchone()
            
            if not arrow_row:
                return CompatibilityResult(
                    component_id=component_id,
                    arrow_id=arrow_id,
                    compatibility_type='incompatible',
                    score=0.0,
                    matching_rules=[],
                    notes="Arrow not found"
                )
            
            # Get component data
            cursor.execute("""
                SELECT c.*, cc.name as category_name
                FROM components c
                JOIN component_categories cc ON c.category_id = cc.id
                WHERE c.id = ?
            """, (component_id,))
            component_row = cursor.fetchone()
            
            if not component_row:
                return CompatibilityResult(
                    component_id=component_id,
                    arrow_id=arrow_id,
                    compatibility_type='incompatible',
                    score=0.0,
                    matching_rules=[],
                    notes="Component not found"
                )
            
            # Parse data
            arrow_data = dict(arrow_row)
            component_data = dict(component_row)
            component_specs = json.loads(component_data.get('specifications', '{}'))
            category = component_data['category_name']
            
            # Apply compatibility rules
            return self._apply_rules(arrow_data, component_data, component_specs, category)
            
        except Exception as e:
            print(f"❌ Error checking compatibility: {e}")
            return CompatibilityResult(
                component_id=component_id,
                arrow_id=arrow_id,
                compatibility_type='incompatible',
                score=0.0,
                matching_rules=[],
                notes=f"Error: {e}"
            )
    
    def _apply_rules(self, arrow_data: Dict, component_data: Dict, 
                     component_specs: Dict, category: str) -> CompatibilityResult:
        """Apply compatibility rules to determine compatibility"""
        
        matching_rules = []
        max_score = 0.0
        best_compatibility = 'incompatible'
        notes = []
        
        category_rules = self.rules.get(category, [])
        
        for rule in category_rules:
            rule_matches, rule_score, rule_note = self._evaluate_rule(
                rule, arrow_data, component_data, component_specs
            )
            
            if rule_matches:
                matching_rules.append(rule.rule_name)
                if rule_score > max_score:
                    max_score = rule_score
                    best_compatibility = rule.compatibility_type
                if rule_note:
                    notes.append(rule_note)
        
        # Default compatibility for universal components
        if not matching_rules and category in ['fletchings']:
            # Fletchings are generally universal with adhesive
            if component_specs.get('attachment') == 'adhesive':
                matching_rules.append('universal_adhesive')
                max_score = 0.80
                best_compatibility = 'universal'
                notes.append('Adhesive fletching works with most arrows')
        
        # Combine notes
        combined_notes = '; '.join(notes) if notes else 'No specific compatibility rules matched'
        
        return CompatibilityResult(
            component_id=component_data['id'],
            arrow_id=arrow_data['id'],
            compatibility_type=best_compatibility,
            score=max_score,
            matching_rules=matching_rules,
            notes=combined_notes
        )
    
    def _evaluate_rule(self, rule: CompatibilityRule, arrow_data: Dict, 
                       component_data: Dict, component_specs: Dict) -> Tuple[bool, float, str]:
        """Evaluate a single compatibility rule"""
        
        try:
            if rule.category == 'points':
                return self._evaluate_point_rule(rule, arrow_data, component_specs)
            elif rule.category == 'nocks':
                return self._evaluate_nock_rule(rule, arrow_data, component_specs)
            elif rule.category == 'inserts':
                return self._evaluate_insert_rule(rule, arrow_data, component_data, component_specs)
            elif rule.category == 'fletchings':
                return self._evaluate_fletching_rule(rule, arrow_data, component_specs)
            else:
                return False, 0.0, ""
                
        except Exception as e:
            print(f"⚠️  Error evaluating rule {rule.rule_name}: {e}")
            return False, 0.0, ""
    
    def _evaluate_point_rule(self, rule: CompatibilityRule, arrow_data: Dict, 
                            component_specs: Dict) -> Tuple[bool, float, str]:
        """Evaluate point compatibility rules"""
        
        if rule.rule_name == 'thread_compatibility':
            # Check if point thread matches insert thread (assume 8-32 standard)
            point_thread = component_specs.get('thread_type', '8-32')
            if point_thread in ['8-32', '5/16-24']:  # Common threads
                return True, rule.score, f"Thread {point_thread} compatible"
            return False, 0.0, ""
        
        elif rule.rule_name == 'weight_range':
            # Check if point weight is reasonable for arrow
            weight_str = component_specs.get('weight', '')
            if weight_str:
                try:
                    weight = float(re.findall(r'(\d+(?:\.\d+)?)', weight_str)[0])
                    gpi = arrow_data.get('gpi_weight', 0)
                    
                    # Reasonable point weight is typically 8-15% of total arrow weight
                    if gpi > 0:
                        total_weight = gpi * 28 + weight  # 28" arrow estimate
                        weight_percentage = weight / total_weight
                        if 0.08 <= weight_percentage <= 0.20:  # 8-20% range
                            return True, rule.score, f"{weight}gr appropriate for arrow"
                    
                    # Fallback: common weight ranges
                    if 75 <= weight <= 200:  # Common hunting/target range
                        return True, rule.score * 0.8, f"{weight}gr in common range"
                        
                except (ValueError, IndexError):
                    pass
            return False, 0.0, ""
        
        elif rule.rule_name == 'universal_thread':
            point_thread = component_specs.get('thread_type', '8-32')
            if point_thread == '8-32':  # Most universal
                return True, rule.score, "Standard 8-32 thread"
            return False, 0.0, ""
        
        return False, 0.0, ""
    
    def _evaluate_nock_rule(self, rule: CompatibilityRule, arrow_data: Dict, 
                           component_specs: Dict) -> Tuple[bool, float, str]:
        """Evaluate nock compatibility rules"""
        
        if rule.rule_name == 'diameter_match':
            nock_size = component_specs.get('nock_size', '')
            arrow_diameter = arrow_data.get('outer_diameter', 0)
            
            if nock_size and arrow_diameter:
                try:
                    nock_dia = float(nock_size.replace('"', ''))
                    # Allow small tolerance
                    if abs(nock_dia - arrow_diameter) <= 0.005:
                        return True, rule.score, f"Nock {nock_size} matches shaft diameter"
                except ValueError:
                    pass
            return False, 0.0, ""
        
        elif rule.rule_name == 'fit_type_compatible':
            fit_type = component_specs.get('fit_type', 'push_in')
            # Most carbon arrows use push-in nocks
            if fit_type in ['push_in', 'push-in']:
                return True, rule.score, "Push-in fit compatible"
            return False, 0.0, ""
        
        elif rule.rule_name == 'universal_fit':
            fit_type = component_specs.get('fit_type', 'push_in')
            if fit_type in ['push_in', 'push-in']:
                return True, rule.score, "Universal push-in nock"
            return False, 0.0, ""
        
        return False, 0.0, ""
    
    def _evaluate_insert_rule(self, rule: CompatibilityRule, arrow_data: Dict, 
                             component_data: Dict, component_specs: Dict) -> Tuple[bool, float, str]:
        """Evaluate insert compatibility rules"""
        
        if rule.rule_name == 'outer_diameter_match':
            insert_od = component_specs.get('outer_diameter', 0)
            arrow_id = arrow_data.get('inner_diameter')
            
            if insert_od and arrow_id:
                # Allow small tolerance for press fit
                if abs(insert_od - arrow_id) <= 0.002:
                    return True, rule.score, f"Insert OD {insert_od} matches arrow ID"
            return False, 0.0, ""
        
        elif rule.rule_name == 'thread_compatibility':
            insert_thread = component_specs.get('thread', '8-32')
            if insert_thread in ['8-32', '5/16-24']:
                return True, rule.score, f"Thread {insert_thread} compatible"
            return False, 0.0, ""
        
        elif rule.rule_name == 'manufacturer_match':
            arrow_manufacturer = arrow_data.get('manufacturer', '').lower()
            component_manufacturer = component_data.get('manufacturer', '').lower()
            
            if arrow_manufacturer and component_manufacturer:
                if arrow_manufacturer == component_manufacturer:
                    return True, rule.score, "Same manufacturer"
            return False, 0.0, ""
        
        return False, 0.0, ""
    
    def _evaluate_fletching_rule(self, rule: CompatibilityRule, arrow_data: Dict, 
                                component_specs: Dict) -> Tuple[bool, float, str]:
        """Evaluate fletching compatibility rules"""
        
        if rule.rule_name == 'universal_adhesive':
            attachment = component_specs.get('attachment', 'adhesive')
            if attachment == 'adhesive':
                return True, rule.score, "Adhesive vanes work with all shafts"
            return False, 0.0, ""
        
        elif rule.rule_name == 'material_compatible':
            fletching_material = component_specs.get('material', 'plastic')
            arrow_material = arrow_data.get('material', 'carbon')
            
            # Plastic vanes work with carbon/aluminum, feathers work with all
            if fletching_material == 'feather':
                return True, rule.score, "Feathers work with all arrow types"
            elif fletching_material == 'plastic' and arrow_material in ['carbon', 'aluminum']:
                return True, rule.score, "Plastic vanes work with carbon/aluminum"
            return False, 0.0, ""
        
        elif rule.rule_name == 'diameter_appropriate':
            fletching_length = component_specs.get('length', 0)
            arrow_diameter = arrow_data.get('outer_diameter', 0.3)
            
            if fletching_length:
                # General rule: larger arrows can handle longer fletching
                if arrow_diameter >= 0.3 and fletching_length <= 4:  # Large arrows
                    return True, rule.score, f"{fletching_length}\" appropriate for shaft"
                elif arrow_diameter < 0.3 and fletching_length <= 3:  # Small arrows
                    return True, rule.score, f"{fletching_length}\" appropriate for shaft"
            return False, 0.0, ""
        
        return False, 0.0, ""
    
    def batch_compatibility_check(self, arrow_ids: List[int], 
                                 component_ids: List[int]) -> List[CompatibilityResult]:
        """Check compatibility for multiple arrow-component pairs"""
        results = []
        
        for arrow_id in arrow_ids:
            for component_id in component_ids:
                result = self.check_compatibility(arrow_id, component_id)
                if result.compatibility_type != 'incompatible':
                    results.append(result)
        
        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def get_compatible_components(self, arrow_id: int, 
                                 category: str = None) -> List[Dict[str, Any]]:
        """Get all compatible components for an arrow"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get all components (or filtered by category)
            query = """
                SELECT c.*, cc.name as category_name
                FROM components c
                JOIN component_categories cc ON c.category_id = cc.id
            """
            params = []
            
            if category:
                query += " WHERE cc.name = ?"
                params.append(category)
            
            cursor.execute(query, params)
            components = cursor.fetchall()
            
            compatible_components = []
            
            for component in components:
                result = self.check_compatibility(arrow_id, component['id'])
                if result.compatibility_type != 'incompatible':
                    component_dict = dict(component)
                    component_dict['compatibility'] = {
                        'type': result.compatibility_type,
                        'score': result.score,
                        'matching_rules': result.matching_rules,
                        'notes': result.notes
                    }
                    compatible_components.append(component_dict)
            
            # Sort by compatibility score
            compatible_components.sort(
                key=lambda x: x['compatibility']['score'], 
                reverse=True
            )
            
            return compatible_components
            
        except Exception as e:
            print(f"❌ Error getting compatible components: {e}")
            return []

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Compatibility Engine")
    print("=" * 50)
    
    # Initialize engine
    engine = CompatibilityEngine()
    
    # Test compatibility check (assuming arrow ID 1 and component ID 1 exist)
    print("\n🔍 Testing arrow-component compatibility...")
    
    try:
        result = engine.check_compatibility(1, 1)
        print(f"Arrow 1 + Component 1:")
        print(f"  Compatibility: {result.compatibility_type}")
        print(f"  Score: {result.score:.2f}")
        print(f"  Matching rules: {result.matching_rules}")
        print(f"  Notes: {result.notes}")
        
        # Test getting compatible components
        print(f"\n🎯 Getting compatible points for arrow 1...")
        compatible = engine.get_compatible_components(1, 'points')
        print(f"Found {len(compatible)} compatible points")
        
        for component in compatible[:3]:  # Show top 3
            comp_info = component['compatibility']
            print(f"  • {component['manufacturer']} {component['model_name']}")
            print(f"    Score: {comp_info['score']:.2f} ({comp_info['type']})")
            print(f"    Rules: {', '.join(comp_info['matching_rules'])}")
        
    except Exception as e:
        print(f"⚠️  Test requires existing arrow and component data: {e}")
    
    print(f"\n✅ Compatibility engine test completed!")
    print(f"Available rule categories: {list(engine.rules.keys())}")