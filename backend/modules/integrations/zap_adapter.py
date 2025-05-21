#!/usr/bin/env python3
# SecureScout - OWASP ZAP Integration Adapter

import os
import json
import time
import logging
import subprocess
import tempfile
import socket
import requests
import random
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import xml.etree.ElementTree as ET

from .adapter_base import BaseToolAdapter, ToolResult, Severity

# Configure logging
logger = logging.getLogger("securescout.integrations.zap")

class ZAPAdapter(BaseToolAdapter):
    """
    Adapter for OWASP ZAP (Zed Attack Proxy).
    
    This adapter provides functionality to run ZAP scans using either the 
    command-line interface or the ZAP API.
    """
    
    DEFAULT_API_KEY = "securescout"  # Default API key for ZAP
    DEFAULT_PORT = 8090  # Default port for ZAP API
    DEFAULT_TIMEOUT = 120  # Default timeout for API calls (in seconds)
    
    def __init__(
        self, 
        executable_path: Optional[str] = None,
        api_key: Optional[str] = None, 
        zap_home: Optional[str] = None,
        port: Optional[int] = None,
        use_api: bool = True,
        api_url: Optional[str] = None
    ):
        """
        Initialize the ZAP adapter.
        
        Args:
            executable_path: Path to the ZAP executable (if not in PATH)
            api_key: ZAP API key
            zap_home: ZAP home directory
            port: Port for ZAP API
            use_api: Whether to use the ZAP API (True) or command-line (False)
            api_url: URL for the ZAP API (if already running)
        """
        super().__init__("zap", executable_path)
        self.api_key = api_key or os.environ.get("ZAP_API_KEY", self.DEFAULT_API_KEY)
        self.zap_home = zap_home or os.environ.get("ZAP_HOME")
        self.port = port or int(os.environ.get("ZAP_PORT", self.DEFAULT_PORT))
        self.use_api = use_api
        self.api_url = api_url or f"http://localhost:{self.port}/JSON/"
        self.zap_process = None
        self.daemon_started = False
        
        if not self.executable_path:
            # Try alternative names if not found
            alternative_names = ["zap.sh", "zaproxy", "zap-baseline.py", "zap-api-scan.py"]
            for name in alternative_names:
                self.tool_name = name
                self.executable_path = self._find_executable()
                if self.executable_path:
                    break
            
            # Reset tool name
            self.tool_name = "zap"
            
            if not self.executable_path:
                logger.warning("ZAP executable not found. ZAP may not be installed correctly.")
    
    def find_free_port(self) -> int:
        """
        Find a free port to use for ZAP API.
        
        Returns:
            A free port number
        """
        # Try the default port first
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("", self.port))
            return self.port
        except socket.error:
            # If default port is in use, find a random free port
            s.bind(("", 0))
            port = s.getsockname()[1]
            return port
        finally:
            s.close()
    
    def start_daemon(self) -> bool:
        """
        Start ZAP as a daemon process.
        
        Returns:
            True if ZAP was started successfully, False otherwise
        """
        if self.daemon_started:
            return True
        
        if not self.executable_path:
            logger.error("Cannot start ZAP daemon: executable not found")
            return False
        
        # Find a free port
        self.port = self.find_free_port()
        
        # Prepare ZAP command
        java_opts = "-Xmx1g"  # Default Java memory
        
        if self.zap_home:
            zap_command = f"java {java_opts} -jar {self.zap_home}/zap.jar"
        elif self.executable_path.endswith(".jar"):
            zap_command = f"java {java_opts} -jar {self.executable_path}"
        elif self.executable_path.endswith(".py"):
            zap_command = f"python3 {self.executable_path}"
        else:
            zap_command = self.executable_path
        
        zap_command += f" -daemon -host 127.0.0.1 -port {self.port} -config api.key={self.api_key} -config api.disablekey=false"
        
        # Start ZAP process
        try:
            logger.info(f"Starting ZAP daemon on port {self.port}")
            self.zap_process = subprocess.Popen(
                zap_command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for ZAP to start
            max_attempts = 10
            attempts = 0
            
            while attempts < max_attempts:
                try:
                    response = requests.get(f"http://localhost:{self.port}/JSON/core/view/version/?apikey={self.api_key}")
                    if response.status_code == 200:
                        logger.info("ZAP daemon started successfully")
                        self.daemon_started = True
                        self.api_url = f"http://localhost:{self.port}/JSON/"
                        return True
                except requests.exceptions.ConnectionError:
                    pass
                
                attempts += 1
                time.sleep(5)
            
            logger.error("Failed to start ZAP daemon: timeout waiting for API")
            return False
        
        except Exception as e:
            logger.error(f"Failed to start ZAP daemon: {str(e)}")
            return False
    
    def stop_daemon(self) -> bool:
        """
        Stop the ZAP daemon process.
        
        Returns:
            True if ZAP was stopped successfully, False otherwise
        """
        if not self.daemon_started or not self.zap_process:
            return True
        
        try:
            # Try to stop ZAP gracefully
            requests.get(f"http://localhost:{self.port}/JSON/core/action/shutdown/?apikey={self.api_key}")
            
            # Wait for process to exit
            max_wait = 20
            for _ in range(max_wait):
                if self.zap_process.poll() is not None:
                    self.daemon_started = False
                    return True
                time.sleep(1)
            
            # Force kill if still running
            if self.zap_process.poll() is None:
                self.zap_process.terminate()
                time.sleep(2)
                if self.zap_process.poll() is None:
                    self.zap_process.kill()
            
            self.daemon_started = False
            return True
        
        except Exception as e:
            logger.error(f"Error stopping ZAP daemon: {str(e)}")
            return False
    
    def prepare_command(self, options: Dict[str, Any]) -> str:
        """
        Prepare the command to execute ZAP with the given options.
        
        Args:
            options: ZAP scan options
            
        Returns:
            Command string to execute
        """
        if not self.use_api:
            # Command-line mode using zap-baseline.py or similar
            if "baseline" in options:
                # Use zap-baseline.py for baseline scans
                baseline_script = self.executable_path if "baseline" in self.executable_path else "zap-baseline.py"
                
                target = options.get("target", "")
                cmd = f"{baseline_script} -t {target}"
                
                # Add optional parameters
                if options.get("ajax", False):
                    cmd += " -j"
                
                if options.get("full_scan", False):
                    cmd += " -a"
                
                report_path = options.get("report_path", os.path.join(self.temp_dir, "zap-report.html"))
                cmd += f" -r {report_path}"
                
                return cmd
            else:
                # Use standard ZAP command with -cmd for non-baseline scans
                target = options.get("target", "")
                cmd = f"{self.executable_path} -cmd -quickurl {target}"
                
                if options.get("spider", True):
                    cmd += " -quickspider"
                
                if options.get("ajax", False):
                    cmd += " -quickajax"
                
                if options.get("full_scan", False):
                    cmd += " -quickscan"
                else:
                    cmd += " -quickprogress"
                
                return cmd
        else:
            # API mode - we don't actually execute a command, but we need a string for logging
            target = options.get("target", "")
            api_command = f"ZAP API scan: spider and active scan for {target}"
            return api_command
    
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse the ZAP output and extract findings.
        
        Args:
            output: Raw ZAP output
            
        Returns:
            List of parsed findings
        """
        findings = []
        
        # Try to parse as JSON first
        try:
            data = json.loads(output)
            if "alerts" in data:
                # Parse alerts from JSON output
                for alert in data["alerts"]:
                    finding = {
                        "title": alert.get("name", "Unknown"),
                        "severity": Severity.normalize(alert.get("risk", "Unknown")),
                        "description": alert.get("description", ""),
                        "solution": alert.get("solution", ""),
                        "references": alert.get("reference", ""),
                        "urls": [instance.get("uri", "") for instance in alert.get("instances", [])],
                        "cweid": alert.get("cweid", ""),
                        "wascid": alert.get("wascid", ""),
                        "evidence": ", ".join([instance.get("evidence", "") for instance in alert.get("instances", []) if "evidence" in instance]),
                        "raw": alert
                    }
                    findings.append(finding)
            return findings
        except json.JSONDecodeError:
            pass
        
        # Try to parse as XML
        try:
            if "<?xml" in output:
                root = ET.fromstring(output)
                for alert in root.findall(".//alertitem"):
                    finding = {
                        "title": self._get_xml_text(alert, "alert"),
                        "severity": Severity.normalize(self._get_xml_text(alert, "riskcode")),
                        "description": self._get_xml_text(alert, "desc"),
                        "solution": self._get_xml_text(alert, "solution"),
                        "references": self._get_xml_text(alert, "reference"),
                        "urls": [instance.text for instance in alert.findall(".//uri")],
                        "cweid": self._get_xml_text(alert, "cweid"),
                        "wascid": self._get_xml_text(alert, "wascid"),
                        "evidence": ", ".join([instance.text for instance in alert.findall(".//evidence")]),
                        "raw": ET.tostring(alert, encoding="unicode")
                    }
                    findings.append(finding)
                return findings
        except Exception as e:
            logger.error(f"Error parsing XML output: {str(e)}")
        
        # Parse line by line for text output
        current_alert = None
        alerts = []
        
        for line in output.split("\n"):
            line = line.strip()
            
            # Look for alert patterns
            if line.startswith("WARN") and "=" in line:
                # New alert
                if current_alert:
                    alerts.append(current_alert)
                
                current_alert = {"title": line.split("=")[1].strip()}
            
            elif line.startswith("INFO") and "=" in line and current_alert:
                # Alert detail
                key, value = line.split("=", 1)
                key = key.replace("INFO", "").strip().lower()
                value = value.strip()
                
                if key in ["risk", "confidence", "url", "solution", "param", "attack", "evidence"]:
                    current_alert[key] = value
        
        # Add the last alert if any
        if current_alert:
            alerts.append(current_alert)
        
        # Convert alerts to findings
        for alert in alerts:
            finding = {
                "title": alert.get("title", "Unknown"),
                "severity": Severity.normalize(alert.get("risk", "Unknown")),
                "description": alert.get("title", ""),  # Often the description is not in the text output
                "solution": alert.get("solution", ""),
                "urls": [alert.get("url", "")],
                "evidence": alert.get("evidence", ""),
                "raw": alert
            }
            findings.append(finding)
        
        return findings
    
    def _get_xml_text(self, element: ET.Element, tag: str) -> str:
        """
        Helper method to extract text from an XML element.
        
        Args:
            element: XML element
            tag: Tag name to look for
            
        Returns:
            Text content or empty string
        """
        found = element.find(f".//{tag}")
        return found.text if found is not None else ""
    
    def execute_with_api(self, options: Dict[str, Any]) -> ToolResult:
        """
        Execute a ZAP scan using the API.
        
        Args:
            options: Scan options
            
        Returns:
            ToolResult with the scan results
        """
        try:
            import time
            from zapv2 import ZAPv2
            
            target = options.get("target", "")
            if not target:
                raise ValueError("Target URL is required")
            
            # Initialize result
            command = self.prepare_command(options)
            self.result = ToolResult(
                tool_name="zap",
                command=command,
                start_time=datetime.now(),
                status="running"
            )
            
            # Start ZAP if not running
            if not self.daemon_started and not options.get("api_url"):
                if not self.start_daemon():
                    self.result.set_error("Failed to start ZAP daemon")
                    return self.result
            
            # Use provided API URL if available
            api_url = options.get("api_url", self.api_url)
            api_key = options.get("api_key", self.api_key)
            
            # Initialize ZAP client
            zap = ZAPv2(apikey=api_key, proxies={"http": api_url, "https": api_url})
            
            # Access the target
            logger.info(f"Accessing target: {target}")
            zap.urlopen(target)
            time.sleep(2)
            
            # Spider the target
            if options.get("spider", True):
                logger.info("Starting spider")
                scan_id = zap.spider.scan(target)
                
                # Wait for spider to complete
                while int(zap.spider.status(scan_id)) < 100:
                    logger.info(f"Spider progress: {zap.spider.status(scan_id)}%")
                    time.sleep(5)
                
                logger.info("Spider completed")
            
            # AJAX Spider if requested
            if options.get("ajax", False):
                logger.info("Starting AJAX spider")
                zap.ajaxSpider.scan(target)
                
                # Wait for AJAX spider to complete
                while zap.ajaxSpider.status == "running":
                    logger.info("AJAX spider still running...")
                    time.sleep(5)
                
                logger.info("AJAX spider completed")
            
            # Run active scan
            if options.get("active_scan", True):
                logger.info("Starting active scan")
                scan_id = zap.ascan.scan(target)
                
                # Wait for active scan to complete
                while int(zap.ascan.status(scan_id)) < 100:
                    logger.info(f"Active scan progress: {zap.ascan.status(scan_id)}%")
                    time.sleep(5)
                
                logger.info("Active scan completed")
            
            # Get the alerts
            logger.info("Retrieving alerts")
            alerts = zap.core.alerts()
            
            # Save raw output
            self.result.raw_output = json.dumps(alerts)
            
            # Parse findings
            self.result.parsed_findings = self.parse_output(self.result.raw_output)
            
            # Generate report
            report_format = options.get("report_format", "html")
            if report_format in ["html", "xml", "json", "md", "pdf"]:
                report_path = options.get("report_path", os.path.join(self.temp_dir, f"zap-report.{report_format}"))
                
                # Generate and save the report
                if report_format == "html":
                    report = zap.core.htmlreport()
                    with open(report_path, "w") as f:
                        f.write(report)
                elif report_format == "xml":
                    report = zap.core.xmlreport()
                    with open(report_path, "w") as f:
                        f.write(report)
                elif report_format == "json":
                    report = json.dumps(alerts)
                    with open(report_path, "w") as f:
                        f.write(report)
                elif report_format == "md":
                    # Generate a markdown report
                    md_report = self._generate_markdown_report(self.result.parsed_findings, target)
                    with open(report_path, "w") as f:
                        f.write(md_report)
                    
                # Add report to result files
                self.result.add_result_file(report_path)
            
            # Mark as completed
            self.result.mark_completed()
            
            return self.result
        
        except Exception as e:
            logger.error(f"Error executing ZAP scan: {str(e)}")
            if self.result:
                self.result.set_error(f"Error executing ZAP scan: {str(e)}")
                return self.result
            else:
                # Create a new result with error
                result = ToolResult(
                    tool_name="zap",
                    command="ZAP API scan",
                    start_time=datetime.now(),
                    status="failed",
                    error_message=f"Error executing ZAP scan: {str(e)}"
                )
                return result
    
    def _generate_markdown_report(self, findings: List[Dict[str, Any]], target: str) -> str:
        """
        Generate a markdown report from the findings.
        
        Args:
            findings: List of parsed findings
            target: Target URL
            
        Returns:
            Markdown report
        """
        md = []
        md.append("# ZAP Security Scan Report")
        md.append("")
        md.append(f"**Target:** {target}")
        md.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append(f"**Total Issues Found:** {len(findings)}")
        md.append("")
        
        # Severity counts
        severity_counts = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 0,
            Severity.MEDIUM: 0,
            Severity.LOW: 0,
            Severity.INFO: 0
        }
        
        for finding in findings:
            severity = finding.get("severity", Severity.UNKNOWN)
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        md.append("## Summary")
        md.append("")
        md.append("| Severity | Count |")
        md.append("|---------|-------|")
        md.append(f"| Critical | {severity_counts.get(Severity.CRITICAL, 0)} |")
        md.append(f"| High | {severity_counts.get(Severity.HIGH, 0)} |")
        md.append(f"| Medium | {severity_counts.get(Severity.MEDIUM, 0)} |")
        md.append(f"| Low | {severity_counts.get(Severity.LOW, 0)} |")
        md.append(f"| Info | {severity_counts.get(Severity.INFO, 0)} |")
        md.append("")
        
        # Findings by severity
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            severity_findings = [f for f in findings if f.get("severity") == severity]
            if severity_findings:
                md.append(f"## {severity.title()} Severity Issues")
                md.append("")
                
                for i, finding in enumerate(severity_findings, 1):
                    md.append(f"### {i}. {finding.get('title', 'Unknown Issue')}")
                    md.append("")
                    
                    if "description" in finding and finding["description"]:
                        md.append("**Description**")
                        md.append("")
                        md.append(finding["description"])
                        md.append("")
                    
                    if "urls" in finding and finding["urls"]:
                        md.append("**Affected URLs**")
                        md.append("")
                        for url in finding["urls"]:
                            md.append(f"- {url}")
                        md.append("")
                    
                    if "evidence" in finding and finding["evidence"]:
                        md.append("**Evidence**")
                        md.append("")
                        md.append("```")
                        md.append(finding["evidence"])
                        md.append("```")
                        md.append("")
                    
                    if "solution" in finding and finding["solution"]:
                        md.append("**Solution**")
                        md.append("")
                        md.append(finding["solution"])
                        md.append("")
                    
                    if "references" in finding and finding["references"]:
                        md.append("**References**")
                        md.append("")
                        md.append(finding["references"])
                        md.append("")
                    
                    if "cweid" in finding and finding["cweid"]:
                        md.append(f"**CWE ID:** {finding['cweid']}")
                        md.append("")
                    
                    if "wascid" in finding and finding["wascid"]:
                        md.append(f"**WASC ID:** {finding['wascid']}")
                        md.append("")
        
        return "\n".join(md)
    
    def execute(self, options: Dict[str, Any]) -> ToolResult:
        """
        Execute a ZAP scan with the given options.
        
        Args:
            options: Scan options
            
        Returns:
            ToolResult with the scan results
        """
        if self.use_api:
            return self.execute_with_api(options)
        else:
            return super().execute(options)
    
    def __del__(self):
        """Clean up resources when the adapter is garbage collected."""
        self.stop_daemon()
        super().__del__()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the adapter
    zap_adapter = ZAPAdapter(use_api=True)
    
    # Execute a scan
    target = "https://example.com"
    result = zap_adapter.execute({
        "target": target,
        "spider": True,
        "ajax": False,
        "active_scan": True,
        "report_format": "html"
    })
    
    # Print results
    print(f"Scan completed with status: {result.status}")
    print(f"Found {len(result.parsed_findings)} issues")
    
    # Print findings by severity
    for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
        findings = [f for f in result.parsed_findings if f.get("severity") == severity]
        if findings:
            print(f"\n{severity.upper()} severity issues ({len(findings)}):")
            for finding in findings:
                print(f"- {finding.get('title')}")