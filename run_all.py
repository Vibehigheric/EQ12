#!/usr/bin/env python3
"""
EQ12 Run All - Godlike Betting Orchestration Pipeline
Master pipeline that chains all modules with error handling and consolidated reporting
Runs schedule fetching → odds collection → stats aggregation → prediction → reporting
"""

import asyncio
import json
import logging
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any

warnings.filterwarnings("ignore")

import pandas as pd
import requests
from dotenv import load_dotenv

# Add EQ12 to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv()

# Configure logging first
log_dir = Path("C:/EQ12/logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import EQ12 modules
try:
    from odds_collector import OddsCollector
    from predictor import EQ12Predictor
    from schedule_fetcher import ScheduleFetcher
    from stats_aggregator import StatsAggregator
except ImportError as e:
    logger.warning(f"Import error: {e}")
    print(f"Module import failed: {e}")
    sys.exit(1)
data_dir = Path("C:/EQ12/data")
data_dir.mkdir(exist_ok=True)
reports_dir = Path("C:/EQ12/reports")
reports_dir.mkdir(exist_ok=True)

class EQ12Pipeline:
    """Master orchestration pipeline for EQ12 betting system"""
    
    def __init__(self, target_time: str = "12:00", after: bool = True, timezone: str = "US/Eastern"):
        self.target_time = target_time
        self.after = after
        self.timezone = timezone
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Pipeline state
        self.pipeline_state = {
            'start_time': datetime.now(),
            'schedule_file': None,
            'odds_file': None,
            'stats_file': None,
            'predictions_file': None,
            'games_found': 0,
            'value_bets_found': 0,
            'total_stake': 0,
            'errors': []
        }
        
        # Slack webhook for notifications
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        
        logger.info(f"🚀 EQ12 Pipeline initialized - Target: {target_time}, After: {after}, TZ: {timezone}")
    
    def log_error(self, stage: str, error: Exception):
        """Log and track pipeline errors"""
        error_msg = f"{stage}: {error!s}"
        self.pipeline_state['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
    
    async def run_schedule_fetcher(self) -> bool:
        """Step 1: Fetch game schedules"""
        logger.info("📅 STEP 1: Fetching game schedules...")
        
        try:
            fetcher = ScheduleFetcher(
                target_time=self.target_time,
                after=self.after,
                timezone=self.timezone
            )
            
            df = await fetcher.fetch_all_schedules()
            
            if df.empty:
                logger.warning("⚠️ No games found matching time criteria")
                await self.send_notification("⚠️ EQ12 Pipeline: No games found for specified time criteria")
                return False
            
            self.pipeline_state['games_found'] = len(df)
            
            # Save schedule
            filepath = fetcher.save_schedule(df)
            self.pipeline_state['schedule_file'] = filepath
            
            fetcher.print_summary(df)
            
            logger.info(f"✅ Schedule fetcher completed - {len(df)} games found")
            return True
            
        except Exception as e:
            self.log_error("Schedule Fetcher", e)
            return False
    
    async def run_odds_collector(self) -> bool:
        """Step 2: Collect odds data"""
        logger.info("🎰 STEP 2: Collecting odds data...")
        
        try:
            collector = OddsCollector(concurrency=5)
            
            # Collect odds
            odds_df = await collector.collect_all_odds()
            
            if odds_df.empty:
                logger.warning("⚠️ No odds data collected")
                return False
            
            # Add implied probabilities
            odds_df = collector.calculate_implied_probabilities(odds_df)
            
            # Match with schedule if available
            merged_df = None
            if self.pipeline_state['schedule_file']:
                merged_df = collector.match_with_schedule(odds_df, self.pipeline_state['schedule_file'])
            
            # Find arbitrage opportunities
            arb_df = collector.find_arbitrage_opportunities(odds_df)
            
            # Save data
            filepaths = collector.save_odds_data(odds_df, merged_df, arb_df)
            self.pipeline_state['odds_file'] = filepaths.get('merged') or filepaths.get('odds')
            
            collector.print_summary(odds_df, arb_df)
            
            logger.info(f"✅ Odds collector completed - {len(odds_df)} odds entries")
            return True
            
        except Exception as e:
            self.log_error("Odds Collector", e)
            return False
    
    async def run_stats_aggregator(self) -> bool:
        """Step 3: Aggregate team statistics"""
        logger.info("📊 STEP 3: Aggregating team statistics...")
        
        try:
            if not self.pipeline_state['odds_file']:
                logger.error("❌ No odds file available for stats aggregation")
                return False
            
            # Load schedule+odds data
            schedule_odds_df = pd.read_csv(self.pipeline_state['odds_file'])
            
            aggregator = StatsAggregator(cache_ttl=3600)
            
            # Aggregate team stats
            stats_df = await aggregator.aggregate_team_stats(schedule_odds_df)
            
            if stats_df.empty:
                logger.warning("⚠️ No team stats collected")
                return False
            
            # Save data
            filepaths = aggregator.save_stats_data(stats_df)
            self.pipeline_state['stats_file'] = filepaths.get('parquet') or filepaths.get('csv')
            
            aggregator.print_summary(stats_df)
            
            logger.info(f"✅ Stats aggregator completed - {len(stats_df)} teams analyzed")
            return True
            
        except Exception as e:
            self.log_error("Stats Aggregator", e)
            return False
    
    async def run_predictor(self, model_type: str = "logistic", bankroll: float = 1000.0, min_edge: float = 5.0) -> bool:
        """Step 4: Generate predictions and find value bets"""
        logger.info("🔮 STEP 4: Generating predictions and finding value bets...")
        
        try:
            if not self.pipeline_state['odds_file'] or not self.pipeline_state['stats_file']:
                logger.error("❌ Missing odds or stats file for prediction")
                return False
            
            # Load data
            schedule_odds_df = pd.read_csv(self.pipeline_state['odds_file'])
            
            if self.pipeline_state['stats_file'].endswith('.parquet'):
                stats_df = pd.read_parquet(self.pipeline_state['stats_file'])
            else:
                stats_df = pd.read_csv(self.pipeline_state['stats_file'])
            
            # Initialize predictor
            predictor = EQ12Predictor(model_type=model_type, bankroll=bankroll)
            
            # Build features
            features_df = predictor.build_features(schedule_odds_df, stats_df)
            
            if features_df.empty:
                logger.warning("⚠️ No features built for prediction")
                return False
            
            # Train models (using synthetic data for demonstration)
            training_results = predictor.train_model(features_df, save_model=False)
            
            # Make predictions
            predictions_df = predictor.predict(features_df)
            
            if predictions_df.empty:
                logger.warning("⚠️ No predictions generated")
                return False
            
            # Calculate betting metrics
            betting_df = predictor.calculate_betting_metrics(predictions_df, schedule_odds_df)
            
            # Find value bets
            value_bets_df = predictor.find_value_bets(betting_df, min_edge=min_edge, min_stake=10.0)
            
            # Save results
            predictions_path = reports_dir / f"predictions_{self.timestamp}.csv"
            predictions_df.to_csv(predictions_path, index=False)
            self.pipeline_state['predictions_file'] = str(predictions_path)
            
            if not betting_df.empty:
                betting_path = reports_dir / f"betting_opportunities_{self.timestamp}.csv"
                betting_df.to_csv(betting_path, index=False)
            
            if not value_bets_df.empty:
                value_path = reports_dir / f"value_bets_{self.timestamp}.csv"
                value_bets_df.to_csv(value_path, index=False)
                
                self.pipeline_state['value_bets_found'] = len(value_bets_df)
                self.pipeline_state['total_stake'] = value_bets_df['kelly_stake'].sum()
            
            # Print prediction summary
            logger.info(f"🎯 Predictions: {len(predictions_df)} games")
            logger.info(f"💰 Value bets: {len(value_bets_df)}")
            
            if not value_bets_df.empty:
                avg_edge = value_bets_df['edge_percent'].mean()
                total_profit_potential = value_bets_df['profit_potential'].sum()
                logger.info(f"📈 Average edge: {avg_edge:.1f}%")
                logger.info(f"💵 Total stake: ${self.pipeline_state['total_stake']:.0f}")
                logger.info(f"🎯 Profit potential: ${total_profit_potential:.0f}")
            
            return True
            
        except Exception as e:
            self.log_error("Predictor", e)
            return False
    
    def generate_consolidated_report(self) -> dict[str, Any]:
        """Generate consolidated JSON and CSV report"""
        logger.info("📋 Generating consolidated report...")
        
        end_time = datetime.now()
        runtime = (end_time - self.pipeline_state['start_time']).total_seconds()
        
        # Load results if available
        predictions_summary = {}
        value_bets_summary = []
        
        try:
            if self.pipeline_state['predictions_file']:
                predictions_df = pd.read_csv(self.pipeline_state['predictions_file'])
                predictions_summary = {
                    'total_games': len(predictions_df),
                    'leagues': predictions_df['league'].value_counts().to_dict()
                }
            
            # Load top value bets
            value_bets_path = reports_dir / f"value_bets_{self.timestamp}.csv"
            if value_bets_path.exists():
                value_bets_df = pd.read_csv(value_bets_path)
                
                for _, bet in value_bets_df.head(10).iterrows():
                    value_bets_summary.append({
                        'league': bet.get('league'),
                        'game': f"{bet.get('away_team')} @ {bet.get('home_team')}",
                        'bet': bet.get('bet_team_name'),
                        'odds': int(bet.get('odds', 0)),
                        'edge_percent': round(bet.get('edge_percent', 0), 1),
                        'kelly_stake': round(bet.get('kelly_stake', 0), 0),
                        'profit_potential': round(bet.get('profit_potential', 0), 0)
                    })
        
        except Exception as e:
            logger.warning(f"Error loading results for report: {e}")
        
        # Build comprehensive report
        report = {
            'pipeline_info': {
                'timestamp': self.timestamp,
                'start_time': self.pipeline_state['start_time'].isoformat(),
                'end_time': end_time.isoformat(),
                'runtime_seconds': runtime,
                'target_time': self.target_time,
                'after_flag': self.after,
                'timezone': self.timezone
            },
            'execution_summary': {
                'games_found': self.pipeline_state['games_found'],
                'value_bets_found': self.pipeline_state['value_bets_found'],
                'total_stake': round(self.pipeline_state['total_stake'], 0),
                'errors_count': len(self.pipeline_state['errors']),
                'success': len(self.pipeline_state['errors']) == 0
            },
            'files_generated': {
                'schedule': self.pipeline_state['schedule_file'],
                'odds': self.pipeline_state['odds_file'],
                'stats': self.pipeline_state['stats_file'],
                'predictions': self.pipeline_state['predictions_file']
            },
            'predictions_summary': predictions_summary,
            'value_bets': value_bets_summary,
            'errors': self.pipeline_state['errors']
        }
        
        # Save consolidated report
        report_path = reports_dir / f"consolidated_report_{self.timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Create CSV summary of top picks
        if value_bets_summary:
            csv_data = []
            for i, bet in enumerate(value_bets_summary, 1):
                csv_data.append({
                    'Rank': i,
                    'League': bet['league'],
                    'Game': bet['game'],
                    'Bet': bet['bet'],
                    'Odds': f"{bet['odds']:+d}",
                    'Edge': f"{bet['edge_percent']}%",
                    'Stake': f"${bet['kelly_stake']}",
                    'Profit': f"${bet['profit_potential']}"
                })
            
            csv_df = pd.DataFrame(csv_data)
            csv_path = reports_dir / f"top_picks_{self.timestamp}.csv"
            csv_df.to_csv(csv_path, index=False)
        
        logger.info(f"📋 Consolidated report saved: {report_path}")
        return report
    
    async def send_notification(self, message: str):
        """Send notification to Slack if webhook configured"""
        if not self.slack_webhook:
            return
        
        try:
            payload = {
                "text": message,
                "username": "EQ12 Godlike Bot",
                "icon_emoji": ":robot_face:"
            }
            
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("📱 Slack notification sent")
            
        except Exception as e:
            logger.warning(f"Failed to send Slack notification: {e}")
    
    async def send_success_notification(self, report: dict[str, Any]):
        """Send detailed success notification"""
        if not self.slack_webhook:
            return
        
        summary = report['execution_summary']
        
        if summary['value_bets_found'] > 0:
            message = f"""🔥 *EQ12 Godlike Betting Pipeline Success!*
            
📊 *Results Summary:*
• Games Analyzed: {summary['games_found']}
• Value Bets Found: {summary['value_bets_found']}
• Total Stake: ${summary['total_stake']:,.0f}
• Runtime: {report['pipeline_info']['runtime_seconds']:.0f}s

🎯 *Top Picks:*"""
            
            for bet in report['value_bets'][:3]:
                message += f"\n• {bet['bet']} ({bet['odds']:+d}) - {bet['edge_percent']}% edge, ${bet['kelly_stake']} stake"
            
            if len(report['value_bets']) > 3:
                message += f"\n... and {len(report['value_bets']) - 3} more picks"
        else:
            message = f"""⚠️ *EQ12 Pipeline Complete - No Value Bets*
            
📊 Games Analyzed: {summary['games_found']}
🎯 No profitable opportunities found today
⏰ Runtime: {report['pipeline_info']['runtime_seconds']:.0f}s"""
        
        await self.send_notification(message)
    
    async def run_pipeline(self, model_type: str = "logistic", bankroll: float = 1000.0, min_edge: float = 5.0) -> dict[str, Any]:
        """Execute the complete pipeline"""
        logger.info("🚀 STARTING EQ12 GODLIKE BETTING PIPELINE")
        logger.info("=" * 60)
        
        # Step 1: Fetch schedules
        schedule_success = await self.run_schedule_fetcher()
        
        if not schedule_success:
            report = self.generate_consolidated_report()
            await self.send_notification("❌ EQ12 Pipeline failed at schedule fetching stage")
            return report
        
        # Step 2: Collect odds
        odds_success = await self.run_odds_collector()
        
        if not odds_success:
            report = self.generate_consolidated_report()
            await self.send_notification("❌ EQ12 Pipeline failed at odds collection stage")
            return report
        
        # Step 3: Aggregate stats
        stats_success = await self.run_stats_aggregator()
        
        if not stats_success:
            report = self.generate_consolidated_report()
            await self.send_notification("❌ EQ12 Pipeline failed at stats aggregation stage")
            return report
        
        # Step 4: Generate predictions
        prediction_success = await self.run_predictor(model_type, bankroll, min_edge)
        
        # Generate final report
        report = self.generate_consolidated_report()
        
        # Send notifications
        if prediction_success and len(self.pipeline_state['errors']) == 0:
            await self.send_success_notification(report)
        else:
            await self.send_notification("⚠️ EQ12 Pipeline completed with errors or warnings")
        
        # Print final summary
        logger.info("=" * 60)
        logger.info("🏆 EQ12 PIPELINE FINAL SUMMARY")
        logger.info("=" * 60)
        logger.info(f"⏰ Runtime: {report['pipeline_info']['runtime_seconds']:.0f} seconds")
        logger.info(f"🎮 Games Found: {report['execution_summary']['games_found']}")
        logger.info(f"🎯 Value Bets: {report['execution_summary']['value_bets_found']}")
        logger.info(f"💰 Total Stake: ${report['execution_summary']['total_stake']:.0f}")
        logger.info(f"❌ Errors: {report['execution_summary']['errors_count']}")
        
        if report['value_bets']:
            logger.info("\n🔥 TOP VALUE BETS:")
            for i, bet in enumerate(report['value_bets'][:5], 1):
                logger.info(f"  {i}. {bet['bet']} ({bet['odds']:+d}) - {bet['edge_percent']}% edge")
        
        success_status = "✅ SUCCESS" if report['execution_summary']['success'] else "⚠️ COMPLETED WITH ERRORS"
        logger.info(f"\n🎉 EQ12 PIPELINE {success_status}")
        
        return report

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Godlike Betting Pipeline")
    parser.add_argument("--time", default="12:00", help="Target time (default: 12:00)")
    parser.add_argument("--after", action="store_true", default=True, help="Include games at or after time")
    parser.add_argument("--exact", action="store_true", help="Include games within ±15min of time")
    parser.add_argument("--tz", default="US/Eastern", help="Timezone (default: US/Eastern)")
    parser.add_argument("--model", choices=['logistic', 'rf', 'xgboost'], default='logistic', help="ML model type")
    parser.add_argument("--bankroll", type=float, default=1000.0, help="Bankroll amount")
    parser.add_argument("--min-edge", type=float, default=5.0, help="Minimum edge percentage for value bets")
    parser.add_argument("--slack-webhook", help="Slack webhook URL for notifications")
    
    args = parser.parse_args()
    
    # Override environment with command line
    if args.slack_webhook:
        os.environ["SLACK_WEBHOOK_URL"] = args.slack_webhook
    
    # Handle exact flag
    after_flag = not args.exact if args.exact else args.after
    
    try:
        # Initialize and run pipeline
        pipeline = EQ12Pipeline(
            target_time=args.time,
            after=after_flag,
            timezone=args.tz
        )
        
        report = await pipeline.run_pipeline(
            model_type=args.model,
            bankroll=args.bankroll,
            min_edge=args.min_edge
        )
        
        return report
        
    except KeyboardInterrupt:
        logger.info("🛑 Pipeline interrupted by user")
        return None
    except Exception as e:
        logger.error(f"💥 Pipeline failed with unexpected error: {e}")
        raise

if __name__ == "__main__":
    # Handle event loop for Windows
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
    except:
        pass
    
    asyncio.run(main())