"""Agent management CLI commands."""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
import click

from ai.agents.base_agent import BaseAgent
from ai.core.agent_config import AgentConfig
from ai.core.config import config as app_config
from ai.core.validators import AgentValidator, format_validation_results
from helpers.logger import logger

console = Console()


@click.group("agents")
def agents():
    """Manage and run AI agents."""


@agents.command("list")
def list_agents():
    """List all available agents."""
    agents_dir = Path("ai/agents")

    if not agents_dir.exists():
        console.print("[red]Error: ai/agents directory not found[/red]")
        return

    # Find all .agent.md files
    agent_files = list(agents_dir.glob("*.agent.md"))

    if not agent_files:
        console.print("[yellow]No agents found[/yellow]")
        return

    # Create table
    table = Table(
        title="🤖 Available Agents", show_header=True, header_style="bold cyan"
    )
    table.add_column("Name", style="cyan", width=20)
    table.add_column("Description", style="green", width=40)
    table.add_column("Model", style="yellow", width=25)
    table.add_column("Version", style="magenta", width=8)

    for agent_file in sorted(agent_files):
        try:
            config = AgentConfig.from_file(agent_file)
            # Truncate description if too long
            desc = config.description
            if len(desc) > 60:
                desc = desc[:60] + "..."

            table.add_row(
                config.name,
                desc,
                config.model_name,
                f"v{config.latest_version}",
            )
        except Exception as e:
            logger.error(f"Error loading {agent_file}: {e}")
            table.add_row(
                agent_file.stem,
                f"[red]Error: {str(e)[:40]}[/red]",
                "N/A",
                "N/A",
            )

    console.print(table)


@agents.command("run")
@click.argument("agent_name", metavar="AGENT_NAME")
@click.option("--query", "-q", help="Query to send to the agent", required=True)
@click.option("--context", "-c", help="Additional context (JSON string)", default=None)
@click.option("--model", "-m", help="Override model", default=None)
@click.option(
    "--temperature", "-t", help="Override temperature", type=float, default=None
)
def run_agent(
    agent_name: str,
    query: str,
    context: str | None,
    model: str | None,
    temperature: float | None,
):
    """Run an agent with a query.

    Example:
        hundredx agents run patrick --query "What's your favorite dinosaur?"
        python -m cli.main agents run patrick -q "Tell me about space!"
    """
    import json

    # Parse context if provided
    context_dict = {}
    if context:
        try:
            context_dict = json.loads(context)
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON context: {e}[/red]")
            return

    try:
        # Initialize agent
        with console.status(
            f"[bold green]Initializing {agent_name}...", spinner="dots"
        ):
            agent = BaseAgent(
                agent_name,
                model_override=model,
                temperature_override=temperature,
            )

        # Show agent info
        console.print(
            Panel(
                agent.explain(),
                title=f"🤖 {agent.config.name}",
                border_style="cyan",
            )
        )

        # Run query
        with console.status("[bold green]Thinking...", spinner="dots"):
            result = agent.query(user_context={"query": query, **context_dict})

        # Display result
        console.print("\n[bold green]Response:[/bold green]\n")

        if hasattr(result, "model_dump"):
            # Structured output
            import json

            result_json = json.dumps(result.model_dump(), indent=2)
            syntax = Syntax(result_json, "json", theme="monokai", line_numbers=True)
            console.print(syntax)
        else:
            # Plain text output
            console.print(Panel(str(result), border_style="green"))

        # Show usage stats
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="yellow")
        stats_table.add_row("Input tokens", str(agent.total_input_tokens))
        stats_table.add_row("Output tokens", str(agent.total_output_tokens))
        stats_table.add_row("Cost", f"${agent.total_cost:.4f}")

        console.print("\n[bold]Usage:[/bold]")
        console.print(stats_table)

    except FileNotFoundError:
        console.print(f"[red]Agent '{agent_name}' not found[/red]")
        console.print("\n[yellow]Run 'agents list' to see available agents[/yellow]")
        raise SystemExit(1) from None
    except Exception as e:
        error_str = str(e)

        # Check for authentication errors
        if "401" in error_str or "authentication" in error_str.lower():
            console.print("[red]Error: OpenRouter authentication failed[/red]")
            console.print("\n[yellow]Your API key may be invalid or expired.[/yellow]")
            console.print("Get a new key from: https://openrouter.ai/keys")
            console.print(
                f"\nCurrent key starts with: {app_config.openrouter_api_key[:15]}..."
            )
            logger.debug(f"Authentication error: {e}")
            raise SystemExit(1) from None  # Suppress traceback

        # Generic error
        console.print(f"[red]Error running agent: {error_str}[/red]")
        logger.exception(f"Agent run failed: {e}")
        raise SystemExit(1) from None  # Suppress traceback


@agents.command("validate")
@click.argument("agent_name", required=False)
@click.option(
    "--format",
    type=click.Choice(["human", "json", "github"]),
    default="human",
    help="Output format",
)
def validate_agent(agent_name: str | None, format: str):  # noqa: A002
    """Validate .agent.md file format and structure."""
    agents_dir = Path("ai/agents")
    validator = AgentValidator()

    if agent_name:
        # Validate specific file
        agent_file = agents_dir / f"{agent_name}.agent.md"
        if not agent_file.exists():
            console.print(f"[red]Agent '{agent_name}' not found[/red]")
            raise SystemExit(1)

        errors = validator.validate_file(agent_file)
        results = {str(agent_file): errors}
    else:
        # Validate all files in directory
        results = validator.validate_directory(agents_dir)

    # Format and display results
    output = format_validation_results(results, format)
    console.print(output)

    # Exit with error code if validation failed
    total_errors = sum(
        len([e for e in errors if e.severity == "error"]) for errors in results.values()
    )

    if total_errors > 0:
        raise SystemExit(1)


@agents.command("explain")
@click.argument("agent_name")
def explain_agent(agent_name: str):
    """Show detailed information about an agent."""
    try:
        agent_file = Path("ai/agents") / f"{agent_name}.agent.md"
        config = AgentConfig.from_file(agent_file)

        # Show agent info
        console.print(
            Panel(
                f"[bold]{config.name}[/bold]\n\n{config.description}",
                title="🤖 Agent Info",
                border_style="cyan",
            )
        )

        # Configuration table
        config_table = Table(show_header=False, box=None)
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="yellow")
        config_table.add_row("Model", config.model_name)
        config_table.add_row("Temperature", str(config.temperature))
        config_table.add_row("Version", f"v{config.latest_version}")

        if config.config.get("purpose"):
            config_table.add_row("Purpose", config.config["purpose"][:60] + "...")

        if config.config.get("capabilities"):
            caps = ", ".join(config.config["capabilities"])
            config_table.add_row("Capabilities", caps)

        console.print("\n[bold]Configuration:[/bold]")
        console.print(config_table)

        # Show prompts (truncated)
        if config.system_prompt:
            console.print("\n[bold]System Prompt (preview):[/bold]")
            preview = (
                config.system_prompt[:200] + "..."
                if len(config.system_prompt) > 200
                else config.system_prompt
            )
            console.print(Panel(preview, border_style="blue"))

        # Show output schema if exists
        if config.output_schema_code:
            console.print("\n[bold]Output Schema:[/bold]")
            syntax = Syntax(
                config.output_schema_code, "python", theme="monokai", line_numbers=True
            )
            console.print(syntax)

    except FileNotFoundError:
        console.print(f"[red]Agent '{agent_name}' not found[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception(f"Explain failed: {e}")


if __name__ == "__main__":
    agents()
