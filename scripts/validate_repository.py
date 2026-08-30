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
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0] != "---":
            validation.fail(f"{path.relative_to(root)}: missing YAML front matter")
            continue
        try:
            end = lines.index("---", 1)
        except ValueError:
            validation.fail(f"{path.relative_to(root)}: unterminated YAML front matter")
            continue
        fields: dict[str, str] = {}
        for line in lines[1:end]:
            key, separator, value = line.partition(":")
            if separator and key in {"name", "description"}:
                fields[key] = value.strip().strip('"').strip("'")
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
    """Run the optional harness once Issue #14 supplies its stable entry point."""
    script = root / "evals" / "run_evals.py"
    if script.is_file():
        run_python(root, script, validation)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skip-evals", action="store_true", help="do not run evals/run_evals.py")
    args = parser.parse_args()
    root = args.root.resolve()
    validation = Validation(errors=[])
    validate_skills(root, validation)
    validate_json_artifacts(root, validation)
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
