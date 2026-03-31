"""
Pi Cloud Server - Configuration
================================

This module contains configuration classes for different environments.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Base configuration class.
    Contains settings common to all environments.
    """
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://picloud:password@localhost:5432/picloud_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Enable connection health checks
        'pool_recycle': 300,    # Recycle connections every 5 minutes
    }
    
    # Storage settings
    STORAGE_PATH = os.environ.get('STORAGE_PATH', './storage')
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 100 * 1024 * 1024))  # 100MB default
    ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS', '*')
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', None)
    
    # Optional API key
    API_KEY = os.environ.get('API_KEY', None)
    
    # Upload settings for Flask
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE


class DevelopmentConfig(Config):
    """
    Development configuration.
    Used during development on local machine.
    """
    
    DEBUG = True
    FLASK_ENV = 'development'
    
    # More verbose logging in development
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')


class ProductionConfig(Config):
    """
    Production configuration.
    Used when deployed to Raspberry Pi.
    """
    
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Ensure secret key is set in production
    @property
    def SECRET_KEY(self):
        key = os.environ.get('SECRET_KEY')
        if not key or key == 'dev-secret-key-change-in-production':
            raise ValueError("SECRET_KEY must be set in production!")
        return key
    
    # Less verbose logging in production
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')


class TestingConfig(Config):
    """
    Testing configuration.
    Used when running tests.
    """
    
    TESTING = True
    DEBUG = True
    
    # Use SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Use temporary directory for test storage
    STORAGE_PATH = '/tmp/picloud_test_storage'


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
