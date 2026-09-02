# Evidence Schema Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the versioned, revision-bound envelope and compatibility contract that every P0-10 evidence family will use.

**Architecture:** A Draft 2020-12 JSON Schema defines the deliberately small common envelope, while a dependency-free Python validator enforces the cross-document semantics that JSON Schema cannot express: supported-version selection, canonical SHA-256 artifact digests, and local reference integrity. Family-specific payload schemas remain outside this issue and compose beneath `payload` in later work.

**Tech Stack:** JSON Schema Draft 2020-12, JSON fixtures, Python 3 standard library, `unittest`.

**Spec:** `docs/schema-architecture.md` (created by Task 1; its durable requirements derive from Issue #87 and `docs/V2_ARCHITECTURE_AND_WORKSTREAM_PLAN.md#p0-10--define-structured-evidence-and-transition-schemas`).

## Global Constraints

- Keep the envelope host-neutral and prohibit secrets, hidden reasoning, and full private prompts in durable evidence.
- Use JSON Schema Draft 2020-12 for declarative shape validation; add no third-party dependency.
- Bind each envelope to an immutable Git revision and identify artifacts with a SHA-256 digest of their UTF-8 JSON bytes.
- Reject unknown top-level fields; permit forward-compatible extension data only under explicit reverse-DNS namespaces in `extensions`.
- Treat a change to required fields, field meaning, validation semantics, or reference semantics as a major incompatible schema change.
- Preserve original evidence during migration; create a new envelope with a `derived-from` reference instead of mutating history.
- Do not add evidence-family payload contracts, risk controls, CI policy, budgets, or security policy.

---

## File structure

- `docs/schema-architecture.md` explains the canonical envelope boundary, version/compatibility/migration rules, digest/reference semantics, and downstream composition contract.
- `schemas/evidence-envelope.schema.json` is the JSON Schema Draft 2020-12 shape for one common evidence envelope.
- `schemas/evidence-compatibility.json` is the machine-readable registry of the supported envelope schema version and its compatibility policy.
- `schemas/fixtures/evidence-envelope/*.json` supplies valid, extension, malformed, incompatible-version, and stale-reference evidence bundles.
- `scripts/validate_evidence_schema.py` validates the envelope schema/registry and every fixture bundle using only the standard library.
- `scripts/test_validate_evidence_schema.py` regression-tests the semantic validator and fixture outcomes.

### Task 1: Envelope contract, architecture, and conformance fixtures

**Files:**
- Create: `docs/schema-architecture.md`
- Create: `schemas/evidence-envelope.schema.json`
- Create: `schemas/evidence-compatibility.json`
- Create: `schemas/fixtures/evidence-envelope/valid.json`
- Create: `schemas/fixtures/evidence-envelope/extension.json`
- Create: `schemas/fixtures/evidence-envelope/malformed.json`
- Create: `schemas/fixtures/evidence-envelope/incompatible-version.json`
- Create: `schemas/fixtures/evidence-envelope/stale-reference.json`

**Interfaces:**
- Consumes: Issue #87’s shared evidence requirements and the P0-10 Layer 6 evidence list.
- Produces: an envelope requiring `schema`, `schema_version`, `evidence_type`, `id`, `repository`, `revision`, `policy`, `produced_at`, `actor`, and `payload`; optional `provenance`, `references`, and `extensions`.
- Produces: fixture documents with `expectation` (`valid` or `invalid`) for the dependency-free validator.

- [ ] **Step 1: Define the desired fixture assertions before writing the schema**

Document these executable expectations in `docs/schema-architecture.md`: `valid.json` validates; `extension.json` validates; `malformed.json` fails because a required immutable revision is malformed; `incompatible-version.json` fails because `2.0.0` has no compatible registry entry; `stale-reference.json` fails because a reference digest differs from the referenced artifact bytes.

- [ ] **Step 2: Record the red fixture matrix**

Create the five JSON fixtures with their target envelope values and expected outcome. Use repository `https://github.com/boggotron/agentic-engineering`, 64-character hexadecimal Git revisions, UTC RFC 3339 timestamps, `sha256:<64-lowercase-hex>` digests, and reverse-DNS extension keys such as `org.example.rendering`.

- [ ] **Step 3: Write the minimal declarative contract**

Create the Draft 2020-12 schema with `additionalProperties: false`, definitions for SemVer, SHA-256 digest, immutable Git revision, actor, policy, provenance, reference, and extensions. Keep `payload` as a JSON object with unrestricted family-owned properties. Create the registry declaring `evidence-envelope` version `1.0.0`, supported major `1`, and the compatibility/migration policy identifiers documented in the architecture.

- [ ] **Step 4: Verify JSON syntax and repository document links**

Run: `python -m json.tool schemas/evidence-envelope.schema.json >/dev/null && python -m json.tool schemas/evidence-compatibility.json >/dev/null && find schemas/fixtures/evidence-envelope -name '*.json' -exec python -m json.tool {} \; >/dev/null`

Expected: exit 0.

- [ ] **Step 5: Commit contract artifacts**

Run:

```bash
git add docs/schema-architecture.md schemas
git commit -m "feat: define evidence envelope schema"
```

### Task 2: Dependency-free semantic validation and regression coverage

**Files:**
- Create: `scripts/validate_evidence_schema.py`
- Create: `scripts/test_validate_evidence_schema.py`

**Interfaces:**
- Consumes: `schemas/evidence-envelope.schema.json`, `schemas/evidence-compatibility.json`, and a directory of fixture JSON files.
- Produces: `validate(root: Path, fixtures: Path) -> list[str]`; process exit `0` only when each fixture outcome matches its declared `expectation` and schema/registry invariants hold.

- [ ] **Step 1: Write failing regression tests**

Create `scripts/test_validate_evidence_schema.py` that copies the canonical schemas and fixture files to a temporary directory, then asserts that the validator exits zero for the unmodified corpus and nonzero after: removing a required envelope field, adding an undeclared top-level field, changing the registry supported major away from `1`, and changing a referenced artifact without updating its digest.

- [ ] **Step 2: Run the regression test to verify RED**

Run: `python scripts/test_validate_evidence_schema.py`

Expected: FAIL because `validate_evidence_schema.py` does not exist.

- [ ] **Step 3: Implement the minimal validator**

Create a standard-library validator that checks JSON parsing, schema `$schema`/`$id`/version constants, registry shape and supported-major consistency, the envelope’s required keys and primitive formats, prohibited unknown top-level keys, extension namespaces, and `derived-from`/artifact reference integrity. For a local reference, read the referenced JSON bytes exactly and compare `sha256:` plus SHA-256 digest; absent reference targets are stale references. Check each fixture result against `expectation`.

- [ ] **Step 4: Run the focused suite to verify GREEN**

Run: `python scripts/test_validate_evidence_schema.py && python scripts/validate_evidence_schema.py`

Expected: exit 0; the fixture corpus contains both accepted and intentionally rejected documents, with their expected results observed.

- [ ] **Step 5: Run repository validation and commit**

Run:

```bash
python scripts/test_validate_repository.py
python scripts/validate_repository.py
git add scripts
git commit -m "test: validate evidence schema fixtures"
```

Expected: all commands exit 0.
