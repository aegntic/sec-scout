#!/usr/bin/env python3
"""Direct GODMODE test bypassing authentication"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.modules.godmode.real_godmode_core import RealGodmodeCore
from backend.modules.reporting.report_generator import ReportGenerator
import json
from datetime import datetime

TARGET = "https://www.theboatwarehouse.com.au"

def run_godmode_scan():
    """Run GODMODE scan directly"""
    print("🚀 SecureScout GODMODE Test - The Boat Warehouse")
    print("=" * 60)
    print(f"🎯 Target: {TARGET}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🔧 Initializing GODMODE engine...")
    
    # Initialize GODMODE
    godmode = RealGodmodeCore()
    
    # Configure scan
    scan_config = {
        "target": TARGET,
        "stealth_level": "ghost",
        "scan_depth": "maximum",
        "ai_enabled": True,
        "modules": [
            "threat_intelligence",
            "advanced_fuzzing",
            "operational_parameters",
            "advanced_tls",
            "stealth_operations",
            "vulnerability_discovery",
            "multi_vector_attack",
            "behavioral_analysis"
        ]
    }
    
    print("\n📋 Scan Configuration:")
    print(f"  • Stealth Level: Ghost Tier")
    print(f"  • AI Enhanced: Enabled")
    print(f"  • Modules: {len(scan_config['modules'])}")
    for module in scan_config['modules']:
        print(f"    ✓ {module}")
    
    print("\n🔍 Starting elite security assessment...")
    print("-" * 60)
    
    try:
        # Run the scan
        results = godmode.elite_security_assessment(
            target=TARGET,
            config=scan_config
        )
        
        print("\n✅ Scan completed successfully!")
        
        # Process results
        if results:
            print("\n📊 Results Summary:")
            print(f"  • Client Tier: {results.get('client_tier', 'Unknown')}")
            print(f"  • Security Score: {results.get('security_score', 'N/A')}/100")
            
            # Vulnerabilities
            vulnerabilities = results.get('vulnerabilities', [])
            print(f"\n🔍 Vulnerabilities Found: {len(vulnerabilities)}")
            
            # Count by severity
            severity_counts = {}
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'Unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            for severity in ['Critical', 'High', 'Medium', 'Low', 'Info']:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    print(f"  • {severity}: {count}")
            
            # Show some example vulnerabilities
            if vulnerabilities:
                print("\n🎯 Top Findings:")
                for i, vuln in enumerate(vulnerabilities[:5], 1):
                    print(f"\n  {i}. {vuln.get('title', 'Unknown')}")
                    print(f"     Severity: {vuln.get('severity', 'Unknown')}")
                    print(f"     Module: {vuln.get('module', 'Unknown')}")
                    if vuln.get('description'):
                        print(f"     Description: {vuln['description'][:100]}...")
            
            # Generate report
            print("\n📄 Generating professional report...")
            
            report_gen = ReportGenerator()
            report_data = {
                "scan_id": f"godmode_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "target": TARGET,
                "client_name": "The Boat Warehouse",
                "scan_type": "GODMODE Elite",
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "results": results
            }
            
            report_path = report_gen.generate_html_report(
                scan_data=report_data,
                output_dir="/home/qubit/Downloads/secure-scout/SecureScout/reports"
            )
            
            print(f"✅ Report generated: {report_path}")
            
            # Save raw results
            results_path = f"/home/qubit/Downloads/secure-scout/SecureScout/boat_warehouse_results.json"
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"💾 Raw results saved: {results_path}")
            
        else:
            print("❌ No results returned from scan")
            
    except Exception as e:
        print(f"\n❌ Error during scan: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    run_godmode_scan()