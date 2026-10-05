from pathlib import Path

import pytest

from repocheckup.audit import audit_repository


def _make_ready_repo(root: Path) -> Path:
    (root / "README.md").write_text("# Example\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname = 'example'\n", encoding="utf-8")
    (root / "LICENSE").write_text("Example license notice\n", encoding="utf-8")
    (root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_example.py").write_text("def test_example(): pass\n", encoding="utf-8")
    workflows = root / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text("name: CI\n", encoding="utf-8")
    return root


def test_complete_repository_passes_all_checks(tmp_path: Path) -> None:
    report = audit_repository(_make_ready_repo(tmp_path))

    assert report.all_passed
    assert report.passed_count == 6
    assert [check.check_id for check in report.checks] == [
        "readme",
        "manifest",
        "license",
        "gitignore",
        "tests",
        "ci",
    ]


def test_empty_directory_reports_each_missing_item(tmp_path: Path) -> None:
    report = audit_repository(tmp_path)

    assert not report.all_passed
    assert report.passed_count == 0
    assert len(report.checks) == 6
    assert all(not check.passed for check in report.checks)


def test_root_names_are_matched_case_insensitively(tmp_path: Path) -> None:
    (tmp_path / "rEaDmE.MD").write_text("# Example\n", encoding="utf-8")
    (tmp_path / "LiCeNsE").write_text("Example license notice\n", encoding="utf-8")
    (tmp_path / ".GiTiGnOrE").write_text("cache/\n", encoding="utf-8")
    (tmp_path / "Cargo.toml").write_text("[package]\nname = 'example'\n", encoding="utf-8")
    (tmp_path / "test_example.py").write_text("def test_example(): pass\n", encoding="utf-8")
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "checks.YAML").write_text("name: Checks\n", encoding="utf-8")

    report = audit_repository(tmp_path)

    assert report.all_passed


def test_empty_readme_does_not_pass(tmp_path: Path) -> None:
    (tmp_path / "README.md").touch()

    report = audit_repository(tmp_path)

    readme = next(check for check in report.checks if check.check_id == "readme")
    assert not readme.passed
    assert "empty" in readme.detail


def test_missing_path_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        audit_repository(tmp_path / "missing")


def test_file_path_raises_not_a_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("not a directory", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        audit_repository(file_path)
