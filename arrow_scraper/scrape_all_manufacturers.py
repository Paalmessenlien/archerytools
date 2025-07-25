#!/usr/bin/env python3
"""
Comprehensive Arrow Data Extraction from All Manufacturers
Extract arrow specifications from all manufacturers documented in phase1-scraping.md
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler
from scrapers.base_scraper import BaseScraper
from models import ArrowSpecification, SpineSpecification, ManufacturerData, ScrapingSession, ScrapingResult
from dotenv import load_dotenv

class ComprehensiveArrowScraper:
    """Scraper for all manufacturers in the phase documentation using updated spine-specific model"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session_id = f"all_manufacturers_{int(time.time())}"
        self.session_data = ScrapingSession(
            session_id=self.session_id,
            manufacturer="ALL_PHASE_MANUFACTURERS"
        )
        
        # Define all manufacturers and their URLs from phase documentation
        self.manufacturers = {
           "Easton Archery": {
                "base_url": "https://eastonarchery.com/",
                "product_urls": [
                    # X10 Series
                    "https://eastonarchery.com/arrows_/x10-parallel-pro/",
                    "https://eastonarchery.com/arrows_/x10/",
                    "https://eastonarchery.com/arrows_/x10-protour/",
                    
                    # Superdrive Series
                    "https://eastonarchery.com/arrows_/superdrive-micro/",
                    "https://eastonarchery.com/arrows_/superdrive-23/",
                    "https://eastonarchery.com/arrows_/superdrive-25/",
                    "https://eastonarchery.com/arrows_/superdrive-27/",
                    
                    # Vector Series
                    "https://eastonarchery.com/arrows_/vector-ready-to-shoot/",
                    "https://eastonarchery.com/arrows_/vector-arrow/",
                    
                    # Venture Series
                    "https://eastonarchery.com/arrows_/venture/",
                    
                    # RX7 Series
                    "https://eastonarchery.com/arrows_/rx7-the-ultimate-indoor-recurve-arrow-shaft/",
                    
                    # X Series
                    "https://eastonarchery.com/arrows_/legendary-x23/",
                    "https://eastonarchery.com/arrows_/x27/",
                    "https://eastonarchery.com/arrows_/x7-eclipse/",
                    
                    # A/C/E Series
                    "https://eastonarchery.com/arrows_/a-c-e/",
                    
                    # Avance Series
                    "https://eastonarchery.com/arrows_/avance-avance-sport/",
                    
                    # XX75 Series
                    "https://eastonarchery.com/arrows_/xx75-platinum-plus/",
                    "https://eastonarchery.com/arrows_/xx75-jazz/",
                    "https://eastonarchery.com/arrows_/xx75-genesis/"
                ]
            },
            "Gold Tip": {
                "base_url": "https://www.goldtip.com/",
                "product_urls": [
                    # Hunter Series
                    "https://www.goldtip.com/hunting-arrows/hunter-series/hunter-hunting-arrows/P01268.html",
                    "https://www.goldtip.com/hunting-arrows/hunter-series/hunter-pro-hunting-arrows/P01271.html",
                    
                    # Specialty Series
                    "https://www.goldtip.com/hunting-arrows/specialty-series/ted-nugent-hunting-arrows/P01279.html",
                    "https://www.goldtip.com/hunting-arrows/specialty-series/twister-flu-flu-hunting-arrow/P01283.html",
                    
                    # Airstrike Series
                    "https://www.goldtip.com/hunting-arrows/airstrike-series/airstrike-hunting-arrows/PG3398796.html",
                    
                    # Kinetic Series
                    "https://www.goldtip.com/hunting-arrows/kinetic-series/kinetic-kaos-hunting-arrows/P01276.html",
                    "https://www.goldtip.com/hunting-arrows/kinetic-series/kinetic-hunting-arrows/P01275.html",
                    
                    # Force F.O.C. Series
                    "https://www.goldtip.com/hunting-arrows/force-foc-high-front-of-center/force-f.o.c.-hunting-arrows/PG3398798.html",
                    
                    # Pierce Series
                    "https://www.goldtip.com/hunting-arrows/pierce-platinum-hunting-arrows/PG4342808.html",
                    "https://www.goldtip.com/hunting-arrows/pierce-hunting-arrows/PG4392856.html",
                    "https://www.goldtip.com/hunting-arrows/pierce-lrt-hunting-arrows/PG3997784.html",
                    
                    # Velocity Series
                    "https://www.goldtip.com/hunting-arrows/velocity-series/velocity-xt-hunting-arrows/P01286.html",
                    "https://www.goldtip.com/hunting-arrows/velocity-series/velocity-hunting-arrows/P01284.html",
                    "https://www.goldtip.com/hunting-arrows/velocity-series/velocity-pro-hunting-arrows/P01285.html",
                    
                    # Traditional Series
                    "https://www.goldtip.com/hunting-arrows/traditional-series/traditional-hunting-arrows/P01281.html",
                    "https://www.goldtip.com/hunting-arrows/traditional-series/traditional-classic-hunting-arrows/P01368.html",
                    "https://www.goldtip.com/hunting-arrows/traditional-series/traditional-xt-hunting-arrows/P01282.html",
                    "https://www.goldtip.com/hunting-arrows/traditional-series/traditional-classic-xt-hunting-arrows/P01369.html",
                    
                    # Black Label Series
                    "https://www.goldtip.com/hunting-arrows/black-label-series/black-label-quantum-hunting-arrows/PG3398799.html",
                    "https://www.goldtip.com/hunting-arrows/black-label-series/black-label-hunting-arrows/PG3398797.html",
                    
                    # X-Cutter Target Series
                    "https://www.goldtip.com/target-arrows/x-cutter-series/x-cutter-pro-target-arrows/GT-XCPROSN.html",
                    "https://www.goldtip.com/target-arrows/x-cutter-series/x-cutter-plus-target-arrows/GT-XCSPLUS.html",
                    
                    # Pierce Target Series
                    "https://www.goldtip.com/target-arrows/pierce-series/kinetic-pierce-tour-target-arrows/PG3399578.html",
                    
                    # 22 Target Series
                    "https://www.goldtip.com/target-arrows/22-series/22-series-pro-target-arrows/GT-22PROSN.html",
                    "https://www.goldtip.com/target-arrows/22-series/22-series-plus-target-arrows/GT-22SPLUS.html",
                    
                    # Triple X Target Series
                    "https://www.goldtip.com/target-arrows/triple-x-series/triple-x-pro-target-arrows/GT-TXPROSN.html",
                    "https://www.goldtip.com/target-arrows/triple-x-series/triple-x--plus-target-arrows/GT-TXSPLUS.html",
                    
                    # Nine.3 Target Series
                    "https://www.goldtip.com/target-arrows/nine.3-series/nine.3-max-pro-target-arrows/GT-93MAXPROSN.html",
                    "https://www.goldtip.com/target-arrows/nine.3-series/nine.3-max-plus-target-arrows/GT-93MAXSPLUS.html",
                    
                    # 30X Target Series
                    "https://www.goldtip.com/target-arrows/30x-series/30x-plus-target-arrows/GT-30XSPLUS.html",
                    "https://www.goldtip.com/target-arrows/30x-series/30x-pro-target-arrows/GT-30XPROSN.html"
                ]
            },
            "Victory Archery": {
                "base_url": "https://victoryarchery.com/",
                "product_urls": [
                    # VAP Series
                    "https://victoryarchery.com/arrows-hunting/vap-ss/",
                    "https://victoryarchery.com/arrows-hunting/vap-tko/",
                    "https://www.victoryarchery.com/arrows-hunting/vap/",
                    
                    # RIP Series
                    "https://www.victoryarchery.com/arrows-hunting/rip-ss/",
                    "https://victoryarchery.com/rip-tko/",
                    "https://www.victoryarchery.com/arrows-hunting/rip-xv/",
                    "https://www.victoryarchery.com/arrows-hunting/rip/",
                    
                    # VF Series
                    "https://www.victoryarchery.com/arrows-hunting/vf-tko/",
                    
                    # HLR Series
                    "https://www.victoryarchery.com/arrows-hunting/hlr/",
                    
                    # VForce Series
                    "https://www.victoryarchery.com/arrows-hunting/vforce/",
                    
                    # Traditional Series
                    "https://www.victoryarchery.com/arrows-hunting/bamboo-trad/",
                    
                    # V-Tac Target Series
                    "https://victoryarchery.com/v-tac23/",
                    "https://victoryarchery.com/arrows-target/v-tac25/",
                    "https://victoryarchery.com/arrows-target/v-tac27/",
                    
                    # VXT Target Series
                    "https://victoryarchery.com/arrows-target/vxt/",
                    
                    # VAP Target Series
                    "https://victoryarchery.com/arrows-target/vap/",
                    
                    # 3DHV Target Series
                    "https://victoryarchery.com/arrows-target/3dhv/",
                    
                    # VFT Target Series
                    "https://www.victoryarchery.com/arrows-target/vft/"
                ]
            },
            "Skylon Archery": {
                "base_url": "https://www.skylonarchery.com/",
                "product_urls": [
                    # ID 3.2 Series
                    "https://www.skylonarchery.com/arrows/id-3-2/performa",
                    "https://www.skylonarchery.com/arrows/id-3-2/precium",
                    "https://www.skylonarchery.com/arrows/id-3-2/paragon",
                    "https://www.skylonarchery.com/arrows/id-3-2/preminens",
                    # ID 4.2 Series
                    "https://www.skylonarchery.com/arrows/2023-06-29-08-52-09/novice",
                    "https://www.skylonarchery.com/arrows/2023-06-29-08-52-09/radius",
                    "https://www.skylonarchery.com/arrows/2023-06-29-08-52-09/brixxon",
                    # ID 5.2 Series
                    "https://www.skylonarchery.com/arrows/id-5-2/instec",
                    "https://www.skylonarchery.com/arrows/id-5-2/quantic",
                    "https://www.skylonarchery.com/arrows/id-5-2/ebony",
                    "https://www.skylonarchery.com/arrows/id-5-2/backbone",
                    # ID 6.2 Series
                    "https://www.skylonarchery.com/arrows/id-6-2/fast-wing",
                    "https://www.skylonarchery.com/arrows/id-6-2/savage",
                    "https://www.skylonarchery.com/arrows/id-6-2/edge",
                    "https://www.skylonarchery.com/arrows/id-6-2/maverick",
                    "https://www.skylonarchery.com/arrows/id-6-2/rove",
                    "https://www.skylonarchery.com/arrows/id-6-2/phoric",
                    "https://www.skylonarchery.com/arrows/id-6-2/frontier",
                    "https://www.skylonarchery.com/arrows/id-6-2/bentwood",
                    # ID 8.0 Series
                    "https://www.skylonarchery.com/arrows/id-8-0/bruxx",
                    "https://www.skylonarchery.com/arrows/id-8-0/empros"
                ]
            },
            "Nijora Archery": {
                "base_url": "https://nijora.com/",
                "product_urls": [
                    "https://nijora.com/product/songan/",
                    "https://nijora.com/product/3d-fly/",
                    "https://nijora.com/product/nigan-pro/",
                    "https://nijora.com/product/ilyan-pro-1000-350/",
                    "https://nijora.com/product/payat/",
                    "https://nijora.com/product/3k-pro/",
                    "https://nijora.com/product/tokala/",
                    "https://nijora.com/product/tokala-m/",
                    "https://nijora.com/product/tokala-long-36-inch/",
                    "https://nijora.com/product/nijora-yona/",
                    "https://nijora.com/product/oxx-pro/",
                    "https://nijora.com/product/taperon/",
                    "https://nijora.com/product/taperon-crust/",
                    "https://nijora.com/product/taperon-crust-600-turned-white/",
                    "https://nijora.com/product/bark/",
                    "https://nijora.com/product/bark-m/",
                    "https://nijora.com/product/bark-pro/",
                    "https://nijora.com/product/bark-heavy/",
                    "https://nijora.com/product/elsu-golden-edition/",
                    "https://nijora.com/product/elsu-pro/",
                    "https://nijora.com/product/zitkala/",
                    "https://nijora.com/product/nijora-linawa/",
                    "https://nijora.com/product/big-9-9-2/",
                    "https://nijora.com/product/mammut-schaft-39-inch/",
                    "https://nijora.com/product/onawa-fly/",
                    "https://nijora.com/product/onawa-pro/",
                    "https://nijora.com/product/onawa-pro-x/",
                    "https://nijora.com/product/onawa-pro-xt-3-2/",
                    "https://nijora.com/product/onawa-pro-xt-40/",
                    "https://nijora.com/product/taperon-sx/",
                    "https://nijora.com/product/bark-small/",
                    "https://nijora.com/product/nijora-taperon-330-hunter/",
                    "https://nijora.com/product/nijora-taperon-3k-400-orange-hunter/",
                    "https://nijora.com/product/taperon-orange/",
                    "https://nijora.com/product/junior-black-1800/",
                    "https://nijora.com/product/junior-1500-black-pink-yellow-orange/",
                    "https://nijora.com/product/junior-carbonschaft-optionale-komponenten/",
                    "https://nijora.com/product/hakan/",
                    "https://nijora.com/product/color-line/",
                    "https://nijora.com/product/nijora-3d-fun/",
                    "https://nijora.com/product/nijora-3d-fun-neon-gelb-small-800-1200/",
                    "https://nijora.com/product/nijora-orange/",
                    "https://nijora.com/product/nijora-orange-small-800-1200/",
                    "https://nijora.com/product/nijora-3d-red-spider/",
                    "https://nijora.com/product/nijora-3d-red-spider-small/",
                    "https://nijora.com/product/nijora-3d-blue/",
                    "https://nijora.com/product/nijora-3d-blue-small-1000/",
                    "https://nijora.com/product/nijora-3d-green/",
                    "https://nijora.com/product/nijora-3d-green-small-1000/",
                    "https://nijora.com/product/nijora-pink/",
                    "https://nijora.com/product/nijora-pink-1000-1200/",
                    "https://nijora.com/product/cyan-color-line-spine-1200-1000/",
                    "https://nijora.com/product/nijora-3d-white-rose/",
                    "https://nijora.com/product/nijora-3d-white-rose-small-1000/",
                    "https://nijora.com/product/tokala-long-white-rose/",
                    "https://nijora.com/product/nijora-grey-panther-500-800/",
                    "https://nijora.com/product/mammut-atlatl-78-inch-fertigpfeil/"
                ]
            },
            "DK Bow": {
                "base_url": "https://dkbow.de/",
                "product_urls": [
                    "https://dkbow.de/DK-Panther-Carbon-Arrow-ID-6.2/SW10007",
                    "https://dkbow.de/DK-Cougar-Carbon-Arrow-ID-4.2/36721",
                    "https://dkbow.de/DK-Tyrfing-Carbon-Arrow-ID-5.2/418",
                    "https://dkbow.de/DK-Gungnir-Carbon-Arrow-ID-4.2/SW10006"
                ]
            },
            "Pandarus Archery": {
                "base_url": "https://www.pandarusarchery.com/",
                "product_urls": [
                    # Target Arrows
                    "https://www.pandarusarchery.com/elite_ca320",
                    "https://www.pandarusarchery.com/elite-xt",
                    "https://www.pandarusarchery.com/elite-ca320-pro",
                    "https://www.pandarusarchery.com/elite-ca390",
                    "https://www.pandarusarchery.com/ice-pointee77bb06",
                    "https://www.pandarusarchery.com/champion",
                    "https://www.pandarusarchery.com/infinity4d2a3aac",
                    "https://www.pandarusarchery.com/precision",
                    "https://www.pandarusarchery.com/alpha-xt",
                    "https://www.pandarusarchery.com/versus",
                    # Hunting Arrows
                    "https://www.pandarusarchery.com/alpha-x"
                ]
            },
            "BigArchery": {
                "base_url": "https://www.bigarchery.com/gb/",
                "product_urls": [
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/282-706-cross-x-shaft-ambitionpoint.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/283-716-cross-x-shaft-helios.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/284-722-cross-x-shaft-ares-hu.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/285-797-cross-x-shaft-gladiator.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/286-724-cross-x-shaft-maior-cube.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/287-731-cross-x-shaft-plurima.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/288-742-cross-x-shaft-ambition-se-point.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/289-752-cross-x-shaft-madera.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/290-755-cross-x-shaft-plurima-cube.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/291-765-cross-x-shaft-exentia.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/292-cross-x-shaft-xxiii-350.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/293-775-cross-x-shaft-hurricane-cube.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/295-782-cross-x-shaft-hurricane-octagon.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/296-788-cross-x-shaft-maior-penta.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/297-791-cross-x-shaft-maior-octagon.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/298-800-cross-x-shaft-ambition-gold-ed.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/299-810-cross-x-shaft-fulmen.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/300-814-cross-x-shaft-madera-light.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/301-818-cross-x-shaft-avatar-penta.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/302-824-cross-x-shaft-avatar-cresting.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/303-cross-x-shaft-xxiii-octagon-350.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/304-828-cross-x-shaft-avatar-cube.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/305-834-cross-x-shaft-pegasus-cube.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/306-840-cross-x-shaft-pegasus-penta.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/307-846-cross-x-shaft-pegasus-octagon.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/308-870-cross-x-shaft-fulmen-octagon.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/309-877-cross-x-shaft-pegasus-cubecrest.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/310-881-cross-x-shaft-centurion.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/311-884-cross-x-shaft-exentia-test-pack.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/312-894-cross-x-shaft-raptor.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/313-900-cross-x-shaft-phoenix.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/314-905-cross-x-shaft-iridium.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/1471-3444-cross-x-shaft-fulmen-xxl.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/1640-4110-cross-x-shaft-avatar-octagon.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/1671-4076-cross-x-shaft-fulmen-xxl-penta.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/1734-4286-cross-x-shaft-pegasus.html",
                    "https://www.bigarchery.com/gb/shafts_304_274_BC9/1735-4294-cross-x-shaft-fulmen-xl.html"
                ]
            },
            "Carbon Express": {
                "base_url": "https://www.feradyne.com/",
                "product_urls": [
                    "https://www.feradyne.com/product/maxima-sable-rz/",
                    "https://www.feradyne.com/product/maxima-sable-rz-select/",
                    "https://www.feradyne.com/product/maxima-photon-sd/",
                    "https://www.feradyne.com/product/maxima-triad/",
                    "https://www.feradyne.com/product/d-stroyer/",
                    "https://www.feradyne.com/product/d-stroyer-mx-hunter/",
                    "https://www.feradyne.com/product/cx-adrenaline/",
                    "https://www.feradyne.com/product/thunder-express/",
                    "https://www.feradyne.com/product/flu-flu-arrows/"
                ]
            }
        }
    
    async def discover_product_links(self, crawler: AsyncWebCrawler, category_url: str, manufacturer: str) -> List[str]:
        """Discover product links from category pages"""
        try:
            result = await crawler.arun(url=category_url, bypass_cache=True)
            if not result.success:
                return []
            
            content = result.markdown or result.html or ""
            
            # Use simple link extraction patterns
            import re
            
            # Common arrow product link patterns
            patterns = [
                r'href=["\']([^"\']*arrow[^"\']*)["\']',
                r'href=["\']([^"\']*product[^"\']*)["\']',
                r'href=["\']([^"\']*shaft[^"\']*)["\']',
                r'href=["\']([^"\']*/arrows[^"\']*)["\']'
            ]
            
            links = set()
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, str) and len(match) > 10:
                        # Filter out navigation, cart, etc.
                        if not any(skip in match.lower() for skip in ['cart', 'login', 'menu', 'nav', 'search', 'category']):
                            # Make absolute URL
                            if match.startswith('/'):
                                base = self.manufacturers[manufacturer]["base_url"].rstrip('/')
                                full_url = base + match
                            elif match.startswith('http'):
                                full_url = match
                            else:
                                continue
                            
                            links.add(full_url)
            
            return list(links)[:20]  # Limit to 20 links per category
            
        except Exception as e:
            print(f"❌ Error discovering links from {category_url}: {e}")
            return []
    
    async def scrape_manufacturer(self, crawler: AsyncWebCrawler, manufacturer: str, config: Dict[str, Any]) -> ManufacturerData:
        """Scrape all arrows from a single manufacturer"""
        
        print(f"\n🏭 SCRAPING MANUFACTURER: {manufacturer.upper()}")
        print("=" * 60)
        
        all_arrows = []
        urls_to_scrape = []
        
        # Get URLs to scrape
        if "product_urls" in config:
            # Direct product URLs
            urls_to_scrape = config["product_urls"]
            print(f"📋 Processing {len(urls_to_scrape)} direct product URLs")
        elif "category_urls" in config:
            # Discover product URLs from categories
            print(f"🔍 Discovering product URLs from {len(config['category_urls'])} categories")
            for category_url in config["category_urls"]:
                discovered_links = await self.discover_product_links(crawler, category_url, manufacturer)
                urls_to_scrape.extend(discovered_links)
                print(f"   Found {len(discovered_links)} links from {category_url}")
            
            # Remove duplicates
            urls_to_scrape = list(set(urls_to_scrape))
            print(f"📊 Total unique product URLs: {len(urls_to_scrape)}")
        
        # Scrape each URL
        successful_extractions = 0
        for i, url in enumerate(urls_to_scrape, 1):
            print(f"\n🔗 [{i}/{len(urls_to_scrape)}] {url}")
            
            try:
                # Extract arrow specifications using dedicated scraper (includes crawling)
                scraper = BaseScraper(manufacturer, self.api_key)
                extraction_prompt = scraper.get_extraction_prompt(
                    f"For {manufacturer} arrows, pay special attention to spine-specific specifications."
                )
                
                # Use the scraper to extract arrows with LLM
                arrows = []
                print(f"   🔍 Extracting with LLM...")
                
                extraction_result = await scraper.scrape_url(url, extraction_prompt)
                
                if extraction_result.success:
                    print(f"   ✓ Crawl and extraction successful")
                    
                    if extraction_result.processed_data and len(extraction_result.processed_data) > 0:
                        arrows = extraction_result.processed_data
                        print(f"      ✅ Found {len(arrows)} arrows with LLM extraction")
                    else:
                        print(f"      ⚠️  LLM extraction returned no arrow data")
                else:
                    print(f"   ❌ Extraction failed: {extraction_result.errors}")
                
                # Process results
                if arrows:
                    print(f"   🎉 Successfully extracted {len(arrows)} arrows!")
                    for j, arrow in enumerate(arrows, 1):
                        spine_options = arrow.get_spine_options()
                        spine_count = len(arrow.spine_specifications)
                        print(f"      {j}. {arrow.model_name} - {spine_count} spine specs: {spine_options}")
                    all_arrows.extend(arrows)
                    successful_extractions += 1
                else:
                    print(f"   ⚠️  No arrows extracted from this URL")
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        # Create manufacturer data
        manufacturer_data = ManufacturerData(
            manufacturer=manufacturer,
            arrows=all_arrows
        )
        
        print(f"\n📊 {manufacturer.upper()} SUMMARY:")
        print(f"   URLs processed: {len(urls_to_scrape)}")
        print(f"   Successful extractions: {successful_extractions}")
        print(f"   Total arrows found: {len(all_arrows)}")
        print(f"   Success rate: {(successful_extractions/len(urls_to_scrape)*100):.1f}%" if urls_to_scrape else "N/A")
        
        return manufacturer_data
    
    async def scrape_all_manufacturers(self) -> Dict[str, ManufacturerData]:
        """Scrape all manufacturers from phase documentation"""
        
        print("COMPREHENSIVE ARROW EXTRACTION")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Manufacturers to process: {len(self.manufacturers)}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_manufacturer_data = {}
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            for manufacturer, config in self.manufacturers.items():
                try:
                    manufacturer_data = await self.scrape_manufacturer(crawler, manufacturer, config)
                    all_manufacturer_data[manufacturer] = manufacturer_data
                    
                    # Add delay between manufacturers
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"❌ Failed to scrape {manufacturer}: {e}")
                    continue
        
        return all_manufacturer_data
    
    def save_results(self, all_data: Dict[str, ManufacturerData]):
        """Save comprehensive results to files"""
        
        # Create output directory
        output_dir = Path(__file__).parent / "data" / "comprehensive_extraction"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        total_arrows = 0
        total_manufacturers = len(all_data)
        
        # Save individual manufacturer files
        for manufacturer, data in all_data.items():
            manufacturer_file = output_dir / f"{manufacturer.lower().replace(' ', '_')}_arrows.json"
            
            manufacturer_export = {
                "manufacturer": manufacturer,
                "extraction_date": datetime.now().isoformat(),
                "total_arrows": len(data.arrows),
                "total_spine_options": sum(len(arrow.spine_specifications) for arrow in data.arrows),
                "arrows": [
                    {
                        "model_name": arrow.model_name,
                        "spine_specifications": [
                            {
                                "spine": spec.spine,
                                "outer_diameter": spec.outer_diameter,
                                "gpi_weight": spec.gpi_weight,
                                "inner_diameter": spec.inner_diameter,
                                "length_options": spec.length_options
                            }
                            for spec in arrow.spine_specifications
                        ],
                        "material": arrow.material,
                        "arrow_type": str(arrow.arrow_type) if arrow.arrow_type else None,
                        "recommended_use": arrow.recommended_use,
                        "description": arrow.description,
                        "source_url": arrow.source_url,
                        "scraped_at": arrow.scraped_at.isoformat(),
                        "diameter_range": {
                            "min": arrow.get_diameter_range()[0],
                            "max": arrow.get_diameter_range()[1]
                        },
                        "gpi_range": {
                            "min": arrow.get_gpi_range()[0],
                            "max": arrow.get_gpi_range()[1]
                        },
                        "spine_options": arrow.get_spine_options()
                    }
                    for arrow in data.arrows
                ]
            }
            
            with open(manufacturer_file, 'w') as f:
                json.dump(manufacturer_export, f, indent=2, default=str)
            
            print(f"💾 {manufacturer}: {len(data.arrows)} arrows saved to {manufacturer_file.name}")
            total_arrows += len(data.arrows)
        
        # Save comprehensive summary
        summary_file = output_dir / "comprehensive_summary.json"
        
        summary_data = {
            "extraction_session": {
                "session_id": self.session_id,
                "extraction_date": datetime.now().isoformat(),
                "total_manufacturers": total_manufacturers,
                "total_arrows_extracted": total_arrows
            },
            "manufacturer_summaries": {
                manufacturer: {
                    "arrows_found": len(data.arrows),
                    "unique_models": len(set(arrow.model_name for arrow in data.arrows)),
                    "spine_range": {
                        "min": min((min(arrow.get_spine_options()) for arrow in data.arrows), default=0),
                        "max": max((max(arrow.get_spine_options()) for arrow in data.arrows), default=0)
                    },
                    "diameter_range": {
                        "min": min((arrow.get_diameter_range()[0] for arrow in data.arrows), default=0),
                        "max": max((arrow.get_diameter_range()[1] for arrow in data.arrows), default=0)
                    },
                    "total_spine_options": sum(len(arrow.spine_specifications) for arrow in data.arrows)
                }
                for manufacturer, data in all_data.items()
            },
            "extraction_statistics": {
                "total_urls_attempted": sum(len(config.get("product_urls", config.get("category_urls", []))) for config in self.manufacturers.values()),
                "successful_extractions": total_arrows,
                "manufacturers_processed": len([m for m, d in all_data.items() if len(d.arrows) > 0])
            }
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2, default=str)
        
        print(f"\n📋 COMPREHENSIVE SUMMARY saved to {summary_file.name}")
        
        return summary_data

async def main():
    """Main execution function"""
    
    # Load environment variables
    load_dotenv()
    
    # Check for DeepSeek API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY environment variable not found")
        print("Please create a .env file with your DeepSeek API key:")
        print("DEEPSEEK_API_KEY='your_api_key_here'")
        return
    
    print("🚀 Starting comprehensive arrow extraction from ALL manufacturers...")
    
    # Create scraper and run extraction
    scraper = ComprehensiveArrowScraper(api_key)
    all_data = await scraper.scrape_all_manufacturers()
    
    # Save results
    summary = scraper.save_results(all_data)
    
    # Final report
    print("\n" + "=" * 60)
    print("🎉 COMPREHENSIVE EXTRACTION COMPLETE!")
    print("=" * 60)
    print(f"✅ Manufacturers processed: {summary['extraction_statistics']['manufacturers_processed']}")
    print(f"✅ Total arrows extracted: {summary['extraction_statistics']['successful_extractions']}")
    print(f"✅ URLs attempted: {summary['extraction_statistics']['total_urls_attempted']}")
    
    print(f"\n📊 MANUFACTURER BREAKDOWN:")
    for manufacturer, stats in summary['manufacturer_summaries'].items():
        if stats['arrows_found'] > 0:
            print(f"   {manufacturer}: {stats['arrows_found']} arrows, {stats['unique_models']} models")
    
    print(f"\n💾 All data saved to: data/comprehensive_extraction/")
    print(f"🎯 Phase 1 (Data Scraping & Collection) COMPLETE!")

if __name__ == "__main__":
    asyncio.run(main())