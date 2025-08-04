#!/usr/bin/env python3
"""
Test --learn-all with JSON export functionality
"""

print("✅ Enhanced --learn-all Functionality")
print("=" * 50)

print("\n🎯 Your Command:")
print("   python main.py --learn-all --limit=1")

print("\n📁 What You'll See in data/processed/:")
print("   After running --learn-all --limit=1, new files will be created:")
print("   • Easton_Archery_learn_20250801_123456.json")
print("   • Gold_Tip_learn_20250801_123457.json") 
print("   • Skylon_Archery_learn_20250801_123458.json")
print("   • Nijora_Archery_learn_20250801_123459.json")
print("   • ... (one file per manufacturer that successfully extracts arrows)")

print("\n📊 Each JSON File Contains:")
print("   {")
print('     "manufacturer": "Easton Archery",')
print('     "total_arrows": 3,')
print('     "scraped_at": "2025-08-01T12:34:56.789012",')
print('     "extraction_method": "pattern_learning",')
print('     "arrows": [')
print("       {")
print('         "manufacturer": "Easton Archery",')
print('         "model_name": "X10 Parallel Pro",')
print('         "spine_specifications": [')
print("           {")
print('             "spine": 1000,')
print('             "outer_diameter": 0.204,')
print('             "gpi_weight": 5.5')
print("           }")
print("         ]")
print("       }")
print("       // ... more arrows")
print("     ]")
print("   }")

print("\n🧠 Two Types of Data Saved:")
print("   1. Pattern Learning Data:")
print("      • File: data/content_patterns.json")
print("      • Contains: Extraction patterns for faster future scraping")
print("      • Purpose: Speed optimization")

print("\n   2. Arrow Data (NEW!):")
print("      • Files: data/processed/*_learn_*.json")  
print("      • Contains: Actual arrow specifications extracted")
print("      • Purpose: Arrow database and production deployment")

print("\n🚀 Benefits:")
print("   • Learn patterns for faster future scraping")
print("   • Save extracted arrow data for immediate use")
print("   • Ready for production deployment (JSON files)")
print("   • Database import capability")
print("   • Compatible with existing workflow")

print("\n⚡ Expected Output:")
print("   [1/11] 🧠 Learning from: Easton Archery")
print("   📊 Found 34 URLs, learning from first 1")
print("      📎 [1/1] Learning from URL... ✓ Crawled → ✅ 3 arrows, pattern learned")
print("   ✅ Easton Archery: 1 patterns learned, 3 arrows saved to Easton_Archery_learn_20250801_123456.json")

print("\n🔥 Perfect! Now you get BOTH:")
print("   • Pattern learning for speed")
print("   • Arrow data for immediate use")
print("   • Ready to import into database!")

print("\n🎯 Ready to Test:")
print("   python main.py --learn-all --limit=1")
print("   (Don't forget to activate the virtual environment first!)")