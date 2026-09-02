#!/usr/bin/env python3
"""Validate the repository's portable Skills, adapters, documentation, and eval hook.

This validator uses only the Python standard library so it can run in a clean
GitHub Actions checkout.  It is deliberately a repository validator rather
than a replacement for host-native plugin validators or an evaluation harness.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse


SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")
YAML_FIELD = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):(?:[ \t]+(.*))?$")
COMMAND_INVENTORY = Path("docs/command-inventory.md")
COMMAND_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|")
CI_WORKFLOW = Path(".github/workflows/validate.yml")
RISK_CLASSIFICATION_SCHEMA = Path("schemas/risk-classification.schema.json")
RISK_SCHEMA_REQUIRED_FIELDS = ("$schema", "$id", "type", "additionalProperties", "required", "properties")
RISK_FIXTURES = (
    "r0-documentation.json", "r1-refactor.json", "r2-feature.json", "r3-sensitive-data.json",
    "r4-destructive-effect.json", "boundary-stricter-signal.json", "human-unknown-input.json",
    "human-conflicting-input.json", "human-policy-change.json", "human-r4-authorization.json", "r4-security-control-weakening.json", "human-unknown-conflicting-inputs.json",
)
RISK_FIXTURE_LEVELS = {
    "r0-documentation.json": "R0", "r1-refactor.json": "R1", "r2-feature.json": "R2",
    "r3-sensitive-data.json": "R3", "r4-destructive-effect.json": "R4",
    "boundary-stricter-signal.json": "R3", "human-unknown-input.json": "R3",
    "human-conflicting-input.json": "R3", "human-policy-change.json": "R3",
    "human-r4-authorization.json": "R4", "r4-security-control-weakening.json": "R4", "human-unknown-conflicting-inputs.json": "R3",
}
RISK_RECORD_FIELDS = {"schema_version", "inputs", "decision"}
RISK_INPUT_FIELDS = {"change_types", "affected_boundaries", "data_and_secrets", "external_effects", "privilege", "reversibility", "blast_radius", "compatibility", "verification_strength", "material_unknowns", "material_conflicts", "changes_classification_enforcement", "security_control_direction", "action_authorization_required"}
RISK_DECISION_FIELDS = {"risk_level", "rationale", "confidence", "human_classification_required", "escalation_reasons"}
RISK_SCALAR_ENUMS = {"data_and_secrets": {"none", "internal", "personal_data", "sensitive_data", "secret", "unknown"}, "external_effects": {"none", "user_visible", "third_party", "production", "unknown"}, "privilege": {"none", "unchanged", "reduced", "increased", "secret_authority", "unknown"}, "reversibility": {"fully_reversible", "rollback_planned", "difficult_to_reverse", "irreversible", "unknown"}, "blast_radius": {"local", "repository", "user_population", "organization", "production", "unknown"}, "compatibility": {"none", "internal", "consumer_compatible", "consumer_breaking", "unknown"}, "verification_strength": {"strong", "partial", "insufficient", "unknown"}, "security_control_direction": {"not_applicable", "strengthened", "unchanged", "weakened", "unknown"}}
RISK_REASONS = {"unknown_material_input", "conflicting_material_input", "stricter_applicable_signal", "classification_enforcement_change", "r4_action_authorization"}
CI_PYTHON_RUN = re.compile(
    r"^\s*(?:-\s*)?run:\s*(['\"]?)(python(?:3(?:\.\d+)?)?\s+.+?)\1\s*$"
)
PRECEDENCE_DOCUMENT = Path("docs/instruction-precedence.md")
NORMATIVE_SOURCES = (
    "methodology.md",
    "security-and-autonomy-boundaries.md",
    "capability-contract.md",
)
PRECEDENCE_TEXT = (
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
NORMATIVE_OWNER = "@boggotron"
NORMATIVE_METADATA = re.compile(
    r"^- \*\*(Owner|Version|Review date):\*\* `([^`]+)`\s*$",
    re.MULTILINE,
)
ARCHITECTURE_PLAN_AUTHORITY_CLAIM = re.compile(
    r"^#{1,6}\s+(?:\d+(?:\.\d+)*[.)]?\s+)?canonical\b|"
    r"\bthis is the canonical (?:engineering )?methodology\b|"
    r"\b(?:this|the)(?:\s+(?:cross-platform|architecture|repository)){0,2}\s+"
    r"(?:plan|document|roadmap)\b\s+(?:is|remains|serves\s+as|acts\s+as)\s+"
    r"(?:the\s+)?(?:canonical|authoritative|normative)\b",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass
class Validation:
    errors: list[str]

    def fail(self, message: str) -> None:
        self.errors.append(message)


def read_json(path: Path, validation: Validation) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        validation.fail(f"{path}: invalid JSON ({error})")
        return None


def parse_yaml_scalar(value: str) -> str:
    """Parse the flat scalar subset used by portable Skill front matter.

    Skills intentionally use a flat mapping of unquoted plain scalar metadata.
    Parsing that subset here keeps validation dependency-free while rejecting
    malformed YAML rather than extracting fields with a regular expression.
    """
    if not value or value.startswith(("[", "{", "- ", "|", ">", "&", "*", "!", "'", '"')):
        raise ValueError("expected a non-empty scalar value")
    if any(character in value for character in "[]{}"):
        raise ValueError("flow collections are not supported in Skill front matter")
    return value.split(" #", 1)[0].rstrip()


def parse_skill_front_matter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing YAML front matter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("unterminated YAML front matter") from error

    fields: dict[str, str] = {}
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = YAML_FIELD.fullmatch(line)
        if not match:
            raise ValueError(f"invalid YAML mapping on line {number}")
        key, raw_value = match.groups()
        if key in fields:
            raise ValueError(f"duplicate YAML key '{key}' on line {number}")
        try:
            fields[key] = parse_yaml_scalar(raw_value or "")
        except ValueError as error:
            raise ValueError(f"invalid value for '{key}' on line {number}: {error}") from error
    return fields


def validate_skills(root: Path, validation: Validation) -> None:
    skills = root / "skills"
    if not skills.is_dir():
        validation.fail("skills/: missing canonical Skills directory")
        return

    skill_directories = sorted(path for path in skills.iterdir() if path.is_dir())
    if not skill_directories:
        validation.fail("skills/: no Skill directories found")
    for directory in skill_directories:
        path = directory / "SKILL.md"
        if not path.is_file():
            validation.fail(f"{path.relative_to(root)}: missing SKILL.md")
            continue
        try:
            fields = parse_skill_front_matter(path)
        except (OSError, UnicodeDecodeError, ValueError) as error:
            validation.fail(f"{path.relative_to(root)}: {error}")
            continue
        name = fields.get("name", "")
        if not SKILL_NAME.fullmatch(name):
            validation.fail(f"{path.relative_to(root)}: front-matter name must be kebab-case")
        if not fields.get("description"):
            validation.fail(f"{path.relative_to(root)}: front matter requires a description")
        if name and name != directory.name:
            validation.fail(f"{path.relative_to(root)}: name must match directory '{directory.name}'")


def validate_json_artifacts(root: Path, validation: Validation) -> None:
    manifests = sorted(root.glob("adapters/**/.codex-plugin/plugin.json"))
    manifests += sorted(root.glob("adapters/**/.claude-plugin/plugin.json"))
    if not manifests:
        validation.fail("adapters/: no plugin manifests found")
    for path in manifests:
        data = read_json(path, validation)
        if not isinstance(data, dict):
            validation.fail(f"{path.relative_to(root)}: manifest must be a JSON object")
            continue
        for field in ("name", "version"):
            if not isinstance(data.get(field), str) or not data[field].strip():
                validation.fail(f"{path.relative_to(root)}: manifest requires non-empty '{field}'")

    for path in sorted((root / "schemas").glob("**/*.json")) if (root / "schemas").is_dir() else []:
        data = read_json(path, validation)
        if not isinstance(data, dict):
            validation.fail(f"{path.relative_to(root)}: schema must be a JSON object")
        elif "$schema" in data and not isinstance(data["$schema"], str):
            validation.fail(f"{path.relative_to(root)}: $schema must be a string")


def validate_risk_classification_schema(root: Path, validation: Validation) -> None:
    """Validate the stable envelope of Issue #74's versioned risk contract."""
    path = root / RISK_CLASSIFICATION_SCHEMA
    if not path.is_file():
        validation.fail(f"{RISK_CLASSIFICATION_SCHEMA}: missing required versioned risk classification schema")
        return
    data = read_json(path, validation)
    if not isinstance(data, dict):
        return
    for field in RISK_SCHEMA_REQUIRED_FIELDS:
        if field not in data:
            validation.fail(f"{RISK_CLASSIFICATION_SCHEMA}: missing required schema field: {field}")
    if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        validation.fail(f"{RISK_CLASSIFICATION_SCHEMA}: must declare JSON Schema Draft 2020-12")
    if data.get("type") != "object" or data.get("additionalProperties") is not False:
        validation.fail(f"{RISK_CLASSIFICATION_SCHEMA}: top-level record must be a closed object")
    required = data.get("required")
    if not isinstance(required, list) or set(required) != {"schema_version", "inputs", "decision"}:
        validation.fail(f"{RISK_CLASSIFICATION_SCHEMA}: must require schema_version, inputs, and decision")


def schema_errors(value: object, schema: dict[str, object], root: dict[str, object], location: str) -> list[str]:
    """Small Draft 2020-12 subset needed by the checked-in risk schema."""
    if "$ref" in schema:
        target: object = root
        for part in str(schema["$ref"]).removeprefix("#/").split("/"):
            target = target[part]  # type: ignore[index]
        return schema_errors(value, target, root, location)  # type: ignore[arg-type]
    errors: list[str] = []
    if "const" in schema and value != schema["const"]:
        errors.append(f"{location}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:  # type: ignore[operator]
        errors.append(f"{location}: invalid enum value")
    kind = schema.get("type")
    valid_type = {"object": isinstance(value, dict), "array": isinstance(value, list), "string": isinstance(value, str), "boolean": isinstance(value, bool)}
    if kind in valid_type and not valid_type[kind]:
        return [f"{location}: must be a {kind}"]
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for field in required:  # type: ignore[union-attr]
            if field not in value:
                errors.append(f"{location}: missing required field {field}")
        if schema.get("additionalProperties") is False:
            for field in value.keys() - properties.keys():  # type: ignore[union-attr]
                errors.append(f"{location}: unknown field {field}")
        for field, child in properties.items():  # type: ignore[union-attr]
            if field in value:
                errors.extend(schema_errors(value[field], child, root, f"{location}.{field}"))
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{location}: too few items")
        if schema.get("uniqueItems") and len({json.dumps(item, sort_keys=True) for item in value}) != len(value):
            errors.append(f"{location}: duplicate items")
        if isinstance(schema.get("items"), dict):
            for index, item in enumerate(value):
                errors.extend(schema_errors(item, schema["items"], root, f"{location}[{index}]"))  # type: ignore[arg-type]
    if isinstance(value, str) and len(value) < schema.get("minLength", 0):
        errors.append(f"{location}: too short")
    return errors


def validate_risk_classification_fixtures(root: Path, validation: Validation) -> None:
    """Validate checked-in representative records without implementing a classifier."""
    directory = root / "evals" / "risk-classification"
    schema = read_json(root / RISK_CLASSIFICATION_SCHEMA, validation)
    if not isinstance(schema, dict):
        return
    for name in RISK_FIXTURES:
        path = directory / name
        if not path.is_file():
            validation.fail(f"evals/risk-classification: missing required fixture: {name}")
            continue
        data = read_json(path, validation)
        if not isinstance(data, dict):
            continue
        for error in schema_errors(data, schema, schema, "record"):
            validation.fail(f"{path.relative_to(root)}: schema violation: {error}")
        if set(data) != RISK_RECORD_FIELDS:
            validation.fail(f"{path.relative_to(root)}: unknown top-level fields or missing record fields")
            continue
        if data.get("schema_version") != 1:
            validation.fail(f"{path.relative_to(root)}: unsupported schema_version")
        inputs = data.get("inputs")
        decision = data.get("decision")
        if not isinstance(inputs, dict) or set(inputs) != RISK_INPUT_FIELDS:
            validation.fail(f"{path.relative_to(root)}: inputs must contain exactly the version-1 fields")
            continue
        if not isinstance(decision, dict) or set(decision) != RISK_DECISION_FIELDS:
            validation.fail(f"{path.relative_to(root)}: decision must contain exactly the version-1 fields")
            continue
        if any(inputs[field] not in values for field, values in RISK_SCALAR_ENUMS.items()):
            validation.fail(f"{path.relative_to(root)}: invalid input enum value")
        if decision.get("risk_level") not in {"R0", "R1", "R2", "R3", "R4"} or not isinstance(decision.get("rationale"), str) or not decision["rationale"].strip():
            validation.fail(f"{path.relative_to(root)}: decision requires a valid risk_level and non-blank rationale")
        elif decision["risk_level"] != RISK_FIXTURE_LEVELS[name]:
            validation.fail(f"{path.relative_to(root)}: expected representative risk level {RISK_FIXTURE_LEVELS[name]}")
        reasons = decision.get("escalation_reasons")
        human_required = decision.get("human_classification_required")
        if decision.get("confidence") not in {"low", "medium", "high"}:
            validation.fail(f"{path.relative_to(root)}: invalid confidence")
        if not isinstance(reasons, list) or len(reasons) != len(set(reasons)) or any(reason not in RISK_REASONS for reason in reasons) or not isinstance(human_required, bool):
            validation.fail(f"{path.relative_to(root)}: decision requires unique escalation_reasons and human_classification_required")
            continue
        required_reasons = set()
        if inputs["material_unknowns"] or any(inputs[field] == "unknown" for field in RISK_SCALAR_ENUMS) or any("unknown" in inputs[field] for field in ("change_types", "affected_boundaries")):
            required_reasons.add("unknown_material_input")
        if inputs["material_conflicts"]:
            required_reasons.add("conflicting_material_input")
        if inputs["changes_classification_enforcement"]:
            required_reasons.add("classification_enforcement_change")
        if decision["risk_level"] == "R4" or inputs["security_control_direction"] == "weakened" or inputs["action_authorization_required"]:
            required_reasons.add("r4_action_authorization")
        if inputs["action_authorization_required"] and decision["risk_level"] != "R4":
            validation.fail(f"{path.relative_to(root)}: action_authorization_required requires R4")
        for reason in required_reasons:
            if not human_required or reason not in reasons:
                validation.fail(f"{path.relative_to(root)}: {reason} requires human_classification_required")


def validate_openai_marketplace(root: Path, validation: Validation) -> None:
    """Validate the repository-local marketplace that exposes the OpenAI adapter."""
    path = root / "adapters" / "openai" / ".agents" / "plugins" / "marketplace.json"
    if not path.is_file():
        validation.fail("adapters/openai/.agents/plugins/marketplace.json: missing marketplace manifest")
        return
    data = read_json(path, validation)
    if not isinstance(data, dict):
        validation.fail(f"{path.relative_to(root)}: marketplace manifest must be a JSON object")
        return
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        validation.fail(f"{path.relative_to(root)}: marketplace manifest requires non-empty 'name'")
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        validation.fail(f"{path.relative_to(root)}: marketplace manifest requires non-empty 'plugins'")
        return

    marketplace_root = path.parents[2]
    for index, plugin in enumerate(plugins):
        prefix = f"{path.relative_to(root)}: plugins[{index}]"
        if not isinstance(plugin, dict) or not isinstance(plugin.get("name"), str) or not plugin["name"].strip():
            validation.fail(f"{prefix}: requires non-empty 'name'")
            continue
        source = plugin.get("source")
        if not isinstance(source, dict) or source.get("source") != "local" or not isinstance(source.get("path"), str):
            validation.fail(f"{prefix}: requires a local source path")
            continue
        source_path = (marketplace_root / source["path"]).resolve()
        manifest = source_path / ".codex-plugin" / "plugin.json"
        if not manifest.is_file():
            validation.fail(f"{prefix}: marketplace plugin source is missing .codex-plugin/plugin.json")
            continue
        manifest_data = read_json(manifest, validation)
        if isinstance(manifest_data, dict) and manifest_data.get("name") != plugin["name"]:
            validation.fail(f"{prefix}: marketplace plugin name must match source manifest")


def github_anchor(heading: str) -> str:
    text = heading.strip().lower()
    text = re.sub(r"[\[\]`*_]", "", text)
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def anchors(path: Path) -> set[str]:
    result: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = HEADING.match(line)
        if match:
            result.add(github_anchor(match.group(1)))
    return result


def validate_docs(root: Path, validation: Validation) -> None:
    markdown_files = sorted(root.rglob("*.md"))
    for source in markdown_files:
        relative = source.relative_to(root)
        if ".git" in source.parts or relative.parts[:2] == (".superpowers", "sdd"):
            continue
        text = source.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.split(maxsplit=1)[0].strip("<>")
            parsed = urlparse(target)
            if parsed.scheme or parsed.netloc or target.startswith("mailto:"):
                continue
            target_path = source if not parsed.path else (source.parent / unquote(parsed.path)).resolve()
            try:
                target_path.relative_to(root.resolve())
            except ValueError:
                validation.fail(f"{source.relative_to(root)}: link escapes repository: {target}")
                continue
            if not target_path.exists():
                validation.fail(f"{source.relative_to(root)}: broken link: {target}")
                continue
            if parsed.fragment and target_path.is_file() and target_path.suffix.lower() == ".md":
                if unquote(parsed.fragment) not in anchors(target_path):
                    validation.fail(f"{source.relative_to(root)}: broken heading link: {target}")


def validate_command_inventory(root: Path, validation: Validation) -> None:
    path = root / COMMAND_INVENTORY
    if not path.is_file():
        validation.fail(f"{COMMAND_INVENTORY}: missing command inventory")
        return

    commands: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = COMMAND_ROW.match(line)
        if match:
            commands.append(match.group(1))

    workflow = root / CI_WORKFLOW
    try:
        workflow_text = workflow.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        validation.fail(f"{CI_WORKFLOW}: missing or unreadable CI workflow")
        ci_commands: list[str] = []
    else:
        ci_commands = []
        for line in workflow_text.splitlines():
            match = CI_PYTHON_RUN.match(line)
            if match:
                ci_commands.append(match.group(2))

    for command in commands:
        parts = command.split(maxsplit=1)
        target = parts[1] if len(parts) == 2 and parts[0] == "python" else ""
        target_path = (root / target).resolve() if target else root / "__missing_command_target__"
        try:
            target_path.relative_to(root.resolve())
        except ValueError:
            target_path = root / "__missing_command_target__"
        if not target or not target_path.is_file():
            validation.fail(f"command target does not exist: {command}")
            continue
        for instructions in (root / "AGENTS.md", root / "CONTRIBUTING.md"):
            try:
                text = instructions.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                text = ""
            if command not in text:
                validation.fail(
                    f"command inventory command is missing from {instructions.name}: {command}"
                )

    for command in ci_commands:
        if command not in commands:
            validation.fail(
                f"{COMMAND_INVENTORY}: CI Python command is missing from command inventory: {command}"
            )
    for command in commands:
        if command not in ci_commands:
            validation.fail(
                f"{CI_WORKFLOW}: command inventory command is missing from CI workflow: {command}"
            )


def validate_normative_document_metadata(root: Path, validation: Validation) -> None:
    """Require stable ownership and versioned review metadata on policy sources."""
    for source in NORMATIVE_SOURCES:
        relative = Path("docs") / source
        path = root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            validation.fail(f"{relative}: missing normative document")
            continue

        metadata = dict(NORMATIVE_METADATA.findall(text))
        for field in ("Owner", "Version", "Review date"):
            if field not in metadata:
                validation.fail(f"{relative}: missing required metadata: {field}")

        owner = metadata.get("Owner")
        if owner is not None and owner != NORMATIVE_OWNER:
            validation.fail(
                f"{relative}: Owner must be stable repository owner {NORMATIVE_OWNER}"
            )

        version = metadata.get("Version")
        if version is not None and not re.fullmatch(r"[1-9]\d*\.\d+(?:\.\d+)?", version):
            validation.fail(f"{relative}: Version must be numeric (for example, 1.0)")

        review_date = metadata.get("Review date")
        if review_date is not None:
            try:
                parsed_date = datetime.date.fromisoformat(review_date)
            except ValueError:
                parsed_date = None
            if parsed_date is None or parsed_date.isoformat() != review_date:
                validation.fail(
                    f"{relative}: Review date must be an ISO date (YYYY-MM-DD)"
                )


def validate_instruction_precedence(root: Path, validation: Validation) -> None:
    """Validate the repository's scoped instruction authority model."""
    precedence = root / PRECEDENCE_DOCUMENT
    if not precedence.is_file():
        validation.fail(f"{PRECEDENCE_DOCUMENT}: missing")
    else:
        try:
            text = precedence.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            validation.fail(f"{PRECEDENCE_DOCUMENT}: unreadable ({error})")
        else:
            for required in PRECEDENCE_TEXT:
                if required not in text:
                    validation.fail(f"{PRECEDENCE_DOCUMENT}: missing required precedence text: {required}")

    for instructions in ("AGENTS.md", "CLAUDE.md"):
        path = root / instructions
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            validation.fail(f"{instructions}: missing normative-source references")
            continue
        for source in NORMATIVE_SOURCES:
            if f"docs/{source}" not in text:
                validation.fail(f"{instructions}: missing normative-source reference: docs/{source}")

    architecture_plan = root / "docs" / "CROSS_PLATFORM_REPO_PLAN.md"
    if architecture_plan.is_file():
        text = architecture_plan.read_text(encoding="utf-8")
        if ARCHITECTURE_PLAN_AUTHORITY_CLAIM.search(text):
            validation.fail("docs/CROSS_PLATFORM_REPO_PLAN.md: architecture plan must not claim to be canonical")


def validate_openai_skills_link(root: Path, validation: Validation) -> None:
    path = root / "adapters" / "openai" / "skills"
    if not path.is_symlink():
        validation.fail("adapters/openai/skills: must be a symbolic link to canonical skills/")
        return
    if path.resolve() != (root / "skills").resolve():
        validation.fail("adapters/openai/skills: must resolve to canonical skills/")


def run_python(root: Path, script: Path, validation: Validation) -> None:
    result = subprocess.run([sys.executable, str(script)], cwd=root, text=True, capture_output=True)
    if result.returncode:
        output = (result.stdout + result.stderr).strip()
        validation.fail(f"{script.relative_to(root)} failed ({result.returncode}): {output}")


def run_package_checks(root: Path, validation: Validation) -> None:
    script = root / "adapters/claude/scripts/test_packaging.py"
    if script.is_file():
        run_python(root, script, validation)


def run_claude_package_integrity_check(root: Path, validation: Validation) -> None:
    """Run the package check that calls validate_package on a fresh artifact."""
    script = root / "adapters/claude/scripts/check_shared_content.py"
    if script.is_file():
        run_python(root, script, validation)


def run_evals(root: Path, validation: Validation) -> None:
    """Run Issue #14's stable harness and its compliant representative fixture."""
    script = root / "evals" / "run.py"
    if not script.is_file():
        return
    results = root / "evals" / "examples" / "compliant.json"
    tests = root / "evals" / "test_run.py"
    if not results.is_file():
        validation.fail("evals/run.py exists but evals/examples/compliant.json is missing")
        return
    if not tests.is_file():
        validation.fail("evals/run.py exists but evals/test_run.py is missing")
        return
    result = subprocess.run(
        [sys.executable, "-m", "unittest", str(tests.relative_to(root))],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        validation.fail(f"evals/test_run.py failed ({result.returncode}): {(result.stdout + result.stderr).strip()}")
    result = subprocess.run(
        [sys.executable, str(script), "--results", str(results), "--json"],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        validation.fail(f"evals/run.py failed ({result.returncode}): {(result.stdout + result.stderr).strip()}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skip-evals", action="store_true", help="do not run evals/run_evals.py")
    args = parser.parse_args()
    root = args.root.resolve()
    validation = Validation(errors=[])
    validate_skills(root, validation)
    validate_json_artifacts(root, validation)
    validate_risk_classification_schema(root, validation)
    validate_risk_classification_fixtures(root, validation)
    validate_openai_marketplace(root, validation)
    validate_openai_skills_link(root, validation)
    validate_docs(root, validation)
    validate_command_inventory(root, validation)
    validate_instruction_precedence(root, validation)
    validate_normative_document_metadata(root, validation)
    run_package_checks(root, validation)
    run_claude_package_integrity_check(root, validation)
    if not args.skip_evals:
        run_evals(root, validation)
    if validation.errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in validation.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
