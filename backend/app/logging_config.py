"""
Production-grade structured logging configuration
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
import os


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    Outputs logs in JSON format for easy parsing by log aggregators
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'api_key_id'):
            log_data['api_key_id'] = record.api_key_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if hasattr(record, 'tokens_saved'):
            log_data['tokens_saved'] = record.tokens_saved

        return json.dumps(log_data)


class ProductionLogger:
    """
    Production-grade logger with structured logging
    """

    @staticmethod
    def setup_logging(
        level: str = "INFO",
        format_type: str = "json"
    ) -> logging.Logger:
        """
        Setup production logging configuration

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format_type: 'json' for structured JSON logs, 'text' for human-readable

        Returns:
            Configured logger instance
        """
        # Get root logger
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, level.upper()))

        # Remove existing handlers
        logger.handlers = []

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))

        # Set formatter based on format type
        if format_type == "json":
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger with the specified name"""
        return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter for adding context to log messages
    """

    def process(self, msg: str, kwargs: Dict) -> tuple:
        """Process log message with extra context"""
        # Add context from self.extra to the log record
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        kwargs['extra'].update(self.extra)
        return msg, kwargs


def get_request_logger(
    request_id: str,
    user_id: str = None,
    api_key_id: str = None
) -> LoggerAdapter:
    """
    Get a logger with request context

    Args:
        request_id: Unique request ID
        user_id: User ID if authenticated
        api_key_id: API key ID if authenticated

    Returns:
        Logger adapter with request context
    """
    logger = logging.getLogger('concise.request')
    extra = {'request_id': request_id}

    if user_id:
        extra['user_id'] = user_id
    if api_key_id:
        extra['api_key_id'] = api_key_id

    return LoggerAdapter(logger, extra)


def log_compression_metrics(
    logger: logging.Logger,
    original_tokens: int,
    compressed_tokens: int,
    compression_ratio: float,
    strategy: str,
    duration_ms: float
):
    """
    Log compression metrics in structured format

    Args:
        logger: Logger instance
        original_tokens: Original token count
        compressed_tokens: Compressed token count
        compression_ratio: Compression ratio
        strategy: Compression strategy used
        duration_ms: Compression duration in milliseconds
    """
    logger.info(
        f"Compression completed: {compression_ratio:.2f}x reduction",
        extra={
            'original_tokens': original_tokens,
            'compressed_tokens': compressed_tokens,
            'tokens_saved': original_tokens - compressed_tokens,
            'compression_ratio': compression_ratio,
            'strategy': strategy,
            'duration_ms': duration_ms,
            'event_type': 'compression'
        }
    )


def log_tale_metrics(
    logger: logging.Logger,
    estimated_budget: int,
    actual_tokens: int,
    within_budget: bool,
    strategy: str
):
    """
    Log TALE optimization metrics

    Args:
        logger: Logger instance
        estimated_budget: Estimated token budget
        actual_tokens: Actual tokens used
        within_budget: Whether output was within budget
        strategy: TALE strategy used
    """
    logger.info(
        f"TALE optimization: {estimated_budget} budget, {actual_tokens} actual",
        extra={
            'estimated_budget': estimated_budget,
            'actual_tokens': actual_tokens,
            'within_budget': within_budget,
            'tokens_saved': max(0, estimated_budget - actual_tokens),
            'strategy': strategy,
            'event_type': 'tale_optimization'
        }
    )


def log_api_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: str = None
):
    """
    Log API request with metrics

    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        user_id: User ID if authenticated
    """
    extra = {
        'method': method,
        'path': path,
        'status_code': status_code,
        'duration_ms': duration_ms,
        'event_type': 'api_request'
    }

    if user_id:
        extra['user_id'] = user_id

    logger.info(
        f"{method} {path} {status_code} {duration_ms:.2f}ms",
        extra=extra
    )


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Dict[str, Any] = None
):
    """
    Log error with context

    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context information
    """
    extra = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'event_type': 'error'
    }

    if context:
        extra.update(context)

    logger.error(
        f"Error occurred: {type(error).__name__}: {str(error)}",
        extra=extra,
        exc_info=True
    )


def setup_production_logging():
    """
    Setup production logging configuration
    Called at application startup
    """
    # Get log level from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_format = os.getenv('LOG_FORMAT', 'json')

    # Setup logging
    ProductionLogger.setup_logging(level=log_level, format_type=log_format)

    # Log startup
    logger = logging.getLogger('concise')
    logger.info(
        "Logging initialized",
        extra={
            'log_level': log_level,
            'log_format': log_format,
            'event_type': 'startup'
        }
    )

    return logger


if __name__ == "__main__":
    # Test logging configuration
    logger = setup_production_logging()

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Test structured logging
    log_compression_metrics(
        logger,
        original_tokens=500,
        compressed_tokens=250,
        compression_ratio=2.0,
        strategy='balanced',
        duration_ms=15.5
    )

    log_api_request(
        logger,
        method='POST',
        path='/v1/compress',
        status_code=200,
        duration_ms=25.3,
        user_id='test_user'
    )

    print("\n✓ Logging configuration test completed")
