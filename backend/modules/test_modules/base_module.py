#!/usr/bin/env python3
# SecureScout - Base Module Class

import logging
import abc
from typing import Dict, List, Any, Optional

logger = logging.getLogger("securescout.test_module")

class BaseTestModule(abc.ABC):
    """
    Base class for all security test modules.
    Defines the common interface and functionality that all test modules must implement.
    """
    
    def __init__(self, scanner):
        """
        Initialize the test module.
        
        Args:
            scanner: Reference to the parent ScannerEngine
        """
        self.scanner = scanner
        self.name = self.__class__.__name__
        self.description = "Base security test module"
        self.category = "general"
        self.findings = []
        self.severity_levels = ["info", "low", "medium", "high", "critical"]
        
    @abc.abstractmethod
    def run(self) -> List[Dict[str, Any]]:
        """
        Run the security test module against the target.
        This method must be implemented by all test modules.
        
        Returns:
            List of findings dictionaries
        """
        pass
    
    def add_finding(self, title: str, description: str, severity: str, 
                   location: str, evidence: str = None, remediation: str = None,
                   references: List[str] = None, cwe_id: str = None,
                   cvss_score: float = None, additional_info: Dict = None) -> Dict[str, Any]:
        """
        Create and add a security finding to the results.
        
        Args:
            title: Short title describing the finding
            description: Detailed description of the finding
            severity: Severity level (info, low, medium, high, critical)
            location: URL or path where the finding was discovered
            evidence: Evidence of the vulnerability (e.g., response data, payload)
            remediation: Recommended steps to fix the issue
            references: List of URLs to related information
            cwe_id: Common Weakness Enumeration ID (e.g., CWE-79)
            cvss_score: Common Vulnerability Scoring System score (0.0-10.0)
            additional_info: Any additional information relevant to the finding
            
        Returns:
            Dictionary containing the finding details
        """
        # Validate severity level
        if severity not in self.severity_levels:
            severity = "info"
        
        # Create finding dictionary
        finding = {
            "module": self.name,
            "category": self.category,
            "title": title,
            "description": description,
            "severity": severity,
            "location": location,
            "evidence": evidence or "",
            "remediation": remediation or "",
            "references": references or [],
            "cwe_id": cwe_id,
            "cvss_score": cvss_score,
            "additional_info": additional_info or {}
        }
        
        # Add to local findings list
        self.findings.append(finding)
        
        # Add to scanner findings list
        self.scanner.add_finding(finding)
        
        return finding