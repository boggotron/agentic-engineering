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

from check_shared_content import coverage, validate_package
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

    def test_package_validation_reports_a_missing_packaged_reference(self) -> None:
        """Catch a package whose copied normative dependency was removed."""
        with tempfile.TemporaryDirectory(prefix="agentic-engineering-claude-") as temporary:
            output = Path(temporary) / "plugin"
            package(output)
            (output / "docs" / "methodology.md").unlink()

            errors = validate_package(output)

        self.assertIn("missing expected package file: docs/methodology.md", errors)

    def test_package_validation_reports_an_unexpected_artifact_file(self) -> None:
        """Catch a package that contains a file the deterministic layout does not allow."""
        with tempfile.TemporaryDirectory(prefix="agentic-engineering-claude-") as temporary:
            output = Path(temporary) / "plugin"
            package(output)
            (output / "unexpected-artifact.txt").write_text("unexpected", encoding="utf-8")

            errors = validate_package(output)

        self.assertIn("unexpected package file: unexpected-artifact.txt", errors)

    def test_package_validation_reports_a_skill_digest_divergence(self) -> None:
        """Catch a package whose canonical Skill bytes have been altered."""
        with tempfile.TemporaryDirectory(prefix="agentic-engineering-claude-") as temporary:
            output = Path(temporary) / "plugin"
            package(output)
            skill = output / "skills" / "engineering-workflow" / "SKILL.md"
            skill.write_text(skill.read_text(encoding="utf-8") + "\nAltered package.\n", encoding="utf-8")

            errors = validate_package(output)

        self.assertIn("digest divergence: skills/engineering-workflow/SKILL.md", errors)

    def test_package_validation_rejects_a_skill_symlink(self) -> None:
        """Catch an expected package file replaced with a symlink outside the artifact."""
        with tempfile.TemporaryDirectory(prefix="agentic-engineering-claude-") as temporary:
            output = Path(temporary) / "plugin"
            package(output)
            skill = output / "skills" / "engineering-workflow" / "SKILL.md"
            external = Path(temporary) / "external-skill.md"
            external.write_text("external", encoding="utf-8")
            skill.unlink()
            skill.symlink_to(external)

            errors = validate_package(output)

        self.assertIn("invalid package artifact entry: skills/engineering-workflow/SKILL.md (symbolic link)", errors)

    def test_package_validation_rejects_a_directory_symlink(self) -> None:
        """Catch an unexpected directory symlink that could conceal external content."""
        with tempfile.TemporaryDirectory(prefix="agentic-engineering-claude-") as temporary:
            output = Path(temporary) / "plugin"
            package(output)
            external = Path(temporary) / "external-directory"
            external.mkdir()
            (output / "linked-directory").symlink_to(external, target_is_directory=True)

            errors = validate_package(output)

        self.assertIn("invalid package artifact entry: linked-directory (symbolic link)", errors)

    def test_package_validation_reports_an_inline_link_escape_with_a_title(self) -> None:
        """Catch an escaping inline Markdown link whose destination has an optional title."""
        with tempfile.TemporaryDirectory(prefix="agentic-engineering-claude-") as temporary:
            output = Path(temporary) / "plugin"
            package(output)
            document = output / "docs" / "methodology.md"
            document.write_text('[x](../../outside.md "title")\n', encoding="utf-8")

            errors = validate_package(output)

        self.assertIn('packaged link escapes package: docs/methodology.md -> ../../outside.md', errors)

    def test_package_validation_reports_a_reference_link_escape(self) -> None:
        """Catch an escaping package-local reference-style Markdown link."""
        with tempfile.TemporaryDirectory(prefix="agentic-engineering-claude-") as temporary:
            output = Path(temporary) / "plugin"
            package(output)
            document = output / "docs" / "methodology.md"
            document.write_text('[x][ref]\n\n[ref]: ../../outside.md\n', encoding="utf-8")

            errors = validate_package(output)

        self.assertIn('packaged link escapes package: docs/methodology.md -> ../../outside.md', errors)

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
