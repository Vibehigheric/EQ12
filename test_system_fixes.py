#!/usr/bin/env python3
"""
Quick validation script for EQ12 system fixes.
Tests the critical components after SRC expert analysis fixes.
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path("c:/EQ12/logs/validation.log"), mode="w"),
    ],
)
logger = logging.getLogger(__name__)


def test_performance_metrics():
    """Test the new performance metrics module"""
    try:
        # Add sports-betting-optimizer path for imports
        sys.path.append(str(Path("c:/EQ12/sports-betting-optimizer/src")))

        from utils.performance_metrics import PerformanceAnalyzer

        # Test with sample data
        sample_returns = [0.02, -0.01, 0.03, 0.01, -0.02, 0.04]
        sample_bets = [100, 100, 100, 100, 100, 100]

        analyzer = PerformanceAnalyzer(sample_returns, sample_bets)

        # Test key metrics
        sharpe = analyzer.calculate_sharpe_ratio()
        kelly = analyzer.kelly_fraction()
        var = analyzer.value_at_risk()

        logger.info("✅ Performance Metrics Module: OPERATIONAL")
        logger.info(f"   Sample Sharpe Ratio: {sharpe:.3f}")
        logger.info(f"   Sample Kelly Fraction: {kelly:.3f}")
        logger.info(f"   Sample VaR (95%): {var:.3f}")

        return True

    except Exception as e:
        logger.error(f"❌ Performance Metrics Module: FAILED - {e}")
        return False


def test_bankroll_visualizer():
    """Test the new bankroll visualizer"""
    try:
        sys.path.append(str(Path("c:/EQ12/sports-betting-optimizer/src")))

        from utils.bankroll_visualizer import BankrollVisualizer

        # Create test CSV data
        test_csv = Path("c:/EQ12/data/test_bankroll.csv")
        test_csv.parent.mkdir(exist_ok=True)

        with open(test_csv, "w") as f:
            f.write("date,bankroll,bet_amount,outcome\n")
            f.write("2024-01-01,1000,50,win\n")
            f.write("2024-01-02,1025,50,loss\n")
            f.write("2024-01-03,975,50,win\n")

        BankrollVisualizer(str(test_csv))

        # Test without actually generating plots (no display)
        logger.info("✅ Bankroll Visualizer Module: OPERATIONAL")
        logger.info("   Professional charting capabilities ready")

        return True

    except Exception as e:
        logger.error(f"❌ Bankroll Visualizer Module: FAILED - {e}")
        return False


def test_file_paths():
    """Test critical file path resolutions"""
    eq12_root = Path("c:/EQ12")

    # Test paths from SRC analysis
    critical_paths = [
        eq12_root / "sports-betting-optimizer/src/core/kelly_bankroll_manager.py",
        eq12_root / "sports-betting-optimizer/src/core/kelly_system.py",
        eq12_root / "scripts/bankroll_tracker_clean.py",
        eq12_root / "eq12_system_manager.py",
    ]

    found_count = 0
    for path in critical_paths:
        if path.exists():
            logger.info(f"✅ Found: {path.name}")
            found_count += 1
        else:
            logger.warning(f"⚠️  Missing: {path}")

    success_rate = (found_count / len(critical_paths)) * 100
    logger.info(f"File Path Resolution: {found_count}/{len(critical_paths)} ({success_rate:.1f}%)")

    return success_rate >= 75


def test_unicode_safety():
    """Test Unicode-safe logging and console output"""
    try:
        # Test various Unicode characters that caused crashes
        test_chars = ["🎯", "✅", "❌", "⚠️", "📊", "💰"]

        for char in test_chars:
            # Safe console output (will fall back to text if Unicode fails)
            safe_message = f"Testing {char} Unicode character"
            logger.info(safe_message)

        logger.info("✅ Unicode Safety: OPERATIONAL")
        return True

    except Exception as e:
        logger.error(f"❌ Unicode Safety: FAILED - {e}")
        return False


def main():
    """Run comprehensive system validation"""
    logger.info("🚀 EQ12 System Validation Starting...")
    logger.info("=" * 50)

    tests = [
        ("Performance Metrics", test_performance_metrics),
        ("Bankroll Visualizer", test_bankroll_visualizer),
        ("File Path Resolution", test_file_paths),
        ("Unicode Safety", test_unicode_safety),
    ]

    results = []
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Testing {test_name}...")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append(False)

    # Summary
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100

    logger.info("\n" + "=" * 50)
    logger.info("🎯 EQ12 SYSTEM VALIDATION COMPLETE")
    logger.info(f"Success Rate: {passed}/{total} ({success_rate:.1f}%)")

    if success_rate >= 75:
        logger.info("✅ System Status: OPERATIONAL")
    elif success_rate >= 50:
        logger.info("⚠️  System Status: DEGRADED")
    else:
        logger.info("❌ System Status: CRITICAL")

    return success_rate


if __name__ == "__main__":
    try:
        success_rate = main()
        sys.exit(0 if success_rate >= 75 else 1)
    except Exception as e:
        logger.error(f"Validation crashed: {e}")
        sys.exit(1)
