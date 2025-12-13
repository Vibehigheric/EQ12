#!/usr/bin/env python3
"""
 EQ12 SPORTS INTELLIGENCE INTEGRATION SYSTEM
==============================================

Advanced sports intelligence integration that combines multiple data sources
and systems for comprehensive sports betting and analytics intelligence.

Integration Points:
- Twitter Sports Intelligence (social media monitoring)
- Real-Time Sports Intelligence (TheSportsDB integration)
- Weather Intelligence (stadium-specific conditions)
- International Sports Weather Engine (global coverage)
- Multi-Tier Architecture (reliability framework)

Features:
- Unified sports data aggregation
- Cross-source correlation analysis
- Intelligent alert prioritization
- Betting opportunity identification
- Performance metric tracking
- Automated decision support

Author: EQ12 Quantum Development Team
Version: 1.0.0 - Sports Intelligence Integration
Date: November 7, 2025
"""

import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import sqlite3


class IntegrationStatus(Enum):
    """Integration status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    INITIALIZING = "initializing"


class DataSource(Enum):
    """Data source enumeration."""
    TWITTER = "twitter"
    THESPORTSDB = "thesportsdb"
    WEATHER = "weather"
    INTERNATIONAL = "international"
    MULTI_TIER = "multi_tier"


@dataclass
class SportsIntelligenceData:
    """Sports intelligence data structure."""
    source: DataSource
    sport: str
    data_type: str
    content: Dict[str, Any]
    timestamp: datetime
    confidence_score: float
    betting_impact: float
    alert_priority: str


class EQ12SportsIntelligenceIntegration:
    """Unified sports intelligence integration and orchestration system."""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.scripts_path = self.workspace_path / "scripts"
        self.logs_path = self.workspace_path / "logs"
        self.data_path = self.workspace_path / "data"
        
        # Ensure directories exist
        for path in [self.logs_path, self.data_path]:
            path.mkdir(exist_ok=True)
        
        # Setup logging
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_path / f"sports_intelligence_integration_{self.timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self.db_path = self.data_path / "sports_intelligence_integration.db"
        self._initialize_database()
        
        # Integration systems
        self.integrated_systems = {
            "twitter_sports": "twitter_sports_intelligence.py",
            "realtime_sports": "scripts/eq12_realtime_sports_intelligence.py",
            "weather_intelligence": "eq12_enhanced_stadium_weather_system.py",
            "international_weather": "eq12_international_sports_weather_engine.py",
            "multi_tier_architecture": "eq12_multi_tier_architecture_engine.py"
        }
        
        # System status tracking
        self.system_status = {}
        self.integration_data = []
        
        # Performance metrics
        self.correlation_matrix = {}
        self.prediction_accuracy = {}
    
    def _initialize_database(self):
        """Initialize the sports intelligence integration database."""
        conn = sqlite3.connect(self.db_path)
        
        # Integration data table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS integration_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                sport TEXT NOT NULL,
                data_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                confidence_score REAL NOT NULL,
                betting_impact REAL NOT NULL,
                alert_priority TEXT NOT NULL,
                processed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # System status table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS system_status (
                system_name TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                last_update TIMESTAMP NOT NULL,
                performance_score REAL DEFAULT 0.0,
                error_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Correlation analysis table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS correlation_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_a TEXT NOT NULL,
                source_b TEXT NOT NULL,
                correlation_score REAL NOT NULL,
                sample_size INTEGER NOT NULL,
                analysis_timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def check_system_availability(self) -> Dict[str, Any]:
        """Check availability of all integrated systems."""
        self.logger.info(" Checking sports intelligence system availability...")
        
        print(" SPORTS INTELLIGENCE SYSTEM CHECK")
        print("=" * 38)
        
        availability_report = {
            "check_timestamp": datetime.now(timezone.utc).isoformat(),
            "systems_checked": len(self.integrated_systems),
            "systems_available": 0,
            "systems_missing": [],
            "system_details": {}
        }
        
        for system_name, script_path in self.integrated_systems.items():
            full_path = self.workspace_path / script_path
            
            system_info = {
                "script_path": str(full_path),
                "exists": full_path.exists(),
                "status": IntegrationStatus.INACTIVE.value,
                "last_check": datetime.now(timezone.utc).isoformat()
            }
            
            if full_path.exists():
                system_info["status"] = IntegrationStatus.ACTIVE.value
                availability_report["systems_available"] += 1
                status_icon = ""
            else:
                availability_report["systems_missing"].append(system_name)
                status_icon = ""
            
            availability_report["system_details"][system_name] = system_info
            self.system_status[system_name] = system_info["status"]
            
            print(f"{status_icon} {system_name}: {system_info['status']}")
            if not system_info["exists"]:
                print(f"    Missing: {script_path}")
        
        print(f"\n Available Systems: {availability_report['systems_available']}/{availability_report['systems_checked']}")
        print(f" Missing Systems: {len(availability_report['systems_missing'])}")
        
        return availability_report
    
    async def execute_twitter_intelligence(self, sports: List[str]) -> Dict[str, Any]:
        """Execute Twitter sports intelligence monitoring."""
        self.logger.info(f" Executing Twitter sports intelligence for {sports}...")
        
        print(f"\n TWITTER SPORTS INTELLIGENCE")
        print("=" * 32)
        
        try:
            # Execute Twitter sports intelligence script
            script_path = self.workspace_path / "twitter_sports_intelligence.py"
            
            if not script_path.exists():
                raise FileNotFoundError(f"Twitter sports intelligence script not found: {script_path}")
            
            # Build command
            cmd = [
                sys.executable, str(script_path),
                "--sports"] + sports + [
                "--duration", "10",  # Short duration for demo
                "--workspace", str(self.workspace_path)
            ]
            
            print(f" Running: {' '.join(cmd)}")
            
            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60.0)
            
            # Parse results
            twitter_results = {
                "execution_status": "success" if process.returncode == 0 else "error",
                "return_code": process.returncode,
                "output": stdout.decode('utf-8', errors='ignore'),
                "error": stderr.decode('utf-8', errors='ignore') if stderr else None,
                "sports_monitored": sports,
                "execution_time": datetime.now(timezone.utc).isoformat()
            }
            
            if process.returncode == 0:
                print(" Twitter intelligence executed successfully")
                self._update_system_status("twitter_sports", IntegrationStatus.ACTIVE, True)
            else:
                print(f" Twitter intelligence failed with code {process.returncode}")
                self._update_system_status("twitter_sports", IntegrationStatus.ERROR, False)
            
            return twitter_results
            
        except asyncio.TimeoutError:
            error_msg = "Twitter intelligence execution timed out"
            self.logger.error(error_msg)
            self._update_system_status("twitter_sports", IntegrationStatus.ERROR, False)
            return {"execution_status": "timeout", "error": error_msg}
        
        except Exception as e:
            error_msg = f"Twitter intelligence execution error: {e}"
            self.logger.error(error_msg)
            self._update_system_status("twitter_sports", IntegrationStatus.ERROR, False)
            return {"execution_status": "error", "error": error_msg}
    
    async def execute_realtime_intelligence(self) -> Dict[str, Any]:
        """Execute real-time sports intelligence monitoring."""
        self.logger.info(" Executing real-time sports intelligence...")
        
        print(f"\n REAL-TIME SPORTS INTELLIGENCE")
        print("=" * 35)
        
        try:
            # Execute real-time sports intelligence script
            script_path = self.scripts_path / "eq12_realtime_sports_intelligence.py"
            
            if not script_path.exists():
                raise FileNotFoundError(f"Real-time sports intelligence script not found: {script_path}")
            
            # Build command for live monitoring
            cmd = [
                sys.executable, str(script_path),
                "--monitor", "5",  # 5 minutes
                "--workspace", str(self.workspace_path)
            ]
            
            print(f" Running: {' '.join(cmd)}")
            
            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120.0)
            
            # Parse results
            realtime_results = {
                "execution_status": "success" if process.returncode == 0 else "error",
                "return_code": process.returncode,
                "output": stdout.decode('utf-8', errors='ignore'),
                "error": stderr.decode('utf-8', errors='ignore') if stderr else None,
                "monitoring_duration": "5 minutes",
                "execution_time": datetime.now(timezone.utc).isoformat()
            }
            
            if process.returncode == 0:
                print(" Real-time intelligence executed successfully")
                self._update_system_status("realtime_sports", IntegrationStatus.ACTIVE, True)
            else:
                print(f" Real-time intelligence failed with code {process.returncode}")
                self._update_system_status("realtime_sports", IntegrationStatus.ERROR, False)
            
            return realtime_results
            
        except asyncio.TimeoutError:
            error_msg = "Real-time intelligence execution timed out"
            self.logger.error(error_msg)
            self._update_system_status("realtime_sports", IntegrationStatus.ERROR, False)
            return {"execution_status": "timeout", "error": error_msg}
        
        except Exception as e:
            error_msg = f"Real-time intelligence execution error: {e}"
            self.logger.error(error_msg)
            self._update_system_status("realtime_sports", IntegrationStatus.ERROR, False)
            return {"execution_status": "error", "error": error_msg}
    
    async def execute_weather_intelligence(self) -> Dict[str, Any]:
        """Execute weather intelligence analysis."""
        self.logger.info(" Executing weather intelligence analysis...")
        
        print(f"\n WEATHER INTELLIGENCE ANALYSIS")
        print("=" * 35)
        
        try:
            # Execute enhanced stadium weather system
            script_path = self.workspace_path / "eq12_enhanced_stadium_weather_system.py"
            
            if not script_path.exists():
                raise FileNotFoundError(f"Weather intelligence script not found: {script_path}")
            
            # Build command
            cmd = [
                sys.executable, str(script_path),
                "--full-report",
                "--workspace", str(self.workspace_path)
            ]
            
            print(f" Running: {' '.join(cmd)}")
            
            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=90.0)
            
            # Parse results
            weather_results = {
                "execution_status": "success" if process.returncode == 0 else "error",
                "return_code": process.returncode,
                "output": stdout.decode('utf-8', errors='ignore'),
                "error": stderr.decode('utf-8', errors='ignore') if stderr else None,
                "analysis_type": "enhanced_stadium_weather",
                "execution_time": datetime.now(timezone.utc).isoformat()
            }
            
            if process.returncode == 0:
                print(" Weather intelligence executed successfully")
                self._update_system_status("weather_intelligence", IntegrationStatus.ACTIVE, True)
            else:
                print(f" Weather intelligence failed with code {process.returncode}")
                self._update_system_status("weather_intelligence", IntegrationStatus.ERROR, False)
            
            return weather_results
            
        except asyncio.TimeoutError:
            error_msg = "Weather intelligence execution timed out"
            self.logger.error(error_msg)
            self._update_system_status("weather_intelligence", IntegrationStatus.ERROR, False)
            return {"execution_status": "timeout", "error": error_msg}
        
        except Exception as e:
            error_msg = f"Weather intelligence execution error: {e}"
            self.logger.error(error_msg)
            self._update_system_status("weather_intelligence", IntegrationStatus.ERROR, False)
            return {"execution_status": "error", "error": error_msg}
    
    def _update_system_status(self, system_name: str, status: IntegrationStatus, success: bool):
        """Update system status in database."""
        conn = sqlite3.connect(self.db_path)
        
        # Get current stats
        cursor = conn.cursor()
        cursor.execute('SELECT success_count, error_count FROM system_status WHERE system_name = ?', (system_name,))
        result = cursor.fetchone()
        
        if result:
            success_count, error_count = result
            if success:
                success_count += 1
            else:
                error_count += 1
        else:
            success_count = 1 if success else 0
            error_count = 0 if success else 1
        
        # Calculate performance score
        total_executions = success_count + error_count
        performance_score = (success_count / total_executions) * 100 if total_executions > 0 else 0
        
        # Update status
        conn.execute('''
            INSERT OR REPLACE INTO system_status 
            (system_name, status, last_update, performance_score, success_count, error_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            system_name,
            status.value,
            datetime.now(timezone.utc).isoformat(),
            performance_score,
            success_count,
            error_count
        ))
        
        conn.commit()
        conn.close()
    
    async def perform_correlation_analysis(self) -> Dict[str, Any]:
        """Perform correlation analysis between different intelligence sources."""
        self.logger.info(" Performing cross-source correlation analysis...")
        
        print(f"\n CORRELATION ANALYSIS")
        print("=" * 25)
        
        # Get recent data from all sources
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get data from last 24 hours
        since_time = datetime.now(timezone.utc) - timedelta(hours=24)
        cursor.execute('''
            SELECT source, sport, betting_impact, confidence_score, timestamp
            FROM integration_data 
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (since_time.isoformat(),))
        
        recent_data = cursor.fetchall()
        conn.close()
        
        # Analyze correlations
        correlation_results = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "data_points_analyzed": len(recent_data),
            "correlations": {},
            "insights": []
        }
        
        # Group data by source
        source_data = {}
        for row in recent_data:
            source, sport, impact, confidence, timestamp = row
            if source not in source_data:
                source_data[source] = []
            source_data[source].append({
                "sport": sport,
                "impact": impact,
                "confidence": confidence,
                "timestamp": timestamp
            })
        
        # Calculate simple correlations between sources
        sources = list(source_data.keys())
        for i, source_a in enumerate(sources):
            for source_b in sources[i+1:]:
                # Calculate correlation based on betting impact alignment
                data_a = source_data[source_a]
                data_b = source_data[source_b]
                
                if len(data_a) > 0 and len(data_b) > 0:
                    avg_impact_a = sum(d["impact"] for d in data_a) / len(data_a)
                    avg_impact_b = sum(d["impact"] for d in data_b) / len(data_b)
                    
                    # Simple correlation based on impact similarity
                    correlation_score = 1.0 - abs(avg_impact_a - avg_impact_b)
                    correlation_score = max(0.0, min(1.0, correlation_score))
                    
                    correlation_key = f"{source_a}_{source_b}"
                    correlation_results["correlations"][correlation_key] = {
                        "score": correlation_score,
                        "source_a": source_a,
                        "source_b": source_b,
                        "sample_size_a": len(data_a),
                        "sample_size_b": len(data_b)
                    }
                    
                    print(f" {source_a}  {source_b}: {correlation_score:.2f}")
        
        # Generate insights
        if correlation_results["correlations"]:
            best_correlation = max(correlation_results["correlations"].values(), key=lambda x: x["score"])
            correlation_results["insights"].append(
                f"Highest correlation: {best_correlation['source_a']} and {best_correlation['source_b']} ({best_correlation['score']:.2f})"
            )
        
        correlation_results["insights"].append(f"Analyzed {len(recent_data)} data points from {len(source_data)} sources")
        
        print(f"\n Correlation Analysis Complete")
        print(f" {len(correlation_results['correlations'])} correlations calculated")
        
        return correlation_results
    
    async def generate_unified_intelligence_report(self, sports: List[str]) -> Dict[str, Any]:
        """Generate comprehensive unified intelligence report."""
        self.logger.info(" Generating unified sports intelligence report...")
        
        print(f"\n UNIFIED INTELLIGENCE REPORT")
        print("=" * 35)
        
        # Execute all intelligence systems
        execution_results = {}
        
        # 1. Twitter Intelligence
        print("1 Executing Twitter Intelligence...")
        execution_results["twitter"] = await self.execute_twitter_intelligence(sports)
        
        # 2. Real-time Intelligence
        print("2 Executing Real-time Intelligence...")
        execution_results["realtime"] = await self.execute_realtime_intelligence()
        
        # 3. Weather Intelligence
        print("3 Executing Weather Intelligence...")
        execution_results["weather"] = await self.execute_weather_intelligence()
        
        # 4. Correlation Analysis
        print("4 Performing Correlation Analysis...")
        correlation_analysis = await self.perform_correlation_analysis()
        
        # Compile unified report
        unified_report = {
            "report_timestamp": datetime.now(timezone.utc).isoformat(),
            "sports_analyzed": sports,
            "execution_results": execution_results,
            "correlation_analysis": correlation_analysis,
            "system_performance": self._get_system_performance_summary(),
            "recommendations": self._generate_unified_recommendations(execution_results, correlation_analysis),
            "next_actions": [
                "Review high-impact alerts from all sources",
                "Monitor correlation trends for pattern identification",
                "Update betting strategies based on integrated intelligence",
                "Schedule next unified analysis cycle"
            ]
        }
        
        # Calculate overall success rate
        successful_executions = sum(1 for result in execution_results.values() 
                                  if result.get("execution_status") == "success")
        total_executions = len(execution_results)
        overall_success_rate = (successful_executions / total_executions) * 100 if total_executions > 0 else 0
        
        unified_report["overall_success_rate"] = overall_success_rate
        
        # Save unified report
        report_file = self.logs_path / f"unified_sports_intelligence_{self.timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(unified_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n UNIFIED REPORT COMPLETE!")
        print(f" Success Rate: {overall_success_rate:.1f}%")
        print(f" Systems Integrated: {total_executions}")
        print(f" Successful Executions: {successful_executions}")
        print(f" Report: {report_file}")
        
        return unified_report
    
    def _get_system_performance_summary(self) -> Dict[str, Any]:
        """Get system performance summary from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT system_name, status, performance_score, success_count, error_count FROM system_status')
        results = cursor.fetchall()
        conn.close()
        
        performance_summary = {}
        for system_name, status, performance_score, success_count, error_count in results:
            performance_summary[system_name] = {
                "status": status,
                "performance_score": performance_score,
                "success_count": success_count,
                "error_count": error_count,
                "total_executions": success_count + error_count
            }
        
        return performance_summary
    
    def _generate_unified_recommendations(self, execution_results: Dict, correlation_analysis: Dict) -> List[str]:
        """Generate unified recommendations based on all analysis."""
        recommendations = []
        
        # Check execution success rates
        successful_systems = [name for name, result in execution_results.items() 
                            if result.get("execution_status") == "success"]
        failed_systems = [name for name, result in execution_results.items() 
                        if result.get("execution_status") != "success"]
        
        if len(successful_systems) >= 2:
            recommendations.append(f"Multiple intelligence sources active - cross-validate alerts from {', '.join(successful_systems[:2])}")
        
        if failed_systems:
            recommendations.append(f"Investigate failures in: {', '.join(failed_systems)}")
        
        # Check correlations
        if correlation_analysis.get("correlations"):
            high_correlations = [corr for corr in correlation_analysis["correlations"].values() 
                               if corr["score"] > 0.7]
            if high_correlations:
                recommendations.append("High correlation detected - prioritize alerts confirmed by multiple sources")
        
        if not recommendations:
            recommendations.append("Continue unified monitoring - all systems operational")
        
        return recommendations


async def main():
    """Main execution function for sports intelligence integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Sports Intelligence Integration")
    parser.add_argument("--sports", nargs="+", default=["nfl", "nhl"],
                       choices=["nfl", "nhl", "nba", "mlb", "ncaa_football", "ncaa_basketball"],
                       help="Sports to analyze")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    parser.add_argument("--check-only", action="store_true", help="Check system availability only")
    args = parser.parse_args()
    
    try:
        # Initialize sports intelligence integration
        integration = EQ12SportsIntelligenceIntegration(args.workspace)
        
        if args.check_only:
            # Check system availability only
            await integration.check_system_availability()
        else:
            # Run full unified intelligence analysis
            await integration.check_system_availability()
            unified_report = await integration.generate_unified_intelligence_report(args.sports)
        
        return 0
        
    except Exception as e:
        print(f" SPORTS INTELLIGENCE INTEGRATION ERROR: {e}")
        logging.error(f"Sports intelligence integration error: {e}")
        return 1


if __name__ == "__main__":
    # Ensure proper event loop for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)