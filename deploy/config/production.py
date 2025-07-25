"""
Arrow Tuning Platform - Production Flask Configuration
"""
import os
from pathlib import Path

class ProductionConfig:
    """Production configuration with security hardening"""
    
    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-in-production'
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or '/opt/arrowtuner/data/arrow_database.db'
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('SESSION_TIMEOUT', 3600))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = os.environ.get('RATE_LIMIT_PER_MINUTE', '60/minute')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_PATH = Path(os.environ.get('LOG_PATH', '/opt/arrowtuner/logs'))
    LOG_MAX_SIZE = int(os.environ.get('LOG_MAX_SIZE', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # Caching
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Application-specific
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    BACKUP_PATH = Path(os.environ.get('BACKUP_PATH', '/opt/arrowtuner/backups'))
    
    # Monitoring
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', 300))
    BACKUP_INTERVAL = int(os.environ.get('BACKUP_INTERVAL', 86400))
    
    @staticmethod
    def init_app(app):
        """Initialize application with production settings"""
        # Ensure required directories exist
        for path in [ProductionConfig.LOG_PATH, ProductionConfig.BACKUP_PATH]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            file_handler = RotatingFileHandler(
                ProductionConfig.LOG_PATH / 'arrowtuner.log',
                maxBytes=ProductionConfig.LOG_MAX_SIZE,
                backupCount=ProductionConfig.LOG_BACKUP_COUNT
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(getattr(logging, ProductionConfig.LOG_LEVEL))
            app.logger.addHandler(file_handler)
            app.logger.setLevel(getattr(logging, ProductionConfig.LOG_LEVEL))
            app.logger.info('Arrow Tuning Platform startup')

# For backward compatibility
Config = ProductionConfig