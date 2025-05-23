#!/usr/bin/env python3
"""Mock adapter for testing when actual tool is not installed"""

from modules.integrations.adapter_base import ToolAdapter
import random
import time

class MockNmapAdapter(ToolAdapter):
    """Mock adapter for nmap - simulates real tool behavior"""
    
    def __init__(self):
        super().__init__("nmap_mock", "Mock Nmap Adapter")
        self.mock_mode = True
    
    def execute(self, target, options=None):
        """Simulate tool execution"""
        self.logger.info(f"Mock nmap scan started on {target}")
        
        # Simulate processing time
        time.sleep(random.uniform(1, 3))
        
        # Generate mock results
        results = {
            "success": True,
            "target": target,
            "findings": self._generate_mock_findings(target),
            "raw_output": f"Mock nmap scan completed",
            "tool": "nmap_mock"
        }
        
        return results
    
    def _generate_mock_findings(self, target):
        """Generate realistic mock findings"""
        findings = []
        
        # Add some mock vulnerabilities
        vuln_types = [
            ("Information Disclosure", "Low", "Server header exposes version"),
            ("Missing Security Headers", "Medium", "X-Frame-Options not set"),
            ("SSL/TLS Issues", "Medium", "Weak ciphers supported"),
            ("Potential SQL Injection", "High", "Parameter 'id' may be vulnerable")
        ]
        
        for i, (title, severity, desc) in enumerate(random.sample(vuln_types, k=random.randint(1, 3))):
            findings.append({
                "id": f"mock_{self.tool_name}_{i}",
                "title": title,
                "severity": severity,
                "description": desc,
                "url": f"{target}/test{i}",
                "evidence": "Mock evidence data",
                "remediation": "This is a mock finding for testing"
            })
        
        return findings
