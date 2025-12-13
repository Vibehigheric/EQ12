#!/usr/bin/env python3
"""
EQ12 NBA Dashboard Generator
Creates interactive HTML dashboard for NBA betting analytics
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse
import logging
from pathlib import Path


class NBADashboardGenerator:
    """Interactive NBA betting dashboard with real-time analytics"""
    
    def __init__(self, workspace_dir: str = "C:/EQ12"):
        self.workspace_dir = Path(workspace_dir)
        self.data_dir = self.workspace_dir / "data"
        self.dashboard_dir = self.workspace_dir / "dashboard"
        self.logs_dir = self.workspace_dir / "logs"
        
        # Ensure directories exist
        for directory in [self.data_dir, self.dashboard_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Database connections
        self.odds_db = self.data_dir / "nba_odds.db"
        self.props_db = self.data_dir / "nba_props.db"
        self.predictions_db = self.data_dir / "nba_predictions.db"
        
    def setup_logging(self):
        """Configure logging"""
        log_file = self.logs_dir / f"nba_dashboard_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get current database statistics"""
        stats = {
            "odds_count": 0,
            "props_count": 0,
            "predictions_count": 0,
            "last_update": None,
            "games_today": 0,
            "active_props": 0
        }
        
        try:
            # Odds database stats
            if self.odds_db.exists():
                with sqlite3.connect(self.odds_db) as conn:
                    cursor = conn.cursor()
                    
                    # Total odds records
                    cursor.execute("SELECT COUNT(*) FROM odds WHERE date(commence_time) >= date('now')")
                    stats["odds_count"] = cursor.fetchone()[0]
                    
                    # Games today
                    cursor.execute("SELECT COUNT(DISTINCT game_id) FROM odds WHERE date(commence_time) = date('now')")
                    stats["games_today"] = cursor.fetchone()[0]
                    
                    # Last update
                    cursor.execute("SELECT MAX(last_updated) FROM odds")
                    last_update = cursor.fetchone()[0]
                    if last_update:
                        stats["last_update"] = last_update
            
            # Props database stats
            if self.props_db.exists():
                with sqlite3.connect(self.props_db) as conn:
                    cursor = conn.cursor()
                    
                    # Total props
                    cursor.execute("SELECT COUNT(*) FROM player_props WHERE game_date >= date('now')")
                    stats["props_count"] = cursor.fetchone()[0]
                    
                    # Active props
                    cursor.execute("SELECT COUNT(*) FROM player_props WHERE game_date = date('now') AND is_active = 1")
                    stats["active_props"] = cursor.fetchone()[0]
            
            # Predictions database stats
            if self.predictions_db.exists():
                with sqlite3.connect(self.predictions_db) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT COUNT(*) FROM predictions WHERE date(prediction_time) = date('now')")
                    stats["predictions_count"] = cursor.fetchone()[0]
        
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
        
        return stats
    
    def get_top_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top predictions by expected value"""
        predictions = []
        
        try:
            if self.predictions_db.exists():
                with sqlite3.connect(self.predictions_db) as conn:
                    cursor = conn.cursor()
                    
                    query = """
                    SELECT 
                        player_name,
                        prop_type,
                        line,
                        predicted_value,
                        confidence,
                        expected_value,
                        bookmaker,
                        odds
                    FROM predictions 
                    WHERE date(prediction_time) = date('now')
                        AND expected_value > 0
                    ORDER BY expected_value DESC
                    LIMIT ?
                    """
                    
                    cursor.execute(query, (limit,))
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        predictions.append({
                            "player": row[0],
                            "prop_type": row[1],
                            "line": row[2],
                            "predicted": row[3],
                            "confidence": row[4],
                            "expected_value": row[5],
                            "bookmaker": row[6],
                            "odds": row[7]
                        })
        
        except Exception as e:
            self.logger.error(f"Error getting top predictions: {e}")
        
        return predictions
    
    def get_recent_parlays(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent generated parlays"""
        parlays = []
        
        try:
            parlay_file = self.data_dir / f"parlays_{datetime.now().strftime('%Y%m%d')}.json"
            
            if parlay_file.exists():
                with open(parlay_file, 'r') as f:
                    parlay_data = json.load(f)
                
                # Get top parlays by expected value
                sorted_parlays = sorted(parlay_data.get("parlays", []), 
                                      key=lambda x: x.get("expected_value", 0), 
                                      reverse=True)
                
                parlays = sorted_parlays[:limit]
        
        except Exception as e:
            self.logger.error(f"Error getting recent parlays: {e}")
        
        return parlays
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get EQ12 cluster status"""
        status = {
            "eq12_online": False,
            "pi_online": False,
            "tpu_available": False,
            "last_ping": None,
            "data_sync_status": "Unknown",
            "inference_queue": 0
        }
        
        try:
            # Check for recent cluster status log
            status_file = self.logs_dir / f"cluster_status_{datetime.now().strftime('%Y%m%d')}.json"
            
            if status_file.exists():
                with open(status_file, 'r') as f:
                    status_data = json.load(f)
                
                status.update(status_data)
        
        except Exception as e:
            self.logger.error(f"Error getting cluster status: {e}")
        
        return status
    
    def get_free_sources_data(self) -> Dict[str, Any]:
        """Get data from free NBA sources enrichment database"""
        sources_data = {
            "sources_active": 0,
            "total_records": 0,
            "recent_collections": [],
            "source_breakdown": {}
        }
        
        try:
            enrichment_db = self.data_dir / "nba_enrichment.db"
            
            if enrichment_db.exists():
                with sqlite3.connect(enrichment_db) as conn:
                    cursor = conn.cursor()
                    
                    # Get total records
                    cursor.execute("SELECT COUNT(*) FROM free_sources_data")
                    sources_data["total_records"] = cursor.fetchone()[0]
                    
                    # Get recent collections by source
                    cursor.execute("""
                        SELECT source, COUNT(*) as count, 
                               MAX(collection_time) as last_update
                        FROM free_sources_data 
                        WHERE date(collection_time) = date('now')
                        GROUP BY source
                        ORDER BY count DESC
                    """)
                    
                    breakdown = {}
                    for row in cursor.fetchall():
                        breakdown[row[0]] = {
                            "count": row[1],
                            "last_update": row[2]
                        }
                    
                    sources_data["source_breakdown"] = breakdown
                    sources_data["sources_active"] = len(breakdown)
                    
                    # Get recent sample data
                    cursor.execute("""
                        SELECT source, home_team, away_team, status, collection_time
                        FROM free_sources_data 
                        WHERE date(collection_time) = date('now')
                        ORDER BY collection_time DESC 
                        LIMIT 10
                    """)
                    
                    recent = []
                    for row in cursor.fetchall():
                        recent.append({
                            "source": row[0],
                            "matchup": f"{row[1]} vs {row[2]}",
                            "status": row[3],
                            "time": row[4]
                        })
                    
                    sources_data["recent_collections"] = recent
        
        except Exception as e:
            self.logger.error(f"Error getting free sources data: {e}")
        
        return sources_data
    
    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get statistics about downloaded NBA datasets"""
        dataset_stats = {
            "historical_data_available": False,
            "stats_dataset_available": False,
            "total_files": 0,
            "coverage_years": "N/A"
        }
        
        try:
            # Check historical data
            historical_path = self.data_dir / "nba_historical_data" / "datasets"
            if historical_path.exists():
                dataset_files = list(historical_path.glob("*.tar.xz"))
                dataset_stats["historical_data_available"] = True
                dataset_stats["total_files"] = len(dataset_files)
                
                # Extract years from filenames
                years = set()
                for file in dataset_files:
                    if "_" in file.stem:
                        parts = file.stem.split("_")
                        for part in parts:
                            if part.isdigit() and len(part) == 4:
                                years.add(int(part))
                
                if years:
                    dataset_stats["coverage_years"] = f"{min(years)}-{max(years)}"
            
            # Check stats dataset
            stats_path = self.data_dir / "nba_stats_dataset"
            if stats_path.exists():
                dataset_stats["stats_dataset_available"] = True
        
        except Exception as e:
            self.logger.error(f"Error getting dataset stats: {e}")
        
        return dataset_stats

    def generate_dashboard_html(self) -> str:
        """Generate complete HTML dashboard with enhanced data sources"""
        
        # Get data for dashboard
        stats = self.get_database_stats()
        predictions = self.get_top_predictions(10)
        parlays = self.get_recent_parlays(5)
        cluster_status = self.get_cluster_status()
        free_sources = self.get_free_sources_data()
        dataset_stats = self.get_dataset_stats()
        
        # Format last update time
        last_update_str = "Never"
        if stats.get("last_update"):
            try:
                update_time = datetime.fromisoformat(stats["last_update"])
                last_update_str = update_time.strftime("%Y-%m-%d %H:%M:%S")
            except:
                last_update_str = str(stats["last_update"])
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 NBA Betting Intelligence Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ffd700, #ffed4e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #ffd700;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .main-content {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .predictions-section {{
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .section-title {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #ffd700;
            border-bottom: 2px solid #ffd700;
            padding-bottom: 10px;
        }}
        
        .prediction-item {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            border-left: 4px solid #ffd700;
            transition: background 0.3s ease;
        }}
        
        .prediction-item:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}
        
        .player-name {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .prop-details {{
            display: flex;
            justify-content: space-between;
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .ev-positive {{
            color: #4ade80;
            font-weight: bold;
        }}
        
        .confidence-high {{
            color: #ffd700;
        }}
        
        .confidence-medium {{
            color: #fbbf24;
        }}
        
        .confidence-low {{
            color: #f87171;
        }}
        
        .sidebar {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        
        .cluster-status {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .status-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .status-online {{
            color: #4ade80;
        }}
        
        .status-offline {{
            color: #f87171;
        }}
        
        .parlays-section {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .parlay-item {{
            background: rgba(255, 255, 255, 0.05);
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 8px;
            font-size: 0.9em;
        }}
        
        .timestamp {{
            text-align: center;
            margin-top: 20px;
            opacity: 0.7;
            font-size: 0.9em;
        }}
        
        .refresh-btn {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(45deg, #ffd700, #ffed4e);
            color: #1e3c72;
            border: none;
            padding: 15px 20px;
            border-radius: 50px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
            transition: transform 0.3s ease;
        }}
        
        .refresh-btn:hover {{
            transform: scale(1.1);
        }}
        
        @media (max-width: 768px) {{
            .main-content {{
                grid-template-columns: 1fr;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> EQ12 NBA Betting Intelligence</h1>
            <p>AI-Powered Prop Betting Analytics | EQ12 + Pi5 + Coral TPU Cluster</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats['games_today']}</div>
                <div class="stat-label">Games Today</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['active_props']}</div>
                <div class="stat-label">Active Props</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['predictions_count']}</div>
                <div class="stat-label">Today's Predictions</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(parlays)}</div>
                <div class="stat-label">Generated Parlays</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="predictions-section">
                <h2 class="section-title"> Top Predictions (Expected Value)</h2>
                """
        
        # Add predictions
        if predictions:
            for pred in predictions:
                confidence_class = "confidence-high" if pred['confidence'] > 0.8 else "confidence-medium" if pred['confidence'] > 0.6 else "confidence-low"
                
                html += f"""
                <div class="prediction-item">
                    <div class="player-name">{pred['player']}</div>
                    <div class="prop-details">
                        <span>{pred['prop_type']} {pred['line']}</span>
                        <span class="ev-positive">EV: +{pred['expected_value']:.3f}</span>
                    </div>
                    <div class="prop-details">
                        <span>Predicted: {pred['predicted']:.1f}</span>
                        <span class="{confidence_class}">Confidence: {pred['confidence']:.1%}</span>
                    </div>
                    <div class="prop-details">
                        <span>{pred['bookmaker']}</span>
                        <span>Odds: {pred['odds']}</span>
                    </div>
                </div>
                """
        else:
            html += """
                <div class="prediction-item">
                    <div class="player-name">No predictions available</div>
                    <div class="prop-details">
                        <span>Run data collection and model inference to generate predictions</span>
                    </div>
                </div>
            """
        
        html += """
            </div>
            
            <div class="sidebar">
                <div class="cluster-status">
                    <h2 class="section-title"> Cluster Status</h2>
                    """
        
        # Add cluster status
        eq12_status = "status-online" if cluster_status.get('eq12_online', False) else "status-offline"
        pi_status = "status-online" if cluster_status.get('pi_online', False) else "status-offline"
        tpu_status = "status-online" if cluster_status.get('tpu_available', False) else "status-offline"
        
        html += f"""
                    <div class="status-item">
                        <span>EQ12 Host</span>
                        <span class="{eq12_status}">{' Online' if cluster_status.get('eq12_online', False) else ' Offline'}</span>
                    </div>
                    <div class="status-item">
                        <span>Pi5 Node</span>
                        <span class="{pi_status}">{' Online' if cluster_status.get('pi_online', False) else ' Offline'}</span>
                    </div>
                    <div class="status-item">
                        <span>Coral TPU</span>
                        <span class="{tpu_status}">{' Available' if cluster_status.get('tpu_available', False) else ' Unavailable'}</span>
                    </div>
                    <div class="status-item">
                        <span>Data Sync</span>
                        <span>{cluster_status.get('data_sync_status', 'Unknown')}</span>
                    </div>
                    <div class="status-item">
                        <span>Inference Queue</span>
                        <span>{cluster_status.get('inference_queue', 0)} jobs</span>
                    </div>
                </div>
                
                <div class="data-sources-section">
                    <h2 class="section-title"> Free Data Sources</h2>
                    """
        
        # Add free sources data
        if free_sources:
            for source_type, count in free_sources.items():
                html += f"""
                    <div class="status-item">
                        <span>{source_type.replace('_', ' ').title()}</span>
                        <span class="status-online">{count} records</span>
                    </div>
                """
            
            # Add last update info
            if 'last_update' in free_sources:
                html += f"""
                    <div class="status-item">
                        <span>Last Update</span>
                        <span>{free_sources['last_update']}</span>
                    </div>
                """
        else:
            html += """
                    <div class="status-item">
                        <span>No free source data available</span>
                    </div>
            """
        
        html += """
                </div>
                
                <div class="datasets-section">
                    <h2 class="section-title"> Historical Datasets</h2>
                    """
        
        # Add dataset statistics
        if dataset_stats:
            # Handle historical data
            if dataset_stats.get("historical_data_available"):
                file_count = dataset_stats.get("total_files", 0)
                coverage = dataset_stats.get("coverage_years", "Unknown")
                html += f"""
                    <div class="status-item">
                        <span>Historical Data</span>
                        <span class="status-online">{file_count} files</span>
                    </div>
                    <div class="status-item">
                        <span>Coverage</span>
                        <span>{coverage}</span>
                    </div>
                """
            
            # Handle stats dataset
            if dataset_stats.get("stats_dataset_available"):
                html += f"""
                    <div class="status-item">
                        <span>Stats Dataset</span>
                        <span class="status-online">Available</span>
                    </div>
                """
        else:
            html += """
                    <div class="status-item">
                        <span>No dataset information available</span>
                    </div>
            """
        
        html += """
                </div>
                
                <div class="parlays-section">
                    <h2 class="section-title"> Recent Parlays</h2>
                    """
        
        # Add parlays
        if parlays:
            for parlay in parlays:
                legs_count = len(parlay.get('legs', []))
                total_odds = parlay.get('total_odds', 0)
                expected_value = parlay.get('expected_value', 0)
                
                html += f"""
                    <div class="parlay-item">
                        <div style="font-weight: bold; margin-bottom: 5px;">
                            {legs_count}-Leg Parlay
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>Odds: +{total_odds:.0f}</span>
                            <span class="ev-positive">EV: +{expected_value:.3f}</span>
                        </div>
                    </div>
                """
        else:
            html += """
                    <div class="parlay-item">
                        <div>No parlays generated yet</div>
                        <div style="font-size: 0.8em; opacity: 0.7;">
                            Run prop analysis to generate optimal parlays
                        </div>
                    </div>
            """
        
        html += f"""
                </div>
            </div>
        </div>
        
        <div class="timestamp">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
            Data last refreshed: {last_update_str}
        </div>
    </div>
    
    <button class="refresh-btn" onclick="location.reload()">
         Refresh
    </button>
    
    <script>
        // Auto-refresh every 5 minutes
        setTimeout(function(){{
            location.reload();
        }}, 300000);
        
        // Add smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});
    </script>
</body>
</html>
        """
        
        return html
    
    def generate_dashboard(self, output_file: Optional[str] = None) -> str:
        """Generate and save dashboard"""
        self.logger.info("Generating NBA betting dashboard...")
        
        try:
            html_content = self.generate_dashboard_html()
            
            if not output_file:
                output_file = self.dashboard_dir / f"nba_betting_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            else:
                output_file = Path(output_file)
            
            # Write dashboard
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create symlink for latest dashboard
            latest_link = self.dashboard_dir / "nba_betting_dashboard_latest.html"
            if latest_link.exists():
                latest_link.unlink()
            
            try:
                latest_link.symlink_to(output_file.name)
            except OSError:
                # Symlink failed, copy instead
                import shutil
                shutil.copy2(output_file, latest_link)
            
            self.logger.info(f"Dashboard generated: {output_file}")
            self.logger.info(f"Latest dashboard: {latest_link}")
            
            return str(output_file)
        
        except Exception as e:
            self.logger.error(f"Error generating dashboard: {e}")
            raise


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 NBA Dashboard Generator")
    parser.add_argument("--workspace", type=str, default="C:/EQ12",
                       help="EQ12 workspace directory")
    parser.add_argument("--output", type=str,
                       help="Output file path (default: auto-generated)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        generator = NBADashboardGenerator(args.workspace)
        dashboard_file = generator.generate_dashboard(args.output)
        
        print(f" NBA Dashboard generated successfully!")
        print(f" Dashboard file: {dashboard_file}")
        print(f" Open in browser: file://{dashboard_file.replace(os.sep, '/')}")
        
        return 0
    
    except Exception as e:
        print(f" Error generating dashboard: {e}")
        return 1


if __name__ == "__main__":
    exit(main())