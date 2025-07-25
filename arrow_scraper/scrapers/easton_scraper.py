from typing import List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.base_scraper import BaseScraper
from config.settings import MANUFACTURERS

class EastonScraper(BaseScraper):
    """Specialized scraper for Easton Archery arrows"""
    
    def __init__(self, deepseek_api_key: str):
        super().__init__("Easton", deepseek_api_key)
        self.manufacturer_config = MANUFACTURERS["easton"]
    
    def get_easton_extraction_prompt(self) -> str:
        """Get Easton-specific extraction prompt targeting HTML table data"""
        manufacturer_info = """
        EASTON-SPECIFIC EXTRACTION INSTRUCTIONS:
        
        Easton arrow specifications are stored in HTML tables with the following structure:
        - Column 1: "Size" or spine values (250, 300, 340, 400, 500, 610, 710, 880, 1000, etc.)
        - Column 2: "Shaft Weight GPI" or "GPI" (grains per inch like 5.5, 6.1, 7.3, 8.9, 10.8)
        - Column 3: "Shaft O.D. (inches)" or "Diameter" (like .204, .207, .213, .224, .245)
        - Column 4: "Stock Length (inches)" or length options (like 28.5, 29, 30, 32.63, 34)
        
        CRITICAL INSTRUCTIONS:
        1. Look for HTML tables with class="tablepress" or similar table structures
        2. Find the table headers: "Size", "GPI", "O.D.", "Length"
        3. Extract each ROW as a separate spine specification
        4. For each row, create a spine_specification object with:
           - spine: the Size/spine value (integer)
           - outer_diameter: the O.D. value (decimal number)
           - gpi_weight: the GPI value (decimal number) 
           - length_options: array of available lengths if specified
        
        EXAMPLE TABLE EXTRACTION:
        If you see a table row: "300 | 9.5 | .236 | *33.63"
        Extract as: {"spine": 300, "outer_diameter": 0.236, "gpi_weight": 9.5, "length_options": [33.63]}
        
        IMPORTANT:
        - Each table row = one spine_specification entry
        - Convert diameter values to decimal (e.g., ".245" becomes 0.245)
        - Spine values are integers (250, 300, 340, etc.)
        - GPI values are decimals (5.5, 9.5, 10.8, etc.)
        - Look for multiple tables on the same page (different arrow models)
        - Extract the arrow model name from headings above each table
        """
        return self.get_extraction_prompt(manufacturer_info)
    
    async def scrape_easton_category(self, category: str) -> List:
        """Scrape a specific Easton arrow category"""
        if category not in self.manufacturer_config["categories"]:
            raise ValueError(f"Unknown category: {category}")
        
        url = self.manufacturer_config["categories"][category]
        extraction_prompt = self.get_easton_extraction_prompt()
        
        result = await self.scrape_url(url, extraction_prompt)
        return result
    
    async def scrape_all_easton_categories(self) -> List:
        """Scrape all Easton arrow categories"""
        urls = list(self.manufacturer_config["categories"].values())
        extraction_prompt = self.get_easton_extraction_prompt()
        
        results = await self.scrape_multiple_urls(urls, extraction_prompt)
        return results