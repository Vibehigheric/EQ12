#!/usr/bin/env python3
"""
EQ12 Pi USB Network Integration Script
Specialized script for discovering and integrating Pi over USB-to-Ethernet
"""

import subprocess
import json
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PiUSBIntegrator:
    def __init__(self):
        self.pi_ip = "192.168.100.2"
        self.host_ip = "192.168.100.1"
        self.pi_username = "pi"  # Default Pi username
        self.log_dir = Path("C:/EQ12/logs")
        self.config_dir = Path("C:/EQ12/configs")
        
        # Ensure directories exist
        self.log_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        
        self.log_file = self.log_dir / f"pi_usb_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
    def log_event(self, level, message, data=None):
        """Log events to both console and JSON file"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data or {},
            "script": "eq12_pi_usb_integrator.py"
        }
        
        # Map custom levels to standard logging levels
        log_level_map = {
            "SUCCESS": logging.INFO,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR
        }
        
        logger.log(log_level_map.get(level.upper(), logging.INFO), message)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f)
                f.write('\n')
        except Exception as e:
            logger.error(f"Failed to write log: {e}")
    
    def test_pi_connectivity(self):
        """Test if Pi is responding on the USB network"""
        self.log_event("INFO", f"Testing Pi connectivity at {self.pi_ip}")
        
        try:
            # Use ping to test basic connectivity
            result = subprocess.run(
                ["ping", "-n", "1", self.pi_ip],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                self.log_event("SUCCESS", "Pi responds to ping", {
                    "pi_ip": self.pi_ip,
                    "response_time": "detected"
                })
                return True
            else:
                self.log_event("WARNING", "Pi does not respond to ping", {
                    "pi_ip": self.pi_ip,
                    "return_code": result.returncode
                })
                return False
                
        except subprocess.TimeoutExpired:
            self.log_event("ERROR", "Ping timeout", {"pi_ip": self.pi_ip})
            return False
        except Exception as e:
            self.log_event("ERROR", "Ping test failed", {"error": str(e)})
            return False
    
    def test_ssh_connectivity(self):
        """Test SSH connectivity to Pi"""
        self.log_event("INFO", f"Testing SSH connectivity to {self.pi_ip}")
        
        try:
            # Test SSH port availability
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((self.pi_ip, 22))
            sock.close()
            
            if result == 0:
                self.log_event("SUCCESS", "SSH port accessible", {
                    "pi_ip": self.pi_ip,
                    "port": 22
                })
                return True
            else:
                self.log_event("WARNING", "SSH port not accessible", {
                    "pi_ip": self.pi_ip,
                    "port": 22,
                    "error_code": result
                })
                return False
                
        except Exception as e:
            self.log_event("ERROR", "SSH test failed", {"error": str(e)})
            return False
    
    def discover_pi_services(self):
        """Discover what services are running on the Pi"""
        if not self.test_pi_connectivity():
            return {}
            
        services = {}
        common_ports = [22, 80, 443, 5000, 8080, 9000]  # SSH, HTTP, HTTPS, common app ports
        
        self.log_event("INFO", "Discovering Pi services")
        
        for port in common_ports:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.pi_ip, port))
                sock.close()
                
                if result == 0:
                    service_name = {
                        22: "SSH",
                        80: "HTTP",
                        443: "HTTPS", 
                        5000: "Flask/App",
                        8080: "Alt HTTP",
                        9000: "App Server"
                    }.get(port, f"Service-{port}")
                    
                    services[port] = service_name
                    self.log_event("INFO", f"Service discovered", {
                        "port": port,
                        "service": service_name
                    })
                    
            except Exception:
                continue
                
        return services
    
    def add_to_cluster(self):
        """Add Pi to the EQ12 cluster"""
        self.log_event("INFO", "Adding Pi to EQ12 cluster")
        
        try:
            # Run the cluster manager to add the node
            cmd = [
                "python", 
                "eq12_raspberry_pi_cluster_manager.py",
                "--action", "add-node",
                "--ip", self.pi_ip,
                "--username", self.pi_username,
                "--verbose"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log_event("SUCCESS", "Pi added to cluster successfully", {
                    "pi_ip": self.pi_ip,
                    "output": result.stdout
                })
                return True
            else:
                self.log_event("ERROR", "Failed to add Pi to cluster", {
                    "return_code": result.returncode,
                    "stderr": result.stderr,
                    "stdout": result.stdout
                })
                return False
                
        except subprocess.TimeoutExpired:
            self.log_event("ERROR", "Cluster add timeout")
            return False
        except Exception as e:
            self.log_event("ERROR", "Cluster add failed", {"error": str(e)})
            return False
    
    def deploy_cross_listing_services(self):
        """Deploy cross-listing services to the Pi"""
        self.log_event("INFO", "Deploying cross-listing services to Pi")
        
        # This would copy our cross-listing scripts to the Pi
        # For now, we'll just log the intent and create deployment plan
        
        deployment_plan = {
            "services": [
                "eq12_crosslisting_manager.py",
                "eq12_selenium_crosslister.py"
            ],
            "dependencies": [
                "selenium",
                "requests", 
                "beautifulsoup4",
                "pandas"
            ],
            "config_files": [
                "crosslisting_config.json",
                "product_catalog.json"
            ]
        }
        
        self.log_event("INFO", "Cross-listing deployment plan created", deployment_plan)
        
        # Save deployment plan for future execution
        plan_file = self.config_dir / "pi_deployment_plan.json"
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(deployment_plan, f, indent=2)
            
        self.log_event("SUCCESS", "Deployment plan saved", {"file": str(plan_file)})
        return deployment_plan
    
    def run_integration_test(self):
        """Run complete integration test"""
        self.log_event("INFO", "Starting Pi USB integration test")
        
        results = {
            "connectivity": self.test_pi_connectivity(),
            "ssh": self.test_ssh_connectivity(),
            "services": self.discover_pi_services(),
            "cluster_added": False,
            "deployment_ready": False
        }
        
        if results["connectivity"] and results["ssh"]:
            results["cluster_added"] = self.add_to_cluster()
            results["deployment_ready"] = bool(self.deploy_cross_listing_services())
        
        # Generate summary
        success_count = sum([
            results["connectivity"],
            results["ssh"], 
            results["cluster_added"],
            results["deployment_ready"]
        ])
        
        self.log_event("SUCCESS", f"Integration test completed: {success_count}/4 steps successful", results)
        
        return results
    
    def generate_status_report(self):
        """Generate comprehensive status report"""
        self.log_event("INFO", "Generating status report")
        
        # Test current status
        connectivity = self.test_pi_connectivity()
        ssh = self.test_ssh_connectivity()
        services = self.discover_pi_services()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "host_ip": self.host_ip,
            "pi_ip": self.pi_ip,
            "connectivity": {
                "ping": connectivity,
                "ssh": ssh,
                "services": services
            },
            "next_steps": []
        }
        
        if not connectivity:
            report["next_steps"].append("Configure Pi network: sudo nano /etc/dhcpcd.conf")
            report["next_steps"].append("Add: interface eth0")
            report["next_steps"].append("Add: static ip_address=192.168.100.2/24")
            report["next_steps"].append("Add: static routers=192.168.100.1")
            report["next_steps"].append("Reboot Pi: sudo reboot")
        elif not ssh:
            report["next_steps"].append("Enable SSH on Pi: sudo systemctl enable ssh")
            report["next_steps"].append("Start SSH: sudo systemctl start ssh")
        else:
            report["next_steps"].append("Run integration: python eq12_pi_usb_integrator.py --integrate")
            report["next_steps"].append("Deploy services: python eq12_pi_usb_integrator.py --deploy")
        
        # Save report
        report_file = self.log_dir / f"pi_status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        self.log_event("SUCCESS", "Status report generated", {"file": str(report_file)})
        return report

def main():
    parser = argparse.ArgumentParser(description="EQ12 Pi USB Network Integration")
    parser.add_argument("--test", action="store_true", help="Test Pi connectivity")
    parser.add_argument("--integrate", action="store_true", help="Run full integration")
    parser.add_argument("--deploy", action="store_true", help="Deploy cross-listing services")
    parser.add_argument("--status", action="store_true", help="Generate status report")
    parser.add_argument("--pi-ip", default="192.168.100.2", help="Pi IP address")
    
    args = parser.parse_args()
    
    integrator = PiUSBIntegrator()
    integrator.pi_ip = args.pi_ip
    
    if args.test:
        connectivity = integrator.test_pi_connectivity()
        ssh = integrator.test_ssh_connectivity()
        services = integrator.discover_pi_services()
        
        print(f"\n Pi Connectivity Test Results:")
        print(f"   Ping: {'' if connectivity else ''}")
        print(f"   SSH:  {'' if ssh else ''}")
        print(f"   Services: {len(services)} discovered")
        
    elif args.integrate:
        results = integrator.run_integration_test()
        
        print(f"\n Integration Test Results:")
        print(f"   Connectivity: {'' if results['connectivity'] else ''}")
        print(f"   SSH Access:   {'' if results['ssh'] else ''}")
        print(f"   Cluster Add:  {'' if results['cluster_added'] else ''}")
        print(f"   Deploy Ready: {'' if results['deployment_ready'] else ''}")
        
    elif args.deploy:
        plan = integrator.deploy_cross_listing_services()
        print(f"\n Deployment Plan Created:")
        print(f"   Services: {len(plan['services'])}")
        print(f"   Dependencies: {len(plan['dependencies'])}")
        
    elif args.status:
        report = integrator.generate_status_report()
        
        print(f"\n Pi Status Report:")
        print(f"   Host IP: {report['host_ip']}")
        print(f"   Pi IP: {report['pi_ip']}")
        print(f"   Ping: {'' if report['connectivity']['ping'] else ''}")
        print(f"   SSH: {'' if report['connectivity']['ssh'] else ''}")
        print(f"   Services: {len(report['connectivity']['services'])}")
        
        if report['next_steps']:
            print(f"\n Next Steps:")
            for step in report['next_steps']:
                print(f"    {step}")
    else:
        # Default: run status check
        report = integrator.generate_status_report()
        print(f"\n Quick Status Check:")
        print(f"   Pi Connectivity: {'' if report['connectivity']['ping'] else ''}")
        print(f"   SSH Available: {'' if report['connectivity']['ssh'] else ''}")
        
        if not report['connectivity']['ping']:
            print(f"\n  Pi needs network configuration!")
            print(f"   See: C:\\EQ12\\PI_ETHERNET_SETUP_INSTRUCTIONS.md")
        elif not report['connectivity']['ssh']:
            print(f"\n  SSH needs to be enabled on Pi")
        else:
            print(f"\n Ready for integration!")
            print(f"   Run: python eq12_pi_usb_integrator.py --integrate")

if __name__ == "__main__":
    main()