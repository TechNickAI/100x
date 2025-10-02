"""Base agent class for 100x agent system."""

from decimal import Decimal
from pathlib import Path
from typing import Any
import time

from heart_centered_prompts import get_prompt
from jinja2 import Environment, FileSystemLoader
from pydantic_ai import Agent

from ai.core.agent_config import AgentConfig
from ai.core.openrouter import (
    create_openrouter_model,
    estimate_token_cost,
    get_model_info,
)
from helpers.logger import logger
from helpers.observability import logfire


class BaseAgent:
    """Base class for all 100x agents.

    Provides core functionality:
    - Load .agent.md configuration
    - Render Jinja2 prompts with context
    - Call LLM via OpenRouter
    - Return structured output via Pydantic AI
    - Track usage and costs
    - Wrap execution in Logfire spans
    """

    def __init__(
        self,
        agent_file: str | Path,
        model_override: str | None = None,
        temperature_override: float | None = None,
    ):
        """Initialize agent from .agent.md file.

        Args:
            agent_file: Path to .agent.md file or agent name
            model_override: Override model from config
            temperature_override: Override temperature from config
        """
        # Resolve agent file path
        agent_file = Path(agent_file)
        if not agent_file.suffix:
            agent_file = agent_file.with_suffix(".agent.md")
        if not agent_file.exists():
            # Try in ai/agents/ directory
            agent_file = Path("ai/agents") / agent_file.name

        if not agent_file.exists():
            raise FileNotFoundError(f"Agent file not found: {agent_file}")

        self.agent_file = agent_file

        # Initialize usage tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = Decimal("0.00")
        self.query_count = 0

        # Set up Jinja2 environment for includes (BEFORE loading config)
        # Note: autoescape=False is intentional - we're rendering prompts, not HTML
        self.jinja_env = Environment(
            loader=FileSystemLoader(["ai/agents", "ai/agents/shared"]),
            autoescape=False,
        )

        # Load configuration
        self._load_config(model_override, temperature_override)

    def _load_config(
        self,
        model_override: str | None = None,
        temperature_override: float | None = None,
    ) -> None:
        """Load agent configuration and set up the Pydantic AI agent."""
        # Load agent configuration
        self.config = AgentConfig.from_file(self.agent_file)

        # Apply overrides (explicit None check to honor zero values)
        self.model_name = (
            model_override if model_override is not None else self.config.model_name
        )
        self.temperature = (
            temperature_override
            if temperature_override is not None
            else self.config.temperature
        )

        # Load structured output if defined
        self.result_type = None
        if self.config.output_schema_code:
            try:
                self.result_type = self.config.get_output_model()
            except ValueError as e:
                logger.warning(f"Could not load output schema: {e}")

        # Create OpenRouter model
        model = create_openrouter_model(
            model_name=self.model_name,
            agent_name=self.config.name,
            settings={"temperature": self.temperature},
        )

        # Render system prompt once (it's static per agent)
        system_prompt_text = self._render_system_prompt({})

        # Create Pydantic AI agent
        if self.result_type is not None:
            self.agent = Agent(
                model=model,
                output_type=self.result_type,
                system_prompt=system_prompt_text,
                defer_model_check=True,
            )
        else:
            self.agent = Agent(
                model=model,
                system_prompt=system_prompt_text,
                defer_model_check=True,
            )

        logger.info(
            f"🤖 Initialized {self.config.name}",
            model=self.model_name,
            temperature=self.temperature,
            has_structured_output=self.result_type is not None,
        )

    def query(
        self,
        user_message: str | None = None,
        user_context: dict[str, Any] | None = None,
        system_context: dict[str, Any] | None = None,
    ) -> Any:
        """Query the agent with a message and optional context.

        Args:
            user_message: Direct user message (alternative to template rendering)
            user_context: Context for rendering user prompt template
            system_context: Context for rendering system prompt template (rarely needed)

        Returns:
            Agent response (structured if output_schema defined, otherwise string)
        """
        if user_message is None and not user_context:
            raise ValueError("Must provide either user_message or user_context")

        with logfire.span(
            f"🧠 {self.config.name} query",
            model=self.model_name,
            has_user_message=user_message is not None,
        ) as span:
            start_time = time.monotonic()

            # Render user prompt
            if user_message:
                user_prompt = user_message
            else:
                user_prompt = self._render_user_prompt(user_context or {})

            if not user_prompt:
                raise ValueError("No user prompt provided")

            # Execute the query synchronously
            result = self.agent.run_sync(user_prompt)

            # Track usage
            self.query_count += 1
            usage = result.usage() if callable(result.usage) else result.usage

            if usage:
                input_tokens = usage.input_tokens
                output_tokens = usage.output_tokens

                self.total_input_tokens += input_tokens
                self.total_output_tokens += output_tokens

                query_cost = estimate_token_cost(
                    self.model_name, input_tokens, output_tokens
                )
                self.total_cost += Decimal(str(query_cost))

                # Detailed cost breakdown
                model_info = get_model_info(self.model_name)
                pricing = model_info["pricing"]
                input_cost = (input_tokens / 1_000_000) * pricing["input_per_million"]
                output_cost = (output_tokens / 1_000_000) * pricing[
                    "output_per_million"
                ]

                duration_s = time.monotonic() - start_time
                total_tokens = input_tokens + output_tokens
                tokens_per_second = total_tokens / duration_s if duration_s else 0.0

                span.set_attributes(
                    {
                        "usage.input_tokens": input_tokens,
                        "usage.output_tokens": output_tokens,
                        "usage.total_tokens": total_tokens,
                        "usage.duration_ms": int(duration_s * 1000),
                        "usage.tokens_per_second": tokens_per_second,
                        "cost.input_usd": float(input_cost),
                        "cost.output_usd": float(output_cost),
                        "cost.total_usd": float(query_cost),
                        "accumulated.total_cost_usd": float(self.total_cost),
                    }
                )

                logger.info(
                    f"💰 {self.config.name} usage",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    duration_ms=int(duration_s * 1000),
                    cost_usd=f"${query_cost:.4f}",
                )

            return result.output

    def _render_system_prompt(self, context: dict[str, Any]) -> str:
        """Render the system prompt template with context.

        Args:
            context: Template context variables

        Returns:
            Rendered system prompt
        """
        # Add heart-centered prompt
        context["heart_centered_prompt"] = get_prompt(detail_level="terse")

        # Add agent metadata
        context.update(
            {
                "agent_name": self.config.name,
                "agent_description": self.config.description,
                "model_name": self.model_name,
            }
        )

        # Render using Jinja2 (supports includes)
        template = self.jinja_env.from_string(self.config.system_prompt)
        return template.render(context)

    def _render_user_prompt(self, context: dict[str, Any]) -> str:
        """Render the user prompt template with context.

        Args:
            context: Template context variables

        Returns:
            Rendered user prompt
        """
        context.update(
            {
                "agent_name": self.config.name,
                "query_count": self.query_count,
            }
        )

        template = self.jinja_env.from_string(self.config.user_prompt)
        return template.render(context)

    def get_usage_summary(self) -> dict[str, Any]:
        """Get usage statistics for this agent instance.

        Returns:
            Dictionary with usage metrics
        """
        return {
            "agent_name": self.config.name,
            "model": self.model_name,
            "temperature": self.temperature,
            "query_count": self.query_count,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost": float(self.total_cost),
            "average_cost_per_query": (
                float(self.total_cost / self.query_count) if self.query_count else 0.0
            ),
            "has_structured_output": self.result_type is not None,
            "version": self.config.latest_version,
        }

    def explain(self) -> str:
        """Explain what this agent does.

        Returns:
            Human-readable description
        """
        return self.config.explain()

    def __repr__(self) -> str:
        """String representation of the agent."""
        return (
            f"BaseAgent("
            f"name='{self.config.name}', "
            f"model='{self.model_name}', "
            f"queries={self.query_count}, "
            f"cost=${self.total_cost:.4f})"
        )
