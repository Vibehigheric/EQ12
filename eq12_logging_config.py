#!/usr/bin/env python3
"""
EQ12 Logging Configuration Module
=================================

Standardized logging configuration for the EQ12 automation and scraping stack.
Provides consistent JSON-structured logging with UTC timestamps, proper log levels,
and integration with EQ12 backend systems.

Features:
- JSON structured logging for EQ12 analytics
- UTC timestamps for consistent timezone handling
- Configurable log levels and output destinations
- Automatic log rotation and cleanup
- EQ12 backend integration hooks
- Performance monitoring and error tracking

Author: EQ12 Development Team
Version: 1.0.0
Updated: 2025-10-03
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# EQ12 Configuration
EQ12_LOGS_DIR = os.getenv("EQ12_LOGS_DIR", "C:/EQ12/logs")
DEFAULT_LOG_LEVEL = os.getenv("EQ12_LOG_LEVEL", "INFO")
MAX_LOG_SIZE = 50 * 1024 * 1024  # 50MB
BACKUP_COUNT = 10
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


class EQ12JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for EQ12 structured logging
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON structure"""

        # Base log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_entry["extra"] = record.extra_data

        # Add EQ12 context if available
        if hasattr(record, "eq12_context"):
            log_entry["eq12_context"] = record.eq12_context

        return json.dumps(log_entry, ensure_ascii=False)


def setup_eq12_logger(
    name: str,
    log_file: str | None = None,
    level: str = DEFAULT_LOG_LEVEL,
    console_output: bool = True,
    json_format: bool = False,
) -> logging.Logger:
    """
    Setup standardized EQ12 logger

    Args:
        name: Logger name (typically module name)
        log_file: Path to log file (auto-generated if None)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Enable console output
        json_format: Use JSON formatting for structured logging

    Returns:
        Configured logger instance
    """

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()

    # Ensure logs directory exists
    logs_dir = Path(EQ12_LOGS_DIR)
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Setup file handler
    if log_file is None:
        log_file = logs_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    else:
        log_file = Path(log_file)

    # Rotating file handler to prevent huge log files
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT, encoding="utf-8"
    )

    # Setup formatters
    file_formatter = EQ12JSONFormatter() if json_format else logging.Formatter(LOG_FORMAT)

    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Setup console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


def log_eq12_event(
    logger: logging.Logger,
    event_type: str,
    event_data: dict[str, Any],
    level: str = "INFO",
):
    """
    Log structured EQ12 events for analytics

    Args:
        logger: Logger instance
        event_type: Type of event (e.g., 'bet_placed', 'optimization_complete')
        event_data: Event data dictionary
        level: Log level
    """

    # Create log record with EQ12 context
    eq12_context = {
        "event_type": event_type,
        "event_data": event_data,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    # Get log level
    log_level = getattr(logging, level.upper())

    # Create custom log record
    if logger.isEnabledFor(log_level):
        record = logger.makeRecord(
            logger.name, log_level, "", 0, f"EQ12 Event: {event_type}", (), None
        )
        record.eq12_context = eq12_context
        logger.handle(record)


def setup_eq12_performance_logger() -> logging.Logger:
    """
    Setup dedicated performance monitoring logger

    Returns:
        Performance logger with JSON formatting
    """
    return setup_eq12_logger(
        "eq12_performance",
        log_file=Path(EQ12_LOGS_DIR) / "eq12_performance.jsonl",
        json_format=True,
        console_output=False,
    )


def cleanup_old_logs(days_to_keep: int = 30):
    """
    Clean up old log files to prevent disk space issues

    Args:
        days_to_keep: Number of days of logs to retain
    """

    logs_dir = Path(EQ12_LOGS_DIR)
    if not logs_dir.exists():
        return

    cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)

    for log_file in logs_dir.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                print(f"Cleaned up old log file: {log_file}")
            except Exception as e:
                print(f"Failed to cleanup {log_file}: {e}")


# Configure root logger for EQ12
def configure_eq12_root_logger():
    """Configure root logger with EQ12 standards"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add EQ12 handler
    setup_eq12_logger("root", console_output=True)


if __name__ == "__main__":
    # Test the logging configuration
    test_logger = setup_eq12_logger("test_module")

    test_logger.info("EQ12 logging configuration test")
    test_logger.debug("Debug message test")
    test_logger.warning("Warning message test")
    test_logger.error("Error message test")

    # Test structured event logging
    log_eq12_event(
        test_logger,
        "test_event",
        {"test_param": "test_value", "numeric_param": 123, "success": True},
    )

    print(f"Test logs written to: {EQ12_LOGS_DIR}")
