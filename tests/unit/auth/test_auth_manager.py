"""
Tests for the auth_manager module.
"""

import pytest
import jwt
from datetime import datetime, timedelta

from backend.modules.auth.auth_manager import create_auth_manager, UserRole

class TestAuthManager:
    """Tests for the AuthManager class."""
    
    def test_create_auth_manager(self, test_auth_manager):
        """Test that an auth manager can be created."""
        assert test_auth_manager is not None
        assert test_auth_manager.user_manager is not None
        assert test_auth_manager.token_manager is not None
    
    def test_user_creation(self, test_auth_manager):
        """Test user creation."""
        success, user, message = test_auth_manager.user_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongP@ssw0rd123",
            role=UserRole.ANALYST
        )
        
        assert success is True
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.ANALYST
    
    def test_user_authentication(self, test_auth_manager):
        """Test user authentication."""
        # First create a user
        test_auth_manager.user_manager.create_user(
            username="authtest",
            email="authtest@example.com",
            password="StrongP@ssw0rd123",
            role=UserRole.VIEWER
        )
        
        # Now authenticate
        success, user, message = test_auth_manager.user_manager.authenticate_user(
            username="authtest",
            password="StrongP@ssw0rd123"
        )
        
        assert success is True
        assert user is not None
        assert user.username == "authtest"
        
        # Test with wrong password
        success, user, message = test_auth_manager.user_manager.authenticate_user(
            username="authtest",
            password="WrongPassword"
        )
        
        assert success is False
        assert user is None
    
    def test_token_generation(self, test_auth_manager):
        """Test token generation and validation."""
        # Create a user
        success, user, _ = test_auth_manager.user_manager.create_user(
            username="tokentest",
            email="token@example.com",
            password="StrongP@ssw0rd123",
            role=UserRole.ANALYST
        )
        
        assert success is True
        
        # Generate tokens
        access_token = test_auth_manager.token_manager.generate_access_token(
            user_id=user.id,
            permissions=user.role.get_permissions()
        )
        
        refresh_token = test_auth_manager.token_manager.generate_refresh_token(
            user_id=user.id
        )
        
        assert access_token is not None
        assert refresh_token is not None
        
        # Validate tokens
        valid, payload, error = test_auth_manager.token_manager.validate_token(access_token)
        assert valid is True
        assert payload is not None
        assert payload['sub'] == user.id
        assert payload['type'] == 'access'
        
        valid, payload, error = test_auth_manager.token_manager.validate_token(refresh_token)
        assert valid is True
        assert payload is not None
        assert payload['sub'] == user.id
        assert payload['type'] == 'refresh'
    
    def test_login_flow(self, test_auth_manager):
        """Test the complete login flow."""
        # Create a user
        test_auth_manager.user_manager.create_user(
            username="logintest",
            email="login@example.com",
            password="StrongP@ssw0rd123",
            role=UserRole.MANAGER
        )
        
        # Login
        success, tokens, message = test_auth_manager.login(
            username="logintest",
            password="StrongP@ssw0rd123"
        )
        
        assert success is True
        assert 'access_token' in tokens
        assert 'refresh_token' in tokens
        assert 'expires_in' in tokens
        
        # Verify the access token
        valid, user, permissions, error = test_auth_manager.verify_access_token(
            tokens['access_token']
        )
        
        assert valid is True
        assert user is not None
        assert user.username == "logintest"
        assert len(permissions) > 0
    
    def test_refresh_token_flow(self, test_auth_manager):
        """Test the token refresh flow."""
        # Create a user and login
        test_auth_manager.user_manager.create_user(
            username="refreshtest",
            email="refresh@example.com",
            password="StrongP@ssw0rd123",
            role=UserRole.VIEWER
        )
        
        success, tokens, _ = test_auth_manager.login(
            username="refreshtest",
            password="StrongP@ssw0rd123"
        )
        
        assert success is True
        
        # Refresh the token
        success, new_tokens, message = test_auth_manager.refresh_token(
            tokens['refresh_token']
        )
        
        assert success is True
        assert 'access_token' in new_tokens
        assert 'refresh_token' in new_tokens
        assert new_tokens['access_token'] != tokens['access_token']
        assert new_tokens['refresh_token'] != tokens['refresh_token']
    
    def test_logout(self, test_auth_manager):
        """Test the logout flow."""
        # Create a user and login
        test_auth_manager.user_manager.create_user(
            username="logouttest",
            email="logout@example.com",
            password="StrongP@ssw0rd123",
            role=UserRole.VIEWER
        )
        
        success, tokens, _ = test_auth_manager.login(
            username="logouttest",
            password="StrongP@ssw0rd123"
        )
        
        assert success is True
        
        # Logout
        success, message = test_auth_manager.logout(tokens['refresh_token'])
        assert success is True
        
        # Try to use the refresh token after logout (should fail)
        refresh_success, _, _ = test_auth_manager.refresh_token(tokens['refresh_token'])
        assert refresh_success is False
    
    def test_password_policy(self, test_auth_manager):
        """Test password policy enforcement."""
        # Test with weak password (too short)
        success, _, message = test_auth_manager.user_manager.create_user(
            username="weakpass",
            email="weak@example.com",
            password="Weak1!",
            role=UserRole.VIEWER
        )
        
        assert success is False
        assert "must be at least" in message
        
        # Test without uppercase
        success, _, message = test_auth_manager.user_manager.create_user(
            username="noupper",
            email="noupper@example.com",
            password="weakpassword123!",
            role=UserRole.VIEWER
        )
        
        assert success is False
        assert "uppercase" in message
        
        # Test without lowercase
        success, _, message = test_auth_manager.user_manager.create_user(
            username="nolower",
            email="nolower@example.com",
            password="WEAKPASSWORD123!",
            role=UserRole.VIEWER
        )
        
        assert success is False
        assert "lowercase" in message
        
        # Test without numbers
        success, _, message = test_auth_manager.user_manager.create_user(
            username="nonumber",
            email="nonumber@example.com",
            password="WeakPassword!",
            role=UserRole.VIEWER
        )
        
        assert success is False
        assert "number" in message
        
        # Test without special characters
        success, _, message = test_auth_manager.user_manager.create_user(
            username="nospecial",
            email="nospecial@example.com",
            password="WeakPassword123",
            role=UserRole.VIEWER
        )
        
        assert success is False
        assert "special" in message
    
    def test_api_key_management(self, test_auth_manager):
        """Test API key creation and validation."""
        # Create a user
        success, user, _ = test_auth_manager.user_manager.create_user(
            username="apitest",
            email="api@example.com",
            password="StrongP@ssw0rd123",
            role=UserRole.ANALYST
        )
        
        assert success is True
        
        # Create an API key
        api_key, key_metadata = test_auth_manager.user_manager.create_api_key_for_user(
            user=user,
            name="Test API Key"
        )
        
        assert api_key is not None
        assert key_metadata is not None
        assert 'id' in key_metadata
        assert key_metadata['name'] == "Test API Key"
        
        # Verify the API key
        valid, auth_user, message = test_auth_manager.user_manager.authenticate_api_key(api_key)
        
        assert valid is True
        assert auth_user is not None
        assert auth_user.id == user.id
        
        # Test API key revocation
        success = test_auth_manager.user_manager.revoke_api_key(user, key_metadata['id'])
        assert success is True
        
        # Verify revoked API key no longer works
        valid, auth_user, message = test_auth_manager.user_manager.authenticate_api_key(api_key)
        assert valid is False
        assert auth_user is None
    
    def test_user_role_permissions(self, test_auth_manager):
        """Test role-based permissions."""
        # Create users with different roles
        _, admin, _ = test_auth_manager.user_manager.create_user(
            username="permadmin",
            email="permadmin@example.com",
            password="StrongP@ssw0rd123",
            role=UserRole.ADMIN
        )
        
        _, analyst, _ = test_auth_manager.user_manager.create_user(
            username="permanalyst",
            email="permanalyst@example.com",
            password="StrongP@ssw0rd123",
            role=UserRole.ANALYST
        )
        
        _, viewer, _ = test_auth_manager.user_manager.create_user(
            username="permviewer",
            email="permviewer@example.com",
            password="StrongP@ssw0rd123",
            role=UserRole.VIEWER
        )
        
        # Admin should have all permissions
        assert admin.has_permission('user:create') is True
        assert admin.has_permission('user:delete') is True
        assert admin.has_permission('scan:create') is True
        assert admin.has_permission('report:create') is True
        
        # Analyst should have scan and report permissions but not user management
        assert analyst.has_permission('scan:create') is True
        assert analyst.has_permission('report:create') is True
        assert analyst.has_permission('user:create') is False
        assert analyst.has_permission('user:delete') is False
        
        # Viewer should only have read permissions
        assert viewer.has_permission('scan:read') is True
        assert viewer.has_permission('report:read') is True
        assert viewer.has_permission('scan:create') is False
        assert viewer.has_permission('report:create') is False