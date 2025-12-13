#!/usr/bin/env python3
"""
EQ12 System Management Suite - Autonomous Operations Center
==========================================================
Comprehensive system management with AI-assisted control and self-healing
"""

import argparse
import asyncio
import json
import logging
import os
import psutil
import sqlite3
import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import yaml


class EQ12SystemManager:
    """Central system management class for EQ12 AI Enterprise"""
    
    def __init__(self, workspace_path: str = "C:/EQ12"):
        self.workspace_path = Path(workspace_path)
        self.logs_dir = self.workspace_path / "logs"
        self.configs_dir = self.workspace_path / "configs"
        self.data_dir = self.workspace_path / "data"
        self.scripts_dir = self.workspace_path / "scripts"
        
        # Ensure directories exist
        for directory in [self.logs_dir, self.configs_dir, self.data_dir]:
            directory.mkdir(exist_ok=True)
        
        # Setup logging
        log_file = self.logs_dir / f"system_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # System state
        self.system_state = {
            "processes": {},
            "health_metrics": {},
            "last_check": None,
            "error_count": 0,
            "uptime_start": datetime.now()
        }
        
        # AI models registry
        self.ai_models = {
            "betting_predictor": {"status": "unknown", "accuracy": 0.0},
            "anomaly_detector": {"status": "unknown", "accuracy": 0.0},
            "revenue_optimizer": {"status": "unknown", "accuracy": 0.0}
        }
        
        # Initialize database
        self.init_management_database()
        
        self.logger.info(" EQ12 System Manager initialized")

    def init_management_database(self):
        """Initialize system management database"""
        db_path = self.data_dir / "system_management.db"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # System metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                cpu_percent REAL,
                memory_percent REAL,
                disk_usage REAL,
                process_count INTEGER,
                health_score REAL
            )
        """)
        
        # Error tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                module TEXT,
                error_type TEXT,
                error_message TEXT,
                auto_fixed BOOLEAN,
                fix_action TEXT
            )
        """)
        
        # Performance tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                module TEXT,
                execution_time REAL,
                success BOOLEAN,
                resource_usage TEXT
            )
        """)
        
        # Revenue tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS revenue_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                source TEXT,
                amount REAL,
                currency TEXT,
                transaction_type TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        self.logger.info(" System management database initialized")

    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health metrics"""
        try:
            # Basic system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(str(self.workspace_path.root))
            
            # EQ12-specific processes
            eq12_processes = self.get_eq12_processes()
            
            # Calculate health score
            health_factors = {
                "cpu": (100 - cpu_percent) / 100,
                "memory": (100 - memory.percent) / 100,
                "disk": disk.free / disk.total,
                "processes": min(1.0, len(eq12_processes) / 5)  # Optimal 5 processes
            }
            
            health_score = sum(health_factors.values()) / len(health_factors)
            
            health_data = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_usage_percent": (disk.used / disk.total) * 100,
                "disk_free_gb": disk.free / (1024**3),
                "eq12_processes": len(eq12_processes),
                "health_score": health_score,
                "status": self.determine_health_status(health_score),
                "factors": health_factors
            }
            
            # Store metrics
            self.store_system_metrics(health_data)
            
            return health_data
            
        except Exception as e:
            self.logger.error(f"Failed to get system health: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def get_eq12_processes(self) -> List[Dict[str, Any]]:
        """Get all EQ12-related running processes"""
        eq12_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info', 'create_time']):
            try:
                cmdline = proc.info['cmdline'] or []
                if any('eq12' in str(item).lower() for item in cmdline):
                    eq12_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_mb": proc.info['memory_info'].rss / (1024*1024) if proc.info['memory_info'] else 0,
                        "cmdline": ' '.join(cmdline),
                        "uptime": time.time() - proc.info['create_time']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return eq12_processes

    def determine_health_status(self, health_score: float) -> str:
        """Determine system health status based on score"""
        if health_score >= 0.8:
            return "excellent"
        elif health_score >= 0.7:
            return "good"
        elif health_score >= 0.5:
            return "warning"
        else:
            return "critical"

    def store_system_metrics(self, metrics: Dict[str, Any]):
        """Store system metrics in database"""
        try:
            db_path = self.data_dir / "system_management.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO system_metrics 
                (timestamp, cpu_percent, memory_percent, disk_usage, process_count, health_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                metrics["timestamp"],
                metrics["cpu_percent"],
                metrics["memory_percent"],
                metrics["disk_usage_percent"],
                metrics["eq12_processes"],
                metrics["health_score"]
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to store system metrics: {e}")

    def run_system_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive system diagnostics"""
        self.logger.info(" Running system diagnostics...")
        
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "system_health": self.get_system_health(),
            "ai_models_status": self.check_ai_models_status(),
            "api_connectivity": self.test_api_connectivity(),
            "script_integrity": self.verify_script_integrity(),
            "log_analysis": self.analyze_recent_logs(),
            "recommendations": []
        }
        
        # Generate recommendations
        diagnostics["recommendations"] = self.generate_recommendations(diagnostics)
        
        # Save diagnostics report
        report_file = self.logs_dir / f"diagnostics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(diagnostics, f, indent=2)
        
        self.logger.info(f" Diagnostics complete. Report saved: {report_file}")
        
        return diagnostics

    def check_ai_models_status(self) -> Dict[str, Any]:
        """Check status of AI models"""
        models_dir = self.workspace_path / "ai_models"
        model_status = {}
        
        if models_dir.exists():
            for metadata_file in models_dir.glob("*_metadata.json"):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    model_name = metadata_file.stem.replace("_metadata", "")
                    model_status[model_name] = {
                        "status": "trained",
                        "accuracy": metadata.get("test_accuracy", metadata.get("test_r2", 0)),
                        "trained_at": metadata.get("trained_at", "unknown"),
                        "model_type": metadata.get("model_type", "unknown")
                    }
                    
                except Exception as e:
                    model_status[model_name] = {"status": "error", "error": str(e)}
        
        return model_status

    def test_api_connectivity(self) -> Dict[str, Any]:
        """Test connectivity to external APIs"""
        api_tests = {}
        
        # Test API key manager
        try:
            result = subprocess.run([
                "python", str(self.scripts_dir / "eq12_api_key_manager.py"), "--test-all"
            ], capture_output=True, text=True, timeout=60)
            
            api_tests["api_key_manager"] = {
                "status": "success" if result.returncode == 0 else "failed",
                "output": result.stdout,
                "errors": result.stderr
            }
            
        except Exception as e:
            api_tests["api_key_manager"] = {"status": "error", "error": str(e)}
        
        return api_tests

    def verify_script_integrity(self) -> Dict[str, Any]:
        """Verify integrity of critical scripts"""
        critical_scripts = [
            "eq12_betting_suite.py",
            "eq12_ai_trainer.py",
            "eq12_ai_inference_engine.py",
            "eq12_api_key_manager.py"
        ]
        
        integrity_results = {}
        
        for script in critical_scripts:
            script_path = self.workspace_path / script
            if not script_path.exists():
                script_path = self.scripts_dir / script
            
            if script_path.exists():
                try:
                    # Test syntax
                    result = subprocess.run([
                        "python", "-m", "py_compile", str(script_path)
                    ], capture_output=True, text=True)
                    
                    integrity_results[script] = {
                        "exists": True,
                        "syntax_valid": result.returncode == 0,
                        "size_kb": script_path.stat().st_size / 1024,
                        "last_modified": datetime.fromtimestamp(script_path.stat().st_mtime).isoformat()
                    }
                    
                except Exception as e:
                    integrity_results[script] = {"exists": True, "error": str(e)}
            else:
                integrity_results[script] = {"exists": False}
        
        return integrity_results

    def analyze_recent_logs(self) -> Dict[str, Any]:
        """Analyze recent log files for errors and patterns"""
        log_analysis = {
            "total_logs": 0,
            "error_count": 0,
            "warning_count": 0,
            "recent_errors": [],
            "patterns": {}
        }
        
        # Analyze logs from last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for log_file in self.logs_dir.glob("*.log"):
            try:
                if datetime.fromtimestamp(log_file.stat().st_mtime) > cutoff_time:
                    log_analysis["total_logs"] += 1
                    
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Count errors and warnings
                        error_count = content.lower().count('error')
                        warning_count = content.lower().count('warning')
                        
                        log_analysis["error_count"] += error_count
                        log_analysis["warning_count"] += warning_count
                        
                        # Extract recent errors
                        if error_count > 0:
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if 'error' in line.lower() and len(log_analysis["recent_errors"]) < 10:
                                    log_analysis["recent_errors"].append({
                                        "file": log_file.name,
                                        "line": line.strip(),
                                        "context": lines[max(0, i-1):i+2] if i > 0 else [line]
                                    })
                        
            except Exception as e:
                self.logger.error(f"Error analyzing log {log_file}: {e}")
        
        return log_analysis

    def generate_recommendations(self, diagnostics: Dict[str, Any]) -> List[str]:
        """Generate AI-assisted recommendations based on diagnostics"""
        recommendations = []
        
        # Health-based recommendations
        health_score = diagnostics["system_health"].get("health_score", 0)
        if health_score < 0.5:
            recommendations.append(" CRITICAL: System health is poor. Run emergency repair protocol.")
        elif health_score < 0.7:
            recommendations.append(" WARNING: System performance degraded. Consider optimization.")
        
        # CPU recommendations
        cpu_percent = diagnostics["system_health"].get("cpu_percent", 0)
        if cpu_percent > 80:
            recommendations.append(f" High CPU usage ({cpu_percent:.1f}%). Consider scaling or process optimization.")
        
        # Memory recommendations
        memory_percent = diagnostics["system_health"].get("memory_percent", 0)
        if memory_percent > 85:
            recommendations.append(f" High memory usage ({memory_percent:.1f}%). RAM upgrade recommended.")
        
        # AI model recommendations
        ai_status = diagnostics.get("ai_models_status", {})
        untrained_models = [name for name, status in ai_status.items() if status.get("status") != "trained"]
        if untrained_models:
            recommendations.append(f" AI models need training: {', '.join(untrained_models)}")
        
        # Error-based recommendations
        log_analysis = diagnostics.get("log_analysis", {})
        if log_analysis.get("error_count", 0) > 10:
            recommendations.append(" High error count detected. Run diagnostic and repair tools.")
        
        return recommendations

    def auto_repair_system(self) -> Dict[str, Any]:
        """Attempt automatic system repair"""
        self.logger.info(" Starting automatic system repair...")
        
        repair_actions = []
        repair_results = {
            "timestamp": datetime.now().isoformat(),
            "actions_taken": [],
            "success_count": 0,
            "failure_count": 0
        }
        
        # 1. Clear temporary files
        try:
            temp_files_cleared = self.clear_temp_files()
            repair_results["actions_taken"].append({
                "action": "clear_temp_files",
                "status": "success",
                "result": f"Cleared {temp_files_cleared} temporary files"
            })
            repair_results["success_count"] += 1
        except Exception as e:
            repair_results["actions_taken"].append({
                "action": "clear_temp_files",
                "status": "failed",
                "error": str(e)
            })
            repair_results["failure_count"] += 1
        
        # 2. Restart failed processes
        try:
            restarted_processes = self.restart_failed_processes()
            repair_results["actions_taken"].append({
                "action": "restart_processes",
                "status": "success",
                "result": f"Restarted {restarted_processes} processes"
            })
            repair_results["success_count"] += 1
        except Exception as e:
            repair_results["actions_taken"].append({
                "action": "restart_processes",
                "status": "failed",
                "error": str(e)
            })
            repair_results["failure_count"] += 1
        
        # 3. Update API keys
        try:
            api_result = subprocess.run([
                "python", str(self.scripts_dir / "eq12_api_key_manager.py"), "--validate-all"
            ], capture_output=True, text=True, timeout=60)
            
            repair_results["actions_taken"].append({
                "action": "validate_api_keys",
                "status": "success" if api_result.returncode == 0 else "failed",
                "result": api_result.stdout
            })
            
            if api_result.returncode == 0:
                repair_results["success_count"] += 1
            else:
                repair_results["failure_count"] += 1
                
        except Exception as e:
            repair_results["actions_taken"].append({
                "action": "validate_api_keys",
                "status": "failed",
                "error": str(e)
            })
            repair_results["failure_count"] += 1
        
        # 4. Run system integrity check
        try:
            integrity_result = subprocess.run([
                "python", str(self.workspace_path / "eq12_final_system_validation.py")
            ], capture_output=True, text=True, timeout=120)
            
            repair_results["actions_taken"].append({
                "action": "system_integrity_check",
                "status": "success" if integrity_result.returncode == 0 else "warning",
                "result": integrity_result.stdout
            })
            repair_results["success_count"] += 1
            
        except Exception as e:
            repair_results["actions_taken"].append({
                "action": "system_integrity_check",
                "status": "failed",
                "error": str(e)
            })
            repair_results["failure_count"] += 1
        
        # Save repair report
        report_file = self.logs_dir / f"auto_repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(repair_results, f, indent=2)
        
        self.logger.info(f" Auto-repair complete: {repair_results['success_count']} successes, {repair_results['failure_count']} failures")
        
        return repair_results

    def clear_temp_files(self) -> int:
        """Clear temporary and cache files"""
        temp_dirs = [
            self.logs_dir / "temp",
            self.workspace_path / "__pycache__",
            self.workspace_path / ".pytest_cache"
        ]
        
        files_cleared = 0
        
        for temp_dir in temp_dirs:
            if temp_dir.exists():
                for file_path in temp_dir.rglob("*"):
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            files_cleared += 1
                        except Exception:
                            pass
        
        return files_cleared

    def restart_failed_processes(self) -> int:
        """Restart any failed EQ12 processes"""
        # This is a placeholder - would need specific process management logic
        return 0

    def run_continuous_monitoring(self, interval: int = 300):
        """Run continuous system monitoring"""
        self.logger.info(f" Starting continuous monitoring (interval: {interval}s)")
        
        while True:
            try:
                # Get system health
                health_data = self.get_system_health()
                
                # Check for critical issues
                if health_data.get("health_score", 1.0) < 0.3:
                    self.logger.warning(" Critical system health detected - triggering auto-repair")
                    self.auto_repair_system()
                
                # Update system state
                self.system_state["last_check"] = datetime.now().isoformat()
                self.system_state["health_metrics"] = health_data
                
                # Sleep until next check
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.logger.info(" Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait before retrying

    def generate_system_report(self) -> str:
        """Generate comprehensive system report"""
        self.logger.info(" Generating system report...")
        
        diagnostics = self.run_system_diagnostics()
        
        report_lines = [
            "# EQ12 System Management Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## System Health Overview",
            f"- Health Score: {diagnostics['system_health'].get('health_score', 0):.2%}",
            f"- Status: {diagnostics['system_health'].get('status', 'unknown')}",
            f"- CPU Usage: {diagnostics['system_health'].get('cpu_percent', 0):.1f}%",
            f"- Memory Usage: {diagnostics['system_health'].get('memory_percent', 0):.1f}%",
            f"- EQ12 Processes: {diagnostics['system_health'].get('eq12_processes', 0)}",
            "",
            "## AI Models Status",
        ]
        
        for model_name, status in diagnostics.get('ai_models_status', {}).items():
            report_lines.append(f"- {model_name}: {status.get('status', 'unknown')} (accuracy: {status.get('accuracy', 0):.1%})")
        
        report_lines.extend([
            "",
            "## Recent Activity",
            f"- Total Log Files: {diagnostics['log_analysis'].get('total_logs', 0)}",
            f"- Errors Found: {diagnostics['log_analysis'].get('error_count', 0)}",
            f"- Warnings Found: {diagnostics['log_analysis'].get('warning_count', 0)}",
            "",
            "## Recommendations",
        ])
        
        for rec in diagnostics.get('recommendations', []):
            report_lines.append(f"- {rec}")
        
        report_content = "\n".join(report_lines)
        
        # Save report
        report_file = self.logs_dir / f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        self.logger.info(f" System report saved: {report_file}")
        
        return report_content


def main():
    parser = argparse.ArgumentParser(description="EQ12 System Management Suite")
    parser.add_argument("--workspace", default="C:/EQ12", help="EQ12 workspace path")
    parser.add_argument("--action", choices=[
        "health-check", "diagnostics", "auto-repair", "monitor", "report"
    ], default="health-check", help="Action to perform")
    parser.add_argument("--interval", type=int, default=300, help="Monitoring interval in seconds")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Initialize system manager
    manager = EQ12SystemManager(args.workspace)
    
    if args.action == "health-check":
        health_data = manager.get_system_health()
        print(json.dumps(health_data, indent=2))
        
    elif args.action == "diagnostics":
        diagnostics = manager.run_system_diagnostics()
        print(json.dumps(diagnostics, indent=2))
        
    elif args.action == "auto-repair":
        repair_results = manager.auto_repair_system()
        print(json.dumps(repair_results, indent=2))
        
    elif args.action == "monitor":
        manager.run_continuous_monitoring(args.interval)
        
    elif args.action == "report":
        report = manager.generate_system_report()
        print(report)


if __name__ == "__main__":
    main()