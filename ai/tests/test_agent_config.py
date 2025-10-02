"""Tests for agent configuration parsing."""

from ai.core.agent_config import AgentConfig


class TestAgentConfig:
    """Test suite for AgentConfig."""

    def test_load_from_file(self):
        """Test loading agent from .agent.md file."""
        config = AgentConfig.from_file("ai/agents/patrick.agent.md")

        assert config.name == "Patrick"
        assert config.description
        assert config.model_name == "anthropic/claude-sonnet-4.5"
        assert config.temperature == 0.9

    def test_parse_sections(self):
        """Test that HTML comment sections are parsed correctly."""
        config = AgentConfig.from_file("ai/agents/patrick.agent.md")

        assert config.system_prompt
        assert config.user_prompt
        assert config.output_schema_code
        assert "{{ query }}" in config.user_prompt

    def test_render_system_prompt(self):
        """Test system prompt rendering with context."""
        config = AgentConfig.from_file("ai/tests/fixtures/simple_test.agent.md")

        rendered = config.render_system_prompt({"test_var": "test_value"})

        assert "test agent" in rendered.lower()
        assert rendered.strip()

    def test_render_user_prompt(self):
        """Test user prompt rendering with context."""
        config = AgentConfig.from_file("ai/tests/fixtures/simple_test.agent.md")

        rendered = config.render_user_prompt({"query": "Hello world"})

        assert "Hello world" in rendered

    def test_get_output_model(self):
        """Test extracting Pydantic model from output schema."""
        config = AgentConfig.from_file("ai/tests/fixtures/simple_test.agent.md")

        output_model = config.get_output_model()

        # Should be able to instantiate it
        output = output_model(result="test")
        assert output.result == "test"

    def test_validate_valid_agent(self):
        """Test validation of a valid agent file."""
        config = AgentConfig.from_file("ai/agents/patrick.agent.md")

        errors = config.validate()

        assert errors == []

    def test_validate_missing_fields(self, tmp_path):
        """Test validation catches missing required fields."""
        # Create invalid agent file
        invalid_agent = tmp_path / "invalid.agent.md"
        invalid_agent.write_text(
            """---
name: Test
---

<!-- System Prompt -->

```jinja2
Test
```
"""
        )

        # Clear cache to ensure fresh load
        AgentConfig.clear_cache()

        config = AgentConfig.from_file(invalid_agent)
        errors = config.validate()

        # Should have errors for missing description, model, and user prompt
        assert len(errors) > 0
        assert any("description" in e.lower() for e in errors)

    def test_explain(self):
        """Test explain method returns readable description."""
        config = AgentConfig.from_file("ai/agents/patrick.agent.md")

        explanation = config.explain()

        assert "Patrick" in explanation
        assert config.description in explanation

    def test_cache_clearing(self):
        """Test that cache can be cleared."""
        # Load once
        AgentConfig.from_file("ai/agents/patrick.agent.md")

        # Clear cache
        AgentConfig.clear_cache()

        # Should still work
        config = AgentConfig.from_file("ai/agents/patrick.agent.md")
        assert config.name == "Patrick"
