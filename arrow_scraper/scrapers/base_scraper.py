import asyncio
import logging
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import random

from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models import ArrowSpecification, SpineSpecification, ScrapingResult, ScrapingSession
from config.settings import CRAWL_SETTINGS, RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR

class BaseScraper:
    """Base scraper class with common functionality for all manufacturer scrapers"""
    
    def __init__(self, manufacturer_name: str, deepseek_api_key: str):
        self.manufacturer_name = manufacturer_name
        self.deepseek_api_key = deepseek_api_key
        self.session_id = f"{manufacturer_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize session tracking
        self.session = ScrapingSession(
            session_id=self.session_id,
            manufacturer=manufacturer_name
        )
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(f"scraper_{self.manufacturer_name}")
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = LOGS_DIR / f"{self.manufacturer_name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    async def scrape_url(self, url: str, extraction_prompt: str) -> ScrapingResult:
        """Scrape a single URL and extract arrow data"""
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting scrape of {url}")
            
            # Add random delay for respectful crawling
            delay = random.uniform(*CRAWL_SETTINGS["delay_range"])
            await asyncio.sleep(delay)
            
            async with AsyncWebCrawler(verbose=True) as crawler:
                # Configure LLM extraction strategy with proper LLMConfig
                from crawl4ai.async_configs import LLMConfig
                
                llm_config = LLMConfig(
                    provider="openai/deepseek-chat",
                    api_token=self.deepseek_api_key,
                    base_url="https://api.deepseek.com"
                )
                
                extraction_strategy = LLMExtractionStrategy(
                    llm_config=llm_config,
                    schema=self._get_extraction_schema(),
                    extraction_type="schema",
                    instruction=extraction_prompt,
                    force_json_response=True,
                    verbose=True
                )
                
                # Perform crawl
                result = await crawler.arun(
                    url=url,
                    extraction_strategy=extraction_strategy,
                    bypass_cache=True,
                    timeout=CRAWL_SETTINGS["timeout"]
                )
                
                if result.success:
                    # Process extracted data
                    processed_arrows = self._process_extracted_data(result.extracted_content, url)
                    
                    scraping_result = ScrapingResult(
                        success=True,
                        url=url,
                        arrows_found=len(processed_arrows),
                        processed_data=processed_arrows,
                        processing_time=time.time() - start_time
                    )
                    
                    self.logger.info(f"Successfully scraped {url} - Found {len(processed_arrows)} arrows")
                    
                else:
                    scraping_result = ScrapingResult(
                        success=False,
                        url=url,
                        errors=[f"Crawl failed: {result.error_message}"],
                        processing_time=time.time() - start_time
                    )
                    
                    self.logger.error(f"Failed to scrape {url}: {result.error_message}")
                
        except Exception as e:
            scraping_result = ScrapingResult(
                success=False,
                url=url,
                errors=[str(e)],
                processing_time=time.time() - start_time
            )
            
            self.logger.error(f"Exception while scraping {url}: {str(e)}")
        
        # Add to session
        self.session.results.append(scraping_result)
        self.session.urls_scraped.append(url)
        
        return scraping_result
    
    def _get_extraction_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for arrow data extraction with spine-specific specifications"""
        return {
            "type": "object",
            "properties": {
                "arrows": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "model_name": {"type": "string"},
                            "spine_specifications": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "spine": {"type": "integer"},
                                        "outer_diameter": {"type": "number"},
                                        "gpi_weight": {"type": "number"},
                                        "inner_diameter": {"type": ["number", "null"]},
                                        "length_options": {
                                            "type": "array",
                                            "items": {"type": "integer"}
                                        }
                                    },
                                    "required": ["spine", "outer_diameter", "gpi_weight"]
                                }
                            },
                            "material": {"type": "string"},
                            "arrow_type": {"type": "string"},
                            "price_range": {"type": "string"},
                            "recommended_use": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "description": {"type": "string"}
                        },
                        "required": ["model_name", "spine_specifications"]
                    }
                }
            },
            "required": ["arrows"]
        }
    
    def _process_extracted_data(self, extracted_data: Any, source_url: str) -> List[ArrowSpecification]:
        """Process extracted data into ArrowSpecification objects with spine-specific data"""
        arrows = []
        
        try:
            if isinstance(extracted_data, str):
                data = json.loads(extracted_data)
            else:
                data = extracted_data
            
            for arrow_data in data.get("arrows", []):
                try:
                    # Process spine specifications
                    spine_specs = []
                    for spine_data in arrow_data.get("spine_specifications", []):
                        try:
                            spine_spec = SpineSpecification(**spine_data)
                            spine_specs.append(spine_spec)
                        except Exception as e:
                            self.logger.warning(f"Failed to create SpineSpecification for {arrow_data.get('model_name', 'unknown')}: {e}")
                            continue
                    
                    if not spine_specs:
                        self.logger.warning(f"No valid spine specifications found for {arrow_data.get('model_name', 'unknown')}")
                        continue
                    
                    # Create arrow specification
                    arrow_spec_data = arrow_data.copy()
                    arrow_spec_data['spine_specifications'] = spine_specs
                    arrow_spec_data['manufacturer'] = self.manufacturer_name
                    arrow_spec_data['source_url'] = source_url
                    
                    arrow = ArrowSpecification(**arrow_spec_data)
                    arrows.append(arrow)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to create ArrowSpecification: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to process extracted data: {e}")
        
        return arrows
    
    async def scrape_multiple_urls(self, urls: List[str], extraction_prompt: str) -> List[ScrapingResult]:
        """Scrape multiple URLs with concurrency control"""
        self.logger.info(f"Starting batch scrape of {len(urls)} URLs")
        
        # Process URLs with limited concurrency
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                return await self.scrape_url(url, extraction_prompt)
        
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Exception for URL {urls[i]}: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    def save_session_data(self) -> None:
        """Save session data to files"""
        # Complete session
        self.session.completed_at = datetime.now()
        self.session.total_arrows_found = sum(r.arrows_found for r in self.session.results)
        
        # Save raw session data
        session_file = RAW_DATA_DIR / f"{self.session_id}_session.json"
        with open(session_file, 'w') as f:
            json.dump(self.session.model_dump(), f, indent=2, default=str)
        
        # Collect all arrows
        all_arrows = []
        for result in self.session.results:
            if result.processed_data:
                all_arrows.extend(result.processed_data)
        
        # Save processed arrow data
        if all_arrows:
            arrows_file = PROCESSED_DATA_DIR / f"{self.manufacturer_name}_arrows.json"
            arrows_data = {
                "manufacturer": self.manufacturer_name,
                "last_updated": datetime.now().isoformat(),
                "total_arrows": len(all_arrows),
                "total_spine_options": sum(len(arrow.spine_specifications) for arrow in all_arrows),
                "arrows": [arrow.model_dump() for arrow in all_arrows]
            }
            
            with open(arrows_file, 'w') as f:
                json.dump(arrows_data, f, indent=2, default=str)
        
        self.logger.info(f"Session data saved - Found {len(all_arrows)} total arrows")
    
    def get_extraction_prompt(self, manufacturer_specific_info: str = "") -> str:
        """Get the base extraction prompt for arrow specifications"""
        return f"""
        Extract arrow specifications from this webpage content. Look for the following information about arrows/shafts:

        Required Information:
        - Model/Product name
        - Spine options (stiffness values, usually numbers like 300, 340, 400, 500, etc.)
        - Diameter (in inches, like 0.246", 0.204", etc.)
        - GPI (grains per inch) weight

        Optional Information:
        - Available lengths (in inches)
        - Material composition (carbon fiber, aluminum, etc.)
        - Arrow type/category (hunting, target, 3D, etc.)
        - Price information
        - Recommended uses

        {manufacturer_specific_info}

        Return the data in the specified JSON schema format. If spine values are given as ranges or with additional text, extract just the numeric values. Be precise with measurements and only include data that is clearly stated on the page.
        """