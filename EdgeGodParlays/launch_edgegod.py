#!/usr/bin/env python3
"""
EQ12 EdgeGod Engine Launcher
Production-ready launcher with configuration management and monitoring
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from edgegod_expert_engine import app, expert_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("edgegod_engine.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def load_configuration():
    """Load and validate configuration"""
    # Load environment variables
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        logger.info(f"Loaded configuration from {env_file}")
    else:
        logger.info("No .env file found, using environment variables")

    # Validate required environment variables
    required_vars = ["ODDS_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]

    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.info("Please set these variables or create a .env file")
        logger.info("See .env.example for reference")
        return False

    # Log configuration (without exposing secrets)
    logger.info("Configuration loaded successfully:")
    logger.info(f"  Bankroll Base: ${os.environ.get('BANKROLL_BASE', '1000')}")
    logger.info(f"  Min Edge Threshold: {os.environ.get('MIN_EDGE_THRESHOLD', '0.02')}")
    logger.info(f"  Max Bet Percentage: {os.environ.get('MAX_SINGLE_BET_PERCENTAGE', '0.05')}")
    logger.info(f"  EQ12 Logs: {os.environ.get('EQ12_LOGS', './logs')}")

    return True


def setup_directories():
    """Create required directories"""
    logs_dir = Path(os.environ.get("EQ12_LOGS", "./logs"))
    logs_dir.mkdir(exist_ok=True, parents=True)
    logger.info(f"Logs directory ready: {logs_dir}")


async def run_initial_analysis():
    """Run initial analysis on startup"""
    logger.info("Running initial analysis...")
    try:
        results = await expert_engine.analyze_full_slate("today")
        logger.info(f"Initial analysis complete: {results['summary']}")
    except Exception as e:
        logger.error(f"Initial analysis failed: {e}")


def main():
    """Main entry point"""
    logger.info("🚀 Starting EQ12 EdgeGod Expert Engine")

    # Load and validate configuration
    if not load_configuration():
        sys.exit(1)

    # Setup directories
    setup_directories()

    # Run initial analysis
    try:
        asyncio.run(run_initial_analysis())
    except Exception as e:
        logger.error(f"Startup analysis failed: {e}")

    # Start FastAPI server
    logger.info("Starting EdgeGod FastAPI Server: http://0.0.0.0:8080")
    logger.info("API Documentation available at: http://0.0.0.0:8080/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
        access_log=True,
        reload=os.environ.get("DEBUG_MODE", "false").lower() == "true",
    )


if __name__ == "__main__":
    main()
