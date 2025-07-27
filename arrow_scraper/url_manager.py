#!/usr/bin/env python3
"""
URL Management System for Arrow Scraper
Handles adding, validating, and organizing URLs in manufacturer configurations
"""

import requests
import yaml
import validators
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import time
from datetime import datetime
import re
from bs4 import BeautifulSoup

class URLManager:
    """Manages URL operations for manufacturer configurations"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.manufacturers_file = self.config_dir / "manufacturers.yaml"
        self.url_types = [
            'arrow', 'components', 'points', 'nocks', 'fletchings', 
            'inserts', 'accessories', 'strings', 'rests'
        ]
        
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """Validate URL format and accessibility"""
        try:
            # Basic format validation
            if not validators.url(url):
                return False, "Invalid URL format"
            
            # Check if URL is accessible
            print(f"🔍 Validating URL: {url}")
            response = requests.head(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                return True, "URL is valid and accessible"
            elif response.status_code == 404:
                return False, "URL not found (404)"
            elif response.status_code >= 400:
                return False, f"HTTP error: {response.status_code}"
            else:
                return True, f"URL accessible (status: {response.status_code})"
                
        except requests.exceptions.Timeout:
            return False, "URL validation timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection error - URL may be invalid"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def categorize_content(self, url: str) -> str:
        """Attempt to categorize URL content by analyzing the URL and page content"""
        try:
            # URL-based categorization
            url_lower = url.lower()
            
            # Check URL path for category indicators
            if any(word in url_lower for word in ['arrow', 'shaft', 'carbon', 'aluminum']):
                return 'arrow'
            elif any(word in url_lower for word in ['point', 'tip', 'broadhead', 'field-point']):
                return 'points'
            elif any(word in url_lower for word in ['nock', 'knock']):
                return 'nocks'
            elif any(word in url_lower for word in ['fletching', 'vane', 'feather']):
                return 'fletchings'
            elif any(word in url_lower for word in ['insert', 'outsert']):
                return 'inserts'
            elif any(word in url_lower for word in ['component', 'accessory', 'part']):
                return 'components'
            elif any(word in url_lower for word in ['string', 'cable']):
                return 'strings'
            elif any(word in url_lower for word in ['rest', 'sight', 'stabilizer']):
                return 'accessories'
            
            # If URL categorization fails, try content analysis
            return self._categorize_by_content(url)
            
        except Exception as e:
            print(f"⚠️  Categorization error: {e}")
            return 'unknown'
    
    def _categorize_by_content(self, url: str) -> str:
        """Categorize by analyzing page content"""
        try:
            print(f"🔍 Analyzing page content for categorization...")
            response = requests.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get page text for analysis
            page_text = soup.get_text().lower()
            
            # Content-based categorization
            arrow_keywords = ['spine', 'gpi', 'shaft', 'carbon arrow', 'aluminum arrow', 'diameter']
            point_keywords = ['grain', 'broadhead', 'field point', 'tip weight', 'thread']
            nock_keywords = ['nock size', 'nock fit', 'string groove', 'nock throat']
            fletching_keywords = ['vane', 'feather', 'fletching', 'wing', 'helical']
            
            arrow_count = sum(1 for keyword in arrow_keywords if keyword in page_text)
            point_count = sum(1 for keyword in point_keywords if keyword in page_text)
            nock_count = sum(1 for keyword in nock_keywords if keyword in page_text)
            fletching_count = sum(1 for keyword in fletching_keywords if keyword in page_text)
            
            # Return category with highest keyword count
            scores = {
                'arrow': arrow_count,
                'points': point_count, 
                'nocks': nock_count,
                'fletchings': fletching_count
            }
            
            max_category = max(scores, key=scores.get)
            if scores[max_category] > 0:
                print(f"   📊 Content analysis: {max_category} ({scores[max_category]} keywords)")
                return max_category
            else:
                return 'components'  # Default for unidentified content
                
        except Exception as e:
            print(f"   ⚠️  Content analysis failed: {e}")
            return 'components'
    
    def get_url_hash(self, url: str) -> str:
        """Generate hash for URL deduplication"""
        # Normalize URL for hashing
        parsed = urlparse(url)
        normalized = f"{parsed.netloc}{parsed.path}".lower().rstrip('/')
        return hashlib.sha256(normalized.encode()).hexdigest()[:12]
    
    def add_url(self, manufacturer: str, url_type: str, url: str, force: bool = False) -> bool:
        """Add URL to manufacturer configuration"""
        try:
            # Validate inputs
            if url_type not in self.url_types:
                print(f"❌ Invalid URL type: {url_type}")
                print(f"   Valid types: {', '.join(self.url_types)}")
                return False
            
            # Validate URL
            if not force:
                is_valid, message = self.validate_url(url)
                if not is_valid:
                    print(f"❌ URL validation failed: {message}")
                    return False
                print(f"✅ {message}")
            
            # Load current configuration
            config = self._load_config()
            
            # Find or create manufacturer
            manufacturer_key = self._find_manufacturer(config, manufacturer)
            if not manufacturer_key:
                print(f"❌ Manufacturer '{manufacturer}' not found in configuration")
                print(f"   Available manufacturers: {list(config['manufacturers'].keys())}")
                return False
            
            # Check for duplicates
            existing_urls = config['manufacturers'][manufacturer_key].get('product_urls', [])
            url_hash = self.get_url_hash(url)
            
            for existing_url in existing_urls:
                if self.get_url_hash(existing_url) == url_hash:
                    print(f"⚠️  URL already exists for {manufacturer_key}: {existing_url}")
                    return False
            
            # Add URL to configuration
            if 'product_urls' not in config['manufacturers'][manufacturer_key]:
                config['manufacturers'][manufacturer_key]['product_urls'] = []
            
            config['manufacturers'][manufacturer_key]['product_urls'].append(url)
            
            # Add metadata if it doesn't exist
            if 'url_metadata' not in config['manufacturers'][manufacturer_key]:
                config['manufacturers'][manufacturer_key]['url_metadata'] = {}
            
            config['manufacturers'][manufacturer_key]['url_metadata'][url] = {
                'type': url_type,
                'added_at': datetime.now().isoformat(),
                'hash': url_hash
            }
            
            # Save configuration
            self._save_config(config)
            
            print(f"✅ Added {url_type} URL to {manufacturer_key}")
            print(f"   URL: {url}")
            print(f"   Total URLs for {manufacturer_key}: {len(config['manufacturers'][manufacturer_key]['product_urls'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding URL: {e}")
            return False
    
    def _find_manufacturer(self, config: Dict, manufacturer_name: str) -> Optional[str]:
        """Find manufacturer key by partial name match"""
        manufacturer_lower = manufacturer_name.lower()
        
        # Exact match first
        for key in config['manufacturers'].keys():
            if key.lower() == manufacturer_lower:
                return key
        
        # Partial match
        for key in config['manufacturers'].keys():
            if manufacturer_lower in key.lower() or key.lower() in manufacturer_lower:
                return key
        
        return None
    
    def _load_config(self) -> Dict:
        """Load manufacturer configuration"""
        try:
            with open(self.manufacturers_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to load config: {e}")
    
    def _save_config(self, config: Dict):
        """Save manufacturer configuration"""
        try:
            # Create backup
            backup_file = self.manufacturers_file.with_suffix('.yaml.backup')
            if self.manufacturers_file.exists():
                self.manufacturers_file.rename(backup_file)
            
            # Save new configuration
            with open(self.manufacturers_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2, allow_unicode=True)
            
            print(f"💾 Configuration saved to {self.manufacturers_file}")
            
        except Exception as e:
            # Restore backup if save failed
            if backup_file.exists():
                backup_file.rename(self.manufacturers_file)
            raise ValueError(f"Failed to save config: {e}")
    
    def list_urls(self, manufacturer: str = None, url_type: str = None) -> Dict[str, Any]:
        """List URLs with optional filtering"""
        try:
            config = self._load_config()
            results = {}
            
            for mfr_name, mfr_config in config['manufacturers'].items():
                if manufacturer and manufacturer.lower() not in mfr_name.lower():
                    continue
                
                urls = mfr_config.get('product_urls', [])
                metadata = mfr_config.get('url_metadata', {})
                
                filtered_urls = []
                for url in urls:
                    url_meta = metadata.get(url, {})
                    url_type_meta = url_meta.get('type', 'unknown')
                    
                    if url_type and url_type != url_type_meta:
                        continue
                    
                    filtered_urls.append({
                        'url': url,
                        'type': url_type_meta,
                        'added_at': url_meta.get('added_at', 'unknown')
                    })
                
                if filtered_urls:
                    results[mfr_name] = {
                        'total_urls': len(urls),
                        'filtered_urls': filtered_urls,
                        'extraction_method': mfr_config.get('extraction_method', 'text'),
                        'language': mfr_config.get('language', 'english')
                    }
            
            return results
            
        except Exception as e:
            print(f"❌ Error listing URLs: {e}")
            return {}
    
    def remove_url(self, manufacturer: str, url: str) -> bool:
        """Remove URL from manufacturer configuration"""
        try:
            config = self._load_config()
            manufacturer_key = self._find_manufacturer(config, manufacturer)
            
            if not manufacturer_key:
                print(f"❌ Manufacturer '{manufacturer}' not found")
                return False
            
            urls = config['manufacturers'][manufacturer_key].get('product_urls', [])
            
            # Find and remove URL
            url_hash = self.get_url_hash(url)
            removed_url = None
            
            for existing_url in urls:
                if self.get_url_hash(existing_url) == url_hash or existing_url == url:
                    urls.remove(existing_url)
                    removed_url = existing_url
                    break
            
            if not removed_url:
                print(f"❌ URL not found for {manufacturer_key}")
                return False
            
            # Remove metadata
            metadata = config['manufacturers'][manufacturer_key].get('url_metadata', {})
            if removed_url in metadata:
                del metadata[removed_url]
            
            # Save configuration
            self._save_config(config)
            
            print(f"✅ Removed URL from {manufacturer_key}: {removed_url}")
            return True
            
        except Exception as e:
            print(f"❌ Error removing URL: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="URL Manager for Arrow Scraper")
    parser.add_argument('--add', action='store_true', help='Add URL to manufacturer')
    parser.add_argument('--list', action='store_true', help='List URLs')
    parser.add_argument('--remove', action='store_true', help='Remove URL from manufacturer')
    parser.add_argument('--manufacturer', help='Manufacturer name')
    parser.add_argument('--type', help='URL type (arrow, components, etc.)')
    parser.add_argument('--url', help='URL to add/remove')
    parser.add_argument('--force', action='store_true', help='Skip URL validation')
    
    args = parser.parse_args()
    
    manager = URLManager()
    
    if args.add:
        if not all([args.manufacturer, args.type, args.url]):
            print("❌ --add requires --manufacturer, --type, and --url")
        else:
            manager.add_url(args.manufacturer, args.type, args.url, args.force)
    
    elif args.remove:
        if not all([args.manufacturer, args.url]):
            print("❌ --remove requires --manufacturer and --url")
        else:
            manager.remove_url(args.manufacturer, args.url)
    
    elif args.list:
        results = manager.list_urls(args.manufacturer, args.type)
        
        print("📋 URL Configuration:")
        print("=" * 60)
        
        for mfr_name, mfr_data in results.items():
            print(f"\n🏭 {mfr_name}")
            print(f"   Language: {mfr_data['language']}")
            print(f"   Method: {mfr_data['extraction_method']}")
            print(f"   Total URLs: {mfr_data['total_urls']}")
            
            for url_data in mfr_data['filtered_urls']:
                print(f"   • [{url_data['type']}] {url_data['url']}")
                print(f"     Added: {url_data['added_at']}")
    
    else:
        print("❌ Please specify --add, --remove, or --list")
        print("Examples:")
        print("  python url_manager.py --add --manufacturer=easton --type=arrow --url=http://example.com")
        print("  python url_manager.py --list --manufacturer=easton")
        print("  python url_manager.py --remove --manufacturer=easton --url=http://example.com")