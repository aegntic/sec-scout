"""
Security Posture Analyzer - Comprehensive Strength & Weakness Analysis
Analyzes and visualizes both security strengths and weaknesses discovered during testing
"""

import asyncio
import json
import base64
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid
import logging

class SecurityDomain(Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    INPUT_VALIDATION = "input_validation"
    OUTPUT_ENCODING = "output_encoding"
    CRYPTOGRAPHY = "cryptography"
    SESSION_MANAGEMENT = "session_management"
    ERROR_HANDLING = "error_handling"
    LOGGING_MONITORING = "logging_monitoring"
    CONFIGURATION = "configuration"
    NETWORK_SECURITY = "network_security"
    DATA_PROTECTION = "data_protection"
    BUSINESS_LOGIC = "business_logic"
    FILE_UPLOAD = "file_upload"
    API_SECURITY = "api_security"
    INFRASTRUCTURE = "infrastructure"

class StrengthLevel(Enum):
    EXCELLENT = "excellent"
    STRONG = "strong"
    ADEQUATE = "adequate"
    WEAK = "weak"
    CRITICAL = "critical"

class WeaknessLevel(Enum):
    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityStrength:
    domain: SecurityDomain
    strength_level: StrengthLevel
    description: str
    evidence: List[str]
    implementation_details: List[str]
    best_practices_followed: List[str]
    confidence_score: float
    impact_on_security: str

@dataclass
class SecurityWeakness:
    domain: SecurityDomain
    weakness_level: WeaknessLevel
    description: str
    evidence: List[str]
    exploitation_potential: str
    business_impact: str
    confidence_score: float
    remediation_effort: str

@dataclass
class SecurityPosture:
    overall_score: float
    risk_level: str
    strengths: List[SecurityStrength]
    weaknesses: List[SecurityWeakness]
    domain_scores: Dict[str, float]
    recommendations: List[str]
    compliance_status: Dict[str, str]

class SecurityPostureAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.strength_detectors = self._initialize_strength_detectors()
        self.weakness_correlators = self._initialize_weakness_correlators()
        self.domain_analyzers = self._initialize_domain_analyzers()
        
    def _initialize_strength_detectors(self) -> Dict[SecurityDomain, Any]:
        """Initialize strength detection algorithms for each security domain"""
        return {
            SecurityDomain.AUTHENTICATION: self._analyze_authentication_strengths,
            SecurityDomain.AUTHORIZATION: self._analyze_authorization_strengths,
            SecurityDomain.INPUT_VALIDATION: self._analyze_input_validation_strengths,
            SecurityDomain.OUTPUT_ENCODING: self._analyze_output_encoding_strengths,
            SecurityDomain.CRYPTOGRAPHY: self._analyze_cryptography_strengths,
            SecurityDomain.SESSION_MANAGEMENT: self._analyze_session_strengths,
            SecurityDomain.ERROR_HANDLING: self._analyze_error_handling_strengths,
            SecurityDomain.LOGGING_MONITORING: self._analyze_logging_strengths,
            SecurityDomain.CONFIGURATION: self._analyze_configuration_strengths,
            SecurityDomain.NETWORK_SECURITY: self._analyze_network_strengths,
            SecurityDomain.DATA_PROTECTION: self._analyze_data_protection_strengths,
            SecurityDomain.BUSINESS_LOGIC: self._analyze_business_logic_strengths,
            SecurityDomain.FILE_UPLOAD: self._analyze_file_upload_strengths,
            SecurityDomain.API_SECURITY: self._analyze_api_security_strengths,
            SecurityDomain.INFRASTRUCTURE: self._analyze_infrastructure_strengths
        }
    
    def _initialize_weakness_correlators(self) -> Dict[SecurityDomain, Any]:
        """Initialize weakness correlation algorithms"""
        return {
            SecurityDomain.AUTHENTICATION: self._correlate_authentication_weaknesses,
            SecurityDomain.AUTHORIZATION: self._correlate_authorization_weaknesses,
            SecurityDomain.INPUT_VALIDATION: self._correlate_input_validation_weaknesses,
            SecurityDomain.OUTPUT_ENCODING: self._correlate_output_encoding_weaknesses,
            SecurityDomain.CRYPTOGRAPHY: self._correlate_cryptography_weaknesses,
            SecurityDomain.SESSION_MANAGEMENT: self._correlate_session_weaknesses,
            SecurityDomain.ERROR_HANDLING: self._correlate_error_handling_weaknesses,
            SecurityDomain.LOGGING_MONITORING: self._correlate_logging_weaknesses,
            SecurityDomain.CONFIGURATION: self._correlate_configuration_weaknesses,
            SecurityDomain.NETWORK_SECURITY: self._correlate_network_weaknesses,
            SecurityDomain.DATA_PROTECTION: self._correlate_data_protection_weaknesses,
            SecurityDomain.BUSINESS_LOGIC: self._correlate_business_logic_weaknesses,
            SecurityDomain.FILE_UPLOAD: self._correlate_file_upload_weaknesses,
            SecurityDomain.API_SECURITY: self._correlate_api_security_weaknesses,
            SecurityDomain.INFRASTRUCTURE: self._correlate_infrastructure_weaknesses
        }
    
    def _initialize_domain_analyzers(self) -> Dict[SecurityDomain, Any]:
        """Initialize comprehensive domain analyzers"""
        return {
            SecurityDomain.AUTHENTICATION: self._analyze_authentication_domain,
            SecurityDomain.AUTHORIZATION: self._analyze_authorization_domain,
            SecurityDomain.INPUT_VALIDATION: self._analyze_input_validation_domain,
            SecurityDomain.OUTPUT_ENCODING: self._analyze_output_encoding_domain,
            SecurityDomain.CRYPTOGRAPHY: self._analyze_cryptography_domain,
            SecurityDomain.SESSION_MANAGEMENT: self._analyze_session_domain,
            SecurityDomain.ERROR_HANDLING: self._analyze_error_handling_domain,
            SecurityDomain.LOGGING_MONITORING: self._analyze_logging_domain,
            SecurityDomain.CONFIGURATION: self._analyze_configuration_domain,
            SecurityDomain.NETWORK_SECURITY: self._analyze_network_domain,
            SecurityDomain.DATA_PROTECTION: self._analyze_data_protection_domain,
            SecurityDomain.BUSINESS_LOGIC: self._analyze_business_logic_domain,
            SecurityDomain.FILE_UPLOAD: self._analyze_file_upload_domain,
            SecurityDomain.API_SECURITY: self._analyze_api_security_domain,
            SecurityDomain.INFRASTRUCTURE: self._analyze_infrastructure_domain
        }

    async def analyze_security_posture(self, exploration_results: Dict[str, Any], 
                                     target_context: Dict[str, Any]) -> SecurityPosture:
        """Comprehensive security posture analysis including strengths and weaknesses"""
        
        self.logger.info("Starting comprehensive security posture analysis")
        
        # Extract analysis data
        vulnerabilities = self._extract_vulnerabilities(exploration_results)
        test_results = self._extract_test_results(exploration_results)
        system_responses = self._extract_system_responses(exploration_results)
        
        # Analyze each security domain
        domain_analysis = {}
        for domain in SecurityDomain:
            domain_analysis[domain] = await self._analyze_security_domain(
                domain, vulnerabilities, test_results, system_responses, target_context
            )
        
        # Extract strengths and weaknesses
        all_strengths = []
        all_weaknesses = []
        domain_scores = {}
        
        for domain, analysis in domain_analysis.items():
            all_strengths.extend(analysis['strengths'])
            all_weaknesses.extend(analysis['weaknesses'])
            domain_scores[domain.value] = analysis['domain_score']
        
        # Calculate overall security posture
        overall_score = self._calculate_overall_score(domain_scores, all_strengths, all_weaknesses)
        risk_level = self._determine_risk_level(overall_score, all_weaknesses)
        
        # Generate recommendations
        recommendations = await self._generate_comprehensive_recommendations(
            all_strengths, all_weaknesses, domain_scores
        )
        
        # Assess compliance status
        compliance_status = await self._assess_compliance_status(
            all_strengths, all_weaknesses, target_context
        )
        
        return SecurityPosture(
            overall_score=overall_score,
            risk_level=risk_level,
            strengths=all_strengths,
            weaknesses=all_weaknesses,
            domain_scores=domain_scores,
            recommendations=recommendations,
            compliance_status=compliance_status
        )

    async def _analyze_security_domain(self, domain: SecurityDomain, vulnerabilities: List[Dict],
                                     test_results: List[Dict], system_responses: List[Dict],
                                     target_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a specific security domain for strengths and weaknesses"""
        
        # Detect strengths in this domain
        strengths = await self.strength_detectors[domain](
            test_results, system_responses, target_context
        )
        
        # Correlate weaknesses from vulnerabilities
        weaknesses = await self.weakness_correlators[domain](
            vulnerabilities, test_results, target_context
        )
        
        # Calculate domain score (0-10 scale)
        domain_score = self._calculate_domain_score(strengths, weaknesses)
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'domain_score': domain_score,
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }

    # Authentication Domain Analysis
    async def _analyze_authentication_strengths(self, test_results: List[Dict], 
                                              system_responses: List[Dict], 
                                              target_context: Dict[str, Any]) -> List[SecurityStrength]:
        """Analyze authentication security strengths"""
        strengths = []
        
        # Check for strong authentication mechanisms
        auth_evidence = self._find_evidence_in_responses(system_responses, [
            'multi-factor', 'mfa', '2fa', 'oauth', 'saml', 'strong password'
        ])
        
        if auth_evidence:
            strengths.append(SecurityStrength(
                domain=SecurityDomain.AUTHENTICATION,
                strength_level=StrengthLevel.STRONG,
                description="Multi-factor authentication implementation detected",
                evidence=auth_evidence,
                implementation_details=[
                    "Strong authentication mechanisms in place",
                    "Multiple authentication factors required",
                    "Industry-standard protocols used"
                ],
                best_practices_followed=[
                    "NIST authentication guidelines",
                    "OAuth 2.0 / SAML implementation",
                    "MFA enforcement"
                ],
                confidence_score=0.85,
                impact_on_security="Significantly reduces unauthorized access risk"
            ))
        
        # Check for account lockout mechanisms
        lockout_evidence = self._find_evidence_in_responses(system_responses, [
            'account locked', 'too many attempts', 'lockout', 'rate limit'
        ])
        
        if lockout_evidence:
            strengths.append(SecurityStrength(
                domain=SecurityDomain.AUTHENTICATION,
                strength_level=StrengthLevel.ADEQUATE,
                description="Account lockout protection implemented",
                evidence=lockout_evidence,
                implementation_details=[
                    "Account lockout after failed attempts",
                    "Rate limiting on authentication endpoints",
                    "Brute force protection active"
                ],
                best_practices_followed=[
                    "OWASP authentication guidelines",
                    "Automated threat detection"
                ],
                confidence_score=0.75,
                impact_on_security="Prevents brute force and credential stuffing attacks"
            ))
        
        # Check for secure password policies
        password_evidence = self._find_evidence_in_responses(system_responses, [
            'password complexity', 'minimum length', 'special characters'
        ])
        
        if password_evidence:
            strengths.append(SecurityStrength(
                domain=SecurityDomain.AUTHENTICATION,
                strength_level=StrengthLevel.ADEQUATE,
                description="Strong password policy enforcement",
                evidence=password_evidence,
                implementation_details=[
                    "Password complexity requirements",
                    "Minimum length enforcement",
                    "Character diversity requirements"
                ],
                best_practices_followed=[
                    "NIST password guidelines",
                    "Industry standard complexity"
                ],
                confidence_score=0.70,
                impact_on_security="Reduces weak password vulnerabilities"
            ))
        
        return strengths

    async def _correlate_authentication_weaknesses(self, vulnerabilities: List[Dict],
                                                 test_results: List[Dict],
                                                 target_context: Dict[str, Any]) -> List[SecurityWeakness]:
        """Correlate authentication weaknesses from vulnerability data"""
        weaknesses = []
        
        # Look for authentication bypass vulnerabilities
        auth_bypasses = [v for v in vulnerabilities if 'authentication' in str(v).lower() and 'bypass' in str(v).lower()]
        
        for bypass in auth_bypasses:
            weaknesses.append(SecurityWeakness(
                domain=SecurityDomain.AUTHENTICATION,
                weakness_level=WeaknessLevel.HIGH,
                description=f"Authentication bypass vulnerability: {bypass.get('description', 'Unknown')}",
                evidence=[
                    f"Bypass method: {bypass.get('method', 'Unknown')}",
                    f"Affected endpoint: {bypass.get('endpoint', 'Unknown')}",
                    f"Confidence: {bypass.get('confidence', 0)}"
                ],
                exploitation_potential="High - Direct access to protected resources",
                business_impact="Critical - Unauthorized access to sensitive data and functions",
                confidence_score=bypass.get('confidence', 0.8),
                remediation_effort="Medium - Requires authentication logic review and testing"
            ))
        
        # Look for weak authentication mechanisms
        weak_auth = [v for v in vulnerabilities if 'weak' in str(v).lower() and 'auth' in str(v).lower()]
        
        for weak in weak_auth:
            weaknesses.append(SecurityWeakness(
                domain=SecurityDomain.AUTHENTICATION,
                weakness_level=WeaknessLevel.MEDIUM,
                description=f"Weak authentication mechanism: {weak.get('description', 'Unknown')}",
                evidence=[
                    f"Weakness type: {weak.get('type', 'Unknown')}",
                    f"Location: {weak.get('location', 'Unknown')}"
                ],
                exploitation_potential="Medium - Credential compromise possible",
                business_impact="High - Account takeover risk",
                confidence_score=weak.get('confidence', 0.7),
                remediation_effort="Low - Configuration and policy updates"
            ))
        
        return weaknesses

    async def _analyze_authentication_domain(self, *args) -> Dict[str, Any]:
        """Complete authentication domain analysis"""
        # This would be implemented by calling both strength and weakness analyzers
        return await self._analyze_security_domain(SecurityDomain.AUTHENTICATION, *args)

    # Input Validation Domain Analysis
    async def _analyze_input_validation_strengths(self, test_results: List[Dict],
                                                system_responses: List[Dict],
                                                target_context: Dict[str, Any]) -> List[SecurityStrength]:
        """Analyze input validation security strengths"""
        strengths = []
        
        # Check for parameterized queries
        param_evidence = self._find_evidence_in_responses(system_responses, [
            'parameterized', 'prepared statement', 'bound parameter'
        ])
        
        if param_evidence:
            strengths.append(SecurityStrength(
                domain=SecurityDomain.INPUT_VALIDATION,
                strength_level=StrengthLevel.EXCELLENT,
                description="Parameterized queries implementation detected",
                evidence=param_evidence,
                implementation_details=[
                    "SQL injection prevention through parameterized queries",
                    "Prepared statements used consistently",
                    "Input/output separation maintained"
                ],
                best_practices_followed=[
                    "OWASP injection prevention",
                    "Secure coding standards",
                    "Database security best practices"
                ],
                confidence_score=0.90,
                impact_on_security="Eliminates SQL injection vulnerabilities"
            ))
        
        # Check for input sanitization
        sanitization_evidence = self._find_evidence_in_responses(system_responses, [
            'input validation', 'sanitized', 'filtered', 'validated'
        ])
        
        if sanitization_evidence:
            strengths.append(SecurityStrength(
                domain=SecurityDomain.INPUT_VALIDATION,
                strength_level=StrengthLevel.STRONG,
                description="Comprehensive input validation implemented",
                evidence=sanitization_evidence,
                implementation_details=[
                    "Input validation on all user inputs",
                    "Data sanitization before processing",
                    "Type validation enforcement"
                ],
                best_practices_followed=[
                    "Defense in depth strategy",
                    "Input validation at multiple layers"
                ],
                confidence_score=0.80,
                impact_on_security="Prevents various injection attacks"
            ))
        
        return strengths

    async def _correlate_input_validation_weaknesses(self, vulnerabilities: List[Dict],
                                                   test_results: List[Dict],
                                                   target_context: Dict[str, Any]) -> List[SecurityWeakness]:
        """Correlate input validation weaknesses"""
        weaknesses = []
        
        # Look for injection vulnerabilities
        injections = [v for v in vulnerabilities if any(inj in str(v).lower() 
                     for inj in ['sql injection', 'xss', 'command injection', 'ldap injection'])]
        
        for injection in injections:
            injection_type = self._determine_injection_type(injection)
            weakness_level = WeaknessLevel.CRITICAL if 'sql' in injection_type.lower() else WeaknessLevel.HIGH
            
            weaknesses.append(SecurityWeakness(
                domain=SecurityDomain.INPUT_VALIDATION,
                weakness_level=weakness_level,
                description=f"{injection_type} vulnerability detected",
                evidence=[
                    f"Injection type: {injection_type}",
                    f"Vulnerable parameter: {injection.get('parameter', 'Unknown')}",
                    f"Payload: {injection.get('payload', 'Unknown')}"
                ],
                exploitation_potential="High - Direct code/query execution possible",
                business_impact="Critical - Data breach and system compromise risk",
                confidence_score=injection.get('confidence', 0.8),
                remediation_effort="Medium - Input validation and sanitization required"
            ))
        
        return weaknesses

    # Cryptography Domain Analysis
    async def _analyze_cryptography_strengths(self, test_results: List[Dict],
                                            system_responses: List[Dict],
                                            target_context: Dict[str, Any]) -> List[SecurityStrength]:
        """Analyze cryptographic security strengths"""
        strengths = []
        
        # Check for HTTPS/TLS implementation
        tls_evidence = self._find_evidence_in_responses(system_responses, [
            'https', 'tls 1.2', 'tls 1.3', 'ssl secure'
        ])
        
        if tls_evidence:
            strengths.append(SecurityStrength(
                domain=SecurityDomain.CRYPTOGRAPHY,
                strength_level=StrengthLevel.STRONG,
                description="Strong TLS/HTTPS implementation",
                evidence=tls_evidence,
                implementation_details=[
                    "HTTPS enforced across application",
                    "Modern TLS versions supported",
                    "Strong cipher suites configured"
                ],
                best_practices_followed=[
                    "NIST cryptographic standards",
                    "Industry-standard encryption"
                ],
                confidence_score=0.85,
                impact_on_security="Protects data in transit from interception"
            ))
        
        # Check for strong hashing algorithms
        hash_evidence = self._find_evidence_in_responses(system_responses, [
            'sha256', 'sha512', 'bcrypt', 'scrypt', 'argon2'
        ])
        
        if hash_evidence:
            strengths.append(SecurityStrength(
                domain=SecurityDomain.CRYPTOGRAPHY,
                strength_level=StrengthLevel.STRONG,
                description="Strong password hashing implementation",
                evidence=hash_evidence,
                implementation_details=[
                    "Cryptographically secure hash functions",
                    "Salt-based password hashing",
                    "Appropriate iteration counts"
                ],
                best_practices_followed=[
                    "OWASP password storage guidelines",
                    "Modern hashing algorithms"
                ],
                confidence_score=0.80,
                impact_on_security="Protects stored passwords from compromise"
            ))
        
        return strengths

    # Session Management Domain Analysis
    async def _analyze_session_strengths(self, test_results: List[Dict],
                                       system_responses: List[Dict],
                                       target_context: Dict[str, Any]) -> List[SecurityStrength]:
        """Analyze session management security strengths"""
        strengths = []
        
        # Check for secure session configuration
        session_evidence = self._find_evidence_in_responses(system_responses, [
            'httponly', 'secure flag', 'samesite', 'session timeout'
        ])
        
        if session_evidence:
            strengths.append(SecurityStrength(
                domain=SecurityDomain.SESSION_MANAGEMENT,
                strength_level=StrengthLevel.STRONG,
                description="Secure session cookie configuration",
                evidence=session_evidence,
                implementation_details=[
                    "HttpOnly flag set on session cookies",
                    "Secure flag enforced for HTTPS",
                    "SameSite protection enabled",
                    "Appropriate session timeouts"
                ],
                best_practices_followed=[
                    "OWASP session management guidelines",
                    "Secure cookie standards"
                ],
                confidence_score=0.85,
                impact_on_security="Prevents session hijacking and CSRF attacks"
            ))
        
        return strengths

    # Error Handling Domain Analysis
    async def _analyze_error_handling_strengths(self, test_results: List[Dict],
                                              system_responses: List[Dict],
                                              target_context: Dict[str, Any]) -> List[SecurityStrength]:
        """Analyze error handling security strengths"""
        strengths = []
        
        # Check for generic error messages
        error_evidence = self._find_evidence_in_responses(system_responses, [
            'generic error', 'custom error page', 'error handling'
        ])
        
        if error_evidence and not self._contains_sensitive_errors(system_responses):
            strengths.append(SecurityStrength(
                domain=SecurityDomain.ERROR_HANDLING,
                strength_level=StrengthLevel.ADEQUATE,
                description="Secure error handling implementation",
                evidence=error_evidence,
                implementation_details=[
                    "Generic error messages to users",
                    "Detailed logging for developers",
                    "No sensitive information disclosure"
                ],
                best_practices_followed=[
                    "Information disclosure prevention",
                    "Secure error handling patterns"
                ],
                confidence_score=0.75,
                impact_on_security="Prevents information leakage through error messages"
            ))
        
        return strengths

    # Network Security Domain Analysis
    async def _analyze_network_strengths(self, test_results: List[Dict],
                                       system_responses: List[Dict],
                                       target_context: Dict[str, Any]) -> List[SecurityStrength]:
        """Analyze network security strengths"""
        strengths = []
        
        # Check for security headers
        header_evidence = self._find_evidence_in_responses(system_responses, [
            'content-security-policy', 'x-frame-options', 'x-content-type-options',
            'strict-transport-security', 'x-xss-protection'
        ])
        
        if header_evidence:
            strengths.append(SecurityStrength(
                domain=SecurityDomain.NETWORK_SECURITY,
                strength_level=StrengthLevel.STRONG,
                description="Comprehensive security headers implementation",
                evidence=header_evidence,
                implementation_details=[
                    "Content Security Policy enforced",
                    "Clickjacking protection enabled",
                    "MIME-type sniffing prevention",
                    "HTTP Strict Transport Security"
                ],
                best_practices_followed=[
                    "OWASP security headers guidelines",
                    "Defense in depth approach"
                ],
                confidence_score=0.85,
                impact_on_security="Prevents various client-side attacks"
            ))
        
        return strengths

    # Utility methods
    def _extract_vulnerabilities(self, exploration_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract vulnerability data from exploration results"""
        vulnerabilities = []
        
        # Extract from detailed findings
        detailed_findings = exploration_results.get('detailed_findings', {})
        successful_vectors = detailed_findings.get('successful_vectors', [])
        
        for vector in successful_vectors:
            vulnerabilities.append({
                'type': 'successful_exploitation',
                'vector_id': vector.get('vector_id', 'unknown'),
                'confidence': vector.get('confidence', 0.5),
                'evidence': vector.get('evidence', []),
                'response_data': vector.get('response_data', {})
            })
        
        # Extract from vulnerability profile
        vuln_profile = exploration_results.get('vulnerability_profile', {})
        if vuln_profile:
            vulnerabilities.append({
                'type': 'classified_vulnerability',
                'category': vuln_profile.get('category', 'unknown'),
                'severity': vuln_profile.get('severity', 'unknown'),
                'attack_vectors': vuln_profile.get('attack_vectors', []),
                'affected_components': vuln_profile.get('affected_components', [])
            })
        
        return vulnerabilities

    def _extract_test_results(self, exploration_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract test results from exploration data"""
        test_results = []
        
        # Extract from detailed findings
        detailed_findings = exploration_results.get('detailed_findings', {})
        
        # Include both successful and failed vectors
        for vector in detailed_findings.get('successful_vectors', []):
            test_results.append({
                'result_type': 'successful',
                'vector_id': vector.get('vector_id', 'unknown'),
                'execution_time': vector.get('execution_time', 0),
                'confidence': vector.get('confidence', 0),
                'evidence': vector.get('evidence', [])
            })
        
        for vector in detailed_findings.get('failed_vectors', []):
            test_results.append({
                'result_type': 'failed',
                'vector_id': vector.get('vector_id', 'unknown'),
                'execution_time': vector.get('execution_time', 0),
                'confidence': vector.get('confidence', 0),
                'failure_reason': vector.get('response_data', {}).get('error', 'unknown')
            })
        
        return test_results

    def _extract_system_responses(self, exploration_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract system responses for analysis"""
        responses = []
        
        detailed_findings = exploration_results.get('detailed_findings', {})
        
        # Extract response data from all vectors
        all_vectors = (detailed_findings.get('successful_vectors', []) + 
                      detailed_findings.get('failed_vectors', []))
        
        for vector in all_vectors:
            response_data = vector.get('response_data', {})
            if response_data:
                responses.append({
                    'vector_id': vector.get('vector_id', 'unknown'),
                    'status_code': response_data.get('status_code', 0),
                    'content': response_data.get('content', ''),
                    'headers': response_data.get('headers', {}),
                    'response_time': response_data.get('response_time', 0)
                })
        
        return responses

    def _find_evidence_in_responses(self, responses: List[Dict], indicators: List[str]) -> List[str]:
        """Find evidence of security mechanisms in responses"""
        evidence = []
        
        for response in responses:
            content = str(response.get('content', '')).lower()
            headers = str(response.get('headers', {})).lower()
            combined_text = content + ' ' + headers
            
            for indicator in indicators:
                if indicator.lower() in combined_text:
                    evidence.append(f"Found '{indicator}' in response from {response.get('vector_id', 'unknown')}")
        
        return evidence

    def _contains_sensitive_errors(self, responses: List[Dict]) -> bool:
        """Check if responses contain sensitive error information"""
        sensitive_patterns = [
            'stack trace', 'sql error', 'database error', 'file path',
            'internal server error', 'exception', 'debug information'
        ]
        
        for response in responses:
            content = str(response.get('content', '')).lower()
            if any(pattern in content for pattern in sensitive_patterns):
                return True
        
        return False

    def _determine_injection_type(self, injection_data: Dict[str, Any]) -> str:
        """Determine the type of injection vulnerability"""
        content = str(injection_data).lower()
        
        if 'sql' in content:
            return "SQL Injection"
        elif 'xss' in content or 'script' in content:
            return "Cross-Site Scripting (XSS)"
        elif 'command' in content:
            return "Command Injection"
        elif 'ldap' in content:
            return "LDAP Injection"
        else:
            return "Code Injection"

    def _calculate_domain_score(self, strengths: List[SecurityStrength], 
                              weaknesses: List[SecurityWeakness]) -> float:
        """Calculate security score for a domain (0-10 scale)"""
        base_score = 5.0  # Neutral starting point
        
        # Add points for strengths
        for strength in strengths:
            if strength.strength_level == StrengthLevel.EXCELLENT:
                base_score += 2.0 * strength.confidence_score
            elif strength.strength_level == StrengthLevel.STRONG:
                base_score += 1.5 * strength.confidence_score
            elif strength.strength_level == StrengthLevel.ADEQUATE:
                base_score += 1.0 * strength.confidence_score
        
        # Subtract points for weaknesses
        for weakness in weaknesses:
            if weakness.weakness_level == WeaknessLevel.CRITICAL:
                base_score -= 3.0 * weakness.confidence_score
            elif weakness.weakness_level == WeaknessLevel.HIGH:
                base_score -= 2.0 * weakness.confidence_score
            elif weakness.weakness_level == WeaknessLevel.MEDIUM:
                base_score -= 1.5 * weakness.confidence_score
            elif weakness.weakness_level == WeaknessLevel.LOW:
                base_score -= 1.0 * weakness.confidence_score
        
        # Ensure score stays within bounds
        return max(0.0, min(10.0, base_score))

    def _calculate_overall_score(self, domain_scores: Dict[str, float], 
                               strengths: List[SecurityStrength], 
                               weaknesses: List[SecurityWeakness]) -> float:
        """Calculate overall security posture score"""
        if not domain_scores:
            return 0.0
        
        # Weighted average of domain scores
        total_score = sum(domain_scores.values())
        average_score = total_score / len(domain_scores)
        
        # Apply global modifiers
        critical_weaknesses = len([w for w in weaknesses if w.weakness_level == WeaknessLevel.CRITICAL])
        excellent_strengths = len([s for s in strengths if s.strength_level == StrengthLevel.EXCELLENT])
        
        # Penalty for critical weaknesses
        if critical_weaknesses > 0:
            average_score *= (1.0 - (critical_weaknesses * 0.1))
        
        # Bonus for excellent strengths
        if excellent_strengths > 0:
            average_score *= (1.0 + (excellent_strengths * 0.05))
        
        return max(0.0, min(10.0, average_score))

    def _determine_risk_level(self, overall_score: float, weaknesses: List[SecurityWeakness]) -> str:
        """Determine overall risk level"""
        critical_weaknesses = len([w for w in weaknesses if w.weakness_level == WeaknessLevel.CRITICAL])
        high_weaknesses = len([w for w in weaknesses if w.weakness_level == WeaknessLevel.HIGH])
        
        if critical_weaknesses > 0 or overall_score < 3.0:
            return "Critical"
        elif high_weaknesses > 2 or overall_score < 5.0:
            return "High"
        elif overall_score < 7.0:
            return "Medium"
        else:
            return "Low"

    async def _generate_comprehensive_recommendations(self, strengths: List[SecurityStrength],
                                                   weaknesses: List[SecurityWeakness],
                                                   domain_scores: Dict[str, float]) -> List[str]:
        """Generate comprehensive security recommendations"""
        recommendations = []
        
        # Recommendations based on critical weaknesses
        critical_weaknesses = [w for w in weaknesses if w.weakness_level == WeaknessLevel.CRITICAL]
        for weakness in critical_weaknesses:
            recommendations.append(
                f"CRITICAL: Address {weakness.domain.value} weakness - {weakness.description}"
            )
        
        # Recommendations for improving weak domains
        weak_domains = [domain for domain, score in domain_scores.items() if score < 5.0]
        for domain in weak_domains:
            recommendations.append(
                f"Improve {domain} security controls - Current score: {domain_scores[domain]:.1f}/10"
            )
        
        # Recommendations for maintaining strengths
        excellent_strengths = [s for s in strengths if s.strength_level == StrengthLevel.EXCELLENT]
        if excellent_strengths:
            recommendations.append(
                "Maintain current excellent security controls in: " + 
                ", ".join([s.domain.value for s in excellent_strengths])
            )
        
        # General recommendations
        recommendations.extend([
            "Implement continuous security monitoring and testing",
            "Regular security training for development teams",
            "Establish incident response procedures",
            "Conduct regular security assessments"
        ])
        
        return recommendations

    async def _assess_compliance_status(self, strengths: List[SecurityStrength],
                                      weaknesses: List[SecurityWeakness],
                                      target_context: Dict[str, Any]) -> Dict[str, str]:
        """Assess compliance with various security frameworks"""
        compliance_status = {}
        
        # OWASP Top 10 compliance
        owasp_score = self._calculate_owasp_compliance(strengths, weaknesses)
        compliance_status['OWASP_Top_10'] = f"{owasp_score:.0f}% compliant"
        
        # NIST Cybersecurity Framework
        nist_score = self._calculate_nist_compliance(strengths, weaknesses)
        compliance_status['NIST_CSF'] = f"{nist_score:.0f}% compliant"
        
        # ISO 27001
        iso_score = self._calculate_iso27001_compliance(strengths, weaknesses)
        compliance_status['ISO_27001'] = f"{iso_score:.0f}% compliant"
        
        # PCI DSS (if applicable)
        if target_context.get('handles_payment_data', False):
            pci_score = self._calculate_pci_compliance(strengths, weaknesses)
            compliance_status['PCI_DSS'] = f"{pci_score:.0f}% compliant"
        
        return compliance_status

    def _calculate_owasp_compliance(self, strengths: List[SecurityStrength], 
                                  weaknesses: List[SecurityWeakness]) -> float:
        """Calculate OWASP Top 10 compliance percentage"""
        # Simplified compliance calculation
        owasp_domains = [
            SecurityDomain.AUTHENTICATION, SecurityDomain.INPUT_VALIDATION,
            SecurityDomain.CRYPTOGRAPHY, SecurityDomain.AUTHORIZATION
        ]
        
        domain_strengths = len([s for s in strengths if s.domain in owasp_domains])
        domain_weaknesses = len([w for w in weaknesses if w.domain in owasp_domains and 
                               w.weakness_level in [WeaknessLevel.HIGH, WeaknessLevel.CRITICAL]])
        
        if domain_weaknesses > 0:
            return max(0, 100 - (domain_weaknesses * 20))
        else:
            return min(100, 70 + (domain_strengths * 5))

    def _calculate_nist_compliance(self, strengths: List[SecurityStrength], 
                                 weaknesses: List[SecurityWeakness]) -> float:
        """Calculate NIST Cybersecurity Framework compliance"""
        # Simplified NIST compliance calculation
        critical_weaknesses = len([w for w in weaknesses if w.weakness_level == WeaknessLevel.CRITICAL])
        strong_strengths = len([s for s in strengths if s.strength_level in [StrengthLevel.STRONG, StrengthLevel.EXCELLENT]])
        
        base_score = 60
        base_score -= critical_weaknesses * 15
        base_score += strong_strengths * 8
        
        return max(0, min(100, base_score))

    def _calculate_iso27001_compliance(self, strengths: List[SecurityStrength], 
                                     weaknesses: List[SecurityWeakness]) -> float:
        """Calculate ISO 27001 compliance percentage"""
        # Simplified ISO compliance calculation
        total_controls = len(SecurityDomain)
        domains_with_strengths = len(set([s.domain for s in strengths]))
        domains_with_critical_weaknesses = len(set([w.domain for w in weaknesses 
                                                  if w.weakness_level == WeaknessLevel.CRITICAL]))
        
        compliance_percentage = (domains_with_strengths / total_controls) * 100
        compliance_percentage -= domains_with_critical_weaknesses * 10
        
        return max(0, min(100, compliance_percentage))

    def _calculate_pci_compliance(self, strengths: List[SecurityStrength], 
                                weaknesses: List[SecurityWeakness]) -> float:
        """Calculate PCI DSS compliance percentage"""
        # PCI DSS focuses heavily on data protection and cryptography
        crypto_strengths = len([s for s in strengths if s.domain == SecurityDomain.CRYPTOGRAPHY])
        data_protection_strengths = len([s for s in strengths if s.domain == SecurityDomain.DATA_PROTECTION])
        
        crypto_weaknesses = len([w for w in weaknesses if w.domain == SecurityDomain.CRYPTOGRAPHY])
        data_weaknesses = len([w for w in weaknesses if w.domain == SecurityDomain.DATA_PROTECTION])
        
        base_score = 50
        base_score += (crypto_strengths + data_protection_strengths) * 15
        base_score -= (crypto_weaknesses + data_weaknesses) * 20
        
        return max(0, min(100, base_score))

    # Placeholder methods for remaining domain analyzers
    async def _analyze_authorization_strengths(self, *args) -> List[SecurityStrength]:
        return []
    
    async def _analyze_output_encoding_strengths(self, *args) -> List[SecurityStrength]:
        return []
    
    async def _analyze_logging_strengths(self, *args) -> List[SecurityStrength]:
        return []
    
    async def _analyze_configuration_strengths(self, *args) -> List[SecurityStrength]:
        return []
    
    async def _analyze_data_protection_strengths(self, *args) -> List[SecurityStrength]:
        return []
    
    async def _analyze_business_logic_strengths(self, *args) -> List[SecurityStrength]:
        return []
    
    async def _analyze_file_upload_strengths(self, *args) -> List[SecurityStrength]:
        return []
    
    async def _analyze_api_security_strengths(self, *args) -> List[SecurityStrength]:
        return []
    
    async def _analyze_infrastructure_strengths(self, *args) -> List[SecurityStrength]:
        return []
    
    # Placeholder weakness correlators
    async def _correlate_authorization_weaknesses(self, *args) -> List[SecurityWeakness]:
        return []
    
    async def _correlate_output_encoding_weaknesses(self, *args) -> List[SecurityWeakness]:
        return []
    
    async def _correlate_cryptography_weaknesses(self, *args) -> List[SecurityWeakness]:
        return []
    
    async def _correlate_session_weaknesses(self, *args) -> List[SecurityWeakness]:
        return []
    
    async def _correlate_error_handling_weaknesses(self, *args) -> List[SecurityWeakness]:
        return []
    
    async def _correlate_logging_weaknesses(self, *args) -> List[SecurityWeakness]:
        return []
    
    async def _correlate_configuration_weaknesses(self, *args) -> List[SecurityWeakness]:
        return []
    
    async def _correlate_network_weaknesses(self, *args) -> List[SecurityWeakness]:
        return []
    
    async def _correlate_data_protection_weaknesses(self, *args) -> List[SecurityWeakness]:
        return []
    
    async def _correlate_business_logic_weaknesses(self, *args) -> List[SecurityWeakness]:
        return []
    
    async def _correlate_file_upload_weaknesses(self, *args) -> List[SecurityWeakness]:
        return []
    
    async def _correlate_api_security_weaknesses(self, *args) -> List[SecurityWeakness]:
        return []
    
    async def _correlate_infrastructure_weaknesses(self, *args) -> List[SecurityWeakness]:
        return []
    
    # Placeholder domain analyzers
    async def _analyze_authorization_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}
    
    async def _analyze_input_validation_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}
    
    async def _analyze_output_encoding_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}
    
    async def _analyze_cryptography_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}
    
    async def _analyze_session_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}
    
    async def _analyze_error_handling_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}
    
    async def _analyze_logging_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}
    
    async def _analyze_configuration_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}
    
    async def _analyze_network_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}
    
    async def _analyze_data_protection_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}
    
    async def _analyze_business_logic_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}
    
    async def _analyze_file_upload_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}
    
    async def _analyze_api_security_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}
    
    async def _analyze_infrastructure_domain(self, *args) -> Dict[str, Any]:
        return {'strengths': [], 'weaknesses': [], 'domain_score': 5.0}

# Export main class
__all__ = ['SecurityPostureAnalyzer', 'SecurityPosture', 'SecurityStrength', 'SecurityWeakness', 'SecurityDomain']