#!/usr/bin/env python3
"""Synchronize the canonical Agent Skill into the Codex plugin package."""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "ratemyskill"
DESTINATION = ROOT / "plugins" / "ratemyskill" / "skills" / "ratemyskill"


def relative_files(root: Path) -> list[Path]:
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file())


def compare() -> list[str]:
    if not DESTINATION.is_dir():
        return [f"missing packaged skill: {DESTINATION.relative_to(ROOT)}"]
    source_files = relative_files(SOURCE)
    destination_files = relative_files(DESTINATION)
    problems: list[str] = []
    if source_files != destination_files:
        missing = sorted(set(source_files) - set(destination_files))
        extra = sorted(set(destination_files) - set(source_files))
        problems.extend(f"missing from package: {path}" for path in missing)
        problems.extend(f"extra in package: {path}" for path in extra)
    for relative in sorted(set(source_files) & set(destination_files)):
        if not filecmp.cmp(SOURCE / relative, DESTINATION / relative, shallow=False):
            problems.append(f"content differs: {relative}")
    return problems


def sync() -> None:
    expected_parent = ROOT / "plugins" / "ratemyskill" / "skills"
    if DESTINATION.parent != expected_parent or DESTINATION.name != "ratemyskill":
        raise RuntimeError("refusing to replace an unexpected destination")
    if not SOURCE.is_dir():
        raise RuntimeError(f"canonical skill is missing: {SOURCE}")
    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, DESTINATION)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when the packaged Codex skill differs from the canonical skill",
    )
    args = parser.parse_args()
    if not args.check:
        sync()
    problems = compare()
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    action = "matches" if args.check else "synchronized"
    print(f"Codex plugin skill {action} canonical skill")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
