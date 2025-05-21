"""
SecureScout Test Configuration

This module provides pytest fixtures and configuration for testing SecureScout.
"""

import os
import sys
import pytest
import tempfile
import sqlite3
from flask import Flask
from datetime import datetime, timedelta

# Add backend directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import app as flask_app
from backend.modules.auth.auth_manager import create_auth_manager, UserRole

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary file to use as the test database
    db_fd, db_path = tempfile.mkstemp()
    
    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-key',
        'JWT_SECRET_KEY': 'test-jwt-key',
        'DATABASE_URI': f'sqlite:///{db_path}',
        'REDIS_URL': 'redis://localhost:6379/1',  # Use a different Redis DB for testing
        'CREATE_DEFAULT_ADMIN': True,
        'DEFAULT_ADMIN_USERNAME': 'admin',
        'DEFAULT_ADMIN_PASSWORD': 'TestPassword123!',
        'DEFAULT_ADMIN_EMAIL': 'admin@test.com',
        'ALLOW_SELF_REGISTRATION': True
    })
    
    # Create required test directories
    os.makedirs('test_data', exist_ok=True)
    os.makedirs('test_logs', exist_ok=True)
    os.makedirs('test_reports', exist_ok=True)
    
    # Initialize the app for testing
    with flask_app.app_context():
        # The app will initialize itself during requests
        pass
    
    yield flask_app
    
    # Clean up temporary dirs and database
    os.close(db_fd)
    os.unlink(db_path)
    os.system('rm -rf test_data test_logs test_reports')

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_auth_manager():
    """Create an auth manager for testing."""
    config = {
        'jwt_secret_key': 'test-jwt-key',
        'access_token_lifetime_minutes': 30,
        'refresh_token_lifetime_days': 7,
        'create_default_admin': True,
        'default_admin_username': 'admin',
        'default_admin_password': 'TestPassword123!',
        'default_admin_email': 'admin@test.com'
    }
    return create_auth_manager(config)

@pytest.fixture
def admin_user(test_auth_manager):
    """Create an admin user for testing."""
    return test_auth_manager.user_manager.get_user('admin')

@pytest.fixture
def analyst_user(test_auth_manager):
    """Create an analyst user for testing."""
    success, user, _ = test_auth_manager.user_manager.create_user(
        username='analyst',
        email='analyst@test.com',
        password='TestPassword123!',
        role=UserRole.ANALYST
    )
    return user if success else None

@pytest.fixture
def viewer_user(test_auth_manager):
    """Create a viewer user for testing."""
    success, user, _ = test_auth_manager.user_manager.create_user(
        username='viewer',
        email='viewer@test.com',
        password='TestPassword123!',
        role=UserRole.VIEWER
    )
    return user if success else None

@pytest.fixture
def admin_tokens(test_auth_manager, admin_user):
    """Get tokens for the admin user."""
    success, tokens, _ = test_auth_manager.login('admin', 'TestPassword123!')
    return tokens if success else None

@pytest.fixture
def analyst_tokens(test_auth_manager):
    """Get tokens for an analyst user."""
    success, tokens, _ = test_auth_manager.login('analyst', 'TestPassword123!')
    return tokens if success else None

@pytest.fixture
def viewer_tokens(test_auth_manager):
    """Get tokens for a viewer user."""
    success, tokens, _ = test_auth_manager.login('viewer', 'TestPassword123!')
    return tokens if success else None

@pytest.fixture
def admin_headers(admin_tokens):
    """Get HTTP headers for the admin user."""
    return {'Authorization': f'Bearer {admin_tokens["access_token"]}'}

@pytest.fixture
def analyst_headers(analyst_tokens):
    """Get HTTP headers for an analyst user."""
    return {'Authorization': f'Bearer {analyst_tokens["access_token"]}'}

@pytest.fixture
def viewer_headers(viewer_tokens):
    """Get HTTP headers for a viewer user."""
    return {'Authorization': f'Bearer {viewer_tokens["access_token"]}'}

@pytest.fixture
def test_scan():
    """Create a test scan object."""
    return {
        'id': 'test-scan-id',
        'target_url': 'https://example.com',
        'scan_type': 'standard',
        'modules': ['discovery', 'xss'],
        'start_time': datetime.utcnow().isoformat(),
        'status': 'completed',
        'progress': 100,
        'findings': [
            {
                'id': 'finding-1',
                'type': 'xss',
                'severity': 'high',
                'name': 'Reflected XSS',
                'description': 'Reflected XSS vulnerability found',
                'url': 'https://example.com/search?q=test',
                'evidence': '<script>alert(1)</script>',
                'remediation': 'Encode user input before displaying it'
            },
            {
                'id': 'finding-2',
                'type': 'information_disclosure',
                'severity': 'medium',
                'name': 'Server Information Disclosure',
                'description': 'Server reveals version information',
                'url': 'https://example.com',
                'evidence': 'Apache/2.4.41 (Ubuntu)',
                'remediation': 'Configure server to hide version information'
            }
        ]
    }

@pytest.fixture
def mock_memory_adapter(monkeypatch):
    """Mock the memory adapter for testing."""
    class MockMemoryAdapter:
        def __init__(self):
            self.data = {}
        
        def get(self, key):
            return self.data.get(key)
        
        def set(self, key, value):
            self.data[key] = value
            return True
        
        def delete(self, key):
            if key in self.data:
                del self.data[key]
                return True
            return False
        
        def list_keys(self, prefix=None):
            if prefix:
                return [k for k in self.data.keys() if k.startswith(prefix)]
            return list(self.data.keys())
        
        def clear(self):
            self.data.clear()
            return True
    
    adapter = MockMemoryAdapter()
    
    # Here we'd monkeypatch the actual memory adapter
    # This depends on how the memory adapter is imported in the code
    
    return adapter