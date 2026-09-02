# V2 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the repository’s executable command inventory and instruction-precedence model authoritative, validated, and discoverable for all supported hosts.

**Architecture:** Add two compact, repository-owned Markdown registries: one for commands and one for instruction precedence. Extend the dependency-free Python validator to validate the registries, their consumers, and their representative failure fixtures; use the existing CI workflow as the executable source for command truth. Keep canonical lifecycle, authority, and capability content in their existing documents and keep `AGENTS.md`/`CLAUDE.md` thin.

**Tech Stack:** Portable Markdown; Python 3.11 standard library; `unittest`; GitHub Actions.

**Spec:** `docs/V2_ARCHITECTURE_AND_WORKSTREAM_PLAN.md` (§§ Layer 1; P0-01; P0-02), GitHub Issues #43 and #44.

## Global Constraints

- Work only in the `issue/43-44-foundation` isolated worktree and do not alter the user-owned `.worktrees/` directory in the primary checkout.
- `docs/methodology.md`, `docs/security-and-autonomy-boundaries.md`, and `docs/capability-contract.md` are respectively the lifecycle, authority, and capability normative sources.
- `docs/CROSS_PLATFORM_REPO_PLAN.md` is architecture history and roadmap, not a competing normative policy source.
- System/host policy and explicit user instructions outrank repository instructions; repository instructions outrank nested instructions, durable memory, and unvalidated task context.
- Core Skills remain host-neutral; host-specific invocation/import details remain in adapters and host guides.
- Use Python standard library only; do not add packages, CI permissions, hooks, MCP services, or host-specific orchestration.
- The authoritative repository validation commands are `python scripts/test_validate_repository.py` and `python scripts/validate_repository.py`; documentation-only work runs both and records their observed results.
- Tests for validator behavior follow RED → GREEN → REFACTOR. A test must fail for the intended missing behavior before its implementation is added.
- Do not merge, enable auto-merge, publish artifacts, modify repository protections, or weaken authority controls.

---

### Task 1: Command inventory and drift validation (P0-01)

**Files:**
- Create: `docs/command-inventory.md`
- Modify: `AGENTS.md`
- Modify: `CONTRIBUTING.md`
- Modify: `scripts/validate_repository.py`
- Modify: `scripts/test_validate_repository.py`

**Interfaces:**
- Consumes: `.github/workflows/validate.yml` command steps and the current validator entry points.
- Produces: `docs/command-inventory.md`, with one `## Authoritative commands` table containing the exact shell command, applicability, prerequisite, and expected evidence for each repository-owned command; `validate_command_inventory(root, validation) -> None` rejects a missing inventory, a missing executable script target, or a missing inventory command from either `AGENTS.md` or `CONTRIBUTING.md`.

- [ ] **Step 1: Write failing validator tests**

Add a minimal inventory fixture to `create_repository`, then add tests equivalent to:

```python
def test_rejects_command_inventory_that_names_a_missing_script(self) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        create_repository(root)
        (root / "docs").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "command-inventory.md").write_text(
            "## Authoritative commands\n\n| Command | Applicability | Evidence |\n| --- | --- | --- |\n| `python scripts/missing.py` | All changes | exit 0 |\n",
            encoding="utf-8",
        )
        result = validate(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("command target does not exist", result.stderr)
```

and a second test that supplies a real `scripts/check.py` but omits its command from `AGENTS.md`, then asserts `command inventory command is missing from AGENTS.md`.

- [ ] **Step 2: Run the focused tests to verify RED**

Run: `python -m unittest scripts.test_validate_repository.ValidatorTests.test_rejects_command_inventory_that_names_a_missing_script scripts.test_validate_repository.ValidatorTests.test_rejects_command_inventory_command_missing_from_agent_instructions`

Expected: FAIL because `validate_command_inventory` has not been implemented.

- [ ] **Step 3: Implement the smallest inventory parser and checks**

Add `COMMAND_INVENTORY = Path("docs/command-inventory.md")` and a standard-library parser that reads Markdown table rows beginning with `| \``. For each first-column command, require a `python <relative-script-path>` target that exists below `root`; require the exact command string to occur in both `AGENTS.md` and `CONTRIBUTING.md`; call the new check from `main()` before package checks. The checker must produce the exact diagnostic prefixes asserted by the tests.

Create `docs/command-inventory.md` with exactly these rows:

```markdown
| Command | Applicability | Prerequisite | Expected evidence |
| --- | --- | --- | --- |
| `python scripts/test_validate_repository.py` | All repository changes | Python 3.11+ | `unittest` exits 0. |
| `python scripts/validate_repository.py` | All repository changes | Python 3.11+ | `Repository validation passed.` |
```

Update `AGENTS.md` and `CONTRIBUTING.md` to show these exact commands, identify documentation-only applicability, and link to the inventory without copying lifecycle policy.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run: `python -m unittest scripts.test_validate_repository.ValidatorTests.test_rejects_command_inventory_that_names_a_missing_script scripts.test_validate_repository.ValidatorTests.test_rejects_command_inventory_command_missing_from_agent_instructions`

Expected: PASS.

- [ ] **Step 5: Refactor and run the complete repository checks**

Keep parsing in a focused helper and retain existing test behavior. Run:

```sh
python scripts/test_validate_repository.py
python scripts/validate_repository.py
git diff --check
```

Expected: every command exits 0.

- [ ] **Step 6: Commit the task**

```sh
git add AGENTS.md CONTRIBUTING.md docs/command-inventory.md scripts/validate_repository.py scripts/test_validate_repository.py
git commit -m "fix: document and validate repository commands"
```

### Task 2: Normative precedence model and contradiction checks (P0-02)

**Files:**
- Create: `docs/instruction-precedence.md`
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`
- Modify: `CONTRIBUTING.md`
- Modify: `docs/CROSS_PLATFORM_REPO_PLAN.md`
- Modify: `docs/methodology.md`
- Modify: `docs/security-and-autonomy-boundaries.md`
- Modify: `docs/capability-contract.md`
- Modify: `scripts/validate_repository.py`
- Modify: `scripts/test_validate_repository.py`

**Interfaces:**
- Consumes: the three normative source documents and current host instruction files.
- Produces: `docs/instruction-precedence.md`, whose `## Normative sources` and `## Conflict resolution` headings declare the three scoped sources and ranked instruction handling; `validate_instruction_precedence(root, validation) -> None` rejects a missing precedence document, missing canonical-source references in `AGENTS.md`/`CLAUDE.md`, or a cross-platform plan that calls itself canonical.

- [ ] **Step 1: Write failing precedence tests**

Extend `create_repository` to create the three canonical docs, `AGENTS.md`, `CLAUDE.md`, and `docs/CROSS_PLATFORM_REPO_PLAN.md`. Add tests equivalent to:

```python
def test_rejects_missing_precedence_document(self) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        create_repository(root)
        result = validate(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("docs/instruction-precedence.md: missing", result.stderr)
```

and a fixture with a valid precedence document but `CROSS_PLATFORM_REPO_PLAN.md` containing `This is the canonical methodology.`, asserting `architecture plan must not claim to be canonical`.

- [ ] **Step 2: Run the focused tests to verify RED**

Run: `python -m unittest scripts.test_validate_repository.ValidatorTests.test_rejects_missing_precedence_document scripts.test_validate_repository.ValidatorTests.test_rejects_architecture_plan_canonical_claim`

Expected: FAIL because `validate_instruction_precedence` has not been implemented.

- [ ] **Step 3: Implement the precedence document and deterministic checks**

Create `docs/instruction-precedence.md` that:

```markdown
## Normative sources

- `methodology.md` controls lifecycle.
- `security-and-autonomy-boundaries.md` controls authority and approval boundaries.
- `capability-contract.md` controls portable semantic capabilities.

## Conflict resolution

1. Applicable system, host, and law/policy controls prevail.
2. Explicit scoped human instructions prevail when they do not conflict with higher controls.
3. Repository instructions and the three normative sources prevail over nested instructions, memory, and unvalidated task context.
4. Current repository state and revision-bound Issue/PR/CI evidence prevail over stale memory and agent observations.
```

Update the cited documents so their role and links agree, mark `CROSS_PLATFORM_REPO_PLAN.md` as historical/roadmap material, and keep `AGENTS.md` and `CLAUDE.md` as thin entry points. Add validator checks for the required precedence headings/text and source links, and for prohibited canonical claims in the cross-platform plan. Do not require package self-containment; that is #45.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run: `python -m unittest scripts.test_validate_repository.ValidatorTests.test_rejects_missing_precedence_document scripts.test_validate_repository.ValidatorTests.test_rejects_architecture_plan_canonical_claim`

Expected: PASS.

- [ ] **Step 5: Run the complete final verification**

Run:

```sh
python scripts/test_validate_repository.py
python scripts/validate_repository.py
git diff --check
rg --files -g '*.md'
```

Manually verify every changed relative Markdown link and heading target; ensure both adapter paths still receive the normative-source links.

- [ ] **Step 6: Commit the task**

```sh
git add AGENTS.md CLAUDE.md CONTRIBUTING.md docs/instruction-precedence.md docs/CROSS_PLATFORM_REPO_PLAN.md docs/methodology.md docs/security-and-autonomy-boundaries.md docs/capability-contract.md scripts/validate_repository.py scripts/test_validate_repository.py
git commit -m "docs: establish normative instruction precedence"
```
