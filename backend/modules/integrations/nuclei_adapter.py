#!/usr/bin/env python3
# SecureScout - Nuclei Integration Adapter

import os
import json
import logging
import subprocess
import tempfile
import re
import yaml
import shutil
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path

from .adapter_base import BaseToolAdapter, Severity, ToolResult

# Configure logging
logger = logging.getLogger("securescout.integrations.nuclei")

class NucleiTemplateManager:
    """
    Manager for Nuclei templates.
    
    This class provides functionality to manage Nuclei templates,
    including updates, custom templates, and template selection.
    """
    
    def __init__(self, nuclei_executable: str, custom_templates_dir: Optional[str] = None):
        """
        Initialize the template manager.
        
        Args:
            nuclei_executable: Path to the Nuclei executable
            custom_templates_dir: Path to custom templates directory
        """
        self.nuclei_executable = nuclei_executable
        self.custom_templates_dir = custom_templates_dir
        
        # Default template directories
        self.default_template_dir = os.path.expanduser("~/.config/nuclei/templates")
        
        # Create custom templates directory if specified and doesn't exist
        if self.custom_templates_dir and not os.path.exists(self.custom_templates_dir):
            os.makedirs(self.custom_templates_dir, exist_ok=True)
    
    def update_templates(self) -> bool:
        """
        Update the Nuclei templates.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Updating Nuclei templates")
            
            result = subprocess.run(
                [self.nuclei_executable, "-update-templates"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                logger.info("Templates updated successfully")
                return True
            else:
                logger.error(f"Error updating templates: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating templates: {e}")
            return False
    
    def list_templates(self, filter_tags: Optional[List[str]] = None, filter_severity: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List available templates with optional filtering.
        
        Args:
            filter_tags: List of tags to filter by
            filter_severity: List of severity levels to filter by
            
        Returns:
            List of template information dictionaries
        """
        templates = []
        
        # Create the template paths to search
        template_paths = [self.default_template_dir]
        if self.custom_templates_dir:
            template_paths.append(self.custom_templates_dir)
        
        # Search for template files
        for template_dir in template_paths:
            if not os.path.exists(template_dir):
                continue
                
            for root, _, files in os.walk(template_dir):
                for file in files:
                    if file.endswith(('.yaml', '.yml')):
                        template_path = os.path.join(root, file)
                        template_info = self._parse_template_info(template_path)
                        
                        if template_info:
                            # Apply filters
                            if filter_tags and not any(tag in template_info.get('tags', []) for tag in filter_tags):
                                continue
                                
                            if filter_severity and template_info.get('severity') not in filter_severity:
                                continue
                                
                            templates.append(template_info)
        
        return templates
    
    def _parse_template_info(self, template_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse template file to extract information.
        
        Args:
            template_path: Path to the template file
            
        Returns:
            Dictionary with template information
        """
        try:
            with open(template_path, 'r') as f:
                template = yaml.safe_load(f)
            
            if not template:
                return None
                
            template_info = {
                'id': template.get('id'),
                'path': template_path,
                'name': None,
                'author': None,
                'description': None,
                'severity': None,
                'tags': []
            }
            
            # Extract info section
            info = template.get('info', {})
            if info:
                template_info.update({
                    'name': info.get('name'),
                    'author': info.get('author'),
                    'description': info.get('description'),
                    'severity': info.get('severity', 'unknown'),
                    'tags': info.get('tags', [])
                })
            
            return template_info
            
        except Exception as e:
            logger.error(f"Error parsing template {template_path}: {e}")
            return None
    
    def find_templates_by_tags(self, tags: List[str]) -> List[str]:
        """
        Find templates matching the specified tags.
        
        Args:
            tags: List of tags to match
            
        Returns:
            List of template paths
        """
        template_info_list = self.list_templates(filter_tags=tags)
        return [template_info['path'] for template_info in template_info_list]
    
    def find_templates_by_severity(self, severities: List[str]) -> List[str]:
        """
        Find templates matching the specified severity levels.
        
        Args:
            severities: List of severity levels to match
            
        Returns:
            List of template paths
        """
        template_info_list = self.list_templates(filter_severity=severities)
        return [template_info['path'] for template_info in template_info_list]
    
    def add_custom_template(self, template_content: str, template_name: str) -> str:
        """
        Add a custom template.
        
        Args:
            template_content: Content of the template
            template_name: Name of the template file
            
        Returns:
            Path to the added template
        """
        if not self.custom_templates_dir:
            raise ValueError("Custom templates directory not specified")
        
        # Ensure the template has a .yaml extension
        if not template_name.endswith(('.yaml', '.yml')):
            template_name += '.yaml'
        
        template_path = os.path.join(self.custom_templates_dir, template_name)
        
        try:
            # Write the template content to file
            with open(template_path, 'w') as f:
                f.write(template_content)
            
            logger.info(f"Added custom template: {template_path}")
            return template_path
            
        except Exception as e:
            logger.error(f"Error adding custom template: {e}")
            raise
    
    def remove_custom_template(self, template_name: str) -> bool:
        """
        Remove a custom template.
        
        Args:
            template_name: Name of the template to remove
            
        Returns:
            True if successful, False otherwise
        """
        if not self.custom_templates_dir:
            return False
        
        # Ensure the template has a .yaml extension
        if not template_name.endswith(('.yaml', '.yml')):
            template_name += '.yaml'
        
        template_path = os.path.join(self.custom_templates_dir, template_name)
        
        try:
            if os.path.exists(template_path):
                os.remove(template_path)
                logger.info(f"Removed custom template: {template_path}")
                return True
            else:
                logger.warning(f"Template not found: {template_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing custom template: {e}")
            return False


class NucleiAdapter(BaseToolAdapter):
    """
    Adapter for Nuclei vulnerability scanner.
    
    This adapter provides functionality to run Nuclei scans and parse the results.
    It includes template management and customization capabilities.
    """
    
    def __init__(self, executable_path: Optional[str] = None, custom_templates_dir: Optional[str] = None):
        """
        Initialize the Nuclei adapter.
        
        Args:
            executable_path: Path to the Nuclei executable
            custom_templates_dir: Path to custom templates directory
        """
        super().__init__("nuclei", executable_path)
        self.custom_templates_dir = custom_templates_dir
        self.template_manager = None
    
    def _find_executable(self) -> Optional[str]:
        """
        Find the Nuclei executable in the system PATH.
        
        Returns:
            Path to the Nuclei executable or None if not found
        """
        # First try the parent class implementation
        executable_path = super()._find_executable()
        if executable_path:
            return executable_path
        
        # Additional Nuclei-specific locations
        common_locations = [
            "/usr/local/bin/nuclei",
            "/usr/bin/nuclei",
            "/snap/bin/nuclei",
            os.path.expanduser("~/go/bin/nuclei")
        ]
        
        for location in common_locations:
            if os.path.exists(location) and os.access(location, os.X_OK):
                return location
        
        return None
    
    def initialize_template_manager(self) -> None:
        """Initialize the template manager if not already initialized."""
        if not self.template_manager and self.executable_path:
            self.template_manager = NucleiTemplateManager(self.executable_path, self.custom_templates_dir)
    
    def update_templates(self) -> bool:
        """
        Update the Nuclei templates.
        
        Returns:
            True if successful, False otherwise
        """
        self.initialize_template_manager()
        if self.template_manager:
            return self.template_manager.update_templates()
        return False
    
    def prepare_command(self, options: Dict[str, Any]) -> str:
        """
        Prepare the command to execute Nuclei with the given options.
        
        Args:
            options: Nuclei-specific options
            
        Returns:
            Command string to execute
        """
        # Initialize template manager if needed
        self.initialize_template_manager()
        
        # Base command
        command = f"{self.executable_path}"
        
        # Target URLs
        if "url" in options:
            command += f" -u {options['url']}"
        elif "urls_file" in options:
            command += f" -l {options['urls_file']}"
        else:
            raise ValueError("No target URL or URLs file specified")
        
        # Template selection
        if "templates" in options:
            templates = options["templates"]
            if isinstance(templates, list):
                templates_str = ",".join(templates)
                command += f" -t {templates_str}"
            else:
                command += f" -t {templates}"
        elif "tags" in options:
            tags = options["tags"]
            if isinstance(tags, list):
                tags_str = ",".join(tags)
                command += f" -tags {tags_str}"
            else:
                command += f" -tags {tags}"
        
        # Severity filtering
        if "severity" in options:
            severity = options["severity"]
            if isinstance(severity, list):
                severity_str = ",".join(severity)
                command += f" -severity {severity_str}"
            else:
                command += f" -severity {severity}"
        
        # Rate limiting
        if "rate_limit" in options:
            command += f" -rate-limit {options['rate_limit']}"
        else:
            # Default rate limit to prevent overwhelming the target
            command += " -rate-limit 150"
        
        # Output formatting
        command += " -json"  # Always use JSON output for parsing
        
        # Output file
        if self.temp_dir:
            output_file = os.path.join(self.temp_dir, "nuclei-output.json")
            command += f" -o {output_file}"
        
        # Authentication headers
        if "headers" in options:
            headers = options["headers"]
            for header, value in headers.items():
                command += f" -H \"{header}: {value}\""
        
        # Include request/response
        if options.get("include_request_response", False):
            command += " -irr"
        
        # Additional arguments
        if "extra_args" in options:
            command += f" {options['extra_args']}"
        
        return command
    
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse the Nuclei output and extract findings.
        
        Args:
            output: Raw Nuclei JSON output
            
        Returns:
            List of parsed findings
        """
        findings = []
        
        # Try to parse the output as JSON lines
        for line in output.strip().split('\n'):
            if not line:
                continue
                
            try:
                finding_data = json.loads(line)
                finding = self._process_finding(finding_data)
                if finding:
                    findings.append(finding)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON line: {line}")
        
        # If no findings were parsed, try parsing the output as a single JSON blob
        if not findings and output.strip():
            try:
                finding_data = json.loads(output)
                if isinstance(finding_data, list):
                    for item in finding_data:
                        finding = self._process_finding(item)
                        if finding:
                            findings.append(finding)
                else:
                    finding = self._process_finding(finding_data)
                    if finding:
                        findings.append(finding)
            except json.JSONDecodeError:
                logger.warning("Failed to parse output as JSON")
        
        return findings
    
    def _process_finding(self, finding_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single finding from Nuclei.
        
        Args:
            finding_data: Raw finding data
            
        Returns:
            Processed finding dictionary
        """
        try:
            if not isinstance(finding_data, dict):
                return None
                
            # Extract basic information
            template_id = finding_data.get("template-id") or finding_data.get("templateID")
            if not template_id:
                return None
                
            info = finding_data.get("info", {})
            if not info:
                return None
                
            name = info.get("name")
            severity = info.get("severity", "unknown")
            tags = info.get("tags", [])
            description = info.get("description", "")
            
            # Extract target information
            host = finding_data.get("host") or finding_data.get("ip")
            matched_at = finding_data.get("matched-at") or finding_data.get("matched")
            
            # Extract request and response if available
            request = finding_data.get("request", "")
            response = finding_data.get("response", "")
            
            # Format finding
            finding = {
                "title": name or template_id,
                "severity": self._normalize_severity(severity),
                "description": description,
                "template_id": template_id,
                "host": host,
                "url": matched_at,
                "tags": tags,
                "evidence": {
                    "request": request,
                    "response": response,
                    "curl": finding_data.get("curl-command", "")
                },
                "remediation": info.get("remediation", "")
            }
            
            return finding
            
        except Exception as e:
            logger.error(f"Error processing finding: {e}")
            return None
    
    def _normalize_severity(self, severity: str) -> str:
        """
        Normalize Nuclei severity to SecureScout severity.
        
        Args:
            severity: Nuclei severity string
            
        Returns:
            Normalized severity string
        """
        severity = severity.lower()
        
        if severity == "critical":
            return Severity.CRITICAL
        elif severity == "high":
            return Severity.HIGH
        elif severity == "medium":
            return Severity.MEDIUM
        elif severity == "low":
            return Severity.LOW
        elif severity == "info":
            return Severity.INFO
        else:
            return Severity.UNKNOWN
    
    def add_custom_template(self, template_content: str, template_name: str) -> str:
        """
        Add a custom template for Nuclei.
        
        Args:
            template_content: Content of the template
            template_name: Name of the template file
            
        Returns:
            Path to the added template
        """
        self.initialize_template_manager()
        if not self.template_manager:
            raise ValueError("Template manager not initialized")
            
        return self.template_manager.add_custom_template(template_content, template_name)
    
    def list_templates(self, filter_tags: Optional[List[str]] = None, filter_severity: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List available templates with optional filtering.
        
        Args:
            filter_tags: List of tags to filter by
            filter_severity: List of severity levels to filter by
            
        Returns:
            List of template information dictionaries
        """
        self.initialize_template_manager()
        if not self.template_manager:
            return []
            
        return self.template_manager.list_templates(filter_tags, filter_severity)
    
    def execute(self, options: Dict[str, Any]) -> ToolResult:
        """
        Execute Nuclei with the given options.
        
        Args:
            options: Nuclei-specific options
            
        Returns:
            ToolResult object with execution results
        """
        # Use the parent class execute method
        result = super().execute(options)
        
        # Check if additional output file needs to be processed
        if self.temp_dir and result.status == "completed":
            output_file = os.path.join(self.temp_dir, "nuclei-output.json")
            if os.path.exists(output_file):
                try:
                    with open(output_file, 'r') as f:
                        output_content = f.read()
                    
                    # If we have no findings yet, try to parse from the output file
                    if not result.parsed_findings:
                        result.parsed_findings = self.parse_output(output_content)
                    
                    # Add the output file to result files
                    result.add_result_file(output_file)
                    
                except Exception as e:
                    logger.error(f"Error processing output file: {e}")
        
        return result


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example adapter usage
    adapter = NucleiAdapter()
    
    # Update templates
    # adapter.update_templates()
    
    # List templates with tag filtering
    # templates = adapter.list_templates(filter_tags=["cve"])
    # for template in templates[:5]:  # Show first 5 templates
    #     print(f"{template['id']} - {template['name']} ({template['severity']})")
    
    # Example scan options
    test_options = {
        "url": "https://example.com",
        "tags": "cve,oast",
        "severity": ["critical", "high"],
        "rate_limit": 100
    }
    
    # Execute and get results
    # result = adapter.execute(test_options)
    
    # Print results
    # print(json.dumps(result.to_dict(), indent=2))