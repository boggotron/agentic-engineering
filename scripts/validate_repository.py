#!/usr/bin/env python3
"""Validate the repository's portable Skills, adapters, documentation, and eval hook.

This validator uses only the Python standard library so it can run in a clean
GitHub Actions checkout.  It is deliberately a repository validator rather
than a replacement for host-native plugin validators or an evaluation harness.
"""

from __future__ import annotations

import argparse
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
        if ".git" in source.parts:
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
    for relative in (
        Path("adapters/claude/scripts/test_packaging.py"),
        Path("adapters/claude/scripts/check_shared_content.py"),
    ):
        script = root / relative
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
    validate_openai_marketplace(root, validation)
    validate_openai_skills_link(root, validation)
    validate_docs(root, validation)
    run_package_checks(root, validation)
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
