#!/usr/bin/env python3
"""Verify that a generated Claude plugin preserves the shared Skill content."""

from __future__ import annotations

import hashlib
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

from package_plugin import SHARED_SKILLS, package


INLINE_MARKDOWN_LINK = re.compile(
    r"(?<!!)\]\(\s*(?P<destination><[^>]+>|[^\s)]+)"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
)
REFERENCE_MARKDOWN_LINK = re.compile(r"(?<!!)\[[^]]+\]\[(?P<label>[^]]+)\]")
REFERENCE_MARKDOWN_DEFINITION = re.compile(
    r"^[ \t]{0,3}\[(?P<label>[^]]+)\]:[ \t]*"
    r"(?P<destination><[^>]+>|[^\s]+)(?:[ \t]+.*)?$",
    re.MULTILINE,
)


def skill_files(root: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(root): path.read_bytes()
        for path in sorted(root.glob("*/SKILL.md"))
    }


def coverage(source: dict[Path, bytes], packaged: dict[Path, bytes]) -> tuple[float, float, int, int]:
    """Return matching file and byte coverage against the canonical source."""
    matching_paths = source.keys() & packaged.keys()
    matching_files = sum(source[path] == packaged[path] for path in matching_paths)
    matching_bytes = sum(
        len(source[path])
        for path in matching_paths
        if source[path] == packaged[path]
    )
    source_bytes = sum(len(contents) for contents in source.values())
    return (
        matching_files / len(source) * 100,
        matching_bytes / source_bytes * 100,
        matching_files,
        matching_bytes,
    )


def package_files(root: Path) -> dict[Path, Path]:
    """Return every regular package file keyed by its package-relative path."""
    return {
        path.relative_to(root): path
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def digest(path: Path) -> str:
    """Return the SHA-256 digest of a package file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_entry_errors(output: Path) -> list[str]:
    """Return errors for symbolic links and non-regular package entries."""
    errors: list[str] = []
    for path in sorted(output.rglob("*")):
        relative = path.relative_to(output)
        if path.is_symlink():
            errors.append(f"invalid package artifact entry: {relative} (symbolic link)")
        elif not path.is_file() and not path.is_dir():
            errors.append(f"invalid package artifact entry: {relative} (not a regular file or directory)")
    return errors


def markdown_destination_errors(
    package_root: Path, relative: Path, document: Path, raw_target: str
) -> list[str]:
    """Validate one local Markdown destination from a packaged document."""
    target = urlsplit(raw_target.strip("<>"))
    if target.scheme or target.netloc or not target.path.endswith(".md"):
        return []
    destination = (document.parent / unquote(target.path)).resolve()
    if not destination.is_relative_to(package_root):
        return [f"packaged link escapes package: {relative} -> {target.path}"]
    if not destination.is_file() or destination.is_symlink():
        return [f"broken packaged link: {relative} -> {target.path}"]
    return []


def normalized_reference_label(label: str) -> str:
    """Normalize a Markdown reference label for case-insensitive matching."""
    return " ".join(label.split()).casefold()


def packaged_link_errors(output: Path) -> list[str]:
    """Return errors for package-local Markdown links that escape or do not resolve."""
    errors: list[str] = []
    package_root = output.resolve()
    for relative, document in package_files(output).items():
        if document.suffix.lower() != ".md":
            continue
        text = document.read_text(encoding="utf-8")
        for match in INLINE_MARKDOWN_LINK.finditer(text):
            errors.extend(markdown_destination_errors(package_root, relative, document, match["destination"]))

        definitions = {
            normalized_reference_label(match["label"]): match["destination"]
            for match in REFERENCE_MARKDOWN_DEFINITION.finditer(text)
        }
        for match in REFERENCE_MARKDOWN_LINK.finditer(text):
            label = normalized_reference_label(match["label"])
            if label not in definitions:
                errors.append(f"broken packaged reference link: {relative} -> [{match['label']}]")
                continue
            errors.extend(markdown_destination_errors(package_root, relative, document, definitions[label]))
    return errors


def validate_package(output: Path) -> list[str]:
    """Validate a Claude package's deterministic files, digests, and local links."""
    output = output.resolve()
    if not output.is_dir():
        return [f"package directory is missing: {output}"]

    errors = artifact_entry_errors(output)
    with tempfile.TemporaryDirectory(prefix="agentic-engineering-claude-expected-") as temporary:
        expected_root = Path(temporary) / "plugin"
        package(expected_root)
        expected = package_files(expected_root)

        actual = package_files(output)
        errors.extend(
            f"missing expected package file: {relative}"
            for relative in sorted(expected.keys() - actual.keys())
        )
        errors.extend(
            f"unexpected package file: {relative}"
            for relative in sorted(actual.keys() - expected.keys())
        )
        errors.extend(
            f"digest divergence: {relative}"
            for relative in sorted(expected.keys() & actual.keys())
            if digest(expected[relative]) != digest(actual[relative])
        )

    errors.extend(packaged_link_errors(output))
    return errors


def main() -> int:
    source = skill_files(SHARED_SKILLS)
    if not source:
        print("FAIL: no shared SKILL.md files found", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="agentic-engineering-claude-") as temporary:
        output = Path(temporary) / "plugin"
        package(output)
        packaged = skill_files(output / "skills")
        package_errors = validate_package(output)

    if package_errors:
        print("FAIL: Claude package integrity", file=sys.stderr)
        for error in package_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    file_coverage, byte_coverage, matching_files, matching_bytes = coverage(source, packaged)
    source_bytes = sum(len(contents) for contents in source.values())

    if source.keys() != packaged.keys() or file_coverage < 90 or byte_coverage < 90:
        print(
            "FAIL: shared content coverage "
            f"{file_coverage:.1f}% files, {byte_coverage:.1f}% bytes "
            f"({matching_files}/{len(source)} Skills)",
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
