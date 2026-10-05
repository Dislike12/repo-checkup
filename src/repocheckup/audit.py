"""Read-only checks for basic repository readiness files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_README_NAMES = ("readme", "readme.md", "readme.rst", "readme.txt")
_MANIFEST_NAMES = (
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "cargo.toml",
    "go.mod",
    "composer.json",
    "pom.xml",
    "gemfile",
    "mix.exs",
    "requirements.txt",
)


@dataclass(frozen=True)
class CheckResult:
    """The result of one repository-readiness check."""

    check_id: str
    name: str
    passed: bool
    detail: str

    def as_dict(self) -> dict[str, str | bool]:
        """Return a JSON-serializable representation."""
        return {
            "id": self.check_id,
            "name": self.name,
            "passed": self.passed,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class AuditReport:
    """Results for the checks performed against one directory."""

    root: Path
    checks: tuple[CheckResult, ...]

    @property
    def passed_count(self) -> int:
        return sum(check.passed for check in self.checks)

    @property
    def all_passed(self) -> bool:
        return self.passed_count == len(self.checks)

    def as_dict(self) -> dict[str, object]:
        """Return a stable, JSON-serializable summary."""
        return {
            "root": str(self.root),
            "passed": self.passed_count,
            "total": len(self.checks),
            "all_passed": self.all_passed,
            "checks": [check.as_dict() for check in self.checks],
        }


def _is_test_file(path: Path) -> bool:
    name = path.name.casefold()
    return path.is_file() and (name.startswith("test_") or "_test." in name)


def audit_repository(path: str | Path = ".") -> AuditReport:
    """Check common project files without reading their contents or changing them.

    Args:
        path: Existing directory to inspect.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        NotADirectoryError: If ``path`` is not a directory.
        OSError: If the directory cannot be inspected.
    """
    candidate = Path(path).expanduser()
    if not candidate.exists():
        raise FileNotFoundError(f"path does not exist: {candidate}")
    if not candidate.is_dir():
        raise NotADirectoryError(f"path is not a directory: {candidate}")

    root = candidate.resolve()
    entries = tuple(root.iterdir())
    files = {entry.name.casefold(): entry for entry in entries if entry.is_file()}

    readme = next((files[name] for name in _README_NAMES if name in files), None)
    if readme is None:
        readme_result = CheckResult(
            "readme", "Root README", False, "No README file found in the project root."
        )
    elif readme.stat().st_size == 0:
        readme_result = CheckResult(
            "readme", "Root README", False, f"{readme.name} exists but is empty."
        )
    else:
        readme_result = CheckResult(
            "readme", "Root README", True, f"Found non-empty {readme.name}."
        )

    manifest = next((files[name] for name in _MANIFEST_NAMES if name in files), None)
    manifest_result = CheckResult(
        "manifest",
        "Project manifest",
        manifest is not None,
        (
            f"Found {manifest.name}."
            if manifest is not None
            else "No recognized root manifest was found."
        ),
    )

    license_file = next(
        (
            entry
            for folded_name, entry in files.items()
            if folded_name.startswith(("license", "copying"))
        ),
        None,
    )
    license_result = CheckResult(
        "license",
        "License notice",
        license_file is not None,
        (
            f"Found {license_file.name}."
            if license_file is not None
            else "No root LICENSE or COPYING file was found."
        ),
    )

    gitignore = files.get(".gitignore")
    gitignore_result = CheckResult(
        "gitignore",
        "Git ignore rules",
        gitignore is not None,
        (
            "Found .gitignore."
            if gitignore is not None
            else "No root .gitignore file was found."
        ),
    )

    tests_dir = root / "tests"
    test_files = tuple(root.glob("test_*")) + tuple(root.glob("*_test.*"))
    has_tests = any(_is_test_file(test_file) for test_file in test_files)
    if tests_dir.is_dir():
        has_tests = has_tests or any(_is_test_file(child) for child in tests_dir.iterdir())
    tests_result = CheckResult(
        "tests",
        "Test files",
        has_tests,
        (
            "Found at least one test file in tests/ or the project root."
            if has_tests
            else "No test_* or *_test.* file was found in tests/ or the project root."
        ),
    )

    workflows_dir = root / ".github" / "workflows"
    has_ci = workflows_dir.is_dir() and any(
        workflow.is_file() and workflow.suffix.casefold() in {".yml", ".yaml"}
        for workflow in workflows_dir.iterdir()
    )
    ci_result = CheckResult(
        "ci",
        "GitHub Actions workflow",
        has_ci,
        (
            "Found a YAML workflow in .github/workflows/."
            if has_ci
            else "No .yml or .yaml workflow was found in .github/workflows/."
        ),
    )

    return AuditReport(
        root=root,
        checks=(
            readme_result,
            manifest_result,
            license_result,
            gitignore_result,
            tests_result,
            ci_result,
        ),
    )
