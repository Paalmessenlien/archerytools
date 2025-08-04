#!/usr/bin/env python3
"""
Test Pattern Learning System
Demonstrates how the scraper learns content patterns for faster extraction
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from content_pattern_learner import ContentPatternLearner

def create_test_content():
    """Create test content similar to real manufacturer pages"""
    return {
        "easton_content": """
        <div class="main-content">
            <h1>X10 PROTOUR</h1>
            <p>Some description text...</p>
            <div class="specs-table">
                <table>
                    <tr><th>Spine</th><th>Shaft Weight GPI</th><th>Shaft O.D. (inches)</th></tr>
                    <tr><td>350</td><td>3.9</td><td>0.166</td></tr>
                    <tr><td>400</td><td>4.2</td><td>0.166</td></tr>
                </table>
            </div>
            <p>More content...</p>
        </div>
        """,
        
        "goldtip_content": """
        <div class="product-details">
            <h2>Nine3 Max Plus</h2>
            <div class="specs specs-loaded">
                <div class="card-body p-0">
                    <table class="table">
                        <thead><tr><th>SPINE</th><th>GPI</th><th>OD</th></tr></thead>
                        <tbody>
                            <tr><td>300</td><td>8.2</td><td>.291"</td></tr>
                            <tr><td>340</td><td>7.8</td><td>.291"</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """,
        
        "nijora_content": """
        <div class="product">
            <h3>Elsu Pro</h3>
            <div class="tablepress-id-123">
                <table>
                    <tr><th>Spine</th><th>Grain/Inch</th><th>Durchmesser</th></tr>
                    <tr><td>500</td><td>8.5</td><td>6.2mm</td></tr>
                    <tr><td>600</td><td>7.8</td><td>6.2mm</td></tr>
                </table>
            </div>
        </div>
        """
    }

def test_pattern_learning():
    """Test the pattern learning system"""
    
    print("🧪 Testing Pattern Learning System")
    print("=" * 50)
    
    # Create learner with test file
    test_file = Path("test_patterns.json")
    learner = ContentPatternLearner(str(test_file))
    
    # Clean up any existing test patterns
    if test_file.exists():
        test_file.unlink()
    
    test_content = create_test_content()
    
    print("\n1️⃣ Learning from successful extractions...")
    
    # Simulate successful extractions
    test_cases = [
        {
            "url": "https://eastonarchery.com/arrows_/x10-protour/",
            "content": test_content["easton_content"],
            "manufacturer": "Easton Archery",
            "extracted_data": [{"spine": 350, "gpi": 3.9}, {"spine": 400, "gpi": 4.2}]
        },
        {
            "url": "https://eastonarchery.com/arrows_/x10-parallel/",
            "content": test_content["easton_content"],  # Same pattern
            "manufacturer": "Easton Archery", 
            "extracted_data": [{"spine": 340, "gpi": 4.0}]
        },
        {
            "url": "https://goldtip.com/arrows/nine3-max-plus/",
            "content": test_content["goldtip_content"],
            "manufacturer": "Gold Tip",
            "extracted_data": [{"spine": 300, "gpi": 8.2}, {"spine": 340, "gpi": 7.8}]
        },
        {
            "url": "https://nijora-archery.de/elsu-pro/",
            "content": test_content["nijora_content"],
            "manufacturer": "Nijora Archery",
            "extracted_data": [{"spine": 500, "gpi": 8.5}]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"   📚 Learning from {test_case['url'].split('/')[-2]}...")
        learner.learn_successful_pattern(
            url=test_case["url"],
            content=test_case["content"],
            manufacturer=test_case["manufacturer"],
            extraction_method="text",
            extracted_data=test_case["extracted_data"]
        )
    
    print("\n2️⃣ Testing pattern recognition and optimization...")
    
    # Test getting optimized slices
    test_optimizations = [
        ("https://eastonarchery.com/arrows_/new-arrow/", test_content["easton_content"], "Easton Archery"),
        ("https://goldtip.com/arrows/new-arrow/", test_content["goldtip_content"], "Gold Tip"),
        ("https://nijora-archery.de/new-arrow/", test_content["nijora_content"], "Nijora Archery")
    ]
    
    for url, content, manufacturer in test_optimizations:
        print(f"   🎯 Testing optimization for {manufacturer}...")
        optimization = learner.get_optimized_content_slice(url, content, manufacturer)
        
        if optimization:
            pattern_type, slice_start, slice_end = optimization
            optimized_size = slice_end - slice_start
            original_size = len(content)
            savings = ((original_size - optimized_size) / original_size) * 100
            
            print(f"      ✅ Pattern: {pattern_type}")
            print(f"      📏 Size: {optimized_size} chars (vs {original_size} original)")
            print(f"      ⚡ Savings: {savings:.1f}% reduction")
        else:
            print(f"      ❌ No pattern found")
        print()
    
    print("3️⃣ Pattern Learning Statistics...")
    stats = learner.get_pattern_statistics()
    
    print(f"   📊 Total patterns: {stats.get('total_patterns', 0)}")
    print(f"   🌐 Domains: {list(stats.get('by_domain', {}).keys())}")
    print(f"   🏭 Manufacturers: {list(stats.get('by_manufacturer', {}).keys())}")
    print(f"   📋 Pattern types: {list(stats.get('by_pattern_type', {}).keys())}")
    
    if stats.get('most_successful'):
        print(f"\n   🏆 Most successful patterns:")
        for pattern in stats['most_successful']:
            print(f"      • {pattern['domain']} - {pattern['pattern_type']}: {pattern['success_count']} uses")
    
    print("\n4️⃣ Speed Improvement Simulation...")
    
    # Simulate speed improvements
    print("   Without Pattern Learning:")
    print("   📎 [1/3] Processing URL... ✓ Crawled (15,000 chars) → ✅ 2 arrows (3.2s)")
    print("   📎 [2/3] Processing URL... ✓ Crawled (16,500 chars) → ✅ 1 arrow (3.5s)")
    print("   📎 [3/3] Processing URL... ✓ Crawled (14,800 chars) → ✅ 3 arrows (3.1s)")
    print("   ⏱️  Total time: 9.8 seconds")
    
    print("\n   With Pattern Learning:")
    print("   📎 [1/3] Processing URL... ✓ Crawled 🎯 Using learned easton_table pattern: 2,500 chars (vs 15,000 original) → ✅ 2 arrows (1.8s)")
    print("   📎 [2/3] Processing URL... ✓ Crawled 🎯 Using learned easton_table pattern: 2,300 chars (vs 16,500 original) → ✅ 1 arrow (1.6s)")
    print("   📎 [3/3] Processing URL... ✓ Crawled 🎯 Using learned easton_table pattern: 2,600 chars (vs 14,800 original) → ✅ 3 arrows (1.9s)")
    print("   ⚡ Total time: 5.3 seconds (46% faster!)")
    
    # Clean up test file
    if test_file.exists():
        test_file.unlink()
    
    print("\n✅ Pattern Learning Test Complete!")
    print("\n🎯 Key Benefits:")
    print("   • Learns successful content extraction patterns")
    print("   • Reduces content size sent to AI (faster processing)")
    print("   • Improves over time with more extractions")
    print("   • Significantly speeds up repeated scraping")
    print("   • Works across different manufacturers and domains")

if __name__ == "__main__":
    test_pattern_learning()