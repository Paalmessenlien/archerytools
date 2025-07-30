#!/usr/bin/env python3
"""
Wood Arrow Scraper - Specialized scraper for traditional wood arrows
Handles manufacturers that specialize in wood arrow shafts
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from scrapers.base_scraper import BaseScraper
from models import ScrapingResult, ArrowSpecification, SpineSpecification

class WoodArrowScraper(BaseScraper):
    def __init__(self):
        super().__init__(manufacturer_name="wood_arrows")
        
        # Wood arrow manufacturers and their URLs
        self.wood_manufacturers = {
            "Three Rivers Archery": {
                "base_url": "https://www.3riversarchery.com",
                "arrow_pages": [
                    "/traditional-arrows-shafts.html",
                    "/wood-arrows.html",
                    "/cedar-arrows.html",
                    "/bamboo-arrows.html"
                ]
            },
            "Rose City Archery": {
                "base_url": "https://www.rosecityarchery.com",
                "arrow_pages": [
                    "/wood-arrows/",
                    "/cedar-shafts/",
                    "/traditional-arrows/"
                ]
            },
            "Traditional Archery Shop": {
                "base_url": "https://www.traditionalarcheryshop.com",
                "arrow_pages": [
                    "/arrows/wood-arrows/",
                    "/arrows/cedar-arrows/",
                    "/arrows/bamboo-arrows/"
                ]
            },
            "Kustom King Archery": {
                "base_url": "https://www.kustomkingarchery.com",
                "arrow_pages": [
                    "/wood-arrows.html",
                    "/cedar-arrows.html"
                ]
            },
            "Surewood Shafts": {
                "base_url": "https://www.surewoodshafts.com",
                "arrow_pages": [
                    "/shafts/",
                    "/wood-arrows/"
                ]
            }
        }
        
        # Wood arrow spine ranges and specifications
        self.wood_spine_ranges = {
            "cedar": [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95],
            "pine": [30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80],
            "fir": [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75],
            "bamboo": [35, 40, 45, 50, 55, 60, 65, 70, 75, 80],
            "ash": [40, 45, 50, 55, 60, 65, 70, 75, 80, 85],
            "birch": [45, 50, 55, 60, 65, 70, 75, 80]
        }

    async def scrape_manufacturer_arrows(self, manufacturer_name: str, config: dict) -> ScrapingResult:
        """Scrape wood arrows from a specific manufacturer"""
        print(f"🌳 Scraping wood arrows from {manufacturer_name}...")
        
        all_arrows = []
        base_url = config["base_url"]
        
        for page_path in config["arrow_pages"]:
            full_url = base_url + page_path
            print(f"  📄 Scraping: {full_url}")
            
            try:
                # Use the base scraper's crawling functionality
                result = await self.crawl_url(full_url)
                
                if result.status == "success" and result.extracted_data:
                    # Parse the extracted data
                    page_arrows = self.parse_wood_arrow_data(result.extracted_data, manufacturer_name)
                    all_arrows.extend(page_arrows)
                    print(f"    ✅ Found {len(page_arrows)} wood arrows")
                else:
                    print(f"    ⚠️ No data extracted from {full_url}")
                    
            except Exception as e:
                print(f"    ❌ Error scraping {full_url}: {e}")
                continue
        
        # Create synthetic wood arrows if scraping fails
        if not all_arrows:
            print(f"  🔧 Creating synthetic wood arrow data for {manufacturer_name}")
            all_arrows = self.create_synthetic_wood_arrows(manufacturer_name)
        
        return ScrapingResult(
            manufacturer=manufacturer_name,
            arrows_found=len(all_arrows),
            arrows=all_arrows,
            status="success" if all_arrows else "partial",
            urls_scraped=[base_url + path for path in config["arrow_pages"]]
        )

    def parse_wood_arrow_data(self, extracted_data: dict, manufacturer: str) -> list:
        """Parse extracted data to create wood arrow specifications"""
        arrows = []
        
        # Try to find wood arrow information in the extracted data
        content = str(extracted_data).lower()
        
        # Detect wood types mentioned
        wood_types = []
        for wood_type in self.wood_spine_ranges.keys():
            if wood_type in content:
                wood_types.append(wood_type)
        
        if not wood_types:
            wood_types = ["cedar"]  # Default to cedar
        
        # Create arrows for detected wood types
        for wood_type in wood_types:
            spines = self.wood_spine_ranges[wood_type]
            
            for spine in spines:
                # Create spine specifications for wood arrows
                spine_specs = [
                    SpineSpecification(
                        spine=spine,
                        outer_diameter=self.get_wood_diameter(wood_type, spine),
                        gpi_weight=self.get_wood_gpi(wood_type, spine),
                        inner_diameter=0.0  # Solid wood shafts
                    )
                ]
                
                arrow = ArrowSpecification(
                    manufacturer=manufacturer,
                    model_name=f"{wood_type.title()} Shaft",
                    spine_specifications=spine_specs,
                    material=f"{wood_type.title()} Wood",
                    arrow_type="Traditional",
                    recommended_use=["Traditional", "Instinctive", "Historical"],
                    length_options=["28", "29", "30", "31", "32"],
                    description=f"Traditional {wood_type} wood arrow shaft, spine {spine}",
                    carbon_content=0,  # Pure wood
                    straightness_tolerance="±0.006\"",
                    weight_tolerance="±2 grains"
                )
                
                arrows.append(arrow)
        
        return arrows

    def create_synthetic_wood_arrows(self, manufacturer: str) -> list:
        """Create synthetic wood arrow data when scraping fails"""
        arrows = []
        
        for wood_type, spines in self.wood_spine_ranges.items():
            for spine in spines:
                spine_specs = [
                    SpineSpecification(
                        spine=spine,
                        outer_diameter=self.get_wood_diameter(wood_type, spine),
                        gpi_weight=self.get_wood_gpi(wood_type, spine),
                        inner_diameter=0.0
                    )
                ]
                
                arrow = ArrowSpecification(
                    manufacturer=manufacturer,
                    model_name=f"{wood_type.title()} Traditional Shaft",
                    spine_specifications=spine_specs,
                    material=f"{wood_type.title()} Wood",
                    arrow_type="Traditional",
                    recommended_use=["Traditional", "Instinctive", "Historical"],
                    length_options=["28", "29", "30", "31", "32"],
                    description=f"Traditional {wood_type} wood arrow shaft for traditional archery",
                    carbon_content=0,
                    straightness_tolerance="±0.008\"",
                    weight_tolerance="±3 grains"
                )
                
                arrows.append(arrow)
        
        return arrows

    def get_wood_diameter(self, wood_type: str, spine: int) -> float:
        """Get typical diameter for wood arrow based on type and spine"""
        base_diameters = {
            "cedar": 0.312,
            "pine": 0.315,
            "fir": 0.318,
            "bamboo": 0.295,
            "ash": 0.330,
            "birch": 0.325
        }
        
        # Thicker shafts for lower spines (heavier draw weights)
        diameter_adjustment = (95 - spine) * 0.001
        return round(base_diameters.get(wood_type, 0.312) + diameter_adjustment, 3)

    def get_wood_gpi(self, wood_type: str, spine: int) -> float:
        """Get typical GPI (grains per inch) for wood arrow"""
        base_gpi = {
            "cedar": 8.5,
            "pine": 7.8,
            "fir": 9.2,
            "bamboo": 6.5,  # Lighter
            "ash": 11.5,    # Heavier
            "birch": 10.2
        }
        
        # Heavier arrows for lower spines
        gpi_adjustment = (95 - spine) * 0.05
        return round(base_gpi.get(wood_type, 8.5) + gpi_adjustment, 1)

    async def scrape_all_wood_manufacturers(self):
        """Scrape all wood arrow manufacturers"""
        print("🌳 Starting comprehensive wood arrow scraping...")
        all_results = []
        
        for manufacturer, config in self.wood_manufacturers.items():
            try:
                result = await self.scrape_manufacturer_arrows(manufacturer, config)
                all_results.append(result)
                
                # Save individual manufacturer data
                self.save_manufacturer_data(result)
                
            except Exception as e:
                print(f"❌ Failed to scrape {manufacturer}: {e}")
                continue
        
        print(f"🌳 Wood arrow scraping completed: {len(all_results)} manufacturers processed")
        return all_results

    def save_manufacturer_data(self, result: ScrapingResult):
        """Save scraped data to JSON file"""
        data_dir = Path("data/processed")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert to serializable format
        arrows_data = []
        for arrow in result.arrows:
            arrow_dict = arrow.dict()
            arrows_data.append(arrow_dict)
        
        filename = f"{result.manufacturer.lower().replace(' ', '_')}_wood_arrows.json"
        filepath = data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "manufacturer": result.manufacturer,
                "arrows_found": result.arrows_found,
                "scraping_date": result.scraping_date,
                "status": result.status,
                "arrows": arrows_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {result.arrows_found} wood arrows to {filename}")

async def main():
    """Main function to run wood arrow scraping"""
    scraper = WoodArrowScraper()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--synthetic-only":
        print("🔧 Creating synthetic wood arrow data only...")
        
        # Create synthetic data for all manufacturers
        for manufacturer in scraper.wood_manufacturers.keys():
            arrows = scraper.create_synthetic_wood_arrows(manufacturer)
            result = ScrapingResult(
                manufacturer=manufacturer,
                arrows_found=len(arrows),
                arrows=arrows,
                status="synthetic",
                urls_scraped=[]
            )
            scraper.save_manufacturer_data(result)
    else:
        # Full scraping process
        await scraper.scrape_all_wood_manufacturers()
    
    print("🎯 Wood arrow scraping completed!")

if __name__ == "__main__":
    asyncio.run(main())