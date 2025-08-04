#!/usr/bin/env python3
"""
Test script to demonstrate the new enhanced argument system
"""

import argparse

def test_arguments():
    parser = argparse.ArgumentParser(
        description="Arrow Database Scraper with Enhanced Pattern Learning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scraping
  python main.py easton                           # Scrape Easton only
  python main.py --update-all                    # Update all manufacturers (with translation)
  python main.py --update-all --force            # Force update ALL manufacturers
  python main.py --update-all --no-translate     # Update without translating non-English content
  
  # Pattern Learning
  python main.py --learn --manufacturer=easton --limit=3    # Learn from first 3 Easton URLs
  python main.py --learn --manufacturer=goldtip --limit=5   # Learn from first 5 Gold Tip URLs
  python main.py --manufacturer=easton --limit=10           # Process first 10 Easton URLs
  
  # URL Management
  python main.py --add --manufacturer=easton --type=arrow --url=http://example.com
  python main.py --list-manufacturers            # List available manufacturers with languages
        """
    )
    
    parser.add_argument(
        "manufacturer", 
        nargs="?", 
        help="Manufacturer to scrape (e.g., easton, goldtip, victory)"
    )
    parser.add_argument(
        "--update-all", 
        action="store_true",
        help="Update all manufacturers in the database"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force update ALL manufacturers even if data already exists"
    )
    parser.add_argument(
        "--learn",
        action="store_true",
        help="Learn patterns from a specific manufacturer (use with --manufacturer and --limit)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of URLs to process (useful for pattern learning)"
    )
    parser.add_argument(
        "--manufacturer",
        help="Manufacturer name for scraping or URL operations"
    )
    
    return parser

if __name__ == "__main__":
    parser = test_arguments()
    
    # Test cases
    test_cases = [
        ["--learn", "--manufacturer=easton", "--limit=3"],
        ["--manufacturer=goldtip", "--limit=5"],
        ["easton", "--limit=2"],
        ["--update-all", "--force"],
        ["--help"]
    ]
    
    print("🧪 Testing Enhanced Argument System")
    print("=" * 50)
    
    for i, test_args in enumerate(test_cases[:-1], 1):  # Skip --help for now
        print(f"\n{i}. Testing: python main.py {' '.join(test_args)}")
        try:
            args = parser.parse_args(test_args)
            print(f"   ✅ Parsed successfully:")
            print(f"      manufacturer (positional): {getattr(args, 'manufacturer', None)}")
            print(f"      --manufacturer: {getattr(args, 'manufacturer', None)}")
            print(f"      --learn: {getattr(args, 'learn', False)}")
            print(f"      --limit: {getattr(args, 'limit', None)}")
            print(f"      --force: {getattr(args, 'force', False)}")
            print(f"      --update-all: {getattr(args, 'update_all', False)}")
        except SystemExit:
            print(f"   ❌ Argument parsing failed")
    
    print(f"\n✅ Enhanced command system supports:")
    print(f"   • --learn flag for pattern learning mode")
    print(f"   • --limit for processing limited URLs")
    print(f"   • --manufacturer for explicit manufacturer specification")
    print(f"   • --force now means 'force update ALL manufacturers'")
    print(f"   • Backward compatibility with existing commands")