#!/usr/bin/env python3
"""Validate the common evidence envelope without third-party dependencies."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
REVISION = re.compile(r"^[0-9a-f]{64}$")
TYPE_NAME = re.compile(r"^[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)+$")
EVIDENCE_ID = re.compile(r"^urn:agentic-engineering:evidence:[a-z0-9][a-z0-9-]{0,127}$")
ROLE = re.compile(r"^[a-z][a-z0-9-]*$")
REQUIRED = {"schema", "schema_version", "evidence_type", "id", "repository", "revision", "policy", "produced_at", "actor", "payload"}
ALLOWED = REQUIRED | {"provenance", "references", "extensions", "expectation"}
RELATIONS = {"derived-from", "supports", "supersedes", "describes"}


def read_json(path: Path, errors: list[str]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"{path}: invalid JSON ({error})")
        return None


def is_semver(value: object) -> bool:
    return isinstance(value, str) and bool(SEMVER.fullmatch(value))


def major(version: str) -> int:
    return int(version.split(".", 1)[0])


def validate_schema_files(root: Path) -> tuple[dict[str, object] | None, list[str]]:
    errors: list[str] = []
    schema = read_json(root / "schemas/evidence-envelope.schema.json", errors)
    registry = read_json(root / "schemas/evidence-compatibility.json", errors)
    if not isinstance(schema, dict):
        errors.append("evidence envelope schema must be a JSON object")
    else:
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append("evidence envelope schema must declare Draft 2020-12")
        if schema.get("$id") != "https://github.com/boggotron/agentic-engineering/schemas/evidence-envelope.schema.json":
            errors.append("evidence envelope schema must declare its stable identifier")
        if set(schema.get("required", [])) != REQUIRED:
            errors.append("evidence envelope schema required fields do not match the common contract")
        if schema.get("additionalProperties") is not False:
            errors.append("evidence envelope schema must reject unknown top-level fields")
    if not isinstance(registry, dict):
        errors.append("evidence compatibility registry must be a JSON object")
        return None, errors
    family = registry.get("families", {}).get("evidence-envelope") if isinstance(registry.get("families"), dict) else None
    if registry.get("schema") != "evidence-compatibility-registry" or not is_semver(registry.get("registry_version")):
        errors.append("evidence compatibility registry has an invalid identity or version")
    if not isinstance(family, dict):
        errors.append("evidence compatibility registry must contain evidence-envelope")
        return None, errors
    if family.get("supported_majors") != [1]:
        errors.append("evidence compatibility registry must support major 1 only")
    if family.get("current_version") != "1.0.0":
        errors.append("evidence compatibility registry must declare current version 1.0.0")
    for key, value in {
        "compatibility": "same-major-with-explicit-registry-support",
        "unknown_top_level_fields": "reject",
        "extension_policy": "reverse-dns-namespace-preserve-unknown",
        "migration_policy": "immutable-derived-from-reference",
    }.items():
        if family.get(key) != value:
            errors.append(f"evidence compatibility registry has invalid {key}")
    return family, errors


def validate_envelope(document: object, path: Path, root: Path, family: dict[str, object]) -> list[str]:
    errors: list[str] = []
    prefix = str(path.relative_to(root))
    if not isinstance(document, dict):
        return [f"{prefix}: envelope must be a JSON object"]
    for field in sorted(REQUIRED - document.keys()):
        errors.append(f"{prefix}: missing required field '{field}'")
    for field in sorted(document.keys() - ALLOWED):
        errors.append(f"{prefix}: unknown top-level field '{field}'")
    if document.get("schema") != "evidence-envelope":
        errors.append(f"{prefix}: schema must be 'evidence-envelope'")
    version = document.get("schema_version")
    if not is_semver(version):
        errors.append(f"{prefix}: schema_version must be SemVer")
    elif major(version) not in family.get("supported_majors", []):
        errors.append(f"{prefix}: schema_version {version} is incompatible with the registry")
    if not isinstance(document.get("evidence_type"), str) or not TYPE_NAME.fullmatch(document["evidence_type"]):
        errors.append(f"{prefix}: evidence_type must be a namespaced type")
    if not isinstance(document.get("id"), str) or not EVIDENCE_ID.fullmatch(document["id"]):
        errors.append(f"{prefix}: id must be a stable evidence URN")
    repository = document.get("repository")
    if not isinstance(repository, str) or not (urlparse(repository).scheme and urlparse(repository).netloc):
        errors.append(f"{prefix}: repository must be an absolute URI")
    revision = document.get("revision")
    if not isinstance(revision, dict) or revision.get("kind") != "git-sha256" or not isinstance(revision.get("value"), str) or not REVISION.fullmatch(revision["value"]):
        errors.append(f"{prefix}: revision must be an immutable git-sha256 identifier")
    policy = document.get("policy")
    if not isinstance(policy, dict) or not TYPE_NAME.fullmatch(policy.get("id", "")) or not is_semver(policy.get("version")):
        errors.append(f"{prefix}: policy must have a namespaced id and SemVer version")
    timestamp = document.get("produced_at")
    try:
        if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
            raise ValueError
        dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{prefix}: produced_at must be an RFC 3339 UTC timestamp")
    actor = document.get("actor")
    if not isinstance(actor, dict) or actor.get("kind") not in {"human", "agent", "service"} or not isinstance(actor.get("id"), str) or not actor["id"] or not isinstance(actor.get("role"), str) or not ROLE.fullmatch(actor["role"]):
        errors.append(f"{prefix}: actor must identify a supported kind, id, and role")
    if not isinstance(document.get("payload"), dict):
        errors.append(f"{prefix}: payload must be an object")
    extensions = document.get("extensions")
    if extensions is not None and (not isinstance(extensions, dict) or any(not TYPE_NAME.fullmatch(key) for key in extensions)):
        errors.append(f"{prefix}: extensions must use reverse-DNS namespaces")
    references = document.get("references", [])
    if not isinstance(references, list):
        errors.append(f"{prefix}: references must be an array")
    else:
        for index, reference in enumerate(references):
            reference_prefix = f"{prefix}: references[{index}]"
            if not isinstance(reference, dict) or set(reference) != {"relation", "target", "digest"}:
                errors.append(f"{reference_prefix}: must contain only relation, target, and digest")
                continue
            if reference["relation"] not in RELATIONS or not isinstance(reference["target"], str) or not reference["target"] or not isinstance(reference["digest"], str) or not SHA256.fullmatch(reference["digest"]):
                errors.append(f"{reference_prefix}: has an invalid relation, target, or digest")
                continue
            target = (path.parent / reference["target"]).resolve()
            try:
                target.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{reference_prefix}: target escapes evidence root")
                continue
            try:
                actual = "sha256:" + hashlib.sha256(target.read_bytes()).hexdigest()
            except OSError:
                errors.append(f"{reference_prefix}: target is a stale reference")
                continue
            if actual != reference["digest"]:
                errors.append(f"{reference_prefix}: digest does not match target bytes")
    return errors


def validate(root: Path, fixtures: Path | None = None) -> list[str]:
    family, errors = validate_schema_files(root)
    if family is None:
        return errors
    fixture_root = fixtures or root / "schemas/fixtures/evidence-envelope"
    for path in sorted(fixture_root.glob("*.json")):
        document_errors: list[str] = []
        document = read_json(path, document_errors)
        if document is not None:
            document_errors.extend(validate_envelope(document, path, root, family))
        expectation = document.get("expectation") if isinstance(document, dict) else None
        actual = "valid" if not document_errors else "invalid"
        if expectation not in {"valid", "invalid"}:
            errors.append(f"{path.relative_to(root)}: expectation must be valid or invalid")
        elif expectation != actual:
            errors.extend(document_errors or [f"{path.relative_to(root)}: expected {expectation}, got {actual}"])
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    arguments = parser.parse_args()
    errors = validate(arguments.root.resolve())
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
