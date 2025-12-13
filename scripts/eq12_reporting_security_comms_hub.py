#!/usr/bin/env python3
"""
EQ12 Reporting, Security & Communication Hub
Unified system for monitoring, protecting, and communicating across the EQ12 ecosystem.
"""

import asyncio
import json
import logging
import os
import smtplib
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMimeMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
import requests
import psutil
from cryptography.fernet import Fernet
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\EQ12\\logs\\reporting_security_comms.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EQ12Hub:
    """Unified Reporting, Security, and Communication Hub"""

    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.config_path = self.workspace_path / "configs" / "hub_config.json"
        self.db_path = self.workspace_path / "data" / "eq12_hub.db"
        self.reports_path = self.workspace_path / "reports"
        self.logs_path = self.workspace_path / "logs"
        
        # Ensure directories exist
        for path in [self.reports_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        self.config = self.load_config()
        self.init_database()
        
        # Security and monitoring state
        self.last_health_check = None
        self.security_alerts = []
        self.performance_metrics = {}
        
        logger.info("EQ12 Hub initialized successfully")

    def load_config(self) -> Dict:
        """Load configuration with secure defaults"""
        default_config = {
            "telegram": {
                "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
                "chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
                "enabled": bool(os.getenv("TELEGRAM_BOT_TOKEN"))
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": os.getenv("EMAIL_USERNAME", ""),
                "password": os.getenv("EMAIL_PASSWORD", ""),
                "enabled": bool(os.getenv("EMAIL_USERNAME"))
            },
            "security": {
                "max_cpu_percent": 90,
                "max_memory_percent": 90,
                "max_disk_percent": 95,
                "alert_threshold": 3,
                "audit_interval": 3600  # 1 hour
            },
            "reporting": {
                "daily_report_time": "09:00",
                "weekly_report_day": "sunday",
                "retention_days": 30
            },
            "communication": {
                "voice_alerts": True,
                "priority_channels": ["telegram", "voice"],
                "notification_cooldown": 300  # 5 minutes
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
        
        return default_config

    def init_database(self):
        """Initialize SQLite database for hub operations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # System metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        cpu_percent REAL,
                        memory_percent REAL,
                        disk_percent REAL,
                        health_score REAL,
                        active_processes INTEGER
                    )
                ''')
                
                # Security events table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS security_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        description TEXT,
                        resolved BOOLEAN DEFAULT FALSE
                    )
                ''')
                
                # Communication log table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS communication_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        channel TEXT NOT NULL,
                        message_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        content TEXT
                    )
                ''')
                
                # Reports archive table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reports_archive (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        report_type TEXT NOT NULL,
                        file_path TEXT,
                        summary TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    # ===============================
    # REPORTING SYSTEM
    # ===============================
    
    def collect_system_metrics(self) -> Dict:
        """Collect comprehensive system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')
            
            # Count active EQ12 processes
            active_processes = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if any('eq12' in str(item).lower() for item in proc.info['cmdline'] or []):
                        active_processes += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Calculate health score
            health_factors = {
                'cpu': max(0, 1 - (cpu_percent / 100)),
                'memory': max(0, 1 - (memory.percent / 100)),
                'disk': max(0, 1 - (disk.percent / 100)),
                'processes': min(1, active_processes / 5)  # Expect ~5 EQ12 processes
            }
            health_score = sum(health_factors.values()) / len(health_factors)
            
            metrics = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'health_score': health_score,
                'active_processes': active_processes,
                'memory_available_gb': memory.available / (1024**3),
                'disk_free_gb': disk.free / (1024**3)
            }
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO system_metrics 
                    (timestamp, cpu_percent, memory_percent, disk_percent, health_score, active_processes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    metrics['timestamp'], cpu_percent, memory.percent, 
                    disk.percent, health_score, active_processes
                ))
                conn.commit()
            
            self.performance_metrics = metrics
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}

    def generate_daily_report(self) -> Dict:
        """Generate comprehensive daily report"""
        try:
            # Collect current metrics
            current_metrics = self.collect_system_metrics()
            
            # Get 24-hour historical data
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                yesterday = datetime.now() - timedelta(days=1)
                cursor.execute('''
                    SELECT * FROM system_metrics 
                    WHERE timestamp > ? 
                    ORDER BY timestamp DESC
                ''', (yesterday.isoformat(),))
                
                historical_data = cursor.fetchall()
            
            # Calculate aggregates
            if historical_data:
                avg_cpu = sum(row[2] for row in historical_data) / len(historical_data)
                avg_memory = sum(row[3] for row in historical_data) / len(historical_data)
                avg_health = sum(row[5] for row in historical_data) / len(historical_data)
                max_cpu = max(row[2] for row in historical_data)
                max_memory = max(row[3] for row in historical_data)
            else:
                avg_cpu = avg_memory = avg_health = max_cpu = max_memory = 0
            
            # Check EQ12 services status
            services_status = self.check_eq12_services()
            
            report = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'report_type': 'daily',
                'current_metrics': current_metrics,
                'aggregates': {
                    'avg_cpu_24h': round(avg_cpu, 2),
                    'avg_memory_24h': round(avg_memory, 2),
                    'avg_health_24h': round(avg_health, 3),
                    'max_cpu_24h': round(max_cpu, 2),
                    'max_memory_24h': round(max_memory, 2)
                },
                'services_status': services_status,
                'recommendations': self.generate_recommendations(current_metrics)
            }
            
            # Save report
            report_file = self.reports_path / f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Archive in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO reports_archive (timestamp, report_type, file_path, summary)
                    VALUES (?, ?, ?, ?)
                ''', (
                    report['timestamp'], 'daily', str(report_file),
                    f"Health: {current_metrics.get('health_score', 0):.2f}, CPU: {current_metrics.get('cpu_percent', 0):.1f}%"
                ))
                conn.commit()
            
            logger.info(f"Daily report generated: {report_file}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate daily report: {e}")
            return {}

    def check_eq12_services(self) -> Dict:
        """Check status of EQ12 services"""
        services = {
            'web_interface': {'port': 8080, 'status': 'unknown'},
            'system_manager': {'process': 'eq12_system_manager.py', 'status': 'unknown'},
            'betting_suite': {'process': 'eq12_betting_suite.py', 'status': 'unknown'},
            'api_server': {'port': 8000, 'status': 'unknown'}
        }
        
        # Check web interfaces by port
        for service, config in services.items():
            if 'port' in config:
                try:
                    response = requests.get(f"http://localhost:{config['port']}/health", timeout=5)
                    services[service]['status'] = 'running' if response.status_code == 200 else 'error'
                except:
                    services[service]['status'] = 'stopped'
        
        # Check processes
        running_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'eq12' in cmdline.lower():
                    running_processes.append(cmdline)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        for service, config in services.items():
            if 'process' in config:
                is_running = any(config['process'] in proc for proc in running_processes)
                services[service]['status'] = 'running' if is_running else 'stopped'
        
        return services

    def generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generate AI-driven recommendations based on metrics"""
        recommendations = []
        
        if metrics.get('cpu_percent', 0) > 85:
            recommendations.append(" High CPU usage detected. Consider reducing background processes or upgrading hardware.")
        
        if metrics.get('memory_percent', 0) > 90:
            recommendations.append(" Memory usage critical. Restart memory-intensive processes or upgrade to 64GB RAM.")
        
        if metrics.get('disk_percent', 0) > 90:
            recommendations.append(" Disk space low. Run log cleanup and consider archive older data.")
        
        if metrics.get('health_score', 1) < 0.7:
            recommendations.append(" System health degraded. Run comprehensive diagnostics and consider auto-repair.")
        
        if metrics.get('active_processes', 0) < 3:
            recommendations.append(" Fewer EQ12 processes than expected. Check if all services are running.")
        
        return recommendations

    # ===============================
    # SECURITY SYSTEM
    # ===============================
    
    def security_audit(self) -> Dict:
        """Perform comprehensive security audit"""
        audit_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'checks': {},
            'alerts': [],
            'overall_status': 'secure'
        }
        
        try:
            # Check file permissions
            audit_results['checks']['file_permissions'] = self.check_file_permissions()
            
            # Check API key security
            audit_results['checks']['api_keys'] = self.check_api_key_security()
            
            # Check network connections
            audit_results['checks']['network'] = self.check_network_security()
            
            # Check process integrity
            audit_results['checks']['processes'] = self.check_process_integrity()
            
            # Check system vulnerabilities
            audit_results['checks']['vulnerabilities'] = self.check_system_vulnerabilities()
            
            # Determine overall status
            critical_issues = sum(1 for check in audit_results['checks'].values() 
                                if check.get('status') == 'critical')
            
            if critical_issues > 0:
                audit_results['overall_status'] = 'critical'
            elif any(check.get('status') == 'warning' for check in audit_results['checks'].values()):
                audit_results['overall_status'] = 'warning'
            
            # Log security events
            if audit_results['alerts']:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    for alert in audit_results['alerts']:
                        cursor.execute('''
                            INSERT INTO security_events (timestamp, event_type, severity, description)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            audit_results['timestamp'], 'audit', 
                            alert['severity'], alert['message']
                        ))
                    conn.commit()
            
            logger.info(f"Security audit completed: {audit_results['overall_status']}")
            return audit_results
            
        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            audit_results['overall_status'] = 'error'
            return audit_results

    def check_file_permissions(self) -> Dict:
        """Check critical file permissions"""
        try:
            critical_files = [
                self.workspace_path / "configs" / ".env",
                self.workspace_path / "scripts" / "eq12_api_key_manager.py",
                self.db_path
            ]
            
            issues = []
            for file_path in critical_files:
                if file_path.exists():
                    # Check if file is readable by others (basic check)
                    stat = file_path.stat()
                    if stat.st_mode & 0o044:  # World or group readable
                        issues.append(f"File {file_path.name} may be too permissive")
            
            return {
                'status': 'warning' if issues else 'ok',
                'issues': issues,
                'checked_files': len(critical_files)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def check_api_key_security(self) -> Dict:
        """Check API key security and rotation status"""
        try:
            env_file = self.workspace_path / "configs" / ".env"
            if not env_file.exists():
                return {'status': 'warning', 'message': 'No .env file found'}
            
            # Check file age
            file_age = datetime.now() - datetime.fromtimestamp(env_file.stat().st_mtime)
            
            issues = []
            if file_age.days > 30:
                issues.append("API keys haven't been rotated in 30+ days")
            
            # Check for plaintext keys (basic pattern matching)
            with open(env_file, 'r') as f:
                content = f.read()
                if 'password' in content.lower() or 'secret' in content.lower():
                    if '=' in content and not content.startswith('enc:'):
                        issues.append("Potential plaintext secrets detected")
            
            return {
                'status': 'warning' if issues else 'ok',
                'issues': issues,
                'file_age_days': file_age.days
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def check_network_security(self) -> Dict:
        """Check network connections and exposed services"""
        try:
            # Get listening ports
            listening_ports = []
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == psutil.CONN_LISTEN:
                    listening_ports.append(conn.laddr.port)
            
            # Expected EQ12 ports
            expected_ports = [8080, 8000]
            unexpected_ports = [port for port in listening_ports 
                              if port not in expected_ports and port > 1024]
            
            issues = []
            if len(unexpected_ports) > 5:
                issues.append(f"Many unexpected listening ports: {unexpected_ports[:5]}...")
            
            return {
                'status': 'warning' if issues else 'ok',
                'listening_ports': listening_ports,
                'unexpected_ports': unexpected_ports,
                'issues': issues
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def check_process_integrity(self) -> Dict:
        """Check for suspicious processes"""
        try:
            eq12_processes = []
            suspicious_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'username']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'eq12' in cmdline.lower():
                        eq12_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline
                        })
                    
                    # Basic suspicious activity detection
                    if any(keyword in cmdline.lower() for keyword in ['hack', 'exploit', 'backdoor']):
                        suspicious_processes.append(proc.info)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                'status': 'critical' if suspicious_processes else 'ok',
                'eq12_processes': len(eq12_processes),
                'suspicious_processes': suspicious_processes
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def check_system_vulnerabilities(self) -> Dict:
        """Check for basic system vulnerabilities"""
        try:
            issues = []
            
            # Check Windows Update status (basic)
            try:
                result = subprocess.run(['powershell', '-Command', 
                    'Get-WindowsUpdate -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count'],
                    capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and result.stdout.strip():
                    pending_updates = int(result.stdout.strip())
                    if pending_updates > 0:
                        issues.append(f"{pending_updates} pending Windows updates")
            except:
                issues.append("Could not check Windows Update status")
            
            # Check PowerShell execution policy
            try:
                result = subprocess.run(['powershell', '-Command', 'Get-ExecutionPolicy'],
                    capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    policy = result.stdout.strip()
                    if policy == 'Unrestricted':
                        issues.append("PowerShell execution policy is unrestricted")
            except:
                pass
            
            return {
                'status': 'warning' if issues else 'ok',
                'issues': issues
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    # ===============================
    # COMMUNICATION SYSTEM
    # ===============================
    
    async def send_telegram_message(self, message: str, priority: str = "normal") -> bool:
        """Send message via Telegram bot"""
        if not self.config['telegram']['enabled']:
            logger.warning("Telegram not configured, skipping message")
            return False
        
        try:
            # Add priority indicators
            if priority == "critical":
                message = f" CRITICAL: {message}"
            elif priority == "warning":
                message = f" WARNING: {message}"
            elif priority == "info":
                message = f" INFO: {message}"
            else:
                message = f" {message}"
            
            url = f"https://api.telegram.org/bot{self.config['telegram']['bot_token']}/sendMessage"
            data = {
                'chat_id': self.config['telegram']['chat_id'],
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=10)
            success = response.status_code == 200
            
            # Log communication
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO communication_log (timestamp, channel, message_type, status, content)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    datetime.now(timezone.utc).isoformat(),
                    'telegram', priority, 'success' if success else 'failed', message
                ))
                conn.commit()
            
            if success:
                logger.info("Telegram message sent successfully")
            else:
                logger.error(f"Telegram message failed: {response.text}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def send_email_report(self, report: Dict, subject: str = "EQ12 Daily Report") -> bool:
        """Send email report"""
        if not self.config['email']['enabled']:
            logger.warning("Email not configured, skipping report")
            return False
        
        try:
            # Create email content
            msg = MIMimeMultipart()
            msg['From'] = self.config['email']['username']
            msg['To'] = self.config['email']['username']  # Send to self
            msg['Subject'] = subject
            
            # Format report as HTML
            html_content = self.format_report_html(report)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info("Email report sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email report: {e}")
            return False

    def format_report_html(self, report: Dict) -> str:
        """Format report as HTML for email"""
        current = report.get('current_metrics', {})
        aggregates = report.get('aggregates', {})
        services = report.get('services_status', {})
        recommendations = report.get('recommendations', [])
        
        html = f"""
        <html>
        <body>
            <h2> EQ12 Daily Report</h2>
            <p><strong>Generated:</strong> {report.get('timestamp', 'Unknown')}</p>
            
            <h3> Current System Status</h3>
            <ul>
                <li>Health Score: {current.get('health_score', 0):.2%}</li>
                <li>CPU Usage: {current.get('cpu_percent', 0):.1f}%</li>
                <li>Memory Usage: {current.get('memory_percent', 0):.1f}%</li>
                <li>Disk Usage: {current.get('disk_percent', 0):.1f}%</li>
                <li>Active Processes: {current.get('active_processes', 0)}</li>
            </ul>
            
            <h3> 24-Hour Averages</h3>
            <ul>
                <li>Average CPU: {aggregates.get('avg_cpu_24h', 0):.1f}%</li>
                <li>Average Memory: {aggregates.get('avg_memory_24h', 0):.1f}%</li>
                <li>Average Health: {aggregates.get('avg_health_24h', 0):.2%}</li>
            </ul>
            
            <h3> Service Status</h3>
            <ul>
        """
        
        for service, status in services.items():
            status_emoji = "" if status.get('status') == 'running' else ""
            html += f"<li>{status_emoji} {service}: {status.get('status', 'unknown')}</li>"
        
        html += "</ul>"
        
        if recommendations:
            html += "<h3> Recommendations</h3><ul>"
            for rec in recommendations:
                html += f"<li>{rec}</li>"
            html += "</ul>"
        
        html += """
            <p><em>Generated by EQ12 Autonomous Intelligence System</em></p>
        </body>
        </html>
        """
        
        return html

    def speak_alert(self, message: str) -> bool:
        """Speak alert using Windows TTS"""
        if not self.config['communication']['voice_alerts']:
            return False
        
        try:
            # Use PowerShell for TTS
            ps_command = f'''
            Add-Type -AssemblyName System.Speech;
            $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer;
            $speak.Speak("{message.replace('"', '')}")
            '''
            
            subprocess.run(['powershell', '-Command', ps_command], 
                         timeout=30, capture_output=True)
            
            logger.info("Voice alert delivered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deliver voice alert: {e}")
            return False

    async def broadcast_alert(self, message: str, priority: str = "normal") -> Dict:
        """Broadcast alert across all configured channels"""
        results = {}
        
        # Telegram
        if 'telegram' in self.config['communication']['priority_channels']:
            results['telegram'] = await self.send_telegram_message(message, priority)
        
        # Voice (for critical alerts)
        if priority == 'critical' and 'voice' in self.config['communication']['priority_channels']:
            results['voice'] = self.speak_alert(message)
        
        # Email (for daily reports or critical issues)
        if priority in ['critical', 'daily_report']:
            results['email'] = self.send_email_report({'summary': message}, f"EQ12 {priority.title()} Alert")
        
        return results

    # ===============================
    # MAIN CONTROL LOOP
    # ===============================
    
    async def monitoring_loop(self):
        """Main monitoring and response loop"""
        logger.info("Starting EQ12 Hub monitoring loop")
        
        while True:
            try:
                # Collect system metrics
                metrics = self.collect_system_metrics()
                
                # Check for alerts
                alerts = []
                
                # CPU alert
                if metrics.get('cpu_percent', 0) > self.config['security']['max_cpu_percent']:
                    alerts.append({
                        'severity': 'warning',
                        'message': f"High CPU usage: {metrics['cpu_percent']:.1f}%"
                    })
                
                # Memory alert
                if metrics.get('memory_percent', 0) > self.config['security']['max_memory_percent']:
                    alerts.append({
                        'severity': 'critical',
                        'message': f"Critical memory usage: {metrics['memory_percent']:.1f}%"
                    })
                
                # Health score alert
                if metrics.get('health_score', 1) < 0.5:
                    alerts.append({
                        'severity': 'critical',
                        'message': f"System health critical: {metrics['health_score']:.2%}"
                    })
                
                # Process count alert
                if metrics.get('active_processes', 0) < 2:
                    alerts.append({
                        'severity': 'warning',
                        'message': f"Low EQ12 process count: {metrics['active_processes']}"
                    })
                
                # Send alerts
                for alert in alerts:
                    await self.broadcast_alert(alert['message'], alert['severity'])
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    def schedule_reports(self):
        """Schedule automated reports"""
        # Daily report
        schedule.every().day.at(self.config['reporting']['daily_report_time']).do(
            self.run_daily_report
        )
        
        # Security audit (hourly)
        schedule.every().hour.do(self.run_security_audit)
        
        # Weekly cleanup
        schedule.every().sunday.at("02:00").do(self.cleanup_old_data)

    def run_daily_report(self):
        """Generate and send daily report"""
        try:
            report = self.generate_daily_report()
            
            # Create summary for Telegram
            current = report.get('current_metrics', {})
            summary = f"""
 *EQ12 Daily Report*

 Health Score: {current.get('health_score', 0):.2%}
 CPU: {current.get('cpu_percent', 0):.1f}%
 Memory: {current.get('memory_percent', 0):.1f}%
 Disk: {current.get('disk_percent', 0):.1f}%
 Processes: {current.get('active_processes', 0)}

{len(report.get('recommendations', []))} recommendations available.
            """
            
            # Send via Telegram
            asyncio.create_task(self.broadcast_alert(summary, 'daily_report'))
            
        except Exception as e:
            logger.error(f"Failed to run daily report: {e}")

    def run_security_audit(self):
        """Run security audit and send alerts if needed"""
        try:
            audit = self.security_audit()
            
            if audit['overall_status'] in ['warning', 'critical']:
                summary = f" Security Status: {audit['overall_status'].upper()}"
                if audit['alerts']:
                    summary += f"\n{len(audit['alerts'])} issues detected"
                
                asyncio.create_task(self.broadcast_alert(summary, audit['overall_status']))
                
        except Exception as e:
            logger.error(f"Failed to run security audit: {e}")

    def cleanup_old_data(self):
        """Clean up old logs and reports"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config['reporting']['retention_days'])
            
            # Clean database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM system_metrics WHERE timestamp < ?', (cutoff_date.isoformat(),))
                cursor.execute('DELETE FROM security_events WHERE timestamp < ?', (cutoff_date.isoformat(),))
                cursor.execute('DELETE FROM communication_log WHERE timestamp < ?', (cutoff_date.isoformat(),))
                conn.commit()
            
            # Clean log files
            for log_file in self.logs_path.glob("*.log"):
                if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                    log_file.unlink()
            
            logger.info("Data cleanup completed")
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")

    async def run_hub(self):
        """Main entry point for the hub"""
        logger.info(" Starting EQ12 Reporting, Security & Communication Hub")
        
        # Schedule reports
        self.schedule_reports()
        
        # Send startup notification
        await self.broadcast_alert("EQ12 Hub started successfully", "info")
        
        # Run monitoring loop
        await self.monitoring_loop()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Reporting, Security & Communication Hub")
    parser.add_argument("--workspace", default="C:\\EQ12", help="Workspace path")
    parser.add_argument("--report-only", action="store_true", help="Generate report and exit")
    parser.add_argument("--security-audit", action="store_true", help="Run security audit and exit")
    parser.add_argument("--test-comms", action="store_true", help="Test communication channels")
    parser.add_argument("--daemon", action="store_true", help="Run as background daemon")
    
    args = parser.parse_args()
    
    hub = EQ12Hub(args.workspace)
    
    if args.report_only:
        report = hub.generate_daily_report()
        print(json.dumps(report, indent=2))
        return 0
    
    if args.security_audit:
        audit = hub.security_audit()
        print(json.dumps(audit, indent=2))
        return 0
    
    if args.test_comms:
        async def test():
            await hub.broadcast_alert("Test message from EQ12 Hub", "info")
        asyncio.run(test())
        return 0
    
    if args.daemon:
        try:
            asyncio.run(hub.run_hub())
        except KeyboardInterrupt:
            logger.info("Hub shutdown requested")
        except Exception as e:
            logger.error(f"Hub failed: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())