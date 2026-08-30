#!/usr/bin/env python3
"""Create a self-contained Claude Code plugin from the shared Skill source."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


ADAPTER_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ADAPTER_ROOT.parents[1]
SHARED_SKILLS = REPOSITORY_ROOT / "skills"


def package(output: Path) -> None:
    """Write the minimal loadable plugin to a new or empty output directory."""
    output = output.resolve()
    if output == ADAPTER_ROOT or ADAPTER_ROOT in output.parents:
        raise ValueError("output must not be the adapter directory or one of its children")
    if output.exists() and not output.is_dir():
        raise ValueError("output must be a directory when it already exists")
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory must be new or empty")
    if not SHARED_SKILLS.is_dir():
        raise ValueError(f"shared Skills directory is missing: {SHARED_SKILLS}")

    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ADAPTER_ROOT / ".claude-plugin", output / ".claude-plugin")
    shutil.copytree(SHARED_SKILLS, output / "skills")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new or empty package directory")
    args = parser.parse_args()
    try:
        package(args.output)
    except ValueError as error:
        parser.error(str(error))
    print(f"Created Claude Code plugin at {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
