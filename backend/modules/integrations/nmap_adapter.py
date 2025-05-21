#!/usr/bin/env python3
# SecureScout - Nmap Integration Adapter

import os
import json
import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

from .adapter_base import BaseToolAdapter, ToolResult, Severity

# Configure logging
logger = logging.getLogger("securescout.integrations.nmap")

class NmapAdapter(BaseToolAdapter):
    """
    Adapter for Nmap network scanner.
    
    This adapter provides functionality to run Nmap scans and parse the results.
    """
    
    def __init__(self, executable_path: Optional[str] = None):
        """
        Initialize the Nmap adapter.
        
        Args:
            executable_path: Path to the Nmap executable (if not in PATH)
        """
        super().__init__("nmap", executable_path)
    
    def prepare_command(self, options: Dict[str, Any]) -> str:
        """
        Prepare the command to execute Nmap with the given options.
        
        Args:
            options: Nmap scan options
            
        Returns:
            Command string to execute
        """
        # Get target(s)
        targets = options.get("targets", [])
        if isinstance(targets, str):
            targets = [targets]
        
        if not targets:
            raise ValueError("At least one target is required")
        
        target_str = " ".join(targets)
        
        # Build command
        cmd = f"{self.executable_path}"
        
        # Output format
        output_xml = os.path.join(self.temp_dir, "nmap-results.xml")
        cmd += f" -oX {output_xml}"
        
        # Add scan type
        scan_type = options.get("scan_type", "default")
        
        if scan_type == "quick":
            cmd += " -T4 -F"  # Fast scan of top 100 ports
        elif scan_type == "comprehensive":
            cmd += " -T4 -A -v"  # Aggressive scan with OS and version detection
        elif scan_type == "vulnerability":
            cmd += " -T4 -A --script vuln"  # Vulnerability scan
        elif scan_type == "service":
            cmd += " -T4 -sV"  # Service detection
        elif scan_type == "os":
            cmd += " -T4 -O"  # OS detection
        elif scan_type == "stealth":
            cmd += " -T2 -sS"  # Stealth SYN scan
        elif scan_type == "custom":
            # Custom scan options
            custom_options = options.get("custom_options", "")
            cmd += f" {custom_options}"
        else:
            # Default scan options
            cmd += " -T4 -A"  # Comprehensive scan with default settings
        
        # Add port specification if provided
        ports = options.get("ports")
        if ports:
            cmd += f" -p {ports}"
        
        # Add script specification if provided
        scripts = options.get("scripts")
        if scripts:
            if isinstance(scripts, list):
                scripts = ",".join(scripts)
            cmd += f" --script={scripts}"
        
        # Add the target(s)
        cmd += f" {target_str}"
        
        return cmd
    
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse the Nmap output and extract findings.
        
        Args:
            output: Raw Nmap output (not used as we read from XML file)
            
        Returns:
            List of parsed findings
        """
        findings = []
        
        # Look for the XML output file
        xml_file = os.path.join(self.temp_dir, "nmap-results.xml")
        
        if not os.path.exists(xml_file):
            logger.warning("Nmap XML output file not found")
            return findings
        
        try:
            # Parse the XML file
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Add the XML file to result files
            self.result.add_result_file(xml_file)
            
            # Extract scan information
            scan_info = {}
            
            # Get general scan info
            if root.find("scaninfo") is not None:
                scan_info = root.find("scaninfo").attrib
            
            # Process each host
            for host in root.findall(".//host"):
                host_data = self._parse_host(host)
                
                # Add host-level findings
                if "status" in host_data and host_data["status"] == "up":
                    # Basic host discovery finding
                    findings.append({
                        "title": f"Host Discovery: {host_data.get('address', 'Unknown')}",
                        "severity": Severity.INFO,
                        "description": f"Host {host_data.get('address')} is up and responding to scans.",
                        "host": host_data.get("address"),
                        "evidence": f"Status: {host_data.get('status')}",
                        "type": "host_discovery",
                        "raw": host_data
                    })
                
                # Process ports for the host
                if "ports" in host_data:
                    for port_data in host_data["ports"]:
                        findings.extend(self._process_port_findings(port_data, host_data))
                
                # Process OS detection findings
                if "os" in host_data and host_data["os"]:
                    findings.append({
                        "title": f"Operating System Detection: {host_data.get('address')}",
                        "severity": Severity.INFO,
                        "description": "Operating system information was detected.",
                        "host": host_data.get("address"),
                        "evidence": f"OS: {', '.join(host_data['os'])}",
                        "type": "os_detection",
                        "raw": {"host": host_data.get("address"), "os": host_data["os"]}
                    })
            
            # Process script output
            script_findings = self._process_script_findings(root)
            findings.extend(script_findings)
            
            # Add general scan info to result data
            if self.result:
                self.result.result_data["scan_info"] = scan_info
                
                # Add summary of findings
                severity_counts = {}
                for finding in findings:
                    severity = finding.get("severity", Severity.UNKNOWN)
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                self.result.result_data["summary"] = {
                    "total_findings": len(findings),
                    "severity_counts": severity_counts
                }
        
        except Exception as e:
            logger.error(f"Error parsing Nmap XML output: {str(e)}")
        
        return findings
    
    def _parse_host(self, host_elem: ET.Element) -> Dict[str, Any]:
        """
        Parse a host element from Nmap XML output.
        
        Args:
            host_elem: XML element for a host
            
        Returns:
            Dictionary with host information
        """
        host_data = {}
        
        # Get host status
        status_elem = host_elem.find("status")
        if status_elem is not None:
            host_data["status"] = status_elem.get("state")
        
        # Get addresses
        for addr_elem in host_elem.findall("address"):
            addr_type = addr_elem.get("addrtype")
            if addr_type == "ipv4" or addr_type == "ipv6":
                host_data["address"] = addr_elem.get("addr")
                host_data["address_type"] = addr_type
            elif addr_type == "mac":
                host_data["mac"] = addr_elem.get("addr")
                host_data["vendor"] = addr_elem.get("vendor")
        
        # Get hostnames
        hostnames = []
        hostnames_elem = host_elem.find("hostnames")
        if hostnames_elem is not None:
            for hostname_elem in hostnames_elem.findall("hostname"):
                hostnames.append(hostname_elem.get("name"))
        
        if hostnames:
            host_data["hostnames"] = hostnames
        
        # Get ports
        ports = []
        ports_elem = host_elem.find("ports")
        if ports_elem is not None:
            for port_elem in ports_elem.findall("port"):
                port_data = {
                    "protocol": port_elem.get("protocol"),
                    "portid": port_elem.get("portid"),
                }
                
                # Get state
                state_elem = port_elem.find("state")
                if state_elem is not None:
                    port_data["state"] = state_elem.get("state")
                    port_data["reason"] = state_elem.get("reason")
                
                # Get service information
                service_elem = port_elem.find("service")
                if service_elem is not None:
                    port_data["service"] = service_elem.get("name")
                    port_data["product"] = service_elem.get("product")
                    port_data["version"] = service_elem.get("version")
                    port_data["extrainfo"] = service_elem.get("extrainfo")
                    port_data["ostype"] = service_elem.get("ostype")
                
                # Get script output
                scripts = {}
                for script_elem in port_elem.findall("script"):
                    script_id = script_elem.get("id")
                    script_output = script_elem.get("output")
                    scripts[script_id] = script_output
                
                if scripts:
                    port_data["scripts"] = scripts
                
                ports.append(port_data)
        
        if ports:
            host_data["ports"] = ports
        
        # Get OS detection
        os_elem = host_elem.find("os")
        if os_elem is not None:
            os_matches = []
            for osmatch_elem in os_elem.findall("osmatch"):
                os_name = osmatch_elem.get("name")
                os_accuracy = osmatch_elem.get("accuracy")
                os_matches.append(f"{os_name} ({os_accuracy}% accuracy)")
            
            if os_matches:
                host_data["os"] = os_matches
        
        return host_data
    
    def _process_port_findings(self, port_data: Dict[str, Any], host_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process findings for a specific port.
        
        Args:
            port_data: Port data from XML output
            host_data: Host data from XML output
            
        Returns:
            List of findings for the port
        """
        findings = []
        
        # Only process open ports
        if port_data.get("state") != "open":
            return findings
        
        port_id = port_data.get("portid", "unknown")
        protocol = port_data.get("protocol", "unknown")
        service = port_data.get("service", "unknown")
        
        # Create a basic open port finding
        findings.append({
            "title": f"Open Port: {port_id}/{protocol} ({service})",
            "severity": Severity.INFO,
            "description": f"Port {port_id}/{protocol} is open on host {host_data.get('address')}.",
            "host": host_data.get("address"),
            "port": port_id,
            "protocol": protocol,
            "service": service,
            "evidence": self._format_port_evidence(port_data),
            "type": "open_port",
            "raw": port_data
        })
        
        # Check for version information
        if "product" in port_data or "version" in port_data:
            version_info = []
            if port_data.get("product"):
                version_info.append(port_data["product"])
            if port_data.get("version"):
                version_info.append(port_data["version"])
            if port_data.get("extrainfo"):
                version_info.append(port_data["extrainfo"])
            
            version_str = " ".join(version_info)
            
            findings.append({
                "title": f"Service Version: {service} {version_str}",
                "severity": Severity.INFO,
                "description": f"Service version information was detected for {service} on port {port_id}/{protocol}.",
                "host": host_data.get("address"),
                "port": port_id,
                "protocol": protocol,
                "service": service,
                "version": version_str,
                "evidence": self._format_port_evidence(port_data),
                "type": "service_version",
                "raw": port_data
            })
        
        # Check for script results
        if "scripts" in port_data:
            for script_id, script_output in port_data["scripts"].items():
                # Determine severity based on script ID
                severity = Severity.INFO
                if "vuln" in script_id:
                    severity = Severity.HIGH
                elif "exploit" in script_id:
                    severity = Severity.CRITICAL
                elif "brute" in script_id and "successful" in script_output.lower():
                    severity = Severity.HIGH
                elif any(x in script_id for x in ["default", "guess", "weak"]):
                    severity = Severity.MEDIUM
                
                findings.append({
                    "title": f"Script: {script_id}",
                    "severity": severity,
                    "description": f"Nmap script {script_id} produced output for {service} on port {port_id}/{protocol}.",
                    "host": host_data.get("address"),
                    "port": port_id,
                    "protocol": protocol,
                    "service": service,
                    "script": script_id,
                    "evidence": script_output,
                    "type": "script_output",
                    "raw": {"script_id": script_id, "output": script_output}
                })
        
        return findings
    
    def _process_script_findings(self, root: ET.Element) -> List[Dict[str, Any]]:
        """
        Process findings from host-level script output.
        
        Args:
            root: Root element from Nmap XML output
            
        Returns:
            List of script findings
        """
        findings = []
        
        # Look for all script outputs in the XML
        for script_elem in root.findall(".//hostscript/script"):
            script_id = script_elem.get("id")
            script_output = script_elem.get("output")
            
            # Find the host this script is associated with
            host_elem = script_elem.find("../../..")
            host_address = "unknown"
            
            # Get host address
            addr_elem = host_elem.find("address[@addrtype='ipv4']")
            if addr_elem is not None:
                host_address = addr_elem.get("addr")
            
            # Determine severity based on script ID
            severity = Severity.INFO
            if "vuln" in script_id:
                severity = Severity.HIGH
            elif "exploit" in script_id:
                severity = Severity.CRITICAL
            elif "brute" in script_id and "successful" in script_output.lower():
                severity = Severity.HIGH
            elif any(x in script_id for x in ["default", "guess", "weak"]):
                severity = Severity.MEDIUM
            
            findings.append({
                "title": f"Host Script: {script_id}",
                "severity": severity,
                "description": f"Nmap script {script_id} produced output for host {host_address}.",
                "host": host_address,
                "script": script_id,
                "evidence": script_output,
                "type": "host_script_output",
                "raw": {"script_id": script_id, "output": script_output}
            })
        
        # Process vulnerability scripts specifically
        for finding in findings:
            script_id = finding.get("script", "")
            if "vuln" in script_id:
                # Make the title more descriptive for vulnerabilities
                if "cve" in script_id.lower():
                    # Extract the CVE identifier
                    import re
                    cve_match = re.search(r'cve-\d+-\d+', script_id, re.IGNORECASE)
                    if cve_match:
                        cve_id = cve_match.group(0).upper()
                        finding["title"] = f"Vulnerability: {cve_id}"
                        finding["cve"] = cve_id
                else:
                    # Non-CVE vulnerability
                    finding["title"] = f"Vulnerability: {script_id.replace('vuln-', '')}"
        
        return findings
    
    def _format_port_evidence(self, port_data: Dict[str, Any]) -> str:
        """
        Format port data as a string for evidence.
        
        Args:
            port_data: Port data from XML output
            
        Returns:
            Formatted port evidence string
        """
        evidence = []
        evidence.append(f"Port: {port_data.get('portid')}/{port_data.get('protocol')}")
        evidence.append(f"State: {port_data.get('state')} ({port_data.get('reason', 'unknown reason')})")
        
        if port_data.get("service"):
            evidence.append(f"Service: {port_data.get('service')}")
        
        if port_data.get("product"):
            product_line = f"Product: {port_data.get('product')}"
            if port_data.get("version"):
                product_line += f" {port_data.get('version')}"
            if port_data.get("extrainfo"):
                product_line += f" ({port_data.get('extrainfo')})"
            evidence.append(product_line)
        
        return "\n".join(evidence)
    
    def execute(self, options: Dict[str, Any]) -> ToolResult:
        """
        Execute an Nmap scan with the given options.
        
        Args:
            options: Scan options
            
        Returns:
            ToolResult with the scan results
        """
        # Execute the scan
        result = super().execute(options)
        
        # Generate additional report formats if requested
        if "report_formats" in options and result.status == "completed":
            report_formats = options["report_formats"]
            
            if isinstance(report_formats, str):
                report_formats = [report_formats]
            
            xml_file = os.path.join(self.temp_dir, "nmap-results.xml")
            
            if os.path.exists(xml_file):
                for report_format in report_formats:
                    if report_format.lower() == "html":
                        # Generate HTML report using xsltproc if available
                        html_file = os.path.join(self.temp_dir, "nmap-results.html")
                        try:
                            xslt_file = "/usr/share/nmap/nmap.xsl"  # Default location
                            
                            if not os.path.exists(xslt_file):
                                # Try to find the XSL file
                                for path in [
                                    "/usr/local/share/nmap/nmap.xsl",
                                    "/opt/local/share/nmap/nmap.xsl",
                                    "/usr/share/nmap/nmap.xsl"
                                ]:
                                    if os.path.exists(path):
                                        xslt_file = path
                                        break
                            
                            if os.path.exists(xslt_file):
                                cmd = f"xsltproc -o {html_file} {xslt_file} {xml_file}"
                                os.system(cmd)
                                
                                if os.path.exists(html_file):
                                    result.add_result_file(html_file)
                        
                        except Exception as e:
                            logger.error(f"Error generating HTML report: {str(e)}")
                    
                    elif report_format.lower() == "json":
                        # Generate JSON report
                        json_file = os.path.join(self.temp_dir, "nmap-results.json")
                        try:
                            import xmltodict
                            
                            with open(xml_file, "r") as f:
                                xml_data = f.read()
                            
                            xml_dict = xmltodict.parse(xml_data)
                            
                            with open(json_file, "w") as f:
                                json.dump(xml_dict, f, indent=2)
                            
                            result.add_result_file(json_file)
                        
                        except Exception as e:
                            logger.error(f"Error generating JSON report: {str(e)}")
                            
        return result


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the adapter
    nmap_adapter = NmapAdapter()
    
    # Execute a scan
    targets = ["localhost", "scanme.nmap.org"]
    result = nmap_adapter.execute({
        "targets": targets,
        "scan_type": "comprehensive",
        "report_formats": ["html", "json"]
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