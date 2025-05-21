#!/usr/bin/env python3
# SecureScout - Advanced Report Generator

import os
import json
import time
import logging
import datetime
import uuid
import hashlib
from typing import Dict, List, Any, Optional, Union
import jinja2
import markdown
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import numpy as np
from dataclasses import dataclass, field, asdict

# Configure logging
logger = logging.getLogger("securescout.reporting")

@dataclass
class ReportConfig:
    """Configuration for report generation."""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scan_id: str = ""
    target_url: str = ""
    target_name: str = ""
    format: str = "html"  # html, pdf, json, csv, md
    include_executive_summary: bool = True
    include_technical_details: bool = True
    include_remediation: bool = True
    include_appendices: bool = True
    include_charts: bool = True
    include_evidence: bool = True
    include_raw_data: bool = False
    max_evidence_length: int = 1000
    company_name: str = "SecureScout"
    company_logo: Optional[str] = None
    report_template: Optional[str] = None
    custom_css: Optional[str] = None
    output_dir: str = ""
    severity_filter: List[str] = field(default_factory=lambda: ["critical", "high", "medium", "low", "info"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

@dataclass
class FindingSummary:
    """Summary of vulnerability findings."""
    total_count: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    unique_cwe_count: int = 0
    vuln_types_count: Dict[str, int] = field(default_factory=dict)
    affected_components: Dict[str, int] = field(default_factory=dict)
    severity_distribution: Dict[str, float] = field(default_factory=dict)
    
    def calculate_risk_score(self) -> float:
        """Calculate overall risk score based on findings."""
        # CVSS-based risk calculation (simplified)
        weights = {
            "critical": 10.0,
            "high": 8.0,
            "medium": 5.0,
            "low": 3.0,
            "info": 0.5
        }
        
        weighted_sum = (
            self.critical_count * weights["critical"] +
            self.high_count * weights["high"] +
            self.medium_count * weights["medium"] +
            self.low_count * weights["low"] +
            self.info_count * weights["info"]
        )
        
        total_findings = self.get_total_count()
        
        # Return a risk score on a scale of 0-10
        if total_findings == 0:
            return 0.0
        
        # Base score is weighted average
        base_score = weighted_sum / total_findings
        
        # Apply logarithmic scaling for large numbers of findings
        volume_factor = min(1 + np.log1p(total_findings / 10) / 2, 1.5)
        
        # Critical findings have a greater impact
        critical_factor = 1 + (self.critical_count / max(total_findings, 1)) * 0.5
        
        # Calculate final score (capped at 10)
        risk_score = min(base_score * volume_factor * critical_factor, 10.0)
        
        return round(risk_score, 2)
    
    def get_risk_level(self) -> str:
        """Get risk level description based on score."""
        score = self.calculate_risk_score()
        
        if score >= 9.0:
            return "Critical"
        elif score >= 7.0:
            return "High"
        elif score >= 4.0:
            return "Medium"
        elif score >= 1.0:
            return "Low"
        else:
            return "Informational"
    
    def get_total_count(self) -> int:
        """Get total count of findings."""
        return (self.critical_count + self.high_count + 
                self.medium_count + self.low_count + self.info_count)
    
    def calculate_severity_distribution(self) -> Dict[str, float]:
        """Calculate severity distribution percentage."""
        total = self.get_total_count()
        if total == 0:
            return {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0
            }
        
        return {
            "critical": round(self.critical_count / total * 100, 1),
            "high": round(self.high_count / total * 100, 1),
            "medium": round(self.medium_count / total * 100, 1),
            "low": round(self.low_count / total * 100, 1),
            "info": round(self.info_count / total * 100, 1)
        }
    
    def update_from_findings(self, findings: List[Dict[str, Any]]) -> None:
        """Update summary statistics from a list of findings."""
        # Reset counters
        self.total_count = len(findings)
        self.critical_count = 0
        self.high_count = 0
        self.medium_count = 0
        self.low_count = 0
        self.info_count = 0
        self.vuln_types_count = {}
        self.affected_components = {}
        
        # Track unique CWEs
        unique_cwes = set()
        
        # Count findings by severity and type
        for finding in findings:
            severity = finding.get('severity', 'info').lower()
            
            if severity == 'critical':
                self.critical_count += 1
            elif severity == 'high':
                self.high_count += 1
            elif severity == 'medium':
                self.medium_count += 1
            elif severity == 'low':
                self.low_count += 1
            else:
                self.info_count += 1
            
            # Count by vulnerability type
            vuln_type = finding.get('vulnerability_type') or finding.get('category', 'unknown')
            if vuln_type in self.vuln_types_count:
                self.vuln_types_count[vuln_type] += 1
            else:
                self.vuln_types_count[vuln_type] = 1
            
            # Track CWEs
            cwe_id = finding.get('cwe_id')
            if cwe_id:
                unique_cwes.add(cwe_id)
            
            # Track affected components/locations
            location = finding.get('location', '')
            if location:
                component = self._extract_component_from_url(location)
                if component in self.affected_components:
                    self.affected_components[component] += 1
                else:
                    self.affected_components[component] = 1
        
        # Update unique CWE count
        self.unique_cwe_count = len(unique_cwes)
        
        # Calculate severity distribution
        self.severity_distribution = self.calculate_severity_distribution()
    
    def _extract_component_from_url(self, url: str) -> str:
        """Extract component name from URL for categorization."""
        try:
            from urllib.parse import urlparse
            
            parsed_url = urlparse(url)
            path = parsed_url.path.strip('/')
            
            # If path is empty, use hostname
            if not path:
                return parsed_url.netloc
            
            # Extract first component of path
            components = path.split('/')
            component = components[0] if components else 'root'
            
            return component
            
        except Exception:
            return "unknown"

class ReportGenerator:
    """
    Advanced report generator for SecureScout.
    Creates comprehensive security reports in various formats.
    """
    
    def __init__(self, config: ReportConfig):
        """
        Initialize the report generator.
        
        Args:
            config: Report configuration
        """
        self.config = config
        self.template_env = self._setup_templates()
        self.charts_data = {}
        
        # Set up output directory
        if not self.config.output_dir:
            self.config.output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'reports'
            )
        
        # Ensure output directory exists
        os.makedirs(self.config.output_dir, exist_ok=True)
    
    def _setup_templates(self) -> jinja2.Environment:
        """Set up Jinja2 template environment."""
        # Find template directory
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        
        # Create Jinja2 environment
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        env.filters['markdown'] = self._markdown_filter
        env.filters['b64encode'] = self._base64_encode_filter
        env.filters['to_json'] = self._to_json_filter
        env.filters['truncate_evidence'] = self._truncate_evidence_filter
        
        return env
    
    def _markdown_filter(self, text: str) -> str:
        """Convert markdown to HTML."""
        if not text:
            return ""
        return markdown.markdown(text, extensions=['tables', 'fenced_code'])
    
    def _base64_encode_filter(self, data: bytes) -> str:
        """Encode binary data to base64 string."""
        if not data:
            return ""
        return base64.b64encode(data).decode('utf-8')
    
    def _to_json_filter(self, data: Any) -> str:
        """Convert data to JSON string."""
        return json.dumps(data, indent=2, default=str)
    
    def _truncate_evidence_filter(self, text: str, max_length: int = None) -> str:
        """Truncate evidence text to a maximum length."""
        if not text:
            return ""
        
        max_len = max_length or self.config.max_evidence_length
        
        if len(text) <= max_len:
            return text
        
        return text[:max_len] + "... [truncated]"
    
    def generate_report(self, scan_results: Dict[str, Any]) -> str:
        """
        Generate a report based on scan results.
        
        Args:
            scan_results: Scan results data
            
        Returns:
            Path to the generated report file
        """
        # Extract findings
        findings = scan_results.get('findings', [])
        
        # Filter findings by severity if needed
        if self.config.severity_filter and self.config.severity_filter != ["all"]:
            findings = [f for f in findings if f.get('severity', '').lower() in self.config.severity_filter]
        
        # Generate summary statistics
        summary = FindingSummary()
        summary.update_from_findings(findings)
        
        # Generate charts if enabled
        if self.config.include_charts:
            self.charts_data = self._generate_charts(findings, summary)
        
        # Prepare report data
        report_data = {
            'report_id': self.config.report_id,
            'scan_id': self.config.scan_id or scan_results.get('scan_id', 'unknown'),
            'target_url': self.config.target_url or scan_results.get('target_url', 'unknown'),
            'target_name': self.config.target_name or scan_results.get('target_name', ''),
            'company_name': self.config.company_name,
            'company_logo': self.config.company_logo,
            'scan_type': scan_results.get('scan_type', 'standard'),
            'scan_modules': scan_results.get('modules', []),
            'start_time': scan_results.get('start_time'),
            'end_time': scan_results.get('end_time'),
            'duration': self._calculate_duration(
                scan_results.get('start_time'), 
                scan_results.get('end_time')
            ),
            'report_time': datetime.datetime.utcnow().isoformat(),
            'findings': findings,
            'summary': summary,
            'charts': self.charts_data,
            'statistics': scan_results.get('stats', {}),
            'config': self.config.to_dict(),
            'risk_score': summary.calculate_risk_score(),
            'risk_level': summary.get_risk_level()
        }
        
        # Generate the report based on the specified format
        if self.config.format == 'html':
            return self._generate_html_report(report_data)
        elif self.config.format == 'pdf':
            return self._generate_pdf_report(report_data)
        elif self.config.format == 'json':
            return self._generate_json_report(report_data)
        elif self.config.format == 'csv':
            return self._generate_csv_report(findings)
        elif self.config.format == 'md':
            return self._generate_markdown_report(report_data)
        else:
            raise ValueError(f"Unsupported report format: {self.config.format}")
    
    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """Calculate duration between start and end time."""
        if not start_time or not end_time:
            return "Unknown"
        
        try:
            # Parse ISO format timestamps
            start = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            # Calculate duration
            duration = end - start
            
            # Format duration
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if hours > 0:
                return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
            else:
                return f"{int(minutes)}m {int(seconds)}s"
        except Exception as e:
            logger.error(f"Error calculating duration: {e}")
            return "Unknown"
    
    def _generate_charts(self, findings: List[Dict[str, Any]], summary: FindingSummary) -> Dict[str, str]:
        """
        Generate charts for the report.
        
        Args:
            findings: List of vulnerability findings
            summary: Summary statistics
            
        Returns:
            Dictionary of chart images encoded as base64 data URLs
        """
        charts = {}
        
        try:
            # Set up Matplotlib with dark style
            plt.style.use('dark_background')
            
            # 1. Severity distribution pie chart
            if summary.total_count > 0:
                fig, ax = plt.subplots(figsize=(8, 6))
                
                # Define data
                labels = []
                sizes = []
                colors = []
                explode = []
                
                severity_map = {
                    "critical": {"label": "Critical", "color": "#E53935", "explode": 0.1},
                    "high": {"label": "High", "color": "#FF5252", "explode": 0.05},
                    "medium": {"label": "Medium", "color": "#FFB74D", "explode": 0},
                    "low": {"label": "Low", "color": "#4FC3F7", "explode": 0},
                    "info": {"label": "Info", "color": "#78909C", "explode": 0}
                }
                
                # Only include severities with counts > 0
                for severity, count_attr in [
                    ("critical", "critical_count"),
                    ("high", "high_count"),
                    ("medium", "medium_count"),
                    ("low", "low_count"),
                    ("info", "info_count")
                ]:
                    count = getattr(summary, count_attr)
                    if count > 0:
                        labels.append(severity_map[severity]["label"])
                        sizes.append(count)
                        colors.append(severity_map[severity]["color"])
                        explode.append(severity_map[severity]["explode"])
                
                # Create pie chart
                wedges, texts, autotexts = ax.pie(
                    sizes, 
                    explode=explode,
                    labels=None,  # No labels on the wedges
                    autopct='%1.1f%%',
                    shadow=True,
                    colors=colors,
                    startangle=90,
                    textprops={'color': 'white', 'weight': 'bold'}
                )
                
                # Fix autopct text color
                for autotext in autotexts:
                    autotext.set_color('white')
                
                # Equal aspect ratio ensures that pie is drawn as a circle
                ax.axis('equal')
                
                # Add custom legend
                ax.legend(
                    wedges, 
                    [f"{label} ({size})" for label, size in zip(labels, sizes)],
                    title="Severity Levels",
                    loc="center left",
                    bbox_to_anchor=(1, 0, 0.5, 1)
                )
                
                plt.title('Vulnerability Severity Distribution', color='white', fontsize=14)
                plt.tight_layout()
                
                # Convert to base64 image
                charts['severity_pie'] = self._fig_to_base64(fig)
                plt.close(fig)
            
            # 2. Vulnerability types bar chart
            if summary.vuln_types_count:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Sort by count, descending
                sorted_types = sorted(
                    summary.vuln_types_count.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                
                # Limit to top 10 for readability
                if len(sorted_types) > 10:
                    sorted_types = sorted_types[:10]
                    
                types = [t[0] for t in sorted_types]
                counts = [t[1] for t in sorted_types]
                
                # Create horizontal bar chart
                bars = ax.barh(types, counts, color='#4FC3F7')
                
                # Add count labels
                for bar in bars:
                    width = bar.get_width()
                    ax.text(
                        width + 0.3, 
                        bar.get_y() + bar.get_height()/2,
                        f'{int(width)}',
                        va='center', 
                        color='white',
                        fontweight='bold'
                    )
                
                ax.set_xlabel('Number of Findings', color='white')
                ax.set_title('Top Vulnerability Types', color='white', fontsize=14)
                
                # Make labels readable
                plt.tight_layout()
                
                # Convert to base64 image
                charts['vuln_types_bar'] = self._fig_to_base64(fig)
                plt.close(fig)
            
            # 3. Risk score gauge chart
            fig, ax = plt.subplots(figsize=(8, 4), subplot_kw={'projection': 'polar'})
            
            # Calculate risk score (0-10)
            risk_score = summary.calculate_risk_score()
            
            # Convert to angle (0-180 degrees, in radians)
            theta = np.pi * (risk_score / 10)
            
            # Create a colorful gauge background
            theta_range = np.linspace(0, np.pi, 1000)
            radius = 0.8
            width = 0.2
            
            # Create gradient colors for the gauge
            cmap = plt.get_cmap('RdYlGn_r')  # Red -> Yellow -> Green (reversed)
            colors = cmap(np.linspace(0, 1, len(theta_range)))
            
            # Draw gauge background
            for i in range(len(theta_range) - 1):
                ax.bar(
                    (theta_range[i] + theta_range[i+1]) / 2,
                    radius,
                    width=width,
                    bottom=0.7,
                    color=colors[i],
                    alpha=0.6,
                    edgecolor=None
                )
            
            # Add needle
            ax.plot([0, theta], [0, radius + 0.7], color='white', linewidth=3)
            
            # Draw circle at base of needle
            ax.scatter(0, 0, color='white', s=100, zorder=3)
            
            # Set up gauge properties
            ax.set_rticks([])  # No radial ticks
            ax.set_xticks(np.linspace(0, np.pi, 6))  # Add ticks at 0, 2, 4, 6, 8, 10
            ax.set_xticklabels(['0', '2', '4', '6', '8', '10'], fontsize=12, color='white')
            ax.spines['polar'].set_visible(False)  # Hide the outer circle
            
            # Show only the upper half
            ax.set_thetamin(0)
            ax.set_thetamax(180)
            
            # Add risk score text
            ax.text(
                0, 0, 
                f"{risk_score:.1f}", 
                ha='center', 
                va='center', 
                fontsize=24, 
                color='white',
                fontweight='bold'
            )
            
            # Add risk level text
            risk_level = summary.get_risk_level()
            ax.text(
                np.pi/2, 0.3, 
                risk_level, 
                ha='center', 
                va='center', 
                fontsize=14, 
                color='white',
                fontweight='bold'
            )
            
            ax.set_title('Overall Risk Score', color='white', fontsize=14, pad=15)
            
            plt.tight_layout()
            
            # Convert to base64 image
            charts['risk_gauge'] = self._fig_to_base64(fig)
            plt.close(fig)
            
            # 4. Affected components chart
            if summary.affected_components:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Sort by count, descending
                sorted_components = sorted(
                    summary.affected_components.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                
                # Limit to top 10 for readability
                if len(sorted_components) > 10:
                    sorted_components = sorted_components[:10]
                    
                components = [c[0] for c in sorted_components]
                counts = [c[1] for c in sorted_components]
                
                # Create horizontal bar chart
                bars = ax.barh(components, counts, color='#8E86FF')
                
                # Add count labels
                for bar in bars:
                    width = bar.get_width()
                    ax.text(
                        width + 0.3, 
                        bar.get_y() + bar.get_height()/2,
                        f'{int(width)}',
                        va='center', 
                        color='white',
                        fontweight='bold'
                    )
                
                ax.set_xlabel('Number of Findings', color='white')
                ax.set_title('Most Affected Components', color='white', fontsize=14)
                
                # Make labels readable
                plt.tight_layout()
                
                # Convert to base64 image
                charts['components_bar'] = self._fig_to_base64(fig)
                plt.close(fig)
            
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
        
        return charts
    
    def _fig_to_base64(self, fig: plt.Figure) -> str:
        """Convert matplotlib figure to base64 data URL for HTML embedding."""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', transparent=True, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{img_str}"
    
    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate HTML report.
        
        Args:
            report_data: Report data
            
        Returns:
            Path to the generated HTML file
        """
        try:
            # Load template
            template_name = self.config.report_template or 'html_report.html'
            template = self.template_env.get_template(template_name)
            
            # Render template
            html_content = template.render(**report_data)
            
            # Define output file path
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            target_domain = self._get_domain(report_data['target_url'])
            filename = f"report_{target_domain}_{timestamp}.html"
            output_path = os.path.join(self.config.output_dir, filename)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            raise
    
    def _generate_pdf_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate PDF report.
        
        Args:
            report_data: Report data
            
        Returns:
            Path to the generated PDF file
        """
        try:
            # First generate HTML report
            html_report_path = self._generate_html_report(report_data)
            
            # Define output file path
            pdf_path = html_report_path.replace('.html', '.pdf')
            
            # Convert HTML to PDF
            # This would normally use a library like weasyprint, pdfkit, or a headless browser
            # For this example, we'll simulate the conversion
            logger.info(f"Converting HTML to PDF: {html_report_path} -> {pdf_path}")
            
            # Simulate PDF conversion - in a real implementation, use something like:
            # import weasyprint
            # weasyprint.HTML(html_report_path).write_pdf(pdf_path)
            
            # For now, just create a placeholder file
            with open(pdf_path, 'w', encoding='utf-8') as f:
                f.write("PDF report would be generated here in a real implementation.")
            
            logger.info(f"PDF report generated: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise
    
    def _generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate JSON report.
        
        Args:
            report_data: Report data
            
        Returns:
            Path to the generated JSON file
        """
        try:
            # Define output file path
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            target_domain = self._get_domain(report_data['target_url'])
            filename = f"report_{target_domain}_{timestamp}.json"
            output_path = os.path.join(self.config.output_dir, filename)
            
            # Remove chart data (base64 images) to keep JSON size manageable
            clean_data = report_data.copy()
            if 'charts' in clean_data:
                del clean_data['charts']
            
            # Convert datetime objects to strings
            json_content = json.dumps(clean_data, indent=2, default=str)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_content)
            
            logger.info(f"JSON report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating JSON report: {e}")
            raise
    
    def _generate_csv_report(self, findings: List[Dict[str, Any]]) -> str:
        """
        Generate CSV report of findings.
        
        Args:
            findings: List of vulnerability findings
            
        Returns:
            Path to the generated CSV file
        """
        try:
            # Define output file path
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            target_domain = self._get_domain(self.config.target_url)
            filename = f"findings_{target_domain}_{timestamp}.csv"
            output_path = os.path.join(self.config.output_dir, filename)
            
            # Create a DataFrame from findings
            df = pd.DataFrame(findings)
            
            # Select and reorder columns for CSV
            columns = [
                'id', 'title', 'vulnerability_type', 'severity', 'confidence', 'cwe_id',
                'cvss_score', 'location', 'parameter', 'description'
            ]
            
            # Only include columns that exist
            csv_columns = [col for col in columns if col in df.columns]
            
            # If no valid columns, use all columns
            if not csv_columns:
                csv_columns = df.columns
            
            # Write to CSV file
            df.to_csv(output_path, columns=csv_columns, index=False)
            
            logger.info(f"CSV report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            raise
    
    def _generate_markdown_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate Markdown report.
        
        Args:
            report_data: Report data
            
        Returns:
            Path to the generated Markdown file
        """
        try:
            # Load template
            template_name = 'markdown_report.md'
            template = self.template_env.get_template(template_name)
            
            # Render template
            md_content = template.render(**report_data)
            
            # Define output file path
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            target_domain = self._get_domain(report_data['target_url'])
            filename = f"report_{target_domain}_{timestamp}.md"
            output_path = os.path.join(self.config.output_dir, filename)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"Markdown report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating Markdown report: {e}")
            raise
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL for use in filenames."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]
            # Replace dots with underscores for filename
            return domain.replace('.', '_')
        except Exception:
            # If URL parsing fails, return a safe default
            return 'target'

# Example usage
def generate_report(scan_results: Dict[str, Any], 
                   output_format: str = 'html',
                   output_dir: str = None) -> str:
    """
    Generate a security report from scan results.
    
    Args:
        scan_results: Scan results dictionary
        output_format: Report format (html, pdf, json, csv, md)
        output_dir: Output directory for the report file
        
    Returns:
        Path to the generated report file
    """
    # Create report configuration
    config = ReportConfig(
        scan_id=scan_results.get('scan_id', str(uuid.uuid4())),
        target_url=scan_results.get('target_url', ''),
        format=output_format,
        output_dir=output_dir or os.path.join(os.getcwd(), 'reports')
    )
    
    # Create report generator
    generator = ReportGenerator(config)
    
    # Generate report
    return generator.generate_report(scan_results)

if __name__ == "__main__":
    # Example usage with mock data
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python report_generator.py <scan_results_json_file> [output_format] [output_dir]")
        sys.exit(1)
    
    # Load scan results from JSON file
    with open(sys.argv[1], 'r') as f:
        scan_results = json.load(f)
    
    # Get optional arguments
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'html'
    output_dir = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Generate report
    report_path = generate_report(scan_results, output_format, output_dir)
    
    print(f"Report generated: {report_path}")