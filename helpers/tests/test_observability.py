"""Tests for observability UnifiedLogger."""

import pytest

from helpers.observability import UnifiedLogger


@pytest.fixture
def unified_logger():
    """Create a fresh UnifiedLogger instance for testing."""
    return UnifiedLogger()


class TestUnifiedLogger:
    """Test suite for the UnifiedLogger class."""

    def test_info_logs_to_both_systems(self, unified_logger, mocker):
        """Test that info logs go to both logfire and loguru."""
        mock_logfire = mocker.patch("helpers.observability._logfire")
        mock_logger = mocker.patch("helpers.observability.logger")

        message = "💸 Test message with emoji"
        kwargs = {"agent_name": "Patrick", "model": "claude-sonnet-4.5"}

        unified_logger.info(message, **kwargs)

        # Verify logfire was called
        mock_logfire.info.assert_called_once_with(message, **kwargs)
        # Verify loguru was called with formatted message
        mock_logger.info.assert_called_once_with(
            f"{message} [agent_name=Patrick | model=claude-sonnet-4.5]"
        )

    def test_error_logs_to_both_systems(self, unified_logger, mocker):
        """Test that error logs go to both systems."""
        mock_logfire = mocker.patch("helpers.observability._logfire")
        mock_logger = mocker.patch("helpers.observability.logger")

        message = "Agent execution failed"
        kwargs = {"error_type": "timeout", "agent_name": "Maya"}

        unified_logger.error(message, **kwargs)

        mock_logfire.error.assert_called_once_with(message, **kwargs)
        mock_logger.error.assert_called_once_with(
            f"{message} [error_type=timeout | agent_name=Maya]"
        )

    def test_span_creates_logfire_span_and_logs_entry(self, unified_logger, mocker):
        """Test that span creates a logfire span and logs entry to console."""
        mock_logfire = mocker.patch("helpers.observability._logfire")
        mock_logger = mocker.patch("helpers.observability.logger")

        # Set up span context manager
        mock_context = mocker.MagicMock()
        mock_logfire.span.return_value.__enter__.return_value = mock_context
        mock_logfire.span.return_value.__exit__.return_value = None

        span_name = "🧠 Agent query"
        kwargs = {"agent_name": "Patrick", "model": "claude-sonnet-4.5"}

        with unified_logger.span(span_name, **kwargs) as span:
            assert span == mock_context

        # Verify logfire span was created
        mock_logfire.span.assert_called_once_with(span_name, **kwargs)
        # Verify console logging for span entry
        mock_logger.info.assert_called_once_with(
            f"▶ {span_name} [agent_name=Patrick | model=claude-sonnet-4.5]"
        )

    def test_span_nesting_indentation(self, unified_logger, mocker):
        """Test that nested spans create proper indentation."""
        mock_logfire = mocker.patch("helpers.observability._logfire")
        mock_logger = mocker.patch("helpers.observability.logger")

        # Set up span context manager
        mock_context = mocker.MagicMock()
        mock_logfire.span.return_value.__enter__.return_value = mock_context
        mock_logfire.span.return_value.__exit__.return_value = None

        with unified_logger.span("Outer span", agent_name="Patrick"):
            unified_logger.info("Inside first span")

            with unified_logger.span("Inner span", operation="nested"):
                unified_logger.info("Inside nested span")

        # Check the calls to logger.info for proper indentation
        expected_calls = [
            mocker.call("▶ Outer span [agent_name=Patrick]"),  # depth 0
            mocker.call("  Inside first span"),  # depth 1 (2 spaces)
            mocker.call("  ▶ Inner span [operation=nested]"),  # depth 1
            mocker.call("    Inside nested span"),  # depth 2 (4 spaces)
        ]
        mock_logger.info.assert_has_calls(expected_calls)

    def test_span_depth_resets_after_exception(self, unified_logger, mocker):
        """Test that span depth resets properly even if exception occurs."""
        mock_logfire = mocker.patch("helpers.observability._logfire")
        mocker.patch("helpers.observability.logger")

        # Set up span context manager
        mock_logfire.span.return_value.__enter__.return_value = mocker.MagicMock()
        mock_logfire.span.return_value.__exit__.return_value = None

        # Depth should start at 0
        assert unified_logger._span_depth == 0

        try:
            with unified_logger.span("Test span"):
                assert unified_logger._span_depth == 1
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Depth should reset to 0 after exception
        assert unified_logger._span_depth == 0

    def test_format_attributes_filters_unimportant_keys(self, unified_logger):
        """Test that _format_attributes only shows important keys."""
        kwargs = {
            "agent_name": "Patrick",
            "model": "claude-sonnet-4.5",
            "operation": "query",
            "unimportant_key": "should_not_appear",
            "random_data": "ignored",
        }

        result = unified_logger._format_attributes(**kwargs)

        # Should include important keys
        assert "agent_name=Patrick" in result
        assert "model=claude-sonnet-4.5" in result
        assert "operation=query" in result
        # Should not include unimportant keys
        assert "unimportant_key" not in result
        assert "random_data" not in result

    def test_format_attributes_filters_none_values(self, unified_logger):
        """Test that None values are filtered out."""
        kwargs = {"agent_name": "Patrick", "model": None, "operation": None}

        result = unified_logger._format_attributes(**kwargs)

        assert "agent_name=Patrick" in result
        assert "model" not in result
        assert "operation" not in result

    def test_format_attributes_empty_kwargs(self, unified_logger):
        """Test that empty kwargs returns empty string."""
        result = unified_logger._format_attributes()
        assert result == ""

        result = unified_logger._format_attributes(unimportant="data")
        assert result == ""

