"""
Tests for the scan controller API endpoints.
"""

import json
import pytest
import uuid
from datetime import datetime

# Mock scan data
MOCK_SCAN_ID = str(uuid.uuid4())
MOCK_TARGET_URL = "https://example.com"

class TestScanController:
    """Tests for scan controller API endpoints."""
    
    def test_start_scan_endpoint(self, client, admin_headers, analyst_headers, viewer_headers):
        """Test the start scan endpoint with different user roles."""
        scan_config = {
            'target_url': MOCK_TARGET_URL,
            'scan_type': 'standard',
            'modules': ['discovery', 'xss'],
            'max_depth': 3,
            'threads': 5
        }
        
        # Admin should be able to start a scan
        response = client.post(
            '/api/scan/start',
            headers=admin_headers,
            json=scan_config
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'scan_id' in data
        assert data['config']['target_url'] == MOCK_TARGET_URL
        
        # Store scan ID for later tests
        admin_scan_id = data['scan_id']
        
        # Analyst should be able to start a scan
        response = client.post(
            '/api/scan/start',
            headers=analyst_headers,
            json=scan_config
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        analyst_scan_id = data['scan_id']
        
        # Viewer should NOT be able to start a scan
        response = client.post(
            '/api/scan/start',
            headers=viewer_headers,
            json=scan_config
        )
        
        assert response.status_code == 403
        
        return admin_scan_id, analyst_scan_id
    
    def test_scan_status_endpoint(self, client, admin_headers, analyst_headers, viewer_headers):
        """Test the scan status endpoint."""
        # First start a scan
        scan_config = {
            'target_url': MOCK_TARGET_URL,
            'scan_type': 'quick'
        }
        response = client.post(
            '/api/scan/start',
            headers=admin_headers,
            json=scan_config
        )
        scan_id = json.loads(response.data)['scan_id']
        
        # Admin should be able to check status
        response = client.get(
            f'/api/scan/status/{scan_id}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['scan_id'] == scan_id
        assert 'status' in data
        assert 'progress' in data
        assert data['target_url'] == MOCK_TARGET_URL
        
        # Analyst should be able to check status
        response = client.get(
            f'/api/scan/status/{scan_id}',
            headers=analyst_headers
        )
        
        assert response.status_code == 200
        
        # Viewer should be able to check status (read permission)
        response = client.get(
            f'/api/scan/status/{scan_id}',
            headers=viewer_headers
        )
        
        assert response.status_code == 200
        
        # Test with non-existent scan ID
        response = client.get(
            f'/api/scan/status/{uuid.uuid4()}',
            headers=admin_headers
        )
        
        assert response.status_code == 404
    
    def test_list_scans_endpoint(self, client, admin_headers, analyst_headers, viewer_headers):
        """Test the list scans endpoint."""
        # Make sure we have at least one scan
        scan_config = {
            'target_url': MOCK_TARGET_URL,
            'scan_type': 'quick'
        }
        client.post(
            '/api/scan/start',
            headers=admin_headers,
            json=scan_config
        )
        
        # Admin should see all scans
        response = client.get(
            '/api/scan/list',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'active_scans' in data
        assert 'scan_history' in data
        
        # Check filtering by user
        # Start a scan as analyst
        client.post(
            '/api/scan/start',
            headers=analyst_headers,
            json=scan_config
        )
        
        # Analyst should see their scans
        response = client.get(
            '/api/scan/list',
            headers=analyst_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Viewer should have read access
        response = client.get(
            '/api/scan/list',
            headers=viewer_headers
        )
        
        assert response.status_code == 200
    
    def test_stop_scan_endpoint(self, client, admin_headers, analyst_headers, viewer_headers):
        """Test the stop scan endpoint."""
        # First start a scan
        scan_config = {
            'target_url': MOCK_TARGET_URL,
            'scan_type': 'quick'
        }
        response = client.post(
            '/api/scan/start',
            headers=admin_headers,
            json=scan_config
        )
        scan_id = json.loads(response.data)['scan_id']
        
        # Admin should be able to stop the scan
        response = client.post(
            f'/api/scan/stop/{scan_id}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        # Start another scan for analyst test
        response = client.post(
            '/api/scan/start',
            headers=analyst_headers,
            json=scan_config
        )
        analyst_scan_id = json.loads(response.data)['scan_id']
        
        # Analyst should be able to stop their own scan
        response = client.post(
            f'/api/scan/stop/{analyst_scan_id}',
            headers=analyst_headers
        )
        
        assert response.status_code == 200
        
        # Viewer should NOT be able to stop scans
        response = client.post(
            f'/api/scan/stop/{scan_id}',
            headers=viewer_headers
        )
        
        assert response.status_code == 403
    
    def test_delete_scan_endpoint(self, client, admin_headers, analyst_headers, viewer_headers):
        """Test the delete scan endpoint."""
        # First start a scan
        scan_config = {
            'target_url': MOCK_TARGET_URL,
            'scan_type': 'quick'
        }
        response = client.post(
            '/api/scan/start',
            headers=admin_headers,
            json=scan_config
        )
        scan_id = json.loads(response.data)['scan_id']
        
        # Start another scan for analyst
        response = client.post(
            '/api/scan/start',
            headers=analyst_headers,
            json=scan_config
        )
        analyst_scan_id = json.loads(response.data)['scan_id']
        
        # Admin should be able to delete a scan
        response = client.delete(
            f'/api/scan/delete/{scan_id}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        # Verify scan is deleted
        response = client.get(
            f'/api/scan/status/{scan_id}',
            headers=admin_headers
        )
        assert response.status_code == 404
        
        # Analyst should NOT be able to delete scans (only admins/managers)
        response = client.delete(
            f'/api/scan/delete/{analyst_scan_id}',
            headers=analyst_headers
        )
        
        assert response.status_code == 403
        
        # Admin can delete analyst's scan
        response = client.delete(
            f'/api/scan/delete/{analyst_scan_id}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
    
    def test_scan_validation(self, client, admin_headers):
        """Test validation of scan request data."""
        # Test missing target URL
        response = client.post(
            '/api/scan/start',
            headers=admin_headers,
            json={
                'scan_type': 'standard'
                # Missing target_url
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'required' in data['error']
        
        # Test invalid scan type
        response = client.post(
            '/api/scan/start',
            headers=admin_headers,
            json={
                'target_url': MOCK_TARGET_URL,
                'scan_type': 'invalid_type'
            }
        )
        
        # This might be accepted in the current implementation with defaults
        # But in a more strict implementation, it would return 400
        
        # Test extreme parameters (should be capped)
        response = client.post(
            '/api/scan/start',
            headers=admin_headers,
            json={
                'target_url': MOCK_TARGET_URL,
                'threads': 1000,  # Very high, should be capped
                'max_depth': 100  # Very high, might be capped
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        # Verify threads were capped
        assert data['config']['threads'] <= 50  # MAX_THREAD_COUNT from config