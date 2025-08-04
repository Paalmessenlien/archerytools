#!/usr/bin/env python3
"""
Debug the argument parsing issue
"""

import argparse
import sys

def debug_args():
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
        help="Manufacturer name for scraping"
    )
    
    # Test the exact command
    test_args = ["--learn", "--manufacturer=easton", "--limit=3"]
    
    print(f"🔍 Debugging: {' '.join(test_args)}")
    print("=" * 50)
    
    try:
        args = parser.parse_args(test_args)
        
        print(f"Parsed arguments:")
        print(f"  args.manufacturer (positional): {getattr(args, 'manufacturer', 'NOT SET - this is the issue!')}")
        print(f"  args.manufacturer (flag): {getattr(args, 'manufacturer', 'NOT SET')}")
        print(f"  args.learn: {getattr(args, 'learn', False)}")
        print(f"  args.limit: {getattr(args, 'limit', None)}")
        
        print(f"\n🔍 All parsed attributes:")
        for attr in dir(args):
            if not attr.startswith('_'):
                print(f"  {attr}: {getattr(args, attr)}")
                
        print(f"\n🧪 Logic test:")
        print(f"  not args.manufacturer: {not getattr(args, 'manufacturer', None)}")
        print(f"  args.manufacturer value: '{getattr(args, 'manufacturer', None)}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_args()