#!/usr/bin/env python3
"""
Arrow Matching Engine
Combines spine calculations with database search to find optimal arrow recommendations
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

# Import our custom modules
from arrow_database import ArrowDatabase
from spine_calculator import SpineCalculator, BowConfiguration, BowType
from spine_service import spine_service

class MatchCriteria(Enum):
    """Criteria for ranking arrow matches"""
    SPINE_ACCURACY = "spine_accuracy"
    AVAILABILITY = "availability" 
    MANUFACTURER = "manufacturer"
    PRICE_RANGE = "price_range"
    DIAMETER = "diameter"
    FOC_TARGET = "foc_target"

@dataclass
class ArrowMatch:
    """Single arrow match result"""
    arrow_id: int
    manufacturer: str
    model_name: str
    matched_spine: int
    spine_deviation: float  # How far from optimal spine
    gpi_weight: float
    outer_diameter: float
    inner_diameter: float  # Inner diameter for sorting
    match_score: float  # Overall match quality (0-100)
    spine_specifications: List[Dict[str, Any]]  # All available spines for this arrow
    confidence_level: str  # high, medium, low
    match_reasons: List[str]  # Why this arrow was matched
    potential_issues: List[str]  # Potential concerns
    material: str = None  # Arrow material (wood, carbon, aluminum, etc.)
    arrow_type: str = None  # Arrow type (hunting, target, etc.)
    description: str = None  # Arrow description
    price_range: str = None  # Price range

@dataclass 
class MatchRequest:
    """Arrow matching request parameters"""
    bow_config: BowConfiguration
    arrow_length: float
    point_weight: float = 100.0
    nock_weight: float = 10.0
    fletching_weight: float = 15.0
    insert_weight: float = 15.0
    
    # Preferences
    preferred_manufacturers: List[str] = None
    target_diameter_range: Tuple[float, float] = None  # (min, max) in inches
    target_weight_range: Tuple[float, float] = None   # (min, max) GPI
    target_foc_range: Tuple[float, float] = None      # (min, max) FOC percentage
    arrow_type_preference: str = None                  # hunting, target, etc.
    material_preference: str = None                    # wood, carbon, aluminum, etc.
    wood_species_preference: str = None                # For wood arrows: cedar, pine, ash, etc.
    
    # Constraints
    max_results: int = 50  # Allow more results for progressive loading
    min_spine_options: int = 3  # Minimum spine options available
    
class ArrowMatchingEngine:
    """Main engine for finding optimal arrow matches"""
    
    def __init__(self, database_path: str = "arrow_database.db"):
        self.db = ArrowDatabase(database_path)
        self.spine_calculator = SpineCalculator()
        
        # Scoring weights for different criteria
        self.scoring_weights = {
            MatchCriteria.SPINE_ACCURACY: 0.4,      # Most important
            MatchCriteria.AVAILABILITY: 0.2,        # Having multiple spine options
            MatchCriteria.MANUFACTURER: 0.1,        # Brand preference
            MatchCriteria.DIAMETER: 0.15,           # Diameter preference
            MatchCriteria.FOC_TARGET: 0.15          # FOC optimization
        }
    
    def find_matching_arrows(self, request: MatchRequest) -> List[ArrowMatch]:
        """
        Find arrows that match the specified bow configuration and preferences
        
        Returns:
            List of ArrowMatch objects sorted by match quality
        """
        
        print(f"🎯 Finding arrows for {request.bow_config.bow_type.value} bow")
        print(f"   Draw: {request.bow_config.draw_weight}# @ {request.bow_config.draw_length}\"")
        print(f"   Arrow length: {request.arrow_length}\"")
        print(f"   Point weight: {request.point_weight}gr")
        print(f"   Material preference: {request.material_preference}")
        
        # Calculate required spine using unified service
        spine_result = spine_service.calculate_spine(
            draw_weight=request.bow_config.draw_weight,
            arrow_length=request.arrow_length,
            point_weight=request.point_weight,
            bow_type=request.bow_config.bow_type.value,
            nock_weight=request.nock_weight,
            fletching_weight=request.fletching_weight,
            material_preference=request.material_preference
        )
        
        optimal_spine = spine_result['calculated_spine']
        spine_range = spine_result['spine_range']
        
        print(f"   Calculated spine: {optimal_spine} (range: {spine_range['minimum']}-{spine_range['maximum']})")
        
        # Check if spine is in pounds (wood arrows) or carbon spine numbers
        spine_units = spine_result.get('spine_units', 'carbon')
        if spine_units == 'pounds':
            print(f"   Using wood arrow spine values (in pounds)")
        else:
            print(f"   Using carbon arrow spine values")
        
        # Handle material-specific manufacturer preferences
        manufacturer_filter = self._format_manufacturer_filter(request.preferred_manufacturers, request.material_preference)
        
        # Search database for arrows within spine range
        # Different expansion logic for wood vs carbon arrows
        if spine_units == 'pounds':
            spine_expansion = 5  # Smaller expansion for wood arrows (pound-based rating)
        else:
            spine_expansion = 50  # Larger expansion for carbon arrows (number-based rating)
            
        search_params = {
            'spine_min': int(spine_range['minimum'] - spine_expansion),
            'spine_max': int(spine_range['maximum'] + spine_expansion),
            'arrow_type': None if request.material_preference and request.material_preference.lower() == 'wood' else request.arrow_type_preference,  # Skip arrow_type filter for wood arrows
            'diameter_min': request.target_diameter_range[0] if request.target_diameter_range else None,
            'diameter_max': request.target_diameter_range[1] if request.target_diameter_range else None,
            'gpi_min': request.target_weight_range[0] if request.target_weight_range else None,
            'gpi_max': request.target_weight_range[1] if request.target_weight_range else None,
            'limit': request.max_results * 10  # Get many more candidates for better diversity
        }
        
        # Only add manufacturer filter if it's not None
        if manufacturer_filter is not None:
            search_params['manufacturer'] = manufacturer_filter
        
        # Add material preference filter if specified
        if request.material_preference:
            # Map frontend material values to database format
            search_params['material'] = self._map_material_preference(request.material_preference)
        
        print(f"   Search parameters: spine {search_params['spine_min']}-{search_params['spine_max']}, manufacturer='{manufacturer_filter}', material='{search_params.get('material', 'None')}'")
        
        search_results = self.db.search_arrows(**search_params)
        
        # If wood material is requested and we didn't find enough arrows, search specifically for wood manufacturers
        if request.material_preference and request.material_preference.lower() == 'wood' and len(search_results) < request.max_results:
            # Define wood species to manufacturer mapping (updated for Migration 047 manufacturers)
            wood_species_manufacturers = {
                'Port Orford Cedar': ['Port Orford Cedar Shafts'],
                'Sitka Spruce': ['Sitka Spruce Shafts'],
                'Douglas Fir': ['Douglas Fir Shafts'],
                'Pine': ['Pine Shafts'],
                'Ash': ['Ash Shafts'],
                'Bamboo': ['Bamboo Shafts', 'Traditional Wood Arrows'],  # Both new and old bamboo entries
                '': ['Traditional Wood Arrows', 'Port Orford Cedar Shafts', 'Sitka Spruce Shafts', 'Douglas Fir Shafts', 'Pine Shafts', 'Ash Shafts', 'Bamboo Shafts']  # All when no species specified
            }
            
            # Get manufacturers to search based on wood species preference
            if request.wood_species_preference and request.wood_species_preference in wood_species_manufacturers:
                target_manufacturers = wood_species_manufacturers[request.wood_species_preference]
            else:
                target_manufacturers = wood_species_manufacturers['']  # All wood manufacturers
            
            additional_results = []
            
            for wood_mfr in target_manufacturers:
                wood_arrows = self.db.search_arrows(
                    spine_min=int(spine_range['minimum'] - spine_expansion),
                    spine_max=int(spine_range['maximum'] + spine_expansion),
                    manufacturer=wood_mfr,
                    material='Wood',  # Explicitly filter for wood material
                    limit=request.max_results
                )
                additional_results.extend(wood_arrows)
            
            # Combine results, avoiding duplicates
            existing_ids = {arrow['id'] for arrow in search_results}
            for arrow in additional_results:
                if arrow['id'] not in existing_ids:
                    search_results.append(arrow)
                    existing_ids.add(arrow['id'])
        
        print(f"   Database search returned {len(search_results)} candidates")
        
        if not search_results:
            print("❌ No arrows found in database matching criteria")
            return []
        
        # Convert to detailed matches
        arrow_matches = []
        print(f"   Processing {len(search_results)} candidates...")
        
        # Group candidates by manufacturer for debugging
        candidate_mfrs = {}
        for arrow_data in search_results:
            mfr = arrow_data.get('manufacturer', 'Unknown')
            if mfr not in candidate_mfrs:
                candidate_mfrs[mfr] = 0
            candidate_mfrs[mfr] += 1
        print(f"   Candidates by manufacturer: {dict(sorted(candidate_mfrs.items()))}")
        
        # First pass: strict spine options requirement
        for arrow_data in search_results:
            arrow_details = self.db.get_arrow_details(arrow_data['id'])
            # Relax spine options requirement for wood arrows (they typically have fewer options)
            min_spine_req = 2 if request.material_preference and request.material_preference.lower() == 'wood' else request.min_spine_options
            
            if arrow_details and len(arrow_details['spine_specifications']) >= min_spine_req:
                match = self._create_arrow_match(arrow_details, optimal_spine, spine_range, request)
                if match:
                    arrow_matches.append(match)
        
        # Fallback: If no arrows found with strict requirements, relax spine options requirement
        if not arrow_matches:
            print(f"   No arrows found with {request.min_spine_options}+ spine options, trying with relaxed requirements...")
            for arrow_data in search_results:
                arrow_details = self.db.get_arrow_details(arrow_data['id'])
                # Accept any arrow with at least 1 spine specification
                if arrow_details and len(arrow_details['spine_specifications']) >= 1:
                    match = self._create_arrow_match(arrow_details, optimal_spine, spine_range, request)
                    if match:
                        arrow_matches.append(match)
        
        # Second fallback: Expand spine range if still no matches found
        if not arrow_matches:
            print(f"   Still no arrows found, expanding spine search range...")
            expanded_spine_search = spine_expansion * 2  # Double the expansion
            expanded_search_params = search_params.copy()
            expanded_search_params['spine_min'] = int(spine_range['minimum'] - expanded_spine_search)
            expanded_search_params['spine_max'] = int(spine_range['maximum'] + expanded_spine_search)
            
            print(f"   Expanded search parameters: spine {expanded_search_params['spine_min']}-{expanded_search_params['spine_max']}")
            
            expanded_results = self.db.search_arrows(**expanded_search_params)
            print(f"   Expanded search returned {len(expanded_results)} candidates")
            
            for arrow_data in expanded_results:
                arrow_details = self.db.get_arrow_details(arrow_data['id'])
                if arrow_details and len(arrow_details['spine_specifications']) >= 1:
                    match = self._create_arrow_match(arrow_details, optimal_spine, spine_range, request)
                    if match:
                        arrow_matches.append(match)
                    
        # Debug: Show what manufacturers made it through
        match_mfrs = {}
        for match in arrow_matches:
            if match.manufacturer not in match_mfrs:
                match_mfrs[match.manufacturer] = 0
            match_mfrs[match.manufacturer] += 1
        print(f"   Matches by manufacturer: {dict(sorted(match_mfrs.items()))}")
        
        # Sort by match score
        arrow_matches.sort(key=lambda x: x.match_score, reverse=True)
        
        # Show more arrows per manufacturer while maintaining some diversity
        # Allow up to 3 arrows per manufacturer, then ensure some diversity
        manufacturer_counts = {}
        diverse_matches = []
        remaining_matches = []
        
        for match in arrow_matches:
            mfr = match.manufacturer
            if mfr not in manufacturer_counts:
                manufacturer_counts[mfr] = 0
            
            # Allow up to 3 arrows per manufacturer if they have good scores >= 85
            if manufacturer_counts[mfr] < 3 and match.match_score >= 85:
                diverse_matches.append(match) 
                manufacturer_counts[mfr] += 1
            else:
                remaining_matches.append(match)
        
        # Second pass: fill remaining slots with best remaining matches (any manufacturer)
        while len(diverse_matches) < request.max_results and remaining_matches:
            diverse_matches.append(remaining_matches.pop(0))
        
        final_matches = diverse_matches[:request.max_results]
        
        print(f"✅ Found {len(final_matches)} high-quality arrow matches")
        
        return final_matches
    
    def _create_arrow_match(self, arrow_details: Dict[str, Any], optimal_spine: float, 
                          spine_range: Dict[str, float], request: MatchRequest) -> Optional[ArrowMatch]:
        """Create an ArrowMatch from database arrow details"""
        
        # Find best spine match
        spine_specs = arrow_details['spine_specifications']
        best_spine_match = None
        min_deviation = float('inf')
        
        # Special handling for wood arrows - check if optimal spine falls within range
        is_wood_arrow = (request.material_preference and request.material_preference.lower() == 'wood') or arrow_details.get('material', '').lower() == 'wood'
        
        if is_wood_arrow and len(spine_specs) >= 2:
            # For wood arrows, find if optimal spine falls within the range
            spine_values = []
            for spec in spine_specs:
                spine_val = spec['spine']
                # Convert spine value to float/int if it's a string
                if isinstance(spine_val, str):
                    try:
                        spine_val = float(spine_val)
                    except ValueError:
                        continue  # Skip invalid spine values
                spine_values.append(spine_val)
            
            if not spine_values:
                return None
                
            min_spine = min(spine_values)
            max_spine = max(spine_values)
            
            # If optimal spine falls within the wood arrow's range, it's a perfect match
            if min_spine <= optimal_spine <= max_spine:
                # Choose the spine specification closest to the optimal
                def safe_spine_diff(spec):
                    spine_val = spec['spine']
                    if isinstance(spine_val, str):
                        try:
                            spine_val = float(spine_val)
                        except ValueError:
                            return float('inf')  # Invalid values get lowest priority
                    return abs(spine_val - optimal_spine)
                
                best_spine_match = min(spine_specs, key=safe_spine_diff)
                min_deviation = 0  # Perfect match for wood arrows within range
            else:
                # Use normal matching logic for wood arrows outside range
                for spec in spine_specs:
                    spine_value = spec['spine']
                    # Convert spine value to float/int if it's a string
                    if isinstance(spine_value, str):
                        try:
                            spine_value = float(spine_value)
                        except ValueError:
                            continue  # Skip invalid spine values
                    
                    deviation = abs(spine_value - optimal_spine)
                    if deviation < min_deviation:
                        min_deviation = deviation
                        best_spine_match = spec
        else:
            # Normal matching logic for non-wood arrows
            for spec in spine_specs:
                spine_value = spec['spine']
                # Convert spine value to float/int if it's a string
                if isinstance(spine_value, str):
                    try:
                        spine_value = float(spine_value)
                    except ValueError:
                        continue  # Skip invalid spine values
                
                deviation = abs(spine_value - optimal_spine)
                if deviation < min_deviation:
                    min_deviation = deviation
                    best_spine_match = spec
        
        if not best_spine_match:
            return None
        
        # Calculate match score
        match_score = self._calculate_match_score(
            arrow_details, best_spine_match, optimal_spine, spine_range, request
        )
        
        # Determine confidence level
        confidence = self._determine_confidence_level(min_deviation, spine_range)
        
        # Generate match reasons
        match_reasons = self._generate_match_reasons(
            arrow_details, best_spine_match, optimal_spine, request
        )
        
        # Check for potential issues
        potential_issues = self._check_potential_issues(
            arrow_details, best_spine_match, spine_range, request
        )
        
        return ArrowMatch(
            arrow_id=arrow_details['id'],
            manufacturer=arrow_details['manufacturer'],
            model_name=arrow_details['model_name'],
            matched_spine=best_spine_match['spine'],
            spine_deviation=min_deviation,
            gpi_weight=best_spine_match['gpi_weight'],
            outer_diameter=best_spine_match.get('outer_diameter', 0.0),
            inner_diameter=best_spine_match.get('inner_diameter', 0.0),
            match_score=match_score,
            spine_specifications=spine_specs,
            confidence_level=confidence,
            match_reasons=match_reasons,
            potential_issues=potential_issues,
            material=arrow_details.get('material'),
            arrow_type=arrow_details.get('arrow_type'),
            description=arrow_details.get('description'),
            price_range=arrow_details.get('price_range')
        )
    
    def _calculate_match_score(self, arrow_details: Dict[str, Any], best_spine_match: Dict[str, Any],
                             optimal_spine: float, spine_range: Dict[str, float], 
                             request: MatchRequest) -> float:
        """Calculate overall match score (0-100)"""
        
        total_score = 0.0
        
        # Spine accuracy score (0-100)
        spine_deviation = abs(best_spine_match['spine'] - optimal_spine)
        max_acceptable_deviation = (spine_range['maximum'] - spine_range['minimum']) / 2
        spine_accuracy = max(0, 100 - (spine_deviation / max_acceptable_deviation) * 100)
        total_score += spine_accuracy * self.scoring_weights[MatchCriteria.SPINE_ACCURACY]
        
        # Availability score (based on number of spine options)
        spine_count = len(arrow_details['spine_specifications'])
        availability_score = min(100, (spine_count / 8) * 100)  # 8 spines = perfect score
        total_score += availability_score * self.scoring_weights[MatchCriteria.AVAILABILITY]
        
        # Manufacturer preference score
        manufacturer_score = 100.0
        if request.preferred_manufacturers:
            manufacturer_lower = arrow_details['manufacturer'].lower()
            if not any(pref.lower() in manufacturer_lower for pref in request.preferred_manufacturers):
                manufacturer_score = 50.0  # Penalty for non-preferred manufacturer
        total_score += manufacturer_score * self.scoring_weights[MatchCriteria.MANUFACTURER]
        
        # Diameter score
        diameter_score = 100.0
        if request.target_diameter_range and best_spine_match.get('outer_diameter'):
            target_min, target_max = request.target_diameter_range
            actual_diameter = best_spine_match['outer_diameter']
            if target_min <= actual_diameter <= target_max:
                diameter_score = 100.0
            else:
                # Calculate penalty based on how far outside range
                if actual_diameter < target_min:
                    deviation = target_min - actual_diameter
                else:
                    deviation = actual_diameter - target_max
                diameter_score = max(0, 100 - (deviation / 0.05) * 100)  # 0.05" = 50% penalty
        total_score += diameter_score * self.scoring_weights[MatchCriteria.DIAMETER]
        
        # FOC target score (if specified)
        foc_score = 100.0
        if request.target_foc_range:
            # Calculate estimated FOC
            estimated_shaft_weight = best_spine_match['gpi_weight'] * request.arrow_length
            foc_calc = self.spine_calculator.calculate_foc(
                request.arrow_length,
                request.point_weight,
                estimated_shaft_weight,
                request.nock_weight,
                request.fletching_weight,
                request.insert_weight
            )
            
            actual_foc = foc_calc['foc_percentage']
            target_min, target_max = request.target_foc_range
            
            if target_min <= actual_foc <= target_max:
                foc_score = 100.0
            else:
                if actual_foc < target_min:
                    deviation = target_min - actual_foc
                else:
                    deviation = actual_foc - target_max
                foc_score = max(0, 100 - (deviation / 2.0) * 100)  # 2% FOC = 50% penalty
        
        total_score += foc_score * self.scoring_weights[MatchCriteria.FOC_TARGET]
        
        return round(total_score, 1)
    
    def _determine_confidence_level(self, spine_deviation: float, spine_range: Dict[str, float]) -> str:
        """Determine confidence level based on spine deviation"""
        
        range_width = spine_range['maximum'] - spine_range['minimum']
        deviation_ratio = spine_deviation / (range_width / 2)
        
        if deviation_ratio <= 0.3:
            return "high"
        elif deviation_ratio <= 0.7:
            return "medium"
        else:
            return "low"
    
    def _generate_match_reasons(self, arrow_details: Dict[str, Any], best_spine_match: Dict[str, Any],
                              optimal_spine: float, request: MatchRequest) -> List[str]:
        """Generate reasons why this arrow is a good match"""
        
        reasons = []
        
        # Spine match quality
        deviation = abs(best_spine_match['spine'] - optimal_spine)
        if deviation <= 10:
            reasons.append("Excellent spine match")
        elif deviation <= 25:
            reasons.append("Good spine match")
        else:
            reasons.append("Acceptable spine match")
        
        # Multiple spine options
        spine_count = len(arrow_details['spine_specifications'])
        if spine_count >= 6:
            reasons.append(f"Excellent availability ({spine_count} spine options)")
        elif spine_count >= 3:
            reasons.append(f"Good availability ({spine_count} spine options)")
        
        # Manufacturer match
        if request.preferred_manufacturers:
            manufacturer_lower = arrow_details['manufacturer'].lower()
            for pref in request.preferred_manufacturers:
                if pref.lower() in manufacturer_lower:
                    reasons.append(f"Preferred manufacturer ({arrow_details['manufacturer']})")
                    break
        
        # Diameter suitability
        if best_spine_match.get('outer_diameter'):
            diameter = best_spine_match['outer_diameter']
            if diameter <= 0.24:
                reasons.append("Small diameter for excellent penetration")
            elif diameter >= 0.30:
                reasons.append("Large diameter for maximum cutting surface")
        
        return reasons
    
    def _check_potential_issues(self, arrow_details: Dict[str, Any], best_spine_match: Dict[str, Any],
                              spine_range: Dict[str, float], request: MatchRequest) -> List[str]:
        """Check for potential issues with this arrow choice"""
        
        issues = []
        
        # Spine deviation warnings
        deviation = abs(best_spine_match['spine'] - ((spine_range['minimum'] + spine_range['maximum']) / 2))
        if deviation > 40:
            issues.append("Large spine deviation - may require tuning")
        elif deviation > 25:
            issues.append("Moderate spine deviation - paper tuning recommended")
        
        # Weight considerations
        if best_spine_match.get('gpi_weight'):
            gpi = best_spine_match['gpi_weight']
            if gpi > 12 and request.bow_config.bow_type == BowType.COMPOUND:
                issues.append("Heavy arrow - may reduce arrow speed significantly")
            elif gpi < 5:
                issues.append("Very light arrow - may cause noise and vibration")
        
        # Diameter issues
        if best_spine_match.get('outer_diameter'):
            diameter = best_spine_match['outer_diameter']
            if diameter < 0.20:
                issues.append("Very small diameter - may be fragile")
            elif diameter > 0.35:
                issues.append("Large diameter - may cause wind drift")
        
        # Availability concerns
        spine_count = len(arrow_details['spine_specifications'])
        if spine_count < 3:
            issues.append("Limited spine options available")
        
        return issues
    
    def _map_material_preference(self, material_preference: str) -> str:
        """Map frontend material values to database format"""
        
        # Material mapping from frontend values to database values
        material_mapping = {
            'carbon': 'Carbon',
            'aluminum': 'Aluminum', 
            'carbon-aluminum': 'Carbon / Aluminum',  # Frontend sends carbon-aluminum, DB has "Carbon / Aluminum"
            'wood': 'Wood',
            'fiberglass': 'Fiberglass'
        }
        
        # Normalize input to lowercase
        normalized_preference = material_preference.lower().strip()
        
        # Return mapped value or fallback to title case
        return material_mapping.get(normalized_preference, material_preference.title())
    
    def _format_manufacturer_filter(self, preferred_manufacturers: Optional[List[str]], 
                                   material_preference: Optional[str] = None) -> Optional[str]:
        """Format manufacturer list for database search, considering material preference"""
        
        # Manufacturer name mapping for common frontend names to database names
        manufacturer_mapping = {
            'Easton': 'Easton Archery',
            'Gold Tip': 'Gold Tip',
            'Victory': 'Victory Archery',
            'Carbon Express': 'Carbon Express',
            'Traditional Wood': 'Traditional Wood Arrows',
            'BigArchery': 'BigArchery',
            'Nijora': 'Nijora Archery',
            'DK Bow': 'DK Bow',
            'Aurel': 'Aurel Archery',
            'Fivics': 'Fivics',
            'Pandarus': 'Pandarus Archery',
            'Skylon': 'Skylon Archery'
        }
        
        # If wood material is requested, let the wood species logic handle manufacturer filtering
        if material_preference == 'wood':
            if preferred_manufacturers:
                # Check if any preferred manufacturers are wood manufacturers
                wood_manufacturers = ['Traditional Wood', 'Traditional Wood Arrows', 'Port Orford Cedar', 'Sitka Spruce', 'Douglas Fir', 'Pine', 'Ash', 'Bamboo']
                for pref in preferred_manufacturers:
                    if any(wood_mfr.lower() in pref.lower() for wood_mfr in wood_manufacturers):
                        return manufacturer_mapping.get(pref, pref)
                # If no wood manufacturers in preferences, return None to let species logic handle it
                return None
            else:
                # No preferences, return None to let wood species logic handle manufacturer selection
                return None
        
        # For non-wood materials, use existing logic
        if not preferred_manufacturers:
            return None
        
        # Map the first preference to database name
        first_pref = preferred_manufacturers[0]
        return manufacturer_mapping.get(first_pref, first_pref)
    
    def generate_recommendation_report(self, matches: List[ArrowMatch], request: MatchRequest) -> str:
        """Generate a detailed recommendation report"""
        
        if not matches:
            return "❌ No suitable arrows found for your bow configuration."
        
        report = f"""
🎯 ARROW RECOMMENDATION REPORT
{'=' * 60}

BOW CONFIGURATION:
• Type: {request.bow_config.bow_type.value.title()}
• Draw Weight: {request.bow_config.draw_weight}#
• Draw Length: {request.bow_config.draw_length}"
• Arrow Length: {request.arrow_length}"
• Point Weight: {request.point_weight} grains

TOP RECOMMENDATIONS:
"""
        
        for i, match in enumerate(matches[:5], 1):
            confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}
            
            # Calculate estimated total arrow weight
            estimated_shaft_weight = match.gpi_weight * request.arrow_length
            total_weight = estimated_shaft_weight + request.point_weight + request.nock_weight + request.fletching_weight
            
            # Calculate FOC
            foc_calc = self.spine_calculator.calculate_foc(
                request.arrow_length,
                request.point_weight,
                estimated_shaft_weight,
                request.nock_weight,
                request.fletching_weight,
                request.insert_weight
            )
            
            report += f"""
{i}. {match.manufacturer} {match.model_name}
   {confidence_emoji[match.confidence_level]} Match Score: {match.match_score}/100 ({match.confidence_level} confidence)
   • Spine: {match.matched_spine} (deviation: ±{match.spine_deviation:.0f})
   • Weight: {match.gpi_weight} GPI (~{total_weight:.0f} total grains)
   • Diameter: {match.outer_diameter:.3f}" 
   • FOC: {foc_calc['foc_percentage']:.1f}%
   • Available spines: {len(match.spine_specifications)} options
   
   ✅ Match Reasons:
"""
            for reason in match.match_reasons:
                report += f"      • {reason}\n"
            
            if match.potential_issues:
                report += "   ⚠️  Considerations:\n"
                for issue in match.potential_issues:
                    report += f"      • {issue}\n"
        
        report += f"""

TUNING NOTES:
• Fine-tune with paper tuning or walk-back tuning
• Consider broadhead testing for hunting setups
• Spine calculations are starting points - field testing is recommended
"""
        
        return report

# Example usage and testing
if __name__ == "__main__":
    print("🏹 Arrow Matching Engine Test")
    print("=" * 50)
    
    # Initialize engine
    engine = ArrowMatchingEngine()
    
    # Create test bow configuration
    test_bow = BowConfiguration(
        draw_weight=65,
        draw_length=28.5,
        bow_type=BowType.COMPOUND,
        cam_type="medium",
        arrow_rest_type="drop_away"
    )
    
    # Create match request
    request = MatchRequest(
        bow_config=test_bow,
        arrow_length=29,
        point_weight=100,
        preferred_manufacturers=["Gold Tip", "Easton"],
        target_diameter_range=(0.240, 0.300),
        target_foc_range=(8.0, 12.0),
        max_results=5
    )
    
    print(f"\n🎯 Test Request:")
    print(f"   Bow: {test_bow.draw_weight}# @ {test_bow.draw_length}\" compound")
    print(f"   Arrow: {request.arrow_length}\" with {request.point_weight}gr point")
    print(f"   Preferences: {request.preferred_manufacturers}")
    
    # Find matches
    matches = engine.find_matching_arrows(request)
    
    # Generate report
    report = engine.generate_recommendation_report(matches, request)
    print(report)