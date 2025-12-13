#!/usr/bin/env python3
"""
EQ12 System Configuration Generator - SCADA-Style Automation
========================================================

Generates configuration files for all EQ12 components based on system scan:
- Professional Parlay Engines (400+ Python scripts)
- Resource Monitoring Systems
- Visual Studio Extensions
- Production Services
- Dashboard Components
- AI/ML Models
- Security & Compliance Systems

Author: EQ12 Engineering Team
Date: November 8, 2025
Version: 1.0.0 (Industrial SCADA Style)
"""

import os
import json
import yaml
import argparse
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import shutil
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/EQ12/logs/system_config_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EQ12SystemComponent:
    """Represents a single EQ12 system component (like a PLC or HMI station)"""
    name: str
    type: str  # "betting_engine", "monitor", "dashboard", "ai_model", "service"
    script_path: str
    config_path: str
    dependencies: List[str]
    status: str = "unknown"
    last_health_check: Optional[str] = None
    performance_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {}

@dataclass
class EQ12SystemConfig:
    """Master system configuration (like SCADA project file)"""
    system_id: str
    components: List[EQ12SystemComponent]
    global_settings: Dict[str, Any]
    network_config: Dict[str, Any]
    security_config: Dict[str, Any]
    monitoring_config: Dict[str, Any]
    created_timestamp: str
    version: str = "1.0.0"

class EQ12SystemScanner:
    """Scans EQ12 workspace to identify all components (like PLC network discovery)"""
    
    def __init__(self, workspace_path: str = "C:/EQ12"):
        self.workspace_path = Path(workspace_path)
        self.components: List[EQ12SystemComponent] = []
        
    def scan_system(self) -> List[EQ12SystemComponent]:
        """Perform comprehensive system scan"""
        logger.info(" Starting EQ12 system component discovery...")
        
        # Scan main scripts directory
        self._scan_betting_engines()
        self._scan_monitoring_systems()
        self._scan_dashboard_components()
        self._scan_ai_models()
        self._scan_production_services()
        self._scan_automation_tools()
        self._scan_security_components()
        
        logger.info(f" Discovered {len(self.components)} system components")
        return self.components
    
    def _scan_betting_engines(self):
        """Scan for betting/parlay engines"""
        scripts_dir = self.workspace_path / "scripts"
        patterns = [
            "*parlay*.py", "*betting*.py", "*sgp*.py", "*odds*.py", 
            "*sports*.py", "*nfl*.py", "*nba*.py", "*mlb*.py"
        ]
        
        for pattern in patterns:
            for script in scripts_dir.glob(pattern):
                if script.is_file():
                    component = EQ12SystemComponent(
                        name=script.stem,
                        type="betting_engine",
                        script_path=str(script),
                        config_path=str(self.workspace_path / "configs" / f"{script.stem}_config.json"),
                        dependencies=self._analyze_dependencies(script)
                    )
                    self.components.append(component)
    
    def _scan_monitoring_systems(self):
        """Scan for monitoring and health check systems"""
        patterns = ["*monitor*.py", "*health*.py", "*status*.py", "*resource*.py"]
        scripts_dir = self.workspace_path / "scripts"
        
        for pattern in patterns:
            for script in scripts_dir.glob(pattern):
                if script.is_file():
                    component = EQ12SystemComponent(
                        name=script.stem,
                        type="monitor",
                        script_path=str(script),
                        config_path=str(self.workspace_path / "configs" / f"{script.stem}_config.json"),
                        dependencies=self._analyze_dependencies(script)
                    )
                    self.components.append(component)
    
    def _scan_dashboard_components(self):
        """Scan for dashboard and visualization components"""
        dashboard_dir = self.workspace_path / "dashboard"
        if dashboard_dir.exists():
            for file in dashboard_dir.glob("*.html"):
                component = EQ12SystemComponent(
                    name=file.stem,
                    type="dashboard",
                    script_path=str(file),
                    config_path=str(self.workspace_path / "configs" / f"{file.stem}_config.json"),
                    dependencies=[]
                )
                self.components.append(component)
    
    def _scan_ai_models(self):
        """Scan for AI/ML models and inference engines"""
        patterns = ["*ai*.py", "*ml*.py", "*model*.py", "*inference*.py", "*coral*.py"]
        scripts_dir = self.workspace_path / "scripts"
        
        for pattern in patterns:
            for script in scripts_dir.glob(pattern):
                if script.is_file():
                    component = EQ12SystemComponent(
                        name=script.stem,
                        type="ai_model",
                        script_path=str(script),
                        config_path=str(self.workspace_path / "configs" / f"{script.stem}_config.json"),
                        dependencies=self._analyze_dependencies(script)
                    )
                    self.components.append(component)
    
    def _scan_production_services(self):
        """Scan for production services and automation tools"""
        patterns = ["*service*.py", "*automation*.py", "*orchestrator*.py", "*launcher*.py"]
        scripts_dir = self.workspace_path / "scripts"
        
        for pattern in patterns:
            for script in scripts_dir.glob(pattern):
                if script.is_file():
                    component = EQ12SystemComponent(
                        name=script.stem,
                        type="service",
                        script_path=str(script),
                        config_path=str(self.workspace_path / "configs" / f"{script.stem}_config.json"),
                        dependencies=self._analyze_dependencies(script)
                    )
                    self.components.append(component)
    
    def _scan_automation_tools(self):
        """Scan for automation and workflow tools"""
        patterns = ["*wrapper*.ps1", "*manager*.ps1", "*deploy*.ps1", "*setup*.ps1"]
        scripts_dir = self.workspace_path / "scripts"
        
        for pattern in patterns:
            for script in scripts_dir.glob(pattern):
                if script.is_file():
                    component = EQ12SystemComponent(
                        name=script.stem,
                        type="automation",
                        script_path=str(script),
                        config_path=str(self.workspace_path / "configs" / f"{script.stem}_config.json"),
                        dependencies=[]
                    )
                    self.components.append(component)
    
    def _scan_security_components(self):
        """Scan for security and compliance tools"""
        patterns = ["*security*.py", "*gitleaks*.py", "*audit*.py", "*compliance*.py"]
        scripts_dir = self.workspace_path / "scripts"
        
        for pattern in patterns:
            for script in scripts_dir.glob(pattern):
                if script.is_file():
                    component = EQ12SystemComponent(
                        name=script.stem,
                        type="security",
                        script_path=str(script),
                        config_path=str(self.workspace_path / "configs" / f"{script.stem}_config.json"),
                        dependencies=self._analyze_dependencies(script)
                    )
                    self.components.append(component)
    
    def _analyze_dependencies(self, script_path: Path) -> List[str]:
        """Analyze script dependencies (like PLC I/O dependencies)"""
        dependencies = []
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for common EQ12 imports and dependencies
            import_patterns = [
                "eq12_", "from eq12", "import eq12",
                "requests", "openai", "pandas", "numpy",
                "telegram", "discord", "playwright"
            ]
            
            for pattern in import_patterns:
                if pattern in content:
                    dependencies.append(pattern)
                    
        except Exception as e:
            logger.warning(f"Could not analyze dependencies for {script_path}: {e}")
            
        return list(set(dependencies))

class EQ12ConfigGenerator:
    """Generates SCADA-style configuration files for EQ12 components"""
    
    def __init__(self, workspace_path: str = "C:/EQ12"):
        self.workspace_path = Path(workspace_path)
        self.configs_dir = self.workspace_path / "configs"
        self.configs_dir.mkdir(exist_ok=True)
        
    def generate_master_config(self, components: List[EQ12SystemComponent]) -> EQ12SystemConfig:
        """Generate master system configuration (like main SCADA project)"""
        logger.info(" Generating master system configuration...")
        
        master_config = EQ12SystemConfig(
            system_id="EQ12_PRODUCTION_SYSTEM",
            components=components,
            global_settings=self._get_global_settings(),
            network_config=self._get_network_config(),
            security_config=self._get_security_config(),
            monitoring_config=self._get_monitoring_config(),
            created_timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Save master config
        master_config_path = self.configs_dir / "eq12_master_config.json"
        with open(master_config_path, 'w') as f:
            json.dump(asdict(master_config), f, indent=4, default=str)
        
        logger.info(f" Master configuration saved: {master_config_path}")
        return master_config
    
    def generate_component_configs(self, components: List[EQ12SystemComponent]):
        """Generate individual component configurations"""
        logger.info(f" Generating {len(components)} component configurations...")
        
        for component in components:
            config = self._generate_component_config(component)
            config_path = Path(component.config_path)
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
        
        logger.info(" All component configurations generated")
    
    def _generate_component_config(self, component: EQ12SystemComponent) -> Dict[str, Any]:
        """Generate configuration for a single component"""
        base_config = {
            "component_info": {
                "name": component.name,
                "type": component.type,
                "script_path": component.script_path,
                "dependencies": component.dependencies,
                "version": "1.0.0"
            },
            "runtime_settings": self._get_runtime_settings(component),
            "monitoring": self._get_monitoring_settings(component),
            "logging": self._get_logging_settings(component),
            "security": self._get_security_settings(component)
        }
        
        # Add type-specific configurations
        if component.type == "betting_engine":
            base_config.update(self._get_betting_engine_config(component))
        elif component.type == "monitor":
            base_config.update(self._get_monitor_config(component))
        elif component.type == "dashboard":
            base_config.update(self._get_dashboard_config(component))
        elif component.type == "ai_model":
            base_config.update(self._get_ai_model_config(component))
        elif component.type == "service":
            base_config.update(self._get_service_config(component))
        
        return base_config
    
    def _get_global_settings(self) -> Dict[str, Any]:
        """Global system settings"""
        return {
            "system_name": "EQ12 Production System",
            "environment": "production",
            "timezone": "UTC",
            "default_timeout": 30,
            "max_concurrent_operations": 10,
            "log_level": "INFO",
            "auto_restart": True,
            "health_check_interval": 60
        }
    
    def _get_network_config(self) -> Dict[str, Any]:
        """Network configuration settings"""
        return {
            "api_endpoints": {
                "odds_api": "https://api.the-odds-api.com/v4",
                "openai_api": "https://api.openai.com/v1",
                "telegram_api": "https://api.telegram.org"
            },
            "timeouts": {
                "api_request": 30,
                "database_query": 10,
                "file_operation": 5
            },
            "retry_settings": {
                "max_retries": 3,
                "retry_delay": 1,
                "exponential_backoff": True
            }
        }
    
    def _get_security_config(self) -> Dict[str, Any]:
        """Security configuration settings"""
        return {
            "encryption": {
                "algorithm": "AES-256",
                "key_rotation_days": 30
            },
            "authentication": {
                "method": "api_key",
                "token_expiry_hours": 24
            },
            "audit": {
                "log_all_operations": True,
                "retain_logs_days": 90
            },
            "compliance": {
                "gdpr_enabled": True,
                "data_retention_days": 365
            }
        }
    
    def _get_monitoring_config(self) -> Dict[str, Any]:
        """Monitoring configuration settings"""
        return {
            "metrics": {
                "cpu_threshold": 80,
                "memory_threshold": 85,
                "disk_threshold": 90,
                "response_time_threshold": 5000
            },
            "alerting": {
                "enabled": True,
                "channels": ["telegram", "email", "dashboard"],
                "escalation_time": 300
            },
            "health_checks": {
                "interval_seconds": 60,
                "timeout_seconds": 10,
                "failure_threshold": 3
            }
        }
    
    def _get_runtime_settings(self, component: EQ12SystemComponent) -> Dict[str, Any]:
        """Runtime settings for component"""
        return {
            "enabled": True,
            "auto_start": True,
            "restart_on_failure": True,
            "max_memory_mb": 512,
            "execution_timeout": 300,
            "priority": "normal"
        }
    
    def _get_monitoring_settings(self, component: EQ12SystemComponent) -> Dict[str, Any]:
        """Monitoring settings for component"""
        return {
            "health_check_enabled": True,
            "performance_monitoring": True,
            "error_tracking": True,
            "metrics_collection": True
        }
    
    def _get_logging_settings(self, component: EQ12SystemComponent) -> Dict[str, Any]:
        """Logging settings for component"""
        return {
            "log_level": "INFO",
            "log_file": f"C:/EQ12/logs/{component.name}.log",
            "log_rotation": True,
            "max_log_size_mb": 100,
            "backup_count": 5
        }
    
    def _get_security_settings(self, component: EQ12SystemComponent) -> Dict[str, Any]:
        """Security settings for component"""
        return {
            "require_authentication": True,
            "encrypt_data": True,
            "audit_operations": True,
            "access_level": "standard"
        }
    
    def _get_betting_engine_config(self, component: EQ12SystemComponent) -> Dict[str, Any]:
        """Betting engine specific configuration"""
        return {
            "betting_settings": {
                "target_win_probability": 0.01,
                "kelly_fraction": 0.25,
                "max_bet_amount": 100,
                "min_ev_threshold": 0.05,
                "correlation_threshold": 0.4
            },
            "api_settings": {
                "odds_api_key": "${ODDS_API_KEY}",
                "update_interval": 300,
                "sports": ["NBA", "NHL", "NFL", "CBB", "CFB"]
            },
            "coral_acceleration": {
                "enabled": True,
                "model_path": "C:/EQ12/ai_models/coral_model.tflite",
                "simulation_mode": True
            }
        }
    
    def _get_monitor_config(self, component: EQ12SystemComponent) -> Dict[str, Any]:
        """Monitor specific configuration"""
        return {
            "monitoring_settings": {
                "check_interval": 60,
                "alert_threshold": 3,
                "auto_healing": True,
                "restart_failed_services": True
            },
            "metrics": {
                "collect_system_metrics": True,
                "collect_application_metrics": True,
                "store_historical_data": True
            }
        }
    
    def _get_dashboard_config(self, component: EQ12SystemComponent) -> Dict[str, Any]:
        """Dashboard specific configuration"""
        return {
            "dashboard_settings": {
                "refresh_interval": 30,
                "theme": "dark",
                "auto_layout": True,
                "responsive": True
            },
            "data_sources": [
                "betting_engines",
                "monitoring_systems",
                "api_endpoints"
            ]
        }
    
    def _get_ai_model_config(self, component: EQ12SystemComponent) -> Dict[str, Any]:
        """AI model specific configuration"""
        return {
            "model_settings": {
                "inference_mode": "production",
                "batch_size": 32,
                "max_sequence_length": 512,
                "temperature": 0.7
            },
            "optimization": {
                "use_coral_acceleration": True,
                "enable_quantization": True,
                "cache_predictions": True
            }
        }
    
    def _get_service_config(self, component: EQ12SystemComponent) -> Dict[str, Any]:
        """Service specific configuration"""
        return {
            "service_settings": {
                "startup_type": "automatic",
                "recovery_action": "restart",
                "dependencies": component.dependencies,
                "environment_variables": {}
            }
        }

class EQ12HMIDashboardGenerator:
    """Generates live HMI dashboard for EQ12 system visualization"""
    
    def __init__(self, workspace_path: str = "C:/EQ12"):
        self.workspace_path = Path(workspace_path)
        self.dashboard_dir = self.workspace_path / "dashboard"
        self.dashboard_dir.mkdir(exist_ok=True)
    
    def generate_live_dashboard(self, system_config: EQ12SystemConfig):
        """Generate live HMI dashboard HTML/CSS/JS"""
        logger.info(" Generating live HMI dashboard...")
        
        html_content = self._generate_html_template(system_config)
        css_content = self._generate_css_styles()
        js_content = self._generate_javascript_logic(system_config)
        
        # Save dashboard files
        with open(self.dashboard_dir / "eq12_live_hmi.html", 'w') as f:
            f.write(html_content)
        
        with open(self.dashboard_dir / "eq12_hmi_styles.css", 'w') as f:
            f.write(css_content)
        
        with open(self.dashboard_dir / "eq12_hmi_logic.js", 'w') as f:
            f.write(js_content)
        
        logger.info(" Live HMI dashboard generated")
    
    def _generate_html_template(self, system_config: EQ12SystemConfig) -> str:
        """Generate HTML template"""
        components_by_type = {}
        for component in system_config.components:
            if component.type not in components_by_type:
                components_by_type[component.type] = []
            components_by_type[component.type].append(component)
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 Live HMI Dashboard</title>
    <link rel="stylesheet" href="eq12_hmi_styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <header class="hmi-header">
        <h1> EQ12 Production System HMI</h1>
        <div class="system-status">
            <span id="system-time"></span>
            <span id="system-health" class="status-indicator"></span>
        </div>
    </header>
    
    <main class="hmi-dashboard">
        <aside class="sidebar">
            <h2>System Components</h2>
            <nav class="component-nav">
                <button class="nav-btn active" data-section="overview">Overview</button>
                <button class="nav-btn" data-section="betting">Betting Engines</button>
                <button class="nav-btn" data-section="monitoring">Monitoring</button>
                <button class="nav-btn" data-section="ai">AI Models</button>
                <button class="nav-btn" data-section="services">Services</button>
                <button class="nav-btn" data-section="security">Security</button>
            </nav>
        </aside>
        
        <section class="main-panel">
            <div id="overview-section" class="panel-section active">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>System Health</h3>
                        <div class="health-indicator">
                            <div class="progress-ring">
                                <span id="health-percentage">98%</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>Active Components</h3>
                        <div class="count-display">
                            <span id="active-components">{len(system_config.components)}</span>
                            <small>/ {len(system_config.components)} total</small>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>Betting Performance</h3>
                        <div class="performance-chart">
                            <canvas id="performance-chart"></canvas>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>System Alerts</h3>
                        <div id="alerts-list" class="alerts-container">
                            <div class="alert info">System initialized successfully</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="betting-section" class="panel-section">
                <h2>Betting Engines Status</h2>
                <div class="components-grid">
                    {self._generate_component_cards(components_by_type.get("betting_engine", []))}
                </div>
            </div>
            
            <div id="monitoring-section" class="panel-section">
                <h2>Monitoring Systems</h2>
                <div class="components-grid">
                    {self._generate_component_cards(components_by_type.get("monitor", []))}
                </div>
            </div>
            
            <div id="ai-section" class="panel-section">
                <h2>AI Models</h2>
                <div class="components-grid">
                    {self._generate_component_cards(components_by_type.get("ai_model", []))}
                </div>
            </div>
            
            <div id="services-section" class="panel-section">
                <h2>Production Services</h2>
                <div class="components-grid">
                    {self._generate_component_cards(components_by_type.get("service", []))}
                </div>
            </div>
            
            <div id="security-section" class="panel-section">
                <h2>Security Components</h2>
                <div class="components-grid">
                    {self._generate_component_cards(components_by_type.get("security", []))}
                </div>
            </div>
        </section>
    </main>
    
    <script src="eq12_hmi_logic.js"></script>
</body>
</html>'''
    
    def _generate_component_cards(self, components: List[EQ12SystemComponent]) -> str:
        """Generate HTML cards for components"""
        cards = []
        for component in components:
            cards.append(f'''
                <div class="component-card" data-component="{component.name}">
                    <div class="card-header">
                        <h3>{component.name}</h3>
                        <span class="status-indicator running"></span>
                    </div>
                    <div class="card-body">
                        <p><strong>Type:</strong> {component.type}</p>
                        <p><strong>Dependencies:</strong> {len(component.dependencies)}</p>
                        <div class="card-metrics">
                            <span class="metric">CPU: <span class="cpu-usage">0%</span></span>
                            <span class="metric">Memory: <span class="memory-usage">0MB</span></span>
                        </div>
                    </div>
                    <div class="card-actions">
                        <button class="btn-start" onclick="controlComponent('{component.name}', 'start')">Start</button>
                        <button class="btn-stop" onclick="controlComponent('{component.name}', 'stop')">Stop</button>
                        <button class="btn-restart" onclick="controlComponent('{component.name}', 'restart')">Restart</button>
                    </div>
                </div>
            ''')
        return '\n'.join(cards)
    
    def _generate_css_styles(self) -> str:
        """Generate CSS styles for HMI dashboard"""
        return '''
/* EQ12 HMI Dashboard Styles - Industrial SCADA Theme */
:root {
    --bg-primary: #0a0a0a;
    --bg-secondary: #1a1a1a;
    --bg-accent: #2a2a2a;
    --text-primary: #fafafa;
    --text-secondary: #cccccc;
    --accent-green: #21bf73;
    --accent-blue: #1e90ff;
    --accent-yellow: #ffd700;
    --accent-red: #ff4444;
    --border-color: #333333;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', 'Roboto', monospace;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
}

.hmi-header {
    background: var(--bg-secondary);
    padding: 1rem 2rem;
    border-bottom: 2px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.hmi-header h1 {
    color: var(--accent-green);
    font-size: 1.5rem;
    font-weight: 600;
}

.system-status {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.status-indicator {
    font-size: 1.2rem;
    color: var(--accent-green);
}

.hmi-dashboard {
    display: grid;
    grid-template-columns: 250px 1fr;
    height: calc(100vh - 80px);
}

.sidebar {
    background: var(--bg-secondary);
    border-right: 2px solid var(--border-color);
    padding: 1rem;
}

.sidebar h2 {
    color: var(--accent-blue);
    margin-bottom: 1rem;
    font-size: 1.1rem;
}

.component-nav {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.nav-btn {
    background: var(--bg-accent);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 0.75rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: left;
}

.nav-btn:hover, .nav-btn.active {
    background: var(--accent-green);
    border-color: var(--accent-green);
}

.main-panel {
    background: var(--bg-primary);
    overflow-y: auto;
    padding: 1rem;
}

.panel-section {
    display: none;
}

.panel-section.active {
    display: block;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
}

.metric-card h3 {
    color: var(--accent-blue);
    margin-bottom: 1rem;
    font-size: 1.1rem;
}

.health-indicator {
    display: flex;
    justify-content: center;
    align-items: center;
}

.progress-ring {
    position: relative;
    width: 80px;
    height: 80px;
    border: 4px solid var(--border-color);
    border-top: 4px solid var(--accent-green);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: spin 2s linear infinite;
}

.progress-ring span {
    font-size: 1.2rem;
    font-weight: bold;
    color: var(--accent-green);
}

.count-display {
    font-size: 2rem;
    font-weight: bold;
    color: var(--accent-green);
}

.count-display small {
    display: block;
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 0.5rem;
}

.components-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1rem;
}

.component-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-color);
}

.card-header h3 {
    color: var(--text-primary);
    font-size: 1rem;
}

.card-header .status-indicator.running {
    color: var(--accent-green);
}

.card-header .status-indicator.stopped {
    color: var(--accent-red);
}

.card-header .status-indicator.warning {
    color: var(--accent-yellow);
}

.card-body p {
    margin-bottom: 0.5rem;
    color: var(--text-secondary);
}

.card-metrics {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
    padding-top: 0.5rem;
    border-top: 1px solid var(--border-color);
}

.metric {
    font-size: 0.9rem;
    color: var(--text-secondary);
}

.card-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
}

.card-actions button {
    flex: 1;
    padding: 0.5rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
    transition: all 0.3s ease;
}

.btn-start {
    background: var(--accent-green);
    color: white;
}

.btn-stop {
    background: var(--accent-red);
    color: white;
}

.btn-restart {
    background: var(--accent-yellow);
    color: var(--bg-primary);
}

.card-actions button:hover {
    opacity: 0.8;
    transform: translateY(-1px);
}

.alerts-container {
    max-height: 200px;
    overflow-y: auto;
}

.alert {
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    border-radius: 4px;
    border-left: 4px solid;
}

.alert.info {
    background: rgba(30, 144, 255, 0.1);
    border-left-color: var(--accent-blue);
}

.alert.warning {
    background: rgba(255, 215, 0, 0.1);
    border-left-color: var(--accent-yellow);
}

.alert.error {
    background: rgba(255, 68, 68, 0.1);
    border-left-color: var(--accent-red);
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
    .hmi-dashboard {
        grid-template-columns: 1fr;
    }
    
    .sidebar {
        height: auto;
        border-right: none;
        border-bottom: 2px solid var(--border-color);
    }
    
    .component-nav {
        flex-direction: row;
        overflow-x: auto;
    }
    
    .metrics-grid {
        grid-template-columns: 1fr;
    }
    
    .components-grid {
        grid-template-columns: 1fr;
    }
}
        '''
    
    def _generate_javascript_logic(self, system_config: EQ12SystemConfig) -> str:
        """Generate JavaScript logic for HMI dashboard"""
        return f'''
// EQ12 HMI Dashboard Logic - Industrial SCADA Style
class EQ12HMIController {{
    constructor() {{
        this.components = {json.dumps([asdict(c) for c in system_config.components], indent=4)};
        this.updateInterval = 5000; // 5 seconds
        this.isConnected = true;
        this.init();
    }}
    
    init() {{
        this.setupNavigation();
        this.setupRealTimeUpdates();
        this.updateSystemTime();
        this.initCharts();
        this.startHealthMonitoring();
    }}
    
    setupNavigation() {{
        const navButtons = document.querySelectorAll('.nav-btn');
        const sections = document.querySelectorAll('.panel-section');
        
        navButtons.forEach(btn => {{
            btn.addEventListener('click', () => {{
                // Remove active classes
                navButtons.forEach(b => b.classList.remove('active'));
                sections.forEach(s => s.classList.remove('active'));
                
                // Add active class to clicked button and corresponding section
                btn.classList.add('active');
                const sectionId = btn.dataset.section + '-section';
                document.getElementById(sectionId).classList.add('active');
            }});
        }});
    }}
    
    setupRealTimeUpdates() {{
        setInterval(() => {{
            this.updateComponentStatus();
            this.updateSystemMetrics();
            this.updatePerformanceChart();
        }}, this.updateInterval);
    }}
    
    updateSystemTime() {{
        setInterval(() => {{
            const now = new Date();
            document.getElementById('system-time').textContent = 
                now.toISOString().slice(0, 19).replace('T', ' ') + ' UTC';
        }}, 1000);
    }}
    
    updateComponentStatus() {{
        this.components.forEach(component => {{
            const card = document.querySelector(`[data-component="${{component.name}}"]`);
            if (card) {{
                // Simulate real-time metrics
                const cpuUsage = Math.floor(Math.random() * 30) + 10;
                const memUsage = Math.floor(Math.random() * 200) + 50;
                
                card.querySelector('.cpu-usage').textContent = cpuUsage + '%';
                card.querySelector('.memory-usage').textContent = memUsage + 'MB';
                
                // Update status indicator based on performance
                const statusIndicator = card.querySelector('.status-indicator');
                if (cpuUsage > 80 || memUsage > 400) {{
                    statusIndicator.className = 'status-indicator warning';
                }} else {{
                    statusIndicator.className = 'status-indicator running';
                }}
            }}
        }});
        
        // Update active components count
        const activeCount = this.components.filter(c => Math.random() > 0.1).length;
        document.getElementById('active-components').textContent = activeCount;
    }}
    
    updateSystemMetrics() {{
        // Update system health percentage
        const healthPercentage = Math.floor(Math.random() * 10) + 90;
        document.getElementById('health-percentage').textContent = healthPercentage + '%';
        
        // Update system health indicator
        const healthIndicator = document.getElementById('system-health');
        if (healthPercentage > 95) {{
            healthIndicator.style.color = 'var(--accent-green)';
        }} else if (healthPercentage > 85) {{
            healthIndicator.style.color = 'var(--accent-yellow)';
        }} else {{
            healthIndicator.style.color = 'var(--accent-red)';
        }}
    }}
    
    initCharts() {{
        const ctx = document.getElementById('performance-chart');
        if (ctx) {{
            this.performanceChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: Array.from({{length: 10}}, (_, i) => `${{i * 5}}s`),
                    datasets: [{{
                        label: 'Win Rate %',
                        data: Array.from({{length: 10}}, () => Math.random() * 2 + 0.5),
                        borderColor: 'var(--accent-green)',
                        backgroundColor: 'rgba(33, 191, 115, 0.1)',
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 3,
                            ticks: {{
                                color: 'var(--text-secondary)'
                            }}
                        }},
                        x: {{
                            ticks: {{
                                color: 'var(--text-secondary)'
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{
                                color: 'var(--text-primary)'
                            }}
                        }}
                    }}
                }}
            }});
        }}
    }}
    
    updatePerformanceChart() {{
        if (this.performanceChart) {{
            // Shift data and add new point
            this.performanceChart.data.datasets[0].data.shift();
            this.performanceChart.data.datasets[0].data.push(Math.random() * 2 + 0.5);
            this.performanceChart.update('none');
        }}
    }}
    
    startHealthMonitoring() {{
        // Simulate connection status
        setInterval(() => {{
            this.isConnected = Math.random() > 0.05; // 95% uptime simulation
            this.updateConnectionStatus();
        }}, 10000);
    }}
    
    updateConnectionStatus() {{
        const healthIndicator = document.getElementById('system-health');
        if (this.isConnected) {{
            healthIndicator.textContent = '';
            healthIndicator.title = 'System Online';
        }} else {{
            healthIndicator.textContent = '';
            healthIndicator.title = 'System Offline';
            healthIndicator.style.color = 'var(--accent-red)';
            this.addAlert('Connection lost to system components', 'error');
        }}
    }}
    
    addAlert(message, type = 'info') {{
        const alertsContainer = document.getElementById('alerts-list');
        const alert = document.createElement('div');
        alert.className = `alert ${{type}}`;
        alert.textContent = new Date().toLocaleTimeString() + ': ' + message;
        
        alertsContainer.insertBefore(alert, alertsContainer.firstChild);
        
        // Remove old alerts (keep only 5)
        while (alertsContainer.children.length > 5) {{
            alertsContainer.removeChild(alertsContainer.lastChild);
        }}
    }}
}}

// Component control functions
function controlComponent(componentName, action) {{
    console.log(`${{action.toUpperCase()}} command sent to ${{componentName}}`);
    
    // Simulate API call
    fetch('/api/components/control', {{
        method: 'POST',
        headers: {{
            'Content-Type': 'application/json'
        }},
        body: JSON.stringify({{
            component: componentName,
            action: action
        }})
    }})
    .then(response => response.json())
    .then(data => {{
        hmi.addAlert(`${{componentName}} ${{action}} command executed`, 'info');
    }})
    .catch(error => {{
        hmi.addAlert(`Failed to ${{action}} ${{componentName}}: ${{error}}`, 'error');
    }});
}}

// Initialize HMI controller when page loads
let hmi;
document.addEventListener('DOMContentLoaded', () => {{
    hmi = new EQ12HMIController();
    hmi.addAlert('EQ12 HMI Dashboard initialized successfully', 'info');
}});

// Export for external use
window.EQ12HMI = {{
    controller: () => hmi,
    addAlert: (msg, type) => hmi.addAlert(msg, type),
    updateComponent: (name, status) => hmi.updateComponentStatus(name, status)
}};
        '''

def main():
    """Main function to run EQ12 system configuration generation"""
    parser = argparse.ArgumentParser(description="EQ12 System Configuration Generator")
    parser.add_argument("--workspace", default="C:/EQ12", help="EQ12 workspace path")
    parser.add_argument("--scan-only", action="store_true", help="Only scan system, don't generate configs")
    parser.add_argument("--generate-dashboard", action="store_true", help="Generate HMI dashboard")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize scanner and generator
        scanner = EQ12SystemScanner(args.workspace)
        config_generator = EQ12ConfigGenerator(args.workspace)
        dashboard_generator = EQ12HMIDashboardGenerator(args.workspace)
        
        # Scan system for components
        logger.info(" Starting EQ12 System Configuration Generator...")
        components = scanner.scan_system()
        
        if args.scan_only:
            logger.info(f" System scan complete. Found {len(components)} components:")
            for component in components:
                logger.info(f"  - {component.name} ({component.type})")
            return
        
        # Generate configurations
        master_config = config_generator.generate_master_config(components)
        config_generator.generate_component_configs(components)
        
        # Generate HMI dashboard if requested
        if args.generate_dashboard:
            dashboard_generator.generate_live_dashboard(master_config)
        
        # Generate summary report
        report = {
            "generation_time": datetime.now(timezone.utc).isoformat(),
            "total_components": len(components),
            "components_by_type": {},
            "master_config_path": str(config_generator.configs_dir / "eq12_master_config.json"),
            "dashboard_generated": args.generate_dashboard
        }
        
        for component in components:
            if component.type not in report["components_by_type"]:
                report["components_by_type"][component.type] = 0
            report["components_by_type"][component.type] += 1
        
        report_path = Path(args.workspace) / "logs" / f"config_generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=4)
        
        logger.info(" EQ12 System Configuration Generation Complete!")
        logger.info(f" Generated configurations for {len(components)} components")
        logger.info(f" Master config: {master_config.system_id}")
        logger.info(f" Report saved: {report_path}")
        
        if args.generate_dashboard:
            dashboard_path = Path(args.workspace) / "dashboard" / "eq12_live_hmi.html"
            logger.info(f" HMI Dashboard: {dashboard_path}")
        
    except Exception as e:
        logger.error(f" Configuration generation failed: {e}")
        raise

if __name__ == "__main__":
    main()