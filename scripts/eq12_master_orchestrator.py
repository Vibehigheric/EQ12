#!/usr/bin/env python3
"""
EQ12 Master Orchestrator - One-Click System Runner
Chains together all EQ12 components with automatic dashboard generation

This is the ultimate one-click runner that executes:
- Intelligence tracker
- Template market builder  
- Quantum revenue deployment
- Advanced revenue reporter
- Dashboard generation
"""

import json
import logging
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EQ12MasterOrchestrator:
    """Ultimate EQ12 system orchestrator for one-click execution"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12_BROKEN_20251122_210342"):
        self.workspace_path = Path(workspace_path)
        self.scripts_path = self.workspace_path / "scripts"
        self.logs_path = self.workspace_path / "logs"
        self.reports_path = self.workspace_path / "reports"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # System execution order and configuration
        self.execution_pipeline = [
            {
                "name": "Player Eligibility Gate",
                "script": "eq12_player_eligibility_gate.py",
                "description": "Enforce Strict Player Eligibility Rules",
                "args": [],
                "critical": True
            },
            {
                "name": "NBA Power Slip Generator",
                "script": "nba_power_slip_generator.py",
                "description": "Generate High-Confidence NBA Bets",
                "args": [],
                "critical": True
            },
            {
                "name": "Loganberry Inventory", 
                "script": "loganberry_inventory_manager.py",
                "description": "Manage Inventory Database",
                "args": [],
                "critical": False
            },
            {
                "name": "Legacy NBA Intelligence",
                "script": "eq12_master_nba_intelligence.py",
                "description": "Run Legacy NBA Intelligence System",
                "args": [],
                "critical": False
            }
        ]
        
        logger.info(" EQ12 Master Orchestrator initialized")

    async def execute_component(self, component: dict[str, Any]) -> dict[str, Any]:
        """Execute a single EQ12 component"""
        try:
            script_path = self.scripts_path / component["script"]
            
            if not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_path}")
            
            # Build command
            cmd = ["python", str(script_path)]
            if component["args"]:
                cmd.extend(component["args"])
            
            logger.info(f" Executing {component['name']}...")
            
            # Execute component
            start_time = datetime.now()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.scripts_path
            )
            
            # PRINT OUTPUT TO CONSOLE
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"STDERR: {result.stderr}")

            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "component": component["name"],
                "script": component["script"],
                "description": component["description"],
                "status": "success" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "execution_time": execution_time,
                "stdout_lines": len(result.stdout.split('\n')) if result.stdout else 0,
                "stderr_lines": len(result.stderr.split('\n')) if result.stderr else 0,
                "critical": component["critical"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f" {component['name']} execution failed: {e}")
            return {
                "component": component["name"],
                "script": component["script"],
                "status": "failed",
                "error": str(e),
                "critical": component["critical"],
                "timestamp": datetime.now().isoformat()
            }

    def create_master_dashboard_index(self, orchestration_results: list[dict[str, Any]]) -> str:
        """Create comprehensive dashboard index combining all reports"""
        try:
            successful_components = [r for r in orchestration_results if r["status"] == "success"]
            failed_components = [r for r in orchestration_results if r["status"] == "failed"]
            critical_failures = [r for r in failed_components if r.get("critical", False)]
            
            success_rate = (len(successful_components) / len(orchestration_results)) * 100
            
            # Find latest dashboard files
            dashboard_files = []
            for file_pattern in ["*dashboard*.html", "*report*.html"]:
                dashboard_files.extend(list(self.reports_path.glob(file_pattern)))
            
            # Sort by modification time
            dashboard_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            recent_dashboards = dashboard_files[:10]  # Top 10 most recent
            
            dashboard_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> EQ12 Master Control Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        .dashboard {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }}
        .status-overview {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .status-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        .status-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .status-success {{ color: #00ff88; }}
        .status-warning {{ color: #ffaa00; }}
        .status-error {{ color: #ff4444; }}
        .component-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .component-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
        }}
        .component-success {{
            border-left: 5px solid #00ff88;
        }}
        .component-failed {{
            border-left: 5px solid #ff4444;
        }}
        .component-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .component-title {{
            font-size: 1.3em;
            font-weight: bold;
        }}
        .component-status {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .status-success-badge {{
            background: #00ff88;
            color: black;
        }}
        .status-failed-badge {{
            background: #ff4444;
            color: white;
        }}
        .dashboards-section {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        .dashboard-links {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}
        .dashboard-link {{
            display: block;
            padding: 15px;
            background: rgba(0, 255, 136, 0.2);
            border-radius: 10px;
            text-decoration: none;
            color: white;
            transition: all 0.3s ease;
        }}
        .dashboard-link:hover {{
            background: rgba(0, 255, 136, 0.4);
            transform: translateY(-2px);
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1> EQ12 MASTER CONTROL DASHBOARD</h1>
            <h2>Ultimate Revenue Empire Orchestration</h2>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="status-overview">
            <div class="status-card">
                <div class="status-value status-success">{len(orchestration_results)}</div>
                <div>Total Components</div>
            </div>
            <div class="status-card">
                <div class="status-value status-success">{len(successful_components)}</div>
                <div>Successful</div>
            </div>
            <div class="status-card">
                <div class="status-value {'status-error' if failed_components else 'status-success'}">{len(failed_components)}</div>
                <div>Failed</div>
            </div>
            <div class="status-card">
                <div class="status-value {'status-error' if critical_failures else 'status-success'}">{len(critical_failures)}</div>
                <div>Critical Failures</div>
            </div>
            <div class="status-card">
                <div class="status-value status-success">{success_rate:.1f}%</div>
                <div>Success Rate</div>
            </div>
        </div>
        
        <div class="component-grid">
"""
            
            for result in orchestration_results:
                status_class = "component-success" if result["status"] == "success" else "component-failed"
                status_badge_class = "status-success-badge" if result["status"] == "success" else "status-failed-badge"
                
                dashboard_html += f"""
            <div class="component-card {status_class}">
                <div class="component-header">
                    <div class="component-title">{result['component']}</div>
                    <div class="component-status {status_badge_class}">{result['status'].upper()}</div>
                </div>
                <div>{result.get('description', 'No description available')}</div>
                <div style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                    <div>Script: {result.get('script', 'Unknown')}</div>
                    <div>Execution Time: {result.get('execution_time', 0):.2f}s</div>
                    {'<div style="color: #ff4444;">Critical Component</div>' if result.get('critical', False) else ''}
                </div>
            </div>
"""
            
            dashboard_html += f"""
        </div>
        
        <div class="dashboards-section">
            <h3> Available Dashboards & Reports</h3>
            <div class="dashboard-links">
"""
            
            for dashboard_file in recent_dashboards:
                relative_path = dashboard_file.relative_to(self.reports_path)
                file_name = dashboard_file.stem.replace('_', ' ').title()
                mod_time = datetime.fromtimestamp(dashboard_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                
                dashboard_html += f"""
                <a href="{relative_path}" class="dashboard-link">
                    <div style="font-weight: bold;">{file_name}</div>
                    <div style="font-size: 0.9em; opacity: 0.8;">Updated: {mod_time}</div>
                </a>
"""
            
            dashboard_html += f"""
            </div>
        </div>
        
        <div class="footer">
            <h3> EQ12 REVENUE EMPIRE STATUS</h3>
            <p>{' ALL SYSTEMS OPERATIONAL' if success_rate >= 80 else ' SOME SYSTEMS NEED ATTENTION'}</p>
            <p>{' Ready for maximum revenue generation' if not critical_failures else ' Critical components require immediate attention'}</p>
            <p>Next orchestration cycle: {(datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Save master dashboard
            dashboard_path = self.reports_path / f"eq12_master_dashboard_{self.timestamp}.html"
            dashboard_path.write_text(dashboard_html, encoding='utf-8')
            
            # Create latest version
            latest_dashboard = self.reports_path / "eq12_master_dashboard_latest.html"
            latest_dashboard.write_text(dashboard_html, encoding='utf-8')
            
            logger.info(f" Master dashboard created: {dashboard_path}")
            return str(dashboard_path)
            
        except Exception as e:
            logger.error(f" Master dashboard creation failed: {e}")
            return ""

    async def execute_full_orchestration(self, mode: str = "full") -> dict[str, Any]:
        """Execute complete EQ12 system orchestration"""
        try:
            print(" EQ12 MASTER ORCHESTRATOR")
            print("=" * 70)
            print("Executing complete EQ12 revenue empire orchestration...")
            print()
            
            orchestration_results = []
            
            # Execute pipeline components
            for i, component in enumerate(self.execution_pipeline, 1):
                print(f" PHASE {i}: {component['name']}")
                print("-" * 50)
                
                result = await self.execute_component(component)
                orchestration_results.append(result)
                
                if result["status"] == "success":
                    print(f" {component['name']} completed successfully")
                else:
                    print(f" {component['name']} failed")
                    if component["critical"]:
                        print(" Critical component failure detected")
                
                print()
                await asyncio.sleep(0.5)
            
            # Calculate orchestration metrics
            successful_count = sum(1 for r in orchestration_results if r["status"] == "success")
            success_rate = (successful_count / len(orchestration_results)) * 100
            critical_failures = [r for r in orchestration_results if r["status"] == "failed" and r.get("critical", False)]
            total_execution_time = sum(r.get("execution_time", 0) for r in orchestration_results)
            
            # Create master dashboard
            dashboard_path = self.create_master_dashboard_index(orchestration_results)
            
            # Create comprehensive orchestration summary
            orchestration_summary = {
                "metadata": {
                    "orchestration_timestamp": datetime.now().isoformat(),
                    "orchestrator_version": "EQ12 Master Orchestrator v6.0",
                    "execution_mode": mode,
                    "total_components": len(orchestration_results),
                    "success_rate": success_rate,
                    "total_execution_time": total_execution_time
                },
                "execution_results": orchestration_results,
                "performance_metrics": {
                    "successful_components": successful_count,
                    "failed_components": len(orchestration_results) - successful_count,
                    "critical_failures": len(critical_failures),
                    "average_execution_time": total_execution_time / len(orchestration_results)
                },
                "system_status": {
                    "template_empire": "operational" if any(r["component"] == "Template Indexer" and r["status"] == "success" for r in orchestration_results) else "failed",
                    "marketplace_deployment": "operational" if any(r["component"] == "Market Builder" and r["status"] == "success" for r in orchestration_results) else "failed",
                    "quantum_systems": "operational" if any(r["component"] == "Quantum Deployer" and r["status"] == "success" for r in orchestration_results) else "failed",
                    "revenue_intelligence": "operational" if any(r["component"] == "Revenue Reporter" and r["status"] == "success" for r in orchestration_results) else "failed"
                },
                "dashboard_path": dashboard_path,
                "next_recommended_action": "Monitor real-time performance" if success_rate >= 80 else "Investigate and fix failed components"
            }
            
            # Save orchestration report
            report_path = self.logs_path / f"master_orchestration_{self.timestamp}.json"
            report_path.write_text(json.dumps(orchestration_summary, indent=2))
            
            # Create latest version
            latest_report = self.logs_path / "master_orchestration_latest.json"
            latest_report.write_text(json.dumps(orchestration_summary, indent=2))
            
            print("=" * 70)
            print(" EQ12 MASTER ORCHESTRATION COMPLETE!")
            print("=" * 70)
            print(f" Components Executed: {len(orchestration_results)}")
            print(f" Success Rate: {success_rate:.1f}%")
            print(f" Critical Failures: {len(critical_failures)}")
            print(f" Total Execution Time: {total_execution_time:.2f}s")
            print(f" Master Dashboard: {dashboard_path}")
            print(f" Report: {report_path}")
            print()
            
            if success_rate >= 80 and not critical_failures:
                print(" EQ12 REVENUE EMPIRE: FULLY OPERATIONAL")
                print(" All systems green - ready for maximum revenue generation")
            elif critical_failures:
                print(" CRITICAL SYSTEMS NEED ATTENTION")
                print(" Address critical failures before proceeding")
            else:
                print(" PARTIAL SUCCESS - SOME OPTIMIZATION NEEDED")
                print(" Review failed components for improvements")
            
            return orchestration_summary
            
        except Exception as e:
            logger.error(f" Master orchestration failed: {e}")
            return {"status": "failed", "error": str(e)}


async def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Master Orchestrator")
    parser.add_argument("--mode", choices=["full", "quick", "critical"], default="full", 
                       help="Execution mode")
    parser.add_argument("--publish", choices=["all", "telegram", "email", "dashboard"], 
                       action="append", help="Publishing options")
    
    args = parser.parse_args()
    
    print(" EQ12 MASTER ORCHESTRATOR")
    print("=" * 70)
    print("Initializing ultimate revenue empire orchestration...")
    print()
    
    # Initialize master orchestrator
    orchestrator = EQ12MasterOrchestrator()
    
    # Execute full orchestration
    result = await orchestrator.execute_full_orchestration(args.mode)
    
    success_rate = result.get("metadata", {}).get("success_rate", 0)
    critical_failures = result.get("performance_metrics", {}).get("critical_failures", 0)
    
    if success_rate >= 80 and critical_failures == 0:
        print("\n MASTER ORCHESTRATION SUCCESSFUL!")
        print(" EQ12 is operating at maximum efficiency!")
    elif critical_failures > 0:
        print("\n CRITICAL ISSUES DETECTED!")
        print(" Address critical failures immediately!")
    else:
        print("\n PARTIAL SUCCESS ACHIEVED!")
        print(" Review and optimize failed components!")


if __name__ == "__main__":
    asyncio.run(main())