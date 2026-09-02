#!/usr/bin/env python3
"""Create a self-contained Claude Code plugin from the shared Skill source."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit


ADAPTER_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ADAPTER_ROOT.parents[1]
SHARED_SKILLS = REPOSITORY_ROOT / "skills"
MARKDOWN_LINK = re.compile(r"(?<!!)(?P<prefix>\]\()(?P<destination><[^>]+>|[^)\s]+)(?P<suffix>\))")


def local_markdown_dependencies(source: Path, repository_root: Path) -> set[Path]:
    """Return local Markdown files reachable from ``source`` within the repository."""
    repository_root = repository_root.resolve()
    pending = [source.resolve()]
    dependencies: set[Path] = set()

    while pending:
        document = pending.pop()
        if document in dependencies:
            continue
        dependencies.add(document)
        for match in MARKDOWN_LINK.finditer(document.read_text(encoding="utf-8")):
            target = urlsplit(match.group("destination").strip("<>"))
            if target.scheme or target.netloc or not target.path.endswith(".md"):
                continue
            dependency = (document.parent / unquote(target.path)).resolve()
            if not dependency.is_relative_to(repository_root) or not dependency.is_file():
                continue
            pending.append(dependency)

    dependencies.remove(source.resolve())
    return dependencies


def packaged_path(source: Path, output: Path) -> Path:
    """Map a local Markdown source to its deterministic package location."""
    if source.is_relative_to(REPOSITORY_ROOT / "docs"):
        return output / "docs" / source.relative_to(REPOSITORY_ROOT / "docs")
    if source.is_relative_to(SHARED_SKILLS):
        return output / "skills" / source.relative_to(SHARED_SKILLS)
    raise ValueError(f"local Markdown dependency cannot be packaged: {source}")


def rewrite_local_links(source: Path, destination: Path, output: Path) -> None:
    """Rewrite copied-reference links for the package's directory layout."""
    def rewrite(match: re.Match[str]) -> str:
        target = urlsplit(match.group("destination").strip("<>"))
        if target.scheme or target.netloc or not target.path.endswith(".md"):
            return match.group(0)
        local_target = (source.parent / unquote(target.path)).resolve()
        if not local_target.is_relative_to(REPOSITORY_ROOT) or not local_target.is_file():
            return match.group(0)
        package_target = packaged_path(local_target, output)
        relative_target = Path(os.path.relpath(package_target, destination.parent)).as_posix()
        rewritten = urlunsplit(("", "", relative_target, target.query, target.fragment))
        return f"{match.group('prefix')}{rewritten}{match.group('suffix')}"

    destination.write_text(MARKDOWN_LINK.sub(rewrite, source.read_text(encoding="utf-8")), encoding="utf-8")


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

    dependencies = set().union(
        *(local_markdown_dependencies(skill, REPOSITORY_ROOT) for skill in SHARED_SKILLS.glob("*/SKILL.md"))
    )
    references = sorted(
        dependency for dependency in dependencies if dependency.is_relative_to(REPOSITORY_ROOT / "docs")
    )
    for reference in references:
        destination = packaged_path(reference, output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(reference, destination)
    for reference in references:
        rewrite_local_links(reference, packaged_path(reference, output), output)


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
