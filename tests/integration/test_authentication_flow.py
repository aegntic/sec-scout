"""
Integration test for the authentication flow.
"""

import json
import pytest

class TestAuthenticationFlow:
    """Integration test for the complete authentication flow."""
    
    def test_full_auth_flow(self, client):
        """Test the complete authentication flow from registration to using API keys."""
        # Step 1: Register a new user
        register_response = client.post(
            '/api/auth/register',
            json={
                'username': 'integration_user',
                'email': 'integration@example.com',
                'password': 'Integration@123!'
            }
        )
        
        assert register_response.status_code == 201
        register_data = json.loads(register_response.data)
        assert register_data['user']['username'] == 'integration_user'
        
        # Step 2: Login with the new user
        login_response = client.post(
            '/api/auth/login',
            json={
                'username': 'integration_user',
                'password': 'Integration@123!'
            }
        )
        
        assert login_response.status_code == 200
        login_data = json.loads(login_response.data)
        assert 'access_token' in login_data
        assert 'refresh_token' in login_data
        
        access_token = login_data['access_token']
        refresh_token = login_data['refresh_token']
        
        # Create auth headers
        auth_headers = {'Authorization': f'Bearer {access_token}'}
        
        # Step 3: Access protected resource
        profile_response = client.get(
            '/api/auth/profile',
            headers=auth_headers
        )
        
        assert profile_response.status_code == 200
        profile_data = json.loads(profile_response.data)
        assert profile_data['username'] == 'integration_user'
        
        # Step 4: Refresh the token
        refresh_response = client.post(
            '/api/auth/refresh',
            json={'refresh_token': refresh_token}
        )
        
        assert refresh_response.status_code == 200
        refresh_data = json.loads(refresh_response.data)
        assert 'access_token' in refresh_data
        assert refresh_data['access_token'] != access_token
        
        new_access_token = refresh_data['access_token']
        new_refresh_token = refresh_data['refresh_token']
        
        # Update auth headers with new token
        auth_headers = {'Authorization': f'Bearer {new_access_token}'}
        
        # Step 5: Access protected resource with new token
        profile_response = client.get(
            '/api/auth/profile',
            headers=auth_headers
        )
        
        assert profile_response.status_code == 200
        
        # Step 6: Create an API key
        api_key_response = client.post(
            '/api/auth/users/integration_user/api-keys',
            headers=auth_headers,
            json={'name': 'Integration Test Key'}
        )
        
        assert api_key_response.status_code == 201
        api_key_data = json.loads(api_key_response.data)
        assert 'api_key' in api_key_data
        
        api_key = api_key_data['api_key']
        key_id = api_key_data['metadata']['id']
        
        # Step 7: Use API key to access protected resource
        api_key_headers = {'X-API-Key': api_key}
        
        profile_response = client.get(
            '/api/auth/profile',
            headers=api_key_headers
        )
        
        assert profile_response.status_code == 200
        
        # Step 8: Revoke API key
        revoke_response = client.delete(
            f'/api/auth/users/integration_user/api-keys/{key_id}',
            headers=auth_headers
        )
        
        assert revoke_response.status_code == 200
        
        # Step 9: Verify API key no longer works
        profile_response = client.get(
            '/api/auth/profile',
            headers=api_key_headers
        )
        
        assert profile_response.status_code == 401
        
        # Step 10: Logout (revoke refresh token)
        logout_response = client.post(
            '/api/auth/logout',
            json={'refresh_token': new_refresh_token}
        )
        
        assert logout_response.status_code == 200
        
        # Step 11: Verify refresh token no longer works
        refresh_response = client.post(
            '/api/auth/refresh',
            json={'refresh_token': new_refresh_token}
        )
        
        assert refresh_response.status_code == 401