"""Test requirements files for common deployment errors."""

import subprocess
from pathlib import Path


def test_requirements_files_exist():
    """Verify all required requirements files exist."""
    project_root = Path(__file__).parent.parent

    assert (project_root / "requirements" / "requirements.in").exists()
    assert (project_root / "requirements" / "requirements.txt").exists()
    assert (project_root / "requirements" / "requirements-dev.txt").exists()
    assert (project_root / "requirements" / "requirements-test.txt").exists()


def test_requirements_in_compiles():
    """Verify requirements.in compiles without errors."""
    import tempfile

    project_root = Path(__file__).parent.parent
    requirements_in = project_root / "requirements" / "requirements.in"

    # Compile to a temp file to verify it works without modifying anything
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        result = subprocess.run(
            ["uv", "pip", "compile", str(requirements_in), "-o", tmp.name],
            capture_output=True,
            text=True,
        )
        Path(tmp.name).unlink()  # Clean up

    assert result.returncode == 0, f"requirements.in failed to compile: {result.stderr}"


def test_no_dependency_conflicts():
    """Verify installed packages have no conflicts."""
    # uv pip check verifies no broken dependencies in the current environment
    result = subprocess.run(
        ["uv", "pip", "check"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Dependency conflicts found: {result.stdout}"


def test_requirements_txt_is_locked():
    """Verify requirements.txt contains locked versions (==) not loose pins."""
    project_root = Path(__file__).parent.parent
    requirements_txt = project_root / "requirements" / "requirements.txt"

    content = requirements_txt.read_text()
    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.startswith("#")
    ]

    for line in lines:
        # Skip continuation lines and editable installs
        if line.startswith("-") or line.startswith("git+"):
            continue

        # Verify we're using == (locked) not >= or ~ (loose)
        assert "==" in line or line.startswith("-e"), (
            f"requirements.txt should have locked versions (==), found: {line}"
        )
