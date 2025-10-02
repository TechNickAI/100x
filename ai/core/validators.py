"""Agent configuration validators for .agent.md files.

Provides comprehensive validation of .agent.md files, ensuring they meet
all requirements for syntax, structure, and schema validity.
"""

from dataclasses import dataclass
from pathlib import Path

from jinja2 import Template, TemplateSyntaxError

from ai.core.agent_config import AgentConfig
from helpers.logger import logger


@dataclass
class AgentValidationError:
    """Represents a single validation error with context."""

    line_number: int | None
    message: str
    error_type: str  # schema, template_syntax, structure
    severity: str = "error"  # error, warning

    def __str__(self) -> str:
        """String representation for display."""
        line_info = f"Line {self.line_number}: " if self.line_number else ""
        return f"[{self.error_type.upper()}] {line_info}{self.message}"


class AgentValidator:
    """Main validator that orchestrates all validation layers."""

    def validate_file(self, file_path: Path | str) -> list[AgentValidationError]:
        """Validate a single agent file through all validation layers.

        Args:
            file_path: Path to the .agent.md file to validate

        Returns:
            List of validation errors (empty if valid)
        """
        file_path = Path(file_path)
        errors = []

        logger.debug(f"🔍 Validating agent file: {file_path}")

        # Check if file exists
        if not file_path.exists():
            errors.append(
                AgentValidationError(
                    line_number=None,
                    message=f"File not found: {file_path}",
                    error_type="structure",
                )
            )
            return errors

        # Parse the agent config
        try:
            config = AgentConfig.from_file(file_path)
        except (FileNotFoundError, ValueError, TypeError) as e:
            errors.append(
                AgentValidationError(
                    line_number=None,
                    message=f"Failed to parse agent file: {e!s}",
                    error_type="structure",
                )
            )
            return errors  # Can't continue without valid parsing

        # Run all validation layers
        errors.extend(self._validate_yaml_structure(file_path))
        errors.extend(self._validate_config_schema(config))
        errors.extend(self._validate_jinja2_templates(config))
        errors.extend(self._validate_output_schema(config))

        if errors:
            logger.warning(f"❌ Found {len(errors)} validation error(s) in {file_path}")
        else:
            logger.success(f"✅ {file_path} passed all validation checks")

        return errors

    def validate_directory(
        self, dir_path: Path | str
    ) -> dict[str, list[AgentValidationError]]:
        """Validate all .agent.md files in a directory.

        Args:
            dir_path: Path to directory to search

        Returns:
            Dictionary mapping file paths to their validation errors
        """
        dir_path = Path(dir_path)
        results = {}

        # Find all .agent.md files recursively
        agent_files = list(dir_path.rglob("*.agent.md"))

        if not agent_files:
            logger.warning(f"⚠️ No .agent.md files found in {dir_path}")
            return results

        logger.info(f"🔍 Validating {len(agent_files)} agent files in {dir_path}")

        for agent_file in agent_files:
            relative_path = agent_file.relative_to(dir_path)
            errors = self.validate_file(agent_file)
            results[str(relative_path)] = errors

        # Summary
        total_errors = sum(len(errors) for errors in results.values())
        valid_files = len([errors for errors in results.values() if not errors])

        logger.info(
            f"📊 Validation complete: {valid_files}/{len(agent_files)} files valid, "
            f"{total_errors} total errors"
        )

        return results

    def _validate_yaml_structure(self, file_path: Path) -> list[AgentValidationError]:
        """Validate YAML frontmatter structure."""
        errors = []

        try:
            content = file_path.read_text()

            # Check for proper YAML frontmatter structure
            if not content.startswith("---\n"):
                errors.append(
                    AgentValidationError(
                        line_number=1,
                        message="File must start with YAML frontmatter delimiter '---'",
                        error_type="structure",
                    )
                )
                return errors

            # Find all occurrences of ---
            lines = content.split("\n")
            yaml_delimiters = []

            for i, line in enumerate(lines):
                if line.strip() == "---":
                    yaml_delimiters.append(i + 1)  # 1-based line numbers

            if len(yaml_delimiters) < 2:
                errors.append(
                    AgentValidationError(
                        line_number=None,
                        message="Missing closing YAML frontmatter delimiter '---'",
                        error_type="structure",
                    )
                )
                return errors

            # Check if there's content between the delimiters
            yaml_start = yaml_delimiters[0]
            yaml_end = yaml_delimiters[1]

            if yaml_end <= yaml_start + 1:
                errors.append(
                    AgentValidationError(
                        line_number=yaml_end,
                        message="Empty YAML frontmatter section",
                        error_type="structure",
                    )
                )

        except Exception as e:
            errors.append(
                AgentValidationError(
                    line_number=None,
                    message=f"Error validating YAML structure: {e!s}",
                    error_type="structure",
                )
            )

        return errors

    def _validate_config_schema(
        self, config: AgentConfig
    ) -> list[AgentValidationError]:
        """Validate the agent configuration using built-in validation."""
        errors = []

        # Use AgentConfig's built-in validation
        config_errors = config.validate()
        for error_msg in config_errors:
            errors.append(
                AgentValidationError(
                    line_number=None,
                    message=error_msg,
                    error_type="schema",
                )
            )

        return errors

    def _validate_jinja2_templates(
        self, config: AgentConfig
    ) -> list[AgentValidationError]:
        """Validate Jinja2 template syntax in prompt sections."""
        errors = []

        # Validate system prompt template
        if config.system_prompt:
            template_errors = self._validate_single_template(
                config.system_prompt, "System Prompt"
            )
            errors.extend(template_errors)

        # Validate user prompt template
        if config.user_prompt:
            template_errors = self._validate_single_template(
                config.user_prompt, "User Prompt"
            )
            errors.extend(template_errors)

        return errors

    def _validate_single_template(
        self, template_content: str, section_name: str
    ) -> list[AgentValidationError]:
        """Validate a single Jinja2 template."""
        errors = []

        try:
            # Try to parse the template - this will catch syntax errors
            Template(template_content)

        except TemplateSyntaxError as e:
            # Extract line number if available
            line_number = e.lineno
            errors.append(
                AgentValidationError(
                    line_number=line_number,
                    message=f"Jinja2 template syntax error in {section_name}: {e}",
                    error_type="template_syntax",
                )
            )
        except Exception as e:
            errors.append(
                AgentValidationError(
                    line_number=None,
                    message=f"Error validating {section_name} template: {e!s}",
                    error_type="template_syntax",
                )
            )

        return errors

    def _validate_output_schema(
        self, config: AgentConfig
    ) -> list[AgentValidationError]:
        """Validate the output schema if present."""
        errors = []

        # For .agent.md files, we check if output_schema_code exists
        if not config.output_schema_code:
            # No schema defined, which is fine
            return errors

        # Try to get the output model
        try:
            config.get_output_model()
        except ValueError as e:
            errors.append(
                AgentValidationError(
                    line_number=None,
                    message=f"Invalid output schema: {e!s}",
                    error_type="schema",
                )
            )

        return errors


def format_validation_results(
    results: dict[str, list[AgentValidationError]], output_format: str = "human"
) -> str:
    """Format validation results for display.

    Args:
        results: Dictionary mapping file paths to validation errors
        output_format: Format for output ("human", "json", "github")

    Returns:
        Formatted string representation
    """
    if output_format == "json":
        import json

        json_results = {}
        for file_path, errors in results.items():
            json_results[file_path] = [
                {
                    "line_number": error.line_number,
                    "message": error.message,
                    "error_type": error.error_type,
                    "severity": error.severity,
                }
                for error in errors
            ]
        return json.dumps(json_results, indent=2)

    if output_format == "github":
        # GitHub Actions format
        lines = []
        for file_path, errors in results.items():
            for error in errors:
                level = "error" if error.severity == "error" else "warning"
                line_info = f",line={error.line_number}" if error.line_number else ""
                lines.append(f"::{level} file={file_path}{line_info}::{error.message}")
        return "\n".join(lines)

    # Human-readable format
    lines = []
    total_errors = 0
    total_warnings = 0

    for file_path, errors in results.items():
        if errors:
            lines.append(f"\n📄 {file_path}:")
            for error in errors:
                icon = "❌" if error.severity == "error" else "⚠️"
                lines.append(f"  {icon} {error}")
                if error.severity == "error":
                    total_errors += 1
                else:
                    total_warnings += 1
        else:
            lines.append(f"\n✅ {file_path}: Valid")

    # Summary
    total_files = len(results)
    valid_files = len([errors for errors in results.values() if not errors])

    lines.append("\n📊 Summary:")
    lines.append(f"  Files: {valid_files}/{total_files} valid")
    if total_errors:
        lines.append(f"  Errors: {total_errors}")
    if total_warnings:
        lines.append(f"  Warnings: {total_warnings}")

    return "\n".join(lines)
