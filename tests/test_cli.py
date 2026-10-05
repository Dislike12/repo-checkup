import json
from pathlib import Path

from repocheckup.cli import main


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


def test_cli_text_output_returns_success_for_complete_repo(tmp_path: Path, capsys) -> None:
    code = main([str(_make_ready_repo(tmp_path))])

    captured = capsys.readouterr()
    assert code == 0
    assert "Repo Checkup:" in captured.out
    assert "6/6 checks passed." in captured.out
    assert captured.err == ""


def test_cli_json_output_returns_success_for_complete_repo(tmp_path: Path, capsys) -> None:
    code = main(["--json", str(_make_ready_repo(tmp_path))])

    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert code == 0
    assert report["all_passed"] is True
    assert report["passed"] == report["total"] == 6
    assert len(report["checks"]) == 6


def test_cli_returns_one_when_readiness_checks_fail(tmp_path: Path, capsys) -> None:
    code = main([str(tmp_path)])

    captured = capsys.readouterr()
    assert code == 1
    assert "0/6 checks passed." in captured.out


def test_cli_returns_two_for_invalid_path(tmp_path: Path, capsys) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("not a directory", encoding="utf-8")

    code = main([str(file_path)])

    captured = capsys.readouterr()
    assert code == 2
    assert "not a directory" in captured.err
