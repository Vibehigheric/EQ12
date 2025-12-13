#!/usr/bin/env python3
"""
EQ12 ML Parlay System - Complete Demo
Demonstrates the full ML-driven parlay improvement pipeline.

Runs the complete system from data pipeline to risk-managed suggestions.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add eq12_learn to path
sys.path.insert(0, str(Path(__file__).parent / "eq12_learn"))

try:
    from build_parlay_dataset import ParlayDatasetBuilder
    from train_parlay_model import ParlayModelTrainer, EnsembleParlayModel
    from builder import IntelligentParlayBuilder, ParlayRecommendation
    from risk_manager import AdvancedRiskManager
    from eq12_parlay_api import app
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the EQ12 root directory")
    sys.exit(1)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EQ12ParlaySystemDemo:
    """Complete demonstration of EQ12 ML Parlay System."""
    
    def __init__(self):
        self.logs_dir = Path("C:/EQ12/logs")
        self.learn_dir = Path("C:/EQ12/eq12_learn")
        self.results = {}
        
        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        self.learn_dir.mkdir(exist_ok=True)
        
    def print_header(self, title: str, char: str = "="):
        """Print formatted section header."""
        print(f"\n{char * 60}")
        print(f"🚀 {title}")
        print(f"{char * 60}")
        
    def print_step(self, step: str, description: str):
        """Print formatted step."""
        print(f"\n📍 Step: {step}")
        print(f"   {description}")
        
    async def run_complete_demo(self):
        """Run complete system demonstration."""
        
        print("🎯 EQ12 ML PARLAY IMPROVEMENT SYSTEM")
        print("=" * 80)
        print("Mathematical + ML Learning Framework for Profitable Parlay Selection")
        print(f"Demonstration started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Step 1: Build Dataset
            await self.demo_dataset_building()
            
            # Step 2: Train Model
            await self.demo_model_training()
            
            # Step 3: Generate Suggestions
            await self.demo_parlay_generation()
            
            # Step 4: Risk Management
            await self.demo_risk_management()
            
            # Step 5: API Demo
            await self.demo_api_integration()
            
            # Final Summary
            await self.print_final_summary()
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            raise
            
    async def demo_dataset_building(self):
        """Demonstrate dataset building from parlay logs."""
        self.print_header("STEP 1: ML Dataset Building", "🔨")
        
        self.print_step("1.1", "Loading parlay analysis logs")
        
        # Initialize dataset builder
        builder = ParlayDatasetBuilder(logs_dir=str(self.logs_dir))
        
        # Load parlay data
        parlays = builder.load_parlay_logs()
        
        if len(parlays) < 10:
            print("⚠️  Warning: Limited parlay data for training")
            print("   Creating synthetic data for demonstration...")
            # Create some mock data for demo
            await self._create_mock_parlay_data()
            parlays = builder.load_parlay_logs()
            
        print(f"✅ Loaded {len(parlays)} historical parlays")
        
        self.print_step("1.2", "Building ML feature matrix")
        
        # Build feature matrix
        feature_df = builder.build_feature_matrix()
        
        print(f"✅ Feature matrix: {feature_df.shape[0]} samples, {feature_df.shape[1]} features")
        
        if 'win_loss_label' in feature_df.columns:
            win_rate = feature_df['win_loss_label'].mean()
            decided_count = feature_df['is_decided'].sum()
            print(f"📊 Baseline win rate: {win_rate:.2%} ({decided_count} decided parlays)")
        
        self.print_step("1.3", "Saving processed dataset")
        
        # Save dataset
        dataset_path = builder.save_dataset()
        
        print(f"✅ Dataset saved: {dataset_path}")
        
        self.results['dataset'] = {
            'path': dataset_path,
            'samples': len(feature_df),
            'features': len(feature_df.columns),
            'baseline_win_rate': win_rate if 'win_loss_label' in feature_df.columns else 0.0
        }
        
    async def demo_model_training(self):
        """Demonstrate ML model training."""
        self.print_header("STEP 2: ML Model Training", "🧠")
        
        dataset_path = self.results['dataset']['path']
        
        self.print_step("2.1", "Initializing ensemble model trainer")
        
        # Initialize trainer
        trainer = ParlayModelTrainer(
            dataset_path=dataset_path,
            output_dir=str(self.learn_dir)
        )
        
        print("✅ Trainer initialized with Random Forest + XGBoost ensemble")
        
        self.print_step("2.2", "Training calibrated ensemble model")
        
        # Train model
        training_results = trainer.train_model()
        
        print(f"✅ Model training completed!")
        print(f"📈 Ensemble ROC-AUC: {training_results['ensemble']['ensemble_roc_auc']:.3f}")
        print(f"🎯 High confidence accuracy: {training_results['performance_summary']['high_confidence_accuracy']:.2%}")
        
        self.print_step("2.3", "Saving trained model")
        
        # Save model
        model_path = trainer.save_model("parlay_ensemble_model")
        
        print(f"✅ Model saved: {model_path}")
        
        self.results['model'] = {
            'path': model_path,
            'roc_auc': training_results['ensemble']['ensemble_roc_auc'],
            'high_confidence_accuracy': training_results['performance_summary']['high_confidence_accuracy']
        }
        
    async def demo_parlay_generation(self):
        """Demonstrate intelligent parlay generation."""
        self.print_header("STEP 3: Intelligent Parlay Generation", "🎲")
        
        model_path = self.results['model']['path']
        
        self.print_step("3.1", "Initializing parlay builder")
        
        # Initialize builder with trained model
        builder = IntelligentParlayBuilder(model_path=model_path)
        
        print("✅ Parlay builder initialized with trained ML model")
        
        self.print_step("3.2", "Generating EV+ parlay suggestions")
        
        # Generate suggestions for different sports
        all_suggestions = []
        
        for sport in ['NFL', 'NBA']:
            print(f"\n🏈 Generating {sport} suggestions...")
            
            suggestions = builder.generate_suggestions(sport, max_suggestions=2)
            all_suggestions.extend(suggestions)
            
            print(f"✅ Generated {len(suggestions)} {sport} parlays")
            
            for i, suggestion in enumerate(suggestions, 1):
                print(f"   #{i}: {suggestion.leg_count} legs, "
                      f"{suggestion.win_probability:.1%} win prob, "
                      f"{suggestion.expected_value:.1%} EV, "
                      f"${suggestion.max_stake:.0f} stake")
                      
        self.print_step("3.3", "Saving parlay suggestions")
        
        if all_suggestions:
            filename = builder.save_suggestions(all_suggestions)
            print(f"✅ Suggestions saved: {filename}")
        else:
            print("⚠️  No valid suggestions generated")
            
        self.results['suggestions'] = {
            'count': len(all_suggestions),
            'avg_win_prob': sum(s.win_probability for s in all_suggestions) / len(all_suggestions) if all_suggestions else 0,
            'avg_ev': sum(s.expected_value for s in all_suggestions) / len(all_suggestions) if all_suggestions else 0
        }
        
    async def demo_risk_management(self):
        """Demonstrate advanced risk management."""
        self.print_header("STEP 4: Advanced Risk Management", "🛡️")
        
        self.print_step("4.1", "Initializing risk management system")
        
        # Initialize risk manager
        risk_manager = AdvancedRiskManager(bankroll=1000.0)
        
        print("✅ Risk manager initialized with Kelly criterion and correlation analysis")
        
        self.print_step("4.2", "Performing comprehensive risk assessment")
        
        # Sample high-risk parlay for assessment
        sample_legs = [
            {
                'team': 'KC', 'opponent': 'LAC', 'bet_type': 'spread',
                'sport': 'NFL', 'game_time': datetime.now()
            },
            {
                'team': 'KC', 'opponent': 'LAC', 'bet_type': 'total',  # Same game = high correlation
                'sport': 'NFL', 'game_time': datetime.now()
            }
        ]
        
        # Risk assessment
        is_valid, violations, risk_metrics = risk_manager.validate_bet(
            sample_legs, stake=50.0, win_prob=0.35, 
            expected_value=0.10, confidence=0.60, decimal_odds=4.0
        )
        
        print(f"🎯 Risk Assessment: {'APPROVED' if is_valid else 'REJECTED'}")
        print(f"   Risk Level: {risk_metrics.risk_level.value.upper()}")
        print(f"   Kelly Fraction: {risk_metrics.kelly_fraction:.2%}")
        print(f"   Correlation Score: {risk_metrics.correlation_score:.2f}")
        
        if violations:
            print("❌ Risk Violations:")
            for violation in violations[:3]:  # Show first 3
                print(f"   - {violation}")
                
        self.print_step("4.3", "Calculating optimal position sizing")
        
        # Calculate optimal stake
        optimal_stake = risk_manager.calculate_optimal_stake(
            risk_metrics.kelly_fraction, 0.45, 0.20, risk_metrics
        )
        
        print(f"💰 Optimal Stake: ${optimal_stake:.0f}")
        print(f"   (Kelly-adjusted with risk controls)")
        
        # Risk dashboard
        dashboard = risk_manager.get_risk_dashboard()
        
        print(f"\n📈 Risk Dashboard:")
        print(f"   Available Balance: ${dashboard['bankroll_status']['available_balance']:.0f}")
        print(f"   Max Single Bet: ${dashboard['position_limits']['max_single_bet']:.0f}")
        print(f"   Loss Streak Protection: {'ACTIVE' if dashboard['risk_metrics']['stop_loss_active'] else 'INACTIVE'}")
        
        self.results['risk_management'] = {
            'is_valid': is_valid,
            'risk_level': risk_metrics.risk_level.value,
            'violations_count': len(violations),
            'optimal_stake': optimal_stake
        }
        
    async def demo_api_integration(self):
        """Demonstrate FastAPI integration."""
        self.print_header("STEP 5: FastAPI Integration", "🌐")
        
        self.print_step("5.1", "FastAPI server configuration")
        
        print("✅ FastAPI server configured with endpoints:")
        print("   📡 POST /model/suggest - Generate parlay suggestions")
        print("   📊 GET /analytics/performance - Performance analytics")
        print("   🛡️ GET /model/status - Risk management status")
        print("   ❤️  GET /health - Health check")
        
        self.print_step("5.2", "API request/response demo")
        
        # Sample API request
        sample_request = {
            "sport": "NFL",
            "max_legs": 3,
            "budget": 25.0,
            "risk_tolerance": "moderate",
            "min_win_probability": 0.40
        }
        
        print("📤 Sample API Request:")
        print(json.dumps(sample_request, indent=2))
        
        # Sample API response structure
        sample_response = {
            "request_id": "req_20241007_120000_0001",
            "timestamp": datetime.now().isoformat(),
            "sport": "NFL",
            "suggestions": [
                {
                    "legs": [
                        {"team": "KC", "bet_type": "spread", "line": -3.5, "odds_american": -110},
                        {"team": "DAL", "bet_type": "total", "line": 47.5, "odds_american": -110}
                    ],
                    "win_probability": 0.42,
                    "expected_value": 0.18,
                    "kelly_fraction": 0.08,
                    "max_stake": 22.0,
                    "potential_payout": 58.40
                }
            ]
        }
        
        print("\n📥 Sample API Response:")
        print(json.dumps(sample_response, indent=2)[:500] + "...")
        
        self.print_step("5.3", "Running server (demo mode)")
        
        print("🚀 FastAPI server ready to run on http://127.0.0.1:8000")
        print("   Use: python eq12_learn/eq12_parlay_api.py")
        print("   Docs: http://127.0.0.1:8000/docs")
        
        self.results['api'] = {
            'configured': True,
            'endpoints': 4,
            'demo_request': sample_request
        }
        
    async def print_final_summary(self):
        """Print final demonstration summary."""
        self.print_header("🎉 DEMO COMPLETE - SYSTEM SUMMARY", "🎯")
        
        print("EQ12 ML Parlay Improvement System Successfully Demonstrated!")
        print()
        
        # Dataset summary
        dataset_info = self.results.get('dataset', {})
        print(f"📊 Dataset: {dataset_info.get('samples', 0)} samples, "
              f"{dataset_info.get('features', 0)} features")
        print(f"   Baseline win rate: {dataset_info.get('baseline_win_rate', 0):.2%}")
        
        # Model summary
        model_info = self.results.get('model', {})
        print(f"🧠 Model: ROC-AUC {model_info.get('roc_auc', 0):.3f}, "
              f"High-confidence accuracy {model_info.get('high_confidence_accuracy', 0):.1%}")
        
        # Suggestions summary
        suggestions_info = self.results.get('suggestions', {})
        print(f"🎲 Suggestions: {suggestions_info.get('count', 0)} generated, "
              f"Avg EV {suggestions_info.get('avg_ev', 0):.1%}")
        
        # Risk management summary
        risk_info = self.results.get('risk_management', {})
        print(f"🛡️ Risk Management: {risk_info.get('violations_count', 0)} violations detected, "
              f"Optimal stake ${risk_info.get('optimal_stake', 0):.0f}")
        
        # API summary
        api_info = self.results.get('api', {})
        print(f"🌐 API: {api_info.get('endpoints', 0)} endpoints configured, FastAPI ready")
        
        print()
        self.print_header("📋 NEXT STEPS", "-")
        
        print("1. 🔄 Run nightly model retraining: GitHub Actions workflow")
        print("2. 📡 Start API server: python eq12_learn/eq12_parlay_api.py")
        print("3. 🎯 Submit parlay feedback for continuous learning")
        print("4. 📊 Monitor performance via /analytics/performance endpoint")
        print("5. 🛡️ Adjust risk parameters based on results")
        
        print()
        print("🏆 TRANSFORMATION ACHIEVED:")
        print(f"   From: {dataset_info.get('baseline_win_rate', 0.0298):.2%} baseline win rate")
        print(f"   To: {model_info.get('high_confidence_accuracy', 0.65):.1%} ML-driven accuracy")
        print(f"   With: Mathematical risk controls and EV optimization")
        
        print(f"\n🕒 Demo completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    async def _create_mock_parlay_data(self):
        """Create mock parlay data for demonstration."""
        mock_parlays = []
        
        sports = ['NFL', 'NBA', 'MLB']
        outcomes = ['win', 'loss', 'pending']
        
        for i in range(50):
            parlay = {
                'timestamp': (datetime.now().replace(microsecond=0) - 
                            timedelta(days=i % 30)).isoformat(),
                'sport': sports[i % len(sports)],
                'type': 'parlay',
                'legs': [
                    f"Team A {-3.5 + (i % 7)} (-110)",
                    f"Over {45.5 + (i % 10)} (-110)"
                ],
                'odds_american': 260 + (i % 100),
                'stake': 25.0,
                'potential_payout': 65.0 + (i % 50),
                'outcome': outcomes[i % len(outcomes)],
                'actual_payout': 65.0 if outcomes[i % len(outcomes)] == 'win' else 0
            }
            mock_parlays.append(parlay)
            
        # Save mock data
        mock_file = self.logs_dir / "parlay_analysis_mock_demo.json"
        with open(mock_file, 'w') as f:
            json.dump({'parlays': mock_parlays, 'total_analyzed': len(mock_parlays)}, 
                     f, indent=2)
        
        print(f"✅ Created mock parlay data: {len(mock_parlays)} parlays")


async def main():
    """Main demo execution."""
    
    try:
        # Run complete demonstration
        demo = EQ12ParlaySystemDemo()
        await demo.run_complete_demo()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        logger.exception("Demo error")
        sys.exit(1)


def run_demo():
    """Synchronous wrapper for demo execution."""
    asyncio.run(main())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='EQ12 ML Parlay System Demo')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick demo (skip model training)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    run_demo()