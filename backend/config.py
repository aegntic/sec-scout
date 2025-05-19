#!/usr/bin/env python3
# SecureScout - Configuration Settings

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-key-change-in-production')
    
    # Application directories
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    LOGS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'logs')
    REPORTS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'reports')
    DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
    
    # Default scan settings
    DEFAULT_SCAN_TIMEOUT = 3600  # 1 hour
    DEFAULT_THREAD_COUNT = 10
    MAX_THREAD_COUNT = 50
    
    # Rate limiting and stealth settings
    DEFAULT_REQUEST_DELAY = 0.5  # seconds between requests
    DEFAULT_JITTER = 0.2  # random delay variation
    DEFAULT_USER_AGENT_ROTATION = True
    DEFAULT_IP_ROTATION = False
    
    # Redis configuration (for task queue)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Database configuration
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///' + os.path.join(DATA_DIR, 'securescout.db'))


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # In production, these must be set via environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # More strict security settings for production
    DEFAULT_REQUEST_DELAY = 1.0  # seconds between requests
    DEFAULT_THREAD_COUNT = 5