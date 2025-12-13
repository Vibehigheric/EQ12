# eq12_structured_observability.py
"""
EQ12 Structured Observability and JSON Schema Output System
Comprehensive logging, metrics, tracing, and structured data validation
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError:
    jsonschema = None

from pydantic import BaseModel, Field

try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
except ImportError:
    trace = None
    JaegerExporter = None
    TracerProvider = None
    BatchSpanProcessor = None

from eq12_helpers import setup_utf8_logging

setup_utf8_logging()


class LogLevel(Enum):
    """Structured log levels"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Metric types for observability"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class EventType(Enum):
    """Structured event types"""

    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    API_CALL = "api_call"
    DATABASE_OPERATION = "database_operation"
    EXTERNAL_SERVICE = "external_service"
    ERROR_EVENT = "error_event"
    PERFORMANCE_EVENT = "performance_event"


# JSON Schemas for validation
BETTING_EVENT_SCHEMA = {
    "type": "object",
    "properties": {
        "event_id": {"type": "string"},
        "event_type": {
            "type": "string",
            "enum": ["bet_placed", "parlay_created", "odds_updated"],
        },
        "timestamp": {"type": "string", "format": "date-time"},
        "user_id": {"type": "string"},
        "bet_data": {
            "type": "object",
            "properties": {
                "bet_id": {"type": "string"},
                "amount": {"type": "number", "minimum": 0},
                "odds": {"type": "number"},
                "selection": {"type": "string"},
                "market": {"type": "string"},
            },
            "required": ["bet_id", "amount", "odds"],
        },
        "metadata": {"type": "object"},
    },
    "required": ["event_id", "event_type", "timestamp", "user_id", "bet_data"],
}

PARLAY_SCHEMA = {
    "type": "object",
    "properties": {
        "parlay_id": {"type": "string"},
        "user_id": {"type": "string"},
        "legs": {
            "type": "array",
            "minItems": 2,
            "items": {
                "type": "object",
                "properties": {
                    "selection": {"type": "string"},
                    "odds": {"type": "number"},
                    "market": {"type": "string"},
                    "sport": {"type": "string"},
                },
                "required": ["selection", "odds", "market"],
            },
        },
        "stake": {"type": "number", "minimum": 0},
        "total_odds": {"type": "number", "minimum": 1},
        "potential_payout": {"type": "number", "minimum": 0},
        "created_at": {"type": "string", "format": "date-time"},
        "status": {
            "type": "string",
            "enum": ["pending", "active", "won", "lost", "void"],
        },
    },
    "required": [
        "parlay_id",
        "user_id",
        "legs",
        "stake",
        "total_odds",
        "potential_payout",
        "created_at",
        "status",
    ],
}

HEALTH_CHECK_SCHEMA = {
    "type": "object",
    "properties": {
        "component": {"type": "string"},
        "status": {
            "type": "string",
            "enum": ["healthy", "degraded", "critical", "unknown"],
        },
        "timestamp": {"type": "string", "format": "date-time"},
        "response_time_ms": {"type": "number", "minimum": 0},
        "details": {"type": "object"},
        "checks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "status": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            },
        },
    },
    "required": ["component", "status", "timestamp", "response_time_ms"],
}


class StructuredLogEntry(BaseModel):
    """Structured log entry with validation"""

    timestamp: str = Field(..., description="ISO 8601 timestamp")
    level: LogLevel = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    component: str = Field(..., description="Component name")
    event_type: EventType | None = Field(None, description="Event type")
    user_id: str | None = Field(None, description="User identifier")
    session_id: str | None = Field(None, description="Session identifier")
    trace_id: str | None = Field(None, description="Trace identifier")
    span_id: str | None = Field(None, description="Span identifier")
    request_id: str | None = Field(None, description="Request identifier")
    duration_ms: float | None = Field(None, description="Operation duration")
    status_code: int | None = Field(None, description="HTTP status code")
    error_code: str | None = Field(None, description="Error code")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        use_enum_values = True


class MetricPoint(BaseModel):
    """Single metric data point"""

    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    metric_type: MetricType = Field(..., description="Type of metric")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    labels: dict[str, str] = Field(default_factory=dict, description="Metric labels")
    unit: str | None = Field(None, description="Unit of measurement")

    class Config:
        use_enum_values = True


class TraceSpan(BaseModel):
    """Distributed trace span"""

    trace_id: str = Field(..., description="Trace identifier")
    span_id: str = Field(..., description="Span identifier")
    parent_id: str | None = Field(None, description="Parent span identifier")
    operation_name: str = Field(..., description="Operation name")
    start_time: str = Field(..., description="Start timestamp")
    end_time: str | None = Field(None, description="End timestamp")
    duration_ms: float | None = Field(None, description="Duration in milliseconds")
    tags: dict[str, Any] = Field(default_factory=dict, description="Span tags")
    logs: list[dict[str, Any]] = Field(default_factory=list, description="Span logs")
    status: str = Field(default="ok", description="Span status")
    error: str | None = Field(None, description="Error message if any")


class StructuredLogger:
    """Enhanced structured logger with JSON output"""

    def __init__(self, component: str, log_file: Path | None = None):
        self.component = component
        self.log_file = log_file or Path("C:/EQ12/logs/structured_logs.jsonl")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Setup trace context
        self.tracer = trace.get_tracer(__name__)

    async def log(self, level: LogLevel, message: str, **kwargs) -> str:
        """Log structured entry"""

        # Generate IDs if not provided
        request_id = kwargs.get("request_id", str(uuid.uuid4()))

        # Get current trace context
        current_span = trace.get_current_span()
        trace_id = None
        span_id = None

        if current_span:
            span_context = current_span.get_span_context()
            trace_id = f"{span_context.trace_id:032x}"
            span_id = f"{span_context.span_id:016x}"

        # Create structured log entry
        entry = StructuredLogEntry(
            timestamp=datetime.now(UTC).isoformat(),
            level=level,
            message=message,
            component=self.component,
            trace_id=trace_id,
            span_id=span_id,
            request_id=request_id,
            **kwargs,
        )

        # Write to file
        await self._write_log_entry(entry)

        # Also log to standard logger
        standard_level = getattr(logging, level.value.upper())
        logging.log(standard_level, f"[{self.component}] {message}")

        return request_id

    async def _write_log_entry(self, entry: StructuredLogEntry):
        """Write log entry to structured log file"""
        try:
            log_line = entry.json() + "\n"

            # Write to file (async would be better with aiofiles)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_line)

        except Exception as e:
            logging.error(f"Failed to write structured log: {e}")

    async def info(self, message: str, **kwargs):
        """Log info message"""
        return await self.log(LogLevel.INFO, message, **kwargs)

    async def warning(self, message: str, **kwargs):
        """Log warning message"""
        return await self.log(LogLevel.WARNING, message, **kwargs)

    async def error(self, message: str, **kwargs):
        """Log error message"""
        return await self.log(LogLevel.ERROR, message, **kwargs)

    async def critical(self, message: str, **kwargs):
        """Log critical message"""
        return await self.log(LogLevel.CRITICAL, message, **kwargs)


class MetricsCollector:
    """Structured metrics collection and export"""

    def __init__(self, export_path: Path | None = None):
        self.export_path = export_path or Path("C:/EQ12/logs/metrics.jsonl")
        self.export_path.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_buffer: list[MetricPoint] = []
        self.buffer_size = 100

    async def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType,
        labels: dict[str, str] | None = None,
        unit: str | None = None,
    ) -> None:
        """Record a metric point"""

        metric = MetricPoint(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(UTC).isoformat(),
            labels=labels or {},
            unit=unit,
        )

        self.metrics_buffer.append(metric)

        # Flush buffer if full
        if len(self.metrics_buffer) >= self.buffer_size:
            await self.flush_metrics()

    async def flush_metrics(self) -> None:
        """Flush metrics buffer to file"""

        if not self.metrics_buffer:
            return

        try:
            with open(self.export_path, "a", encoding="utf-8") as f:
                for metric in self.metrics_buffer:
                    f.write(metric.json() + "\n")

            logging.info(f"Flushed {len(self.metrics_buffer)} metrics")
            self.metrics_buffer.clear()

        except Exception as e:
            logging.error(f"Failed to flush metrics: {e}")

    async def counter(self, name: str, value: float = 1, **labels) -> None:
        """Record counter metric"""
        await self.record_metric(name, value, MetricType.COUNTER, labels)

    async def gauge(self, name: str, value: float, **labels) -> None:
        """Record gauge metric"""
        await self.record_metric(name, value, MetricType.GAUGE, labels)

    async def histogram(self, name: str, value: float, **labels) -> None:
        """Record histogram metric"""
        await self.record_metric(name, value, MetricType.HISTOGRAM, labels)


class DistributedTracer:
    """Distributed tracing with structured output"""

    def __init__(self, service_name: str = "eq12_system"):
        self.service_name = service_name
        self.trace_file = Path("C:/EQ12/logs/traces.jsonl")
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)

        # Setup OpenTelemetry if available
        if trace:
            try:
                trace.set_tracer_provider(TracerProvider())
                self.tracer = trace.get_tracer(__name__)

                # Setup Jaeger exporter (optional)
                if JaegerExporter and BatchSpanProcessor:
                    jaeger_exporter = JaegerExporter(
                        agent_host_name="localhost",
                        agent_port=6831,
                    )

                    span_processor = BatchSpanProcessor(jaeger_exporter)
                    trace.get_tracer_provider().add_span_processor(span_processor)

            except Exception as e:
                logging.debug(f"OpenTelemetry setup failed: {e}")
                self.tracer = None
        else:
            logging.debug("OpenTelemetry not available - tracing disabled")
            self.tracer = None

    async def start_span(self, operation_name: str, parent_context=None, **tags) -> TraceSpan:
        """Start a new trace span"""

        with self.tracer.start_as_current_span(operation_name) as span:
            span_context = span.get_span_context()

            # Add tags
            for key, value in tags.items():
                span.set_attribute(key, str(value))

            trace_span = TraceSpan(
                trace_id=f"{span_context.trace_id:032x}",
                span_id=f"{span_context.span_id:016x}",
                operation_name=operation_name,
                start_time=datetime.now(UTC).isoformat(),
                tags=tags,
            )

            return trace_span

    async def finish_span(
        self, span: TraceSpan, status: str = "ok", error: str | None = None
    ) -> None:
        """Finish and record trace span"""

        span.end_time = datetime.now(UTC).isoformat()
        span.status = status
        span.error = error

        # Calculate duration
        if span.start_time and span.end_time:
            start = datetime.fromisoformat(span.start_time.replace("Z", "+00:00"))
            end = datetime.fromisoformat(span.end_time.replace("Z", "+00:00"))
            span.duration_ms = (end - start).total_seconds() * 1000

        # Write to trace file
        try:
            with open(self.trace_file, "a", encoding="utf-8") as f:
                f.write(span.json() + "\n")

        except Exception as e:
            logging.error(f"Failed to write trace: {e}")


class SchemaValidator:
    """JSON schema validation for structured outputs"""

    def __init__(self):
        self.schemas = {
            "betting_event": BETTING_EVENT_SCHEMA,
            "parlay": PARLAY_SCHEMA,
            "health_check": HEALTH_CHECK_SCHEMA,
        }

    def validate(self, data: dict[str, Any], schema_name: str) -> dict[str, Any]:
        """Validate data against schema"""

        if schema_name not in self.schemas:
            raise ValueError(f"Unknown schema: {schema_name}")

        schema = self.schemas[schema_name]

        if not jsonschema:
            # Schema validation not available - return as valid
            logging.debug("jsonschema not available - skipping validation")
            return {
                "valid": True,
                "data": data,
                "schema": schema_name,
                "timestamp": datetime.now(UTC).isoformat(),
                "note": "Schema validation skipped - jsonschema not installed",
            }

        try:
            jsonschema.validate(data, schema)
            return {
                "valid": True,
                "data": data,
                "schema": schema_name,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:  # Catch any jsonschema error
            return {
                "valid": False,
                "error": str(e),
                "error_path": getattr(e, "absolute_path", []),
                "schema": schema_name,
                "timestamp": datetime.now(UTC).isoformat(),
            }

    def add_custom_schema(self, name: str, schema: dict[str, Any]) -> None:
        """Add custom validation schema"""
        self.schemas[name] = schema


class ObservabilityManager:
    """Central observability management system"""

    def __init__(self, component_name: str = "eq12_system"):
        self.component_name = component_name
        self.logger = StructuredLogger(component_name)
        self.metrics = MetricsCollector()
        self.tracer = DistributedTracer()
        self.validator = SchemaValidator()

        # Observability configuration
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load observability configuration"""

        config_file = Path("C:/EQ12/configs/observability_config.json")

        if config_file.exists():
            try:
                with open(config_file) as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load observability config: {e}")

        # Default configuration
        return {
            "log_level": "info",
            "metrics_enabled": True,
            "tracing_enabled": True,
            "export_interval_seconds": 60,
            "retention_days": 30,
            "sampling_rate": 1.0,
        }

    async def start_operation(self, operation_name: str, **context) -> dict[str, Any]:
        """Start monitored operation"""

        # Start trace span
        span = await self.tracer.start_span(operation_name, **context)

        # Log operation start
        request_id = await self.logger.info(
            f"Starting operation: {operation_name}",
            event_type=EventType.SYSTEM_EVENT,
            operation=operation_name,
            trace_id=span.trace_id,
            span_id=span.span_id,
            **context,
        )

        # Record metric
        await self.metrics.counter(
            "operations_started",
            labels={"operation": operation_name, "component": self.component_name},
        )

        return {
            "request_id": request_id,
            "trace_id": span.trace_id,
            "span_id": span.span_id,
            "span": span,
            "start_time": time.time(),
        }

    async def finish_operation(
        self,
        operation_context: dict[str, Any],
        status: str = "success",
        error: Exception | None = None,
    ) -> None:
        """Finish monitored operation"""

        operation_name = operation_context["span"].operation_name
        duration = time.time() - operation_context["start_time"]

        # Finish trace span
        await self.tracer.finish_span(
            operation_context["span"],
            status="error" if error else "ok",
            error=str(error) if error else None,
        )

        # Log operation completion
        log_level = LogLevel.ERROR if error else LogLevel.INFO
        message = f"Completed operation: {operation_name}"

        if error:
            message += f" with error: {error!s}"

        await self.logger.log(
            log_level,
            message,
            event_type=EventType.SYSTEM_EVENT,
            operation=operation_name,
            duration_ms=duration * 1000,
            status=status,
            error_code=type(error).__name__ if error else None,
            trace_id=operation_context["trace_id"],
            span_id=operation_context["span_id"],
        )

        # Record metrics
        await self.metrics.counter(
            "operations_completed",
            labels={
                "operation": operation_name,
                "status": status,
                "component": self.component_name,
            },
        )

        await self.metrics.histogram(
            "operation_duration_ms",
            duration * 1000,
            labels={"operation": operation_name, "component": self.component_name},
        )

    async def validate_and_log(self, data: dict[str, Any], schema_name: str) -> bool:
        """Validate data against schema and log result"""

        validation_result = self.validator.validate(data, schema_name)

        if validation_result["valid"]:
            await self.logger.info(
                f"Schema validation successful: {schema_name}",
                event_type=EventType.SYSTEM_EVENT,
                schema_name=schema_name,
                data_size=len(json.dumps(data)),
            )
        else:
            await self.logger.error(
                f"Schema validation failed: {schema_name}",
                event_type=EventType.ERROR_EVENT,
                schema_name=schema_name,
                validation_error=validation_result["error"],
                error_path=validation_result.get("error_path", []),
            )

        return validation_result["valid"]

    async def create_structured_response(
        self,
        status: str,
        data: Any = None,
        message: str = "",
        request_id: str | None = None,
        **metadata,
    ) -> dict[str, Any]:
        """Create standardized structured response"""

        response = {
            "status": status,
            "timestamp": datetime.now(UTC).isoformat(),
            "request_id": request_id or str(uuid.uuid4()),
            "component": self.component_name,
            "message": message,
            "data": data,
            "metadata": metadata,
        }

        # Log response creation
        await self.logger.info(
            f"Created structured response: {status}",
            event_type=EventType.API_CALL,
            response_status=status,
            request_id=response["request_id"],
        )

        return response

    async def health_check(self) -> dict[str, Any]:
        """Perform observability system health check"""

        start_time = time.time()
        checks = []

        # Check log file writability
        try:
            await self.logger.info("Health check test log")
            checks.append(
                {
                    "name": "structured_logging",
                    "status": True,
                    "message": "Log file writable",
                }
            )
        except Exception as e:
            checks.append(
                {
                    "name": "structured_logging",
                    "status": False,
                    "message": f"Log file error: {e!s}",
                }
            )

        # Check metrics collection
        try:
            await self.metrics.counter("health_check", labels={"component": self.component_name})
            checks.append(
                {
                    "name": "metrics_collection",
                    "status": True,
                    "message": "Metrics collection working",
                }
            )
        except Exception as e:
            checks.append(
                {
                    "name": "metrics_collection",
                    "status": False,
                    "message": f"Metrics error: {e!s}",
                }
            )

        # Calculate overall status
        all_healthy = all(check["status"] for check in checks)
        status = "healthy" if all_healthy else "degraded"

        response_time_ms = (time.time() - start_time) * 1000

        health_data = {
            "component": f"{self.component_name}_observability",
            "status": status,
            "timestamp": datetime.now(UTC).isoformat(),
            "response_time_ms": response_time_ms,
            "checks": checks,
            "details": {
                "config": self.config,
                "log_file": str(self.logger.log_file),
                "metrics_file": str(self.metrics.export_path),
            },
        }

        # Validate against schema
        await self.validate_and_log(health_data, "health_check")

        return health_data


# Context manager for operation tracking
class tracked_operation:
    """Context manager for automatic operation tracking"""

    def __init__(self, observability: ObservabilityManager, operation_name: str, **context):
        self.observability = observability
        self.operation_name = operation_name
        self.context = context
        self.operation_context = None

    async def __aenter__(self):
        self.operation_context = await self.observability.start_operation(
            self.operation_name, **self.context
        )
        return self.operation_context

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        status = "error" if exc_type else "success"
        await self.observability.finish_operation(self.operation_context, status, exc_val)


async def main():
    """Demonstration of structured observability system"""

    setup_utf8_logging()
    logging.info("🔍 Starting EQ12 Structured Observability System")

    # Initialize observability
    obs = ObservabilityManager("demo_component")

    # Example: Tracked operation
    async with tracked_operation(obs, "demo_betting_operation", user_id="user123") as ctx:
        # Log structured events
        await obs.logger.info(
            "Processing bet placement",
            event_type=EventType.USER_ACTION,
            user_id="user123",
            bet_amount=50.0,
        )

        # Record metrics
        await obs.metrics.counter("bets_placed", labels={"user": "user123"})
        await obs.metrics.gauge("active_users", 145)

        # Validate structured data
        parlay_data = {
            "parlay_id": "parlay_123",
            "user_id": "user123",
            "legs": [
                {"selection": "Team A", "odds": 150, "market": "moneyline"},
                {"selection": "Over 45.5", "odds": -110, "market": "total"},
            ],
            "stake": 25.0,
            "total_odds": 375,
            "potential_payout": 93.75,
            "created_at": datetime.now(UTC).isoformat(),
            "status": "pending",
        }

        is_valid = await obs.validate_and_log(parlay_data, "parlay")
        logging.info(f"Parlay validation result: {is_valid}")

        # Create structured response
        response = await obs.create_structured_response(
            status="success",
            data={"parlay_id": "parlay_123", "confirmed": True},
            message="Parlay created successfully",
            request_id=ctx["request_id"],
        )

        logging.info(f"Structured response: {json.dumps(response, indent=2)}")

    # Health check
    health = await obs.health_check()
    logging.info(f"System health: {health['status']}")

    # Flush remaining data
    await obs.metrics.flush_metrics()

    logging.info("✅ Observability demonstration completed")


if __name__ == "__main__":
    asyncio.run(main())
