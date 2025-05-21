#!/usr/bin/env python3
# SecureScout - SQLMap Adapter Test

import os
import sys
import unittest
import json
import logging
from unittest.mock import patch, MagicMock

# Add parent directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import modules to test
from modules.integrations.sqlmap_adapter import SQLMapAdapter, SQLMapAPI
from modules.integrations.adapter_base import Severity, ToolResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestSQLMapAdapter(unittest.TestCase):
    """Test case for SQLMap adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.adapter = SQLMapAdapter()
        
        # Load sample data
        self.sample_data_path = os.path.join(
            os.path.dirname(__file__), 
            'test_data', 
            'sqlmap_sample_output.txt'
        )
        
        with open(self.sample_data_path, 'r') as f:
            self.sample_output = f.read()
    
    def test_initialization(self):
        """Test adapter initialization."""
        self.assertEqual(self.adapter.tool_name, "sqlmap")
        self.assertIsNone(self.adapter.result)
    
    def test_command_preparation(self):
        """Test command preparation with different options."""
        # Basic options
        options = {
            "url": "http://example.com/page.php?id=1",
            "level": 1,
            "risk": 1
        }
        
        command = self.adapter.prepare_command(options)
        
        # Check that the command contains the expected elements
        self.assertIn("sqlmap", command)
        self.assertIn("-u http://example.com/page.php?id=1", command)
        self.assertIn("--level=1", command)
        self.assertIn("--risk=1", command)
        
        # More complex options
        options = {
            "url": "http://example.com/login.php",
            "data": "username=test&password=test",
            "cookies": "PHPSESSID=123456789",
            "level": 2,
            "risk": 2,
            "techniques": "BEUST",
            "extra_args": "--tamper=space2comment"
        }
        
        command = self.adapter.prepare_command(options)
        
        # Check that the command contains the expected elements
        self.assertIn("-u http://example.com/login.php", command)
        self.assertIn('--data="username=test&password=test"', command)
        self.assertIn('--cookie="PHPSESSID=123456789"', command)
        self.assertIn("--level=2", command)
        self.assertIn("--risk=2", command)
        self.assertIn("--technique=BEUST", command)
        self.assertIn("--tamper=space2comment", command)
    
    def test_output_parsing(self):
        """Test parsing of SQLMap output."""
        findings = self.adapter.parse_output(self.sample_output)
        
        # Check that findings were extracted
        self.assertGreater(len(findings), 0)
        
        # Check first finding
        first_finding = findings[0]
        self.assertIn("title", first_finding)
        self.assertIn("severity", first_finding)
        self.assertIn("description", first_finding)
        self.assertIn("evidence", first_finding)
        
        # Check that the evidence contains expected information
        evidence = first_finding["evidence"]
        self.assertIn("parameter", evidence)
        self.assertIn("injection_type", evidence)
        self.assertIn("database_type", evidence)
        
        # Check that the severity is a valid value
        self.assertIn(first_finding["severity"], [
            Severity.CRITICAL, 
            Severity.HIGH, 
            Severity.MEDIUM, 
            Severity.LOW, 
            Severity.INFO
        ])
        
        # Check that UNION-based SQL injection is reported as high severity
        union_finding = None
        for finding in findings:
            if "UNION" in finding["evidence"]["injection_type"]:
                union_finding = finding
                break
        
        if union_finding:
            self.assertEqual(union_finding["severity"], Severity.HIGH)
    
    @patch('subprocess.Popen')
    def test_execute(self, mock_popen):
        """Test execute method."""
        # Mock the subprocess.Popen return value
        mock_process = MagicMock()
        mock_process.communicate.return_value = (self.sample_output, "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Execute the adapter
        options = {
            "url": "http://example.com/page.php?id=1",
            "level": 1,
            "risk": 1
        }
        
        result = self.adapter.execute(options)
        
        # Check that the result is a ToolResult object
        self.assertIsInstance(result, ToolResult)
        
        # Check that the result has the expected status
        self.assertEqual(result.status, "completed")
        
        # Check that findings were extracted
        self.assertGreater(len(result.parsed_findings), 0)
        
        # Verify that subprocess.Popen was called
        mock_popen.assert_called_once()
        
        # Check error handling
        mock_process.returncode = 1
        mock_process.communicate.return_value = ("", "Error message")
        
        result = self.adapter.execute(options)
        
        # Check that the result has the expected status
        self.assertEqual(result.status, "failed")
        self.assertIsNotNone(result.error_message)
    
    @patch('modules.integrations.sqlmap_adapter.SQLMapAPI')
    def test_api_execution(self, mock_api_class):
        """Test execution through SQLMap API."""
        # Create a SQLMap adapter with API enabled
        api_adapter = SQLMapAdapter(use_api=True)
        
        # Mock the API client
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        
        # Mock API methods
        mock_api.start_server.return_value = True
        mock_api.new_task.return_value = "task123"
        mock_api.set_option.return_value = True
        mock_api.start_scan.return_value = True
        mock_api.get_status.side_effect = ["running", "terminated"]
        
        # Create sample API data
        sample_api_data = {
            "http://example.com": {
                "dbms": "MySQL",
                "GET": {
                    "id": {
                        "UNION query": {
                            "title": "Generic UNION query",
                            "payload": "id=1 UNION ALL SELECT NULL,NULL,NULL"
                        }
                    }
                }
            }
        }
        
        mock_api.get_data.return_value = sample_api_data
        
        # Execute the adapter through API
        options = {
            "url": "http://example.com/page.php?id=1",
            "level": 1,
            "risk": 1
        }
        
        result = api_adapter.execute_api(options)
        
        # Check that the result is a ToolResult object
        self.assertIsInstance(result, ToolResult)
        
        # Check that the result has the expected status
        self.assertEqual(result.status, "completed")
        
        # Check that findings were extracted
        self.assertGreater(len(result.parsed_findings), 0)
        
        # Verify that API methods were called
        mock_api.start_server.assert_called_once()
        mock_api.new_task.assert_called_once()
        mock_api.set_option.assert_called()
        mock_api.start_scan.assert_called_once()
        mock_api.get_status.assert_called()
        mock_api.get_data.assert_called_once()
        
        # Test error handling
        mock_api.reset_mock()
        mock_api.start_scan.return_value = False
        
        result = api_adapter.execute_api(options)
        
        # Check that the result has the expected status
        self.assertEqual(result.status, "failed")
        self.assertIsNotNone(result.error_message)


class TestSQLMapAPI(unittest.TestCase):
    """Test case for SQLMap API client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = SQLMapAPI()
    
    @patch('requests.get')
    def test_server_status_check(self, mock_get):
        """Test server status check."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Check that the server is running
        self.assertTrue(self.api.start_server())
        
        # Verify that requests.get was called with the expected URL
        mock_get.assert_called_with("http://127.0.0.1:8775/status", timeout=2)
    
    @patch('requests.get')
    def test_new_task(self, mock_get):
        """Test creating a new task."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "taskid": "task123"
        }
        mock_get.return_value = mock_response
        
        # Create a new task
        task_id = self.api.new_task()
        
        # Check that the task_id is correct
        self.assertEqual(task_id, "task123")
        
        # Verify that requests.get was called with the expected URL
        mock_get.assert_called_with("http://127.0.0.1:8775/task/new")


if __name__ == '__main__':
    unittest.main()