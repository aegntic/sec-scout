#!/usr/bin/env python3
# SecureScout - Trivy Container Scanner Integration Adapter

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

from .adapter_base import BaseToolAdapter, ToolResult, Severity

# Configure logging
logger = logging.getLogger("securescout.integrations.trivy")

class TrivyAdapter(BaseToolAdapter):
    """
    Adapter for Trivy container vulnerability scanner.
    
    This adapter provides functionality to run Trivy scans and parse the results.
    """
    
    def __init__(self, executable_path: Optional[str] = None):
        """
        Initialize the Trivy adapter.
        
        Args:
            executable_path: Path to the Trivy executable (if not in PATH)
        """
        super().__init__("trivy", executable_path)
    
    def prepare_command(self, options: Dict[str, Any]) -> str:
        """
        Prepare the command to execute Trivy with the given options.
        
        Args:
            options: Trivy scan options
            
        Returns:
            Command string to execute
        """
        # Get target
        target = options.get("target")
        if not target:
            raise ValueError("Target is required")
        
        # Get scan type
        scan_type = options.get("scan_type", "image")
        
        # Build command
        cmd = f"{self.executable_path}"
        
        # Output format
        output_format = options.get("format", "json")
        output_file = os.path.join(self.temp_dir, f"trivy-results.{output_format}")
        cmd += f" --format {output_format} --output {output_file}"
        
        # Set severity level if provided
        severity = options.get("severity")
        if severity:
            cmd += f" --severity {severity}"
        
        # Set vulnerability type if provided
        vuln_type = options.get("vuln_type")
        if vuln_type:
            cmd += f" --vuln-type {vuln_type}"
        
        # Set ignore unfixed flag if provided
        ignore_unfixed = options.get("ignore_unfixed", False)
        if ignore_unfixed:
            cmd += " --ignore-unfixed"
        
        # Set security checks if provided
        security_checks = options.get("security_checks")
        if security_checks:
            if isinstance(security_checks, list):
                security_checks = ",".join(security_checks)
            cmd += f" --security-checks {security_checks}"
        
        # Set exit code if provided
        exit_code = options.get("exit_code")
        if exit_code is not None:
            cmd += f" --exit-code {exit_code}"
        else:
            # Default to not failing on vulnerabilities for integration purposes
            cmd += " --exit-code 0"
        
        # Add quiet flag if provided
        quiet = options.get("quiet", False)
        if quiet:
            cmd += " --quiet"
        
        # Add debug flag if provided
        debug = options.get("debug", False)
        if debug:
            cmd += " --debug"
        
        # Add the scan type and target
        cmd += f" {scan_type} {target}"
        
        return cmd
    
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse the Trivy output and extract findings.
        
        Args:
            output: Raw Trivy output (not used as we read from JSON file)
            
        Returns:
            List of parsed findings
        """
        findings = []
        
        # Look for the JSON output file
        json_file = os.path.join(self.temp_dir, "trivy-results.json")
        
        if not os.path.exists(json_file):
            logger.warning("Trivy JSON output file not found")
            return findings
        
        try:
            # Read the JSON file
            with open(json_file, "r") as f:
                data = json.load(f)
            
            # Add the JSON file to result files
            self.result.add_result_file(json_file)
            
            # Extract scan information
            if "Metadata" in data:
                self.result.result_data["metadata"] = data["Metadata"]
            
            # Process vulnerabilities
            if "Results" in data:
                for result in data["Results"]:
                    # Get target info
                    target_name = result.get("Target", "Unknown")
                    target_type = result.get("Type", "Unknown")
                    
                    # Process vulnerabilities
                    if "Vulnerabilities" in result and result["Vulnerabilities"]:
                        for vuln in result["Vulnerabilities"]:
                            finding = self._process_vulnerability(vuln, target_name, target_type)
                            findings.append(finding)
                    
                    # Process misconfigurations
                    if "Misconfigurations" in result and result["Misconfigurations"]:
                        for misconfig in result["Misconfigurations"]:
                            finding = self._process_misconfiguration(misconfig, target_name, target_type)
                            findings.append(finding)
                    
                    # Process secrets
                    if "Secrets" in result and result["Secrets"]:
                        for secret in result["Secrets"]:
                            finding = self._process_secret(secret, target_name, target_type)
                            findings.append(finding)
            
            # Add summary of findings to result data
            if self.result:
                # Count findings by severity
                severity_counts = {}
                for finding in findings:
                    severity = finding.get("severity", Severity.UNKNOWN)
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                self.result.result_data["summary"] = {
                    "total_findings": len(findings),
                    "severity_counts": severity_counts
                }
        
        except Exception as e:
            logger.error(f"Error parsing Trivy output: {str(e)}")
        
        return findings
    
    def _process_vulnerability(self, vuln: Dict[str, Any], target_name: str, target_type: str) -> Dict[str, Any]:
        """
        Process a vulnerability from Trivy output.
        
        Args:
            vuln: Vulnerability data
            target_name: Name of the target (image, filesystem, etc.)
            target_type: Type of the target
            
        Returns:
            Processed finding
        """
        # Map Trivy severity to our standard severity
        severity_mapping = {
            "CRITICAL": Severity.CRITICAL,
            "HIGH": Severity.HIGH,
            "MEDIUM": Severity.MEDIUM,
            "LOW": Severity.LOW,
            "UNKNOWN": Severity.UNKNOWN
        }
        
        trivy_severity = vuln.get("Severity", "UNKNOWN")
        severity = severity_mapping.get(trivy_severity, Severity.UNKNOWN)
        
        # Create the finding
        finding = {
            "title": f"Vulnerability: {vuln.get('VulnerabilityID', 'Unknown')}",
            "severity": severity,
            "description": vuln.get("Description", "No description available"),
            "target": target_name,
            "target_type": target_type,
            "package_name": vuln.get("PkgName"),
            "installed_version": vuln.get("InstalledVersion"),
            "fixed_version": vuln.get("FixedVersion"),
            "vulnerability_id": vuln.get("VulnerabilityID"),
            "references": vuln.get("References", []),
            "cvss": vuln.get("CVSS"),
            "cwe_ids": vuln.get("CweIDs", []),
            "type": "vulnerability",
            "raw": vuln
        }
        
        # Generate evidence text
        evidence = []
        evidence.append(f"Vulnerability ID: {vuln.get('VulnerabilityID', 'Unknown')}")
        evidence.append(f"Package: {vuln.get('PkgName', 'Unknown')}")
        evidence.append(f"Installed Version: {vuln.get('InstalledVersion', 'Unknown')}")
        
        if vuln.get("FixedVersion"):
            evidence.append(f"Fixed Version: {vuln.get('FixedVersion')}")
        
        if vuln.get("Title"):
            evidence.append(f"Title: {vuln.get('Title')}")
        
        if vuln.get("Description"):
            evidence.append(f"Description: {vuln.get('Description')}")
        
        finding["evidence"] = "\n".join(evidence)
        
        return finding
    
    def _process_misconfiguration(self, misconfig: Dict[str, Any], target_name: str, target_type: str) -> Dict[str, Any]:
        """
        Process a misconfiguration from Trivy output.
        
        Args:
            misconfig: Misconfiguration data
            target_name: Name of the target (image, filesystem, etc.)
            target_type: Type of the target
            
        Returns:
            Processed finding
        """
        # Map Trivy severity to our standard severity
        severity_mapping = {
            "CRITICAL": Severity.CRITICAL,
            "HIGH": Severity.HIGH,
            "MEDIUM": Severity.MEDIUM,
            "LOW": Severity.LOW,
            "UNKNOWN": Severity.UNKNOWN
        }
        
        trivy_severity = misconfig.get("Severity", "UNKNOWN")
        severity = severity_mapping.get(trivy_severity, Severity.UNKNOWN)
        
        # Create the finding
        finding = {
            "title": f"Misconfiguration: {misconfig.get('Title', 'Unknown')}",
            "severity": severity,
            "description": misconfig.get("Description", "No description available"),
            "target": target_name,
            "target_type": target_type,
            "id": misconfig.get("ID"),
            "message": misconfig.get("Message"),
            "resolution": misconfig.get("Resolution"),
            "references": misconfig.get("References", []),
            "type": "misconfiguration",
            "raw": misconfig
        }
        
        # Generate evidence text
        evidence = []
        evidence.append(f"ID: {misconfig.get('ID', 'Unknown')}")
        
        if misconfig.get("Title"):
            evidence.append(f"Title: {misconfig.get('Title')}")
        
        if misconfig.get("Message"):
            evidence.append(f"Message: {misconfig.get('Message')}")
        
        if misconfig.get("Resolution"):
            evidence.append(f"Resolution: {misconfig.get('Resolution')}")
        
        if "CauseMetadata" in misconfig:
            metadata = misconfig["CauseMetadata"]
            if "Resource" in metadata:
                evidence.append(f"Resource: {metadata['Resource']}")
            if "Provider" in metadata:
                evidence.append(f"Provider: {metadata['Provider']}")
            if "Service" in metadata:
                evidence.append(f"Service: {metadata['Service']}")
            if "Code" in metadata:
                evidence.append(f"Code:\n{metadata['Code']['Lines'][0]['Content']}")
        
        finding["evidence"] = "\n".join(evidence)
        
        return finding
    
    def _process_secret(self, secret: Dict[str, Any], target_name: str, target_type: str) -> Dict[str, Any]:
        """
        Process a secret from Trivy output.
        
        Args:
            secret: Secret data
            target_name: Name of the target (image, filesystem, etc.)
            target_type: Type of the target
            
        Returns:
            Processed finding
        """
        # Secrets are usually critical
        severity = Severity.CRITICAL
        
        # Create the finding
        finding = {
            "title": f"Secret: {secret.get('Category', 'Unknown')}",
            "severity": severity,
            "description": f"Secret of type {secret.get('RuleID', 'Unknown')} found in {target_name}",
            "target": target_name,
            "target_type": target_type,
            "rule_id": secret.get("RuleID"),
            "category": secret.get("Category"),
            "title": secret.get("Title"),
            "match": secret.get("Match"),
            "type": "secret",
            "raw": secret
        }
        
        # Generate evidence text
        evidence = []
        evidence.append(f"Rule ID: {secret.get('RuleID', 'Unknown')}")
        evidence.append(f"Category: {secret.get('Category', 'Unknown')}")
        
        if secret.get("Title"):
            evidence.append(f"Title: {secret.get('Title')}")
        
        if secret.get("Match"):
            # Redact the actual secret value for security
            match = secret.get("Match")
            # Keep first 2 chars and last 2 chars, replace rest with *
            if len(match) > 6:
                redacted = match[:2] + "*" * (len(match) - 4) + match[-2:]
            else:
                redacted = "*" * len(match)
            evidence.append(f"Match: {redacted}")
        
        if "Code" in secret:
            code = secret["Code"]
            evidence.append(f"File: {code.get('Path', 'Unknown')}")
            
            if "Lines" in code:
                line = code["Lines"][0]
                line_number = line.get("Number")
                line_content = line.get("Content", "")
                
                # Redact the line content containing the secret
                if line_content and secret.get("Match"):
                    match = secret.get("Match")
                    redacted_content = line_content.replace(match, "*" * len(match))
                    evidence.append(f"Line {line_number}: {redacted_content}")
        
        finding["evidence"] = "\n".join(evidence)
        
        return finding
    
    def execute(self, options: Dict[str, Any]) -> ToolResult:
        """
        Execute a Trivy scan with the given options.
        
        Args:
            options: Scan options
            
        Returns:
            ToolResult with the scan results
        """
        # Add default security checks if not specified
        if "security_checks" not in options:
            options["security_checks"] = "vuln,secret,config"
        
        # Execute the scan
        result = super().execute(options)
        
        # Generate additional report formats if requested
        if "report_formats" in options and result.status == "completed":
            report_formats = options["report_formats"]
            
            if isinstance(report_formats, str):
                report_formats = [report_formats]
            
            # Get the target
            target = options.get("target", "unknown")
            
            # Generate other formats directly from Trivy
            for format_name in report_formats:
                if format_name.lower() not in ["json", "table", "html", "sarif", "cyclonedx"]:
                    logger.warning(f"Unsupported report format: {format_name}")
                    continue
                
                # Skip JSON as it's the default
                if format_name.lower() == "json":
                    continue
                
                # Execute Trivy again with different format
                format_options = options.copy()
                format_options["format"] = format_name.lower()
                
                # Prepare command for this format
                cmd = self.prepare_command(format_options)
                
                try:
                    # Execute command directly
                    import subprocess
                    process = subprocess.run(
                        cmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=self.temp_dir
                    )
                    
                    # Check if the report was generated
                    report_file = os.path.join(self.temp_dir, f"trivy-results.{format_name.lower()}")
                    if os.path.exists(report_file):
                        result.add_result_file(report_file)
                        logger.info(f"Generated {format_name} report: {report_file}")
                
                except Exception as e:
                    logger.error(f"Error generating {format_name} report: {str(e)}")
        
        return result


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the adapter
    trivy_adapter = TrivyAdapter()
    
    # Execute a scan
    target = "alpine:latest"
    result = trivy_adapter.execute({
        "target": target,
        "scan_type": "image",
        "security_checks": "vuln,secret,config",
        "report_formats": ["json", "html"]
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