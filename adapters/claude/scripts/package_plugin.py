#!/usr/bin/env python3
"""Create a self-contained Claude Code plugin from the shared Skill source."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

from markdown_links import parse_markdown_links


ADAPTER_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ADAPTER_ROOT.parents[1]
SHARED_SKILLS = REPOSITORY_ROOT / "skills"


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
        links = parse_markdown_links(document.read_text(encoding="utf-8"))
        for link in links.destinations:
            target = urlsplit(link.target)
            if target.scheme or target.netloc or not target.path.endswith(".md"):
                continue
            dependency = (document.parent / unquote(target.path)).resolve()
            if not dependency.is_relative_to(repository_root) or not dependency.is_file():
                continue
            pending.append(dependency)

    dependencies.remove(source.resolve())
    return dependencies


def packaged_path(
    source: Path,
    output: Path,
    repository_root: Path = REPOSITORY_ROOT,
    shared_skills: Path = SHARED_SKILLS,
) -> Path:
    """Map a local Markdown source to its deterministic package location."""
    if source.is_relative_to(repository_root / "docs"):
        return output / "docs" / source.relative_to(repository_root / "docs")
    if source.is_relative_to(shared_skills):
        return output / "skills" / source.relative_to(shared_skills)
    raise ValueError(f"local Markdown dependency cannot be packaged: {source}")


def rewrite_local_links(
    source: Path,
    destination: Path,
    output: Path,
    repository_root: Path = REPOSITORY_ROOT,
    shared_skills: Path = SHARED_SKILLS,
) -> None:
    """Rewrite copied-reference links for the package's directory layout."""
    text = source.read_text(encoding="utf-8")
    replacements: list[tuple[int, int, str]] = []
    for link in parse_markdown_links(text).destinations:
        target = urlsplit(link.target)
        if target.scheme or target.netloc or not target.path.endswith(".md"):
            continue
        local_target = (source.parent / unquote(target.path)).resolve()
        if not local_target.is_relative_to(repository_root) or not local_target.is_file():
            continue
        package_target = packaged_path(local_target, output, repository_root, shared_skills)
        relative_target = Path(os.path.relpath(package_target, destination.parent)).as_posix()
        rewritten = urlunsplit(("", "", relative_target, target.query, target.fragment))
        replacements.append((link.start, link.end, link.replace_target(rewritten)))

    for start, end, replacement in reversed(replacements):
        text = f"{text[:start]}{replacement}{text[end:]}"
    destination.write_text(text, encoding="utf-8")


def package(
    output: Path,
    *,
    adapter_root: Path = ADAPTER_ROOT,
    repository_root: Path = REPOSITORY_ROOT,
    shared_skills: Path = SHARED_SKILLS,
) -> None:
    """Write the minimal loadable plugin to a new or empty output directory."""
    output = output.resolve()
    adapter_root = adapter_root.resolve()
    repository_root = repository_root.resolve()
    shared_skills = shared_skills.resolve()
    if output == adapter_root or adapter_root in output.parents:
        raise ValueError("output must not be the adapter directory or one of its children")
    if output.exists() and not output.is_dir():
        raise ValueError("output must be a directory when it already exists")
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory must be new or empty")
    if not shared_skills.is_dir():
        raise ValueError(f"shared Skills directory is missing: {shared_skills}")

    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(adapter_root / ".claude-plugin", output / ".claude-plugin")
    shutil.copytree(shared_skills, output / "skills")

    dependencies = set().union(
        *(local_markdown_dependencies(skill, repository_root) for skill in shared_skills.glob("*/SKILL.md"))
    )
    references = sorted(
        dependency for dependency in dependencies if dependency.is_relative_to(repository_root / "docs")
    )
    for reference in references:
        destination = packaged_path(reference, output, repository_root, shared_skills)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(reference, destination)
    for reference in references:
        rewrite_local_links(
            reference,
            packaged_path(reference, output, repository_root, shared_skills),
            output,
            repository_root,
            shared_skills,
        )


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
