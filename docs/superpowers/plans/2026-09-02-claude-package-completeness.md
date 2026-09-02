# Claude Package Completeness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Produce a deterministic, self-contained Claude plugin that includes every local normative dependency needed by packaged Skills.

**Architecture:** The packager will discover local Markdown links transitively from the shared Skills, copy those source files beneath a deterministic `docs/` package directory, and rewrite only links in copied package content to point inside that artifact. A standard-library verifier will reject missing or escaping links, unexpected package paths, and digest divergence while preserving byte-identical packaged Skill files.

**Tech Stack:** Python 3.11 standard library; `unittest`; Markdown links; Claude Code local-plugin CLI.

**Spec:** `docs/V2_ARCHITECTURE_AND_WORKSTREAM_PLAN.md` (P0-03) and GitHub Issue #45.

## Global Constraints

- Preserve the canonical `skills/` sources; never add Claude-only methodology or edit Skill content to package it.
- Package-time link rewriting is permitted only in copied reference material and must not permit a link to escape the artifact.
- Package `.claude-plugin/`, `skills/`, and required transitive local references at deterministic paths; reject unexpected files.
- Use only Python standard library and existing repository commands.
- Tests use RED → GREEN → REFACTOR for packager behavior; clean-install CLI verification is required when `claude` is installed, otherwise record N/A.
- Do not publish a plugin, merge a PR, change CI permissions, or implement P0-04.

---

### Task 1: Transitive dependency graph and deterministic package contents

**Files:**
- Modify: `adapters/claude/scripts/package_plugin.py`
- Modify: `adapters/claude/scripts/test_packaging.py`
- Modify: `adapters/claude/scripts/check_shared_content.py`

**Interfaces:**
- Produces: `local_markdown_dependencies(source: Path, repository_root: Path) -> set[Path]` and `package(output: Path) -> None`; copied references live at `docs/<repository-relative-path-under-docs>` and packaged Skills stay byte-identical.

- [ ] Write tests that package the real adapter and assert the artifact contains `docs/methodology.md`, `docs/capability-contract.md`, `docs/security-and-autonomy-boundaries.md`, and `docs/instruction-precedence.md`, while every packaged local Markdown link resolves within the artifact.
- [ ] Run `python -m unittest adapters/claude/scripts/test_packaging.py` and observe failure because the current package contains only `.claude-plugin/` and `skills/`.
- [ ] Implement recursive local-link discovery from every packaged `SKILL.md`, copy required repository files into `output/docs/`, and rewrite copied relative links so their targets remain within `output`; do not modify source Skills.
- [ ] Re-run the focused tests, then `python adapters/claude/scripts/test_packaging.py` and `python adapters/claude/scripts/check_shared_content.py`.
- [ ] Commit: `git add adapters/claude/scripts && git commit -m "feat: package Claude skill dependencies"`.

### Task 2: Artifact integrity validation and clean-install evidence

**Files:**
- Modify: `adapters/claude/scripts/test_packaging.py`
- Modify: `adapters/claude/scripts/check_shared_content.py`
- Modify: `adapters/claude/README.md`
- Modify: `scripts/validate_repository.py`

**Interfaces:**
- Produces: `validate_package(output: Path) -> list[str]`, used by packaging tests and repository validation; it detects missing dependency, link escape/breakage, unexpected file, and digest divergence.

- [ ] Write focused tests that delete a packaged reference, add an unexpected artifact file, and alter a packaged Skill; each must produce a distinct validation failure.
- [ ] Run the focused tests and observe failure before `validate_package` exists.
- [ ] Implement the validator using hashes from `hashlib.sha256`, exact expected-path comparison, and packaged local-link traversal. Document deterministic layout, authoring mode, package validation, and clean-install commands in the adapter README.
- [ ] Run all: `python adapters/claude/scripts/test_packaging.py`; `python adapters/claude/scripts/check_shared_content.py`; `python scripts/test_validate_repository.py`; `python scripts/validate_repository.py`; create a temporary package and run `claude plugin validate <output>` and `claude --plugin-dir <output>` only if they can be non-interactively verified; otherwise record an N/A rationale.
- [ ] Commit: `git add adapters/claude/README.md adapters/claude/scripts scripts/validate_repository.py && git commit -m "test: validate Claude package integrity"`.
