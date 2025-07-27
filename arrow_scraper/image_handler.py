#!/usr/bin/env python3
"""
Enhanced Image Handler with CDN Integration
Handles image downloading, processing, and CDN upload for the arrow scraper
"""

import os
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import logging
from cdn_uploader import CDNUploader

class ImageHandler:
    """Enhanced image handling with CDN upload capabilities"""
    
    def __init__(self, local_storage_dir: str = "./data/images", 
                 cdn_enabled: bool = None, cdn_type: str = None):
        """
        Initialize image handler
        
        Args:
            local_storage_dir: Local directory for temporary image storage
            cdn_enabled: Whether to upload to CDN (auto-detect if None)
            cdn_type: CDN service type (cloudinary, s3, local)
        """
        self.local_storage_dir = Path(local_storage_dir)
        self.local_storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
        
        # Initialize CDN uploader
        self.cdn_enabled = cdn_enabled
        self.cdn_uploader = None
        
        if self.cdn_enabled is None:
            # Auto-detect CDN availability
            self.cdn_enabled = self._detect_cdn_config()
        
        if self.cdn_enabled:
            try:
                cdn_service = cdn_type or os.getenv('CDN_TYPE', 'local')
                self.cdn_uploader = CDNUploader(cdn_service)
                self.logger.info(f"CDN uploader initialized: {cdn_service}")
            except Exception as e:
                self.logger.warning(f"CDN initialization failed: {e}")
                self.cdn_enabled = False
        
        if not self.cdn_enabled:
            self.logger.info("Using local storage only")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for image operations"""
        logger = logging.getLogger('image_handler')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _detect_cdn_config(self) -> bool:
        """Auto-detect if CDN configuration is available"""
        # Check for CDN environment variables
        cloudinary_config = all([
            os.getenv('CLOUDINARY_CLOUD_NAME'),
            os.getenv('CLOUDINARY_API_KEY'),
            os.getenv('CLOUDINARY_API_SECRET')
        ])
        
        s3_config = all([
            os.getenv('AWS_S3_BUCKET'),
            os.getenv('AWS_CLOUDFRONT_DOMAIN')
        ])
        
        return cloudinary_config or s3_config
    
    def process_image(self, image_url: str, manufacturer: str, 
                     model_name: str, image_type: str = "primary") -> Dict[str, Any]:
        """
        Download image and upload to CDN if enabled
        
        Returns:
            Dict with image URLs and metadata
        """
        try:
            # Step 1: Download image locally (for backup/processing)
            local_path = self._download_image_locally(
                image_url, manufacturer, model_name, image_type
            )
            
            if not local_path:
                return self._create_error_result(image_url, "Download failed")
            
            # Step 2: Upload to CDN if enabled
            cdn_result = None
            if self.cdn_enabled and self.cdn_uploader:
                cdn_result = self.cdn_uploader.upload_from_file(
                    local_path, manufacturer, model_name, image_type
                )
                
                if cdn_result:
                    self.logger.info(f"Uploaded to CDN: {cdn_result['cdn_url']}")
                    
                    # Clean up local file if CDN upload successful (optional)
                    if os.getenv('CLEANUP_LOCAL_AFTER_CDN', 'false').lower() == 'true':
                        try:
                            os.remove(local_path)
                            self.logger.debug(f"Cleaned up local file: {local_path}")
                        except Exception as e:
                            self.logger.warning(f"Failed to cleanup {local_path}: {e}")
            
            # Step 3: Prepare result
            result = {
                "original_url": image_url,
                "local_path": local_path,
                "status": "success",
                "manufacturer": manufacturer,
                "model_name": model_name,
                "image_type": image_type,
                "processed_at": time.time()
            }
            
            # Add CDN information if available
            if cdn_result:
                result.update({
                    "cdn_url": cdn_result["cdn_url"],
                    "cdn_type": cdn_result["cdn_type"],
                    "cdn_metadata": cdn_result
                })
                # Use CDN URL as primary
                result["image_url"] = cdn_result["cdn_url"]
            else:
                # Fallback to local URL
                result["image_url"] = self._generate_local_url(local_path)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process image {image_url}: {e}")
            return self._create_error_result(image_url, str(e))
    
    def _download_image_locally(self, image_url: str, manufacturer: str, 
                               model_name: str, image_type: str) -> Optional[str]:
        """Download image to local storage"""
        try:
            # Create safe filename
            safe_manufacturer = "".join(c for c in manufacturer if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
            safe_model = "".join(c for c in model_name if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
            
            # Get file extension from URL
            parsed_url = urlparse(image_url)
            file_ext = Path(parsed_url.path).suffix
            if not file_ext:
                file_ext = '.jpg'  # Default extension
            
            # Create local filename with timestamp to avoid conflicts
            timestamp = int(time.time())
            filename = f"{safe_manufacturer}_{safe_model}_{image_type}_{timestamp}{file_ext}"
            local_path = self.local_storage_dir / filename
            
            # Download image with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        image_url, 
                        timeout=30, 
                        stream=True,
                        headers={'User-Agent': 'ArrowTuner Image Scraper 1.0'}
                    )
                    response.raise_for_status()
                    
                    # Validate content type
                    content_type = response.headers.get('content-type', '').lower()
                    if not content_type.startswith('image/'):
                        raise ValueError(f"Invalid content type: {content_type}")
                    
                    # Save file
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Validate file size
                    file_size = local_path.stat().st_size
                    if file_size < 1024:  # Less than 1KB
                        raise ValueError(f"File too small: {file_size} bytes")
                    
                    self.logger.info(f"Downloaded image: {filename} ({file_size} bytes)")
                    return str(local_path)
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        self.logger.warning(f"Download attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                        time.sleep(wait_time)
                    else:
                        raise
            
        except Exception as e:
            self.logger.error(f"Failed to download image {image_url}: {e}")
            return None
    
    def _generate_local_url(self, local_path: str) -> str:
        """Generate URL for locally stored image"""
        local_path = Path(local_path)
        relative_path = local_path.relative_to(self.local_storage_dir)
        base_url = os.getenv('LOCAL_IMAGES_URL', 'http://localhost:5000/images')
        return f"{base_url}/{relative_path}"
    
    def _create_error_result(self, image_url: str, error_message: str) -> Dict[str, Any]:
        """Create error result dictionary"""
        return {
            "original_url": image_url,
            "local_path": None,
            "image_url": image_url,  # Fallback to original URL
            "status": "error",
            "error": error_message,
            "processed_at": time.time()
        }
    
    def process_multiple_images(self, image_urls: List[str], manufacturer: str, 
                               model_name: str) -> List[Dict[str, Any]]:
        """Process multiple images for a single arrow model"""
        results = []
        
        for i, image_url in enumerate(image_urls):
            # Determine image type based on position
            image_type = "primary" if i == 0 else f"detail_{i}"
            
            result = self.process_image(image_url, manufacturer, model_name, image_type)
            results.append(result)
            
            # Rate limiting to be respectful
            if i < len(image_urls) - 1:  # Don't sleep after last image
                time.sleep(0.5)
        
        return results
    
    def migrate_existing_images(self, local_images_dir: str, manufacturer: str) -> List[Dict[str, Any]]:
        """Migrate existing local images to CDN"""
        if not self.cdn_enabled or not self.cdn_uploader:
            self.logger.warning("CDN not enabled, cannot migrate images")
            return []
        
        images_dir = Path(local_images_dir)
        if not images_dir.exists():
            self.logger.warning(f"Images directory not found: {images_dir}")
            return []
        
        results = []
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        for image_file in images_dir.glob('*'):
            if image_file.suffix.lower() in image_extensions:
                # Extract model name from filename
                model_name = image_file.stem.replace('_', ' ').replace('-', ' ')
                
                try:
                    cdn_result = self.cdn_uploader.upload_from_file(
                        str(image_file), manufacturer, model_name, "migrated"
                    )
                    
                    if cdn_result:
                        results.append({
                            "local_file": str(image_file),
                            "cdn_url": cdn_result["cdn_url"],
                            "status": "migrated"
                        })
                        self.logger.info(f"Migrated: {image_file.name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to migrate {image_file}: {e}")
                    results.append({
                        "local_file": str(image_file),
                        "status": "error",
                        "error": str(e)
                    })
                
                # Rate limiting
                time.sleep(0.2)
        
        return results
    
    def get_image_stats(self) -> Dict[str, Any]:
        """Get statistics about processed images"""
        local_count = len(list(self.local_storage_dir.glob('*')))
        
        stats = {
            "local_images": local_count,
            "local_storage_dir": str(self.local_storage_dir),
            "cdn_enabled": self.cdn_enabled,
            "cdn_type": getattr(self.cdn_uploader, 'cdn_type', None) if self.cdn_uploader else None
        }
        
        return stats

# Example usage and testing
if __name__ == "__main__":
    print("🖼️ Enhanced Image Handler Test Suite")
    print("=" * 50)
    
    # Initialize handler
    handler = ImageHandler()
    
    # Test image processing
    test_url = "https://www.eastonarchery.com/uploads/image/field/2024-01/FMJ-5mm-arrow.png"
    
    result = handler.process_image(
        test_url, 
        "Easton Archery", 
        "FMJ 5mm Test", 
        "primary"
    )
    
    print(f"📋 Processing Result:")
    print(f"   Status: {result['status']}")
    print(f"   Image URL: {result.get('image_url', 'N/A')}")
    print(f"   Local Path: {result.get('local_path', 'N/A')}")
    if result.get('cdn_url'):
        print(f"   CDN URL: {result['cdn_url']}")
        print(f"   CDN Type: {result.get('cdn_type', 'N/A')}")
    
    # Show stats
    stats = handler.get_image_stats()
    print(f"\n📊 Image Handler Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")