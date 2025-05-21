#!/usr/bin/env python3
# SecureScout - Nikto Adapter Test

import os
import sys
import unittest
import json
import logging
from unittest.mock import patch, MagicMock

# Add parent directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import modules to test
from modules.integrations.nikto_adapter import NiktoAdapter, NIKTO_CATEGORIES, NIKTO_ID_MAPPINGS
from modules.integrations.adapter_base import Severity, ToolResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestNiktoAdapter(unittest.TestCase):
    """Test case for Nikto adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.adapter = NiktoAdapter()
        
        # Load sample data
        self.sample_data_path = os.path.join(
            os.path.dirname(__file__), 
            'test_data', 
            'nikto_sample_output.txt'
        )
        
        with open(self.sample_data_path, 'r') as f:
            self.sample_output = f.read()
    
    def test_initialization(self):
        """Test adapter initialization."""
        self.assertEqual(self.adapter.tool_name, "nikto")
        self.assertIsNone(self.adapter.result)
    
    def test_command_preparation(self):
        """Test command preparation with different options."""
        # Basic options
        options = {
            "host": "example.com",
            "format": "json"
        }
        
        command = self.adapter.prepare_command(options)
        
        # Check that the command contains the expected elements
        self.assertIn("nikto", command)
        self.assertIn("-h example.com", command)
        self.assertIn("-Format json", command)
        
        # More complex options
        options = {
            "host": "example.com",
            "port": [80, 443],
            "tuning": "1234abc",
            "ssl": True,
            "cookies": {"PHPSESSID": "123456789", "session": "abcdef"},
            "headers": {"User-Agent": "Custom User Agent"},
            "pause": 2,
            "max_time": 3600
        }
        
        command = self.adapter.prepare_command(options)
        
        # Check that the command contains the expected elements
        self.assertIn("-h example.com", command)
        self.assertIn("-p 80,443", command)
        self.assertIn("-Tuning 1234abc", command)
        self.assertIn("-ssl", command)
        self.assertIn("-cookies PHPSESSID=123456789; session=abcdef", command)
        self.assertIn('-vhost "User-Agent: Custom User Agent"', command)
        self.assertIn("-Pause 2", command)
        self.assertIn("-maxtime 3600", command)
        
        # Check options for proxy, no SSL, etc.
        options = {
            "host": "example.com",
            "no_ssl_check": True,
            "proxy": "http://proxy.example.com:8080",
            "no_host_lookup": True,
            "debug": True
        }
        
        command = self.adapter.prepare_command(options)
        
        # Check that the command contains the expected elements
        self.assertIn("-nossl", command)
        self.assertIn("-proxy http://proxy.example.com:8080", command)
        self.assertIn("-nolookup", command)
        self.assertIn("-debug", command)
    
    def test_output_parsing(self):
        """Test parsing of Nikto output."""
        findings = self.adapter.parse_output(self.sample_output)
        
        # Check that findings were extracted
        self.assertGreater(len(findings), 0)
        
        # Check that the number of findings is correct (from sample data)
        self.assertEqual(len(findings), 13)
        
        # Check first finding
        first_finding = findings[0]
        self.assertIn("title", first_finding)
        self.assertIn("severity", first_finding)
        self.assertIn("description", first_finding)
        self.assertIn("test_id", first_finding)
        self.assertIn("evidence", first_finding)
        self.assertIn("remediation", first_finding)
        
        # Check that the evidence contains expected information
        evidence = first_finding["evidence"]
        self.assertIn("host", evidence)
        self.assertIn("ip", evidence)
        self.assertIn("port", evidence)
        self.assertIn("method", evidence)
        self.assertIn("url", evidence)
        
        # Check that the severity is a valid value
        self.assertIn(first_finding["severity"], [
            Severity.CRITICAL, 
            Severity.HIGH, 
            Severity.MEDIUM, 
            Severity.LOW, 
            Severity.INFO, 
            Severity.UNKNOWN
        ])
        
        # Check that specific findings have the expected severity
        rce_finding = None
        sqli_finding = None
        info_finding = None
        
        for finding in findings:
            if finding["test_id"] == "009673":  # Remote command execution
                rce_finding = finding
            elif finding["test_id"] == "009532":  # SQL injection
                sqli_finding = finding
            elif finding["test_id"] == "999986":  # Missing header (info)
                info_finding = finding
        
        # Check RCE finding severity
        if rce_finding:
            self.assertEqual(rce_finding["severity"], Severity.CRITICAL)
        
        # Check SQL injection finding severity
        if sqli_finding:
            self.assertEqual(sqli_finding["severity"], Severity.HIGH)
        
        # Check info finding severity
        if info_finding:
            self.assertEqual(info_finding["severity"], Severity.INFO)
    
    def test_severity_determination(self):
        """Test severity determination based on test ID."""
        # Test specific ID mappings
        self.assertEqual(self.adapter._determine_severity("009673"), Severity.CRITICAL)  # RCE
        self.assertEqual(self.adapter._determine_severity("009532"), Severity.HIGH)      # SQLi
        self.assertEqual(self.adapter._determine_severity("001328"), Severity.MEDIUM)    # Admin login page
        self.assertEqual(self.adapter._determine_severity("999986"), Severity.INFO)      # Missing header
        
        # Test ID ranges (based on category heuristics)
        self.assertEqual(self.adapter._determine_severity("005000"), Severity.MEDIUM)    # Based on ID range
        self.assertEqual(self.adapter._determine_severity("008000"), Severity.HIGH)      # Based on ID range
    
    def test_generate_title(self):
        """Test title generation."""
        # Test title generation with a short message
        message = "Short message"
        test_id = "123456"
        title = self.adapter._generate_title(message, test_id)
        self.assertEqual(title, "Nikto #123456: Short message")
        
        # Test title generation with a long message
        long_message = "This is a very long message that exceeds the 60 character limit for titles in the Nikto adapter implementation"
        test_id = "654321"
        title = self.adapter._generate_title(long_message, test_id)
        self.assertEqual(len(title), 71)  # 60 chars + "Nikto #654321: " + "..."
        self.assertTrue(title.endswith("..."))
    
    def test_get_remediation(self):
        """Test remediation advice generation."""
        # Test SQL injection remediation
        sqli_message = "SQL injection might be possible in the 'id' parameter."
        sqli_id = "009532"
        remediation = self.adapter._get_remediation(sqli_id, sqli_message)
        self.assertIn("parameterized queries", remediation.lower())
        
        # Test missing header remediation
        header_message = "The 'X-XSS-Protection' header is not defined."
        header_id = "999986"
        remediation = self.adapter._get_remediation(header_id, header_message)
        self.assertIn("configure the web server", remediation.lower())
    
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
            "host": "example.com",
            "format": "json",
            "tuning": "1234abc"
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


if __name__ == '__main__':
    unittest.main()