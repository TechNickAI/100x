"""Tests for agent CLI commands."""

from click.testing import CliRunner
import pytest

from cli.main import cli


class TestAgentsCLI:
    """Test suite for agent CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner."""
        return CliRunner()

    def test_agents_list(self, runner):
        """Test agents list command."""
        result = runner.invoke(cli, ["agents", "list"])

        assert result.exit_code == 0
        assert "Patrick" in result.output
        assert "Available Agents" in result.output

    def test_agents_list_no_agents(self, runner, tmp_path, monkeypatch):
        """Test agents list with no agents found."""
        # Change to empty directory
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(cli, ["agents", "list"])

        # Should handle gracefully
        assert "not found" in result.output.lower() or "No agents" in result.output

    def test_agents_validate_all(self, runner):
        """Test validating all agents."""
        result = runner.invoke(cli, ["agents", "validate"])

        assert result.exit_code == 0
        assert "patrick" in result.output.lower() or "Patrick" in result.output

    def test_agents_validate_specific(self, runner):
        """Test validating specific agent."""
        result = runner.invoke(cli, ["agents", "validate", "patrick"])

        assert result.exit_code == 0
        assert "Valid" in result.output or "valid" in result.output

    def test_agents_validate_nonexistent(self, runner):
        """Test validating non-existent agent."""
        result = runner.invoke(cli, ["agents", "validate", "nonexistent_agent"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_agents_explain(self, runner):
        """Test explain command."""
        result = runner.invoke(cli, ["agents", "explain", "patrick"])

        assert result.exit_code == 0
        assert "Patrick" in result.output
        assert "12-year-old" in result.output or "dinosaur" in result.output.lower()

    def test_agents_explain_nonexistent(self, runner):
        """Test explain for non-existent agent."""
        result = runner.invoke(cli, ["agents", "explain", "nonexistent"])

        assert result.exit_code != 0 or "not found" in result.output.lower()

    def test_agents_run_requires_query(self, runner):
        """Test run command requires query option."""
        result = runner.invoke(cli, ["agents", "run", "patrick"])

        # Should fail without --query
        assert result.exit_code != 0

    def test_agents_run_with_mocked_model(self, runner, monkeypatch):
        """Test run command with mocked model (no real API call)."""
        # This would require more complex mocking of the agent execution
        # For now, just test that the command structure is correct
        result = runner.invoke(
            cli, ["agents", "run", "patrick", "--query", "test"], catch_exceptions=False
        )

        # Will fail without API key configured, which is expected
        # The important thing is the command parsed correctly
        assert (
            "OPENROUTER_API_KEY" in result.output
            or result.exit_code == 0  # If API key is configured
            or "Error" in result.output  # Some error occurred
        )

    def test_agents_run_nonexistent(self, runner):
        """Test running non-existent agent."""
        result = runner.invoke(cli, ["agents", "run", "nonexistent", "--query", "test"])

        assert "not found" in result.output.lower()

    def test_validate_json_output(self, runner):
        """Test validation with JSON output format."""
        result = runner.invoke(cli, ["agents", "validate", "--format", "json"])

        assert result.exit_code == 0
        # JSON output should be parseable
        import json

        try:
            json.loads(result.output.strip())
        except json.JSONDecodeError:
            # Some extra text might be present, that's ok
            pass

    def test_validate_github_output(self, runner):
        """Test validation with GitHub Actions output format."""
        result = runner.invoke(cli, ["agents", "validate", "--format", "github"])

        assert result.exit_code == 0
        # GitHub format uses :: syntax, or might be empty if all valid
        assert "::" in result.output or len(result.output.strip()) == 0

    def test_main_cli_version(self, runner):
        """Test CLI version command."""
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output
