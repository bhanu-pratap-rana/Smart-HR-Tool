"""JSON logging configuration for structured logging."""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.

    Outputs log records as JSON objects for easier parsing and analysis
    in log aggregation systems like ELK, Splunk, or CloudWatch.

    Example output:
    {
        "timestamp": "2025-11-09T10:30:00.123Z",
        "level": "INFO",
        "logger": "backend.app.services.groq_service",
        "message": "Successfully generated content",
        "trace_id": "abc-123-def",
        "extra_data": {"model": "llama-3.3-70b", "chars": 1500}
    }
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON string.

        Args:
            record: Log record to format

        Returns:
            str: JSON-formatted log entry
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add trace_id if available
        if hasattr(record, 'trace_id'):
            log_data["trace_id"] = record.trace_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add any extra fields from record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'pathname', 'process', 'processName', 'relativeCreated',
                'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
                'trace_id'
            ]:
                extra_fields[key] = value

        if extra_fields:
            log_data["extra_data"] = extra_fields

        return json.dumps(log_data)


def setup_json_logging(
    level: int = logging.INFO,
    format_as_json: bool = True
) -> None:
    """
    Configure logging with JSON formatter.

    Args:
        level: Logging level (default: logging.INFO)
        format_as_json: Whether to use JSON formatting (default: True)

    Example:
        ```python
        from backend.app.utils.logging import setup_json_logging

        # In main.py or app startup
        setup_json_logging(level=logging.INFO)
        ```
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler with JSON formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    if format_as_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        # Fallback to standard formatting for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)


def get_logger_with_trace(
    name: str,
    trace_id: Optional[str] = None
) -> logging.LoggerAdapter:
    """
    Get a logger with trace_id context.

    This creates a LoggerAdapter that automatically adds trace_id
    to all log records, making it easier to track requests through
    the system.

    Args:
        name: Logger name (usually __name__)
        trace_id: Optional trace ID to include in logs

    Returns:
        logging.LoggerAdapter: Logger with trace_id context

    Example:
        ```python
        from backend.app.utils.logging import get_logger_with_trace
        import uuid

        trace_id = str(uuid.uuid4())
        logger = get_logger_with_trace(__name__, trace_id)
        logger.info("Processing request")  # Will include trace_id
        ```
    """
    logger = logging.getLogger(name)

    class TraceAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            if self.extra and 'trace_id' in self.extra:
                # Add trace_id to the log record
                if 'extra' not in kwargs:
                    kwargs['extra'] = {}
                kwargs['extra']['trace_id'] = self.extra['trace_id']
            return msg, kwargs

    return TraceAdapter(logger, {'trace_id': trace_id})
