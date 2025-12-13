"""
EQ12 Comprehensive Logging System
Standardized JSONL logging with UTF-8 encoding, secret redaction, rotation, and analytics integration
"""

import gzip
import json
import logging
import logging.handlers
import os
import re
import shutil
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class SecretRedactionFilter(logging.Filter):
    """Filter to redact sensitive information from log records."""

    def __init__(self):
        super().__init__()
        # Patterns for secret detection
        self.secret_patterns = [
            (r'(api[_-]?key|apikey)\s*[=:]\s*["\']?([^"\'\s,}]+)["\']?', r"\1=***REDACTED***"),
            (r'(password|passwd|pwd)\s*[=:]\s*["\']?([^"\'\s,}]+)["\']?', r"\1=***REDACTED***"),
            (r'(token|access[_-]?token)\s*[=:]\s*["\']?([^"\'\s,}]+)["\']?', r"\1=***REDACTED***"),
            (
                r'(secret|client[_-]?secret)\s*[=:]\s*["\']?([^"\'\s,}]+)["\']?',
                r"\1=***REDACTED***",
            ),
            (r"Bearer\s+([^\s]+)", r"Bearer ***REDACTED***"),
            (r"(sk-[a-zA-Z0-9]{48})", r"***REDACTED_OPENAI_KEY***"),
            (r"(ghp_[a-zA-Z0-9]{36})", r"***REDACTED_GITHUB_TOKEN***"),
        ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Apply redaction to log record message."""
        if hasattr(record, "msg") and record.msg:
            msg = str(record.msg)
            for pattern, replacement in self.secret_patterns:
                msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE)
            record.msg = msg

        # Also redact args if present
        if hasattr(record, "args") and record.args:
            redacted_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    for pattern, replacement in self.secret_patterns:
                        arg = re.sub(pattern, replacement, arg, flags=re.IGNORECASE)
                redacted_args.append(arg)
            record.args = tuple(redacted_args)

        return True


class JSONLFormatter(logging.Formatter):
    """JSON Lines formatter with structured logging support."""

    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON line."""
        # Base log structure
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "filename": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add process info
        log_entry["process"] = {
            "pid": os.getpid(),
            "thread": record.thread,
            "thread_name": record.threadName,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add stack info if present
        if record.stack_info:
            log_entry["stack_info"] = record.stack_info

        # Add extra fields if enabled
        if self.include_extra:
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in [
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "message",
                ]:
                    try:
                        json.dumps(value)  # Test if serializable
                        extra_fields[key] = value
                    except (TypeError, ValueError):
                        extra_fields[key] = str(value)

            if extra_fields:
                log_entry["extra"] = extra_fields

        # Ensure UTF-8 serializable
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class CompressedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """Rotating file handler with gzip compression."""

    def __init__(
        self,
        filename: str,
        when: str = "midnight",
        interval: int = 1,
        backupCount: int = 7,
        encoding: str = "utf-8",
        compress: bool = True,
    ):
        self.compress_files = compress
        super().__init__(
            filename,
            when=when,
            interval=interval,
            backupCount=backupCount,
            encoding=encoding,
            utc=True,
        )

    def doRollover(self):
        """Perform rollover with compression."""
        super().doRollover()

        if self.compress_files and self.backupCount > 0:
            # Compress the rolled over file
            base_filename = self.rotation_filename(self.baseFilename + ".1")
            if os.path.exists(base_filename) and not base_filename.endswith(".gz"):
                self._compress_file(base_filename)

    def _compress_file(self, filename: str):
        """Compress a log file using gzip."""
        try:
            compressed_filename = filename + ".gz"
            with open(filename, "rb") as f_in:
                with gzip.open(compressed_filename, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(filename)
        except Exception as e:
            # Don't fail on compression errors
            print(f"Warning: Failed to compress log file {filename}: {e}")


class EQ12Logger:
    """Centralized logging configuration for EQ12."""

    def __init__(
        self,
        name: str,
        log_level: str = "INFO",
        log_dir: str | None = None,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_rotation: bool = True,
        enable_compression: bool = True,
        retention_days: int = 30,
        max_file_size_mb: int = 100,
    ):

        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = Path(log_dir) if log_dir else Path("C:/EQ12/logs")
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_rotation = enable_rotation
        self.enable_compression = enable_compression
        self.retention_days = retention_days
        self.max_file_size_mb = max_file_size_mb

        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup and configure logger with handlers."""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level)

        # Clear existing handlers
        logger.handlers.clear()

        # Add redaction filter
        redaction_filter = SecretRedactionFilter()

        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level)
            console_handler.addFilter(redaction_filter)

            # Simple format for console
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        # File handler
        if self.enable_file:
            log_file = self.log_dir / f"{self.name}.jsonl"

            if self.enable_rotation:
                file_handler = CompressedRotatingFileHandler(
                    str(log_file),
                    when="midnight",
                    interval=1,
                    backupCount=self.retention_days,
                    encoding="utf-8",
                    compress=self.enable_compression,
                )
            else:
                file_handler = logging.FileHandler(str(log_file), encoding="utf-8")

            file_handler.setLevel(self.log_level)
            file_handler.addFilter(redaction_filter)
            file_handler.setFormatter(JSONLFormatter())
            logger.addHandler(file_handler)

        return logger

    def get_logger(self) -> logging.Logger:
        """Get configured logger instance."""
        return self.logger

    def log_structured(self, level: str, message: str, **kwargs):
        """Log structured data with extra fields."""
        log_method = getattr(self.logger, level.lower())
        log_method(message, extra=kwargs)

    def log_performance(self, operation: str, duration_ms: float, **kwargs):
        """Log performance metrics."""
        self.log_structured(
            "info",
            f"Performance: {operation}",
            operation=operation,
            duration_ms=duration_ms,
            performance_metric=True,
            **kwargs,
        )

    def log_security_event(
        self, event_type: str, details: dict[str, Any], severity: str = "warning"
    ):
        """Log security-related events."""
        self.log_structured(
            severity,
            f"Security Event: {event_type}",
            security_event=True,
            event_type=event_type,
            **details,
        )

    def log_api_call(
        self, endpoint: str, method: str, status_code: int, duration_ms: float, **kwargs
    ):
        """Log API call metrics."""
        self.log_structured(
            "info",
            f"API Call: {method} {endpoint}",
            api_call=True,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs,
        )


class LoggingConfig:
    """Global logging configuration for EQ12."""

    @staticmethod
    def setup_root_logging(log_level: str = "INFO", log_dir: str = "C:/EQ12/logs"):
        """Setup root logger configuration."""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[],
        )

        # Suppress noisy third-party loggers
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("github").setLevel(logging.WARNING)
        logging.getLogger("git").setLevel(logging.WARNING)

    @staticmethod
    def get_logger(name: str, **kwargs) -> logging.Logger:
        """Get a configured EQ12 logger."""
        eq12_logger = EQ12Logger(name, **kwargs)
        return eq12_logger.get_logger()

    @staticmethod
    def create_module_logger(module_name: str, **kwargs) -> logging.Logger:
        """Create logger for a specific module."""
        return LoggingConfig.get_logger(f"eq12.{module_name}", **kwargs)


# Analytics and ETL helpers
class LogAnalytics:
    """Log analytics and ETL utilities."""

    @staticmethod
    def parse_jsonl_logs(log_file: Path) -> list[dict[str, Any]]:
        """Parse JSONL log file into structured data."""
        logs = []
        try:
            with open(log_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            logs.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            pass
        return logs

    @staticmethod
    def export_for_grafana(log_dir: Path, output_file: Path):
        """Export logs in Grafana-compatible format."""
        all_logs = []

        for log_file in log_dir.glob("*.jsonl*"):
            if log_file.suffix == ".gz":
                import gzip

                with gzip.open(log_file, "rt", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                all_logs.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
            else:
                all_logs.extend(LogAnalytics.parse_jsonl_logs(log_file))

        # Sort by timestamp
        all_logs.sort(key=lambda x: x.get("timestamp", ""))

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_logs, f, indent=2, ensure_ascii=False)


# Example usage and initialization
if __name__ == "__main__":
    # Setup global logging
    LoggingConfig.setup_root_logging()

    # Create module-specific logger
    logger = LoggingConfig.create_module_logger("test")

    # Test logging
    logger.info("EQ12 logging system initialized")
    logger.warning("This is a test warning with API key: sk-test123", extra={"test_field": "value"})

    # Test structured logging
    eq12_logger = EQ12Logger("test_structured")
    eq12_logger.log_performance("test_operation", 150.5, user_id="test_user")
    eq12_logger.log_security_event("login_attempt", {"ip": "192.168.1.1", "success": True})
    eq12_logger.log_api_call("/api/test", "GET", 200, 45.2, user_agent="test")

    print("✅ EQ12 logging system test completed")
