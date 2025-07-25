#!/usr/bin/env python3
"""
Run multiple batches and combine results
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime

async def run_batch(batch_size, start_index):
    """Run a single batch and return results"""
    from run_batch_extraction import run_batch_extraction
    return await run_batch_extraction(batch_size, start_index)

async def run_multi_batch():
    """Run multiple batches to cover more URLs efficiently"""
    print("🚀 Running Multi-Batch Arrow Extraction")
    print("=" * 45)
    
    # Configuration
    batch_size = 8  # Smaller batches for speed
    max_batches = 5  # Process first 40 URLs
    
    print(f"📦 Processing {max_batches} batches of {batch_size} URLs each")
    print(f"🎯 Total URLs to process: {max_batches * batch_size}")
    
    all_results = []
    total_arrows = 0
    
    for batch_num in range(max_batches):
        start_index = batch_num * batch_size
        print(f"\n{'='*60}")
        print(f"🔄 BATCH {batch_num + 1}/{max_batches} (URLs {start_index}-{start_index + batch_size - 1})")
        print(f"{'='*60}")
        
        try:
            arrows_found = await run_batch(batch_size, start_index)
            total_arrows += arrows_found
            all_results.append({
                "batch_number": batch_num + 1,
                "start_index": start_index,
                "arrows_found": arrows_found
            })
            print(f"✅ Batch {batch_num + 1} complete: {arrows_found} arrows")
            
        except Exception as e:
            print(f"❌ Batch {batch_num + 1} failed: {e}")
            all_results.append({
                "batch_number": batch_num + 1,
                "start_index": start_index,
                "arrows_found": 0,
                "error": str(e)
            })
        
        # Short break between batches
        if batch_num < max_batches - 1:
            print(f"⏸️  Waiting 10 seconds before next batch...")
            await asyncio.sleep(10)
    
    # Combine all batch results
    print(f"\n{'='*60}")
    print(f"📊 MULTI-BATCH SUMMARY")
    print(f"{'='*60}")
    print(f"Total batches processed: {max_batches}")
    print(f"Total arrows extracted: {total_arrows}")
    print(f"URLs processed: {max_batches * batch_size}")
    
    # Show batch breakdown
    print(f"\n📋 Batch Results:")
    for result in all_results:
        if "error" in result:
            print(f"   Batch {result['batch_number']}: ❌ {result['error']}")
        else:
            print(f"   Batch {result['batch_number']}: ✅ {result['arrows_found']} arrows")
    
    # Combine all batch files into one comprehensive result
    combined_arrows = []
    combined_failed = []
    
    data_dir = Path("data/processed")
    for batch_file in data_dir.glob("batch_*.json"):
        try:
            with open(batch_file, 'r') as f:
                batch_data = json.load(f)
                combined_arrows.extend(batch_data.get("arrows", []))
                combined_failed.extend(batch_data.get("failed_urls", []))
        except Exception as e:
            print(f"⚠️  Could not read {batch_file}: {e}")
    
    if combined_arrows:
        # Save comprehensive results
        comprehensive_data = {
            "extraction_timestamp": datetime.now().isoformat(),
            "extraction_type": "multi_batch_comprehensive",
            "total_arrows": len(combined_arrows),
            "total_spine_specs": sum(len(arrow.get("spine_specifications", [])) for arrow in combined_arrows),
            "batches_processed": max_batches,
            "urls_processed": max_batches * batch_size,
            "failed_urls": len(combined_failed),
            "arrows": combined_arrows,
            "batch_summary": all_results
        }
        
        output_file = Path("data/processed/multi_batch_comprehensive_results.json")
        with open(output_file, 'w') as f:
            json.dump(comprehensive_data, f, indent=2)
        
        print(f"\n💾 Comprehensive results saved to {output_file}")
        print(f"🎉 FINAL RESULTS:")
        print(f"   Total arrows: {len(combined_arrows)}")
        print(f"   Total spine specifications: {sum(len(arrow.get('spine_specifications', [])) for arrow in combined_arrows)}")
        print(f"   Success rate: {((max_batches * batch_size - len(combined_failed)) / (max_batches * batch_size) * 100):.1f}%")
        
        # Show some sample results
        unique_models = set(arrow.get("model_name", "Unknown") for arrow in combined_arrows)
        print(f"   Unique arrow models: {len(unique_models)}")
        
        manufacturers = set(arrow.get("manufacturer", "Unknown") for arrow in combined_arrows)
        print(f"   Manufacturers represented: {len(manufacturers)}")
        print(f"   Manufacturers: {', '.join(sorted(manufacturers))}")

def main():
    asyncio.run(run_multi_batch())

if __name__ == "__main__":
    main()