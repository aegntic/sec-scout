#!/usr/bin/env python3
# SecureScout - SQLMap Integration Adapter

import os
import json
import logging
import subprocess
import tempfile
import time
import re
import requests
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

from .adapter_base import BaseToolAdapter, Severity, ToolResult

# Configure logging
logger = logging.getLogger("securescout.integrations.sqlmap")

class SQLMapAPI:
    """
    Client for SQLMap API server.
    
    This class provides methods to interact with the SQLMap API server
    for running SQL injection tests programmatically.
    """
    
    def __init__(self, server_url: str = "http://127.0.0.1:8775"):
        """
        Initialize the SQLMap API client.
        
        Args:
            server_url: URL of the SQLMap API server
        """
        self.server_url = server_url
        self.task_id = None
        self.headers = {"Content-Type": "application/json"}
    
    def start_server(self, host: str = "127.0.0.1", port: int = 8775) -> bool:
        """
        Start the SQLMap API server.
        
        Args:
            host: Host to bind the server to
            port: Port to bind the server to
            
        Returns:
            True if server started successfully, False otherwise
        """
        try:
            # Check if SQLMap API server is already running
            response = requests.get(f"{self.server_url}/status", timeout=2)
            if response.status_code == 200:
                logger.info("SQLMap API server is already running")
                return True
        except requests.RequestException:
            # Server not running, attempt to start it
            pass

        # Server not running, start it
        try:
            sqlmap_api_path = self._find_sqlmapapi_script()
            if not sqlmap_api_path:
                logger.error("SQLMap API script not found")
                return False
            
            # Start the server process in the background
            command = f"{sqlmap_api_path} -s -H {host} -p {port}"
            subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            for _ in range(5):  # Try 5 times
                time.sleep(1)
                try:
                    response = requests.get(f"{self.server_url}/status", timeout=2)
                    if response.status_code == 200:
                        logger.info("SQLMap API server started successfully")
                        return True
                except requests.RequestException:
                    continue
            
            logger.error("Failed to start SQLMap API server")
            return False
            
        except Exception as e:
            logger.error(f"Error starting SQLMap API server: {e}")
            return False
    
    def _find_sqlmapapi_script(self) -> Optional[str]:
        """
        Find the sqlmapapi.py script in common locations.
        
        Returns:
            Path to the sqlmapapi.py script or None if not found
        """
        # Common locations for sqlmapapi.py
        common_locations = [
            "sqlmapapi.py",
            "/usr/share/sqlmap/sqlmapapi.py",
            "/usr/local/share/sqlmap/sqlmapapi.py",
            "/opt/sqlmap/sqlmapapi.py",
            os.path.expanduser("~/.local/share/sqlmap/sqlmapapi.py")
        ]
        
        for location in common_locations:
            if os.path.exists(location):
                return location
        
        # Try to find via which command
        try:
            result = subprocess.run(
                ["which", "sqlmapapi.py"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return None
    
    def new_task(self) -> Optional[str]:
        """
        Create a new scan task.
        
        Returns:
            Task ID if successful, None otherwise
        """
        try:
            response = requests.get(f"{self.server_url}/task/new")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.task_id = data.get("taskid")
                    return self.task_id
            return None
        except Exception as e:
            logger.error(f"Error creating new task: {e}")
            return None
    
    def set_option(self, option: str, value: Any) -> bool:
        """
        Set a scan option.
        
        Args:
            option: Option name
            value: Option value
            
        Returns:
            True if successful, False otherwise
        """
        if not self.task_id:
            logger.error("No task created yet")
            return False
        
        try:
            data = {option: value}
            response = requests.post(
                f"{self.server_url}/option/{self.task_id}/set",
                data=json.dumps(data),
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            return False
        except Exception as e:
            logger.error(f"Error setting option {option}: {e}")
            return False
    
    def start_scan(self) -> bool:
        """
        Start the scan for the current task.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.task_id:
            logger.error("No task created yet")
            return False
        
        try:
            response = requests.post(f"{self.server_url}/scan/{self.task_id}/start")
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            return False
        except Exception as e:
            logger.error(f"Error starting scan: {e}")
            return False
    
    def get_status(self) -> str:
        """
        Get the status of the current task.
        
        Returns:
            Status string (running, terminated, etc.)
        """
        if not self.task_id:
            return "not_created"
        
        try:
            response = requests.get(f"{self.server_url}/scan/{self.task_id}/status")
            if response.status_code == 200:
                data = response.json()
                return data.get("status", "unknown")
            return "error"
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return "error"
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get the scan results for the current task.
        
        Returns:
            Dictionary with scan data
        """
        if not self.task_id:
            return {}
        
        try:
            response = requests.get(f"{self.server_url}/scan/{self.task_id}/data")
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {})
            return {}
        except Exception as e:
            logger.error(f"Error getting data: {e}")
            return {}
    
    def stop_scan(self) -> bool:
        """
        Stop the current scan.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.task_id:
            return False
        
        try:
            response = requests.get(f"{self.server_url}/scan/{self.task_id}/stop")
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            return False
        except Exception as e:
            logger.error(f"Error stopping scan: {e}")
            return False
    
    def delete_task(self) -> bool:
        """
        Delete the current task.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.task_id:
            return False
        
        try:
            response = requests.get(f"{self.server_url}/task/{self.task_id}/delete")
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                if success:
                    self.task_id = None
                return success
            return False
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False


class SQLMapAdapter(BaseToolAdapter):
    """
    Adapter for SQLMap SQL injection scanner.
    
    This adapter provides functionality to run SQLMap scans and parse the results.
    It supports both direct command-line execution and API-based scanning.
    """
    
    def __init__(self, executable_path: Optional[str] = None, use_api: bool = False, api_server: str = "http://127.0.0.1:8775"):
        """
        Initialize the SQLMap adapter.
        
        Args:
            executable_path: Path to the SQLMap executable
            use_api: Whether to use the SQLMap API
            api_server: URL of the SQLMap API server
        """
        super().__init__("sqlmap", executable_path)
        self.use_api = use_api
        self.api_server = api_server
        self.api_client = SQLMapAPI(api_server) if use_api else None
    
    def _find_executable(self) -> Optional[str]:
        """
        Find the SQLMap executable in the system PATH.
        
        Returns:
            Path to the SQLMap executable or None if not found
        """
        # First try the parent class implementation
        executable_path = super()._find_executable()
        if executable_path:
            return executable_path
        
        # Additional SQLMap-specific locations
        common_locations = [
            "/usr/share/sqlmap/sqlmap.py",
            "/usr/local/share/sqlmap/sqlmap.py",
            "/opt/sqlmap/sqlmap.py",
            os.path.expanduser("~/.local/share/sqlmap/sqlmap.py")
        ]
        
        for location in common_locations:
            if os.path.exists(location):
                return location
        
        # Check for the parent directory of sqlmap if it's installed as a package
        try:
            import sqlmap
            sqlmap_dir = os.path.dirname(sqlmap.__file__)
            if os.path.exists(os.path.join(sqlmap_dir, "sqlmap.py")):
                return os.path.join(sqlmap_dir, "sqlmap.py")
        except ImportError:
            pass
        
        return None
    
    def prepare_command(self, options: Dict[str, Any]) -> str:
        """
        Prepare the command to execute SQLMap with the given options.
        
        Args:
            options: SQLMap-specific options
            
        Returns:
            Command string to execute
        """
        # Base command
        command = f"{self.executable_path}"
        
        # Target URL
        target_url = options.get("url")
        if target_url:
            command += f" -u {target_url}"
        
        # Target parameters
        params = options.get("params")
        if params:
            command += f" -p {params}"
        
        # Data for POST requests
        data = options.get("data")
        if data:
            command += f" --data=\"{data}\""
        
        # Cookies
        cookies = options.get("cookies")
        if cookies:
            command += f" --cookie=\"{cookies}\""
        
        # Headers
        headers = options.get("headers")
        if headers:
            for header, value in headers.items():
                command += f" --headers=\"{header}: {value}\""
        
        # Test level (1-5)
        level = options.get("level", 1)
        command += f" --level={level}"
        
        # Risk level (1-3)
        risk = options.get("risk", 1)
        command += f" --risk={risk}"
        
        # Techniques
        techniques = options.get("techniques", "BEUSTQ")
        command += f" --technique={techniques}"
        
        # Output directory
        if self.temp_dir:
            command += f" --output-dir={self.temp_dir}"
        
        # Output format (text only by default)
        command += " -v 1"
        
        # Form detection
        if options.get("forms", False):
            command += " --forms"
        
        # Batch mode (non-interactive)
        command += " --batch"
        
        # Additional arguments
        extra_args = options.get("extra_args", "")
        if extra_args:
            command += f" {extra_args}"
        
        return command
    
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse the SQLMap output and extract findings.
        
        Args:
            output: Raw SQLMap output
            
        Returns:
            List of parsed findings
        """
        findings = []
        
        # Parse for injection points
        injection_points = re.findall(r"Parameter '([^']+)'.*is (.*) injectable", output)
        database_info = re.search(r"back-end DBMS: (.+)$", output, re.MULTILINE)
        database_version = re.search(r"web application technology: (.+)$", output, re.MULTILINE)
        
        # Extract tables if available
        tables = []
        tables_section = re.search(r"Database: [^\n]+\nTable: ([^\n]+)", output)
        if tables_section:
            tables = re.findall(r"Table: ([^\n]+)", output)
        
        # Process each injection point
        for param, injection_type in injection_points:
            # Determine severity based on injection type
            severity = self._determine_severity(injection_type)
            
            # Create a finding
            finding = {
                "title": f"SQL Injection in parameter '{param}'",
                "severity": severity,
                "description": f"SQL Injection vulnerability detected in parameter '{param}' using {injection_type} technique.",
                "evidence": {
                    "parameter": param,
                    "injection_type": injection_type,
                    "database_type": database_info.group(1) if database_info else "Unknown",
                    "database_version": database_version.group(1) if database_version else "Unknown",
                    "tables": tables
                },
                "remediation": "Implement proper input validation and parameterized queries to prevent SQL injection attacks."
            }
            
            findings.append(finding)
        
        return findings
    
    def _determine_severity(self, injection_type: str) -> str:
        """
        Determine the severity based on the injection type.
        
        Args:
            injection_type: Type of SQL injection
            
        Returns:
            Normalized severity string
        """
        # Union and error-based injections are typically high severity
        if 'UNION' in injection_type or 'error-based' in injection_type:
            return Severity.HIGH
        
        # Time-based and boolean-based blind injections are typically medium severity
        if 'time-based' in injection_type or 'boolean-based' in injection_type:
            return Severity.MEDIUM
        
        # Default to medium severity for other types
        return Severity.MEDIUM
    
    def execute_api(self, options: Dict[str, Any]) -> ToolResult:
        """
        Execute SQLMap through its API interface.
        
        Args:
            options: SQLMap-specific options
            
        Returns:
            ToolResult object with execution results
        """
        # Check if API client is available
        if not self.api_client:
            raise ValueError("API client not initialized")
        
        # Start the API server if needed
        if not self.api_client.start_server():
            raise RuntimeError("Failed to start SQLMap API server")
        
        # Prepare command representation for logging
        command = f"sqlmap-api scan on {options.get('url', 'unknown target')}"
        
        # Initialize the result object
        self.result = ToolResult(
            tool_name=self.tool_name,
            command=command,
            start_time=datetime.now()
        )
        
        try:
            # Create a new task
            task_id = self.api_client.new_task()
            if not task_id:
                raise RuntimeError("Failed to create a new task")
            
            # Set options
            if "url" in options:
                self.api_client.set_option("url", options["url"])
            
            if "params" in options:
                self.api_client.set_option("p", options["params"])
            
            if "data" in options:
                self.api_client.set_option("data", options["data"])
            
            if "cookies" in options:
                self.api_client.set_option("cookie", options["cookies"])
            
            if "level" in options:
                self.api_client.set_option("level", options["level"])
            
            if "risk" in options:
                self.api_client.set_option("risk", options["risk"])
            
            # Set batch mode
            self.api_client.set_option("batch", True)
            
            # Start the scan
            if not self.api_client.start_scan():
                raise RuntimeError("Failed to start the scan")
            
            self.result.status = "running"
            
            # Poll for results
            while True:
                status = self.api_client.get_status()
                
                if status == "terminated":
                    break
                elif status == "error":
                    raise RuntimeError("Scan encountered an error")
                
                time.sleep(2)  # Wait before polling again
            
            # Get the scan data
            scan_data = self.api_client.get_data()
            
            # Parse the API results
            findings = self._parse_api_results(scan_data)
            
            # Set parsed findings
            self.result.parsed_findings = findings
            
            # Mark as completed
            self.result.mark_completed()
            
            return self.result
            
        except Exception as e:
            logger.error(f"Error executing SQLMap API scan: {str(e)}")
            self.result.set_error(f"Error executing tool: {str(e)}")
            return self.result
        finally:
            # Clean up API task
            if self.api_client and self.api_client.task_id:
                self.api_client.delete_task()
    
    def _parse_api_results(self, scan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the results from the SQLMap API.
        
        Args:
            scan_data: Data from the SQLMap API
            
        Returns:
            List of parsed findings
        """
        findings = []
        
        # Extract relevant data from the API response
        if not scan_data:
            return findings
        
        # Process data structure from SQLMap API
        for target_url, target_data in scan_data.items():
            if not isinstance(target_data, dict):
                continue
                
            # Get DBMS information
            dbms = target_data.get("dbms", "Unknown")
            
            # Extract injection points
            for place, place_data in target_data.items():
                if not isinstance(place_data, dict) or place == "dbms":
                    continue
                
                for parameter, param_data in place_data.items():
                    if not isinstance(param_data, dict):
                        continue
                    
                    # Get injection types
                    for inj_type, type_details in param_data.items():
                        if not isinstance(type_details, dict):
                            continue
                        
                        # Determine severity
                        severity = self._determine_severity(inj_type)
                        
                        # Create finding
                        finding = {
                            "title": f"SQL Injection in parameter '{parameter}'",
                            "severity": severity,
                            "description": f"SQL Injection vulnerability detected in parameter '{parameter}' using {inj_type} technique.",
                            "evidence": {
                                "parameter": parameter,
                                "injection_type": inj_type,
                                "database_type": dbms,
                                "place": place
                            },
                            "remediation": "Implement proper input validation and parameterized queries to prevent SQL injection attacks."
                        }
                        
                        findings.append(finding)
        
        return findings
    
    def execute(self, options: Dict[str, Any]) -> ToolResult:
        """
        Execute SQLMap with the given options.
        
        Args:
            options: SQLMap-specific options
            
        Returns:
            ToolResult object with execution results
        """
        # Use API method if enabled
        if self.use_api and self.api_client:
            return self.execute_api(options)
        
        # Otherwise use command-line execution
        return super().execute(options)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example adapter usage with direct command execution
    adapter = SQLMapAdapter()
    
    # Test target options
    test_options = {
        "url": "http://testphp.vulnweb.com/listproducts.php?cat=1",
        "level": 1,
        "risk": 1
    }
    
    # Execute and get results
    result = adapter.execute(test_options)
    
    # Print results
    print(json.dumps(result.to_dict(), indent=2))