"""Tests for CLI error messages and UX."""

from click.testing import CliRunner
import pytest

from cli.main import cli


class TestCLIErrorMessages:
    """Test that CLI provides helpful error messages."""

    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner."""
        return CliRunner()

    def test_run_missing_agent_name(self, runner):
        """Test that missing agent name shows helpful error."""
        result = runner.invoke(cli, ["agents", "run", "-q", "test query"])

        assert result.exit_code != 0
        assert "AGENT_NAME" in result.output or "Missing argument" in result.output

    def test_run_missing_query(self, runner):
        """Test that missing query shows helpful error."""
        result = runner.invoke(cli, ["agents", "run", "patrick"])

        assert result.exit_code != 0
        assert "query" in result.output.lower() or "required" in result.output.lower()

    def test_run_invalid_agent_shows_help(self, runner):
        """Test that invalid agent suggests listing agents."""
        result = runner.invoke(cli, ["agents", "run", "nonexistent", "-q", "test"])

        assert "not found" in result.output.lower()
        assert "list" in result.output.lower()  # Suggests running list command

    def test_help_messages_exist(self, runner):
        """Test that all commands have help messages."""
        # Main CLI help
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "agents" in result.output.lower()

        # Agents group help
        result = runner.invoke(cli, ["agents", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output.lower()
        assert "run" in result.output.lower()
        assert "validate" in result.output.lower()

        # Run command help
        result = runner.invoke(cli, ["agents", "run", "--help"])
        assert result.exit_code == 0
        assert "AGENT_NAME" in result.output
        assert "query" in result.output.lower()
        assert "Example:" in result.output  # Should show usage example
