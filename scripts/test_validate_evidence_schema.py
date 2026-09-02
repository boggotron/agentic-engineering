#!/usr/bin/env python3
"""Regression tests for the dependency-free evidence-envelope validator."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate_evidence_schema import validate_envelope, validate_schema_files


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = Path(__file__).with_name("validate_evidence_schema.py")


def copy_schema_root(destination: Path) -> None:
    shutil.copytree(ROOT / "schemas", destination / "schemas")


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--root", str(root)],
        text=True,
        capture_output=True,
        check=False,
    )


class EvidenceSchemaValidationTests(unittest.TestCase):
    def test_accepts_canonical_fixture_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            self.assertEqual(run_validator(root).returncode, 0)

    def test_rejects_missing_required_envelope_field(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            fixture = root / "schemas/fixtures/evidence-envelope/valid.json"
            document = json.loads(fixture.read_text(encoding="utf-8"))
            del document["actor"]
            fixture.write_text(json.dumps(document), encoding="utf-8")
            result = run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing required field 'actor'", result.stderr)

    def test_rejects_unknown_top_level_envelope_field(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            fixture = root / "schemas/fixtures/evidence-envelope/valid.json"
            document = json.loads(fixture.read_text(encoding="utf-8"))
            document["unrecognized"] = True
            fixture.write_text(json.dumps(document), encoding="utf-8")
            result = run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown top-level field 'unrecognized'", result.stderr)

    def test_rejects_registry_without_supported_major_one(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            registry = root / "schemas/evidence-compatibility.json"
            document = json.loads(registry.read_text(encoding="utf-8"))
            document["families"]["evidence-envelope"]["supported_majors"] = [2]
            registry.write_text(json.dumps(document), encoding="utf-8")
            result = run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must support major 1", result.stderr)

    def test_rejects_changed_referenced_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            artifact = root / "schemas/fixtures/artifacts/source-plan.json"
            artifact.write_text('{"artifact":"source-plan","status":"changed"}\n', encoding="utf-8")
            result = run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("digest does not match", result.stderr)

    def test_rejects_invalid_nested_provenance_and_oversized_actor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            fixture = root / "schemas/fixtures/evidence-envelope/valid.json"
            document = json.loads(fixture.read_text(encoding="utf-8"))
            document["provenance"] = {"source": "host", "unexpected": True}
            document["actor"]["id"] = "a" * 257
            fixture.write_text(json.dumps(document), encoding="utf-8")
            result = run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("provenance must contain only source, run_id, and recorded_at", result.stderr)
            self.assertIn("actor id must be 1 to 256 characters", result.stderr)

    def test_rejects_duplicate_references(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            fixture = root / "schemas/fixtures/evidence-envelope/extension.json"
            document = json.loads(fixture.read_text(encoding="utf-8"))
            document["references"].append(document["references"][0].copy())
            fixture.write_text(json.dumps(document), encoding="utf-8")
            result = run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("references must not contain duplicates", result.stderr)

    def test_accepts_git_sha1_revision_for_detected_repository_format(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            fixture = root / "schemas/fixtures/evidence-envelope/valid.json"
            document = json.loads(fixture.read_text(encoding="utf-8"))
            document["revision"] = {"kind": "git-sha1", "value": "0123456789abcdef0123456789abcdef01234567"}
            fixture.write_text(json.dumps(document), encoding="utf-8")
            self.assertEqual(run_validator(root).returncode, 0)

    def test_rejects_migration_without_derived_from_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            fixture = root / "schemas/fixtures/evidence-envelope/valid.json"
            document = json.loads(fixture.read_text(encoding="utf-8"))
            document["migration"] = {"from_schema_version": "0.9.0"}
            fixture.write_text(json.dumps(document), encoding="utf-8")
            result = run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("migration requires a derived-from reference", result.stderr)

    def test_reports_external_url_reference_as_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            fixture = root / "schemas/fixtures/evidence-envelope/extension.json"
            document = json.loads(fixture.read_text(encoding="utf-8"))
            document["references"][0]["target"] = "https://example.invalid/evidence.json"
            fixture.write_text(json.dumps(document), encoding="utf-8")
            result = run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("external reference is unsupported by the local validator", result.stderr)

    def test_reports_file_uri_reference_as_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            fixture = root / "schemas/fixtures/evidence-envelope/extension.json"
            document = json.loads(fixture.read_text(encoding="utf-8"))
            document["references"][0]["target"] = "file:///private/evidence.json"
            fixture.write_text(json.dumps(document), encoding="utf-8")
            result = run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("external reference is unsupported by the local validator", result.stderr)

    def test_rejects_explicit_null_migration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            fixture = root / "schemas/fixtures/evidence-envelope/valid.json"
            document = json.loads(fixture.read_text(encoding="utf-8"))
            document["migration"] = None
            fixture.write_text(json.dumps(document), encoding="utf-8")
            result = run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("migration must identify an evidence-envelope source schema", result.stderr)

    def test_reports_malformed_nested_json_types_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            valid = root / "schemas/fixtures/evidence-envelope/valid.json"
            valid_document = json.loads(valid.read_text(encoding="utf-8"))
            valid_document["policy"]["id"] = 42
            valid.write_text(json.dumps(valid_document), encoding="utf-8")
            extension = root / "schemas/fixtures/evidence-envelope/extension.json"
            extension_document = json.loads(extension.read_text(encoding="utf-8"))
            extension_document["references"][0]["relation"] = []
            extension.write_text(json.dumps(extension_document), encoding="utf-8")
            result = run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("policy must have a namespaced id and SemVer version", result.stderr)
            self.assertIn("has an invalid relation, target, or digest", result.stderr)

    def test_fixture_shape_conforms_to_committed_stdlib_contract(self) -> None:
        schema = json.loads((ROOT / "schemas/evidence-envelope.schema.json").read_text(encoding="utf-8"))
        expectations = json.loads((ROOT / "schemas/fixtures/evidence-envelope-schema-expectations.json").read_text(encoding="utf-8"))
        family, errors = validate_schema_files(ROOT)
        self.assertEqual(errors, [])
        self.assertIsNotNone(family)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        fixture_root = ROOT / "schemas/fixtures/evidence-envelope"
        self.assertEqual(set(expectations), {path.name for path in fixture_root.glob("*.json")})
        for path in sorted(fixture_root.glob("*.json")):
            with self.subTest(fixture=path.name):
                shape_errors = validate_envelope(
                    json.loads(path.read_text(encoding="utf-8")), path, ROOT, family, shape_only=True
                )
                self.assertEqual(not shape_errors, expectations[path.name])

    def test_rejects_actor_enum_schema_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_schema_root(root)
            path = root / "schemas/evidence-envelope.schema.json"
            schema = json.loads(path.read_text(encoding="utf-8"))
            schema["$defs"]["actor"]["properties"]["kind"]["enum"] = ["human", "service"]
            path.write_text(json.dumps(schema), encoding="utf-8")
            result = run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("actor kind enum", result.stderr)


if __name__ == "__main__":
    unittest.main()
