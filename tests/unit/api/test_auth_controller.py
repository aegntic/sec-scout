"""
Tests for the auth controller API endpoints.
"""

import json
import pytest
from flask import url_for

class TestAuthController:
    """Tests for auth controller API endpoints."""
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get('/api/health')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'ok'
    
    def test_login_endpoint(self, client, test_auth_manager):
        """Test the login endpoint."""
        # First ensure admin user exists
        admin = test_auth_manager.user_manager.get_user('admin')
        assert admin is not None
        
        # Test login with correct credentials
        response = client.post(
            '/api/auth/login',
            json={
                'username': 'admin',
                'password': 'TestPassword123!'
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'admin'
        
        # Test login with incorrect password
        response = client.post(
            '/api/auth/login',
            json={
                'username': 'admin',
                'password': 'WrongPassword'
            }
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_register_endpoint(self, client):
        """Test the user registration endpoint."""
        # Test registration with valid data
        response = client.post(
            '/api/auth/register',
            json={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'StrongP@ssw0rd123'
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'message' in data
        assert data['user']['username'] == 'newuser'
        
        # Test registration with existing username
        response = client.post(
            '/api/auth/register',
            json={
                'username': 'newuser',
                'email': 'another@example.com',
                'password': 'StrongP@ssw0rd123'
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'exists' in data['error']
    
    def test_refresh_token_endpoint(self, client, admin_tokens):
        """Test the token refresh endpoint."""
        # Test refreshing with valid token
        response = client.post(
            '/api/auth/refresh',
            json={
                'refresh_token': admin_tokens['refresh_token']
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['access_token'] != admin_tokens['access_token']
        
        # Test refreshing with invalid token
        response = client.post(
            '/api/auth/refresh',
            json={
                'refresh_token': 'invalid-token'
            }
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_logout_endpoint(self, client, admin_tokens):
        """Test the logout endpoint."""
        response = client.post(
            '/api/auth/logout',
            json={
                'refresh_token': admin_tokens['refresh_token']
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        
        # After logout, refresh token should no longer work
        response = client.post(
            '/api/auth/refresh',
            json={
                'refresh_token': admin_tokens['refresh_token']
            }
        )
        
        assert response.status_code == 401
    
    def test_profile_endpoint(self, client, admin_headers):
        """Test the user profile endpoint."""
        response = client.get(
            '/api/auth/profile',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'admin'
        assert 'email' in data
        assert 'role' in data
        
        # Test without auth header
        response = client.get('/api/auth/profile')
        assert response.status_code == 401
    
    def test_users_list_endpoint(self, client, admin_headers, viewer_headers):
        """Test the users list endpoint with different permissions."""
        # Admin should be able to list users
        response = client.get(
            '/api/auth/users',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Viewer should not be able to list users
        response = client.get(
            '/api/auth/users',
            headers=viewer_headers
        )
        
        assert response.status_code == 403
    
    def test_user_create_endpoint(self, client, admin_headers, viewer_headers):
        """Test the user creation endpoint with different permissions."""
        # Admin should be able to create users
        response = client.post(
            '/api/auth/users',
            headers=admin_headers,
            json={
                'username': 'createduser',
                'email': 'created@example.com',
                'password': 'StrongP@ssw0rd123',
                'role': 'ANALYST'
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['user']['username'] == 'createduser'
        assert data['user']['role'] == 'ANALYST'
        
        # Viewer should not be able to create users
        response = client.post(
            '/api/auth/users',
            headers=viewer_headers,
            json={
                'username': 'anotheruser',
                'email': 'another@example.com',
                'password': 'StrongP@ssw0rd123',
                'role': 'VIEWER'
            }
        )
        
        assert response.status_code == 403
    
    def test_user_update_endpoint(self, client, admin_headers, admin_user):
        """Test the user update endpoint."""
        response = client.put(
            f'/api/auth/users/{admin_user.username}',
            headers=admin_headers,
            json={
                'email': 'updated@example.com'
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['email'] == 'updated@example.com'
    
    def test_password_update_endpoint(self, client, admin_headers, admin_user):
        """Test the password update endpoint."""
        response = client.put(
            f'/api/auth/users/{admin_user.username}/password',
            headers=admin_headers,
            json={
                'current_password': 'TestPassword123!',
                'new_password': 'NewPassword456!'
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        
        # Verify new password works
        response = client.post(
            '/api/auth/login',
            json={
                'username': admin_user.username,
                'password': 'NewPassword456!'
            }
        )
        
        assert response.status_code == 200
    
    def test_api_key_endpoints(self, client, admin_headers, admin_user):
        """Test the API key endpoints."""
        # Create an API key
        response = client.post(
            f'/api/auth/users/{admin_user.username}/api-keys',
            headers=admin_headers,
            json={
                'name': 'Test API Key',
                'expires_in_days': 30
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'api_key' in data
        assert data['metadata']['name'] == 'Test API Key'
        
        api_key = data['api_key']
        key_id = data['metadata']['id']
        
        # List API keys
        response = client.get(
            f'/api/auth/users/{admin_user.username}/api-keys',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Use API key for authentication
        response = client.get(
            '/api/auth/profile',
            headers={'X-API-Key': api_key}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == admin_user.username
        
        # Revoke API key
        response = client.delete(
            f'/api/auth/users/{admin_user.username}/api-keys/{key_id}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        
        # Verify revoked key doesn't work
        response = client.get(
            '/api/auth/profile',
            headers={'X-API-Key': api_key}
        )
        
        assert response.status_code == 401
    
    def test_roles_endpoint(self, client, admin_headers):
        """Test the roles endpoint."""
        response = client.get(
            '/api/auth/roles',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert 'ADMIN' in data
        assert 'ANALYST' in data
        assert 'VIEWER' in data
    
    def test_setup_status_endpoint(self, client):
        """Test the setup status endpoint."""
        response = client.get('/api/auth/setup-status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'setup_complete' in data
        assert data['setup_complete'] is True  # Because we have an admin user