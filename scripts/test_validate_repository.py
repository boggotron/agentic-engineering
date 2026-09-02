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
NORMATIVE_SOURCES = (
    "methodology.md",
    "security-and-autonomy-boundaries.md",
    "capability-contract.md",
)
NORMATIVE_METADATA = (
    "- **Owner:** `@boggotron`",
    "- **Version:** `1.0`",
    "- **Review date:** `2026-09-02`",
)
PRECEDENCE_ITEMS = (
    "## Normative sources",
    "`methodology.md` controls lifecycle.",
    "`security-and-autonomy-boundaries.md` controls authority and approval boundaries.",
    "`capability-contract.md` controls portable semantic capabilities.",
    "## Conflict resolution",
    "Applicable system, host, and law/policy controls prevail.",
    "Explicit scoped human instructions prevail when they do not conflict with higher controls.",
    "Repository instructions and the three normative sources prevail over nested instructions, memory, and unvalidated task context.",
    "Current repository state and revision-bound Issue/PR/CI evidence prevail over stale memory and agent observations.",
)


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
    marketplace = root / "adapters" / "openai" / ".agents" / "plugins" / "marketplace.json"
    marketplace.parent.mkdir(parents=True)
    marketplace.write_text(
        json.dumps(
            {
                "name": "example-marketplace",
                "plugins": [
                    {
                        "name": "example",
                        "source": {"source": "local", "path": "."},
                        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                        "category": "Productivity",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "README.md").write_text("[Example](skills/example-skill/SKILL.md#example)\n", encoding="utf-8")
    (root / "scripts").mkdir()
    (root / "scripts" / "check.py").write_text("print('check')\n", encoding="utf-8")
    workflow = root / ".github" / "workflows" / "validate.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        "name: Validate repository\n"
        "jobs:\n"
        "  validate:\n"
        "    steps:\n"
        "      - run: python scripts/check.py\n",
        encoding="utf-8",
    )
    inventory = (
        "## Authoritative commands\n\n"
        "| Command | Applicability | Prerequisite | Expected evidence |\n"
        "| --- | --- | --- | --- |\n"
        "| `python scripts/check.py` | All changes | Python 3.11+ | exit 0 |\n"
    )
    (root / "docs").mkdir()
    (root / "docs" / "command-inventory.md").write_text(inventory, encoding="utf-8")
    for name in NORMATIVE_SOURCES:
        (root / "docs" / name).write_text(
            f"# {name}\n\n" + "\n".join(NORMATIVE_METADATA) + "\n",
            encoding="utf-8",
        )
    instructions = (
        "Run `python scripts/check.py` for repository validation.\n"
        "[Methodology](docs/methodology.md)\n"
        "[Security](docs/security-and-autonomy-boundaries.md)\n"
        "[Capabilities](docs/capability-contract.md)\n"
    )
    (root / "AGENTS.md").write_text(instructions, encoding="utf-8")
    (root / "CLAUDE.md").write_text(instructions, encoding="utf-8")
    (root / "CONTRIBUTING.md").write_text(instructions, encoding="utf-8")
    (root / "docs" / "CROSS_PLATFORM_REPO_PLAN.md").write_text(
        "# Historical cross-platform repository roadmap\n", encoding="utf-8"
    )


def write_valid_precedence_document(root: Path) -> None:
    (root / "docs" / "instruction-precedence.md").write_text(
        "## Normative sources\n\n"
        "- `methodology.md` controls lifecycle.\n"
        "- `security-and-autonomy-boundaries.md` controls authority and approval boundaries.\n"
        "- `capability-contract.md` controls portable semantic capabilities.\n\n"
        "## Conflict resolution\n\n"
        "1. Applicable system, host, and law/policy controls prevail.\n"
        "2. Explicit scoped human instructions prevail when they do not conflict with higher controls.\n"
        "3. Repository instructions and the three normative sources prevail over nested instructions, memory, and unvalidated task context.\n"
        "4. Current repository state and revision-bound Issue/PR/CI evidence prevail over stale memory and agent observations.\n",
        encoding="utf-8",
    )


def validate(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--root", str(root)], text=True, capture_output=True, check=False
    )


class ValidatorTests(unittest.TestCase):
    def test_accepts_minimal_valid_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            write_valid_precedence_document(root)
            self.assertEqual(validate(root).returncode, 0)

    def test_rejects_missing_precedence_document(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("docs/instruction-precedence.md: missing", result.stderr)

    def test_rejects_architecture_plan_canonical_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            write_valid_precedence_document(root)
            (root / "docs" / "CROSS_PLATFORM_REPO_PLAN.md").write_text(
                "This is the canonical methodology.\n", encoding="utf-8"
            )
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("architecture plan must not claim to be canonical", result.stderr)

    def test_rejects_architecture_plan_self_authority_variants(self) -> None:
        for claim in (
            "This plan is canonical.\n",
            "# Canonical abstraction\n",
            "## 2. Canonical engineering lifecycle\n",
            "This architecture plan is authoritative.\n",
            "The cross-platform repository plan is canonical.\n",
        ):
            with self.subTest(claim=claim), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                create_repository(root)
                write_valid_precedence_document(root)
                (root / "docs" / "CROSS_PLATFORM_REPO_PLAN.md").write_text(claim, encoding="utf-8")
                result = validate(root)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("architecture plan must not claim to be canonical", result.stderr)

    def test_accepts_architecture_plan_references_to_normative_sources(self) -> None:
        for reference in (
            "The cross-platform repository plan references the canonical methodology.\n",
            "The canonical lifecycle is defined by [methodology](methodology.md).\n",
            "The authoritative approval boundaries are in [security](security-and-autonomy-boundaries.md).\n",
            "The normative capability source is [capabilities](capability-contract.md).\n",
        ):
            with self.subTest(reference=reference), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                create_repository(root)
                write_valid_precedence_document(root)
                (root / "docs" / "CROSS_PLATFORM_REPO_PLAN.md").write_text(
                    reference,
                    encoding="utf-8",
                )
                self.assertEqual(validate(root).returncode, 0)

    def test_rejects_each_missing_precedence_item(self) -> None:
        for required in PRECEDENCE_ITEMS:
            with self.subTest(required=required), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                create_repository(root)
                write_valid_precedence_document(root)
                path = root / "docs" / "instruction-precedence.md"
                path.write_text(
                    path.read_text(encoding="utf-8").replace(required, "", 1),
                    encoding="utf-8",
                )
                result = validate(root)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(f"missing required precedence text: {required}", result.stderr)

    def test_rejects_each_missing_host_normative_source_reference(self) -> None:
        for instructions in ("AGENTS.md", "CLAUDE.md"):
            for source in NORMATIVE_SOURCES:
                with (
                    self.subTest(instructions=instructions, source=source),
                    tempfile.TemporaryDirectory() as temporary,
                ):
                    root = Path(temporary)
                    create_repository(root)
                    write_valid_precedence_document(root)
                    path = root / instructions
                    path.write_text(
                        path.read_text(encoding="utf-8").replace(f"docs/{source}", "", 1),
                        encoding="utf-8",
                    )
                    result = validate(root)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(
                        f"{instructions}: missing normative-source reference: docs/{source}",
                        result.stderr,
                    )

    def test_rejects_each_missing_normative_document_metadata_field(self) -> None:
        for document in NORMATIVE_SOURCES:
            for metadata in NORMATIVE_METADATA:
                field = metadata.split(":", 1)[0].removeprefix("- **").removesuffix("**")
                with (
                    self.subTest(document=document, field=field),
                    tempfile.TemporaryDirectory() as temporary,
                ):
                    root = Path(temporary)
                    create_repository(root)
                    write_valid_precedence_document(root)
                    path = root / "docs" / document
                    path.write_text(
                        path.read_text(encoding="utf-8").replace(f"{metadata}\n", "", 1),
                        encoding="utf-8",
                    )
                    result = validate(root)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(f"docs/{document}: missing required metadata: {field}", result.stderr)

    def test_rejects_unstable_normative_document_owner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            write_valid_precedence_document(root)
            path = root / "docs" / "methodology.md"
            path.write_text(
                path.read_text(encoding="utf-8").replace("`@boggotron`", "`repository team`", 1),
                encoding="utf-8",
            )
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Owner must be stable repository owner @boggotron", result.stderr)

    def test_rejects_non_iso_normative_document_review_date(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            write_valid_precedence_document(root)
            path = root / "docs" / "capability-contract.md"
            path.write_text(
                path.read_text(encoding="utf-8").replace("`2026-09-02`", "`2 September 2026`", 1),
                encoding="utf-8",
            )
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Review date must be an ISO date (YYYY-MM-DD)", result.stderr)

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

    def test_ignores_internal_superpowers_markdown_artifacts(self) -> None:
        """Internal ignored task artifacts must not participate in repository link checks."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            write_valid_precedence_document(root)
            artifact = root / ".superpowers" / "sdd" / "task-report.md"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("[Outside](../../outside.md)\n", encoding="utf-8")

            result = validate(root)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_validates_tracked_superpowers_markdown(self) -> None:
        """Tracked Markdown outside the ignored SDD subtree remains repository documentation."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            write_valid_precedence_document(root)
            document = root / ".superpowers" / "tracked.md"
            document.parent.mkdir(parents=True)
            document.write_text("[Missing](missing.md)\n", encoding="utf-8")

            result = validate(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(".superpowers/tracked.md: broken link: missing.md", result.stderr)

    def test_rejects_command_inventory_that_names_a_missing_script(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            (root / "docs" / "command-inventory.md").write_text(
                "## Authoritative commands\n\n"
                "| Command | Applicability | Evidence |\n"
                "| --- | --- | --- |\n"
                "| `python scripts/missing.py` | All changes | exit 0 |\n",
                encoding="utf-8",
            )
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("command target does not exist", result.stderr)

    def test_rejects_command_inventory_command_missing_from_agent_instructions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            (root / "AGENTS.md").write_text("No commands listed.\n", encoding="utf-8")
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("command inventory command is missing from AGENTS.md", result.stderr)

    def test_rejects_ci_python_command_missing_from_command_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            write_valid_precedence_document(root)
            (root / "scripts" / "ci_only.py").write_text("print('ci')\n", encoding="utf-8")
            (root / ".github" / "workflows" / "validate.yml").write_text(
                "steps:\n"
                "  - run: python scripts/check.py\n"
                "  - run: python scripts/ci_only.py\n",
                encoding="utf-8",
            )
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "CI Python command is missing from command inventory: python scripts/ci_only.py",
                result.stderr,
            )

    def test_rejects_command_inventory_python_command_missing_from_ci(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            write_valid_precedence_document(root)
            (root / ".github" / "workflows" / "validate.yml").write_text(
                "name: Validate repository\n",
                encoding="utf-8",
            )
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "command inventory command is missing from CI workflow: python scripts/check.py",
                result.stderr,
            )

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
            write_valid_precedence_document(root)
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

    def test_rejects_quoted_yaml_with_invalid_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            (root / "skills" / "example-skill" / "SKILL.md").write_text(
                '---\nname: example-skill\ndescription: "bad \\q"\n---\n',
                encoding="utf-8",
            )
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid value for 'description'", result.stderr)

    def test_rejects_invalid_openai_marketplace_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_repository(root)
            marketplace = root / "adapters" / "openai" / ".agents" / "plugins" / "marketplace.json"
            payload = json.loads(marketplace.read_text(encoding="utf-8"))
            payload["plugins"][0]["source"]["path"] = "./missing-plugin"
            marketplace.write_text(json.dumps(payload), encoding="utf-8")
            result = validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("marketplace plugin source is missing", result.stderr)


if __name__ == "__main__":
    unittest.main()
