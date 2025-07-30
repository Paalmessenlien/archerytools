#!/usr/bin/env python3
"""
CDN Image Uploader for Archery Tools
Uploads scraped images to CDN services for better performance and storage optimization
"""

import os
import time
import hashlib
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import logging

# Load environment variables from root .env file
try:
    from dotenv import load_dotenv
    # Load from root .env file which now contains CDN configuration
    root_env_path = Path(__file__).parent.parent / '.env'
    if root_env_path.exists():
        load_dotenv(root_env_path)
        print(f"✅ Loaded environment from: {root_env_path}")
    else:
        print("⚠️ No root .env file found, using system environment variables")
except ImportError:
    print("⚠️ python-dotenv not available, using system environment variables only")

try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

try:
    import boto3
    from botocore.exceptions import ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

class CDNUploader:
    """Upload images to CDN services with fallback options"""
    
    def __init__(self, cdn_type: str = "cloudinary"):
        self.cdn_type = cdn_type.lower()
        self.logger = self._setup_logging()
        
        # Initialize CDN client based on type
        if self.cdn_type == "cloudinary":
            self._init_cloudinary()
        elif self.cdn_type == "s3":
            self._init_s3()
        elif self.cdn_type == "bunnycdn":
            self._init_bunnycdn()
        elif self.cdn_type == "local":
            self._init_local()
        else:
            raise ValueError(f"Unsupported CDN type: {cdn_type}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for CDN operations"""
        logger = logging.getLogger('cdn_uploader')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _init_cloudinary(self):
        """Initialize Cloudinary CDN"""
        if not CLOUDINARY_AVAILABLE:
            raise ImportError("Cloudinary package not installed. Install with: pip install cloudinary")
        
        # Configure Cloudinary from environment variables
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
        
        if not all([os.getenv('CLOUDINARY_CLOUD_NAME'), 
                   os.getenv('CLOUDINARY_API_KEY'), 
                   os.getenv('CLOUDINARY_API_SECRET')]):
            raise ValueError("Cloudinary credentials not found in environment variables")
        
        self.logger.info("Cloudinary CDN initialized")
    
    def _init_s3(self):
        """Initialize AWS S3 + CloudFront CDN"""
        if not S3_AVAILABLE:
            raise ImportError("Boto3 package not installed. Install with: pip install boto3")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        self.s3_bucket = os.getenv('AWS_S3_BUCKET')
        self.cloudfront_domain = os.getenv('AWS_CLOUDFRONT_DOMAIN')
        
        if not all([self.s3_bucket, self.cloudfront_domain]):
            raise ValueError("S3 bucket and CloudFront domain required")
        
        self.logger.info("AWS S3 + CloudFront CDN initialized")
    
    def _init_bunnycdn(self):
        """Initialize Bunny CDN"""
        self.bunny_storage_zone = os.getenv('BUNNY_STORAGE_ZONE')
        self.bunny_access_key = os.getenv('BUNNY_ACCESS_KEY')
        self.bunny_hostname = os.getenv('BUNNY_HOSTNAME')  # Your CDN hostname
        self.bunny_region = os.getenv('BUNNY_REGION', 'de')  # Default to Germany
        
        if not all([self.bunny_storage_zone, self.bunny_access_key, self.bunny_hostname]):
            raise ValueError("Bunny CDN credentials required: BUNNY_STORAGE_ZONE, BUNNY_ACCESS_KEY, BUNNY_HOSTNAME")
        
        # Bunny Storage API endpoint based on region
        region_endpoints = {
            'de': 'storage.bunnycdn.com',
            'ny': 'ny.storage.bunnycdn.com',
            'la': 'la.storage.bunnycdn.com',
            'sg': 'sg.storage.bunnycdn.com',
            'syd': 'syd.storage.bunnycdn.com',
            'uk': 'uk.storage.bunnycdn.com'
        }
        
        self.bunny_storage_endpoint = region_endpoints.get(self.bunny_region, 'storage.bunnycdn.com')
        self.logger.info(f"Bunny CDN initialized (region: {self.bunny_region})")
    
    def _init_local(self):
        """Initialize local file storage (fallback)"""
        self.local_base_path = Path(os.getenv('LOCAL_CDN_PATH', './cdn_images'))
        self.local_base_path.mkdir(exist_ok=True)
        self.local_base_url = os.getenv('LOCAL_CDN_URL', 'http://localhost:5000/images')
        self.logger.info("Local file storage initialized")
    
    def generate_image_id(self, manufacturer: str, model_name: str, 
                         image_url: str, image_type: str = "primary") -> str:
        """Generate unique, SEO-friendly image ID"""
        # Clean manufacturer and model name
        clean_manufacturer = "".join(c for c in manufacturer if c.isalnum() or c in "-_").strip("-_")
        clean_model = "".join(c for c in model_name if c.isalnum() or c in "-_").strip("-_")
        
        # Create hash of original URL for uniqueness
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
        
        # Generate SEO-friendly ID
        image_id = f"arrows/{clean_manufacturer}/{clean_model}/{image_type}_{url_hash}"
        return image_id.lower()
    
    def upload_from_url(self, image_url: str, manufacturer: str, 
                       model_name: str, image_type: str = "primary") -> Optional[Dict[str, Any]]:
        """Upload image from URL to CDN"""
        try:
            image_id = self.generate_image_id(manufacturer, model_name, image_url, image_type)
            
            if self.cdn_type == "cloudinary":
                return self._upload_to_cloudinary_from_url(image_url, image_id)
            elif self.cdn_type == "s3":
                return self._upload_to_s3_from_url(image_url, image_id)
            elif self.cdn_type == "bunnycdn":
                return self._upload_to_bunnycdn_from_url(image_url, image_id)
            elif self.cdn_type == "local":
                return self._upload_to_local_from_url(image_url, image_id)
            
        except Exception as e:
            self.logger.error(f"Failed to upload image {image_url}: {e}")
            return None
    
    def upload_from_file(self, file_path: str, manufacturer: str, 
                        model_name: str, image_type: str = "primary") -> Optional[Dict[str, Any]]:
        """Upload local image file to CDN"""
        try:
            # Use file path to generate unique ID
            image_id = self.generate_image_id(manufacturer, model_name, file_path, image_type)
            
            if self.cdn_type == "cloudinary":
                return self._upload_to_cloudinary_from_file(file_path, image_id)
            elif self.cdn_type == "s3":
                return self._upload_to_s3_from_file(file_path, image_id)
            elif self.cdn_type == "bunnycdn":
                return self._upload_to_bunnycdn_from_file(file_path, image_id)
            elif self.cdn_type == "local":
                return self._upload_to_local_from_file(file_path, image_id)
            
        except Exception as e:
            self.logger.error(f"Failed to upload file {file_path}: {e}")
            return None
    
    def _upload_to_cloudinary_from_url(self, image_url: str, image_id: str) -> Dict[str, Any]:
        """Upload to Cloudinary from URL"""
        result = cloudinary.uploader.upload(
            image_url,
            public_id=image_id,
            folder="arrowtuner",
            quality="auto:good",
            fetch_format="auto",
            flags="progressive",
            transformation=[
                {"width": 800, "height": 600, "crop": "limit"},
                {"quality": "auto:good"}
            ]
        )
        
        self.logger.info(f"Uploaded to Cloudinary: {result['public_id']}")
        
        return {
            "cdn_url": result['secure_url'],
            "public_id": result['public_id'],
            "cdn_type": "cloudinary",
            "width": result.get('width'),
            "height": result.get('height'),
            "format": result.get('format'),
            "bytes": result.get('bytes')
        }
    
    def _upload_to_cloudinary_from_file(self, file_path: str, image_id: str) -> Dict[str, Any]:
        """Upload local file to Cloudinary"""
        result = cloudinary.uploader.upload(
            file_path,
            public_id=image_id,
            folder="arrowtuner",
            quality="auto:good",
            fetch_format="auto",
            flags="progressive",
            transformation=[
                {"width": 800, "height": 600, "crop": "limit"},
                {"quality": "auto:good"}
            ]
        )
        
        self.logger.info(f"Uploaded file to Cloudinary: {result['public_id']}")
        
        return {
            "cdn_url": result['secure_url'],
            "public_id": result['public_id'],
            "cdn_type": "cloudinary",
            "width": result.get('width'),
            "height": result.get('height'),
            "format": result.get('format'),
            "bytes": result.get('bytes')
        }
    
    def _upload_to_s3_from_url(self, image_url: str, image_id: str) -> Dict[str, Any]:
        """Upload to S3 from URL"""
        # Download image data
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Determine content type
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        # Upload to S3
        key = f"{image_id}.{self._get_extension_from_content_type(content_type)}"
        
        self.s3_client.put_object(
            Bucket=self.s3_bucket,
            Key=key,
            Body=response.content,
            ContentType=content_type,
            CacheControl='max-age=31536000'  # 1 year cache
        )
        
        cdn_url = f"https://{self.cloudfront_domain}/{key}"
        
        self.logger.info(f"Uploaded to S3: {key}")
        
        return {
            "cdn_url": cdn_url,
            "s3_key": key,
            "cdn_type": "s3",
            "content_type": content_type,
            "bytes": len(response.content)
        }
    
    def _upload_to_s3_from_file(self, file_path: str, image_id: str) -> Dict[str, Any]:
        """Upload local file to S3"""
        file_path = Path(file_path)
        
        # Determine content type from extension
        extension = file_path.suffix.lower()
        content_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }.get(extension, 'image/jpeg')
        
        key = f"{image_id}{extension}"
        
        # Upload file
        self.s3_client.upload_file(
            str(file_path),
            self.s3_bucket,
            key,
            ExtraArgs={
                'ContentType': content_type,
                'CacheControl': 'max-age=31536000'
            }
        )
        
        cdn_url = f"https://{self.cloudfront_domain}/{key}"
        
        self.logger.info(f"Uploaded file to S3: {key}")
        
        return {
            "cdn_url": cdn_url,
            "s3_key": key,
            "cdn_type": "s3",
            "content_type": content_type,
            "bytes": file_path.stat().st_size
        }
    
    def _upload_to_bunnycdn_from_url(self, image_url: str, image_id: str) -> Dict[str, Any]:
        """Upload to Bunny CDN from URL"""
        # Download image data
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Determine content type and extension
        content_type = response.headers.get('content-type', 'image/jpeg')
        extension = self._get_extension_from_content_type(content_type)
        
        # Create file path for Bunny Storage
        file_path = f"{image_id}.{extension}"
        
        # Upload to Bunny Storage using PUT request
        storage_url = f"https://{self.bunny_storage_endpoint}/{self.bunny_storage_zone}/{file_path}"
        
        headers = {
            'AccessKey': self.bunny_access_key,
            'Content-Type': content_type,
            'Cache-Control': 'max-age=31536000'
        }
        
        upload_response = requests.put(
            storage_url,
            data=response.content,
            headers=headers,
            timeout=60
        )
        upload_response.raise_for_status()
        
        # Generate CDN URL
        cdn_url = f"https://{self.bunny_hostname}/{file_path}"
        
        self.logger.info(f"Uploaded to Bunny CDN: {file_path}")
        
        return {
            "cdn_url": cdn_url,
            "bunny_path": file_path,
            "cdn_type": "bunnycdn",
            "content_type": content_type,
            "bytes": len(response.content)
        }
    
    def _upload_to_bunnycdn_from_file(self, file_path: str, image_id: str) -> Dict[str, Any]:
        """Upload local file to Bunny CDN"""
        file_path = Path(file_path)
        
        # Determine content type from extension
        extension = file_path.suffix.lower()
        content_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }.get(extension, 'image/jpeg')
        
        # Create remote file path
        remote_path = f"{image_id}{extension}"
        
        # Upload to Bunny Storage
        storage_url = f"https://{self.bunny_storage_endpoint}/{self.bunny_storage_zone}/{remote_path}"
        
        headers = {
            'AccessKey': self.bunny_access_key,
            'Content-Type': content_type,
            'Cache-Control': 'max-age=31536000'
        }
        
        with open(file_path, 'rb') as f:
            upload_response = requests.put(
                storage_url,
                data=f,
                headers=headers,
                timeout=60
            )
            upload_response.raise_for_status()
        
        # Generate CDN URL
        cdn_url = f"https://{self.bunny_hostname}/{remote_path}"
        
        self.logger.info(f"Uploaded file to Bunny CDN: {remote_path}")
        
        return {
            "cdn_url": cdn_url,
            "bunny_path": remote_path,
            "cdn_type": "bunnycdn",
            "content_type": content_type,
            "bytes": file_path.stat().st_size
        }
    
    def _upload_to_local_from_url(self, image_url: str, image_id: str) -> Dict[str, Any]:
        """Save to local storage from URL"""
        # Download image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Create local path
        local_path = self.local_base_path / f"{image_id}.jpg"
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        # Generate URL
        relative_path = local_path.relative_to(self.local_base_path)
        cdn_url = f"{self.local_base_url}/{relative_path}"
        
        self.logger.info(f"Saved locally: {local_path}")
        
        return {
            "cdn_url": cdn_url,
            "local_path": str(local_path),
            "cdn_type": "local",
            "bytes": len(response.content)
        }
    
    def _upload_to_local_from_file(self, file_path: str, image_id: str) -> Dict[str, Any]:
        """Copy to local storage from file"""
        import shutil
        
        source_path = Path(file_path)
        local_path = self.local_base_path / f"{image_id}{source_path.suffix}"
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source_path, local_path)
        
        # Generate URL
        relative_path = local_path.relative_to(self.local_base_path)
        cdn_url = f"{self.local_base_url}/{relative_path}"
        
        self.logger.info(f"Copied locally: {local_path}")
        
        return {
            "cdn_url": cdn_url,
            "local_path": str(local_path),
            "cdn_type": "local",
            "bytes": local_path.stat().st_size
        }
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Get file extension from content type"""
        extensions = {
            'image/jpeg': 'jpg',
            'image/jpg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'image/webp': 'webp'
        }
        return extensions.get(content_type, 'jpg')
    
    def batch_upload_from_directory(self, directory_path: str, 
                                  manufacturer: str) -> List[Dict[str, Any]]:
        """Upload all images from a directory"""
        directory = Path(directory_path)
        results = []
        
        for image_file in directory.glob('*'):
            if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                # Extract model name from filename
                model_name = image_file.stem.replace('_', ' ').replace('-', ' ')
                
                result = self.upload_from_file(
                    str(image_file), 
                    manufacturer, 
                    model_name
                )
                
                if result:
                    results.append(result)
                
                # Rate limiting
                time.sleep(0.1)
        
        return results

# Example usage and testing
if __name__ == "__main__":
    print("🖼️ CDN Image Uploader Test Suite")
    print("=" * 50)
    
    # Test with local storage (fallback)
    try:
        uploader = CDNUploader("local")
        
        # Test image URL
        test_url = "https://www.eastonarchery.com/uploads/image/field/2024-01/FMJ-5mm-arrow.png"
        
        result = uploader.upload_from_url(
            test_url, 
            "Easton Archery", 
            "FMJ 5mm", 
            "primary"
        )
        
        if result:
            print(f"✅ Upload successful:")
            print(f"   CDN URL: {result['cdn_url']}")
            print(f"   CDN Type: {result['cdn_type']}")
            print(f"   Size: {result['bytes']} bytes")
        else:
            print("❌ Upload failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 To use CDN services:")
        print("   Cloudinary: pip install cloudinary")
        print("   AWS S3: pip install boto3")
        print("   Set environment variables for your chosen service")