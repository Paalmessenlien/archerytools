#!/usr/bin/env python3
"""
Configuration loader for arrow scraper
Loads manufacturer URLs and settings from YAML config files
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class ConfigLoader:
    """Loads and manages scraper configuration"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.manufacturers_config = None
        self.settings = None
        self.load_config()
    
    def load_config(self):
        """Load configuration from YAML files"""
        manufacturers_file = self.config_dir / "manufacturers.yaml"
        
        if not manufacturers_file.exists():
            raise FileNotFoundError(f"Manufacturers config not found: {manufacturers_file}")
        
        try:
            with open(manufacturers_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            self.manufacturers_config = config.get('manufacturers', {})
            self.settings = config.get('settings', {})
            
            print(f"✅ Loaded config for {len(self.manufacturers_config)} manufacturers")
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading config: {e}")
    
    def get_manufacturers(self) -> Dict[str, Dict]:
        """Get all manufacturer configurations"""
        return self.manufacturers_config.copy()
    
    def get_manufacturer(self, name: str) -> Optional[Dict]:
        """Get configuration for a specific manufacturer"""
        return self.manufacturers_config.get(name)
    
    def get_manufacturer_urls(self, name: str) -> List[str]:
        """Get product URLs for a specific manufacturer"""
        manufacturer = self.get_manufacturer(name)
        if manufacturer:
            return manufacturer.get('product_urls', [])
        return []
    
    def get_manufacturer_names(self) -> List[str]:
        """Get list of all manufacturer names"""
        return list(self.manufacturers_config.keys())
    
    def get_settings(self) -> Dict:
        """Get global settings"""
        return self.settings.copy()
    
    def get_setting(self, key: str, default=None):
        """Get a specific setting value"""
        return self.settings.get(key, default)
    
    def find_manufacturer_by_partial_name(self, partial_name: str) -> Optional[str]:
        """Find manufacturer by partial name match (case insensitive)"""
        partial_lower = partial_name.lower()
        
        for name in self.manufacturers_config.keys():
            if partial_lower in name.lower():
                return name
        
        return None
    
    def get_extraction_method(self, manufacturer_name: str) -> str:
        """Get extraction method for manufacturer (text, vision, etc.)"""
        manufacturer = self.get_manufacturer(manufacturer_name)
        if manufacturer:
            return manufacturer.get('extraction_method', 'text')
        return 'text'
    
    def is_vision_extraction(self, manufacturer_name: str) -> bool:
        """Check if manufacturer uses vision-based extraction"""
        return self.get_extraction_method(manufacturer_name) == 'vision'
    
    def get_manufacturer_language(self, manufacturer_name: str) -> str:
        """Get language for manufacturer (for specialized extraction)"""
        manufacturer = self.get_manufacturer(manufacturer_name)
        if manufacturer:
            return manufacturer.get('language', 'english')
        return 'english'
    
    def export_to_legacy_format(self) -> Dict:
        """Export config to legacy format for backward compatibility"""
        legacy_format = {}
        
        for name, config in self.manufacturers_config.items():
            legacy_format[name] = {
                "base_url": config.get('base_url', ''),
                "product_urls": config.get('product_urls', [])
            }
        
        return legacy_format
    
    def save_config(self, filepath: Optional[str] = None):
        """Save current config to file"""
        if filepath is None:
            filepath = self.config_dir / "manufacturers.yaml"
        
        config_data = {
            'manufacturers': self.manufacturers_config,
            'settings': self.settings
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
        
        print(f"✅ Config saved to {filepath}")
    
    def add_manufacturer(self, name: str, base_url: str, product_urls: List[str], 
                        extraction_method: str = "text", **kwargs):
        """Add a new manufacturer to the config"""
        self.manufacturers_config[name] = {
            "base_url": base_url,
            "extraction_method": extraction_method,
            "product_urls": product_urls,
            **kwargs
        }
        print(f"✅ Added manufacturer: {name}")
    
    def add_urls_to_manufacturer(self, name: str, urls: List[str]):
        """Add URLs to existing manufacturer"""
        if name in self.manufacturers_config:
            existing_urls = set(self.manufacturers_config[name].get('product_urls', []))
            new_urls = [url for url in urls if url not in existing_urls]
            
            self.manufacturers_config[name]['product_urls'].extend(new_urls)
            print(f"✅ Added {len(new_urls)} new URLs to {name}")
        else:
            print(f"❌ Manufacturer {name} not found")
    
    def remove_manufacturer(self, name: str):
        """Remove a manufacturer from the config"""
        if name in self.manufacturers_config:
            del self.manufacturers_config[name]
            print(f"✅ Removed manufacturer: {name}")
        else:
            print(f"❌ Manufacturer {name} not found")
    
    def list_manufacturers(self):
        """Print list of all manufacturers with their URL counts"""
        print("📋 Configured Manufacturers:")
        print("-" * 50)
        
        for name, config in self.manufacturers_config.items():
            url_count = len(config.get('product_urls', []))
            method = config.get('extraction_method', 'text')
            language = config.get('language', 'english')
            
            extra_info = f"({method}"
            if language != 'english':
                extra_info += f", {language}"
            extra_info += ")"
            
            print(f"  • {name}: {url_count} URLs {extra_info}")
        
        total_urls = sum(len(config.get('product_urls', [])) for config in self.manufacturers_config.values())
        print(f"\n🎯 Total: {len(self.manufacturers_config)} manufacturers, {total_urls} URLs")

# Example usage and testing
if __name__ == "__main__":
    try:
        config = ConfigLoader()
        
        print("🚀 Arrow Scraper Configuration")
        print("=" * 50)
        
        # List all manufacturers
        config.list_manufacturers()
        
        # Show settings
        print(f"\n⚙️  Settings:")
        for key, value in config.get_settings().items():
            print(f"   {key}: {value}")
        
        # Test specific manufacturer lookup
        print(f"\n🔍 Testing manufacturer lookup:")
        test_names = ["Carbon Express", "Easton", "DK"]
        for test_name in test_names:
            found = config.find_manufacturer_by_partial_name(test_name)
            if found:
                urls = config.get_manufacturer_urls(found)
                method = config.get_extraction_method(found)
                print(f"   '{test_name}' → {found}: {len(urls)} URLs, {method} extraction")
            else:
                print(f"   '{test_name}' → Not found")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")