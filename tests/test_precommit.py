"""Test pre-commit configuration is valid."""

import subprocess
from pathlib import Path


def test_precommit_config_exists():
    """Verify pre-commit config file exists."""
    project_root = Path(__file__).parent.parent
    assert (project_root / ".pre-commit-config.yaml").exists()


def test_precommit_config_valid():
    """Verify pre-commit configuration is valid."""
    # pre-commit validate-config checks YAML syntax and hook definitions
    result = subprocess.run(
        ["pre-commit", "validate-config"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"pre-commit config invalid: {result.stderr}"


def test_precommit_manifest_valid():
    """Verify pre-commit hook manifests are valid."""
    # pre-commit validate-manifest checks that hooks are properly defined
    result = subprocess.run(
        ["pre-commit", "validate-manifest"],
        capture_output=True,
        text=True,
    )

    # This returns 0 even if there's no manifest (we're not a hook repo),
    # so we just check it doesn't error out
    assert result.returncode == 0, f"pre-commit manifest check failed: {result.stderr}"
