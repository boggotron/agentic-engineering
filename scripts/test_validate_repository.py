#!/usr/bin/env python3
"""Regression tests for the dependency-free repository validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


VALIDATOR = Path(__file__).with_name("validate_repository.py")


def create_repository(root: Path) -> None:
    (root / "skills" / "example-skill").mkdir(parents=True)
    (root / "skills" / "example-skill" / "SKILL.md").write_text(
        "---\nname: example-skill\ndescription: Example.\n---\n\n# Example\n",
        encoding="utf-8",
    )
    (root / "adapters" / "openai" / ".codex-plugin").mkdir(parents=True)
    (root / "adapters" / "openai" / ".codex-plugin" / "plugin.json").write_text(
        json.dumps({"name": "example", "version": "0.1.0"}), encoding="utf-8"
    )
    (root / "adapters" / "claude" / ".claude-plugin").mkdir(parents=True)
    (root / "adapters" / "claude" / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "example", "version": "0.1.0"}), encoding="utf-8"
    )
    (root / "adapters" / "openai" / "skills").symlink_to(root / "skills", target_is_directory=True)
    (root / "README.md").write_text("[Example](skills/example-skill/SKILL.md#example)\n", encoding="utf-8")


def validate(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--root", str(root)], text=True, capture_output=True, check=False
    )


class ValidatorTests(unittest.TestCase):
    def test_accepts_minimal_valid_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            self.assertEqual(validate(root).returncode, 0)

    def test_rejects_malformed_skill_broken_docs_and_invalid_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            (root / "skills" / "example-skill" / "SKILL.md").write_text("# no front matter\n", encoding="utf-8")
            (root / "README.md").write_text("[Missing](missing.md)\n", encoding="utf-8")
            (root / "adapters" / "openai" / ".codex-plugin" / "plugin.json").write_text("{", encoding="utf-8")
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing YAML front matter", result.stderr)
            self.assertIn("broken link", result.stderr)
            self.assertIn("invalid JSON", result.stderr)

    def test_runs_issue_14_harness_and_propagates_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            (root / "evals" / "examples").mkdir(parents=True)
            results = root / "evals" / "examples" / "compliant.json"
            results.write_text("{}\n", encoding="utf-8")
            (root / "evals" / "test_run.py").write_text(
                "import unittest\n\nclass HarnessTests(unittest.TestCase):\n    def test_contract(self):\n        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            runner = root / "evals" / "run.py"
            runner.write_text(
                "import json\nimport sys\nfrom pathlib import Path\nPath(__file__).with_name('arguments.json').write_text(json.dumps(sys.argv[1:]))\n",
                encoding="utf-8",
            )
            successful = validate(root)
            self.assertEqual(successful.returncode, 0, successful.stderr)
            self.assertEqual(
                json.loads((root / "evals" / "arguments.json").read_text()),
                ["--results", str(results.resolve()), "--json"],
            )
            runner.write_text("raise SystemExit(1)\n", encoding="utf-8")
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("evals/run.py failed", result.stderr)

    def test_rejects_invalid_future_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            (root / "schemas").mkdir()
            (root / "schemas" / "plan.schema.json").write_text("not JSON", encoding="utf-8")
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("schemas/plan.schema.json: invalid JSON", result.stderr)

    def test_rejects_malformed_yaml_front_matter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            (root / "skills" / "example-skill" / "SKILL.md").write_text(
                "---\nname: example-skill\ndescription: [unterminated\n---\n",
                encoding="utf-8",
            )
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid value for 'description'", result.stderr)


if __name__ == "__main__":
    unittest.main()
