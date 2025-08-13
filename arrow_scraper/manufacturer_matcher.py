#!/usr/bin/env python3
"""
Smart Manufacturer Detection and Linking System

This module provides fuzzy matching capabilities to link custom equipment 
with existing manufacturers in the database, even when names don't match exactly.

Features:
- Fuzzy string matching using multiple algorithms
- Common name variations and aliases
- Manufacturer category specialization detection
- Smart linking with confidence scoring
"""

import re
from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Optional

class ManufacturerMatcher:
    """Smart manufacturer matching with fuzzy algorithms and alias detection"""
    
    def __init__(self):
        # Common manufacturer name variations and aliases
        self.manufacturer_aliases = {
            # Archery companies with common variations
            'easton': ['easton archery', 'easton arrows', 'easton technical products'],
            'gold tip': ['goldtip', 'gold-tip', 'gold tip arrows'],
            'carbon express': ['carbonexpress', 'carbon-express', 'ce arrows'],
            'victory': ['victory archery', 'victory arrows'],
            'black gold': ['blackgold', 'black-gold', 'bg archery'],
            'b-stinger': ['bstinger', 'b stinger', 'bee stinger'],
            'spot-hogg': ['spothogg', 'spot hogg'],
            'tight spot': ['tightspot', 'tight-spot'],
            'axcel': ['axcel archery', 'axcel sights'],
            'trophy taker': ['trophytaker', 'trophy-taker'],
            'quality archery designs': ['qad', 'quality archery', 'q.a.d.'],
            'new archery products': ['nap', 'new archery', 'n.a.p.'],
            'trophy ridge': ['trophyridge', 'trophy-ridge'],
            'fuse': ['fuse archery', 'fuse carbon'],
            'shrewd': ['shrewd archery'],
            'doinker': ['doinker archery'],
            'specialty archery': ['specialty', 'spec archery'],
            'copper john': ['copperjohn', 'copper-john'],
            'pine ridge': ['pineridge', 'pine-ridge'],
            'scott': ['scott archery', 'scott releases'],
            'tru ball': ['truball', 'tru-ball', 'truball archery'],
            'carter': ['carter enterprises', 'carter releases'],
            'stan': ['stan perfection', 'stan archery'],
            'mathews': ['mathews archery', 'mathews bows'],
            'hoyt': ['hoyt archery', 'hoyt usa'],
            'pse': ['pse archery', 'precision shooting equipment'],
            'bowtech': ['bow tech', 'bow-tech'],
            'elite': ['elite archery'],
            'prime': ['prime archery', 'prime bows'],
            'bear': ['bear archery'],
            'diamond': ['diamond archery', 'diamond bows'],
            'mission': ['mission archery'],
            'oneida': ['oneida eagle'],
        }
        
        # Category-specific manufacturer specializations
        self.category_specializations = {
            'strings': ['bcv', 'bcy', 'angel majesty', 'brownell', 'dynasty', '60x'],
            'sights': ['black gold', 'spot-hogg', 'axcel', 'trophy taker', 'tight spot', 'shrewd'],
            'scopes': ['leupold', 'vortex', 'zeiss', 'swarovski', 'nightforce', 'schmidt bender', 'kahles'],
            'stabilizers': ['b-stinger', 'doinker', 'fuse', 'shrewd', 'bee stinger'],
            'arrow_rests': ['qad', 'trophy taker', 'vapor trail', 'ripcord', 'hamskea'],
            'weights': ['b-stinger', 'shrewd', 'doinker', 'fuse'],
            'plungers': ['beiter', 'shibuya', 'avalon', 'cartel', 'fivics'],
            'other': []  # No specific specialists for Other category
        }
        
        # Common abbreviations and shortened forms
        self.common_abbreviations = {
            'qad': 'quality archery designs',
            'nap': 'new archery products',
            'pse': 'precision shooting equipment',
            'bg': 'black gold',
            'ce': 'carbon express',
            'gt': 'gold tip',
            'tt': 'trophy taker',
            'tr': 'trophy ridge',
            'sh': 'spot-hogg',
            'bs': 'b-stinger'
        }
    
    def normalize_name(self, name: str) -> str:
        """Normalize manufacturer name for comparison"""
        if not name:
            return ""
        
        # Convert to lowercase and remove extra spaces
        normalized = re.sub(r'\s+', ' ', name.lower().strip())
        
        # Remove common business suffixes
        business_suffixes = ['inc', 'llc', 'ltd', 'corp', 'corporation', 'company', 'co', 'archery', 'arrows', 'products']
        for suffix in business_suffixes:
            pattern = r'\b' + re.escape(suffix) + r'\b'
            normalized = re.sub(pattern, '', normalized).strip()
        
        # Remove punctuation and special characters
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity score between two names using multiple algorithms"""
        if not name1 or not name2:
            return 0.0
        
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        # Exact match after normalization
        if norm1 == norm2:
            return 1.0
        
        # Calculate multiple similarity metrics
        similarities = []
        
        # 1. Sequence matcher ratio
        similarities.append(SequenceMatcher(None, norm1, norm2).ratio())
        
        # 2. Word overlap ratio
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        if words1 or words2:
            overlap = len(words1.intersection(words2))
            total = len(words1.union(words2))
            similarities.append(overlap / total if total > 0 else 0.0)
        
        # 3. Substring matching
        longer = max(norm1, norm2, key=len)
        shorter = min(norm1, norm2, key=len)
        if len(shorter) >= 3 and shorter in longer:
            similarities.append(0.8)  # High score for substring matches
        
        # 4. Check for abbreviations
        abbrev_score = self.check_abbreviation_match(norm1, norm2)
        if abbrev_score > 0:
            similarities.append(abbrev_score)
        
        # Return the maximum similarity score
        return max(similarities) if similarities else 0.0
    
    def check_abbreviation_match(self, name1: str, name2: str) -> float:
        """Check if names match through common abbreviations"""
        # Check if one name is in abbreviations dict
        for abbrev, full_name in self.common_abbreviations.items():
            if (name1 == abbrev and self.normalize_name(full_name) == name2) or \
               (name2 == abbrev and self.normalize_name(full_name) == name1):
                return 0.9  # High confidence for known abbreviations
        
        return 0.0
    
    def check_alias_match(self, input_name: str) -> List[str]:
        """Check if input name matches any known aliases"""
        normalized_input = self.normalize_name(input_name)
        matches = []
        
        for canonical_name, aliases in self.manufacturer_aliases.items():
            # Check if input matches canonical name
            if self.normalize_name(canonical_name) == normalized_input:
                matches.append(canonical_name)
                continue
            
            # Check if input matches any alias
            for alias in aliases:
                if self.normalize_name(alias) == normalized_input:
                    matches.append(canonical_name)
                    break
        
        return matches
    
    def find_best_matches(self, input_name: str, manufacturer_list: List[Dict], 
                         category: str = None, min_confidence: float = 0.6) -> List[Dict]:
        """Find best matching manufacturers with confidence scores"""
        if not input_name or not manufacturer_list:
            return []
        
        matches = []
        
        # First check for exact alias matches
        alias_matches = self.check_alias_match(input_name)
        for alias_match in alias_matches:
            for manufacturer in manufacturer_list:
                if self.normalize_name(manufacturer['name']) == self.normalize_name(alias_match):
                    matches.append({
                        'manufacturer': manufacturer,
                        'confidence': 0.95,
                        'match_type': 'alias',
                        'reason': f'Known alias match: {input_name} → {manufacturer["name"]}'
                    })
        
        # If we found high-confidence alias matches, return them
        if matches:
            return sorted(matches, key=lambda x: x['confidence'], reverse=True)
        
        # Calculate similarity scores for all manufacturers
        for manufacturer in manufacturer_list:
            similarity = self.calculate_similarity(input_name, manufacturer['name'])
            
            if similarity >= min_confidence:
                match_info = {
                    'manufacturer': manufacturer,
                    'confidence': similarity,
                    'match_type': 'fuzzy',
                    'reason': f'Fuzzy match (similarity: {similarity:.2f})'
                }
                
                # Boost confidence if manufacturer specializes in the category
                if category and self.is_category_specialist(manufacturer['name'], category):
                    match_info['confidence'] = min(1.0, similarity + 0.1)
                    match_info['reason'] += f' + category specialist ({category})'
                
                matches.append(match_info)
        
        # Sort by confidence score, descending
        return sorted(matches, key=lambda x: x['confidence'], reverse=True)
    
    def is_category_specialist(self, manufacturer_name: str, category: str) -> bool:
        """Check if manufacturer specializes in the given equipment category"""
        if not category:
            return False
        
        category_lower = category.lower()
        manufacturer_lower = self.normalize_name(manufacturer_name)
        
        # Map frontend categories to internal categories
        category_mapping = {
            'string': 'strings',
            'sight': 'sights',
            'scope': 'scopes',
            'stabilizer': 'stabilizers',
            'arrow rest': 'arrow_rests',
            'weight': 'weights',
            'plunger': 'plungers',
            'other': 'other'
        }
        
        internal_category = category_mapping.get(category_lower, category_lower)
        
        if internal_category in self.category_specializations:
            specialists = self.category_specializations[internal_category]
            return any(self.normalize_name(specialist) == manufacturer_lower for specialist in specialists)
        
        return False
    
    def get_manufacturer_suggestions(self, input_name: str, manufacturer_list: List[Dict], 
                                   category: str = None, limit: int = 10) -> List[Dict]:
        """Get manufacturer suggestions for autocomplete with smart ranking"""
        if not input_name:
            # Return category specialists first, then others
            if category:
                specialists = []
                others = []
                
                for manufacturer in manufacturer_list:
                    if self.is_category_specialist(manufacturer['name'], category):
                        specialists.append(manufacturer)
                    else:
                        others.append(manufacturer)
                
                # Return specialists first, then others, up to limit
                result = specialists + others
                return result[:limit]
            
            return manufacturer_list[:limit]
        
        # Find matches with fuzzy matching
        matches = self.find_best_matches(input_name, manufacturer_list, category, min_confidence=0.3)
        
        # Extract manufacturers and add those that partially match the input
        suggestions = []
        input_lower = input_name.lower()
        
        # Add high-confidence matches first
        for match in matches:
            if match['confidence'] >= 0.6:
                suggestions.append(match['manufacturer'])
        
        # Add partial string matches that weren't caught by fuzzy matching
        for manufacturer in manufacturer_list:
            if manufacturer not in [s for s in suggestions]:
                if input_lower in manufacturer['name'].lower():
                    suggestions.append(manufacturer)
        
        return suggestions[:limit]
    
    def link_manufacturer(self, input_name: str, manufacturer_list: List[Dict], 
                         category: str = None) -> Optional[Dict]:
        """Attempt to link input name to existing manufacturer with high confidence"""
        matches = self.find_best_matches(input_name, manufacturer_list, category, min_confidence=0.8)
        
        if matches and matches[0]['confidence'] >= 0.8:
            return {
                'manufacturer_id': matches[0]['manufacturer']['id'],
                'manufacturer_name': matches[0]['manufacturer']['name'],
                'confidence': matches[0]['confidence'],
                'match_type': matches[0]['match_type'],
                'reason': matches[0]['reason']
            }
        
        return None

def test_manufacturer_matcher():
    """Test the manufacturer matching functionality"""
    matcher = ManufacturerMatcher()
    
    # Sample manufacturer data
    test_manufacturers = [
        {'id': 1, 'name': 'Easton Archery', 'country': 'USA'},
        {'id': 2, 'name': 'Gold Tip', 'country': 'USA'},
        {'id': 3, 'name': 'Black Gold', 'country': 'USA'},
        {'id': 4, 'name': 'B-Stinger', 'country': 'USA'},
        {'id': 5, 'name': 'Quality Archery Designs', 'country': 'USA'},
    ]
    
    # Test cases
    test_cases = [
        ('easton', 'Sight'),
        ('goldtip', 'Arrow Rest'),
        ('QAD', 'Arrow Rest'),
        ('black-gold', 'Sight'),
        ('bee stinger', 'Stabilizer'),
    ]
    
    print("🔍 Testing Manufacturer Matcher")
    print("=" * 50)
    
    for input_name, category in test_cases:
        print(f"\nInput: '{input_name}' (Category: {category})")
        
        # Test linking
        link_result = matcher.link_manufacturer(input_name, test_manufacturers, category)
        if link_result:
            print(f"✅ Linked to: {link_result['manufacturer_name']} (confidence: {link_result['confidence']:.2f})")
            print(f"   Reason: {link_result['reason']}")
        else:
            print("❌ No high-confidence match found")
        
        # Test suggestions
        suggestions = matcher.get_manufacturer_suggestions(input_name, test_manufacturers, category, limit=3)
        print(f"💡 Top suggestions: {[s['name'] for s in suggestions[:3]]}")

if __name__ == "__main__":
    test_manufacturer_matcher()