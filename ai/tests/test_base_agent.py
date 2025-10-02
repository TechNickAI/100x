"""Tests for BaseAgent using Pydantic AI TestModel."""

from pydantic_ai.models.test import TestModel
import pytest

from ai.agents.base_agent import BaseAgent
from ai.core.config import config


class TestBaseAgent:
    """Test suite for BaseAgent."""

    def test_init_agent(self, mocker):
        """Test agent initialization."""
        # Mock OpenRouter to avoid needing API key
        mocker.patch("ai.agents.base_agent.create_openrouter_model")

        agent = BaseAgent("ai/tests/fixtures/simple_test.agent.md")

        assert agent.config.name == "Simple Test Agent"
        assert agent.model_name == "anthropic/claude-sonnet-4.5"
        assert agent.temperature == 0.5

    def test_explain(self, mocker):
        """Test explain method."""
        # Mock OpenRouter to avoid needing API key
        mocker.patch("ai.agents.base_agent.create_openrouter_model")

        agent = BaseAgent("ai/tests/fixtures/simple_test.agent.md")

        explanation = agent.explain()

        assert "Simple Test Agent" in explanation
        assert agent.config.description in explanation

    def test_query_with_test_model(self):
        """Test querying agent with TestModel for deterministic responses."""
        if not config.openrouter_api_key:
            pytest.skip("No API key configured - demo mode")

        agent = BaseAgent("ai/tests/fixtures/simple_test.agent.md")

        # Override with TestModel for testing (it returns default text)
        test_model = TestModel()

        # Use context manager for override
        with agent.agent.override(model=test_model):
            result = agent.query(user_context={"query": "Test query"})

        # TestModel returns a simple string (exact content varies)
        assert hasattr(result, "result")
        assert isinstance(result.result, str)
        assert agent.query_count == 1

    def test_usage_tracking(self):
        """Test that usage is tracked correctly."""
        if not config.openrouter_api_key:
            pytest.skip("No API key configured - demo mode")

        agent = BaseAgent("ai/tests/fixtures/simple_test.agent.md")

        # Override with TestModel
        test_model = TestModel()

        # Make a query with override
        with agent.agent.override(model=test_model):
            agent.query(user_context={"query": "Test"})

        # Check usage tracking
        usage = agent.get_usage_summary()
        assert usage["query_count"] == 1
        assert usage["agent_name"] == "Simple Test Agent"
        assert "model" in usage
        assert "total_cost" in usage

    def test_model_override(self, mocker):
        """Test model override parameter."""
        # Mock OpenRouter to avoid needing API key
        mocker.patch("ai.agents.base_agent.create_openrouter_model")

        agent = BaseAgent(
            "ai/tests/fixtures/simple_test.agent.md",
            model_override="anthropic/claude-3.5-haiku",
        )

        assert agent.model_name == "anthropic/claude-3.5-haiku"

    def test_temperature_override(self, mocker):
        """Test temperature override parameter."""
        # Mock OpenRouter to avoid needing API key
        mocker.patch("ai.agents.base_agent.create_openrouter_model")

        agent = BaseAgent(
            "ai/tests/fixtures/simple_test.agent.md",
            temperature_override=0.8,
        )

        assert agent.temperature == 0.8

    def test_temperature_zero_override(self, mocker):
        """Test that temperature=0.0 override is honored (not treated as falsy)."""
        # Mock OpenRouter to avoid needing API key
        mocker.patch("ai.agents.base_agent.create_openrouter_model")

        agent = BaseAgent(
            "ai/tests/fixtures/simple_test.agent.md",
            temperature_override=0.0,
        )

        # Zero should be honored, not fall back to config value (0.5)
        assert agent.temperature == 0.0

    def test_agent_not_found(self):
        """Test that missing agent file raises error."""
        with pytest.raises(FileNotFoundError):
            BaseAgent("nonexistent.agent.md")

    def test_query_requires_input(self):
        """Test that query requires either message or context."""
        if not config.openrouter_api_key:
            pytest.skip("No API key configured")

        agent = BaseAgent("ai/tests/fixtures/simple_test.agent.md")

        with pytest.raises(ValueError, match="Must provide"):
            agent.query()

    def test_repr(self, mocker):
        """Test string representation."""
        # Mock OpenRouter to avoid needing API key
        mocker.patch("ai.agents.base_agent.create_openrouter_model")

        agent = BaseAgent("ai/tests/fixtures/simple_test.agent.md")

        repr_str = repr(agent)

        assert "BaseAgent" in repr_str
        assert "Simple Test Agent" in repr_str
        assert agent.model_name in repr_str
