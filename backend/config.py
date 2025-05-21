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

    # Authentication configuration
    ACCESS_TOKEN_LIFETIME_MINUTES = int(os.environ.get('ACCESS_TOKEN_LIFETIME_MINUTES', 30))
    REFRESH_TOKEN_LIFETIME_DAYS = int(os.environ.get('REFRESH_TOKEN_LIFETIME_DAYS', 7))
    CREATE_DEFAULT_ADMIN = os.environ.get('CREATE_DEFAULT_ADMIN', 'true').lower() == 'true'
    DEFAULT_ADMIN_USERNAME = os.environ.get('DEFAULT_ADMIN_USERNAME', 'admin')
    DEFAULT_ADMIN_PASSWORD = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'SecureScout@2025!')
    DEFAULT_ADMIN_EMAIL = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@securescout.local')
    ALLOW_SELF_REGISTRATION = os.environ.get('ALLOW_SELF_REGISTRATION', 'false').lower() == 'true'

    # Password policy
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', 12))
    PASSWORD_REQUIRE_UPPERCASE = os.environ.get('PASSWORD_REQUIRE_UPPERCASE', 'true').lower() == 'true'
    PASSWORD_REQUIRE_LOWERCASE = os.environ.get('PASSWORD_REQUIRE_LOWERCASE', 'true').lower() == 'true'
    PASSWORD_REQUIRE_NUMBERS = os.environ.get('PASSWORD_REQUIRE_NUMBERS', 'true').lower() == 'true'
    PASSWORD_REQUIRE_SPECIAL = os.environ.get('PASSWORD_REQUIRE_SPECIAL', 'true').lower() == 'true'

    # Account security
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
    ACCOUNT_LOCKOUT_MINUTES = int(os.environ.get('ACCOUNT_LOCKOUT_MINUTES', 15))


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