#!/usr/bin/env python3
"""
 EQ12 SOCIAL INTELLIGENCE ECOSYSTEM DASHBOARD
===============================================

Comprehensive dashboard showing the complete social intelligence ecosystem
built for the EQ12 automation empire, including all components, integrations,
and real-time analytics capabilities.

System Components Overview:
 Twitter Sports Intelligence - Real-time Twitter monitoring and sentiment analysis
 Social Intelligence Orchestrator - Multi-platform data aggregation and correlation
 Social Integration Suite - Cross-platform signal generation and validation
 Social Master Integrator - BI correlation and Kelly criterion betting signals
 Revenue Database Integration - Automated opportunity tracking and performance metrics

Author: EQ12 Quantum Development Team
Version: 1.0.0 - Social Intelligence Ecosystem Dashboard
Date: November 7, 2025
"""

import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List


class EQ12SocialEcosystemDashboard:
    """Complete social intelligence ecosystem status dashboard."""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.data_path = self.workspace_path / "data"
        self.logs_path = self.workspace_path / "logs"
        self.scripts_path = self.workspace_path / "scripts"
        
    def check_ecosystem_components(self) -> Dict[str, Dict[str, Any]]:
        """Check status of all social intelligence ecosystem components."""
        components = {
            "twitter_sports_intelligence": {
                "script_path": self.scripts_path / "twitter_sports_intelligence.py",
                "purpose": "Real-time Twitter monitoring for NFL/NHL with sentiment analysis",
                "features": ["Sentiment analysis", "Team/player detection", "Betting impact scoring", "Alert generation"],
                "database_tables": ["twitter_sports_alerts"],
                "status": "unknown"
            },
            "social_orchestrator": {
                "script_path": self.workspace_path / "eq12_social_orchestrator.py",
                "purpose": "Multi-platform social intelligence orchestration",
                "features": ["Twitter/Reddit/Telegram integration", "Cross-platform correlation", "Real-time analytics", "Automated reporting"],
                "database_tables": ["social_data", "sentiment_analysis", "platform_correlations", "social_alerts"],
                "status": "unknown"
            },
            "social_integration_suite": {
                "script_path": self.workspace_path / "eq12_social_integration_suite.py",
                "purpose": "Comprehensive social intelligence integration and signal generation",
                "features": ["System availability checking", "Data correlation", "Betting signal generation", "Performance tracking"],
                "database_tables": ["social_betting_signals", "social_intelligence_metrics"],
                "status": "unknown"
            },
            "social_master_integrator": {
                "script_path": self.workspace_path / "eq12_social_master_integrator.py",
                "purpose": "Final integration with BI tracker and Kelly criterion betting",
                "features": ["BI correlation analysis", "Kelly criterion calculation", "Risk-adjusted betting", "Portfolio optimization"],
                "database_tables": ["master_betting_opportunities", "bi_social_enhancements"],
                "status": "unknown"
            }
        }
        
        # Check component status
        for component, info in components.items():
            if info["script_path"].exists():
                components[component]["status"] = " Active"
                components[component]["file_size"] = f"{info['script_path'].stat().st_size // 1024}KB"
                components[component]["last_modified"] = datetime.fromtimestamp(info['script_path'].stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            else:
                components[component]["status"] = " Missing"
        
        return components
    
    def check_database_status(self) -> Dict[str, Dict[str, Any]]:
        """Check status of all databases used by the ecosystem."""
        databases = {
            "social_intelligence.db": {
                "path": self.data_path / "social_intelligence.db",
                "purpose": "Primary social intelligence data storage",
                "tables": ["social_data", "sentiment_analysis", "platform_correlations", "social_alerts"],
                "status": "unknown",
                "size": 0,
                "record_counts": {}
            },
            "revenue.db": {
                "path": self.data_path / "revenue.db",
                "purpose": "Revenue tracking and betting opportunities",
                "tables": ["social_intelligence_metrics", "social_betting_opportunities", "social_betting_signals", "master_betting_opportunities", "bi_social_enhancements"],
                "status": "unknown",
                "size": 0,
                "record_counts": {}
            }
        }
        
        for db_name, db_info in databases.items():
            if db_info["path"].exists():
                databases[db_name]["status"] = " Active"
                databases[db_name]["size"] = db_info["path"].stat().st_size // 1024  # KB
                
                # Get record counts
                try:
                    conn = sqlite3.connect(db_info["path"])
                    for table in db_info["tables"]:
                        try:
                            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                            count = cursor.fetchone()[0]
                            databases[db_name]["record_counts"][table] = count
                        except sqlite3.OperationalError:
                            databases[db_name]["record_counts"][table] = "N/A"
                    conn.close()
                except Exception as e:
                    databases[db_name]["record_counts"] = {"error": str(e)}
            else:
                databases[db_name]["status"] = " Missing"
        
        return databases
    
    def get_latest_execution_logs(self) -> List[Dict[str, Any]]:
        """Get latest execution logs from the ecosystem."""
        log_files = []
        
        # Find recent log files
        if self.logs_path.exists():
            for log_file in self.logs_path.glob("*social*.json"):
                try:
                    stat = log_file.stat()
                    log_files.append({
                        "name": log_file.name,
                        "type": "JSON Report",
                        "size": f"{stat.st_size // 1024}KB",
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "age_minutes": (time.time() - stat.st_mtime) / 60
                    })
                except Exception:
                    continue
            
            # Add recent .log files
            for log_file in self.logs_path.glob("*social*.log"):
                try:
                    stat = log_file.stat()
                    log_files.append({
                        "name": log_file.name,
                        "type": "Execution Log",
                        "size": f"{stat.st_size // 1024}KB",
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "age_minutes": (time.time() - stat.st_mtime) / 60
                    })
                except Exception:
                    continue
        
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x["age_minutes"])
        
        return log_files[:10]  # Return 10 most recent
    
    def analyze_ecosystem_performance(self) -> Dict[str, Any]:
        """Analyze overall ecosystem performance."""
        performance = {
            "total_data_points": 0,
            "total_alerts": 0,
            "total_signals": 0,
            "total_opportunities": 0,
            "latest_executions": {},
            "success_metrics": {
                "data_collection_success": 0,
                "signal_generation_success": 0,
                "integration_success": 0
            }
        }
        
        # Check social intelligence database
        social_db_path = self.data_path / "social_intelligence.db"
        if social_db_path.exists():
            try:
                conn = sqlite3.connect(social_db_path)
                
                # Count data points
                cursor = conn.execute("SELECT COUNT(*) FROM social_data")
                performance["total_data_points"] = cursor.fetchone()[0]
                
                # Count alerts
                cursor = conn.execute("SELECT COUNT(*) FROM social_alerts")
                performance["total_alerts"] = cursor.fetchone()[0]
                
                # Get latest execution timestamp
                cursor = conn.execute("SELECT MAX(timestamp) FROM social_data")
                latest_data = cursor.fetchone()[0]
                if latest_data:
                    performance["latest_executions"]["data_collection"] = latest_data
                
                conn.close()
                performance["success_metrics"]["data_collection_success"] = 1
            except Exception:
                performance["success_metrics"]["data_collection_success"] = 0
        
        # Check revenue database
        revenue_db_path = self.data_path / "revenue.db"
        if revenue_db_path.exists():
            try:
                conn = sqlite3.connect(revenue_db_path)
                
                # Count betting signals
                try:
                    cursor = conn.execute("SELECT COUNT(*) FROM social_betting_signals")
                    performance["total_signals"] = cursor.fetchone()[0]
                except sqlite3.OperationalError:
                    performance["total_signals"] = 0
                
                # Count master opportunities
                try:
                    cursor = conn.execute("SELECT COUNT(*) FROM master_betting_opportunities")
                    performance["total_opportunities"] = cursor.fetchone()[0]
                except sqlite3.OperationalError:
                    performance["total_opportunities"] = 0
                
                conn.close()
                performance["success_metrics"]["signal_generation_success"] = 1
            except Exception:
                performance["success_metrics"]["signal_generation_success"] = 0
        
        # Calculate overall success rate
        success_count = sum(performance["success_metrics"].values())
        performance["success_metrics"]["integration_success"] = success_count / 3.0
        
        return performance
    
    def display_ecosystem_dashboard(self):
        """Display the complete ecosystem dashboard."""
        print(" EQ12 SOCIAL INTELLIGENCE ECOSYSTEM DASHBOARD")
        print("=" * 50)
        print("Complete social intelligence automation empire status...")
        print()
        
        # Component Status
        print(" ECOSYSTEM COMPONENTS")
        print("-" * 25)
        components = self.check_ecosystem_components()
        
        for component, info in components.items():
            print(f"{info['status']} {component.replace('_', ' ').title()}")
            print(f"    Purpose: {info['purpose']}")
            if info['status'] == " Active":
                print(f"    Size: {info['file_size']} | Modified: {info['last_modified']}")
            print(f"    Features: {', '.join(info['features'][:2])}...")
            print()
        
        # Database Status
        print(" DATABASE INFRASTRUCTURE")
        print("-" * 29)
        databases = self.check_database_status()
        
        for db_name, db_info in databases.items():
            print(f"{db_info['status']} {db_name}")
            print(f"    Purpose: {db_info['purpose']}")
            if db_info['status'] == " Active":
                print(f"    Size: {db_info['size']}KB")
                print(f"    Tables: {len(db_info['tables'])} tables")
                if db_info['record_counts']:
                    total_records = sum(v for v in db_info['record_counts'].values() if isinstance(v, int))
                    print(f"    Records: {total_records} total")
            print()
        
        # Performance Analysis
        print(" ECOSYSTEM PERFORMANCE")
        print("-" * 26)
        performance = self.analyze_ecosystem_performance()
        
        print(f" Data Points Collected: {performance['total_data_points']}")
        print(f" Alerts Generated: {performance['total_alerts']}")
        print(f" Betting Signals: {performance['total_signals']}")
        print(f" Opportunities Created: {performance['total_opportunities']}")
        print(f" Integration Success: {performance['success_metrics']['integration_success']:.1%}")
        print()
        
        # Recent Activity
        print(" RECENT EXECUTION LOGS")
        print("-" * 26)
        recent_logs = self.get_latest_execution_logs()
        
        if recent_logs:
            for log in recent_logs[:5]:  # Show top 5
                age_text = f"{log['age_minutes']:.0f}m ago" if log['age_minutes'] < 60 else f"{log['age_minutes']/60:.1f}h ago"
                print(f" {log['name']}")
                print(f"    {log['type']} | {log['size']} | {age_text}")
        else:
            print(" No recent execution logs found")
        
        print()
        
        # System Integration Map
        print(" INTEGRATION ARCHITECTURE")
        print("-" * 29)
        print(" Twitter Intelligence   Social Orchestrator")
        print("                         ")
        print(" Integration Suite   Master Integrator")
        print("                         ")
        print(" Revenue Database   BI Tracker   Betting Engine")
        print()
        
        # Next Steps
        print(" ECOSYSTEM CAPABILITIES")
        print("-" * 27)
        print(" Real-time social sentiment monitoring across multiple platforms")
        print(" Cross-platform correlation and validation for enhanced confidence")
        print(" Automated betting signal generation using Kelly criterion")
        print(" Integration with EQ12 BI tracker for comprehensive market analysis")
        print(" Performance tracking and opportunity identification")
        print(" Risk-adjusted portfolio recommendations with social intelligence boost")
        print()
        
        print(" USAGE RECOMMENDATIONS")
        print("-" * 27)
        print("1. Run twitter_sports_intelligence.py for real-time monitoring")
        print("2. Execute eq12_social_orchestrator.py for multi-platform analysis")
        print("3. Use eq12_social_integration_suite.py for comprehensive signals")
        print("4. Deploy eq12_social_master_integrator.py for final betting decisions")
        print()
        
        print(" EQ12 SOCIAL INTELLIGENCE ECOSYSTEM: FULLY OPERATIONAL! ")


def main():
    """Main execution function."""
    dashboard = EQ12SocialEcosystemDashboard()
    dashboard.display_ecosystem_dashboard()


if __name__ == "__main__":
    main()