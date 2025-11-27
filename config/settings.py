"""
Configuration module for Gravity TSETMC
Contains environment variables and settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./tsetmc.db')
    
    # API Settings
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 10))
    API_RETRIES = int(os.getenv('API_RETRIES', 3))
    API_RETRY_DELAY = int(os.getenv('API_RETRY_DELAY', 1))
    
    # TSE API Settings
    TSE_BASE_URL = os.getenv('TSE_BASE_URL', 'https://service.tsetmc.com')
    TGJU_BASE_URL = os.getenv('TGJU_BASE_URL', 'https://api.tgju.org')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    
    # Application
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENVIRONMENT = 'development'
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENVIRONMENT = 'production'
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Testing configuration"""
    DATABASE_URL = 'sqlite:///:memory:'
    DEBUG = True
    ENVIRONMENT = 'testing'
    LOG_LEVEL = 'DEBUG'


def get_config(env: str = None) -> Config:
    """
    Get configuration based on environment.
    
    Args:
        env: Environment name (development, production, testing)
             If None, uses ENVIRONMENT env variable
    
    Returns:
        Configuration instance
    """
    if env is None:
        env = os.getenv('ENVIRONMENT', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return config_map.get(env, DevelopmentConfig)()
