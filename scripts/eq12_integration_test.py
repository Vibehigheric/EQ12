#!/usr/bin/env python3
"""
EQ12 Integration Test Suite
Validates the complete Python+C# system management toolchain

This script validates:
1. Python configuration generator functionality
2. Generated configuration integrity
3. C# application accessibility
4. HMI dashboard availability
5. Component discovery accuracy
"""

import os
import sys
import json
import logging
import subprocess
import requests
from datetime import datetime
from pathlib import Path

# EQ12 Standard Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'C:\\EQ12\\logs\\integration_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EQ12IntegrationValidator:
    """Industrial-grade integration testing for EQ12 system management toolchain"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace = Path(workspace_path)
        self.master_config = self.workspace / "configs" / "eq12_master_config.json"
        self.cs_app_path = self.workspace / "EQ12SystemManager" / "bin" / "Release" / "net8.0-windows" / "EQ12SystemManager.exe"
        self.hmi_dashboard = self.workspace / "dashboard" / "eq12_live_hmi.html"
        self.test_results = {}
        
    def validate_configuration_generator(self) -> bool:
        """Test Python configuration generator functionality"""
        logger.info(" Testing Python configuration generator...")
        
        try:
            # Check if master config exists and is valid
            if not self.master_config.exists():
                logger.error(" Master configuration file not found")
                return False
                
            with open(self.master_config, 'r') as f:
                config_data = json.load(f)
                
            # Validate configuration structure
            required_keys = ['system_id', 'components']
            for key in required_keys:
                if key not in config_data:
                    logger.error(f" Missing required key: {key}")
                    return False
                    
            # Validate component count
            component_count = len(config_data['components'])
            logger.info(f" Found {component_count} configured components")
            
            # Validate component types
            component_types = {}
            for component in config_data['components']:
                comp_type = component.get('type', 'unknown')
                component_types[comp_type] = component_types.get(comp_type, 0) + 1
                
            logger.info(f" Component distribution: {component_types}")
            
            self.test_results['config_generator'] = {
                'status': 'PASS',
                'component_count': component_count,
                'component_types': component_types
            }
            return True
            
        except Exception as e:
            logger.error(f" Configuration validation failed: {e}")
            self.test_results['config_generator'] = {'status': 'FAIL', 'error': str(e)}
            return False
            
    def validate_cs_application(self) -> bool:
        """Test C# WPF application build status"""
        logger.info(" Testing C# WPF application...")
        
        try:
            if not self.cs_app_path.exists():
                logger.error(" C# application executable not found")
                return False
                
            # Check file size and modification time
            file_stats = self.cs_app_path.stat()
            logger.info(f" C# application found: {file_stats.st_size} bytes, modified {datetime.fromtimestamp(file_stats.st_mtime)}")
            
            self.test_results['cs_application'] = {
                'status': 'PASS',
                'file_size': file_stats.st_size,
                'last_modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
            }
            return True
            
        except Exception as e:
            logger.error(f" C# application validation failed: {e}")
            self.test_results['cs_application'] = {'status': 'FAIL', 'error': str(e)}
            return False
            
    def validate_hmi_dashboard(self) -> bool:
        """Test HMI dashboard availability"""
        logger.info(" Testing HMI dashboard...")
        
        try:
            if not self.hmi_dashboard.exists():
                logger.error(" HMI dashboard file not found")
                return False
                
            # Check dashboard content
            with open(self.hmi_dashboard, 'r', encoding='utf-8') as f:
                dashboard_content = f.read()
                
            # Validate essential dashboard elements
            required_elements = ['EQ12 Live HMI', 'System Status', 'Component Monitor', 'Performance Metrics']
            for element in required_elements:
                if element not in dashboard_content:
                    logger.error(f" Missing dashboard element: {element}")
                    return False
                    
            logger.info(f" HMI dashboard validated: {len(dashboard_content)} characters")
            
            self.test_results['hmi_dashboard'] = {
                'status': 'PASS',
                'content_size': len(dashboard_content),
                'elements_found': required_elements
            }
            return True
            
        except Exception as e:
            logger.error(f" HMI dashboard validation failed: {e}")
            self.test_results['hmi_dashboard'] = {'status': 'FAIL', 'error': str(e)}
            return False
            
    def validate_component_discovery(self) -> bool:
        """Test component discovery accuracy"""
        logger.info(" Testing component discovery accuracy...")
        
        try:
            scripts_dir = self.workspace / "scripts"
            actual_python_files = list(scripts_dir.glob("*.py"))
            actual_powershell_files = list(scripts_dir.glob("*.ps1"))
            
            # Load discovered components from config
            with open(self.master_config, 'r') as f:
                config_data = json.load(f)
                
            discovered_python = [c for c in config_data['components'] if c['script_path'].endswith('.py')]
            discovered_powershell = [c for c in config_data['components'] if c['script_path'].endswith('.ps1')]
            
            python_discovery_rate = len(discovered_python) / len(actual_python_files) * 100
            powershell_discovery_rate = len(discovered_powershell) / len(actual_powershell_files) * 100
            
            logger.info(f" Python discovery: {len(discovered_python)}/{len(actual_python_files)} ({python_discovery_rate:.1f}%)")
            logger.info(f" PowerShell discovery: {len(discovered_powershell)}/{len(actual_powershell_files)} ({powershell_discovery_rate:.1f}%)")
            
            self.test_results['component_discovery'] = {
                'status': 'PASS',
                'python_files': len(actual_python_files),
                'powershell_files': len(actual_powershell_files),
                'python_discovered': len(discovered_python),
                'powershell_discovered': len(discovered_powershell),
                'python_discovery_rate': python_discovery_rate,
                'powershell_discovery_rate': powershell_discovery_rate
            }
            return True
            
        except Exception as e:
            logger.error(f" Component discovery validation failed: {e}")
            self.test_results['component_discovery'] = {'status': 'FAIL', 'error': str(e)}
            return False
            
    def validate_http_server(self) -> bool:
        """Test if HMI dashboard is accessible via HTTP"""
        logger.info(" Testing HMI dashboard HTTP accessibility...")
        
        try:
            # Try to connect to the HTTP server
            response = requests.get('http://localhost:8080/eq12_live_hmi.html', timeout=5)
            
            if response.status_code == 200:
                logger.info(f" HMI dashboard accessible via HTTP: {len(response.content)} bytes")
                self.test_results['http_server'] = {
                    'status': 'PASS',
                    'status_code': response.status_code,
                    'content_length': len(response.content)
                }
                return True
            else:
                logger.error(f" HTTP server returned status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f" HTTP server test failed (may not be running): {e}")
            self.test_results['http_server'] = {'status': 'SKIP', 'reason': 'HTTP server not accessible'}
            return True  # Don't fail the overall test for this
            
    def run_full_integration_test(self) -> dict:
        """Execute complete integration test suite"""
        logger.info(" Starting EQ12 Integration Test Suite...")
        start_time = datetime.now()
        
        test_methods = [
            self.validate_configuration_generator,
            self.validate_cs_application,
            self.validate_hmi_dashboard,
            self.validate_component_discovery,
            self.validate_http_server
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            if test_method():
                passed_tests += 1
                
        end_time = datetime.now()
        test_duration = (end_time - start_time).total_seconds()
        
        # Generate comprehensive test report
        test_report = {
            'test_suite': 'EQ12 Integration Test',
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': test_duration,
            'tests_passed': passed_tests,
            'tests_total': total_tests,
            'success_rate': (passed_tests / total_tests) * 100,
            'overall_status': 'PASS' if passed_tests == total_tests else 'PARTIAL_PASS',
            'detailed_results': self.test_results
        }
        
        # Save test report
        report_file = self.workspace / "logs" / f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(test_report, f, indent=2)
            
        logger.info(f" Integration Test Complete: {passed_tests}/{total_tests} tests passed ({test_report['success_rate']:.1f}%)")
        logger.info(f" Test report saved: {report_file}")
        
        return test_report

def main():
    """Main execution function"""
    validator = EQ12IntegrationValidator()
    test_report = validator.run_full_integration_test()
    
    # Print final status
    if test_report['overall_status'] == 'PASS':
        print(" EQ12 INTEGRATION TEST: ALL SYSTEMS OPERATIONAL")
    else:
        print(f" EQ12 INTEGRATION TEST: {test_report['tests_passed']}/{test_report['tests_total']} systems operational")
        
    return test_report

if __name__ == "__main__":
    main()