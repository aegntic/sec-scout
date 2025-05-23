#!/usr/bin/env python3
"""Test GODMODE scan on The Boat Warehouse website"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8001/api"
TARGET = "https://www.theboatwarehouse.com.au"

def login():
    """Login to get JWT token"""
    response = requests.post(f"{API_BASE}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    if response.status_code == 200:
        return response.json()['token']
    else:
        print(f"Login failed: {response.text}")
        return None

def start_godmode_scan(token):
    """Start a GODMODE scan"""
    headers = {"Authorization": f"Bearer {token}"}
    
    scan_config = {
        "target": TARGET,
        "scan_type": "godmode",
        "scan_profile": {
            "name": "GODMODE Elite",
            "description": "Complete security assessment with all vectors",
            "modules": [
                "threat_intelligence",
                "advanced_fuzzing", 
                "operational_parameters",
                "advanced_tls",
                "stealth_operations",
                "vulnerability_discovery",
                "multi_vector_attack",
                "behavioral_analysis",
                "zero_day_hunting"
            ],
            "settings": {
                "stealth_level": "ghost",
                "scan_depth": "maximum",
                "ai_enabled": True,
                "swarm_intelligence": True,
                "polymorphic_attacks": True,
                "evasion_techniques": True,
                "client_tier": "auto-detect"
            }
        }
    }
    
    print(f"\n🎯 Starting GODMODE scan on {TARGET}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📋 Scan Configuration:")
    print(json.dumps(scan_config, indent=2))
    
    response = requests.post(
        f"{API_BASE}/scans/start", 
        json=scan_config,
        headers=headers
    )
    
    if response.status_code == 200:
        scan_data = response.json()
        print(f"\n✅ Scan started successfully!")
        print(f"🔍 Scan ID: {scan_data['scan_id']}")
        return scan_data['scan_id']
    else:
        print(f"\n❌ Failed to start scan: {response.text}")
        return None

def monitor_scan(token, scan_id):
    """Monitor scan progress"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📊 Monitoring scan progress...")
    
    while True:
        response = requests.get(
            f"{API_BASE}/scans/{scan_id}/status",
            headers=headers
        )
        
        if response.status_code == 200:
            status = response.json()
            progress = status.get('progress', 0)
            state = status.get('status', 'unknown')
            current_module = status.get('current_module', '')
            
            print(f"\r⚡ Status: {state} | Progress: {progress}% | Module: {current_module}", end='', flush=True)
            
            if state in ['completed', 'failed', 'error']:
                print("\n")
                return state
                
        time.sleep(2)

def get_scan_results(token, scan_id):
    """Get scan results"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{API_BASE}/scans/{scan_id}/results",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get results: {response.text}")
        return None

def generate_report(token, scan_id):
    """Generate professional report"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📄 Generating professional report...")
    
    response = requests.post(
        f"{API_BASE}/reports/generate",
        json={
            "scan_id": scan_id,
            "format": "html",
            "include_executive_summary": True,
            "include_technical_details": True,
            "include_remediation": True,
            "client_name": "The Boat Warehouse",
            "report_type": "professional"
        },
        headers=headers
    )
    
    if response.status_code == 200:
        report_data = response.json()
        report_path = report_data.get('report_path', '')
        print(f"✅ Report generated: {report_path}")
        return report_path
    else:
        print(f"❌ Failed to generate report: {response.text}")
        return None

def main():
    print("🚀 SecureScout GODMODE Test - The Boat Warehouse")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        return
    
    print("✅ Authentication successful")
    
    # Start scan
    scan_id = start_godmode_scan(token)
    if not scan_id:
        return
    
    # Monitor progress
    final_status = monitor_scan(token, scan_id)
    
    if final_status == 'completed':
        print("✅ Scan completed successfully!")
        
        # Get results
        results = get_scan_results(token, scan_id)
        if results:
            vulnerabilities = results.get('vulnerabilities', [])
            print(f"\n🔍 Found {len(vulnerabilities)} vulnerabilities")
            
            # Summary by severity
            severity_counts = {}
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'Unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            print("\n📊 Vulnerability Summary:")
            for severity, count in sorted(severity_counts.items()):
                print(f"  - {severity}: {count}")
            
            # Generate report
            report_path = generate_report(token, scan_id)
            
            print("\n🎯 GODMODE Modules Executed:")
            modules_run = results.get('modules_executed', [])
            for module in modules_run:
                print(f"  ✓ {module}")
                
            print(f"\n💡 Client Tier Detected: {results.get('client_tier', 'Unknown')}")
            print(f"🛡️ Security Score: {results.get('security_score', 'N/A')}/100")
            
    else:
        print(f"❌ Scan failed with status: {final_status}")
    
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    main()