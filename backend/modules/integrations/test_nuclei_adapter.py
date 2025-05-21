#!/usr/bin/env python3
# SecureScout - Nuclei Adapter Test

import os
import sys
import unittest
import json
import logging
from unittest.mock import patch, MagicMock

# Add parent directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import modules to test
from modules.integrations.nuclei_adapter import NucleiAdapter, NucleiTemplateManager
from modules.integrations.adapter_base import Severity, ToolResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestNucleiAdapter(unittest.TestCase):
    """Test case for Nuclei adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.adapter = NucleiAdapter()
        
        # Load sample data
        self.sample_data_path = os.path.join(
            os.path.dirname(__file__), 
            'test_data', 
            'nuclei_sample_output.txt'
        )
        
        with open(self.sample_data_path, 'r') as f:
            self.sample_output = f.read()
    
    def test_initialization(self):
        """Test adapter initialization."""
        self.assertEqual(self.adapter.tool_name, "nuclei")
        self.assertIsNone(self.adapter.result)
        self.assertIsNone(self.adapter.template_manager)
    
    def test_command_preparation(self):
        """Test command preparation with different options."""
        # Basic options with URL
        options = {
            "url": "https://example.com",
            "tags": "cve,oast",
            "severity": ["critical", "high"]
        }
        
        # Initialize template manager for command preparation
        self.adapter.initialize_template_manager()
        
        command = self.adapter.prepare_command(options)
        
        # Check that the command contains the expected elements
        self.assertIn("nuclei", command)
        self.assertIn("-u https://example.com", command)
        self.assertIn("-tags cve,oast", command)
        self.assertIn("-severity critical,high", command)
        self.assertIn("-json", command)  # Always use JSON output for parsing
        
        # Options with URL file
        options = {
            "urls_file": "/path/to/urls.txt",
            "tags": "cve,oast",
            "severity": ["critical", "high", "medium"],
            "rate_limit": 200,
            "include_request_response": True,
            "extra_args": "-headless"
        }
        
        command = self.adapter.prepare_command(options)
        
        # Check that the command contains the expected elements
        self.assertIn("-l /path/to/urls.txt", command)
        self.assertIn("-tags cve,oast", command)
        self.assertIn("-severity critical,high,medium", command)
        self.assertIn("-rate-limit 200", command)
        self.assertIn("-irr", command)
        self.assertIn("-headless", command)
        
        # Options with templates
        options = {
            "url": "https://example.com",
            "templates": ["/path/to/template1.yaml", "/path/to/template2.yaml"]
        }
        
        command = self.adapter.prepare_command(options)
        
        # Check that the command contains the expected elements
        self.assertIn("-t /path/to/template1.yaml,/path/to/template2.yaml", command)
    
    def test_output_parsing(self):
        """Test parsing of Nuclei output."""
        findings = self.adapter.parse_output(self.sample_output)
        
        # Check that findings were extracted
        self.assertGreater(len(findings), 0)
        
        # Check that we have 5 findings (from sample data)
        self.assertEqual(len(findings), 5)
        
        # Check first finding
        first_finding = findings[0]
        self.assertIn("title", first_finding)
        self.assertIn("severity", first_finding)
        self.assertIn("description", first_finding)
        self.assertIn("template_id", first_finding)
        self.assertIn("host", first_finding)
        self.assertIn("url", first_finding)
        self.assertIn("tags", first_finding)
        self.assertIn("evidence", first_finding)
        
        # Check that severity is properly normalized
        self.assertIn(first_finding["severity"], [
            Severity.CRITICAL, 
            Severity.HIGH, 
            Severity.MEDIUM, 
            Severity.LOW, 
            Severity.INFO, 
            Severity.UNKNOWN
        ])
        
        # Check that critical vulnerabilities are properly recognized
        cve_finding = None
        for finding in findings:
            if "cve-" in finding["template_id"].lower():
                cve_finding = finding
                break
        
        if cve_finding:
            self.assertEqual(cve_finding["severity"], Severity.CRITICAL)
        
        # Check that template_id matches expected value
        self.assertEqual(first_finding["template_id"], "cve-2023-36664-oracle-fusion-middleware")
        
        # Check directory listing severity (should be low)
        directory_listing_finding = None
        for finding in findings:
            if "directory-listing" in finding["template_id"].lower():
                directory_listing_finding = finding
                break
        
        if directory_listing_finding:
            self.assertEqual(directory_listing_finding["severity"], Severity.LOW)
    
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
            "url": "https://example.com",
            "tags": "cve,oast",
            "severity": ["critical", "high"]
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


class TestNucleiTemplateManager(unittest.TestCase):
    """Test case for Nuclei template manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.nuclei_executable = "/usr/bin/nuclei"
        self.custom_templates_dir = "/tmp/nuclei-templates"
        self.template_manager = NucleiTemplateManager(self.nuclei_executable, self.custom_templates_dir)
    
    @patch('os.path.exists')
    @patch('os.walk')
    @patch('builtins.open')
    @patch('yaml.safe_load')
    def test_list_templates(self, mock_yaml_load, mock_open, mock_walk, mock_exists):
        """Test listing templates."""
        # Mock os.path.exists to return True for template directories
        mock_exists.return_value = True
        
        # Mock os.walk to return template files
        mock_walk.return_value = [
            (
                "/tmp/nuclei-templates", 
                ["cves", "exposures"], 
                []
            ),
            (
                "/tmp/nuclei-templates/cves", 
                [], 
                ["cve-2023-12345.yaml", "cve-2023-67890.yaml"]
            ),
            (
                "/tmp/nuclei-templates/exposures", 
                [], 
                ["directory-listing.yaml"]
            )
        ]
        
        # Mock file open and yaml.safe_load to return template info
        mock_open.return_value.__enter__.return_value = "mock file content"
        
        # Define mock templates
        mock_templates = [
            {
                "id": "cve-2023-12345",
                "info": {
                    "name": "CVE-2023-12345",
                    "author": "security-researcher",
                    "severity": "critical",
                    "description": "A critical vulnerability",
                    "tags": ["cve", "rce"]
                }
            },
            {
                "id": "cve-2023-67890",
                "info": {
                    "name": "CVE-2023-67890",
                    "author": "security-researcher",
                    "severity": "high",
                    "description": "A high severity vulnerability",
                    "tags": ["cve", "sqli"]
                }
            },
            {
                "id": "directory-listing",
                "info": {
                    "name": "Directory Listing",
                    "author": "security-researcher",
                    "severity": "low",
                    "description": "Directory listing enabled",
                    "tags": ["exposure", "misconfig"]
                }
            }
        ]
        
        # Set up the yaml.safe_load mock to return different templates
        mock_yaml_load.side_effect = mock_templates
        
        # Test listing all templates
        templates = self.template_manager.list_templates()
        
        # Check that templates were found
        self.assertEqual(len(templates), 3)
        
        # Check filtering by tags
        templates = self.template_manager.list_templates(filter_tags=["cve"])
        
        # Check that only CVE templates were returned
        self.assertEqual(len(templates), 2)
        
        # Check filtering by severity
        templates = self.template_manager.list_templates(filter_severity=["critical"])
        
        # Check that only critical templates were returned
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0]["id"], "cve-2023-12345")
    
    @patch('subprocess.run')
    def test_update_templates(self, mock_run):
        """Test updating templates."""
        # Mock successful update
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Update templates
        result = self.template_manager.update_templates()
        
        # Check that the update was successful
        self.assertTrue(result)
        
        # Verify that subprocess.run was called with the expected arguments
        mock_run.assert_called_with(
            [self.nuclei_executable, "-update-templates"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Mock failed update
        mock_process.returncode = 1
        mock_run.return_value = mock_process
        
        # Update templates
        result = self.template_manager.update_templates()
        
        # Check that the update failed
        self.assertFalse(result)
    
    @patch('os.makedirs')
    @patch('builtins.open')
    def test_add_custom_template(self, mock_open, mock_makedirs):
        """Test adding a custom template."""
        # Mock successful template creation
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Template content
        template_content = """
        id: custom-template
        info:
          name: Custom Template
          author: test-user
          severity: medium
          description: A custom template for testing
          tags: [test, custom]
        """
        
        # Add custom template
        template_path = self.template_manager.add_custom_template(
            template_content, 
            "custom-template.yaml"
        )
        
        # Check that the template path is correct
        expected_path = os.path.join(self.custom_templates_dir, "custom-template.yaml")
        self.assertEqual(template_path, expected_path)
        
        # Verify that os.makedirs and open were called
        mock_makedirs.assert_called_with(self.custom_templates_dir, exist_ok=True)
        mock_open.assert_called_with(expected_path, 'w')
        
        # Verify that the template content was written
        mock_file.write.assert_called_with(template_content)


if __name__ == '__main__':
    unittest.main()