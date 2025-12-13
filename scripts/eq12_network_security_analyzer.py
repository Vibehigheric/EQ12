#!/usr/bin/env python3
"""
 EQ12 NETWORK SECURITY LOG ANALYZER & DASHBOARD
Advanced security log parsing with anomaly detection and visual analytics

Created: November 7, 2025
Author: EQ12 Network Security Team
Purpose: Parse security logs, detect anomalies, create visual dashboards
Classification: NETWORK SECURITY - OPERATIONAL INTELLIGENCE
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import re
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
import ipaddress
import geoip2.database
import argparse
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("EQ12_SECURITY_ANALYZER")


class SecurityLogAnalyzer:
    """Advanced security log analyzer with anomaly detection"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.security_path = self.workspace_path / "security_analytics"
        self.security_path.mkdir(parents=True, exist_ok=True)
        
        self.dashboard_path = self.workspace_path / "dashboard"
        self.dashboard_path.mkdir(parents=True, exist_ok=True)
        
        # Security patterns for log parsing
        self.patterns = {
            'firewall_block': re.compile(r'BLOCK.*SRC=(\d+\.\d+\.\d+\.\d+).*DPT=(\d+)'),
            'ssh_fail': re.compile(r'Failed password.*from (\d+\.\d+\.\d+\.\d+).*port (\d+)'),
            'web_attack': re.compile(r'(\d+\.\d+\.\d+\.\d+).*"(GET|POST).*(\d{3})'),
            'intrusion_attempt': re.compile(r'INTRUSION.*SRC=(\d+\.\d+\.\d+\.\d+).*TYPE=(.+)'),
            'malware_detection': re.compile(r'MALWARE.*FILE=(.+).*THREAT=(.+)'),
            'timestamp': re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
        }
        
        self.anomaly_data = {
            'attack_sources': Counter(),
            'blocked_ports': Counter(),
            'attack_types': Counter(),
            'hourly_attacks': defaultdict(int),
            'geographic_attacks': defaultdict(int),
            'failed_logins': Counter(),
            'malware_threats': Counter()
        }
        
        log.info(" EQ12 Security Log Analyzer initialized")

    def generate_sample_security_logs(self) -> str:
        """Generate realistic sample security logs for demonstration"""
        
        sample_logs = []
        base_time = datetime.now() - timedelta(days=7)
        
        # Common attack sources (using safe test IPs)
        attack_ips = [
            "203.0.113.10", "198.51.100.20", "192.0.2.30", "203.0.113.40",
            "198.51.100.50", "192.0.2.60", "203.0.113.70", "198.51.100.80"
        ]
        
        # Generate firewall logs
        for i in range(1000):
            timestamp = base_time + timedelta(minutes=i * 7)
            ip = np.random.choice(attack_ips)
            port = np.random.choice([22, 80, 443, 3389, 21, 23, 25, 53, 135, 445])
            
            sample_logs.append(
                f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
                f"FIREWALL: BLOCK SRC={ip} DST=10.0.1.100 DPT={port} "
                f"PROTO=TCP LEN=40"
            )
        
        # Generate SSH attack logs
        for i in range(300):
            timestamp = base_time + timedelta(minutes=i * 15)
            ip = np.random.choice(attack_ips)
            port = np.random.choice([22, 2222])
            
            sample_logs.append(
                f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
                f"SSH: Failed password for admin from {ip} port {port} ssh2"
            )
        
        # Generate web attack logs
        for i in range(500):
            timestamp = base_time + timedelta(minutes=i * 10)
            ip = np.random.choice(attack_ips)
            method = np.random.choice(["GET", "POST"])
            status = np.random.choice([403, 404, 500, 200])
            path = np.random.choice([
                "/admin", "/wp-admin", "/phpmyadmin", "/shell.php",
                "/config.php", "/login.php", "/admin.php", "/backup.zip"
            ])
            
            sample_logs.append(
                f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
                f"WEB: {ip} \"{method} {path} HTTP/1.1\" {status} 1234"
            )
        
        # Generate intrusion detection logs
        for i in range(200):
            timestamp = base_time + timedelta(minutes=i * 20)
            ip = np.random.choice(attack_ips)
            attack_type = np.random.choice([
                "SQL_INJECTION", "XSS_ATTEMPT", "DIRECTORY_TRAVERSAL",
                "BRUTE_FORCE", "PORT_SCAN", "DDoS_ATTEMPT"
            ])
            
            sample_logs.append(
                f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
                f"IDS: INTRUSION DETECTED SRC={ip} TYPE={attack_type} "
                f"SEVERITY=HIGH"
            )
        
        # Generate malware detection logs
        for i in range(50):
            timestamp = base_time + timedelta(hours=i * 3)
            filename = np.random.choice([
                "trojan.exe", "malware.dll", "virus.scr", "backdoor.bat",
                "keylogger.exe", "ransomware.zip", "spyware.doc"
            ])
            threat = np.random.choice([
                "Trojan.Win32.Agent", "Backdoor.Win32.Remote", "Virus.Boot.Sector",
                "Ransomware.Win32.Locker", "Spyware.Win32.KeyLog"
            ])
            
            sample_logs.append(
                f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
                f"ANTIVIRUS: MALWARE DETECTED FILE={filename} THREAT={threat} "
                f"ACTION=QUARANTINED"
            )
        
        # Save sample logs
        log_file = self.security_path / "sample_security_logs.txt"
        with open(log_file, 'w') as f:
            for log_entry in sorted(sample_logs):
                f.write(log_entry + "\n")
        
        log.info(f" Generated {len(sample_logs)} sample security log entries")
        return str(log_file)

    def parse_security_logs(self, log_file_path: str) -> Dict[str, Any]:
        """Parse security logs and extract threat intelligence"""
        
        log.info(f" Parsing security logs from: {log_file_path}")
        
        with open(log_file_path, 'r') as f:
            logs = f.readlines()
        
        parsed_data = []
        
        for line in logs:
            entry = {"raw_log": line.strip(), "timestamp": None, "event_type": "unknown"}
            
            # Extract timestamp
            ts_match = self.patterns['timestamp'].search(line)
            if ts_match:
                entry["timestamp"] = datetime.strptime(ts_match.group(1), '%Y-%m-%d %H:%M:%S')
            
            # Parse firewall blocks
            fw_match = self.patterns['firewall_block'].search(line)
            if fw_match:
                entry.update({
                    "event_type": "firewall_block",
                    "source_ip": fw_match.group(1),
                    "destination_port": int(fw_match.group(2))
                })
                self.anomaly_data['attack_sources'][fw_match.group(1)] += 1
                self.anomaly_data['blocked_ports'][int(fw_match.group(2))] += 1
            
            # Parse SSH failures
            ssh_match = self.patterns['ssh_fail'].search(line)
            if ssh_match:
                entry.update({
                    "event_type": "ssh_failure",
                    "source_ip": ssh_match.group(1),
                    "port": int(ssh_match.group(2))
                })
                self.anomaly_data['failed_logins'][ssh_match.group(1)] += 1
            
            # Parse web attacks
            web_match = self.patterns['web_attack'].search(line)
            if web_match:
                entry.update({
                    "event_type": "web_request",
                    "source_ip": web_match.group(1),
                    "method": web_match.group(2),
                    "status_code": int(web_match.group(3))
                })
            
            # Parse intrusion attempts
            intrusion_match = self.patterns['intrusion_attempt'].search(line)
            if intrusion_match:
                entry.update({
                    "event_type": "intrusion_attempt",
                    "source_ip": intrusion_match.group(1),
                    "attack_type": intrusion_match.group(2)
                })
                self.anomaly_data['attack_types'][intrusion_match.group(2)] += 1
            
            # Parse malware detections
            malware_match = self.patterns['malware_detection'].search(line)
            if malware_match:
                entry.update({
                    "event_type": "malware_detection",
                    "filename": malware_match.group(1),
                    "threat_type": malware_match.group(2)
                })
                self.anomaly_data['malware_threats'][malware_match.group(2)] += 1
            
            # Track hourly patterns
            if entry["timestamp"]:
                hour = entry["timestamp"].hour
                self.anomaly_data['hourly_attacks'][hour] += 1
            
            parsed_data.append(entry)
        
        log.info(f" Parsed {len(parsed_data)} log entries")
        return {
            "parsed_logs": parsed_data,
            "anomaly_data": self.anomaly_data,
            "summary_stats": self._generate_summary_stats(parsed_data)
        }

    def _generate_summary_stats(self, parsed_logs: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics from parsed logs"""
        
        total_logs = len(parsed_logs)
        event_types = Counter([log.get('event_type', 'unknown') for log in parsed_logs])
        
        # Calculate time range
        timestamps = [log['timestamp'] for log in parsed_logs if log['timestamp']]
        if timestamps:
            time_range = {
                "start": min(timestamps).isoformat(),
                "end": max(timestamps).isoformat(),
                "duration_hours": (max(timestamps) - min(timestamps)).total_seconds() / 3600
            }
        else:
            time_range = {"start": None, "end": None, "duration_hours": 0}
        
        # Top threat sources
        source_ips = [log.get('source_ip') for log in parsed_logs if log.get('source_ip')]
        top_sources = Counter(source_ips).most_common(10)
        
        return {
            "total_events": total_logs,
            "event_type_distribution": dict(event_types),
            "time_range": time_range,
            "top_threat_sources": top_sources,
            "unique_source_ips": len(set(source_ips)),
            "analysis_timestamp": datetime.now().isoformat()
        }

    def detect_anomalies(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect security anomalies and patterns"""
        
        log.info(" Detecting security anomalies...")
        
        anomalies = {
            "high_volume_sources": [],
            "unusual_ports": [],
            "attack_spikes": [],
            "geographic_anomalies": [],
            "malware_trends": []
        }
        
        # Detect high-volume attack sources (threshold: >50 attacks)
        for ip, count in self.anomaly_data['attack_sources'].most_common(20):
            if count > 50:
                anomalies["high_volume_sources"].append({
                    "ip": ip,
                    "attack_count": count,
                    "severity": "HIGH" if count > 100 else "MEDIUM"
                })
        
        # Detect unusual port activity
        common_ports = {22, 80, 443, 21, 23, 25, 53, 135, 445, 3389}
        for port, count in self.anomaly_data['blocked_ports'].most_common(20):
            if port not in common_ports and count > 10:
                anomalies["unusual_ports"].append({
                    "port": port,
                    "block_count": count,
                    "severity": "MEDIUM"
                })
        
        # Detect hourly attack spikes
        avg_hourly = np.mean(list(self.anomaly_data['hourly_attacks'].values()))
        std_hourly = np.std(list(self.anomaly_data['hourly_attacks'].values()))
        threshold = avg_hourly + (2 * std_hourly)
        
        for hour, count in self.anomaly_data['hourly_attacks'].items():
            if count > threshold:
                anomalies["attack_spikes"].append({
                    "hour": hour,
                    "attack_count": count,
                    "severity": "HIGH" if count > avg_hourly + (3 * std_hourly) else "MEDIUM"
                })
        
        # Analyze malware trends
        if self.anomaly_data['malware_threats']:
            for threat, count in self.anomaly_data['malware_threats'].most_common(10):
                anomalies["malware_trends"].append({
                    "threat_type": threat,
                    "detection_count": count,
                    "severity": "HIGH" if count > 5 else "MEDIUM"
                })
        
        log.info(f" Detected {len(anomalies['high_volume_sources'])} high-volume sources")
        log.info(f" Detected {len(anomalies['unusual_ports'])} unusual port activities")
        log.info(f" Detected {len(anomalies['attack_spikes'])} attack spikes")
        
        return anomalies

    def create_security_dashboard(self, parsed_data: Dict[str, Any], anomalies: Dict[str, Any]) -> str:
        """Create interactive security dashboard"""
        
        log.info(" Creating interactive security dashboard...")
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                "Top Attack Sources", "Blocked Ports Distribution",
                "Hourly Attack Patterns", "Attack Types Distribution", 
                "Failed Login Attempts", "Malware Threat Types"
            ],
            specs=[
                [{"type": "bar"}, {"type": "pie"}],
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "pie"}]
            ]
        )
        
        # Top Attack Sources
        if self.anomaly_data['attack_sources']:
            top_sources = self.anomaly_data['attack_sources'].most_common(10)
            ips, counts = zip(*top_sources)
            fig.add_trace(
                go.Bar(x=list(ips), y=list(counts), name="Attack Sources",
                       marker_color='red', showlegend=False),
                row=1, col=1
            )
        
        # Blocked Ports Distribution
        if self.anomaly_data['blocked_ports']:
            top_ports = self.anomaly_data['blocked_ports'].most_common(8)
            ports, counts = zip(*top_ports)
            fig.add_trace(
                go.Pie(labels=[f"Port {p}" for p in ports], values=list(counts),
                       name="Blocked Ports", showlegend=False),
                row=1, col=2
            )
        
        # Hourly Attack Patterns
        if self.anomaly_data['hourly_attacks']:
            hours = list(range(24))
            attack_counts = [self.anomaly_data['hourly_attacks'].get(h, 0) for h in hours]
            fig.add_trace(
                go.Scatter(x=hours, y=attack_counts, mode='lines+markers',
                          name="Hourly Attacks", line=dict(color='orange'),
                          showlegend=False),
                row=2, col=1
            )
        
        # Attack Types Distribution
        if self.anomaly_data['attack_types']:
            attack_types = list(self.anomaly_data['attack_types'].keys())
            type_counts = list(self.anomaly_data['attack_types'].values())
            fig.add_trace(
                go.Bar(x=attack_types, y=type_counts, name="Attack Types",
                       marker_color='purple', showlegend=False),
                row=2, col=2
            )
        
        # Failed Login Attempts
        if self.anomaly_data['failed_logins']:
            top_failed = self.anomaly_data['failed_logins'].most_common(10)
            ips, counts = zip(*top_failed)
            fig.add_trace(
                go.Bar(x=list(ips), y=list(counts), name="Failed Logins",
                       marker_color='darkred', showlegend=False),
                row=3, col=1
            )
        
        # Malware Threat Types
        if self.anomaly_data['malware_threats']:
            threats = list(self.anomaly_data['malware_threats'].keys())
            threat_counts = list(self.anomaly_data['malware_threats'].values())
            fig.add_trace(
                go.Pie(labels=threats, values=threat_counts,
                       name="Malware Threats", showlegend=False),
                row=3, col=2
            )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text=" EQ12 Network Security Dashboard - Real-time Threat Analysis",
            title_x=0.5,
            showlegend=False
        )
        
        # Save dashboard
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dashboard_file = self.dashboard_path / f"security_dashboard_{timestamp}.html"
        
        fig.write_html(str(dashboard_file))
        
        log.info(f" Security dashboard created: {dashboard_file}")
        return str(dashboard_file)

    def generate_security_report(self, parsed_data: Dict[str, Any], 
                                anomalies: Dict[str, Any]) -> str:
        """Generate comprehensive security analysis report"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.security_path / f"security_analysis_report_{timestamp}.json"
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_id": f"EQ12-SEC-{timestamp}",
                "analyzer_version": "1.0.0"
            },
            "executive_summary": {
                "total_security_events": parsed_data["summary_stats"]["total_events"],
                "unique_threat_sources": parsed_data["summary_stats"]["unique_source_ips"],
                "high_priority_threats": len(anomalies["high_volume_sources"]),
                "unusual_activities": len(anomalies["unusual_ports"]),
                "risk_level": self._calculate_risk_level(anomalies)
            },
            "detailed_analysis": {
                "parsed_data": parsed_data,
                "detected_anomalies": anomalies,
                "threat_intelligence": self._generate_threat_intelligence(anomalies)
            },
            "recommendations": self._generate_security_recommendations(anomalies)
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        log.info(f" Security analysis report saved: {report_file}")
        return str(report_file)

    def _calculate_risk_level(self, anomalies: Dict[str, Any]) -> str:
        """Calculate overall risk level based on detected anomalies"""
        
        high_risk_indicators = 0
        medium_risk_indicators = 0
        
        for category in anomalies.values():
            if isinstance(category, list):
                for item in category:
                    if item.get('severity') == 'HIGH':
                        high_risk_indicators += 1
                    elif item.get('severity') == 'MEDIUM':
                        medium_risk_indicators += 1
        
        if high_risk_indicators >= 5:
            return "CRITICAL"
        elif high_risk_indicators >= 2 or medium_risk_indicators >= 10:
            return "HIGH"
        elif high_risk_indicators >= 1 or medium_risk_indicators >= 5:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_threat_intelligence(self, anomalies: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable threat intelligence"""
        
        return {
            "attack_pattern_analysis": {
                "coordinated_attacks": len(anomalies["high_volume_sources"]) > 3,
                "port_scanning_detected": len(anomalies["unusual_ports"]) > 5,
                "time_based_patterns": len(anomalies["attack_spikes"]) > 0
            },
            "threat_actor_indicators": {
                "persistent_sources": [
                    src for src in anomalies["high_volume_sources"] 
                    if src["attack_count"] > 100
                ],
                "advanced_techniques": len(anomalies["malware_trends"]) > 0
            },
            "infrastructure_insights": {
                "targeted_services": list(self.anomaly_data['blocked_ports'].keys())[:10],
                "attack_vectors": list(self.anomaly_data['attack_types'].keys())
            }
        }

    def _generate_security_recommendations(self, anomalies: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate security recommendations based on analysis"""
        
        recommendations = []
        
        if anomalies["high_volume_sources"]:
            recommendations.append({
                "priority": "HIGH",
                "category": "IP_BLOCKING",
                "action": "Implement automated IP blocking for high-volume attack sources",
                "details": f"Block {len(anomalies['high_volume_sources'])} identified threat sources"
            })
        
        if anomalies["unusual_ports"]:
            recommendations.append({
                "priority": "MEDIUM", 
                "category": "PORT_SECURITY",
                "action": "Review and secure unusual port activities",
                "details": f"Investigate {len(anomalies['unusual_ports'])} non-standard ports under attack"
            })
        
        if anomalies["attack_spikes"]:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "MONITORING",
                "action": "Implement time-based attack spike detection",
                "details": "Set up alerts for unusual hourly attack patterns"
            })
        
        if anomalies["malware_trends"]:
            recommendations.append({
                "priority": "HIGH",
                "category": "MALWARE_PROTECTION",
                "action": "Enhance malware detection and response capabilities",
                "details": f"Address {len(anomalies['malware_trends'])} different malware threat types"
            })
        
        recommendations.append({
            "priority": "ONGOING",
            "category": "CONTINUOUS_MONITORING",
            "action": "Implement continuous security log monitoring",
            "details": "Deploy automated log analysis with real-time alerting"
        })
        
        return recommendations


def main():
    parser = argparse.ArgumentParser(description=" EQ12 Network Security Log Analyzer")
    parser.add_argument("--action", choices=["generate-logs", "analyze", "dashboard", "full-analysis"], 
                       default="full-analysis", help="Action to perform")
    parser.add_argument("--log-file", help="Path to security log file")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    analyzer = SecurityLogAnalyzer(args.workspace)
    
    if args.action == "generate-logs":
        log_file = analyzer.generate_sample_security_logs()
        print(f" Sample security logs generated: {log_file}")
        
    elif args.action == "analyze":
        if not args.log_file:
            print(" --log-file required for analysis")
            return
        
        parsed_data = analyzer.parse_security_logs(args.log_file)
        anomalies = analyzer.detect_anomalies(parsed_data)
        report_file = analyzer.generate_security_report(parsed_data, anomalies)
        
        print(f" Security analysis complete: {report_file}")
        
    elif args.action == "dashboard":
        if not args.log_file:
            # Generate sample logs first
            log_file = analyzer.generate_sample_security_logs()
        else:
            log_file = args.log_file
        
        parsed_data = analyzer.parse_security_logs(log_file)
        anomalies = analyzer.detect_anomalies(parsed_data)
        dashboard_file = analyzer.create_security_dashboard(parsed_data, anomalies)
        
        print(f" Security dashboard created: {dashboard_file}")
        
    elif args.action == "full-analysis":
        print("" + "="*70)
        print(" EQ12 NETWORK SECURITY LOG ANALYZER")
        print("" + "="*70)
        
        # Generate sample logs
        log_file = analyzer.generate_sample_security_logs()
        
        # Parse and analyze
        parsed_data = analyzer.parse_security_logs(log_file)
        anomalies = analyzer.detect_anomalies(parsed_data)
        
        # Generate dashboard and report
        dashboard_file = analyzer.create_security_dashboard(parsed_data, anomalies)
        report_file = analyzer.generate_security_report(parsed_data, anomalies)
        
        # Display summary
        summary = parsed_data["summary_stats"]
        print(f"\n SECURITY ANALYSIS SUMMARY")
        print(f"    Total Security Events: {summary['total_events']:,}")
        print(f"    Unique Threat Sources: {summary['unique_source_ips']}")
        print(f"    High-Volume Attackers: {len(anomalies['high_volume_sources'])}")
        print(f"    Unusual Port Activities: {len(anomalies['unusual_ports'])}")
        print(f"    Attack Time Spikes: {len(anomalies['attack_spikes'])}")
        print(f"    Malware Threats: {len(anomalies['malware_trends'])}")
        
        print(f"\n TOP THREAT SOURCES:")
        for threat in anomalies["high_volume_sources"][:5]:
            print(f"    {threat['ip']} - {threat['attack_count']} attacks ({threat['severity']})")
        
        print(f"\n Dashboard: {dashboard_file}")
        print(f" Report: {report_file}")
        print("" + "="*70)


if __name__ == "__main__":
    main()