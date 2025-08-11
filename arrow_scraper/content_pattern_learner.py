#!/usr/bin/env python3
"""
Content Pattern Learner for Arrow Scraper
Learns and caches successful content extraction patterns to speed up future scraping
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse
from dataclasses import dataclass, asdict
import re

@dataclass
class ContentPattern:
    """Represents a successful content extraction pattern"""
    domain: str
    manufacturer: str
    pattern_type: str  # 'table', 'specs', 'list', etc.
    start_marker: str  # Text that indicates where data starts
    end_marker: str    # Text that indicates where data ends
    content_slice: Tuple[int, int]  # (start_pos, end_pos) relative positions
    extraction_method: str  # 'text', 'vision', 'knowledge'
    success_count: int = 1
    last_used: str = ""
    confidence_score: float = 1.0
    sample_content: str = ""  # First 200 chars for pattern matching

class ContentPatternLearner:
    """Learns and applies content extraction patterns for faster scraping"""
    
    def __init__(self, cache_file: str = "data/content_patterns.json"):
        self.cache_file = Path(cache_file)
        self.patterns: Dict[str, ContentPattern] = {}
        self.load_patterns()
        
        # Common patterns to look for
        self.table_indicators = [
            'spine', 'gpi', 'diameter', 'weight', 'specifications',
            'tablepress', 'specs specs-loaded', 'tech_daten',
            'rundlaufgenauigkeit', 'offcanvas-body'
        ]
        
    def load_patterns(self):
        """Load existing patterns from cache"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for pattern_id, pattern_data in data.items():
                    self.patterns[pattern_id] = ContentPattern(**pattern_data)
                    
                print(f"📚 Loaded {len(self.patterns)} content patterns")
            except Exception as e:
                print(f"⚠️  Error loading patterns: {e}")
                self.patterns = {}
    
    def save_patterns(self):
        """Save patterns to cache"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert patterns to dict for JSON serialization
            data = {
                pattern_id: asdict(pattern) 
                for pattern_id, pattern in self.patterns.items()
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️  Error saving patterns: {e}")
    
    def generate_pattern_id(self, domain: str, manufacturer: str, pattern_type: str) -> str:
        """Generate unique pattern ID"""
        key = f"{domain}_{manufacturer}_{pattern_type}".lower()
        return hashlib.md5(key.encode()).hexdigest()[:16]
    
    def learn_successful_pattern(self, url: str, content: str, manufacturer: str, 
                                extraction_method: str, extracted_data: List[Any]):
        """Learn from a successful extraction"""
        if not extracted_data:
            return
            
        domain = urlparse(url).netloc
        content_lower = content.lower()
        
        # Detect pattern type and markers
        pattern_info = self._analyze_content_structure(content, content_lower)
        if not pattern_info:
            return
            
        pattern_type, start_marker, end_marker, content_slice = pattern_info
        
        # Generate pattern ID
        pattern_id = self.generate_pattern_id(domain, manufacturer, pattern_type)
        
        # Create or update pattern
        if pattern_id in self.patterns:
            # Update existing pattern
            pattern = self.patterns[pattern_id]
            pattern.success_count += 1
            pattern.last_used = datetime.now().isoformat()
            pattern.confidence_score = min(1.0, pattern.confidence_score + 0.1)
            print(f"📈 Updated pattern: {pattern_type} for {domain} (uses: {pattern.success_count})")
        else:
            # Create new pattern
            sample_content = content[content_slice[0]:content_slice[0]+200] if content_slice[0] >= 0 else ""
            
            pattern = ContentPattern(
                domain=domain,
                manufacturer=manufacturer,
                pattern_type=pattern_type,
                start_marker=start_marker,
                end_marker=end_marker,
                content_slice=content_slice,
                extraction_method=extraction_method,
                success_count=1,
                last_used=datetime.now().isoformat(),
                confidence_score=1.0,
                sample_content=sample_content
            )
            
            self.patterns[pattern_id] = pattern
            print(f"🧠 Learned new pattern: {pattern_type} for {domain}")
        
        # Save patterns periodically
        if len(self.patterns) % 5 == 0:  # Save every 5 new patterns
            self.save_patterns()
    
    def _analyze_content_structure(self, content: str, content_lower: str) -> Optional[Tuple[str, str, str, Tuple[int, int]]]:
        """Analyze content to identify extraction patterns"""
        
        # Look for table patterns
        table_patterns = [
            ('easton_table', 'spine', 'shaft weight', 'gpi'),
            ('goldtip_specs', 'specs specs-loaded', 'spine', 'gpi'),
            ('nijora_table', 'tablepress', 'spine', 'grain/inch'),
            ('dk_table', 'offcanvas-body', 'rundlaufgenauigkeit', 'sw-text-editor-table'),
            ('generic_table', 'spine', 'diameter', 'weight')
        ]
        
        for pattern_name, start_indicator, middle_indicator, end_indicator in table_patterns:
            start_pos = content_lower.find(start_indicator.lower())
            middle_pos = content_lower.find(middle_indicator.lower())
            end_pos = content_lower.find(end_indicator.lower())
            
            if start_pos >= 0 and middle_pos >= 0:
                # Found a potential table pattern
                # Calculate optimal slice window
                slice_start = max(0, start_pos - 1000)  # Include some context before
                slice_end = min(len(content), end_pos + 2000) if end_pos >= 0 else start_pos + 8000
                
                return (
                    pattern_name,
                    start_indicator,
                    end_indicator if end_pos >= 0 else middle_indicator,
                    (slice_start, slice_end)
                )
        
        # Look for specification list patterns
        if any(indicator in content_lower for indicator in ['specifications', 'tech specs', 'arrow specs']):
            spec_pos = next((content_lower.find(ind) for ind in ['specifications', 'tech specs', 'arrow specs'] if content_lower.find(ind) >= 0), -1)
            if spec_pos >= 0:
                return (
                    'spec_list',
                    'specifications',
                    'description',
                    (max(0, spec_pos - 500), spec_pos + 3000)
                )
        
        return None
    
    def get_optimized_content_slice(self, url: str, content: str, manufacturer: str) -> Optional[Tuple[str, int, int]]:
        """Get optimized content slice based on learned patterns"""
        domain = urlparse(url).netloc
        content_lower = content.lower()
        
        # Find matching patterns for this domain/manufacturer
        matching_patterns = [
            pattern for pattern in self.patterns.values()
            if pattern.domain == domain and 
            pattern.manufacturer.lower() == manufacturer.lower() and
            pattern.confidence_score > 0.5
        ]
        
        if not matching_patterns:
            return None
            
        # Sort by success count and confidence
        matching_patterns.sort(key=lambda p: (p.success_count, p.confidence_score), reverse=True)
        best_pattern = matching_patterns[0]
        
        # Check if the pattern markers are present in current content
        start_pos = content_lower.find(best_pattern.start_marker.lower())
        if start_pos < 0:
            return None
            
        # Calculate optimized slice based on learned pattern
        if best_pattern.content_slice[0] >= 0:
            # Use relative positioning from the learned pattern
            slice_start = max(0, start_pos + best_pattern.content_slice[0] - start_pos)
            slice_end = min(len(content), start_pos + best_pattern.content_slice[1] - best_pattern.content_slice[0])
        else:
            # Use negative positioning (from end of content)
            content_len = len(content)
            slice_start = max(0, content_len + best_pattern.content_slice[0])  # e.g., len + (-25000)
            slice_end = min(content_len, content_len + best_pattern.content_slice[1])  # e.g., len + (-1000)
        
        print(f"🎯 Using learned pattern: {best_pattern.pattern_type} (used {best_pattern.success_count} times)")
        print(f"🎯 Optimized slice: {slice_end - slice_start} chars (vs default ~15000)")
        
        return (best_pattern.pattern_type, slice_start, slice_end)
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about learned patterns"""
        if not self.patterns:
            return {"total_patterns": 0}
            
        stats = {
            "total_patterns": len(self.patterns),
            "by_domain": {},
            "by_manufacturer": {},
            "by_pattern_type": {},
            "most_successful": [],
            "recent_patterns": []
        }
        
        for pattern in self.patterns.values():
            # By domain
            if pattern.domain not in stats["by_domain"]:
                stats["by_domain"][pattern.domain] = 0
            stats["by_domain"][pattern.domain] += 1
            
            # By manufacturer
            if pattern.manufacturer not in stats["by_manufacturer"]:
                stats["by_manufacturer"][pattern.manufacturer] = 0
            stats["by_manufacturer"][pattern.manufacturer] += 1
            
            # By pattern type
            if pattern.pattern_type not in stats["by_pattern_type"]:
                stats["by_pattern_type"][pattern.pattern_type] = 0
            stats["by_pattern_type"][pattern.pattern_type] += 1
        
        # Most successful patterns
        successful_patterns = sorted(self.patterns.values(), key=lambda p: p.success_count, reverse=True)[:5]
        stats["most_successful"] = [
            {
                "domain": p.domain,
                "manufacturer": p.manufacturer,
                "pattern_type": p.pattern_type,
                "success_count": p.success_count,
                "confidence": p.confidence_score
            }
            for p in successful_patterns
        ]
        
        return stats
    
    def cleanup_old_patterns(self, days_old: int = 30):
        """Remove patterns that haven't been used recently"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        patterns_to_remove = []
        for pattern_id, pattern in self.patterns.items():
            if pattern.last_used:
                last_used = datetime.fromisoformat(pattern.last_used)
                if last_used < cutoff_date and pattern.success_count < 3:
                    patterns_to_remove.append(pattern_id)
        
        for pattern_id in patterns_to_remove:
            del self.patterns[pattern_id]
        
        if patterns_to_remove:
            print(f"🧹 Cleaned up {len(patterns_to_remove)} old patterns")
            self.save_patterns()


def test_pattern_learning():
    """Test the pattern learning system"""
    learner = ContentPatternLearner("test_patterns.json")
    
    # Simulate successful extraction
    test_content = """
    Some content here...
    <div class="specs specs-loaded">
        <table>
            <tr><th>Spine</th><th>GPI</th><th>Diameter</th></tr>
            <tr><td>400</td><td>8.2</td><td>0.246</td></tr>
        </table>
    </div>
    More content...
    """
    
    # Learn from successful extraction
    learner.learn_successful_pattern(
        url="https://goldtip.com/arrows/test",
        content=test_content,
        manufacturer="Gold Tip",
        extraction_method="text",
        extracted_data=[{"spine": 400, "gpi": 8.2}]
    )
    
    # Test getting optimized slice
    optimized = learner.get_optimized_content_slice(
        url="https://goldtip.com/arrows/another-test",
        content=test_content,
        manufacturer="Gold Tip"
    )
    
    print("Optimized slice:", optimized)
    
    # Show statistics
    stats = learner.get_pattern_statistics()
    print("Pattern statistics:", json.dumps(stats, indent=2))

if __name__ == "__main__":
    test_pattern_learning()