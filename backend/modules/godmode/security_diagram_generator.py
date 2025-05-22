"""
Security Diagram Generator - Visual Security Posture Representation
Generates comprehensive visual diagrams showing both strengths and weaknesses
"""

import asyncio
import json
import base64
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import logging
import colorsys
import math

from .security_posture_analyzer import SecurityPosture, SecurityStrength, SecurityWeakness, SecurityDomain, StrengthLevel, WeaknessLevel

class DiagramType(Enum):
    RADAR_CHART = "radar_chart"
    HEATMAP = "heatmap"
    NETWORK_TOPOLOGY = "network_topology"
    RISK_MATRIX = "risk_matrix"
    TIMELINE = "timeline"
    ATTACK_TREE = "attack_tree"
    STRENGTH_WEAKNESS_MAP = "strength_weakness_map"
    COMPLIANCE_DASHBOARD = "compliance_dashboard"

class OutputFormat(Enum):
    SVG = "svg"
    HTML_CANVAS = "html_canvas"
    MERMAID = "mermaid"
    D3_JSON = "d3_json"
    PLOTLY_JSON = "plotly_json"

@dataclass
class DiagramConfig:
    diagram_type: DiagramType
    output_format: OutputFormat
    width: int = 800
    height: int = 600
    color_scheme: str = "default"
    show_labels: bool = True
    show_legend: bool = True
    interactive: bool = True
    animation: bool = True

@dataclass
class DiagramElement:
    element_type: str
    position: Tuple[float, float]
    size: Tuple[float, float]
    color: str
    label: str
    data: Dict[str, Any]
    style: Dict[str, str]

class SecurityDiagramGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.color_schemes = {
            'default': {
                'excellent': '#2E7D32',  # Dark Green
                'strong': '#388E3C',     # Green
                'adequate': '#FBC02D',   # Yellow
                'weak': '#F57C00',       # Orange
                'critical': '#D32F2F',   # Red
                'background': '#FAFAFA', # Light Grey
                'border': '#E0E0E0',     # Grey
                'text': '#212121'        # Dark Grey
            },
            'high_contrast': {
                'excellent': '#1B5E20',
                'strong': '#2E7D32',
                'adequate': '#F57F17',
                'weak': '#E65100',
                'critical': '#B71C1C',
                'background': '#FFFFFF',
                'border': '#000000',
                'text': '#000000'
            },
            'dark_mode': {
                'excellent': '#4CAF50',
                'strong': '#66BB6A',
                'adequate': '#FFEB3B',
                'weak': '#FF9800',
                'critical': '#F44336',
                'background': '#121212',
                'border': '#424242',
                'text': '#FFFFFF'
            }
        }

    async def generate_comprehensive_diagrams(self, security_posture: SecurityPosture, 
                                            target_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive set of security diagrams"""
        
        diagrams = {}
        target_context = target_context or {}
        
        # Generate different types of diagrams
        diagram_configs = [
            DiagramConfig(DiagramType.RADAR_CHART, OutputFormat.SVG),
            DiagramConfig(DiagramType.HEATMAP, OutputFormat.HTML_CANVAS),
            DiagramConfig(DiagramType.RISK_MATRIX, OutputFormat.SVG),
            DiagramConfig(DiagramType.STRENGTH_WEAKNESS_MAP, OutputFormat.SVG),
            DiagramConfig(DiagramType.COMPLIANCE_DASHBOARD, OutputFormat.HTML_CANVAS),
            DiagramConfig(DiagramType.ATTACK_TREE, OutputFormat.MERMAID),
            DiagramConfig(DiagramType.NETWORK_TOPOLOGY, OutputFormat.D3_JSON)
        ]
        
        for config in diagram_configs:
            try:
                diagram_data = await self._generate_diagram(security_posture, config, target_context)
                diagrams[config.diagram_type.value] = diagram_data
            except Exception as e:
                self.logger.error(f"Failed to generate {config.diagram_type.value}: {str(e)}")
                diagrams[config.diagram_type.value] = {'error': str(e)}
        
        # Generate summary visualization
        summary_viz = await self._generate_summary_visualization(security_posture)
        diagrams['summary'] = summary_viz
        
        return diagrams

    async def _generate_diagram(self, security_posture: SecurityPosture, 
                              config: DiagramConfig, target_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a specific type of diagram"""
        
        if config.diagram_type == DiagramType.RADAR_CHART:
            return await self._generate_radar_chart(security_posture, config)
        elif config.diagram_type == DiagramType.HEATMAP:
            return await self._generate_heatmap(security_posture, config)
        elif config.diagram_type == DiagramType.RISK_MATRIX:
            return await self._generate_risk_matrix(security_posture, config)
        elif config.diagram_type == DiagramType.STRENGTH_WEAKNESS_MAP:
            return await self._generate_strength_weakness_map(security_posture, config)
        elif config.diagram_type == DiagramType.COMPLIANCE_DASHBOARD:
            return await self._generate_compliance_dashboard(security_posture, config)
        elif config.diagram_type == DiagramType.ATTACK_TREE:
            return await self._generate_attack_tree(security_posture, config)
        elif config.diagram_type == DiagramType.NETWORK_TOPOLOGY:
            return await self._generate_network_topology(security_posture, config, target_context)
        else:
            raise ValueError(f"Unsupported diagram type: {config.diagram_type}")

    async def _generate_radar_chart(self, security_posture: SecurityPosture, 
                                  config: DiagramConfig) -> Dict[str, Any]:
        """Generate radar chart showing security domain scores"""
        
        domains = list(SecurityDomain)
        domain_scores = security_posture.domain_scores
        colors = self.color_schemes[config.color_scheme]
        
        # SVG generation
        svg_content = f'''
        <svg width="{config.width}" height="{config.height}" viewBox="0 0 {config.width} {config.height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <style>
                    .radar-bg {{ fill: {colors['background']}; stroke: {colors['border']}; stroke-width: 1; }}
                    .radar-grid {{ fill: none; stroke: {colors['border']}; stroke-width: 0.5; opacity: 0.5; }}
                    .radar-axis {{ stroke: {colors['border']}; stroke-width: 1; }}
                    .radar-label {{ fill: {colors['text']}; font-family: Arial, sans-serif; font-size: 12px; text-anchor: middle; }}
                    .radar-area {{ fill: {colors['adequate']}; fill-opacity: 0.3; stroke: {colors['adequate']}; stroke-width: 2; }}
                    .radar-point {{ fill: {colors['strong']}; r: 4; }}
                    .title {{ fill: {colors['text']}; font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; text-anchor: middle; }}
                </style>
            </defs>
            
            <!-- Background -->
            <rect width="{config.width}" height="{config.height}" class="radar-bg"/>
            
            <!-- Title -->
            <text x="{config.width // 2}" y="30" class="title">Security Domain Radar Chart</text>
            
            <!-- Radar Chart -->
            {self._generate_radar_chart_content(domains, domain_scores, config)}
            
            <!-- Legend -->
            {self._generate_radar_legend(config) if config.show_legend else ""}
        </svg>
        '''
        
        return {
            'format': config.output_format.value,
            'content': svg_content.strip(),
            'metadata': {
                'domains_count': len(domains),
                'average_score': sum(domain_scores.values()) / len(domain_scores) if domain_scores else 0,
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        }

    def _generate_radar_chart_content(self, domains: List[SecurityDomain], 
                                    domain_scores: Dict[str, float], config: DiagramConfig) -> str:
        """Generate radar chart SVG content"""
        center_x, center_y = config.width // 2, config.height // 2 - 20
        radius = min(config.width, config.height) // 3
        
        svg_parts = []
        
        # Generate grid circles
        for i in range(1, 6):
            grid_radius = (radius * i) / 5
            svg_parts.append(f'<circle cx="{center_x}" cy="{center_y}" r="{grid_radius}" class="radar-grid"/>')
        
        # Generate axis lines and calculate points
        angle_step = 2 * math.pi / len(domains)
        radar_points = []
        
        for i, domain in enumerate(domains):
            angle = i * angle_step - math.pi / 2  # Start from top
            
            # Axis line
            end_x = center_x + radius * math.cos(angle)
            end_y = center_y + radius * math.sin(angle)
            svg_parts.append(f'<line x1="{center_x}" y1="{center_y}" x2="{end_x}" y2="{end_y}" class="radar-axis"/>')
            
            # Domain label
            label_distance = radius + 20
            label_x = center_x + label_distance * math.cos(angle)
            label_y = center_y + label_distance * math.sin(angle) + 5
            domain_name = domain.value.replace('_', ' ').title()
            svg_parts.append(f'<text x="{label_x}" y="{label_y}" class="radar-label">{domain_name}</text>')
            
            # Calculate point position based on score
            score = domain_scores.get(domain.value, 5.0)
            point_distance = (score / 10.0) * radius
            point_x = center_x + point_distance * math.cos(angle)
            point_y = center_y + point_distance * math.sin(angle)
            radar_points.append(f"{point_x},{point_y}")
        
        # Generate radar area
        if radar_points:
            points_str = " ".join(radar_points)
            svg_parts.append(f'<polygon points="{points_str}" class="radar-area"/>')
            
            # Generate points
            for point in radar_points:
                x, y = point.split(',')
                svg_parts.append(f'<circle cx="{x}" cy="{y}" class="radar-point"/>')
        
        return "\n".join(svg_parts)

    def _generate_radar_legend(self, config: DiagramConfig) -> str:
        """Generate legend for radar chart"""
        legend_x = config.width - 120
        legend_y = 50
        
        legend_items = [
            ('Score: 0-2', 'critical'),
            ('Score: 2-4', 'weak'),
            ('Score: 4-6', 'adequate'),
            ('Score: 6-8', 'strong'),
            ('Score: 8-10', 'excellent')
        ]
        
        legend_svg = ['<g class="legend">']
        for i, (label, color_key) in enumerate(legend_items):
            y_pos = legend_y + i * 20
            color = self.color_schemes[config.color_scheme][color_key]
            legend_svg.append(f'<rect x="{legend_x}" y="{y_pos}" width="12" height="12" fill="{color}"/>')
            legend_svg.append(f'<text x="{legend_x + 16}" y="{y_pos + 9}" class="radar-label" text-anchor="start">{label}</text>')
        legend_svg.append('</g>')
        
        return "\n".join(legend_svg)

    async def _generate_heatmap(self, security_posture: SecurityPosture, 
                              config: DiagramConfig) -> Dict[str, Any]:
        """Generate heatmap showing security strengths and weaknesses by domain"""
        
        domains = list(SecurityDomain)
        domain_scores = security_posture.domain_scores
        
        # Generate HTML Canvas with JavaScript
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Heatmap</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                canvas {{ border: 1px solid #ccc; }}
                .legend {{ margin-top: 20px; }}
                .legend-item {{ display: inline-block; margin-right: 20px; }}
                .legend-color {{ width: 20px; height: 20px; display: inline-block; margin-right: 5px; vertical-align: middle; }}
            </style>
        </head>
        <body>
            <h2>Security Domain Heatmap</h2>
            <canvas id="heatmapCanvas" width="{config.width}" height="{config.height}"></canvas>
            <div class="legend">
                <div class="legend-item"><span class="legend-color" style="background-color: #D32F2F;"></span>Critical (0-2)</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #F57C00;"></span>Weak (2-4)</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #FBC02D;"></span>Adequate (4-6)</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #388E3C;"></span>Strong (6-8)</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #2E7D32;"></span>Excellent (8-10)</div>
            </div>
            
            <script>
                {self._generate_heatmap_javascript(domains, domain_scores, config)}
            </script>
        </body>
        </html>
        '''
        
        return {
            'format': config.output_format.value,
            'content': html_content,
            'metadata': {
                'domains_analyzed': len(domains),
                'visualization_type': 'heatmap',
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        }

    def _generate_heatmap_javascript(self, domains: List[SecurityDomain], 
                                   domain_scores: Dict[str, float], config: DiagramConfig) -> str:
        """Generate JavaScript for heatmap visualization"""
        
        return f'''
        const canvas = document.getElementById('heatmapCanvas');
        const ctx = canvas.getContext('2d');
        
        const domains = {json.dumps([d.value for d in domains])};
        const scores = {json.dumps(domain_scores)};
        
        const cols = Math.ceil(Math.sqrt(domains.length));
        const rows = Math.ceil(domains.length / cols);
        const cellWidth = {config.width} / cols;
        const cellHeight = {config.height} / rows;
        
        function getColor(score) {{
            if (score >= 8) return '#2E7D32';      // Excellent
            else if (score >= 6) return '#388E3C'; // Strong
            else if (score >= 4) return '#FBC02D'; // Adequate
            else if (score >= 2) return '#F57C00'; // Weak
            else return '#D32F2F';                  // Critical
        }}
        
        domains.forEach((domain, index) => {{
            const row = Math.floor(index / cols);
            const col = index % cols;
            const x = col * cellWidth;
            const y = row * cellHeight;
            const score = scores[domain] || 5.0;
            
            // Draw cell background
            ctx.fillStyle = getColor(score);
            ctx.fillRect(x, y, cellWidth, cellHeight);
            
            // Draw border
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, cellWidth, cellHeight);
            
            // Draw domain name
            ctx.fillStyle = '#000';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            const domainName = domain.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
            ctx.fillText(domainName, x + cellWidth/2, y + cellHeight/2 - 10);
            
            // Draw score
            ctx.fillStyle = '#000';
            ctx.font = 'bold 14px Arial';
            ctx.fillText(score.toFixed(1), x + cellWidth/2, y + cellHeight/2 + 10);
        }});
        '''

    async def _generate_risk_matrix(self, security_posture: SecurityPosture, 
                                  config: DiagramConfig) -> Dict[str, Any]:
        """Generate risk matrix showing likelihood vs impact"""
        
        # Analyze weaknesses for risk matrix positioning
        risk_items = []
        for weakness in security_posture.weaknesses:
            likelihood = self._calculate_likelihood(weakness)
            impact = self._calculate_impact(weakness)
            risk_items.append({
                'name': weakness.description[:30] + "..." if len(weakness.description) > 30 else weakness.description,
                'likelihood': likelihood,
                'impact': impact,
                'domain': weakness.domain.value,
                'level': weakness.weakness_level.value
            })
        
        # Generate SVG risk matrix
        svg_content = f'''
        <svg width="{config.width}" height="{config.height}" viewBox="0 0 {config.width} {config.height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <style>
                    .matrix-bg {{ fill: white; stroke: #ccc; stroke-width: 1; }}
                    .grid-line {{ stroke: #ddd; stroke-width: 1; }}
                    .axis-label {{ fill: #333; font-family: Arial, sans-serif; font-size: 14px; text-anchor: middle; }}
                    .title {{ fill: #333; font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; text-anchor: middle; }}
                    .risk-point {{ stroke: #333; stroke-width: 1; }}
                    .risk-label {{ fill: #333; font-family: Arial, sans-serif; font-size: 10px; text-anchor: middle; }}
                </style>
            </defs>
            
            <!-- Background -->
            <rect width="{config.width}" height="{config.height}" fill="white"/>
            
            <!-- Title -->
            <text x="{config.width // 2}" y="30" class="title">Risk Matrix - Likelihood vs Impact</text>
            
            <!-- Matrix content -->
            {self._generate_risk_matrix_content(risk_items, config)}
        </svg>
        '''
        
        return {
            'format': config.output_format.value,
            'content': svg_content.strip(),
            'metadata': {
                'risk_items_count': len(risk_items),
                'high_risk_items': len([r for r in risk_items if r['likelihood'] > 3 and r['impact'] > 3]),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        }

    def _generate_risk_matrix_content(self, risk_items: List[Dict], config: DiagramConfig) -> str:
        """Generate risk matrix SVG content"""
        margin = 80
        matrix_width = config.width - 2 * margin
        matrix_height = config.height - 2 * margin - 50
        
        svg_parts = []
        
        # Draw matrix grid
        svg_parts.append(f'<rect x="{margin}" y="{margin}" width="{matrix_width}" height="{matrix_height}" class="matrix-bg"/>')
        
        # Draw grid lines
        for i in range(1, 5):
            x = margin + (matrix_width * i) / 5
            y = margin + (matrix_height * i) / 5
            svg_parts.append(f'<line x1="{x}" y1="{margin}" x2="{x}" y2="{margin + matrix_height}" class="grid-line"/>')
            svg_parts.append(f'<line x1="{margin}" y1="{y}" x2="{margin + matrix_width}" y2="{y}" class="grid-line"/>')
        
        # Draw axis labels
        svg_parts.append(f'<text x="{margin + matrix_width // 2}" y="{config.height - 20}" class="axis-label">Impact</text>')
        svg_parts.append(f'<text x="20" y="{margin + matrix_height // 2}" class="axis-label" transform="rotate(-90, 20, {margin + matrix_height // 2})">Likelihood</text>')
        
        # Plot risk items
        for i, item in enumerate(risk_items):
            x = margin + (item['impact'] / 5.0) * matrix_width
            y = margin + matrix_height - (item['likelihood'] / 5.0) * matrix_height
            
            # Color based on risk level
            color = self._get_risk_color(item['level'])
            
            # Draw point
            svg_parts.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{color}" class="risk-point"/>')
            
            # Add label if space allows
            if config.show_labels and len(risk_items) < 15:
                svg_parts.append(f'<text x="{x}" y="{y - 10}" class="risk-label">{item["name"][:15]}</text>')
        
        return "\n".join(svg_parts)

    def _get_risk_color(self, level: str) -> str:
        """Get color for risk level"""
        color_map = {
            'critical': '#D32F2F',
            'high': '#F57C00',
            'medium': '#FBC02D',
            'low': '#388E3C',
            'informational': '#2196F3'
        }
        return color_map.get(level, '#757575')

    def _calculate_likelihood(self, weakness: SecurityWeakness) -> float:
        """Calculate likelihood score (1-5) for weakness"""
        # Base likelihood on confidence and exploitation potential
        base_likelihood = weakness.confidence_score * 3
        
        if 'high' in weakness.exploitation_potential.lower():
            base_likelihood += 1.5
        elif 'medium' in weakness.exploitation_potential.lower():
            base_likelihood += 1.0
        elif 'low' in weakness.exploitation_potential.lower():
            base_likelihood += 0.5
        
        return min(5.0, max(1.0, base_likelihood))

    def _calculate_impact(self, weakness: SecurityWeakness) -> float:
        """Calculate impact score (1-5) for weakness"""
        # Base impact on weakness level and business impact
        level_impact = {
            WeaknessLevel.CRITICAL: 5.0,
            WeaknessLevel.HIGH: 4.0,
            WeaknessLevel.MEDIUM: 3.0,
            WeaknessLevel.LOW: 2.0,
            WeaknessLevel.INFORMATIONAL: 1.0
        }
        
        base_impact = level_impact.get(weakness.weakness_level, 3.0)
        
        if 'critical' in weakness.business_impact.lower():
            base_impact = min(5.0, base_impact + 1.0)
        elif 'high' in weakness.business_impact.lower():
            base_impact = min(5.0, base_impact + 0.5)
        
        return base_impact

    async def _generate_strength_weakness_map(self, security_posture: SecurityPosture, 
                                            config: DiagramConfig) -> Dict[str, Any]:
        """Generate comprehensive strength/weakness visualization"""
        
        domains = list(SecurityDomain)
        colors = self.color_schemes[config.color_scheme]
        
        # Create domain analysis
        domain_analysis = {}
        for domain in domains:
            domain_strengths = [s for s in security_posture.strengths if s.domain == domain]
            domain_weaknesses = [w for w in security_posture.weaknesses if w.domain == domain]
            score = security_posture.domain_scores.get(domain.value, 5.0)
            
            domain_analysis[domain.value] = {
                'strengths': len(domain_strengths),
                'weaknesses': len(domain_weaknesses),
                'score': score,
                'status': self._determine_domain_status(score, len(domain_strengths), len(domain_weaknesses))
            }
        
        # Generate SVG
        svg_content = f'''
        <svg width="{config.width}" height="{config.height}" viewBox="0 0 {config.width} {config.height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <style>
                    .bg {{ fill: {colors['background']}; }}
                    .domain-rect {{ stroke: {colors['border']}; stroke-width: 2; rx: 5; }}
                    .strength-bar {{ fill: {colors['strong']}; }}
                    .weakness-bar {{ fill: {colors['critical']}; }}
                    .domain-label {{ fill: {colors['text']}; font-family: Arial, sans-serif; font-size: 12px; font-weight: bold; text-anchor: middle; }}
                    .score-label {{ fill: {colors['text']}; font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; text-anchor: middle; }}
                    .title {{ fill: {colors['text']}; font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; text-anchor: middle; }}
                    .legend-text {{ fill: {colors['text']}; font-family: Arial, sans-serif; font-size: 11px; }}
                </style>
            </defs>
            
            <!-- Background -->
            <rect width="{config.width}" height="{config.height}" class="bg"/>
            
            <!-- Title -->
            <text x="{config.width // 2}" y="30" class="title">Security Strengths & Weaknesses by Domain</text>
            
            <!-- Domain visualization -->
            {self._generate_strength_weakness_content(domain_analysis, config)}
            
            <!-- Legend -->
            {self._generate_strength_weakness_legend(config)}
        </svg>
        '''
        
        return {
            'format': config.output_format.value,
            'content': svg_content.strip(),
            'metadata': {
                'domains_analyzed': len(domains),
                'total_strengths': len(security_posture.strengths),
                'total_weaknesses': len(security_posture.weaknesses),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        }

    def _generate_strength_weakness_content(self, domain_analysis: Dict[str, Any], 
                                          config: DiagramConfig) -> str:
        """Generate strength/weakness map content"""
        svg_parts = []
        
        # Calculate layout
        cols = 4
        rows = math.ceil(len(domain_analysis) / cols)
        cell_width = (config.width - 80) / cols
        cell_height = (config.height - 150) / rows
        
        for i, (domain, data) in enumerate(domain_analysis.items()):
            row = i // cols
            col = i % cols
            x = 40 + col * cell_width
            y = 60 + row * cell_height
            
            # Domain rectangle with color based on score
            domain_color = self._get_score_color(data['score'])
            svg_parts.append(f'<rect x="{x}" y="{y}" width="{cell_width - 10}" height="{cell_height - 10}" fill="{domain_color}" fill-opacity="0.3" class="domain-rect"/>')
            
            # Domain name
            domain_name = domain.replace('_', ' ').title()
            svg_parts.append(f'<text x="{x + cell_width // 2}" y="{y + 20}" class="domain-label">{domain_name[:12]}</text>')
            
            # Score
            svg_parts.append(f'<text x="{x + cell_width // 2}" y="{y + 40}" class="score-label">Score: {data["score"]:.1f}</text>')
            
            # Strength/Weakness bars
            bar_y = y + 50
            bar_width = cell_width - 40
            max_bar_height = cell_height - 80
            
            # Strengths bar
            if data['strengths'] > 0:
                strength_height = min(max_bar_height // 2, data['strengths'] * 10)
                svg_parts.append(f'<rect x="{x + 10}" y="{bar_y}" width="{bar_width // 2 - 5}" height="{strength_height}" class="strength-bar"/>')
                svg_parts.append(f'<text x="{x + bar_width // 4}" y="{bar_y + strength_height + 15}" class="legend-text" text-anchor="middle">Strengths: {data["strengths"]}</text>')
            
            # Weaknesses bar
            if data['weaknesses'] > 0:
                weakness_height = min(max_bar_height // 2, data['weaknesses'] * 10)
                svg_parts.append(f'<rect x="{x + bar_width // 2 + 5}" y="{bar_y}" width="{bar_width // 2 - 5}" height="{weakness_height}" class="weakness-bar"/>')
                svg_parts.append(f'<text x="{x + 3 * bar_width // 4}" y="{bar_y + weakness_height + 15}" class="legend-text" text-anchor="middle">Weaknesses: {data["weaknesses"]}</text>')
        
        return "\n".join(svg_parts)

    def _generate_strength_weakness_legend(self, config: DiagramConfig) -> str:
        """Generate legend for strength/weakness map"""
        legend_y = config.height - 40
        colors = self.color_schemes[config.color_scheme]
        
        return f'''
        <g class="legend">
            <rect x="50" y="{legend_y}" width="15" height="15" class="strength-bar"/>
            <text x="70" y="{legend_y + 12}" class="legend-text">Strengths</text>
            <rect x="150" y="{legend_y}" width="15" height="15" class="weakness-bar"/>
            <text x="170" y="{legend_y + 12}" class="legend-text">Weaknesses</text>
            <text x="300" y="{legend_y + 12}" class="legend-text">Background color indicates domain security score</text>
        </g>
        '''

    def _get_score_color(self, score: float) -> str:
        """Get color based on security score"""
        if score >= 8:
            return '#2E7D32'  # Excellent
        elif score >= 6:
            return '#388E3C'  # Strong
        elif score >= 4:
            return '#FBC02D'  # Adequate
        elif score >= 2:
            return '#F57C00'  # Weak
        else:
            return '#D32F2F'  # Critical

    def _determine_domain_status(self, score: float, strengths: int, weaknesses: int) -> str:
        """Determine overall domain status"""
        if score >= 8 and strengths > weaknesses:
            return 'excellent'
        elif score >= 6 and weaknesses <= strengths:
            return 'strong'
        elif score >= 4:
            return 'adequate'
        elif score >= 2:
            return 'weak'
        else:
            return 'critical'

    async def _generate_compliance_dashboard(self, security_posture: SecurityPosture, 
                                           config: DiagramConfig) -> Dict[str, Any]:
        """Generate compliance dashboard visualization"""
        
        compliance_status = security_posture.compliance_status
        
        # Generate HTML dashboard
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Compliance Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .compliance-card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .compliance-header {{ font-size: 18px; font-weight: bold; margin-bottom: 15px; }}
                .compliance-score {{ font-size: 36px; font-weight: bold; text-align: center; margin: 20px 0; }}
                .compliance-bar {{ width: 100%; height: 20px; background-color: #e0e0e0; border-radius: 10px; overflow: hidden; }}
                .compliance-fill {{ height: 100%; transition: width 0.3s ease; }}
                .score-excellent {{ color: #2E7D32; }}
                .score-good {{ color: #388E3C; }}
                .score-adequate {{ color: #FBC02D; }}
                .score-poor {{ color: #F57C00; }}
                .score-critical {{ color: #D32F2F; }}
                .fill-excellent {{ background-color: #2E7D32; }}
                .fill-good {{ background-color: #388E3C; }}
                .fill-adequate {{ background-color: #FBC02D; }}
                .fill-poor {{ background-color: #F57C00; }}
                .fill-critical {{ background-color: #D32F2F; }}
                h1 {{ text-align: center; color: #333; }}
            </style>
        </head>
        <body>
            <h1>Security Compliance Dashboard</h1>
            <div class="dashboard">
                {self._generate_compliance_cards(compliance_status)}
            </div>
            
            <script>
                // Animate compliance bars on load
                window.addEventListener('load', function() {{
                    const bars = document.querySelectorAll('.compliance-fill');
                    bars.forEach(bar => {{
                        const width = bar.dataset.width;
                        setTimeout(() => {{ bar.style.width = width + '%'; }}, 100);
                    }});
                }});
            </script>
        </body>
        </html>
        '''
        
        return {
            'format': config.output_format.value,
            'content': html_content,
            'metadata': {
                'frameworks_assessed': len(compliance_status),
                'average_compliance': self._calculate_average_compliance(compliance_status),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        }

    def _generate_compliance_cards(self, compliance_status: Dict[str, str]) -> str:
        """Generate compliance cards HTML"""
        cards = []
        
        for framework, status in compliance_status.items():
            # Extract percentage from status string
            percentage = float(status.split('%')[0]) if '%' in status else 0
            
            # Determine score class
            score_class = self._get_compliance_class(percentage)
            
            card_html = f'''
            <div class="compliance-card">
                <div class="compliance-header">{framework.replace('_', ' ')}</div>
                <div class="compliance-score {score_class}">{percentage:.0f}%</div>
                <div class="compliance-bar">
                    <div class="compliance-fill {score_class.replace('score-', 'fill-')}" data-width="{percentage}" style="width: 0%;"></div>
                </div>
                <div style="margin-top: 10px; text-align: center; color: #666;">
                    {self._get_compliance_status_text(percentage)}
                </div>
            </div>
            '''
            cards.append(card_html)
        
        return "\n".join(cards)

    def _get_compliance_class(self, percentage: float) -> str:
        """Get CSS class for compliance percentage"""
        if percentage >= 90:
            return 'score-excellent'
        elif percentage >= 75:
            return 'score-good'
        elif percentage >= 60:
            return 'score-adequate'
        elif percentage >= 40:
            return 'score-poor'
        else:
            return 'score-critical'

    def _get_compliance_status_text(self, percentage: float) -> str:
        """Get status text for compliance percentage"""
        if percentage >= 90:
            return 'Excellent Compliance'
        elif percentage >= 75:
            return 'Good Compliance'
        elif percentage >= 60:
            return 'Adequate Compliance'
        elif percentage >= 40:
            return 'Poor Compliance'
        else:
            return 'Critical Gaps'

    def _calculate_average_compliance(self, compliance_status: Dict[str, str]) -> float:
        """Calculate average compliance percentage"""
        if not compliance_status:
            return 0.0
        
        total = 0
        count = 0
        
        for status in compliance_status.values():
            if '%' in status:
                percentage = float(status.split('%')[0])
                total += percentage
                count += 1
        
        return total / count if count > 0 else 0.0

    async def _generate_attack_tree(self, security_posture: SecurityPosture, 
                                  config: DiagramConfig) -> Dict[str, Any]:
        """Generate attack tree in Mermaid format"""
        
        # Create attack tree based on weaknesses
        attack_paths = self._analyze_attack_paths(security_posture.weaknesses)
        
        mermaid_content = "graph TD\n"
        mermaid_content += "    A[Target System] --> B[Authentication Layer]\n"
        mermaid_content += "    A --> C[Application Layer]\n"
        mermaid_content += "    A --> D[Infrastructure Layer]\n"
        
        # Add attack paths based on weaknesses
        node_id = ord('E')
        for weakness in security_posture.weaknesses:
            if weakness.weakness_level in [WeaknessLevel.HIGH, WeaknessLevel.CRITICAL]:
                domain = weakness.domain.value
                node_letter = chr(node_id)
                
                if 'authentication' in domain:
                    mermaid_content += f"    B --> {node_letter}[{weakness.description[:30]}]\n"
                elif 'input' in domain or 'output' in domain:
                    mermaid_content += f"    C --> {node_letter}[{weakness.description[:30]}]\n"
                else:
                    mermaid_content += f"    D --> {node_letter}[{weakness.description[:30]}]\n"
                
                # Add impact
                impact_node = chr(node_id + 1)
                mermaid_content += f"    {node_letter} --> {impact_node}[{weakness.business_impact[:20]}]\n"
                
                node_id += 2
        
        # Add styling
        mermaid_content += "\n"
        mermaid_content += "    classDef criticalPath fill:#ff6b6b,stroke:#d63031,stroke-width:3px\n"
        mermaid_content += "    classDef highRisk fill:#feca57,stroke:#ff9f43,stroke-width:2px\n"
        mermaid_content += "    classDef normalPath fill:#48dbfb,stroke:#0abde3,stroke-width:1px\n"
        
        return {
            'format': config.output_format.value,
            'content': mermaid_content,
            'metadata': {
                'attack_paths_identified': len(attack_paths),
                'critical_paths': len([w for w in security_posture.weaknesses if w.weakness_level == WeaknessLevel.CRITICAL]),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        }

    def _analyze_attack_paths(self, weaknesses: List[SecurityWeakness]) -> List[Dict[str, Any]]:
        """Analyze potential attack paths from weaknesses"""
        attack_paths = []
        
        for weakness in weaknesses:
            if weakness.weakness_level in [WeaknessLevel.HIGH, WeaknessLevel.CRITICAL]:
                attack_paths.append({
                    'domain': weakness.domain.value,
                    'entry_point': weakness.description,
                    'impact': weakness.business_impact,
                    'likelihood': self._calculate_likelihood(weakness)
                })
        
        return attack_paths

    async def _generate_network_topology(self, security_posture: SecurityPosture, 
                                       config: DiagramConfig, target_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate network topology with security annotations"""
        
        # Create D3.js compatible JSON
        nodes = [
            {'id': 'internet', 'group': 'external', 'label': 'Internet'},
            {'id': 'firewall', 'group': 'security', 'label': 'Firewall'},
            {'id': 'loadbalancer', 'group': 'infrastructure', 'label': 'Load Balancer'},
            {'id': 'webserver', 'group': 'application', 'label': 'Web Server'},
            {'id': 'database', 'group': 'data', 'label': 'Database'},
            {'id': 'users', 'group': 'external', 'label': 'Users'}
        ]
        
        links = [
            {'source': 'users', 'target': 'internet', 'type': 'connection'},
            {'source': 'internet', 'target': 'firewall', 'type': 'connection'},
            {'source': 'firewall', 'target': 'loadbalancer', 'type': 'connection'},
            {'source': 'loadbalancer', 'target': 'webserver', 'type': 'connection'},
            {'source': 'webserver', 'target': 'database', 'type': 'connection'}
        ]
        
        # Add security annotations based on posture
        security_annotations = []
        for weakness in security_posture.weaknesses:
            if weakness.weakness_level in [WeaknessLevel.HIGH, WeaknessLevel.CRITICAL]:
                security_annotations.append({
                    'type': 'vulnerability',
                    'severity': weakness.weakness_level.value,
                    'description': weakness.description,
                    'location': self._map_domain_to_component(weakness.domain)
                })
        
        for strength in security_posture.strengths:
            if strength.strength_level in [StrengthLevel.STRONG, StrengthLevel.EXCELLENT]:
                security_annotations.append({
                    'type': 'protection',
                    'level': strength.strength_level.value,
                    'description': strength.description,
                    'location': self._map_domain_to_component(strength.domain)
                })
        
        d3_data = {
            'nodes': nodes,
            'links': links,
            'security_annotations': security_annotations,
            'layout': {
                'width': config.width,
                'height': config.height,
                'force_strength': -300
            }
        }
        
        return {
            'format': config.output_format.value,
            'content': json.dumps(d3_data, indent=2),
            'metadata': {
                'nodes_count': len(nodes),
                'vulnerabilities_mapped': len([a for a in security_annotations if a['type'] == 'vulnerability']),
                'protections_mapped': len([a for a in security_annotations if a['type'] == 'protection']),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        }

    def _map_domain_to_component(self, domain: SecurityDomain) -> str:
        """Map security domain to network component"""
        domain_mapping = {
            SecurityDomain.AUTHENTICATION: 'webserver',
            SecurityDomain.AUTHORIZATION: 'webserver',
            SecurityDomain.INPUT_VALIDATION: 'webserver',
            SecurityDomain.OUTPUT_ENCODING: 'webserver',
            SecurityDomain.CRYPTOGRAPHY: 'webserver',
            SecurityDomain.SESSION_MANAGEMENT: 'webserver',
            SecurityDomain.ERROR_HANDLING: 'webserver',
            SecurityDomain.LOGGING_MONITORING: 'webserver',
            SecurityDomain.CONFIGURATION: 'webserver',
            SecurityDomain.NETWORK_SECURITY: 'firewall',
            SecurityDomain.DATA_PROTECTION: 'database',
            SecurityDomain.BUSINESS_LOGIC: 'webserver',
            SecurityDomain.FILE_UPLOAD: 'webserver',
            SecurityDomain.API_SECURITY: 'webserver',
            SecurityDomain.INFRASTRUCTURE: 'loadbalancer'
        }
        return domain_mapping.get(domain, 'webserver')

    async def _generate_summary_visualization(self, security_posture: SecurityPosture) -> Dict[str, Any]:
        """Generate summary visualization combining key metrics"""
        
        # Calculate key metrics
        total_strengths = len(security_posture.strengths)
        total_weaknesses = len(security_posture.weaknesses)
        critical_weaknesses = len([w for w in security_posture.weaknesses if w.weakness_level == WeaknessLevel.CRITICAL])
        excellent_strengths = len([s for s in security_posture.strengths if s.strength_level == StrengthLevel.EXCELLENT])
        
        summary_data = {
            'overall_score': security_posture.overall_score,
            'risk_level': security_posture.risk_level,
            'total_strengths': total_strengths,
            'total_weaknesses': total_weaknesses,
            'critical_weaknesses': critical_weaknesses,
            'excellent_strengths': excellent_strengths,
            'domain_scores': security_posture.domain_scores,
            'compliance_summary': security_posture.compliance_status,
            'key_recommendations': security_posture.recommendations[:5]  # Top 5 recommendations
        }
        
        return {
            'format': 'json',
            'content': json.dumps(summary_data, indent=2),
            'metadata': {
                'summary_type': 'comprehensive_security_posture',
                'data_points': len(summary_data),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        }

# Export main class
__all__ = ['SecurityDiagramGenerator', 'DiagramType', 'DiagramConfig', 'OutputFormat']