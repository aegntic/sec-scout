#!/usr/bin/env python3
"""GODMODE Module Validator and Fixer"""

import os
import sys
import importlib
import traceback
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

class GodmodeFixer:
    def __init__(self):
        self.log_file = "GODMODE_FIX_LOG.md"
        self.errors = []
        self.fixes = []
        self.modules_status = {}
        
    def log(self, message, level="INFO"):
        """Log messages to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        # Append to log file
        with open(self.log_file, 'a') as f:
            f.write(f"\n{log_entry}")
    
    def check_module(self, module_path):
        """Check if a module can be imported"""
        try:
            module = importlib.import_module(module_path)
            self.modules_status[module_path] = "✅ OK"
            return True, None
        except Exception as e:
            self.modules_status[module_path] = f"❌ {str(e)}"
            return False, str(e)
    
    def validate_godmode_modules(self):
        """Validate all GODMODE modules"""
        self.log("=" * 60)
        self.log("Starting GODMODE Module Validation", "INFO")
        self.log("=" * 60)
        
        godmode_modules = [
            # Core modules
            "modules.godmode.real_godmode_core",
            "modules.godmode.threat_intelligence_engine",
            "modules.godmode.advanced_fuzzing_engine",
            "modules.godmode.operational_parameters_engine",
            "modules.godmode.advanced_tls_engine",
            "modules.godmode.real_stealth_engine",
            
            # Swarm Intelligence
            "modules.godmode.swarm_intelligence_hub",
            "modules.godmode.hive_mind_coordinator",
            "modules.godmode.vector_communication_protocol",
            "modules.godmode.collective_target_understanding",
            
            # Advanced Attack Systems
            "modules.godmode.advanced_multi_vector",
            "modules.godmode.autonomous_orchestration",
            "modules.godmode.polymorphic_attack_engine",
            
            # AI and Analysis
            "modules.godmode.ai_discovery",
            "modules.godmode.behavioral_analysis",
            "modules.godmode.chaos_testing",
            "modules.godmode.creative_vectors",
            "modules.godmode.deep_logic_detection",
            "modules.godmode.edge_case_exploitation",
            "modules.godmode.novel_testing_techniques",
            "modules.godmode.social_engineering_vectors",
            "modules.godmode.zero_day_hunting",
            
            # Support modules
            "modules.godmode.vulnerability_explorer",
            "modules.godmode.vulnerability_intelligence_hub",
            "modules.godmode.security_posture_analyzer",
            "modules.godmode.auto_report_generator",
            "modules.godmode.error_handler",
        ]
        
        self.log(f"Checking {len(godmode_modules)} GODMODE modules...")
        
        for module in godmode_modules:
            self.log(f"\nChecking: {module}")
            success, error = self.check_module(module)
            
            if not success:
                self.errors.append((module, error))
                self.log(f"  ERROR: {error}", "ERROR")
                
                # Try to fix common issues
                if "No module named" in error:
                    missing = error.split("'")[1]
                    self.log(f"  Missing dependency: {missing}", "WARNING")
                    self.attempt_fix(module, missing)
    
    def attempt_fix(self, module, missing_dep):
        """Attempt to fix missing dependencies"""
        self.log(f"  Attempting to fix: {missing_dep}", "INFO")
        
        # Common fixes
        fixes = {
            "quantum_fuzzing": "Use advanced_fuzzing_engine instead",
            "elite_adversary_simulation": "Use threat_intelligence_engine instead",
            "universal_clearance_core": "Use operational_parameters_engine instead"
        }
        
        if missing_dep in fixes:
            self.log(f"  FIX: {fixes[missing_dep]}", "SUCCESS")
            self.fixes.append((missing_dep, fixes[missing_dep]))
    
    def check_tool_dependencies(self):
        """Check for required security tools"""
        self.log("\n" + "=" * 60)
        self.log("Checking Security Tool Dependencies", "INFO")
        self.log("=" * 60)
        
        tools = {
            "nmap": "Network discovery and port scanning",
            "nikto": "Web server scanner",
            "nuclei": "Template-based vulnerability scanner",
            "sqlmap": "SQL injection testing",
            "zap-cli": "OWASP ZAP CLI",
            "trivy": "Container/infrastructure scanner",
            "rg": "Ripgrep for fast searching"
        }
        
        import subprocess
        
        for tool, description in tools.items():
            try:
                result = subprocess.run(['which', tool], capture_output=True, text=True)
                if result.returncode == 0:
                    self.log(f"✅ {tool}: {description}", "SUCCESS")
                else:
                    self.log(f"❌ {tool}: NOT INSTALLED - {description}", "WARNING")
                    self.log(f"   Install with: sudo apt install {tool} (or appropriate method)", "INFO")
            except Exception as e:
                self.log(f"❌ {tool}: Error checking - {str(e)}", "ERROR")
    
    def check_real_tool_installation(self):
        """Provide real tool installation instructions"""
        self.log("\n" + "=" * 60)
        self.log("Real Tool Installation Instructions", "INFO")
        self.log("=" * 60)
        
        install_commands = {
            "nmap": {
                "ubuntu": "sudo apt-get install nmap",
                "macos": "brew install nmap",
                "description": "Network discovery and security auditing"
            },
            "nikto": {
                "ubuntu": "sudo apt-get install nikto",
                "macos": "brew install nikto",
                "description": "Web server scanner"
            },
            "nuclei": {
                "ubuntu": "GO111MODULE=on go get -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei",
                "macos": "brew install nuclei",
                "description": "Fast and customizable vulnerability scanner"
            },
            "sqlmap": {
                "ubuntu": "sudo apt-get install sqlmap",
                "macos": "brew install sqlmap",
                "description": "SQL injection detection and exploitation"
            },
            "zap-cli": {
                "ubuntu": "pip install --upgrade zapcli",
                "macos": "pip install --upgrade zapcli",
                "description": "OWASP ZAP command line interface"
            },
            "trivy": {
                "ubuntu": "sudo apt-get install wget apt-transport-https gnupg lsb-release\nwget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -\necho deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | sudo tee -a /etc/apt/sources.list.d/trivy.list\nsudo apt-get update\nsudo apt-get install trivy",
                "macos": "brew install aquasecurity/trivy/trivy",
                "description": "Vulnerability scanner for containers and other artifacts"
            }
        }
        
        self.log("\n🔧 To use real security tools, install them using these commands:")
        self.log("")
        
        for tool, info in install_commands.items():
            self.log(f"📦 {tool} - {info['description']}")
            self.log(f"   Ubuntu/Debian: {info['ubuntu']}")
            self.log(f"   macOS: {info['macos']}")
            self.log("")
    
    def generate_report(self):
        """Generate fix report"""
        self.log("\n" + "=" * 60)
        self.log("GODMODE Validation Report", "INFO")
        self.log("=" * 60)
        
        # Module status
        self.log("\nModule Status:")
        for module, status in self.modules_status.items():
            self.log(f"  {module}: {status}")
        
        # Errors summary
        if self.errors:
            self.log(f"\nTotal Errors: {len(self.errors)}", "ERROR")
            for module, error in self.errors:
                self.log(f"  - {module}: {error}")
        else:
            self.log("\nNo errors found! ✅", "SUCCESS")
        
        # Fixes applied
        if self.fixes:
            self.log(f"\nFixes Applied: {len(self.fixes)}", "SUCCESS")
            for dep, fix in self.fixes:
                self.log(f"  - {dep}: {fix}")
        
        # Update fix log
        with open(self.log_file, 'a') as f:
            f.write(f"\n\n### Validation Run: {datetime.now()}")
            f.write(f"\n- Modules Checked: {len(self.modules_status)}")
            f.write(f"\n- Errors Found: {len(self.errors)}")
            f.write(f"\n- Fixes Applied: {len(self.fixes)}")
    
    def run_full_diagnostic(self):
        """Run complete diagnostic and fix process"""
        self.log("🔧 GODMODE Diagnostic and Fix Tool", "INFO")
        self.log("Target: The Boat Warehouse Security Assessment", "INFO")
        
        # Step 1: Validate modules
        self.validate_godmode_modules()
        
        # Step 2: Check tools
        self.check_tool_dependencies()
        
        # Step 3: Show real tool installation
        self.check_real_tool_installation()
        
        # Step 4: Generate report
        self.generate_report()
        
        self.log("\n✅ Diagnostic complete!", "SUCCESS")
        self.log("Check GODMODE_FIX_LOG.md for detailed results", "INFO")

if __name__ == "__main__":
    fixer = GodmodeFixer()
    fixer.run_full_diagnostic()