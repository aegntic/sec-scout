#!/usr/bin/env python3
# SecureScout - Integration Adapter Tester
"""
This module provides functionality to test and validate security tool adapters.
It includes tests for adapter initialization, command generation, result parsing,
and complete execution flows.
"""

import os
import sys
import json
import logging
import argparse
import tempfile
from typing import Dict, List, Any, Optional, Type, Tuple
import unittest
from unittest import mock
import datetime

# Add parent directory to path to allow importing adapter modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import adapters
from backend.modules.integrations.adapter_base import BaseToolAdapter, ToolResult, Severity
from backend.modules.integrations.zap_adapter import ZAPAdapter
from backend.modules.integrations.nmap_adapter import NmapAdapter
from backend.modules.integrations.trivy_adapter import TrivyAdapter
from backend.modules.integrations.sqlmap_adapter import SQLMapAdapter, SQLMapAPI
from backend.modules.integrations.nuclei_adapter import NucleiAdapter, NucleiTemplateManager
from backend.modules.integrations.nikto_adapter import NiktoAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('securescout.integrations.tester')


class AdapterTest:
    """
    Base class for adapter tests, providing common functionality.
    """
    
    def __init__(self, adapter_class: Type[BaseToolAdapter], adapter_name: str, sample_options: Dict[str, Any]):
        """
        Initialize the adapter test.
        
        Args:
            adapter_class: Class of the adapter to test
            adapter_name: Name of the adapter for logging
            sample_options: Sample options to use for testing
        """
        self.adapter_class = adapter_class
        self.adapter_name = adapter_name
        self.sample_options = sample_options
        self.adapter_instance = None
        self.test_results = {
            "init": False,
            "command": False,
            "execute": False,
            "parse": False,
            "overall": False,
            "errors": []
        }
    
    def test_initialization(self) -> bool:
        """
        Test adapter initialization.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Testing initialization of {self.adapter_name} adapter")
            self.adapter_instance = self.adapter_class()
            self.test_results["init"] = True
            return True
        except Exception as e:
            logger.error(f"Error initializing {self.adapter_name} adapter: {e}")
            self.test_results["errors"].append(f"Initialization error: {str(e)}")
            return False
    
    def test_command_generation(self) -> bool:
        """
        Test command generation.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.adapter_instance:
            return False
        
        try:
            logger.info(f"Testing command generation for {self.adapter_name} adapter")
            
            # Mock the executable path
            self.adapter_instance.executable_path = f"/usr/bin/{self.adapter_name.lower()}"
            
            # Test with sample options
            command = self.adapter_instance.prepare_command(self.sample_options)
            
            logger.info(f"Generated command: {command}")
            self.test_results["command"] = True
            return True
        except Exception as e:
            logger.error(f"Error generating command with {self.adapter_name} adapter: {e}")
            self.test_results["errors"].append(f"Command generation error: {str(e)}")
            return False
    
    def test_output_parsing(self) -> bool:
        """
        Test output parsing with sample data.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.adapter_instance:
            return False
        
        try:
            logger.info(f"Testing output parsing for {self.adapter_name} adapter")
            
            # Load sample output from file if available
            sample_output = self._load_sample_output()
            
            if not sample_output:
                # Create a synthetic sample output if no file is available
                sample_output = self._generate_sample_output()
            
            # Parse the output
            findings = self.adapter_instance.parse_output(sample_output)
            
            if not findings:
                logger.warning(f"No findings parsed from sample output for {self.adapter_name} adapter")
            else:
                logger.info(f"Successfully parsed {len(findings)} findings from sample output")
            
            self.test_results["parse"] = True
            return True
        except Exception as e:
            logger.error(f"Error parsing output with {self.adapter_name} adapter: {e}")
            self.test_results["errors"].append(f"Output parsing error: {str(e)}")
            return False
    
    def test_execution_flow(self) -> bool:
        """
        Test the full execution flow with mocked subprocess.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.adapter_instance:
            return False
        
        try:
            logger.info(f"Testing execution flow for {self.adapter_name} adapter")
            
            # Mock the subprocess.Popen to avoid actual execution
            with mock.patch('subprocess.Popen') as mock_popen:
                # Configure the mock
                mock_process = mock.MagicMock()
                mock_process.communicate.return_value = (self._generate_sample_output(), "")
                mock_process.returncode = 0
                mock_popen.return_value = mock_process
                
                # Execute the adapter
                result = self.adapter_instance.execute(self.sample_options)
                
                if not isinstance(result, ToolResult):
                    raise TypeError("Execute did not return a ToolResult object")
                
                if result.status != "completed":
                    raise ValueError(f"Execution did not complete successfully: {result.status}")
                
                logger.info(f"Successfully executed {self.adapter_name} adapter")
                self.test_results["execute"] = True
                return True
        except Exception as e:
            logger.error(f"Error in execution flow for {self.adapter_name} adapter: {e}")
            self.test_results["errors"].append(f"Execution flow error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all tests for the adapter.
        
        Returns:
            Dictionary with test results
        """
        logger.info(f"Running all tests for {self.adapter_name} adapter")
        
        # Run tests
        init_ok = self.test_initialization()
        command_ok = False
        parse_ok = False
        execute_ok = False
        
        if init_ok:
            command_ok = self.test_command_generation()
            parse_ok = self.test_output_parsing()
            execute_ok = self.test_execution_flow()
        
        # Set overall result
        self.test_results["overall"] = init_ok and command_ok and parse_ok and execute_ok
        
        if self.test_results["overall"]:
            logger.info(f"All tests passed for {self.adapter_name} adapter")
        else:
            logger.warning(f"Some tests failed for {self.adapter_name} adapter")
            for error in self.test_results["errors"]:
                logger.error(f"  - {error}")
        
        return self.test_results
    
    def _load_sample_output(self) -> Optional[str]:
        """
        Load sample output from a file.
        
        Returns:
            Sample output string or None if file not found
        """
        # Try to load sample output from a file
        sample_file = os.path.join(
            os.path.dirname(__file__), 
            'test_data', 
            f'{self.adapter_name.lower()}_sample_output.txt'
        )
        
        if os.path.exists(sample_file):
            try:
                with open(sample_file, 'r') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Error loading sample output from {sample_file}: {e}")
        
        return None
    
    def _generate_sample_output(self) -> str:
        """
        Generate a synthetic sample output for testing.
        
        Returns:
            Sample output string
        """
        # Override in subclasses to provide tool-specific sample output
        return "Sample output"


class ZAPAdapterTest(AdapterTest):
    """Test class for ZAP adapter."""
    
    def __init__(self):
        super().__init__(
            ZAPAdapter,
            "ZAP",
            {
                "target": "https://example.com",
                "scan_mode": "active",
                "api_key": "zap-api-key",
                "context_name": "test-context"
            }
        )
    
    def _generate_sample_output(self) -> str:
        # Sample ZAP JSON output
        return json.dumps({
            "scan_id": "1",
            "site": "https://example.com",
            "alerts": [
                {
                    "id": "1",
                    "name": "XSS Vulnerability",
                    "risk": "High",
                    "confidence": "Medium",
                    "description": "Cross-site scripting vulnerability detected.",
                    "url": "https://example.com/page?id=1",
                    "param": "id",
                    "attack": "<script>alert(1)</script>",
                    "evidence": "<script>alert(1)</script>",
                    "solution": "Filter user input",
                    "reference": "https://owasp.org/www-community/attacks/xss/",
                    "cweid": "79",
                    "wascid": "8"
                }
            ]
        })


class NmapAdapterTest(AdapterTest):
    """Test class for Nmap adapter."""
    
    def __init__(self):
        super().__init__(
            NmapAdapter,
            "Nmap",
            {
                "target": "192.168.1.1",
                "ports": "1-1000",
                "scan_type": "SV"
            }
        )
    
    def _generate_sample_output(self) -> str:
        # Sample Nmap XML output
        return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<nmaprun scanner="nmap" start="1598918400" version="7.80">
  <scaninfo type="syn" protocol="tcp" numservices="1000" services="1-1000"/>
  <host starttime="1598918400" endtime="1598918450">
    <status state="up" reason="echo-reply"/>
    <address addr="192.168.1.1" addrtype="ipv4"/>
    <hostnames>
      <hostname name="router.local" type="PTR"/>
    </hostnames>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open" reason="syn-ack"/>
        <service name="ssh" product="OpenSSH" version="7.9" method="probed" conf="10"/>
      </port>
      <port protocol="tcp" portid="80">
        <state state="open" reason="syn-ack"/>
        <service name="http" product="nginx" version="1.14.2" method="probed" conf="10"/>
      </port>
    </ports>
  </host>
  <runstats>
    <finished time="1598918450" timestr="2020-09-01 10:00:50" elapsed="50.00"/>
    <hosts up="1" down="0" total="1"/>
  </runstats>
</nmaprun>
"""


class TrivyAdapterTest(AdapterTest):
    """Test class for Trivy adapter."""
    
    def __init__(self):
        super().__init__(
            TrivyAdapter,
            "Trivy",
            {
                "target": "alpine:latest",
                "scan_type": "image",
                "severity": ["HIGH", "CRITICAL"]
            }
        )
    
    def _generate_sample_output(self) -> str:
        # Sample Trivy JSON output
        return json.dumps({
            "SchemaVersion": 2,
            "ArtifactName": "alpine:latest",
            "ArtifactType": "container_image",
            "Metadata": {
                "ImageID": "sha256:e7d92cdc71feacf90708cb59182d0df1b911f8ae022d29e8e95d75ca6a99776a",
                "DiffIDs": [
                    "sha256:5843afab387455b37944e709ee8c78d7520df80f8d01cf7f861aae63beeddb6b"
                ],
                "RepoTags": [
                    "alpine:latest"
                ],
                "RepoDigests": [
                    "alpine@sha256:e1c082e3d3c45cccac829840a25941e679c25d438cc8412c2fa221cf1a824e6a"
                ],
                "ImageConfig": {
                    "architecture": "amd64",
                    "created": "2022-06-22T22:19:05.519376778Z",
                    "os": "linux"
                }
            },
            "Results": [
                {
                    "Target": "alpine:latest (alpine 3.16.0)",
                    "Class": "os-pkgs",
                    "Type": "alpine",
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-2022-37458",
                            "PkgName": "zlib",
                            "InstalledVersion": "1.2.12-r0",
                            "FixedVersion": "1.2.12-r1",
                            "Layer": {
                                "DiffID": "sha256:5843afab387455b37944e709ee8c78d7520df80f8d01cf7f861aae63beeddb6b"
                            },
                            "SeveritySource": "nvd",
                            "PrimaryURL": "https://avd.aquasec.com/nvd/cve-2022-37458",
                            "Title": "zlib: heap-based buffer over-read in inflate()",
                            "Description": "A vulnerability in the inflate() function...",
                            "Severity": "CRITICAL",
                            "CVSS": {
                                "nvd": {
                                    "V3Score": 9.8,
                                    "V3Vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                                }
                            },
                            "References": [
                                "https://github.com/madler/zlib/issues/605",
                                "https://nvd.nist.gov/vuln/detail/CVE-2022-37458"
                            ]
                        }
                    ]
                }
            ]
        })


class SQLMapAdapterTest(AdapterTest):
    """Test class for SQLMap adapter."""
    
    def __init__(self):
        super().__init__(
            SQLMapAdapter,
            "SQLMap",
            {
                "url": "http://testphp.vulnweb.com/listproducts.php?cat=1",
                "level": 1,
                "risk": 1
            }
        )
    
    def _generate_sample_output(self) -> str:
        # Sample SQLMap output
        return """
sqlmap identified the following injection point(s) with a total of 46 HTTP(s) requests:
---
Parameter: cat (GET)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: cat=1 AND 5438=5438

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind
    Payload: cat=1 AND SLEEP(5)

    Type: UNION query
    Title: Generic UNION query (NULL) - 3 columns
    Payload: cat=1 UNION ALL SELECT NULL,CONCAT(0x716b707671,0x4949524a7975584f437675754c55704673645178444e615a436c6b7173466f6e56466e624873426c,0x7170707a71),NULL-- -
---
back-end DBMS: MySQL >= 5.0.12
"""


class NucleiAdapterTest(AdapterTest):
    """Test class for Nuclei adapter."""
    
    def __init__(self):
        super().__init__(
            NucleiAdapter,
            "Nuclei",
            {
                "url": "https://example.com",
                "tags": "cve,oast",
                "severity": ["critical", "high"],
                "rate_limit": 100
            }
        )
    
    def _generate_sample_output(self) -> str:
        # Sample Nuclei JSON output
        return json.dumps({
            "template-id": "cve-2021-34473-exchange-server",
            "info": {
                "name": "Microsoft Exchange Server SSRF Vulnerability",
                "author": "example",
                "tags": ["cve", "ssrf", "exchange"],
                "severity": "critical",
                "description": "Microsoft Exchange Server contains a SSRF vulnerability."
            },
            "host": "https://example.com",
            "matched-at": "https://example.com/autodiscover/autodiscover.json",
            "type": "http",
            "timestamp": "2023-04-06 15:45:30",
            "curl-command": "curl -X GET https://example.com/autodiscover/autodiscover.json"
        })


class NiktoAdapterTest(AdapterTest):
    """Test class for Nikto adapter."""
    
    def __init__(self):
        super().__init__(
            NiktoAdapter,
            "Nikto",
            {
                "host": "example.com",
                "format": "json",
                "tuning": "1234abc"
            }
        )
    
    def _generate_sample_output(self) -> str:
        # Sample Nikto JSON output
        return json.dumps([{
            "host": "example.com",
            "ip": "203.0.113.37",
            "port": "443",
            "banner": "nginx",
            "vulnerabilities": [
                {
                    "id": "999986",
                    "method": "GET",
                    "url": "/",
                    "msg": "The 'X-XSS-Protection' header is not defined. This header can hint to the user agent to protect against some forms of XSS",
                    "reference": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection"
                },
                {
                    "id": "999970",
                    "method": "GET",
                    "url": "/login.php",
                    "msg": "The anti-clickjacking X-Frame-Options header is not present."
                },
                {
                    "id": "001327",
                    "method": "GET",
                    "url": "/admin/",
                    "msg": "Admin login page/section found."
                }
            ]
        }])


class IntegrationTester:
    """
    Main class to manage testing of all adapters.
    """
    
    def __init__(self):
        """Initialize the integration tester."""
        self.tests = []
        self.results = {}
    
    def register_tests(self):
        """Register all adapter tests."""
        self.tests.extend([
            ZAPAdapterTest(),
            NmapAdapterTest(),
            TrivyAdapterTest(),
            SQLMapAdapterTest(),
            NucleiAdapterTest(),
            NiktoAdapterTest()
        ])
    
    def run_tests(self, specific_adapter: Optional[str] = None):
        """
        Run tests for all registered adapters or a specific one.
        
        Args:
            specific_adapter: Name of a specific adapter to test (optional)
        """
        if not self.tests:
            self.register_tests()
        
        for test in self.tests:
            if specific_adapter and test.adapter_name.lower() != specific_adapter.lower():
                continue
                
            logger.info(f"Running tests for {test.adapter_name} adapter")
            self.results[test.adapter_name] = test.run_all_tests()
    
    def print_results(self):
        """Print test results in a readable format."""
        print("\n" + "=" * 50)
        print("SecureScout Integration Adapter Test Results")
        print("=" * 50 + "\n")
        
        all_passed = True
        
        for adapter_name, results in self.results.items():
            print(f"Adapter: {adapter_name}")
            print("-" * 30)
            
            # Print test status
            for test_name, status in results.items():
                if test_name != "errors":
                    print(f"  {test_name.capitalize()}: {'PASS' if status else 'FAIL'}")
            
            # Print errors if any
            if results.get("errors"):
                print("\n  Errors:")
                for error in results["errors"]:
                    print(f"    - {error}")
            
            print("\n  Overall: {'PASS' if results['overall'] else 'FAIL'}")
            print("\n")
            
            all_passed = all_passed and results["overall"]
        
        print("=" * 50)
        print(f"Final Result: {'ALL PASSED' if all_passed else 'SOME TESTS FAILED'}")
        print("=" * 50 + "\n")
    
    def export_results(self, file_path: str):
        """
        Export test results to a JSON file.
        
        Args:
            file_path: Path to the output file
        """
        try:
            with open(file_path, 'w') as f:
                json.dump({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "results": self.results
                }, f, indent=2)
                
            logger.info(f"Results exported to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting results: {e}")


def main():
    """Main function to run the integration tester."""
    parser = argparse.ArgumentParser(description='SecureScout Integration Adapter Tester')
    parser.add_argument(
        '--adapter', '-a',
        help='Test a specific adapter (e.g., ZAP, Nmap, Trivy, SQLMap, Nuclei, Nikto)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Export results to a JSON file'
    )
    
    args = parser.parse_args()
    
    # Initialize and run tester
    tester = IntegrationTester()
    tester.run_tests(args.adapter)
    tester.print_results()
    
    # Export results if requested
    if args.output:
        tester.export_results(args.output)


if __name__ == "__main__":
    main()