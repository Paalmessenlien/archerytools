#!/usr/bin/env python3
"""
Guide to file outputs for different scraper modes
"""

print("📁 FILE OUTPUT GUIDE FOR SCRAPER MODES")
print("=" * 50)

print("\n🥇 FAST MODE (Default - No API)")
print("   Command: python main.py --learn --manufacturer=easton --limit=3")
print("   Purpose: Pattern learning without API calls")
print("   ")
print("   Files Created:")
print("   ✅ data/content_patterns.json (pattern updates)")
print("   ❌ NO files in data/processed/ (no arrows extracted)")
print("   ")
print("   Why: Fast mode only learns content patterns, doesn't extract arrow data")

print("\n🥈 DEEPSEEK MODE (With API)")
print("   Command: python main.py --learn --manufacturer=easton --limit=3 --use-deepseek")
print("   Purpose: Full extraction with pattern learning")
print("   ")
print("   Files Created:")
print("   ✅ data/content_patterns.json (pattern updates)")
print("   ✅ data/processed/Easton_Archery_learn_YYYYMMDD_HHMMSS.json")
print("   ")
print("   Why: DeepSeek mode extracts real arrow data AND learns patterns")

print("\n🥉 CRAWL-ONLY MODE (Ultra Fast)")
print("   Command: python main.py --crawl-only --manufacturer=easton --limit=3")
print("   Purpose: Just collect raw content")
print("   ")
print("   Files Created:")
print("   ❌ NO files created (content stored in memory only)")
print("   ")
print("   Why: Crawl-only just collects raw HTML/markdown content")

print("\n🌍 LEARN-ALL MODES")
print("   Fast Mode: python main.py --learn-all --limit=1")
print("   ✅ data/content_patterns.json (updated)")
print("   ❌ NO data/processed/ files")
print("   ")
print("   DeepSeek Mode: python main.py --learn-all --limit=1 --use-deepseek")
print("   ✅ data/content_patterns.json (updated)")
print("   ✅ data/processed/[Manufacturer]_learn_[timestamp].json (for each manufacturer)")

print("\n📊 EXISTING FILES IN YOUR SYSTEM:")
print("   data/processed/Easton_Archery_learn_20250801_101124.json")
print("   data/processed/Gold_Tip_learn_20250801_101152.json")
print("   data/processed/Nijora_Archery_learn_20250801_101242.json")
print("   ↑ These are from previous DeepSeek mode runs")

print("\n🎯 WHAT MODE WERE YOU RUNNING?")
print("   If you ran: python main.py --learn --manufacturer=easton --limit=3")
print("   → Expected: Only content_patterns.json updated (NO processed files)")
print("   ")
print("   If you want JSON files with arrow data:")
print("   → Run: python main.py --learn --manufacturer=easton --limit=3 --use-deepseek")

print("\n🔍 CHECK WHAT WAS UPDATED:")
print("   1. content_patterns.json should show updated 'last_used' timestamps")
print("   2. success_count should have increased")
print("   3. For JSON files, you need --use-deepseek flag")

print("\n💡 RECOMMENDATION:")
print("   • Fast mode for pattern learning: Updates content_patterns.json only")
print("   • DeepSeek mode for arrow data: Creates both pattern and JSON files")
print("   • Check content_patterns.json to confirm fast mode worked")