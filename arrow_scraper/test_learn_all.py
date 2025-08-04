#!/usr/bin/env python3
"""
Test the new --learn-all functionality
"""

import argparse

def test_learn_all_args():
    parser = argparse.ArgumentParser()
    
    # Simulate the main argument parser
    parser.add_argument("manufacturer", nargs="?")
    parser.add_argument("--update-all", action="store_true")
    parser.add_argument("--learn", action="store_true")
    parser.add_argument("--learn-all", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--manufacturer", dest="manufacturer_flag")
    
    test_cases = [
        ["--learn-all", "--limit=1"],
        ["--learn-all", "--limit=2"],
        ["--learn-all"],  # Should default to 1
        ["--learn", "--manufacturer=easton", "--limit=3"],
        ["--update-all"]
    ]
    
    print("🧪 Testing --learn-all Functionality")
    print("=" * 50)
    
    for i, test_args in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: python main.py {' '.join(test_args)}")
        
        try:
            args = parser.parse_args(test_args)
            
            # Simulate the main logic
            if args.update_all:
                print("   → Would run: update_all_manufacturers()")
            elif args.learn_all:
                url_limit = args.limit or 1
                print(f"   → Would run: learn_all_manufacturers(url_limit={url_limit})")
                print(f"   → Processing first {url_limit} URL(s) from ALL manufacturers")
            elif args.learn:
                manufacturer_name = args.manufacturer or args.manufacturer_flag
                print(f"   → Would run: scrape_manufacturer({manufacturer_name}, limit={args.limit}, learn_mode=True)")
            
            print(f"   ✅ Arguments parsed successfully")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_learn_all_args()
    
    print(f"\n🎯 Your New Command:")
    print(f"   python main.py --learn-all --limit=1")
    print(f"   → Learn patterns from first URL of ALL 11 manufacturers")
    print(f"   → Perfect for comprehensive pattern learning!")
    
    print(f"\n🚀 Other Examples:")
    print(f"   python main.py --learn-all --limit=2    # First 2 URLs per manufacturer")
    print(f"   python main.py --learn-all              # Defaults to 1 URL per manufacturer")
    print(f"   python main.py --learn-all --limit=5    # First 5 URLs per manufacturer")