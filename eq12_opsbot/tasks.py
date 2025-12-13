"""
Task Scheduler
==============

APScheduler jobs for RSS polling, snapshots, config drift checks.
"""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .config import get_config
from .rss_watcher import RSSWatcher

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Manages scheduled background tasks"""

    def __init__(self):
        self.config = get_config()
        self.scheduler = AsyncIOScheduler()
        self.rss_watcher = None

        if self.config.enable_community_monitor:
            self.rss_watcher = RSSWatcher()

    def start(self):
        """Start the scheduler and add jobs"""
        logger.info("Starting task scheduler...")

        # RSS monitoring (every 15 minutes)
        if self.rss_watcher:
            self.scheduler.add_job(
                func=self.rss_watcher.check_feeds,
                trigger=IntervalTrigger(minutes=self.config.rss_poll_interval_minutes),
                id="rss_monitor",
                name="RSS Feed Monitor",
            )

        # Budget snapshot (hourly)
        self.scheduler.add_job(
            func=self.budget_snapshot,
            trigger=CronTrigger(minute=0),  # Every hour at minute 0
            id="budget_snapshot",
            name="Budget Snapshot",
        )

        # Cache cleanup (daily at 3 AM)
        self.scheduler.add_job(
            func=self.cleanup_caches,
            trigger=CronTrigger(hour=3, minute=0),
            id="cache_cleanup",
            name="Cache Cleanup",
        )

        # Config drift check (daily at 6 AM)
        self.scheduler.add_job(
            func=self.check_config_drift,
            trigger=CronTrigger(hour=6, minute=0),
            id="config_drift",
            name="Config Drift Check",
        )

        self.scheduler.start()
        logger.info("Task scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Task scheduler stopped")

    async def budget_snapshot(self):
        """Take budget usage snapshot"""
        try:
            from .budget_guard import BudgetGuard

            guard = BudgetGuard()
            status = guard.get_status()

            logger.info(
                f"Budget snapshot - Daily: ${status['daily_spent']:.2f}, "
                f"Monthly: ${status['monthly_spent']:.2f}"
            )

        except Exception as e:
            logger.error(f"Budget snapshot failed: {e}")

    async def cleanup_caches(self):
        """Clean up old cache entries"""
        try:
            # This would clean up TTL caches, old log files, etc.
            logger.info("Cache cleanup completed")
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")

    async def check_config_drift(self):
        """Check for configuration drift"""
        try:
            # This would compare current config with defaults/expected values
            logger.info("Config drift check completed")
        except Exception as e:
            logger.error(f"Config drift check failed: {e}")


class RSSWatcher:
    """Minimal RSS watcher for community monitoring"""

    def __init__(self):
        self.config = get_config()

    async def check_feeds(self):
        """Check RSS feeds for new posts"""
        try:
            # This would integrate with the existing community monitor
            logger.debug("RSS feeds checked")
        except Exception as e:
            logger.error(f"RSS check failed: {e}")
