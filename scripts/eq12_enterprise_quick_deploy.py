#!/usr/bin/env python3
"""
EQ12 Enterprise Quick Deploy Script
One-command deployment of the complete enterprise stack

Usage:
    python eq12_enterprise_quick_deploy.py --action setup
    python eq12_enterprise_quick_deploy.py --action deploy
    python eq12_enterprise_quick_deploy.py --action status
    python eq12_enterprise_quick_deploy.py --action stop
"""

import os
import sys
import json
import time
import argparse
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'C:\\EQ12\\logs\\enterprise_deploy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EQ12EnterpriseDeployer:
    """One-click deployment for EQ12 Enterprise Stack"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace = Path(workspace_path)
        self.enterprise_dir = self.workspace / "enterprise"
        self.compose_dir = self.enterprise_dir / "infra" / "compose"
        self.docker_compose_file = self.compose_dir / "docker-compose.yml"
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed"""
        logger.info(" Checking prerequisites...")
        
        prerequisites = {
            "docker": "docker --version",
            "docker-compose": "docker compose version",
            "python": "python --version",
            "dotnet": "dotnet --version"
        }
        
        missing = []
        for name, command in prerequisites.items():
            try:
                result = subprocess.run(command.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f" {name}: {result.stdout.strip()}")
                else:
                    missing.append(name)
                    logger.error(f" {name}: Not working properly")
            except FileNotFoundError:
                missing.append(name)
                logger.error(f" {name}: Not found")
        
        if missing:
            logger.error(f"Missing prerequisites: {', '.join(missing)}")
            return False
            
        return True
    
    def setup_enterprise_structure(self) -> bool:
        """Create enterprise directory structure and files"""
        logger.info(" Setting up enterprise directory structure...")
        
        try:
            # Create directories
            directories = [
                self.enterprise_dir / "apps" / "eq12_parlay_engine",
                self.enterprise_dir / "apps" / "eq12_model_server",
                self.enterprise_dir / "infra" / "compose",
                self.enterprise_dir / "infra" / "prometheus",
                self.enterprise_dir / "infra" / "grafana" / "provisioning" / "dashboards",
                self.enterprise_dir / "data_models"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f" Created: {directory}")
            
            # Check if essential files exist
            essential_files = [
                self.docker_compose_file,
                self.compose_dir / ".env.example",
                self.enterprise_dir / "apps" / "eq12_parlay_engine" / "Dockerfile"
            ]
            
            missing_files = [f for f in essential_files if not f.exists()]
            if missing_files:
                logger.warning(f" Missing files: {[str(f) for f in missing_files]}")
                logger.info(" Please ensure all enterprise files are copied to the correct directories")
                return False
            
            logger.info(" Enterprise structure setup complete")
            return True
            
        except Exception as e:
            logger.error(f" Setup failed: {e}")
            return False
    
    def validate_eq12_foundation(self) -> bool:
        """Validate existing EQ12 system is ready"""
        logger.info(" Validating EQ12 foundation...")
        
        try:
            # Check master config
            master_config = self.workspace / "configs" / "eq12_master_config.json"
            if master_config.exists():
                with open(master_config, 'r') as f:
                    config = json.load(f)
                component_count = len(config.get('components', []))
                logger.info(f" EQ12 Master Config: {component_count} components discovered")
            else:
                logger.warning(" EQ12 master config not found, running generator...")
                self.run_eq12_config_generator()
            
            # Check C# control interface
            cs_app = self.workspace / "EQ12SystemManager" / "bin" / "Release" / "net8.0-windows" / "EQ12SystemManager.exe"
            if cs_app.exists():
                logger.info(f" C# Control Interface: {cs_app}")
            else:
                logger.error(" C# Control Interface not built")
                return False
            
            # Check HMI dashboard
            hmi_dashboard = self.workspace / "dashboard" / "eq12_live_hmi.html"
            if hmi_dashboard.exists():
                logger.info(f" HMI Dashboard: {hmi_dashboard}")
            else:
                logger.warning(" HMI dashboard not found")
            
            logger.info(" EQ12 foundation validation complete")
            return True
            
        except Exception as e:
            logger.error(f" EQ12 foundation validation failed: {e}")
            return False
    
    def run_eq12_config_generator(self) -> bool:
        """Run EQ12 configuration generator"""
        logger.info(" Running EQ12 configuration generator...")
        
        try:
            config_generator = self.workspace / "scripts" / "eq12_system_config_generator.py"
            if not config_generator.exists():
                logger.error(f" Config generator not found: {config_generator}")
                return False
            
            cmd = [
                "python", str(config_generator),
                "--workspace", str(self.workspace),
                "--generate-dashboard", 
                "--verbose"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.workspace))
            
            if result.returncode == 0:
                logger.info(" EQ12 configuration generator completed")
                return True
            else:
                logger.error(f" Config generator failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f" Config generator execution failed: {e}")
            return False
    
    def setup_environment(self) -> bool:
        """Set up Docker environment configuration"""
        logger.info(" Setting up environment configuration...")
        
        try:
            env_example = self.compose_dir / ".env.example"
            env_file = self.compose_dir / ".env"
            
            if not env_file.exists() and env_example.exists():
                # Copy example to .env with basic values
                with open(env_example, 'r') as f:
                    env_content = f.read()
                
                # Replace placeholder values with basic defaults
                env_content = env_content.replace("your_secure_password_here", "eq12_default_password_2025")
                env_content = env_content.replace("your_minio_secret_here", "eq12_minio_secret_key_2025")
                env_content = env_content.replace("your_grafana_password_here", "eq12_grafana_admin_2025")
                
                with open(env_file, 'w') as f:
                    f.write(env_content)
                
                logger.info(f" Environment file created: {env_file}")
                logger.warning(" Please review and update passwords in .env file for production")
            else:
                logger.info(" Environment file already exists")
            
            return True
            
        except Exception as e:
            logger.error(f" Environment setup failed: {e}")
            return False
    
    def deploy_infrastructure(self) -> bool:
        """Deploy Docker infrastructure services"""
        logger.info(" Deploying infrastructure services...")
        
        try:
            os.chdir(self.compose_dir)
            
            # Pull images first
            logger.info(" Pulling Docker images...")
            subprocess.run(["docker", "compose", "pull"], check=True)
            
            # Start infrastructure services
            logger.info(" Starting infrastructure services...")
            infrastructure_services = [
                "traefik", "minio", "postgres", "redis", 
                "prometheus", "grafana", "loki"
            ]
            
            cmd = ["docker", "compose", "up", "-d"] + infrastructure_services
            subprocess.run(cmd, check=True)
            
            # Wait for services to be ready
            logger.info(" Waiting for services to be ready...")
            time.sleep(30)
            
            # Check service health
            result = subprocess.run(["docker", "compose", "ps"], capture_output=True, text=True)
            logger.info(f"Infrastructure status:\n{result.stdout}")
            
            logger.info(" Infrastructure deployment complete")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f" Infrastructure deployment failed: {e}")
            return False
        except Exception as e:
            logger.error(f" Unexpected error: {e}")
            return False
    
    def deploy_eq12_services(self) -> bool:
        """Deploy EQ12 microservices"""
        logger.info(" Deploying EQ12 microservices...")
        
        try:
            os.chdir(self.compose_dir)
            
            # Build and start EQ12 services
            eq12_services = [
                "eq12-parlay-engine",
                "eq12-model-server", 
                "eq12-config-sync",
                "eq12-system-bridge"
            ]
            
            cmd = ["docker", "compose", "up", "-d", "--build"] + eq12_services
            subprocess.run(cmd, check=True)
            
            # Wait for services to be ready
            logger.info(" Waiting for EQ12 services to be ready...")
            time.sleep(20)
            
            # Test API endpoints
            logger.info(" Testing API endpoints...")
            self.test_api_endpoints()
            
            logger.info(" EQ12 services deployment complete")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f" EQ12 services deployment failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test deployed API endpoints"""
        endpoints = [
            ("http://localhost/api/parlay/health", "Parlay Engine Health"),
            ("http://localhost/api/models", "Model Server"),
            ("http://localhost:9090/-/healthy", "Prometheus"),
            ("http://localhost:3000/api/health", "Grafana")
        ]
        
        for url, name in endpoints:
            try:
                import requests
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f" {name}: OK")
                else:
                    logger.warning(f" {name}: HTTP {response.status_code}")
            except Exception as e:
                logger.warning(f" {name}: {e}")
    
    def get_deployment_status(self) -> dict:
        """Get current deployment status"""
        logger.info(" Checking deployment status...")
        
        try:
            os.chdir(self.compose_dir)
            result = subprocess.run(["docker", "compose", "ps", "--format", "json"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse JSON output
                services = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            service = json.loads(line)
                            services.append({
                                'name': service.get('Service'),
                                'state': service.get('State'),
                                'status': service.get('Status')
                            })
                        except json.JSONDecodeError:
                            continue
                
                return {
                    'status': 'running',
                    'services': services,
                    'total_services': len(services),
                    'healthy_services': len([s for s in services if s['state'] == 'running'])
                }
            else:
                return {'status': 'error', 'message': result.stderr}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def stop_deployment(self) -> bool:
        """Stop enterprise deployment"""
        logger.info(" Stopping enterprise deployment...")
        
        try:
            os.chdir(self.compose_dir)
            subprocess.run(["docker", "compose", "down"], check=True)
            logger.info(" Enterprise deployment stopped")
            return True
        except Exception as e:
            logger.error(f" Stop failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="EQ12 Enterprise Quick Deploy")
    parser.add_argument("--action", choices=["setup", "deploy", "status", "stop"], 
                       required=True, help="Deployment action")
    parser.add_argument("--workspace", default="C:\\EQ12", 
                       help="EQ12 workspace path")
    
    args = parser.parse_args()
    
    deployer = EQ12EnterpriseDeployer(args.workspace)
    
    if args.action == "setup":
        logger.info(" Starting EQ12 Enterprise Setup...")
        
        if not deployer.check_prerequisites():
            logger.error(" Prerequisites check failed")
            sys.exit(1)
        
        if not deployer.setup_enterprise_structure():
            logger.error(" Enterprise structure setup failed")
            sys.exit(1)
        
        if not deployer.validate_eq12_foundation():
            logger.error(" EQ12 foundation validation failed")
            sys.exit(1)
        
        if not deployer.setup_environment():
            logger.error(" Environment setup failed")
            sys.exit(1)
        
        logger.info(" EQ12 Enterprise setup complete!")
        logger.info(" Next steps:")
        logger.info("   1. Review and update .env file with your passwords")
        logger.info("   2. Run: python eq12_enterprise_quick_deploy.py --action deploy")
    
    elif args.action == "deploy":
        logger.info(" Starting EQ12 Enterprise Deployment...")
        
        if not deployer.deploy_infrastructure():
            logger.error(" Infrastructure deployment failed")
            sys.exit(1)
        
        if not deployer.deploy_eq12_services():
            logger.error(" EQ12 services deployment failed")
            sys.exit(1)
        
        logger.info(" EQ12 Enterprise deployment complete!")
        logger.info(" Access points:")
        logger.info("    EQ12 Control Interface: C:\\EQ12\\EQ12SystemManager\\bin\\Release\\net8.0-windows\\EQ12SystemManager.exe")
        logger.info("    Grafana Dashboard: http://localhost:3000")
        logger.info("    Prometheus: http://localhost:9090")
        logger.info("    MinIO Console: http://localhost:9001")
        logger.info("    Parlay API: http://localhost/api/parlay/docs")
    
    elif args.action == "status":
        status = deployer.get_deployment_status()
        logger.info(f" Deployment Status: {status['status']}")
        
        if 'services' in status:
            logger.info(f" Services: {status['healthy_services']}/{status['total_services']} healthy")
            for service in status['services']:
                state_icon = "" if service['state'] == 'running' else ""
                logger.info(f"   {state_icon} {service['name']}: {service['state']}")
    
    elif args.action == "stop":
        if deployer.stop_deployment():
            logger.info(" EQ12 Enterprise stopped successfully")
        else:
            logger.error(" Stop operation failed")
            sys.exit(1)

if __name__ == "__main__":
    main()