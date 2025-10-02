"""Agent configuration parser for .agent.md files."""

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any
import re

from jinja2 import Template, TemplateSyntaxError
import frontmatter

from helpers.logger import logger


@dataclass
class AgentConfig:
    """Container for an agent's complete configuration from .agent.md file."""

    # Configuration from YAML frontmatter
    config: dict[str, Any] = field(default_factory=dict)

    # Parsed sections
    system_prompt: str = ""
    user_prompt: str = ""
    output_schema_code: str = ""
    context_builder_code: str = ""

    # Raw content for debugging
    raw_content: str = ""

    @classmethod
    @lru_cache(maxsize=32)
    def from_file(cls, file_path: Path | str) -> "AgentConfig":
        """Load agent configuration from .agent.md file.

        Args:
            file_path: Path to the .agent.md file

        Returns:
            AgentConfig instance with parsed content

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Agent config not found: {file_path}")

        # Parse with python-frontmatter
        post = frontmatter.load(file_path)
        config_dict = post.metadata
        content = post.content

        # Extract sections using HTML comment markers
        sections = cls._parse_sections(content)

        logger.debug(
            f"Loaded agent config from {file_path.name}",
            agent_name=config_dict.get("name", "Unknown"),
            sections_found=list(sections.keys()),
        )

        return cls(
            config=config_dict,
            system_prompt=sections.get("system_prompt", ""),
            user_prompt=sections.get("user_prompt", ""),
            output_schema_code=sections.get("output_schema", ""),
            context_builder_code=sections.get("context_builder", ""),
            raw_content=content,
        )

    @classmethod
    def clear_cache(cls):
        """Clear the agent config cache. Useful for testing or when files change."""
        cls.from_file.cache_clear()
        logger.debug("🗑️  Agent config cache cleared")

    @staticmethod
    def _parse_sections(content: str) -> dict[str, str]:
        """Parse sections from markdown content using HTML comment markers.

        Looks for patterns like:
            <!-- System Prompt -->
            ```jinja2
            content here
            ```

        Args:
            content: Markdown content after frontmatter

        Returns:
            Dictionary mapping section names to their content
        """
        sections = {}

        # Pattern: <!-- ([\w\s]+) -->\s*```(\w+)?\n(.*?)```
        # Captures: comment text, optional language, content
        pattern = r"<!-- ([\w\s]+) -->\s*```(\w+)?\n(.*?)```"

        for match in re.finditer(pattern, content, re.DOTALL):
            section_name = match.group(1)  # "System Prompt"
            language = match.group(2)  # "jinja2" or None
            code = match.group(3).strip()  # The actual content

            # Normalize section name to snake_case
            key = section_name.lower().replace(" ", "_")
            sections[key] = code

            logger.debug(
                f"Found section: {section_name} (language: {language or 'none'})"
            )

        return sections

    def render_system_prompt(self, context: dict[str, Any] | None = None) -> str:
        """Render the system prompt template with context.

        Args:
            context: Template context variables

        Returns:
            Rendered system prompt
        """
        if not self.system_prompt:
            return ""

        if context is None:
            context = {}

        # Add agent metadata to context
        context.update(
            {
                "agent_name": self.name,
                "agent_description": self.description,
            }
        )

        template = Template(self.system_prompt)
        return template.render(context)

    def render_user_prompt(self, context: dict[str, Any] | None = None) -> str:
        """Render the user prompt template with context.

        Args:
            context: Template context variables

        Returns:
            Rendered user prompt
        """
        if not self.user_prompt:
            return ""

        if context is None:
            context = {}

        template = Template(self.user_prompt)
        return template.render(context)

    def get_output_model(self):
        """Extract and instantiate the Output class from output schema code.

        Returns:
            The Output Pydantic model class

        Raises:
            ValueError: If no output schema defined or Output class not found
        """
        if not self.output_schema_code:
            raise ValueError(f"No output schema defined for {self.name}")

        # Execute the Python code to get the Output class
        # Note: exec is intentional - we're loading Pydantic models from .agent.md files
        namespace = {}
        try:
            exec(self.output_schema_code, namespace)
        except Exception as e:
            raise ValueError(f"Failed to execute output schema code: {e}") from e

        if "Output" not in namespace:
            raise ValueError(
                f"Output schema must define a class named 'Output'. Found: {list(namespace.keys())}"
            )

        return namespace["Output"]

    def validate(self) -> list[str]:
        """Validate the agent configuration for required fields.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required fields
        if not self.config.get("name"):
            errors.append("Missing required field: name")

        if not self.config.get("description"):
            errors.append("Missing required field: description")

        if not self.config.get("model"):
            errors.append("Missing required field: model")

        # Check for prompts
        if not self.system_prompt:
            errors.append("Missing system prompt section")

        if not self.user_prompt:
            errors.append("Missing user prompt section")

        # Validate Jinja2 template syntax
        if self.system_prompt:
            try:
                Template(self.system_prompt)
            except TemplateSyntaxError as e:
                errors.append(f"Invalid Jinja2 syntax in system prompt: {e}")

        if self.user_prompt:
            try:
                Template(self.user_prompt)
            except TemplateSyntaxError as e:
                errors.append(f"Invalid Jinja2 syntax in user prompt: {e}")

        # Validate temperature
        temperature = self.config.get("temperature")
        if temperature is not None and (
            not isinstance(temperature, int | float) or not 0 <= temperature <= 2
        ):
            errors.append("Temperature must be a number between 0 and 2")

        return errors

    @property
    def name(self) -> str:
        """Get the agent name."""
        return self.config.get("name", "Unknown Agent")

    @property
    def description(self) -> str:
        """Get the agent description."""
        return self.config.get("description", "No description provided")

    @property
    def model_name(self) -> str:
        """Get the model name (required field, no default)."""
        model = self.config.get("model")
        if not model:
            raise ValueError(f"Agent {self.name} missing required 'model' field")
        return model

    @property
    def temperature(self) -> float:
        """Get the temperature setting."""
        return self.config.get("temperature", 0.7)

    @property
    def latest_version(self) -> int:
        """Get the latest version number from evolution history."""
        history = self.config.get("evolution_history", [])
        if not history:
            return 1
        return max(entry.get("version", 1) for entry in history)

    def explain(self) -> str:
        """Explain what this agent does.

        Returns:
            Human-readable description of agent's purpose and capabilities
        """
        history = ""
        if self.latest_version > 1:
            history = f" (v{self.latest_version})"

        return f"{self.name}{history}: {self.description}"
