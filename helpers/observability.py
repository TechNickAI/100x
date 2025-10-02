"""Observability setup using Logfire with intelligent environment detection."""

from contextlib import contextmanager
import sys

import logfire as _logfire

from ai.core.config import config
from helpers.logger import logger

__all__ = ["logfire"]


def should_send_to_logfire() -> bool:
    """Determine if telemetry should be sent to Logfire based on environment.

    Rules:
    - Don't send when tests are running
    - Don't send if no token configured
    - Send in all other cases

    Returns:
        bool: True if telemetry should be sent to Logfire
    """
    # Don't send when tests are running
    if "pytest" in sys.modules:
        return False

    # Don't send if no token
    return bool(config.logfire_token)


class UnifiedLogger:
    """Elegant unified logger that dispatches to both logfire and loguru.

    Maintains the exact logfire API while also giving beautiful console output
    via loguru. All emojis preserved! 💸🎯🧠

    Features:
    - Drop-in replacement for logfire - no code changes needed
    - Dual logging to both systems with a single call
    - Intelligent span tracking with indented loguru output
    - Preserves all context attributes for both loggers
    """

    def __init__(self):
        self._span_depth = 0  # Track span nesting for pretty console output

    def _format_attributes(self, **kwargs) -> str:
        """Format attributes nicely for console display."""
        if not kwargs:
            return ""
        # Only show most important attributes to avoid clutter
        important_keys = [
            "agent_name",
            "model",
            "operation",
            "error_type",
            "token_symbol",
            "strategy_name",
        ]
        filtered = {
            k: v for k, v in kwargs.items() if k in important_keys and v is not None
        }
        if not filtered:
            return ""
        attrs = " | ".join(f"{k}={v}" for k, v in filtered.items())
        return f" [{attrs}]"

    def info(self, message: str, **kwargs):
        """Log info to both logfire and loguru."""
        indent = "  " * self._span_depth
        logger.info(f"{indent}{message}{self._format_attributes(**kwargs)}")
        _logfire.info(message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error to both systems."""
        indent = "  " * self._span_depth
        logger.error(f"{indent}{message}{self._format_attributes(**kwargs)}")
        _logfire.error(message, **kwargs)

    def exception(self, message: str, **kwargs):
        """Log exception to both systems with traceback."""
        indent = "  " * self._span_depth
        logger.exception(f"{indent}{message}{self._format_attributes(**kwargs)}")
        _logfire.exception(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning to both systems."""
        indent = "  " * self._span_depth
        logger.warning(f"{indent}{message}{self._format_attributes(**kwargs)}")
        _logfire.warning(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug to both systems."""
        indent = "  " * self._span_depth
        logger.debug(f"{indent}{message}{self._format_attributes(**kwargs)}")
        _logfire.debug(message, **kwargs)

    @contextmanager
    def span(self, name: str, **kwargs):
        """Create a span in logfire AND beautiful nested console output.

        Example output:
            🧠 Agent evaluating query
              📊 Analyzing context
                🎯 Found 3 relevant entities
              💸 Calling LLM
        """
        # Log span entry to console
        logger.info(
            f"{'  ' * self._span_depth}▶ {name}{self._format_attributes(**kwargs)}"
        )

        # Track nesting depth for indentation
        self._span_depth += 1

        # Create the actual logfire span
        with _logfire.span(name, **kwargs) as span:
            try:
                yield span
            finally:
                self._span_depth -= 1

    @contextmanager
    def suppress_instrumentation(self):
        """Proxy to logfire.suppress_instrumentation for tests."""
        with _logfire.suppress_instrumentation():
            yield None

    # Proxy logfire API methods
    def configure(self, *args, **kwargs):
        """Configure logfire."""
        return _logfire.configure(*args, **kwargs)

    def instrument_requests(self, *args, **kwargs):
        """Instrument requests."""
        return _logfire.instrument_requests(*args, **kwargs)

    def instrument_httpx(self, *args, **kwargs):
        """Instrument httpx."""
        return _logfire.instrument_httpx(*args, **kwargs)


# Create unified logger instance
logfire = UnifiedLogger()

# Configure Logfire with intelligent environment detection
if config.logfire_token:
    _logfire.configure(
        token=config.logfire_token,
        service_name="100x",
        send_to_logfire=should_send_to_logfire(),
        scrubbing=False,
        console=False,  # Disable console output (project URL message)
    )
    # Note: Could add _logfire.instrument_httpx() here if needed for detailed HTTP tracing
    logger.debug("🔥 Logfire observability enabled")
else:
    _logfire.configure(send_to_logfire=False, console=False)
    logger.debug("Logfire observability disabled (no token configured)")
