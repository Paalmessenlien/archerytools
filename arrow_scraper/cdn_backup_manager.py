#!/usr/bin/env python3
"""
CDN Backup Manager for ArrowTuner
Provides centralized backup management across multiple CDN providers
"""

import os
import re
import requests
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class BackupInfo:
    """Standardized backup information across all CDN providers"""
    id: str
    name: str
    filename: str
    created_at: str
    file_size_mb: float
    environment: str  # production, development, staging
    backup_type: str  # full, arrow_only, user_only
    cdn_url: str
    cdn_type: str
    include_arrow_db: bool = True
    include_user_db: bool = True
    is_cdn_direct: bool = True
    source: str = 'cdn'
    source_description: str = 'CDN Storage'

class CDNProvider(ABC):
    """Abstract base class for CDN providers"""
    
    @abstractmethod
    def list_backups(self, backup_path: str = "arrows/backups/") -> List[BackupInfo]:
        """List all backup files from CDN"""
        pass
    
    @abstractmethod
    def upload_backup(self, local_file_path: str, remote_path: str) -> str:
        """Upload backup file to CDN and return CDN URL"""
        pass
    
    @abstractmethod
    def delete_backup(self, backup_id: str, remote_path: str) -> bool:
        """Delete backup file from CDN"""
        pass
    
    @abstractmethod
    def get_backup_url(self, filename: str, backup_path: str = "arrows/backups/") -> str:
        """Get direct download URL for backup file"""
        pass

class BunnyCDNProvider(CDNProvider):
    """Bunny CDN Storage provider implementation"""
    
    def __init__(self):
        self.storage_zone = os.getenv('BUNNY_STORAGE_ZONE', 'arrowtuner-images')
        self.access_key = os.getenv('BUNNY_ACCESS_KEY')
        self.region = os.getenv('BUNNY_REGION', 'de')
        self.hostname = os.getenv('BUNNY_HOSTNAME', f'{self.storage_zone}.b-cdn.net')
        
        # Determine API endpoint based on region
        if self.region == 'de':
            self.api_base = 'https://storage.bunnycdn.com'
        else:
            self.api_base = 'https://ny.storage.bunnycdn.com'
    
    def list_backups(self, backup_path: str = "arrows/backups/") -> List[BackupInfo]:
        """List backup files from Bunny CDN Storage API"""
        if not self.access_key:
            print("❌ Bunny CDN access key not configured")
            return []
        
        api_url = f"{self.api_base}/{self.storage_zone}/{backup_path}"
        headers = {
            'AccessKey': self.access_key,
            'Accept': 'application/json'
        }
        
        try:
            print(f"🌐 Fetching backups from Bunny CDN: {api_url}")
            response = requests.get(api_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                files = response.json()
                backups = []
                
                for file_info in files:
                    filename = file_info.get('ObjectName', '')
                    if filename.endswith('.tar.gz') or filename.endswith('.gz'):
                        backup_info = self._parse_backup_file_info(file_info, backup_path)
                        if backup_info:
                            backups.append(backup_info)
                
                print(f"✅ Found {len(backups)} backup files on Bunny CDN")
                return backups
                
            elif response.status_code == 404:
                print(f"⚠️  Bunny CDN backups directory not found: {api_url}")
                print("ℹ️  This is normal if no backups have been uploaded yet")
                return []
            else:
                print(f"❌ Bunny CDN API error: {response.status_code} - {response.text}")
                return []
                
        except requests.RequestException as e:
            print(f"❌ Bunny CDN request failed: {e}")
            return []
    
    def _parse_backup_file_info(self, file_info: dict, backup_path: str) -> Optional[BackupInfo]:
        """Parse Bunny CDN file info into standardized BackupInfo"""
        try:
            filename = file_info.get('ObjectName', '')
            file_size_bytes = file_info.get('Length', 0)
            last_changed = file_info.get('LastChanged', '')
            
            # Parse backup metadata from filename
            metadata = self._extract_backup_metadata(filename)
            
            # Generate consistent backup ID
            import hashlib
            backup_id = f"cdn_{hashlib.md5(filename.encode()).hexdigest()[:8]}"
            
            # Convert file size to MB
            file_size_mb = file_size_bytes / (1024 * 1024) if file_size_bytes else 0.0
            
            # Format creation date
            created_at = self._format_bunny_timestamp(last_changed) or datetime.now().isoformat()
            
            return BackupInfo(
                id=backup_id,
                name=metadata['display_name'],
                filename=filename,
                created_at=created_at,
                file_size_mb=round(file_size_mb, 2),
                environment=metadata['environment'],
                backup_type=metadata['backup_type'],
                cdn_url=f"https://{self.hostname}/{backup_path}{filename}",
                cdn_type='bunnycdn',
                include_arrow_db=metadata['include_arrow_db'],
                include_user_db=metadata['include_user_db'],
                is_cdn_direct=True,
                source='cdn',
                source_description=f'{metadata["environment"].title()} (Bunny CDN)'
            )
            
        except Exception as e:
            print(f"⚠️  Could not parse backup file {filename}: {e}")
            return None
    
    def _format_bunny_timestamp(self, timestamp_str: str) -> Optional[str]:
        """Convert Bunny CDN timestamp to ISO format"""
        try:
            # Bunny CDN uses format like "2025-08-12T14:30:45.123"
            if timestamp_str and 'T' in timestamp_str:
                # Remove microseconds if present and ensure timezone
                clean_timestamp = timestamp_str.split('.')[0]
                dt = datetime.fromisoformat(clean_timestamp)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.isoformat()
        except Exception as e:
            print(f"⚠️  Could not parse timestamp {timestamp_str}: {e}")
        
        return None
    
    def upload_backup(self, local_file_path: str, remote_path: str) -> str:
        """Upload backup file to Bunny CDN"""
        if not self.access_key:
            raise ValueError("Bunny CDN access key not configured")
        
        filename = os.path.basename(local_file_path)
        upload_url = f"{self.api_base}/{self.storage_zone}/{remote_path}{filename}"
        
        headers = {
            'AccessKey': self.access_key,
            'Content-Type': 'application/octet-stream'
        }
        
        try:
            with open(local_file_path, 'rb') as f:
                response = requests.put(upload_url, data=f, headers=headers, timeout=300)
                response.raise_for_status()
            
            cdn_url = f"https://{self.hostname}/{remote_path}{filename}"
            print(f"✅ Backup uploaded to Bunny CDN: {cdn_url}")
            return cdn_url
            
        except Exception as e:
            print(f"❌ Failed to upload to Bunny CDN: {e}")
            raise
    
    def delete_backup(self, backup_id: str, remote_path: str) -> bool:
        """Delete backup from Bunny CDN (not implemented)"""
        # TODO: Implement Bunny CDN deletion
        print(f"⚠️  Bunny CDN backup deletion not yet implemented for {backup_id}")
        return False
    
    def get_backup_url(self, filename: str, backup_path: str = "arrows/backups/") -> str:
        """Get direct download URL for backup file"""
        return f"https://{self.hostname}/{backup_path}{filename}"

class CloudinaryCDNProvider(CDNProvider):
    """Cloudinary CDN provider implementation"""
    
    def __init__(self):
        self.cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        self.api_key = os.getenv('CLOUDINARY_API_KEY')
        self.api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    def list_backups(self, backup_path: str = "arrows/backups/") -> List[BackupInfo]:
        """List backups from Cloudinary (placeholder)"""
        print("⚠️  Cloudinary backup listing not yet implemented")
        return []
    
    def upload_backup(self, local_file_path: str, remote_path: str) -> str:
        """Upload to Cloudinary (placeholder)"""
        raise NotImplementedError("Cloudinary upload not yet implemented")
    
    def delete_backup(self, backup_id: str, remote_path: str) -> bool:
        """Delete from Cloudinary (placeholder)"""
        return False
    
    def get_backup_url(self, filename: str, backup_path: str = "arrows/backups/") -> str:
        """Get Cloudinary download URL (placeholder)"""
        return f"https://res.cloudinary.com/{self.cloud_name}/raw/upload/{backup_path}{filename}"

class AWSS3CDNProvider(CDNProvider):
    """AWS S3 CDN provider implementation"""
    
    def __init__(self):
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
        self.access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
    
    def list_backups(self, backup_path: str = "arrows/backups/") -> List[BackupInfo]:
        """List backups from AWS S3 (placeholder)"""
        print("⚠️  AWS S3 backup listing not yet implemented")
        return []
    
    def upload_backup(self, local_file_path: str, remote_path: str) -> str:
        """Upload to AWS S3 (placeholder)"""
        raise NotImplementedError("AWS S3 upload not yet implemented")
    
    def delete_backup(self, backup_id: str, remote_path: str) -> bool:
        """Delete from AWS S3 (placeholder)"""
        return False
    
    def get_backup_url(self, filename: str, backup_path: str = "arrows/backups/") -> str:
        """Get S3 download URL (placeholder)"""
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{backup_path}{filename}"

class CDNBackupManager:
    """Centralized CDN backup manager with multi-provider support"""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.primary_provider = self._get_primary_provider()
        print(f"🌐 CDN Backup Manager initialized with {len(self.providers)} providers")
        print(f"   Primary provider: {self.primary_provider.__class__.__name__ if self.primary_provider else 'None'}")
    
    def _initialize_providers(self) -> Dict[str, CDNProvider]:
        """Initialize available CDN providers based on configuration"""
        providers = {}
        
        # Bunny CDN
        if os.getenv('BUNNY_ACCESS_KEY'):
            providers['bunnycdn'] = BunnyCDNProvider()
            print("✅ Bunny CDN provider configured")
        else:
            print("⚠️  Bunny CDN not configured (missing BUNNY_ACCESS_KEY)")
        
        # Cloudinary
        if all([os.getenv('CLOUDINARY_CLOUD_NAME'), os.getenv('CLOUDINARY_API_KEY'), os.getenv('CLOUDINARY_API_SECRET')]):
            providers['cloudinary'] = CloudinaryCDNProvider()
            print("✅ Cloudinary provider configured")
        else:
            print("ℹ️  Cloudinary not configured (missing credentials)")
        
        # AWS S3
        if all([os.getenv('AWS_S3_BUCKET'), os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY')]):
            providers['aws_s3'] = AWSS3CDNProvider()
            print("✅ AWS S3 provider configured")
        else:
            print("ℹ️  AWS S3 not configured (missing credentials)")
        
        return providers
    
    def _get_primary_provider(self) -> Optional[CDNProvider]:
        """Get the primary CDN provider based on configuration"""
        cdn_type = os.getenv('CDN_TYPE', 'bunnycdn')
        return self.providers.get(cdn_type)
    
    def list_all_backups(self) -> List[BackupInfo]:
        """List backups from all configured CDN providers"""
        all_backups = []
        
        for provider_name, provider in self.providers.items():
            try:
                print(f"📡 Fetching backups from {provider_name}...")
                provider_backups = provider.list_backups()
                
                # Add provider indicator to each backup
                for backup in provider_backups:
                    backup.source_description += f" ({provider_name})"
                
                all_backups.extend(provider_backups)
                print(f"✅ {provider_name}: {len(provider_backups)} backups")
                
            except Exception as e:
                print(f"❌ Error fetching backups from {provider_name}: {e}")
        
        # Sort by creation date (newest first)
        all_backups.sort(key=lambda x: x.created_at, reverse=True)
        
        print(f"🎯 Total CDN backups found: {len(all_backups)}")
        return all_backups
    
    def upload_backup(self, local_file_path: str, backup_name: str = None) -> Optional[str]:
        """Upload backup to primary CDN provider"""
        if not self.primary_provider:
            print("❌ No primary CDN provider configured")
            return None
        
        try:
            filename = backup_name or os.path.basename(local_file_path)
            remote_path = "arrows/backups/"
            
            cdn_url = self.primary_provider.upload_backup(local_file_path, remote_path)
            return cdn_url
            
        except Exception as e:
            print(f"❌ Failed to upload backup to CDN: {e}")
            return None
    
    def _extract_backup_metadata(self, filename: str) -> Dict[str, Any]:
        """Extract metadata from backup filename"""
        # Default metadata
        metadata = {
            'display_name': filename.replace('.tar.gz', '').replace('.gz', ''),
            'environment': 'unknown',
            'backup_type': 'full',
            'include_arrow_db': True,
            'include_user_db': True
        }
        
        # Try to parse structured filename: {env}_{type}_{timestamp}.tar.gz
        # Examples: production_full_20250812_143045.tar.gz, dev_arrows_20250812.tar.gz
        pattern = r'^(production|prod|development|dev|staging|stage)_(full|arrows?|users?|arrow_only|user_only)_.*'
        match = re.match(pattern, filename.lower())
        
        if match:
            env, backup_type = match.groups()
            
            # Normalize environment names
            if env in ['prod', 'production']:
                metadata['environment'] = 'production'
            elif env in ['dev', 'development']:
                metadata['environment'] = 'development'
            elif env in ['stage', 'staging']:
                metadata['environment'] = 'staging'
            
            # Determine backup contents
            if backup_type in ['arrows', 'arrow_only']:
                metadata['backup_type'] = 'arrow_only'
                metadata['include_user_db'] = False
            elif backup_type in ['users', 'user_only']:
                metadata['backup_type'] = 'user_only'
                metadata['include_arrow_db'] = False
            else:
                metadata['backup_type'] = 'full'
        
        # Try to detect environment from other patterns
        filename_lower = filename.lower()
        if 'production' in filename_lower or 'prod' in filename_lower:
            metadata['environment'] = 'production'
        elif 'development' in filename_lower or 'dev' in filename_lower:
            metadata['environment'] = 'development'
        elif 'staging' in filename_lower or 'stage' in filename_lower:
            metadata['environment'] = 'staging'
        
        # Enhance display name
        env_display = metadata['environment'].title()
        type_display = metadata['backup_type'].replace('_', ' ').title()
        metadata['display_name'] = f"{env_display} {type_display} Backup"
        
        return metadata

# Convenience function for backward compatibility
def get_cdn_backups() -> List[BackupInfo]:
    """Get all CDN backups using the centralized manager"""
    manager = CDNBackupManager()
    return manager.list_all_backups()

# For testing
if __name__ == "__main__":
    print("🧪 Testing CDN Backup Manager")
    print("=" * 50)
    
    manager = CDNBackupManager()
    backups = manager.list_all_backups()
    
    print(f"\n📊 Found {len(backups)} total backups:")
    for backup in backups:
        print(f"  • {backup.name} ({backup.environment}) - {backup.file_size_mb:.1f}MB")
        print(f"    {backup.source_description} - {backup.created_at}")
        print(f"    {backup.cdn_url}")
        print()