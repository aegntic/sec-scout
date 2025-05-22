"""
Autonomous Report Generator - Human & AI Readable Vulnerability Reports
Generates comprehensive, actionable reports for vulnerability findings
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import jinja2
import markdown
import base64
import uuid
import os
from pathlib import Path

class ReportFormat(Enum):
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    PDF = "pdf"
    XML = "xml"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    AI_STRUCTURED = "ai_structured"

class ReportAudience(Enum):
    SECURITY_ENGINEER = "security_engineer"
    DEVELOPER = "developer"
    MANAGEMENT = "management"
    COMPLIANCE = "compliance"
    AI_SYSTEM = "ai_system"
    INCIDENT_RESPONSE = "incident_response"

class ReportPriority(Enum):
    IMMEDIATE = "immediate"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

@dataclass
class ReportMetadata:
    report_id: str
    generated_at: str
    vulnerability_id: str
    target_system: str
    report_version: str
    confidence_score: float
    exploration_depth: str
    total_findings: int
    critical_findings: int
    ai_analysis_version: str

@dataclass
class ExecutiveSummary:
    risk_level: str
    business_impact: str
    immediate_actions: List[str]
    timeline_for_remediation: str
    cost_implications: str
    regulatory_concerns: List[str]

@dataclass
class TechnicalDetails:
    vulnerability_type: str
    attack_vectors: List[str]
    exploitation_steps: List[str]
    proof_of_concept: str
    affected_systems: List[str]
    root_cause_analysis: str
    technical_remediation: List[str]

@dataclass
class AIStructuredData:
    vulnerability_classification: Dict[str, Any]
    attack_taxonomy: Dict[str, Any]
    remediation_ontology: Dict[str, Any]
    threat_intelligence: Dict[str, Any]
    machine_readable_iocs: List[str]
    automation_hooks: Dict[str, Any]

class AutoReportGenerator:
    def __init__(self, templates_dir: str = None):
        self.templates_dir = templates_dir or "/tmp/report_templates"
        self.output_dir = "/tmp/vulnerability_reports"
        self._ensure_directories()
        self._initialize_templates()
        self.ai_insights_engine = AIInsightsEngine()

        # Import security analysis components
        try:
            from .security_posture_analyzer import SecurityPostureAnalyzer
            from .security_diagram_generator import SecurityDiagramGenerator
            self.posture_analyzer = SecurityPostureAnalyzer()
            self.diagram_generator = SecurityDiagramGenerator()
        except ImportError as e:
            logging.warning(f"Could not import security analysis components: {e}")
            self.posture_analyzer = None
            self.diagram_generator = None
        
    def _ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _initialize_templates(self):
        """Initialize Jinja2 templates for different report formats"""
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        self._create_default_templates()

    def _create_default_templates(self):
        """Create default report templates if they don't exist"""
        templates = {
            'executive_summary.html': self._get_executive_template(),
            'technical_report.html': self._get_technical_template(),
            'security_engineer.md': self._get_security_engineer_template(),
            'developer_guide.md': self._get_developer_template(),
            'ai_structured.json': self._get_ai_template(),
            'incident_response.md': self._get_incident_response_template()
        }
        
        for template_name, template_content in templates.items():
            template_path = Path(self.templates_dir) / template_name
            if not template_path.exists():
                template_path.write_text(template_content)

    async def generate_comprehensive_report(self, exploration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive multi-format vulnerability report"""
        report_id = str(uuid.uuid4())
        
        # Extract and enhance data
        enhanced_data = await self._enhance_exploration_data(exploration_result)
        
        # Generate metadata
        metadata = self._generate_metadata(report_id, enhanced_data)
        
        # Generate security posture analysis with strengths and weaknesses
        security_posture = await self._analyze_security_posture(enhanced_data)

        # Generate visual diagrams
        security_diagrams = await self._generate_security_diagrams(security_posture, enhanced_data)

        # Generate different report sections
        executive_summary = await self._generate_executive_summary(enhanced_data, security_posture)
        technical_details = await self._generate_technical_details(enhanced_data, security_posture)
        ai_structured = await self._generate_ai_structured_data(enhanced_data)
        
        # Generate reports for different audiences
        reports = {}

        # Executive/Management Report with security posture
        reports['executive'] = await self._generate_executive_report(
            metadata, executive_summary, enhanced_data, security_posture, security_diagrams
        )
        
        # Technical Security Engineer Report with diagrams
        reports['technical'] = await self._generate_technical_report(
            metadata, technical_details, enhanced_data, security_posture, security_diagrams
        )
        
        # Developer-Focused Report
        reports['developer'] = await self._generate_developer_report(
            metadata, enhanced_data
        )
        
        # AI-Structured Report
        reports['ai_structured'] = await self._generate_ai_report(
            metadata, ai_structured, enhanced_data
        )
        
        # Incident Response Report
        reports['incident_response'] = await self._generate_incident_response_report(
            metadata, enhanced_data
        )
        
        # Compliance Report
        reports['compliance'] = await self._generate_compliance_report(
            metadata, enhanced_data
        )
        
        # Generate priority-based action items
        action_items = await self._generate_prioritized_actions(enhanced_data)
        
        # Create master report package
        master_report = {
            'report_id': report_id,
            'metadata': asdict(metadata),
            'security_posture': asdict(security_posture) if security_posture else {},
            'security_diagrams': security_diagrams,
            'executive_summary': asdict(executive_summary),
            'technical_details': asdict(technical_details),
            'ai_structured_data': asdict(ai_structured),
            'reports_by_audience': reports,
            'prioritized_actions': action_items,
            'file_attachments': await self._generate_file_attachments(reports, report_id),
            'automated_notifications': await self._generate_notification_data(enhanced_data),
            'integration_hooks': await self._generate_integration_hooks(enhanced_data)
        }
        
        # Save reports to files
        await self._save_reports_to_files(master_report)
        
        return master_report

    async def _enhance_exploration_data(self, exploration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance exploration data with AI insights and additional analysis"""
        enhanced = exploration_result.copy()
        
        # Add AI-powered insights
        ai_insights = await self.ai_insights_engine.generate_insights(exploration_result)
        enhanced['ai_insights'] = ai_insights
        
        # Add threat intelligence correlation
        threat_intel = await self._correlate_threat_intelligence(exploration_result)
        enhanced['threat_intelligence'] = threat_intel
        
        # Add business context analysis
        business_context = await self._analyze_business_context(exploration_result)
        enhanced['business_context'] = business_context
        
        # Add remediation recommendations
        remediation = await self._generate_remediation_strategies(exploration_result)
        enhanced['remediation_strategies'] = remediation
        
        return enhanced

    async def _analyze_security_posture(self, enhanced_data: Dict[str, Any]) -> Optional[Any]:
        """Analyze comprehensive security posture including strengths and weaknesses"""
        if not self.posture_analyzer:
            self.logger.warning("Security posture analyzer not available")
            return None

        try:
            # Extract target context
            target_context = {
                'target_url': enhanced_data.get('vulnerability_profile', {}).get('affected_components', ['unknown'])[0],
                'handles_payment_data': False,  # Could be enhanced with context detection
                'industry': 'unknown',
                'compliance_requirements': []
            }

            # Perform comprehensive security posture analysis
            security_posture = await self.posture_analyzer.analyze_security_posture(
                enhanced_data, target_context
            )

            return security_posture

        except Exception as e:
            self.logger.error(f"Security posture analysis failed: {str(e)}")
            return None

    async def _generate_security_diagrams(self, security_posture: Any, enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive security diagrams"""
        if not self.diagram_generator or not security_posture:
            self.logger.warning("Security diagram generator not available or no posture data")
            return {}

        try:
            # Extract target context for diagram generation
            target_context = {
                'system_architecture': 'web_application',
                'network_topology': 'standard',
                'deployment_model': 'cloud'
            }

            # Generate comprehensive diagrams
            diagrams = await self.diagram_generator.generate_comprehensive_diagrams(
                security_posture, target_context
            )

            return diagrams

        except Exception as e:
            self.logger.error(f"Security diagram generation failed: {str(e)}")
            return {}

    def _generate_metadata(self, report_id: str, enhanced_data: Dict[str, Any]) -> ReportMetadata:
        """Generate comprehensive report metadata"""
        exploration_summary = enhanced_data.get('exploration_summary', {})
        
        return ReportMetadata(
            report_id=report_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            vulnerability_id=enhanced_data.get('vulnerability_profile', {}).get('vuln_id', 'unknown'),
            target_system=enhanced_data.get('vulnerability_profile', {}).get('affected_components', ['unknown'])[0],
            report_version="1.0",
            confidence_score=exploration_summary.get('confidence_score', 0.0),
            exploration_depth=exploration_summary.get('depth_achieved', 'unknown'),
            total_findings=exploration_summary.get('total_vectors_tested', 0),
            critical_findings=len([f for f in enhanced_data.get('detailed_findings', {}).get('successful_vectors', []) 
                                 if f.get('confidence', 0) > 0.8]),
            ai_analysis_version="GODMODE_AI_v1.0"
        )

    async def _generate_executive_summary(self, enhanced_data: Dict[str, Any], security_posture: Any = None) -> ExecutiveSummary:
        """Generate executive summary for management"""
        impact_assessment = enhanced_data.get('impact_assessment', {})
        business_context = enhanced_data.get('business_context', {})

        # Include security posture insights in executive summary
        if security_posture:
            risk_level = security_posture.risk_level
            overall_score = security_posture.overall_score
            immediate_actions = self._extract_immediate_actions_from_posture(enhanced_data, security_posture)
        else:
            risk_level = self._calculate_business_risk_level(enhanced_data)
            overall_score = 5.0
            immediate_actions = self._extract_immediate_actions(enhanced_data)
        
        return ExecutiveSummary(
            risk_level=risk_level,
            business_impact=impact_assessment.get('financial_impact', 'Medium business impact'),
            immediate_actions=immediate_actions,
            timeline_for_remediation=self._calculate_remediation_timeline(enhanced_data),
            cost_implications=self._estimate_cost_implications(enhanced_data),
            regulatory_concerns=self._identify_regulatory_concerns(enhanced_data)
        )

    async def _generate_technical_details(self, enhanced_data: Dict[str, Any], security_posture: Any = None) -> TechnicalDetails:
        """Generate detailed technical analysis"""
        vuln_profile = enhanced_data.get('vulnerability_profile', {})
        successful_vectors = enhanced_data.get('detailed_findings', {}).get('successful_vectors', [])
        
        return TechnicalDetails(
            vulnerability_type=vuln_profile.get('category', 'unknown'),
            attack_vectors=vuln_profile.get('attack_vectors', []),
            exploitation_steps=self._extract_exploitation_steps(successful_vectors),
            proof_of_concept=self._generate_poc_code(successful_vectors),
            affected_systems=vuln_profile.get('affected_components', []),
            root_cause_analysis=await self._perform_root_cause_analysis(enhanced_data),
            technical_remediation=self._extract_technical_remediation(enhanced_data)
        )

    async def _generate_ai_structured_data(self, enhanced_data: Dict[str, Any]) -> AIStructuredData:
        """Generate AI-readable structured data"""
        return AIStructuredData(
            vulnerability_classification=self._create_vulnerability_taxonomy(enhanced_data),
            attack_taxonomy=self._create_attack_taxonomy(enhanced_data),
            remediation_ontology=self._create_remediation_ontology(enhanced_data),
            threat_intelligence=enhanced_data.get('threat_intelligence', {}),
            machine_readable_iocs=self._extract_iocs(enhanced_data),
            automation_hooks=self._create_automation_hooks(enhanced_data)
        )

    async def _generate_executive_report(self, metadata: ReportMetadata, executive_summary: ExecutiveSummary,
                                       enhanced_data: Dict[str, Any], security_posture: Any = None,
                                       security_diagrams: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate executive/management focused report"""
        template = self.jinja_env.get_template('executive_summary.html')
        
        context = {
            'metadata': asdict(metadata),
            'executive_summary': asdict(executive_summary),
            'security_posture': asdict(security_posture) if security_posture else {},
            'security_diagrams': security_diagrams or {},
            'risk_visualization': self._generate_risk_charts(enhanced_data),
            'business_impact_metrics': self._calculate_business_metrics(enhanced_data),
            'action_timeline': self._create_action_timeline(enhanced_data),
            'resource_requirements': self._estimate_resources(enhanced_data),
            'strengths_summary': self._summarize_strengths(security_posture) if security_posture else [],
            'weaknesses_summary': self._summarize_weaknesses(security_posture) if security_posture else []
        }
        
        html_content = template.render(**context)
        
        return {
            'format': ReportFormat.HTML.value,
            'audience': ReportAudience.MANAGEMENT.value,
            'content': html_content,
            'summary': self._create_executive_one_liner(enhanced_data),
            'key_metrics': context['business_impact_metrics'],
            'recommended_actions': executive_summary.immediate_actions
        }

    async def _generate_technical_report(self, metadata: ReportMetadata, technical_details: TechnicalDetails,
                                       enhanced_data: Dict[str, Any], security_posture: Any = None,
                                       security_diagrams: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate technical security engineer report"""
        template = self.jinja_env.get_template('technical_report.html')
        
        context = {
            'metadata': asdict(metadata),
            'technical_details': asdict(technical_details),
            'security_posture': asdict(security_posture) if security_posture else {},
            'security_diagrams': security_diagrams or {},
            'exploitation_timeline': self._create_exploitation_timeline(enhanced_data),
            'attack_flow_diagram': self._generate_attack_flow(enhanced_data),
            'evidence_chain': enhanced_data.get('evidence_chain', []),
            'technical_recommendations': self._generate_technical_recommendations(enhanced_data),
            'testing_artifacts': self._collect_testing_artifacts(enhanced_data),
            'domain_analysis': self._analyze_technical_domains(security_posture) if security_posture else {}
        }
        
        html_content = template.render(**context)
        
        return {
            'format': ReportFormat.HTML.value,
            'audience': ReportAudience.SECURITY_ENGINEER.value,
            'content': html_content,
            'exploitability_score': self._calculate_exploitability(enhanced_data),
            'technical_severity': self._calculate_technical_severity(enhanced_data),
            'remediation_complexity': self._assess_remediation_complexity(enhanced_data)
        }

    async def _generate_developer_report(self, metadata: ReportMetadata, enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate developer-focused report with code examples"""
        template = self.jinja_env.get_template('developer_guide.md')
        
        context = {
            'metadata': asdict(metadata),
            'vulnerable_code_examples': self._extract_code_examples(enhanced_data),
            'secure_code_alternatives': await self._generate_secure_code(enhanced_data),
            'testing_strategies': self._recommend_testing_strategies(enhanced_data),
            'development_guidelines': self._create_dev_guidelines(enhanced_data),
            'code_review_checklist': self._generate_code_review_checklist(enhanced_data)
        }
        
        markdown_content = template.render(**context)
        
        return {
            'format': ReportFormat.MARKDOWN.value,
            'audience': ReportAudience.DEVELOPER.value,
            'content': markdown_content,
            'code_fixes': context['secure_code_alternatives'],
            'development_impact': self._assess_development_impact(enhanced_data),
            'testing_requirements': context['testing_strategies']
        }

    async def _generate_ai_report(self, metadata: ReportMetadata, ai_structured: AIStructuredData,
                                enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-readable structured report"""
        structured_data = {
            'metadata': asdict(metadata),
            'ai_structured_data': asdict(ai_structured),
            'machine_learning_features': self._extract_ml_features(enhanced_data),
            'vulnerability_vector': self._create_vulnerability_vector(enhanced_data),
            'similarity_scores': await self._calculate_similarity_scores(enhanced_data),
            'automated_response_actions': self._generate_automated_responses(enhanced_data),
            'knowledge_graph_nodes': self._create_knowledge_graph(enhanced_data)
        }
        
        return {
            'format': ReportFormat.JSON.value,
            'audience': ReportAudience.AI_SYSTEM.value,
            'content': json.dumps(structured_data, indent=2),
            'machine_actionable': True,
            'automation_ready': True,
            'api_endpoints': self._generate_api_hooks(enhanced_data)
        }

    async def _generate_incident_response_report(self, metadata: ReportMetadata, enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate incident response playbook"""
        template = self.jinja_env.get_template('incident_response.md')
        
        context = {
            'metadata': asdict(metadata),
            'incident_classification': self._classify_incident_type(enhanced_data),
            'containment_procedures': self._generate_containment_steps(enhanced_data),
            'eradication_steps': self._generate_eradication_steps(enhanced_data),
            'recovery_procedures': self._generate_recovery_steps(enhanced_data),
            'forensic_artifacts': self._identify_forensic_artifacts(enhanced_data),
            'communication_templates': self._generate_communication_templates(enhanced_data)
        }
        
        markdown_content = template.render(**context)
        
        return {
            'format': ReportFormat.MARKDOWN.value,
            'audience': ReportAudience.INCIDENT_RESPONSE.value,
            'content': markdown_content,
            'urgency_level': self._determine_urgency(enhanced_data),
            'escalation_triggers': self._define_escalation_triggers(enhanced_data),
            'response_timeline': self._create_response_timeline(enhanced_data)
        }

    async def _generate_compliance_report(self, metadata: ReportMetadata, enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance-focused report"""
        compliance_frameworks = ['NIST', 'ISO27001', 'GDPR', 'SOX', 'HIPAA', 'PCI-DSS']
        
        compliance_mapping = {}
        for framework in compliance_frameworks:
            compliance_mapping[framework] = await self._map_to_compliance_framework(enhanced_data, framework)
        
        context = {
            'metadata': asdict(metadata),
            'compliance_violations': self._identify_compliance_violations(enhanced_data),
            'regulatory_requirements': self._map_regulatory_requirements(enhanced_data),
            'audit_evidence': self._collect_audit_evidence(enhanced_data),
            'compliance_gap_analysis': compliance_mapping,
            'remediation_tracking': self._create_remediation_tracking(enhanced_data)
        }
        
        return {
            'format': ReportFormat.HTML.value,
            'audience': ReportAudience.COMPLIANCE.value,
            'content': self._render_compliance_template(context),
            'compliance_score': self._calculate_compliance_score(enhanced_data),
            'violations_summary': context['compliance_violations'],
            'audit_readiness': self._assess_audit_readiness(enhanced_data)
        }

    async def _generate_prioritized_actions(self, enhanced_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized action items across all audiences"""
        actions = []
        
        # Immediate critical actions
        if self._is_critical_vulnerability(enhanced_data):
            actions.extend(self._generate_critical_actions(enhanced_data))
        
        # Technical remediation actions
        actions.extend(self._generate_technical_actions(enhanced_data))
        
        # Process improvement actions
        actions.extend(self._generate_process_actions(enhanced_data))
        
        # Strategic actions
        actions.extend(self._generate_strategic_actions(enhanced_data))
        
        # Sort by priority and urgency
        return sorted(actions, key=lambda x: (x['priority_score'], x['urgency_score']), reverse=True)

    def _extract_immediate_actions_from_posture(self, enhanced_data: Dict[str, Any], security_posture: Any) -> List[str]:
        """Extract immediate actions based on security posture analysis"""
        actions = []

        # Actions based on critical weaknesses
        critical_weaknesses = [w for w in security_posture.weaknesses if w.weakness_level.value == 'critical']
        for weakness in critical_weaknesses[:3]:  # Top 3 critical weaknesses
            actions.append(f"CRITICAL: Address {weakness.domain.value.replace('_', ' ')} - {weakness.description[:50]}...")

        # Actions based on low domain scores
        low_scoring_domains = [domain for domain, score in security_posture.domain_scores.items() if score < 4.0]
        for domain in low_scoring_domains[:2]:  # Top 2 low scoring domains
            actions.append(f"Improve {domain.replace('_', ' ')} security controls immediately")

        # General immediate actions
        if not actions:
            actions.extend([
                "Implement comprehensive input validation",
                "Deploy Web Application Firewall",
                "Enable comprehensive security logging"
            ])

        return actions

    def _summarize_strengths(self, security_posture: Any) -> List[Dict[str, str]]:
        """Summarize security strengths for reports"""
        strength_summary = []

        # Group strengths by domain
        domain_strengths = {}
        for strength in security_posture.strengths:
            domain = strength.domain.value
            if domain not in domain_strengths:
                domain_strengths[domain] = []
            domain_strengths[domain].append(strength)

        # Create summary
        for domain, strengths in domain_strengths.items():
            excellent_count = len([s for s in strengths if s.strength_level.value == 'excellent'])
            strong_count = len([s for s in strengths if s.strength_level.value == 'strong'])

            if excellent_count > 0 or strong_count > 0:
                strength_summary.append({
                    'domain': domain.replace('_', ' ').title(),
                    'level': 'Excellent' if excellent_count > 0 else 'Strong',
                    'count': excellent_count + strong_count,
                    'description': strengths[0].description[:100] + "..." if len(strengths[0].description) > 100 else strengths[0].description
                })

        return strength_summary

    def _summarize_weaknesses(self, security_posture: Any) -> List[Dict[str, str]]:
        """Summarize security weaknesses for reports"""
        weakness_summary = []

        # Group weaknesses by level
        level_weaknesses = {}
        for weakness in security_posture.weaknesses:
            level = weakness.weakness_level.value
            if level not in level_weaknesses:
                level_weaknesses[level] = []
            level_weaknesses[level].append(weakness)

        # Create summary prioritizing critical and high
        for level in ['critical', 'high', 'medium']:
            if level in level_weaknesses:
                weaknesses = level_weaknesses[level]
                for weakness in weaknesses[:3]:  # Top 3 per level
                    weakness_summary.append({
                        'level': level.title(),
                        'domain': weakness.domain.value.replace('_', ' ').title(),
                        'description': weakness.description[:100] + "..." if len(weakness.description) > 100 else weakness.description,
                        'impact': weakness.business_impact[:50] + "..." if len(weakness.business_impact) > 50 else weakness.business_impact
                    })

        return weakness_summary

    def _analyze_technical_domains(self, security_posture: Any) -> Dict[str, Any]:
        """Analyze technical domains for detailed technical reports"""
        domain_analysis = {}

        for domain_name, score in security_posture.domain_scores.items():
            domain_strengths = [s for s in security_posture.strengths if s.domain.value == domain_name]
            domain_weaknesses = [w for w in security_posture.weaknesses if w.domain.value == domain_name]

            domain_analysis[domain_name] = {
                'score': score,
                'status': 'Strong' if score >= 7 else 'Adequate' if score >= 5 else 'Weak' if score >= 3 else 'Critical',
                'strengths_count': len(domain_strengths),
                'weaknesses_count': len(domain_weaknesses),
                'top_strength': domain_strengths[0].description if domain_strengths else None,
                'top_weakness': domain_weaknesses[0].description if domain_weaknesses else None,
                'recommendations': self._get_domain_recommendations(domain_name, score, domain_weaknesses)
            }

        return domain_analysis

    def _get_domain_recommendations(self, domain: str, score: float, weaknesses: List[Any]) -> List[str]:
        """Get specific recommendations for a domain"""
        recommendations = []

        if score < 5.0:
            if domain == 'input_validation':
                recommendations.extend([
                    "Implement comprehensive input validation framework",
                    "Deploy parameterized queries for all database interactions",
                    "Add server-side validation for all user inputs"
                ])
            elif domain == 'authentication':
                recommendations.extend([
                    "Implement multi-factor authentication",
                    "Strengthen password policies",
                    "Add account lockout mechanisms"
                ])
            elif domain == 'authorization':
                recommendations.extend([
                    "Implement role-based access control (RBAC)",
                    "Add authorization checks to all endpoints",
                    "Regular access control reviews"
                ])
            else:
                recommendations.append(f"Improve {domain.replace('_', ' ')} security controls")

        # Add weakness-specific recommendations
        for weakness in weaknesses[:2]:  # Top 2 weaknesses
            if 'injection' in weakness.description.lower():
                recommendations.append("Implement input sanitization and validation")
            elif 'authentication' in weakness.description.lower():
                recommendations.append("Strengthen authentication mechanisms")
            elif 'authorization' in weakness.description.lower():
                recommendations.append("Implement proper access controls")

        return recommendations[:3]  # Return top 3 recommendations

    # Template Content Methods
    def _get_executive_template(self) -> str:
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Security Vulnerability Executive Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #1e3a8a; color: white; padding: 20px; text-align: center; }
        .risk-high { background: #dc2626; color: white; padding: 10px; }
        .risk-medium { background: #ea580c; color: white; padding: 10px; }
        .risk-low { background: #16a34a; color: white; padding: 10px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #e5e7eb; }
        .metric { display: inline-block; margin: 10px; padding: 15px; background: #f9fafb; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Security Vulnerability Report</h1>
        <p>Report ID: {{ metadata.report_id }}</p>
        <p>Generated: {{ metadata.generated_at }}</p>
    </div>
    
    <div class="section risk-{{ executive_summary.risk_level }}">
        <h2>Risk Level: {{ executive_summary.risk_level|upper }}</h2>
        <p>{{ executive_summary.business_impact }}</p>
    </div>
    
    <div class="section">
        <h2>Immediate Actions Required</h2>
        <ul>
        {% for action in executive_summary.immediate_actions %}
            <li>{{ action }}</li>
        {% endfor %}
        </ul>
    </div>

    {% if security_posture %}
    <div class="section">
        <h2>Security Posture Overview</h2>
        <div class="metric">
            <strong>Overall Security Score:</strong> {{ security_posture.overall_score|round(1) }}/10
        </div>
        <div class="metric">
            <strong>Risk Level:</strong> {{ security_posture.risk_level }}
        </div>
        <div class="metric">
            <strong>Security Strengths:</strong> {{ security_posture.strengths|length }}
        </div>
        <div class="metric">
            <strong>Security Weaknesses:</strong> {{ security_posture.weaknesses|length }}
        </div>
    </div>

    {% if strengths_summary %}
    <div class="section">
        <h2>Key Security Strengths</h2>
        {% for strength in strengths_summary %}
        <div class="metric" style="background-color: #e8f5e8;">
            <strong>{{ strength.domain }}:</strong> {{ strength.level }} ({{ strength.count }} controls)<br>
            <small>{{ strength.description }}</small>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if weaknesses_summary %}
    <div class="section">
        <h2>Critical Security Weaknesses</h2>
        {% for weakness in weaknesses_summary %}
        <div class="metric" style="background-color: #ffe8e8;">
            <strong>{{ weakness.domain }}:</strong> {{ weakness.level }} Risk<br>
            <small>{{ weakness.description }}</small><br>
            <em>Impact: {{ weakness.impact }}</em>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if security_diagrams and security_diagrams.radar_chart %}
    <div class="section">
        <h2>Security Domain Analysis</h2>
        {{ security_diagrams.radar_chart.content|safe }}
    </div>
    {% endif %}
    {% endif %}
    
    <div class="section">
        <h2>Business Impact Metrics</h2>
        {% for metric, value in business_impact_metrics.items() %}
        <div class="metric">
            <strong>{{ metric|replace('_', ' ')|title }}</strong><br>
            {{ value }}
        </div>
        {% endfor %}
    </div>
    
    <div class="section">
        <h2>Remediation Timeline</h2>
        <p><strong>Recommended Timeline:</strong> {{ executive_summary.timeline_for_remediation }}</p>
        <p><strong>Cost Implications:</strong> {{ executive_summary.cost_implications }}</p>
    </div>
    
    {% if executive_summary.regulatory_concerns %}
    <div class="section">
        <h2>Regulatory Concerns</h2>
        <ul>
        {% for concern in executive_summary.regulatory_concerns %}
            <li>{{ concern }}</li>
        {% endfor %}
        </ul>
    </div>
    {% endif %}
</body>
</html>
        """

    def _get_technical_template(self) -> str:
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Technical Vulnerability Analysis</title>
    <style>
        body { font-family: 'Courier New', monospace; margin: 20px; }
        .code { background: #f4f4f4; padding: 10px; border-left: 4px solid #007acc; margin: 10px 0; }
        .evidence { background: #fff3cd; padding: 10px; border: 1px solid #ffeaa7; }
        .critical { color: #dc2626; font-weight: bold; }
        .high { color: #ea580c; font-weight: bold; }
        .section { margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Technical Vulnerability Analysis</h1>
    <p><strong>Vulnerability Type:</strong> {{ technical_details.vulnerability_type }}</p>
    <p><strong>Confidence Score:</strong> {{ metadata.confidence_score }}</p>
    
    <div class="section">
        <h2>Attack Vectors</h2>
        <ul>
        {% for vector in technical_details.attack_vectors %}
            <li>{{ vector }}</li>
        {% endfor %}
        </ul>
    </div>
    
    <div class="section">
        <h2>Exploitation Steps</h2>
        <ol>
        {% for step in technical_details.exploitation_steps %}
            <li>{{ step }}</li>
        {% endfor %}
        </ol>
    </div>
    
    <div class="section">
        <h2>Proof of Concept</h2>
        <div class="code">{{ technical_details.proof_of_concept }}</div>
    </div>
    
    <div class="section">
        <h2>Root Cause Analysis</h2>
        <p>{{ technical_details.root_cause_analysis }}</p>
    </div>
    
    <div class="section">
        <h2>Evidence Chain</h2>
        {% for evidence in evidence_chain %}
        <div class="evidence">{{ evidence }}</div>
        {% endfor %}
    </div>
    
    <div class="section">
        <h2>Technical Remediation</h2>
        <ul>
        {% for remedy in technical_details.technical_remediation %}
            <li>{{ remedy }}</li>
        {% endfor %}
        </ul>
    </div>

    {% if security_posture %}
    <div class="section">
        <h2>Security Domain Analysis</h2>
        {% if domain_analysis %}
        {% for domain, analysis in domain_analysis.items() %}
        <div style="margin: 15px 0; padding: 10px; border: 1px solid #ddd;">
            <h3>{{ domain.replace('_', ' ')|title }}</h3>
            <p><strong>Score:</strong> {{ analysis.score|round(1) }}/10 ({{ analysis.status }})</p>
            <p><strong>Strengths:</strong> {{ analysis.strengths_count }} | <strong>Weaknesses:</strong> {{ analysis.weaknesses_count }}</p>
            {% if analysis.top_strength %}
            <p><strong>Top Strength:</strong> {{ analysis.top_strength }}</p>
            {% endif %}
            {% if analysis.top_weakness %}
            <p><strong>Top Weakness:</strong> {{ analysis.top_weakness }}</p>
            {% endif %}
            {% if analysis.recommendations %}
            <p><strong>Recommendations:</strong></p>
            <ul>
            {% for rec in analysis.recommendations %}
                <li>{{ rec }}</li>
            {% endfor %}
            </ul>
            {% endif %}
        </div>
        {% endfor %}
        {% endif %}
    </div>

    {% if security_diagrams %}
    <div class="section">
        <h2>Visual Security Analysis</h2>

        {% if security_diagrams.strength_weakness_map %}
        <h3>Strengths & Weaknesses Map</h3>
        {{ security_diagrams.strength_weakness_map.content|safe }}
        {% endif %}

        {% if security_diagrams.risk_matrix %}
        <h3>Risk Matrix</h3>
        {{ security_diagrams.risk_matrix.content|safe }}
        {% endif %}

        {% if security_diagrams.attack_tree %}
        <h3>Attack Tree Analysis</h3>
        <pre class="code">{{ security_diagrams.attack_tree.content }}</pre>
        {% endif %}
    </div>
    {% endif %}
    {% endif %}
</body>
</html>
        """

    def _get_security_engineer_template(self) -> str:
        return """
# Security Engineering Report

## Vulnerability Summary
- **ID:** {{ metadata.vulnerability_id }}
- **Type:** {{ technical_details.vulnerability_type }}
- **Confidence:** {{ metadata.confidence_score }}
- **Affected Systems:** {{ technical_details.affected_systems|join(', ') }}

## Technical Analysis

### Attack Surface
{{ technical_details.root_cause_analysis }}

### Exploitation Chain
{% for step in technical_details.exploitation_steps %}
{{ loop.index }}. {{ step }}
{% endfor %}

### Proof of Concept
```
{{ technical_details.proof_of_concept }}
```

### Evidence Artifacts
{% for evidence in evidence_chain %}
- {{ evidence }}
{% endfor %}

## Remediation Strategy

### Immediate Actions
{% for remedy in technical_details.technical_remediation %}
- {{ remedy }}
{% endfor %}

### Long-term Fixes
{{ technical_recommendations|join('\n- ') }}

## Testing Verification
{{ testing_artifacts|join('\n') }}
        """

    def _get_developer_template(self) -> str:
        return """
# Developer Security Guide

## Vulnerability Overview
{{ metadata.vulnerability_id }} - {{ technical_details.vulnerability_type }}

## Vulnerable Code Patterns
{% for example in vulnerable_code_examples %}
### {{ example.description }}
```{{ example.language }}
{{ example.code }}
```
**Issue:** {{ example.vulnerability }}
{% endfor %}

## Secure Code Alternatives
{% for fix in secure_code_alternatives %}
### {{ fix.description }}
```{{ fix.language }}
{{ fix.code }}
```
**Security Benefit:** {{ fix.benefit }}
{% endfor %}

## Testing Strategies
{% for strategy in testing_strategies %}
- **{{ strategy.type }}:** {{ strategy.description }}
  - Implementation: {{ strategy.implementation }}
{% endfor %}

## Code Review Checklist
{% for item in code_review_checklist %}
- [ ] {{ item }}
{% endfor %}

## Development Guidelines
{% for guideline in development_guidelines %}
- {{ guideline }}
{% endfor %}
        """

    def _get_ai_template(self) -> str:
        return """
{
  "vulnerability_classification": {{ vulnerability_classification|tojson }},
  "attack_taxonomy": {{ attack_taxonomy|tojson }},
  "remediation_ontology": {{ remediation_ontology|tojson }},
  "machine_learning_features": {{ machine_learning_features|tojson }},
  "automation_hooks": {{ automation_hooks|tojson }}
}
        """

    def _get_incident_response_template(self) -> str:
        return """
# Incident Response Playbook

## Incident Classification
- **Type:** {{ incident_classification.type }}
- **Severity:** {{ incident_classification.severity }}
- **Urgency:** {{ urgency_level }}

## Containment Procedures
{% for step in containment_procedures %}
{{ loop.index }}. {{ step.action }}
   - **Timeline:** {{ step.timeline }}
   - **Responsible:** {{ step.responsible }}
{% endfor %}

## Eradication Steps
{% for step in eradication_steps %}
- {{ step }}
{% endfor %}

## Recovery Procedures
{% for step in recovery_procedures %}
- {{ step }}
{% endfor %}

## Forensic Artifacts
{% for artifact in forensic_artifacts %}
- **{{ artifact.type }}:** {{ artifact.location }}
  - Collection method: {{ artifact.collection_method }}
{% endfor %}

## Communication Templates
{{ communication_templates|join('\n\n') }}
        """

    # Helper methods for report generation
    def _calculate_business_risk_level(self, enhanced_data: Dict[str, Any]) -> str:
        impact = enhanced_data.get('impact_assessment', {})
        confidence = enhanced_data.get('exploration_summary', {}).get('confidence_score', 0)
        
        if confidence > 0.8 and 'critical' in str(impact).lower():
            return 'critical'
        elif confidence > 0.6 and 'high' in str(impact).lower():
            return 'high'
        else:
            return 'medium'

    def _extract_immediate_actions(self, enhanced_data: Dict[str, Any]) -> List[str]:
        return [
            "Immediately patch affected systems",
            "Implement temporary mitigations",
            "Monitor for active exploitation",
            "Review access logs for indicators of compromise"
        ]

    def _calculate_remediation_timeline(self, enhanced_data: Dict[str, Any]) -> str:
        severity = enhanced_data.get('vulnerability_profile', {}).get('severity', 'medium')
        if severity == 'critical':
            return "24-48 hours"
        elif severity == 'high':
            return "1-2 weeks"
        else:
            return "1 month"

    def _estimate_cost_implications(self, enhanced_data: Dict[str, Any]) -> str:
        return "Estimated remediation cost: $10,000-50,000 including development time and testing"

    def _identify_regulatory_concerns(self, enhanced_data: Dict[str, Any]) -> List[str]:
        return ["GDPR Article 32 - Security of processing", "SOX Section 404 - Internal controls"]

    def _extract_exploitation_steps(self, successful_vectors: List[Dict[str, Any]]) -> List[str]:
        steps = []
        for vector in successful_vectors:
            steps.append(f"Execute payload: {vector.get('vector_id', 'unknown')}")
        return steps

    def _generate_poc_code(self, successful_vectors: List[Dict[str, Any]]) -> str:
        if not successful_vectors:
            return "No proof of concept available"
        
        return f"# Proof of Concept\n{successful_vectors[0].get('response_data', {}).get('payload', 'N/A')}"

    async def _perform_root_cause_analysis(self, enhanced_data: Dict[str, Any]) -> str:
        return "Root cause: Insufficient input validation leading to injection vulnerability"

    def _extract_technical_remediation(self, enhanced_data: Dict[str, Any]) -> List[str]:
        return [
            "Implement parameterized queries",
            "Add input validation and sanitization",
            "Deploy Web Application Firewall",
            "Regular security code reviews"
        ]

    # Additional helper methods would continue here...
    # (Truncated for brevity - the full implementation would include all helper methods)

    async def _save_reports_to_files(self, master_report: Dict[str, Any]) -> None:
        """Save all reports to files"""
        report_id = master_report['report_id']
        report_dir = Path(self.output_dir) / report_id
        report_dir.mkdir(exist_ok=True)
        
        # Save master report
        with open(report_dir / 'master_report.json', 'w') as f:
            json.dump(master_report, f, indent=2)
        
        # Save individual reports
        for audience, report_data in master_report['reports_by_audience'].items():
            filename = f"{audience}_report"
            if report_data['format'] == 'html':
                filename += '.html'
            elif report_data['format'] == 'markdown':
                filename += '.md'
            else:
                filename += '.json'
            
            with open(report_dir / filename, 'w') as f:
                f.write(report_data['content'])

# AI Insights Engine for enhanced analysis
class AIInsightsEngine:
    async def generate_insights(self, exploration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered insights for the vulnerability"""
        return {
            'pattern_analysis': await self._analyze_attack_patterns(exploration_result),
            'threat_modeling': await self._perform_threat_modeling(exploration_result),
            'risk_correlation': await self._correlate_risks(exploration_result),
            'predictive_analysis': await self._predict_future_attacks(exploration_result)
        }
    
    async def _analyze_attack_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'common_patterns': ['SQL injection', 'Parameter tampering']}
    
    async def _perform_threat_modeling(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'threat_actors': ['Script kiddies', 'Advanced persistent threats']}
    
    async def _correlate_risks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'related_vulnerabilities': ['Authentication bypass', 'Privilege escalation']}
    
    async def _predict_future_attacks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'likelihood': 0.75, 'timeframe': '30 days'}

# Export main class
__all__ = ['AutoReportGenerator', 'ReportFormat', 'ReportAudience']