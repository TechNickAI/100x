#!/usr/bin/env python3
"""Pre-commit wrapper for validating .agent.md files."""

from pathlib import Path
import sys


def main():
    """Validate .agent.md files passed as arguments."""
    # Get the files from command line arguments
    files_to_validate = sys.argv[1:]

    if not files_to_validate:
        return 0

    # Only process .agent.md files
    agent_files = [f for f in files_to_validate if f.endswith(".agent.md")]
    if not agent_files:
        return 0

    # Import validator
    try:
        from ai.core.validators import AgentValidator, format_validation_results
    except ImportError:
        # Dependencies not installed - skip silently
        return 0

    # Validate all files
    validator = AgentValidator()
    results = {}

    for file_path in agent_files:
        errors = validator.validate_file(Path(file_path))
        if errors:
            results[file_path] = errors

    # Show errors if any
    if results:
        output = format_validation_results(results, "human")
        print(output, file=sys.stderr)  # noqa: T201
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
