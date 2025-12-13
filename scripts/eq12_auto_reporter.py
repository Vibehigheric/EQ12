#!/usr/bin/env python3
"""
EQ12 Automated Sports Betting Reporter
Generates comprehensive reports from Coral AI betting analysis

Author: EQ12 Team
Date: November 2, 2025
"""

import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
import sqlite3


class AutomatedReporter:
    """Automated report generator for EQ12 Coral betting system"""
    
    def __init__(self, workspace_path: str, verbose: bool = False):
        self.workspace_path = Path(workspace_path)
        self.reports_path = self.workspace_path / "coral_betting_ai" / "reports"
        self.data_path = self.workspace_path / "data"
        self.dashboard_path = self.workspace_path / "dashboard"
        self.logs_path = self.workspace_path / "logs"
        
        # Ensure directories exist
        for path in [self.reports_path, self.data_path, self.dashboard_path]:
            path.mkdir(parents=True, exist_ok=True)
            
        self.verbose = verbose
        self.setup_logging()
        
        # Initialize database for historical tracking
        self.db_path = self.data_path / "coral_betting_history.db"
        self.init_database()
        
    def setup_logging(self):
        """Setup logging for automated reporting"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.logs_path / f"auto_reporter_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def init_database(self):
        """Initialize SQLite database for historical tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables for tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bet_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    bet_id TEXT,
                    description TEXT,
                    sport TEXT,
                    coral_ev_score REAL,
                    coral_confidence REAL,
                    recommendation TEXT,
                    odds REAL,
                    actual_outcome TEXT,
                    profit_loss REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parlay_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    parlay_id TEXT,
                    total_legs INTEGER,
                    total_odds REAL,
                    parlay_ev REAL,
                    parlay_confidence REAL,
                    risk_adjusted_score REAL,
                    actual_outcome TEXT,
                    profit_loss REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_predictions INTEGER,
                    avg_inference_time_ms REAL,
                    models_loaded INTEGER,
                    bets_processed INTEGER,
                    parlays_generated INTEGER
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Database initialization error: {e}")
            
    def store_bet_analysis(self, bets: List[Dict]):
        """Store bet analysis data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for bet in bets:
                cursor.execute('''
                    INSERT INTO bet_analysis 
                    (timestamp, bet_id, description, sport, coral_ev_score, 
                     coral_confidence, recommendation, odds)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bet.get('processed_at', datetime.now().isoformat()),
                    bet.get('bet_id', f"bet_{datetime.now().timestamp()}"),
                    bet.get('description', 'Unknown'),
                    bet.get('sport', 'Unknown'),
                    bet.get('coral_ev_score', 0.0),
                    bet.get('coral_confidence', 0.0),
                    bet.get('coral_recommendation', 'NO_BET'),
                    bet.get('decimal_odds', 0.0)
                ))
                
            conn.commit()
            conn.close()
            
            self.logger.info(f"Stored {len(bets)} bet analyses in database")
            
        except Exception as e:
            self.logger.error(f"Error storing bet analysis: {e}")
            
    def generate_daily_report(self) -> str:
        """Generate comprehensive daily report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_data = self.collect_daily_data()
        
        # Generate HTML report
        html_report = self.create_daily_html_report(report_data)
        html_file = self.dashboard_path / f"daily_coral_report_{timestamp}.html"
        
        with open(html_file, 'w') as f:
            f.write(html_report)
            
        # Generate JSON summary
        json_file = self.reports_path / f"daily_summary_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        self.logger.info(f"Daily report generated: {html_file}")
        return str(html_file)
        
    def collect_daily_data(self) -> Dict:
        """Collect all data for daily report"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        report_data = {
            'report_date': today,
            'generated_at': datetime.now().isoformat(),
            'coral_analysis': {},
            'parlay_optimization': {},
            'system_performance': {},
            'historical_comparison': {}
        }
        
        # Collect Coral analysis data
        coral_files = list(self.reports_path.glob("coral_results_*.json"))
        if coral_files:
            latest_coral = max(coral_files, key=lambda f: f.stat().st_mtime)
            try:
                with open(latest_coral, 'r') as f:
                    coral_data = json.load(f)
                    
                bets = coral_data.get('bets', [])
                report_data['coral_analysis'] = {
                    'total_bets_analyzed': len(bets),
                    'strong_recommendations': len([b for b in bets 
                                                 if b.get('coral_recommendation') == 'STRONG_BET']),
                    'moderate_recommendations': len([b for b in bets 
                                                   if b.get('coral_recommendation') == 'MODERATE_BET']),
                    'avg_ev_score': sum(b.get('coral_ev_score', 0) for b in bets) / len(bets) if bets else 0,
                    'avg_confidence': sum(b.get('coral_confidence', 0) for b in bets) / len(bets) if bets else 0,
                    'top_bets': sorted(bets, key=lambda x: x.get('coral_ev_score', 0), reverse=True)[:10]
                }
                
                performance = coral_data.get('coral_performance', {})
                report_data['system_performance'] = {
                    'avg_inference_time_ms': performance.get('avg_inference_time_ms', 0),
                    'total_predictions': performance.get('total_predictions', 0),
                    'models_loaded': len(performance.get('models_loaded', [])),
                    'predictions_per_second': 1000 / performance.get('avg_inference_time_ms', 1000) if performance.get('avg_inference_time_ms') else 0
                }
                
            except Exception as e:
                self.logger.error(f"Error collecting Coral data: {e}")
                
        # Collect parlay data
        parlay_file = self.reports_path / "optimized_parlays_latest.json"
        if parlay_file.exists():
            try:
                with open(parlay_file, 'r') as f:
                    parlay_data = json.load(f)
                    
                parlay_summary = parlay_data.get('optimization_summary', {})
                top_parlays = parlay_data.get('top_20_parlays', [])
                
                report_data['parlay_optimization'] = {
                    'total_combinations_generated': parlay_summary.get('parlay_combinations_generated', 0),
                    'qualified_bets_used': parlay_summary.get('qualified_bets', 0),
                    'top_parlay_count': len(top_parlays),
                    'best_parlay_score': top_parlays[0].get('risk_adjusted_score', 0) if top_parlays else 0,
                    'best_parlay_odds': top_parlays[0].get('total_odds', 0) if top_parlays else 0,
                    'top_parlays': top_parlays[:5]
                }
                
            except Exception as e:
                self.logger.error(f"Error collecting parlay data: {e}")
                
        # Collect historical comparison
        report_data['historical_comparison'] = self.get_historical_comparison()
        
        return report_data
        
    def get_historical_comparison(self) -> Dict:
        """Get historical performance comparison"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get last 7 days of data
            cursor.execute('''
                SELECT DATE(timestamp) as date, 
                       COUNT(*) as bet_count,
                       AVG(coral_ev_score) as avg_ev,
                       AVG(coral_confidence) as avg_confidence
                FROM bet_analysis 
                WHERE datetime(timestamp) >= datetime('now', '-7 days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            ''')
            
            daily_stats = cursor.fetchall()
            
            # Get system performance trends
            cursor.execute('''
                SELECT DATE(timestamp) as date,
                       AVG(avg_inference_time_ms) as avg_inference_time,
                       SUM(total_predictions) as total_predictions
                FROM system_performance
                WHERE datetime(timestamp) >= datetime('now', '-7 days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            ''')
            
            performance_trends = cursor.fetchall()
            
            conn.close()
            
            return {
                'daily_betting_stats': [
                    {
                        'date': row[0],
                        'bet_count': row[1],
                        'avg_ev': row[2],
                        'avg_confidence': row[3]
                    } for row in daily_stats
                ],
                'performance_trends': [
                    {
                        'date': row[0],
                        'avg_inference_time': row[1],
                        'total_predictions': row[2]
                    } for row in performance_trends
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting historical data: {e}")
            return {}
            
    def create_daily_html_report(self, data: Dict) -> str:
        """Create comprehensive HTML daily report"""
        coral_analysis = data.get('coral_analysis', {})
        parlay_optimization = data.get('parlay_optimization', {})
        system_performance = data.get('system_performance', {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>EQ12 Coral AI Daily Report - {data['report_date']}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 30px; text-align: center; border-radius: 10px; margin-bottom: 20px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .metric-card h3 {{ margin: 0 0 10px 0; color: #333; font-size: 14px; text-transform: uppercase; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #667eea; margin-bottom: 5px; }}
        .metric-label {{ color: #666; font-size: 14px; }}
        .section {{ background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .section h2 {{ color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .bet-item {{ border-left: 4px solid #667eea; padding: 15px; margin: 10px 0; background: #f8f9fa; }}
        .bet-item.strong {{ border-left-color: #28a745; }}
        .bet-item.moderate {{ border-left-color: #ffc107; }}
        .parlay-item {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .performance-bar {{ height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; }}
        .performance-fill {{ height: 100%; background: linear-gradient(90deg, #28a745, #20c997); }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> EQ12 Coral AI Daily Report</h1>
            <p>{data['report_date']} | Generated at {datetime.now().strftime('%H:%M:%S UTC')}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Bets Analyzed</h3>
                <div class="metric-value">{coral_analysis.get('total_bets_analyzed', 0)}</div>
                <div class="metric-label">Coral AI processed</div>
            </div>
            
            <div class="metric-card">
                <h3>Strong Recommendations</h3>
                <div class="metric-value">{coral_analysis.get('strong_recommendations', 0)}</div>
                <div class="metric-label">High confidence bets</div>
            </div>
            
            <div class="metric-card">
                <h3>Avg EV Score</h3>
                <div class="metric-value">{coral_analysis.get('avg_ev_score', 0):.3f}</div>
                <div class="metric-label">Expected value</div>
            </div>
            
            <div class="metric-card">
                <h3>Inference Speed</h3>
                <div class="metric-value">{system_performance.get('avg_inference_time_ms', 0):.1f}ms</div>
                <div class="metric-label">Average per prediction</div>
            </div>
            
            <div class="metric-card">
                <h3>Parlays Generated</h3>
                <div class="metric-value">{parlay_optimization.get('total_combinations_generated', 0)}</div>
                <div class="metric-label">Optimized combinations</div>
            </div>
            
            <div class="metric-card">
                <h3>TPU Predictions</h3>
                <div class="metric-value">{system_performance.get('total_predictions', 0)}</div>
                <div class="metric-label">Total processed</div>
            </div>
        </div>
        
        <div class="section">
            <h2> Top Coral AI Recommendations</h2>
"""
        
        top_bets = coral_analysis.get('top_bets', [])[:10]
        for i, bet in enumerate(top_bets, 1):
            recommendation = bet.get('coral_recommendation', 'NO_BET')
            css_class = 'strong' if recommendation == 'STRONG_BET' else 'moderate' if recommendation == 'MODERATE_BET' else ''
            
            html += f"""
            <div class="bet-item {css_class}">
                <strong>#{i}. {bet.get('description', 'Unknown bet')}</strong><br>
                <span>EV: {bet.get('coral_ev_score', 0):.3f} | 
                      Confidence: {bet.get('coral_confidence', 0):.3f} | 
                      Recommendation: {recommendation}</span>
            </div>
"""
        
        html += """
        </div>
        
        <div class="section">
            <h2> Top Optimized Parlays</h2>
"""
        
        top_parlays = parlay_optimization.get('top_parlays', [])[:5]
        for i, parlay in enumerate(top_parlays, 1):
            html += f"""
            <div class="parlay-item">
                <strong>Parlay #{i} - {parlay.get('total_legs', 0)} Legs</strong><br>
                <span>Odds: {parlay.get('total_odds', 0):.2f} | 
                      EV: {parlay.get('parlay_ev', 0):.3f} | 
                      Score: {parlay.get('risk_adjusted_score', 0):.3f}</span>
            </div>
"""
        
        html += f"""
        </div>
        
        <div class="section">
            <h2> System Performance</h2>
            <div class="metrics-grid">
                <div>
                    <h4>Processing Speed</h4>
                    <div class="performance-bar">
                        <div class="performance-fill" style="width: {min(100, 100 - system_performance.get('avg_inference_time_ms', 100) / 10)}%"></div>
                    </div>
                    <small>{system_performance.get('predictions_per_second', 0):.1f} predictions/second</small>
                </div>
                
                <div>
                    <h4>Models Active</h4>
                    <div style="font-size: 24px; color: #28a745; font-weight: bold;">
                        {system_performance.get('models_loaded', 0)}/5
                    </div>
                    <small>Coral Edge TPU models loaded</small>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p> Automated report generated by EQ12 Coral AI Sports Betting System</p>
            <p>Report generated at {data['generated_at']}</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
        
    def generate_performance_report(self) -> str:
        """Generate system performance report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Collect performance data
        performance_data = self.collect_performance_data()
        
        # Generate JSON report
        json_file = self.reports_path / f"performance_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(performance_data, f, indent=2)
            
        self.logger.info(f"Performance report generated: {json_file}")
        return str(json_file)
        
    def collect_performance_data(self) -> Dict:
        """Collect system performance data"""
        performance_data = {
            'report_type': 'system_performance',
            'generated_at': datetime.now().isoformat(),
            'coral_tpu_metrics': {},
            'database_metrics': {},
            'file_system_metrics': {}
        }
        
        # TPU performance from latest Coral results
        coral_files = list(self.reports_path.glob("coral_results_*.json"))
        if coral_files:
            latest_coral = max(coral_files, key=lambda f: f.stat().st_mtime)
            try:
                with open(latest_coral, 'r') as f:
                    coral_data = json.load(f)
                    
                perf = coral_data.get('coral_performance', {})
                performance_data['coral_tpu_metrics'] = {
                    'avg_inference_time_ms': perf.get('avg_inference_time_ms', 0),
                    'total_predictions': perf.get('total_predictions', 0),
                    'models_loaded': len(perf.get('models_loaded', [])),
                    'throughput_per_second': 1000 / perf.get('avg_inference_time_ms', 1000) if perf.get('avg_inference_time_ms') else 0
                }
                
            except Exception as e:
                self.logger.error(f"Error collecting TPU metrics: {e}")
                
        # Database metrics
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM bet_analysis")
            bet_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM parlay_analysis")
            parlay_count = cursor.fetchone()[0]
            
            performance_data['database_metrics'] = {
                'total_bet_records': bet_count,
                'total_parlay_records': parlay_count,
                'database_size_mb': os.path.getsize(self.db_path) / (1024 * 1024) if self.db_path.exists() else 0
            }
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error collecting database metrics: {e}")
            
        # File system metrics
        performance_data['file_system_metrics'] = {
            'coral_result_files': len(list(self.reports_path.glob("coral_results_*.json"))),
            'parlay_result_files': len(list(self.reports_path.glob("optimized_parlays_*.json"))),
            'log_files': len(list(self.logs_path.glob("*.log"))),
            'total_reports_size_mb': sum(f.stat().st_size for f in self.reports_path.glob("*.json")) / (1024 * 1024)
        }
        
        return performance_data


def main():
    parser = argparse.ArgumentParser(description="EQ12 Automated Sports Betting Reporter")
    parser.add_argument("--workspace", default="c:/EQ12", help="Workspace path")
    parser.add_argument("--daily-report", action="store_true", 
                       help="Generate daily report")
    parser.add_argument("--performance-report", action="store_true", 
                       help="Generate performance report")
    parser.add_argument("--store-data", action="store_true", 
                       help="Store latest data in database")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    reporter = AutomatedReporter(args.workspace, args.verbose)
    
    if args.daily_report:
        report_file = reporter.generate_daily_report()
        print(f"Daily report generated: {report_file}")
        
    elif args.performance_report:
        report_file = reporter.generate_performance_report()
        print(f"Performance report generated: {report_file}")
        
    elif args.store_data:
        # Store latest Coral results in database
        coral_files = list(reporter.reports_path.glob("coral_results_*.json"))
        if coral_files:
            latest_coral = max(coral_files, key=lambda f: f.stat().st_mtime)
            with open(latest_coral, 'r') as f:
                data = json.load(f)
            reporter.store_bet_analysis(data.get('bets', []))
            print("Latest data stored in database")
        else:
            print("No Coral results found to store")
            
    else:
        print("EQ12 Automated Reporter ready")
        print("Use --daily-report or --performance-report to generate reports")


if __name__ == "__main__":
    main()