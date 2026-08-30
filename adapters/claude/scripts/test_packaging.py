#!/usr/bin/env python3
"""Focused regression tests for the Claude Code package adapter."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_shared_content import coverage
from package_plugin import __file__ as PACKAGER


class PackagingTests(unittest.TestCase):
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
