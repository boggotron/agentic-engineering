#!/usr/bin/env python3
"""Focused regression tests for the Claude Code package adapter."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).parent))

from check_shared_content import coverage
from package_plugin import __file__ as PACKAGER
from package_plugin import package


def local_markdown_targets(document: Path) -> list[Path]:
    """Return the package-local Markdown targets linked by ``document``."""
    targets: list[Path] = []
    for destination in re.findall(r"(?<!!)\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
        target = urlsplit(destination.strip().strip("<>"))
        if target.scheme or target.netloc or not target.path.endswith(".md"):
            continue
        targets.append((document.parent / unquote(target.path)).resolve())
    return targets


class PackagingTests(unittest.TestCase):
    def test_package_includes_transitive_references_with_resolving_links(self) -> None:
        """Catch a package that ships Skills but omits their local documentation."""
        with tempfile.TemporaryDirectory(prefix="agentic-engineering-claude-") as temporary:
            output = Path(temporary) / "plugin"
            package(output)
            package_root = output.resolve()

            for reference in (
                "docs/methodology.md",
                "docs/capability-contract.md",
                "docs/security-and-autonomy-boundaries.md",
                "docs/instruction-precedence.md",
            ):
                self.assertTrue((output / reference).is_file(), reference)

            for document in sorted(output.rglob("*.md")):
                for target in local_markdown_targets(document):
                    self.assertTrue(target.is_file(), f"{document.relative_to(output)} -> {target}")
                    self.assertTrue(target.is_relative_to(package_root), f"link escapes package: {target}")

    def test_altered_skill_does_not_count_as_shared(self) -> None:
        source = {Path("first/SKILL.md"): b"first", Path("second/SKILL.md"): b"second"}
        packaged = {Path("first/SKILL.md"): b"altered", Path("second/SKILL.md"): b"second"}

        file_coverage, byte_coverage, matching_files, matching_bytes = coverage(source, packaged)

        self.assertEqual((file_coverage, matching_files), (50.0, 1))
        self.assertLess(byte_coverage, 90.0)
        self.assertEqual(matching_bytes, len(b"second"))

    def test_existing_file_output_is_an_argparse_error(self) -> None:
        with tempfile.TemporaryDirectory(prefix="agentic-engineering-claude-") as temporary:
            output = Path(temporary) / "not-a-directory"
            output.write_text("not a directory", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, PACKAGER, "--output", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("error: output must be a directory when it already exists", result.stderr)


if __name__ == "__main__":
    unittest.main()
