#!/usr/bin/env python3
"""
Test the fixed argument parsing
"""

import argparse
import sys

def test_fixed_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "manufacturer", 
        nargs="?", 
        help="Manufacturer to scrape (e.g., easton, goldtip, victory)"
    )
    parser.add_argument(
        "--learn",
        action="store_true",
        help="Learn patterns from a specific manufacturer"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of URLs to process"
    )
    parser.add_argument(
        "--manufacturer",
        dest="manufacturer_flag",  # This is the fix!
        help="Manufacturer name for scraping"
    )
    
    # Test cases
    test_cases = [
        ["--learn", "--manufacturer=easton", "--limit=3"],
        ["--manufacturer=goldtip", "--limit=5"],
        ["easton", "--limit=2"],
        ["--learn", "--manufacturer=easton", "--limit=1"]
    ]
    
    print("🔧 Testing Fixed Argument System")
    print("=" * 50)
    
    for i, test_args in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {' '.join(test_args)}")
        
        try:
            args = parser.parse_args(test_args)
            
            # Apply the same logic as main.py
            manufacturer_name = args.manufacturer or args.manufacturer_flag
            
            print(f"   ✅ SUCCESS!")
            print(f"      args.manufacturer (positional): {args.manufacturer}")
            print(f"      args.manufacturer_flag (--manufacturer): {args.manufacturer_flag}")
            print(f"      Final manufacturer_name: {manufacturer_name}")
            print(f"      args.learn: {args.learn}")
            print(f"      args.limit: {args.limit}")
            
            # Test the logic conditions
            if args.learn:
                if not manufacturer_name:
                    print(f"      ❌ Would fail: --learn requires --manufacturer")
                else:
                    print(f"      ✅ Would succeed: Learn mode with {manufacturer_name}")
            elif manufacturer_name:
                print(f"      ✅ Would succeed: Scrape {manufacturer_name} with limit {args.limit}")
            
        except Exception as e:
            print(f"   ❌ FAILED: {e}")

if __name__ == "__main__":
    test_fixed_args()