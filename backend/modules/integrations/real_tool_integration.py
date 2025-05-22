"""
Real Tool Integration Manager - Professional Security Tool Integration
=====================================================================

Real integration with professional security testing tools.
No sample outputs - actual tool execution and result parsing.
"""

import asyncio
import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import os
import re

class ToolType(Enum):
    VULNERABILITY_SCANNER = "vulnerability_scanner"
    WEB_SCANNER = "web_scanner"
    NETWORK_SCANNER = "network_scanner"
    STATIC_ANALYSIS = "static_analysis"

class FindingSeverity(Enum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    INFO = 0

@dataclass
class SecurityFinding:
    """Real security finding from tool execution"""
    tool: str
    finding_id: str
    title: str
    description: str
    severity: FindingSeverity
    target: str
    evidence: str
    remediation: str
    references: List[str]
    raw_output: str

class RealToolIntegration:
    """
    Real security tool integration manager
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_tools = {
            'nmap': self._execute_nmap,
            'nikto': self._execute_nikto,
            'nuclei': self._execute_nuclei,
            'sqlmap': self._execute_sqlmap,
            'zap': self._execute_zap_baseline,
            'trivy': self._execute_trivy
        }
        
    async def execute_tool(self, tool_name: str, target: str, 
                          options: Dict[str, Any] = None) -> List[SecurityFinding]:
        """Execute real security tool against target"""
        
        if tool_name not in self.supported_tools:
            raise ValueError(f"Unsupported tool: {tool_name}")
        
        self.logger.info(f"Executing {tool_name} against {target}")
        
        try:
            return await self.supported_tools[tool_name](target, options or {})
        except Exception as e:
            self.logger.error(f"Tool execution failed for {tool_name}: {str(e)}")
            return []
    
    async def _execute_nmap(self, target: str, options: Dict[str, Any]) -> List[SecurityFinding]:
        """Execute real Nmap scan"""
        
        # Build Nmap command
        cmd = ['nmap']
        
        # Add scan type
        scan_type = options.get('scan_type', 'default')
        if scan_type == 'stealth':
            cmd.extend(['-sS', '-T2'])
        elif scan_type == 'aggressive':
            cmd.extend(['-A', '-T4'])
        else:
            cmd.extend(['-sV', '-sC'])
        
        # Add output format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            output_file = f.name
        
        cmd.extend(['-oX', output_file, target])
        
        # Execute Nmap
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                self.logger.error(f"Nmap failed: {result.stderr}")
                return []
            
            # Parse XML output
            findings = self._parse_nmap_xml(output_file, target)
            
        finally:
            # Cleanup
            if os.path.exists(output_file):
                os.unlink(output_file)
        
        return findings
    
    async def _execute_nikto(self, target: str, options: Dict[str, Any]) -> List[SecurityFinding]:
        """Execute real Nikto scan"""
        
        # Build Nikto command
        cmd = ['nikto', '-h', target]
        
        # Add options
        if options.get('ssl', False):
            cmd.append('-ssl')
        
        if options.get('evasion', False):
            cmd.extend(['-evasion', '1'])
        
        # Add output format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        cmd.extend(['-Format', 'json', '-output', output_file])
        
        # Execute Nikto
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            # Nikto returns 0 even with findings, check output file
            if not os.path.exists(output_file):
                self.logger.error(f"Nikto output file not created: {result.stderr}")
                return []
            
            # Parse JSON output
            findings = self._parse_nikto_json(output_file, target)
            
        finally:
            # Cleanup
            if os.path.exists(output_file):
                os.unlink(output_file)
        
        return findings
    
    async def _execute_nuclei(self, target: str, options: Dict[str, Any]) -> List[SecurityFinding]:
        """Execute real Nuclei scan"""
        
        # Build Nuclei command
        cmd = ['nuclei', '-u', target]
        
        # Add template options
        severity = options.get('severity', 'medium,high,critical')
        cmd.extend(['-severity', severity])
        
        # Add output format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        cmd.extend(['-json', '-o', output_file])
        
        # Execute Nuclei
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if not os.path.exists(output_file):
                self.logger.warning(f"Nuclei output file not created, no findings")
                return []
            
            # Parse JSON output
            findings = self._parse_nuclei_json(output_file, target)
            
        finally:
            # Cleanup
            if os.path.exists(output_file):
                os.unlink(output_file)
        
        return findings
    
    async def _execute_sqlmap(self, target: str, options: Dict[str, Any]) -> List[SecurityFinding]:
        """Execute real SQLMap scan"""
        
        # Build SQLMap command
        cmd = ['sqlmap', '-u', target]
        
        # Add options
        cmd.extend(['--batch', '--random-agent'])
        
        # Add risk and level
        risk = options.get('risk', 1)
        level = options.get('level', 1)
        cmd.extend(['--risk', str(risk), '--level', str(level)])
        
        # Add output format
        with tempfile.TemporaryDirectory() as temp_dir:
            cmd.extend(['--output-dir', temp_dir])
            
            # Execute SQLMap
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                
                # Parse output directory for results
                findings = self._parse_sqlmap_output(temp_dir, target, result.stdout)
                
            except subprocess.TimeoutExpired:
                self.logger.warning("SQLMap scan timed out")
                return []
        
        return findings
    
    async def _execute_zap_baseline(self, target: str, options: Dict[str, Any]) -> List[SecurityFinding]:
        """Execute real OWASP ZAP baseline scan"""
        
        # Build ZAP command
        cmd = ['zap-baseline.py', '-t', target]
        
        # Add options
        if options.get('ajax', False):
            cmd.append('-j')
        
        # Add output format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        cmd.extend(['-J', output_file])
        
        # Execute ZAP
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            
            if not os.path.exists(output_file):
                self.logger.warning(f"ZAP output file not created")
                return []
            
            # Parse JSON output
            findings = self._parse_zap_json(output_file, target)
            
        finally:
            # Cleanup
            if os.path.exists(output_file):
                os.unlink(output_file)
        
        return findings
    
    async def _execute_trivy(self, target: str, options: Dict[str, Any]) -> List[SecurityFinding]:
        """Execute real Trivy scan"""
        
        # Build Trivy command for filesystem scan
        cmd = ['trivy', 'fs']
        
        # Add security checks
        cmd.extend(['--security-checks', 'vuln,secret,config'])
        
        # Add output format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        cmd.extend(['-f', 'json', '-o', output_file, target])
        
        # Execute Trivy
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if not os.path.exists(output_file):
                self.logger.warning(f"Trivy output file not created")
                return []
            
            # Parse JSON output
            findings = self._parse_trivy_json(output_file, target)
            
        finally:
            # Cleanup
            if os.path.exists(output_file):
                os.unlink(output_file)
        
        return findings
    
    def _parse_nmap_xml(self, xml_file: str, target: str) -> List[SecurityFinding]:
        """Parse real Nmap XML output"""
        
        findings = []
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            for host in root.findall('host'):
                for port in host.findall('.//port'):
                    port_id = port.get('portid')
                    protocol = port.get('protocol')
                    
                    state = port.find('state')
                    if state is not None and state.get('state') == 'open':
                        
                        service = port.find('service')
                        service_name = service.get('name') if service is not None else 'unknown'
                        version = service.get('version') if service is not None else ''
                        
                        finding = SecurityFinding(
                            tool='nmap',
                            finding_id=f'open_port_{port_id}_{protocol}',
                            title=f'Open Port: {port_id}/{protocol}',
                            description=f'Port {port_id}/{protocol} is open running {service_name} {version}'.strip(),
                            severity=self._determine_port_severity(int(port_id), service_name),
                            target=f'{target}:{port_id}',
                            evidence=f'Port scan detected open port {port_id}/{protocol}',
                            remediation='Review if this service is necessary and properly secured',
                            references=[],
                            raw_output=ET.tostring(port, encoding='unicode')
                        )
                        findings.append(finding)
        
        except Exception as e:
            self.logger.error(f"Error parsing Nmap XML: {str(e)}")
        
        return findings
    
    def _parse_nikto_json(self, json_file: str, target: str) -> List[SecurityFinding]:
        """Parse real Nikto JSON output"""
        
        findings = []
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            for vuln in data.get('vulnerabilities', []):
                finding = SecurityFinding(
                    tool='nikto',
                    finding_id=vuln.get('id', 'unknown'),
                    title=vuln.get('msg', 'Nikto Finding'),
                    description=vuln.get('msg', ''),
                    severity=self._map_nikto_severity(vuln.get('OSVDB', '')),
                    target=vuln.get('url', target),
                    evidence=vuln.get('msg', ''),
                    remediation='Review and remediate the identified vulnerability',
                    references=[vuln.get('OSVDB', '')] if vuln.get('OSVDB') else [],
                    raw_output=json.dumps(vuln)
                )
                findings.append(finding)
        
        except Exception as e:
            self.logger.error(f"Error parsing Nikto JSON: {str(e)}")
        
        return findings
    
    def _parse_nuclei_json(self, json_file: str, target: str) -> List[SecurityFinding]:
        """Parse real Nuclei JSON output"""
        
        findings = []
        
        try:
            with open(json_file, 'r') as f:
                for line in f:
                    if line.strip():
                        vuln = json.loads(line)
                        
                        info = vuln.get('info', {})
                        finding = SecurityFinding(
                            tool='nuclei',
                            finding_id=vuln.get('template-id', 'unknown'),
                            title=info.get('name', 'Nuclei Finding'),
                            description=info.get('description', ''),
                            severity=self._map_nuclei_severity(info.get('severity', 'info')),
                            target=vuln.get('matched-at', target),
                            evidence=vuln.get('extracted-results', [''])[0] if vuln.get('extracted-results') else '',
                            remediation=info.get('remediation', 'Review and remediate the identified vulnerability'),
                            references=info.get('reference', []),
                            raw_output=json.dumps(vuln)
                        )
                        findings.append(finding)
        
        except Exception as e:
            self.logger.error(f"Error parsing Nuclei JSON: {str(e)}")
        
        return findings
    
    def _parse_sqlmap_output(self, output_dir: str, target: str, stdout: str) -> List[SecurityFinding]:
        """Parse real SQLMap output"""
        
        findings = []
        
        # Check for SQL injection indicators in stdout
        if 'sqlmap identified the following injection point' in stdout:
            finding = SecurityFinding(
                tool='sqlmap',
                finding_id='sql_injection',
                title='SQL Injection Vulnerability',
                description='SQLMap identified SQL injection vulnerability',
                severity=FindingSeverity.HIGH,
                target=target,
                evidence=stdout,
                remediation='Use parameterized queries and input validation',
                references=['https://owasp.org/www-community/attacks/SQL_Injection'],
                raw_output=stdout
            )
            findings.append(finding)
        
        return findings
    
    def _parse_zap_json(self, json_file: str, target: str) -> List[SecurityFinding]:
        """Parse real ZAP JSON output"""
        
        findings = []
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            for site in data.get('site', []):
                for alert in site.get('alerts', []):
                    finding = SecurityFinding(
                        tool='zap',
                        finding_id=alert.get('pluginid', 'unknown'),
                        title=alert.get('name', 'ZAP Finding'),
                        description=alert.get('desc', ''),
                        severity=self._map_zap_severity(alert.get('riskdesc', 'Low')),
                        target=alert.get('url', target),
                        evidence=alert.get('evidence', ''),
                        remediation=alert.get('solution', 'Review and remediate the identified vulnerability'),
                        references=alert.get('reference', '').split('\n') if alert.get('reference') else [],
                        raw_output=json.dumps(alert)
                    )
                    findings.append(finding)
        
        except Exception as e:
            self.logger.error(f"Error parsing ZAP JSON: {str(e)}")
        
        return findings
    
    def _parse_trivy_json(self, json_file: str, target: str) -> List[SecurityFinding]:
        """Parse real Trivy JSON output"""
        
        findings = []
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            for result in data.get('Results', []):
                for vuln in result.get('Vulnerabilities', []):
                    finding = SecurityFinding(
                        tool='trivy',
                        finding_id=vuln.get('VulnerabilityID', 'unknown'),
                        title=f"Vulnerability: {vuln.get('VulnerabilityID', 'Unknown')}",
                        description=vuln.get('Description', ''),
                        severity=self._map_trivy_severity(vuln.get('Severity', 'UNKNOWN')),
                        target=result.get('Target', target),
                        evidence=f"Package: {vuln.get('PkgName', 'unknown')} Version: {vuln.get('InstalledVersion', 'unknown')}",
                        remediation=f"Update to version {vuln.get('FixedVersion', 'latest')}" if vuln.get('FixedVersion') else 'Update package',
                        references=vuln.get('References', []),
                        raw_output=json.dumps(vuln)
                    )
                    findings.append(finding)
        
        except Exception as e:
            self.logger.error(f"Error parsing Trivy JSON: {str(e)}")
        
        return findings
    
    def _determine_port_severity(self, port: int, service: str) -> FindingSeverity:
        """Determine severity based on port and service"""
        
        # High-risk ports
        high_risk_ports = [21, 23, 135, 139, 445, 1433, 3389, 5900]
        # Medium-risk ports  
        medium_risk_ports = [25, 53, 110, 143, 993, 995]
        
        if port in high_risk_ports:
            return FindingSeverity.HIGH
        elif port in medium_risk_ports:
            return FindingSeverity.MEDIUM
        elif port < 1024:  # Well-known ports
            return FindingSeverity.MEDIUM
        else:
            return FindingSeverity.LOW
    
    def _map_nikto_severity(self, osvdb: str) -> FindingSeverity:
        """Map Nikto OSVDB to severity"""
        # This is a simplified mapping - real implementation would use OSVDB database
        if not osvdb:
            return FindingSeverity.MEDIUM
        return FindingSeverity.MEDIUM
    
    def _map_nuclei_severity(self, severity: str) -> FindingSeverity:
        """Map Nuclei severity to internal severity"""
        
        mapping = {
            'critical': FindingSeverity.CRITICAL,
            'high': FindingSeverity.HIGH,
            'medium': FindingSeverity.MEDIUM,
            'low': FindingSeverity.LOW,
            'info': FindingSeverity.INFO
        }
        
        return mapping.get(severity.lower(), FindingSeverity.MEDIUM)
    
    def _map_zap_severity(self, risk_desc: str) -> FindingSeverity:
        """Map ZAP risk description to severity"""
        
        if 'High' in risk_desc:
            return FindingSeverity.HIGH
        elif 'Medium' in risk_desc:
            return FindingSeverity.MEDIUM
        elif 'Low' in risk_desc:
            return FindingSeverity.LOW
        else:
            return FindingSeverity.INFO
    
    def _map_trivy_severity(self, severity: str) -> FindingSeverity:
        """Map Trivy severity to internal severity"""
        
        mapping = {
            'CRITICAL': FindingSeverity.CRITICAL,
            'HIGH': FindingSeverity.HIGH,
            'MEDIUM': FindingSeverity.MEDIUM,
            'LOW': FindingSeverity.LOW,
            'UNKNOWN': FindingSeverity.INFO
        }
        
        return mapping.get(severity.upper(), FindingSeverity.MEDIUM)

# Export the real tool integration
__all__ = ['RealToolIntegration']