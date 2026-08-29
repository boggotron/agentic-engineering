#!/usr/bin/env python3
"""Verify that a generated Claude plugin preserves the shared Skill content."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from package_plugin import SHARED_SKILLS, package


def skill_files(root: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(root): path.read_bytes()
        for path in sorted(root.glob("*/SKILL.md"))
    }


def main() -> int:
    source = skill_files(SHARED_SKILLS)
    if not source:
        print("FAIL: no shared SKILL.md files found", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="agentic-engineering-claude-") as temporary:
        output = Path(temporary) / "plugin"
        package(output)
        packaged = skill_files(output / "skills")

    matching_paths = source.keys() & packaged.keys()
    matching_bytes = sum(
        len(source[path])
        for path in matching_paths
        if source[path] == packaged[path]
    )
    source_bytes = sum(len(contents) for contents in source.values())
    file_coverage = len(matching_paths) / len(source) * 100
    byte_coverage = matching_bytes / source_bytes * 100

    if source.keys() != packaged.keys() or byte_coverage < 90:
        print(
            "FAIL: shared content coverage "
            f"{file_coverage:.1f}% files, {byte_coverage:.1f}% bytes "
            f"({len(matching_paths)}/{len(source)} Skills)",
            file=sys.stderr,
        )
        return 1

    print(
        "PASS: shared content coverage "
        f"{file_coverage:.1f}% files, {byte_coverage:.1f}% bytes "
        f"({len(source)}/{len(source)} Skills; {matching_bytes}/{source_bytes} bytes)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
