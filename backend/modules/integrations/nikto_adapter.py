#!/usr/bin/env python3
# SecureScout - Nikto Integration Adapter

import os
import json
import logging
import subprocess
import tempfile
import re
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import csv
import xml.etree.ElementTree as ET

from .adapter_base import BaseToolAdapter, Severity, ToolResult

# Configure logging
logger = logging.getLogger("securescout.integrations.nikto")

# Nikto finding categories for severity mapping
NIKTO_CATEGORIES = {
    # Categories are based on Nikto's tuning options
    "1": {"name": "File Upload", "default_severity": Severity.HIGH},
    "2": {"name": "Misconfiguration / Default Files", "default_severity": Severity.MEDIUM},
    "3": {"name": "Information Disclosure", "default_severity": Severity.LOW},
    "4": {"name": "Injection / Command Execution", "default_severity": Severity.HIGH},
    "5": {"name": "Remote File Retrieval", "default_severity": Severity.HIGH},
    "6": {"name": "Denial of Service", "default_severity": Severity.MEDIUM},
    "7": {"name": "Remote File Retrieval", "default_severity": Severity.MEDIUM},
    "8": {"name": "Command Execution / Authentication Bypass", "default_severity": Severity.CRITICAL},
    "9": {"name": "SQL Injection", "default_severity": Severity.HIGH},
    "0": {"name": "File Disclosure", "default_severity": Severity.MEDIUM},
    "a": {"name": "Authentication", "default_severity": Severity.HIGH},
    "b": {"name": "Software Identification", "default_severity": Severity.INFO},
    "c": {"name": "Remote Source Inclusion", "default_severity": Severity.HIGH},
    "x": {"name": "Reverse Proxy", "default_severity": Severity.MEDIUM}
}

# Mapping of Nikto test IDs to categories and custom severity overrides
NIKTO_ID_MAPPINGS = {
    # Format: "id": {"category": "category_code", "severity": "custom_severity_if_different"}
    # These are just examples - a comprehensive mapping would be quite extensive
    "000001": {"category": "b", "severity": Severity.INFO},   # Server version/type disclosure
    "001152": {"category": "2", "severity": Severity.MEDIUM}, # Default Apache page
    "006493": {"category": "3", "severity": Severity.LOW},    # PHP info disclosure
    "006628": {"category": "2", "severity": Severity.LOW},    # Default docs
    "006756": {"category": "4", "severity": Severity.HIGH},   # PHP CGI Argument Injection
    "007608": {"category": "3", "severity": Severity.MEDIUM}, # Open directory indexing
    "009671": {"category": "9", "severity": Severity.HIGH},   # SQL injection
    "009673": {"category": "8", "severity": Severity.CRITICAL} # Remote command execution
}


class NiktoAdapter(BaseToolAdapter):
    """
    Adapter for Nikto web server scanner.
    
    This adapter provides functionality to run Nikto scans and parse the results.
    It includes options for output formatting and custom scanning parameters.
    """
    
    def __init__(self, executable_path: Optional[str] = None, plugin_dir: Optional[str] = None):
        """
        Initialize the Nikto adapter.
        
        Args:
            executable_path: Path to the Nikto executable
            plugin_dir: Path to Nikto plugins directory
        """
        super().__init__("nikto", executable_path)
        self.plugin_dir = plugin_dir
    
    def _find_executable(self) -> Optional[str]:
        """
        Find the Nikto executable in the system PATH.
        
        Returns:
            Path to the Nikto executable or None if not found
        """
        # First try the parent class implementation
        executable_path = super()._find_executable()
        if executable_path:
            return executable_path
        
        # Additional Nikto-specific locations
        common_locations = [
            "/usr/bin/nikto",
            "/usr/local/bin/nikto",
            "/usr/share/nikto/nikto.pl",
            "/opt/nikto/nikto.pl",
            "/usr/local/share/nikto/nikto.pl"
        ]
        
        for location in common_locations:
            if os.path.exists(location) and os.access(location, os.X_OK):
                return location
            elif location.endswith('.pl') and os.path.exists(location):
                # Perl script needs perl interpreter
                return f"perl {location}"
        
        return None
    
    def prepare_command(self, options: Dict[str, Any]) -> str:
        """
        Prepare the command to execute Nikto with the given options.
        
        Args:
            options: Nikto-specific options
            
        Returns:
            Command string to execute
        """
        # Base command
        command = f"{self.executable_path}"
        
        # Target host (required)
        if "host" not in options:
            raise ValueError("Target host is required")
        
        command += f" -h {options['host']}"
        
        # Port specification
        if "port" in options:
            port = options["port"]
            if isinstance(port, list):
                port_str = ",".join(map(str, port))
            else:
                port_str = str(port)
            command += f" -p {port_str}"
        
        # Output format and file
        output_format = options.get("format", "json").lower()
        
        if self.temp_dir:
            output_file = os.path.join(self.temp_dir, f"nikto-output.{output_format}")
            command += f" -o {output_file} -Format {output_format}"
        
        # Authentication
        if "username" in options and "password" in options:
            command += f" -id {options['username']}:{options['password']}"
        
        # Scan tuning
        if "tuning" in options:
            tuning = options["tuning"]
            if isinstance(tuning, list):
                tuning_str = "".join(tuning)
            else:
                tuning_str = tuning
            command += f" -Tuning {tuning_str}"
        
        # Scan timing
        if "pause" in options:
            command += f" -Pause {options['pause']}"
        
        if "max_time" in options:
            command += f" -maxtime {options['max_time']}"
        
        # SSL options
        if options.get("ssl", False):
            command += " -ssl"
            
        if options.get("no_ssl_check", False):
            command += " -nossl"
        
        # Proxy settings
        if "proxy" in options:
            command += f" -proxy {options['proxy']}"
        
        # Cookies
        if "cookies" in options:
            if isinstance(options["cookies"], dict):
                cookie_str = "; ".join([f"{k}={v}" for k, v in options["cookies"].items()])
                command += f" -cookies {cookie_str}"
            else:
                command += f" -cookies {options['cookies']}"
        
        # Custom headers
        if "headers" in options:
            if isinstance(options["headers"], dict):
                for key, value in options["headers"].items():
                    command += f" -vhost \"{key}: {value}\""
            else:
                command += f" -vhost \"{options['headers']}\""
        
        # Disable host header override
        if options.get("no_host_lookup", False):
            command += " -nolookup"
        
        # Enable debug output
        if options.get("debug", False):
            command += " -debug"
        
        # Use plugin directory
        if self.plugin_dir:
            command += f" -plugins {self.plugin_dir}"
        
        # Display progress
        command += " -Display V"  # Verbose output
        
        # Additional arguments
        if "extra_args" in options:
            command += f" {options['extra_args']}"
        
        return command
    
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse the Nikto output and extract findings.
        
        Args:
            output: Raw Nikto output
            
        Returns:
            List of parsed findings
        """
        findings = []
        
        # Check if Nikto returned meaningful output
        if not output or "No web server found" in output:
            return findings
        
        # Check if a JSON file is available
        if self.temp_dir:
            json_file = os.path.join(self.temp_dir, "nikto-output.json")
            if os.path.exists(json_file):
                findings = self._parse_json_file(json_file)
                if findings:
                    return findings
        
        # If no JSON file or it couldn't be parsed, try parsing the output directly
        try:
            # Try to parse as JSON
            data = json.loads(output)
            findings = self._parse_json(data)
        except json.JSONDecodeError:
            # If not JSON, try parsing as text
            findings = self._parse_text(output)
        
        return findings
    
    def _parse_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a Nikto JSON output file.
        
        Args:
            file_path: Path to the JSON output file
            
        Returns:
            List of parsed findings
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return self._parse_json(data)
        except Exception as e:
            logger.error(f"Error parsing JSON file {file_path}: {e}")
            return []
    
    def _parse_json(self, data: Any) -> List[Dict[str, Any]]:
        """
        Parse Nikto JSON data.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            List of parsed findings
        """
        findings = []
        
        try:
            if isinstance(data, list):
                for scan in data:
                    host_findings = self._parse_host_scan(scan)
                    findings.extend(host_findings)
            elif isinstance(data, dict):
                # Single host scan
                host_findings = self._parse_host_scan(data)
                findings.extend(host_findings)
            
            return findings
        except Exception as e:
            logger.error(f"Error parsing JSON data: {e}")
            return []
    
    def _parse_host_scan(self, host_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse data for a single host scan.
        
        Args:
            host_data: Host scan data
            
        Returns:
            List of parsed findings
        """
        findings = []
        
        try:
            host = host_data.get("host", "")
            ip = host_data.get("ip", "")
            port = host_data.get("port", "")
            
            vulnerabilities = host_data.get("vulnerabilities", [])
            if not vulnerabilities:
                return findings
            
            for vuln in vulnerabilities:
                finding = self._process_vulnerability(vuln, host, ip, port)
                if finding:
                    findings.append(finding)
            
            return findings
        except Exception as e:
            logger.error(f"Error parsing host scan: {e}")
            return []
    
    def _process_vulnerability(self, vuln: Dict[str, Any], host: str, ip: str, port: str) -> Optional[Dict[str, Any]]:
        """
        Process a single vulnerability finding.
        
        Args:
            vuln: Vulnerability data
            host: Target hostname
            ip: Target IP address
            port: Target port
            
        Returns:
            Processed finding dictionary
        """
        try:
            if not isinstance(vuln, dict):
                return None
            
            # Extract basic information
            test_id = vuln.get("id", "")
            method = vuln.get("method", "GET")
            url = vuln.get("url", "/")
            message = vuln.get("msg", "")
            
            # Skip empty or incomplete findings
            if not test_id or not message:
                return None
            
            # Determine severity based on test ID
            severity = self._determine_severity(test_id)
            
            # Generate a descriptive title
            title = self._generate_title(message, test_id)
            
            # Extract references if available
            references = vuln.get("references", {})
            ref_links = []
            
            if isinstance(references, dict):
                for ref_type, ref_items in references.items():
                    if isinstance(ref_items, list):
                        for item in ref_items:
                            ref_links.append(f"{ref_type}:{item}")
                    else:
                        ref_links.append(f"{ref_type}:{ref_items}")
            
            # Create finding
            finding = {
                "title": title,
                "severity": severity,
                "description": message,
                "test_id": test_id,
                "evidence": {
                    "host": host,
                    "ip": ip,
                    "port": port,
                    "method": method,
                    "url": url,
                    "references": ref_links
                },
                "remediation": self._get_remediation(test_id, message)
            }
            
            return finding
            
        except Exception as e:
            logger.error(f"Error processing vulnerability: {e}")
            return None
    
    def _parse_text(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse Nikto text output.
        
        Args:
            output: Raw Nikto text output
            
        Returns:
            List of parsed findings
        """
        findings = []
        
        # Regular expressions for key information
        target_regex = r"- Target: (?P<host>[^\s]+)(\s+IP:(?P<ip>[^\s]+))?(\s+Port: (?P<port>\d+))?"
        finding_regex = r"- (?P<id>\d+)\s+(?P<message>.*?)(?:\s+(?P<url>http[s]?://[^\s]+))?"
        
        # Extract target information
        target_match = re.search(target_regex, output)
        host = target_match.group("host") if target_match and target_match.group("host") else ""
        ip = target_match.group("ip") if target_match and target_match.group("ip") else ""
        port = target_match.group("port") if target_match and target_match.group("port") else ""
        
        # Extract findings
        for line in output.splitlines():
            if line.startswith("- ") and re.search(r"- \d+\s+", line):
                finding_match = re.search(finding_regex, line)
                
                if finding_match:
                    test_id = finding_match.group("id").zfill(6)  # Pad ID to 6 digits
                    message = finding_match.group("message")
                    url = finding_match.group("url") or "/"
                    
                    # Skip empty or incomplete findings
                    if not test_id or not message:
                        continue
                    
                    # Determine severity based on test ID
                    severity = self._determine_severity(test_id)
                    
                    # Generate a descriptive title
                    title = self._generate_title(message, test_id)
                    
                    # Create finding
                    finding = {
                        "title": title,
                        "severity": severity,
                        "description": message,
                        "test_id": test_id,
                        "evidence": {
                            "host": host,
                            "ip": ip,
                            "port": port,
                            "url": url,
                            "references": []
                        },
                        "remediation": self._get_remediation(test_id, message)
                    }
                    
                    findings.append(finding)
        
        return findings
    
    def _determine_severity(self, test_id: str) -> str:
        """
        Determine the severity based on the test ID.
        
        Args:
            test_id: Nikto test ID
            
        Returns:
            Normalized severity string
        """
        # Check for specific ID mapping
        if test_id in NIKTO_ID_MAPPINGS:
            return NIKTO_ID_MAPPINGS[test_id].get("severity")
        
        # Try to determine category from the ID
        # (This is a simplification; a real implementation would need a more comprehensive mapping)
        category = None
        
        # Try to extract category from ID ranges
        id_num = int(test_id) if test_id.isdigit() else 0
        
        if 1 <= id_num <= 999:
            category = "b"  # Server type/version
        elif 1000 <= id_num <= 1999:
            category = "2"  # Default files
        elif 2000 <= id_num <= 2999:
            category = "3"  # Information disclosure
        elif 3000 <= id_num <= 3999:
            category = "0"  # File disclosure
        elif 4000 <= id_num <= 4999:
            category = "4"  # Injection
        elif 5000 <= id_num <= 5999:
            category = "5"  # Remote file retrieval
        elif 6000 <= id_num <= 6999:
            category = "4"  # Command execution
        elif 7000 <= id_num <= 7999:
            category = "a"  # Authentication
        elif 8000 <= id_num <= 8999:
            category = "9"  # SQL injection
        elif 9000 <= id_num <= 9999:
            category = "8"  # Command execution
        else:
            category = "2"  # Default to misconfiguration
        
        # Get default severity for category
        if category in NIKTO_CATEGORIES:
            return NIKTO_CATEGORIES[category]["default_severity"]
        
        # Default severity if no mapping found
        return Severity.MEDIUM
    
    def _generate_title(self, message: str, test_id: str) -> str:
        """
        Generate a descriptive title for the finding.
        
        Args:
            message: Finding message
            test_id: Nikto test ID
            
        Returns:
            Generated title string
        """
        # Extract first part of message (limit to 60 chars)
        title = message.split(": ")[0] if ": " in message else message
        
        # Trim and add test ID
        title = title[:60] + ("..." if len(title) > 60 else "")
        return f"Nikto #{test_id}: {title}"
    
    def _get_remediation(self, test_id: str, message: str) -> str:
        """
        Generate remediation advice based on test ID and message.
        
        Args:
            test_id: Nikto test ID
            message: Finding message
            
        Returns:
            Remediation advice string
        """
        # This would ideally be a more comprehensive mapping of test IDs to remediation advice
        # For now, we'll provide generic advice based on category
        
        # Determine category from test ID
        category = None
        if test_id in NIKTO_ID_MAPPINGS:
            category = NIKTO_ID_MAPPINGS[test_id].get("category")
        
        # If we couldn't determine a specific category, try to guess from the message
        if not category:
            if "default" in message.lower() or "sample" in message.lower():
                category = "2"  # Default files
            elif "directory" in message.lower() and "listing" in message.lower():
                category = "3"  # Information disclosure
            elif "sql" in message.lower():
                category = "9"  # SQL injection
            elif "xss" in message.lower() or "script" in message.lower():
                category = "4"  # Injection
            elif "server" in message.lower() and "version" in message.lower():
                category = "b"  # Server information
            elif "login" in message.lower() or "password" in message.lower():
                category = "a"  # Authentication
            else:
                category = "2"  # Default to misconfiguration
        
        # Generate remediation based on category
        if category == "1":  # File Upload
            return "Disable file uploads if not needed, or implement strict validation of uploaded files."
        
        elif category == "2":  # Default files
            return "Remove default, sample, or test files and directories from the web server."
        
        elif category == "3":  # Information disclosure
            return "Configure the web server to prevent information disclosure. Review server configurations and disable verbose error messages."
        
        elif category == "4":  # Injection
            return "Implement input validation and output encoding to prevent injection attacks."
        
        elif category == "5" or category == "7":  # Remote file retrieval
            return "Disable directory traversal and ensure proper access controls for files."
        
        elif category == "6":  # Denial of service
            return "Implement rate limiting and resource constraints to prevent DoS attacks."
        
        elif category == "8":  # Command execution
            return "Validate all user input and avoid passing user-controlled data to system commands."
        
        elif category == "9":  # SQL injection
            return "Use parameterized queries or prepared statements to prevent SQL injection."
        
        elif category == "0":  # File disclosure
            return "Configure proper file permissions and ensure sensitive files are not accessible through the web server."
        
        elif category == "a":  # Authentication
            return "Implement secure authentication mechanisms and protect credentials in transit and at rest."
        
        elif category == "b":  # Software identification
            return "Configure server to minimize information disclosure about software versions in use."
        
        elif category == "c":  # Remote source inclusion
            return "Validate all input and avoid including remote files based on user input."
        
        elif category == "x":  # Reverse proxy
            return "Configure reverse proxy settings to prevent unauthorized access to internal resources."
        
        # Default remediation
        return "Review server configuration and security settings to address this vulnerability."
    
    def execute(self, options: Dict[str, Any]) -> ToolResult:
        """
        Execute Nikto with the given options.
        
        Args:
            options: Nikto-specific options
            
        Returns:
            ToolResult object with execution results
        """
        # Use the parent class execute method
        result = super().execute(options)
        
        # Check if additional output file needs to be processed
        if self.temp_dir and result.status == "completed":
            # Try different output formats
            for fmt in ["json", "csv", "xml", "txt"]:
                output_file = os.path.join(self.temp_dir, f"nikto-output.{fmt}")
                if os.path.exists(output_file):
                    # Add the output file to result files
                    result.add_result_file(output_file)
            
            # If no findings were parsed from stdout, try from the output file
            if not result.parsed_findings:
                json_file = os.path.join(self.temp_dir, "nikto-output.json")
                if os.path.exists(json_file):
                    result.parsed_findings = self._parse_json_file(json_file)
        
        return result


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example adapter usage
    adapter = NiktoAdapter()
    
    # Simple scan options
    test_options = {
        "host": "example.com",
        "format": "json",
        "tuning": "1234abc"
    }
    
    # Execute and get results
    # result = adapter.execute(test_options)
    
    # Print results
    # print(json.dumps(result.to_dict(), indent=2))