#!/usr/bin/env python3
# SecureScout - Demo Backend Server

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import time
import random
import json
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
CORS(app)

# Sample data
scan_history = []
active_scans = {}
test_findings = [
    {
        "id": "vuln1",
        "title": "SQL Injection Vulnerability",
        "description": "A SQL injection vulnerability was detected in the search parameter that could allow an attacker to extract data from the database.",
        "severity": "high",
        "category": "Injection",
        "location": "https://example.com/search?q=test",
        "cvss": "8.5",
        "cwe": "89",
        "evidence": "search?q=test' OR 1=1 --",
        "evidenceType": "http",
        "impact": "An attacker could exploit this vulnerability to access, modify, or delete data from the database. This could lead to unauthorized access to sensitive information or complete system compromise.",
        "recommendation": "Use parameterized queries or prepared statements instead of dynamically building SQL queries. Additionally, implement input validation and sanitize user inputs before processing.",
        "references": [
            { "title": "OWASP SQL Injection", "url": "https://owasp.org/www-community/attacks/SQL_Injection" },
            { "title": "CWE-89", "url": "https://cwe.mitre.org/data/definitions/89.html" }
        ],
        "detectionMethod": "Automated SQL Injection Testing"
    },
    {
        "id": "vuln2",
        "title": "Missing CSRF Protection",
        "description": "The application does not implement proper Cross-Site Request Forgery (CSRF) protections on state-changing operations.",
        "severity": "medium",
        "category": "CSRF",
        "location": "https://example.com/profile/update",
        "cvss": "6.1",
        "cwe": "352",
        "evidence": "<form method=\"POST\" action=\"/profile/update\">\n  <input type=\"text\" name=\"email\" />\n  <input type=\"submit\" />\n</form>",
        "evidenceType": "html",
        "impact": "An attacker could trick a user into making unwanted state changes to their account or data while they are authenticated. This could lead to account compromise or data manipulation.",
        "recommendation": "Implement proper CSRF token validation for all state-changing operations. Include a unique, secret token with each request and validate it on the server side.",
        "references": [
            { "title": "OWASP CSRF Prevention", "url": "https://owasp.org/www-community/attacks/csrf" },
            { "title": "CWE-352", "url": "https://cwe.mitre.org/data/definitions/352.html" }
        ],
        "detectionMethod": "Form Analysis"
    },
    {
        "id": "vuln3",
        "title": "Sensitive Data Exposure in Response Headers",
        "description": "The application exposes sensitive information in response headers that could aid attackers in fingerprinting the technology stack.",
        "severity": "low",
        "category": "Information Disclosure",
        "location": "Response Headers",
        "cvss": "3.7",
        "cwe": "200",
        "evidence": "X-Powered-By: PHP/7.4.3\nX-AspNet-Version: 4.8.0\nServer: Apache/2.4.41 (Ubuntu)",
        "evidenceType": "http",
        "impact": "Attackers can use the exposed information to identify the technology stack and target known vulnerabilities in those specific versions.",
        "recommendation": "Configure web servers to suppress or modify headers that reveal technology stack details. Remove unnecessary version information from headers.",
        "references": [
            { "title": "OWASP Secure Headers Project", "url": "https://owasp.org/www-project-secure-headers/" },
            { "title": "CWE-200", "url": "https://cwe.mitre.org/data/definitions/200.html" }
        ],
        "detectionMethod": "Header Analysis"
    }
]

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'mode': 'demo'
    })

# Scan endpoints
@app.route('/api/scan/start', methods=['POST'])
def start_scan():
    data = request.get_json()
    
    if not data or 'target_url' not in data:
        return jsonify({'error': 'Target URL is required'}), 400
    
    scan_id = str(uuid.uuid4())
    
    scan_config = {
        'id': scan_id,
        'target_url': data.get('target_url'),
        'scan_type': data.get('scan_type', 'comprehensive'),
        'modules': data.get('modules', ['discovery', 'authentication', 'injection', 'xss', 'csrf']),
        'start_time': datetime.utcnow().isoformat(),
        'status': 'running',
        'progress': 0,
        'findings': []
    }
    
    active_scans[scan_id] = scan_config
    scan_history.append({
        'id': scan_id,
        'target_url': data.get('target_url'),
        'scan_type': data.get('scan_type', 'comprehensive'),
        'start_time': scan_config['start_time'],
        'status': 'running'
    })
    
    # Start progress simulation
    return jsonify({
        'status': 'success',
        'message': 'Scan initiated successfully',
        'scan_id': scan_id,
        'config': scan_config
    }), 201

@app.route('/api/scan/status/<scan_id>', methods=['GET'])
def get_scan_status(scan_id):
    if scan_id not in active_scans:
        return jsonify({'error': 'Scan not found'}), 404
    
    scan_info = active_scans[scan_id]
    
    # Simulate progress
    if scan_info['status'] == 'running':
        elapsed = (datetime.utcnow() - datetime.fromisoformat(scan_info['start_time'])).total_seconds()
        progress = min(int(elapsed * 5), 100)
        
        if progress >= 100:
            scan_info['status'] = 'completed'
            scan_info['progress'] = 100
            scan_info['end_time'] = datetime.utcnow().isoformat()
            
            # Add random findings
            for finding in test_findings:
                # Deep copy finding and add it to the results
                scan_info['findings'].append(json.loads(json.dumps(finding)))
                
            # Update scan in history
            for scan in scan_history:
                if scan['id'] == scan_id:
                    scan['status'] = 'completed'
                    scan['end_time'] = scan_info['end_time']
                    break
        else:
            scan_info['progress'] = progress
    
    return jsonify({
        'scan_id': scan_id,
        'status': scan_info['status'],
        'progress': scan_info['progress'],
        'target_url': scan_info['target_url'],
        'start_time': scan_info['start_time'],
        'elapsed_time': get_elapsed_time(scan_info['start_time']),
        'findings_count': len(scan_info['findings'])
    })

@app.route('/api/scan/list', methods=['GET'])
def list_scans():
    return jsonify({
        'active_scans': list(active_scans.values()),
        'scan_history': scan_history
    })

@app.route('/api/scan/stop/<scan_id>', methods=['POST'])
def stop_scan(scan_id):
    if scan_id not in active_scans:
        return jsonify({'error': 'Scan not found'}), 404
    
    active_scans[scan_id]['status'] = 'stopped'
    
    # Update scan in history
    for scan in scan_history:
        if scan['id'] == scan_id:
            scan['status'] = 'stopped'
            break
    
    return jsonify({
        'status': 'success',
        'message': f'Scan {scan_id} has been stopped'
    })

@app.route('/api/scan/delete/<scan_id>', methods=['DELETE'])
def delete_scan(scan_id):
    if scan_id not in active_scans and not any(s['id'] == scan_id for s in scan_history):
        return jsonify({'error': 'Scan not found'}), 404
    
    if scan_id in active_scans:
        del active_scans[scan_id]
    
    # Remove from history
    updated_history = [s for s in scan_history if s['id'] != scan_id]
    scan_history.clear()
    scan_history.extend(updated_history)
    
    return jsonify({
        'status': 'success',
        'message': f'Scan {scan_id} deleted successfully'
    })

# Helper functions
def get_elapsed_time(start_time_iso):
    """Calculate elapsed time from ISO format start time to now"""
    start_time = datetime.fromisoformat(start_time_iso)
    elapsed = datetime.utcnow() - start_time
    return str(elapsed).split('.')[0]  # Remove microseconds

# Mock profiles
@app.route('/api/config/profiles', methods=['GET'])
def get_profiles():
    profiles = {
        'passive': {
            'name': 'Passive Scan',
            'description': 'Non-intrusive information gathering only',
            'modules': ['discovery', 'ssl_tls', 'headers', 'cookies'],
            'max_depth': 2,
            'max_pages': 100,
            'threads': 5,
            'request_delay': 1.0,
            'user_agent_rotation': True,
            'ip_rotation': False,
            'stealth_level': 'high'
        },
        'standard': {
            'name': 'Standard Scan',
            'description': 'Balanced security testing with moderate intrusiveness',
            'modules': ['discovery', 'authentication', 'injection', 'xss', 'csrf', 'ssl_tls', 
                      'headers', 'cookies', 'sensitive_data'],
            'max_depth': 3,
            'max_pages': 200,
            'threads': 10,
            'request_delay': 0.5,
            'user_agent_rotation': True,
            'ip_rotation': False,
            'stealth_level': 'medium'
        },
        'aggressive': {
            'name': 'Aggressive Scan',
            'description': 'Comprehensive security testing with high intrusiveness',
            'modules': ['discovery', 'authentication', 'injection', 'xss', 'csrf', 'ssl_tls', 
                      'headers', 'cookies', 'sensitive_data', 'brute_force', 'dos_simulation', 
                      'file_inclusion', 'command_injection', 'deserialization'],
            'max_depth': 5,
            'max_pages': 500,
            'threads': 20,
            'request_delay': 0.1,
            'user_agent_rotation': True,
            'ip_rotation': True,
            'stealth_level': 'low'
        },
        'stealth': {
            'name': 'Stealth Scan',
            'description': 'Maximum evasion techniques with balanced testing',
            'modules': ['discovery', 'authentication', 'injection', 'xss', 'csrf', 'ssl_tls', 
                      'headers', 'cookies', 'sensitive_data'],
            'max_depth': 3,
            'max_pages': 200,
            'threads': 3,
            'request_delay': 3.0,
            'user_agent_rotation': True,
            'ip_rotation': True,
            'stealth_level': 'maximum'
        }
    }
    
    return jsonify({
        'status': 'success',
        'profiles': profiles
    })

@app.route('/api/config/modules', methods=['GET'])
def get_modules():
    modules = {
        'discovery': {
            'name': 'Discovery & Enumeration',
            'description': 'Identifies application structure, endpoints, and technologies',
            'passive': True
        },
        'authentication': {
            'name': 'Authentication Testing',
            'description': 'Tests for authentication vulnerabilities like weak passwords',
            'passive': False
        },
        'injection': {
            'name': 'Injection Vulnerabilities',
            'description': 'Tests for SQL, NoSQL, and other injection attacks',
            'passive': False
        },
        'xss': {
            'name': 'Cross-Site Scripting (XSS)',
            'description': 'Tests for XSS vulnerabilities',
            'passive': False
        },
        'csrf': {
            'name': 'Cross-Site Request Forgery',
            'description': 'Tests for CSRF vulnerabilities',
            'passive': False
        },
        'ssl_tls': {
            'name': 'SSL/TLS Analysis',
            'description': 'Analyzes SSL/TLS configuration',
            'passive': True
        },
        'headers': {
            'name': 'HTTP Headers Analysis',
            'description': 'Tests for missing security headers',
            'passive': True
        },
        'cookies': {
            'name': 'Cookie Analysis',
            'description': 'Tests for insecure cookie configurations',
            'passive': True
        }
    }
    
    return jsonify({
        'status': 'success',
        'modules': modules
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8001)), debug=True)