"""
Cấu hình chính cho ứng dụng ETC Backend
"""
import os
from pathlib import Path

# Đường dẫn gốc của project
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """Cấu hình cơ bản"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/etc_backend.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    
    # Logs
    LOG_FOLDER = BASE_DIR / 'logs'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # OCR Settings
    OCR_CONFIDENCE_THRESHOLD = 0.5
    OCR_MERGE_THRESHOLD = 0.2
    OCR_LANGUAGES = ['en', 'vi']
    
    # Server
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # API Documentation
    SWAGGER_UI_DOC_EXPANSION = 'list'
    SWAGGER_UI_OPERATION_ID = True
    SWAGGER_UI_REQUEST_DURATION = True

class DevelopmentConfig(Config):
    """Cấu hình cho môi trường phát triển"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # Development database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or f'sqlite:///{BASE_DIR}/etc_backend_dev.db'

class ProductionConfig(Config):
    """Cấu hình cho môi trường production"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # Production database - should use PostgreSQL or MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/etc_backend_prod.db'
    
    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-in-production'

class TestingConfig(Config):
    """Cấu hình cho testing"""
    TESTING = True
    DEBUG = True
    
    # In-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Dictionary để chọn config dựa trên môi trường
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
