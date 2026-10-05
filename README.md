# Repo Checkup

**Repo Checkup** is a small, local-only command-line tool that checks whether a project contains a handful of common maintainer-readiness files. It is intended as a quick first-pass checklist for personal projects and small teams—not as a quality score, security scanner, or substitute for code review.

## What it checks

Run it against a project directory. It reports pass/fail for these six items:

1. A non-empty root README (`README`, `README.md`, `README.rst`, or `README.txt`).
2. A recognized root project manifest, such as `pyproject.toml`, `package.json`, `Cargo.toml`, or `go.mod`.
3. A root license or copying notice.
4. A root `.gitignore` file.
5. At least one test file in `tests/` or at the repository root.
6. At least one `.yml` or `.yaml` workflow under `.github/workflows/`.

The checks are intentionally transparent: they inspect the presence and, for the README, non-emptiness of files. A passing result does **not** prove that a project builds, its tests are meaningful, its license is legally appropriate, or its workflow succeeds.

## Install

Requires Python 3.10 or newer.

```bash
python -m pip install -e .
```

For development, including tests and linting:

```bash
python -m pip install -e ".[dev]"
```

## Use

Check the current directory or provide a path:

```bash
repo-checkup .
repo-checkup /path/to/project
```

Get machine-readable JSON:

```bash
repo-checkup . --json
```

Exit codes:

- `0` — all six checks passed.
- `1` — the path was readable, but one or more checks did not pass.
- `2` — the supplied path does not exist or is not a directory.

## Privacy and limitations

Repo Checkup runs locally. It does not make network requests, execute project code, modify the inspected repository, read the contents of project files, or upload paths or results. It only examines root entries and whether a few expected files/directories exist. Do not treat it as a secret scanner or security audit.

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
ruff check .
python -m build
```

GitHub Actions runs lint, tests, and a distribution build on pushes and pull requests, using Python 3.10, 3.11, and 3.12. The workflow grants only read access to repository contents.

## Project layout

```text
src/repocheckup/       audit logic and CLI
tests/                 unit and CLI tests
.github/workflows/     CI workflow
pyproject.toml         packaging, test, and lint configuration
```

## License

MIT. See [LICENSE](LICENSE).
