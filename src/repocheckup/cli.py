"""Command-line entry point for Repo Checkup."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from repocheckup.audit import AuditReport, audit_repository


def _format_text(report: AuditReport) -> str:
    lines = [f"Repo Checkup: {report.root}"]
    for check in report.checks:
        status = "PASS" if check.passed else "FAIL"
        lines.append(f"{status:4}  {check.name}: {check.detail}")
    lines.append(f"\n{report.passed_count}/{len(report.checks)} checks passed.")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return its process exit code."""
    parser = argparse.ArgumentParser(
        prog="repo-checkup",
        description="Check common readiness files in a local project directory.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        type=Path,
        metavar="PATH",
        help="project directory to inspect (default: current directory)",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="print machine-readable JSON instead of a text report",
    )
    args = parser.parse_args(argv)

    try:
        report = audit_repository(args.path)
    except OSError as exc:
        print(f"repo-checkup: {exc}", file=sys.stderr)
        return 2

    if args.json_output:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        print(_format_text(report))

    return 0 if report.all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
