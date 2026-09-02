# Risk Classification Schema Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an additive, versioned R0-R4 classification contract with conservative escalation semantics and representative conformance fixtures.

**Architecture:** A JSON Schema defines the stable data boundary, while a companion normative Markdown document explains classifications and conservative decisions that JSON Schema cannot evaluate. Dependency-free validation asserts the contract and fixture shape, leaving classification execution, repository profiles, controls, budgets, and P0-10 evidence schemas to their own issues.

**Tech Stack:** JSON Schema Draft 2020-12, JSON fixtures, portable Markdown, Python 3 standard library `unittest`.

**Spec:** `docs/superpowers/specs/2026-09-02-risk-classification-schema-design.md`

## Global Constraints

- Create only the R0-R4 risk-schema contract, conservative classifier-input/escalation rules, human-classification cases, fixtures, and their dependency-free validation.
- `schema_version` is exactly integer `1`; valid risk levels are exactly `R0`, `R1`, `R2`, `R3`, and `R4`.
- Inputs must cover change type, affected boundary, data/secrets, external effects, privilege, reversibility, blast radius, compatibility, verification strength, and material unknown/conflicting inputs.
- A declared decision must include a non-empty rationale; confidence cannot lower risk; tied or conflicting applicable signals select the stricter risk.
- Material unknown/conflicting inputs, risk-profile/classifier/enforcement changes, and R4 action authorization require a human classification record; existing authority rules independently govern authorization.
- Reject unsupported schema versions and unknown top-level fields.
- Do not add repository profiles (#75/#76), a classifier implementation/integration (#77), P0-10 schemas, security controls, budgets, host-specific policy, or a merge/push.

---

## File structure

- `schemas/risk-classification.schema.json` — version-1 machine-readable classification record contract.
- `docs/risk-classification.md` — normative risk levels, conservative escalation, and human-classification semantics.
- `evals/risk-classification/*.json` — valid representative records covering normal, boundary, and human-escalation decisions.
- `scripts/validate_repository.py` — dependency-free structural and fixture validation only, not classification execution.
- `scripts/test_validate_repository.py` — focused regression coverage for the new validator checks.

### Task 1: Define the versioned risk record contract

**Files:**
- Create: `schemas/risk-classification.schema.json`
- Create: `docs/risk-classification.md`
- Modify: `scripts/validate_repository.py`
- Modify: `scripts/test_validate_repository.py`

**Interfaces:**
- Consumes: V2 risk levels and classifier factors from `docs/V2_ARCHITECTURE_AND_WORKSTREAM_PLAN.md`; authority boundary from `docs/security-and-autonomy-boundaries.md`.
- Produces: Draft 2020-12 schema with `schema_version`, `inputs`, and `decision`; normative decision rules that later profile and classifier issues can consume.

- [ ] **Step 1: Write the failing schema acceptance test**

Add a focused validator regression test that creates the required schema path with invalid top-level shape and expects a precise rejection. Keep the test dependency-free.

- [ ] **Step 2: Run the focused test to verify RED**

Run `python scripts/test_validate_repository.py` and record the relevant failing assertion before implementation.

- [ ] **Step 3: Create the schema, companion document, and artifact check**

Define closed top-level and nested object shapes, the exact version and risk enum, all required input categories, decision rationale and escalation fields, and portable documentation for R0-R4, stricter tie-breaking, unknown/conflicting signals, confidence, and human classification.
Extend the dependency-free repository validator only far enough to reject an absent
or structurally incomplete versioned schema artifact; fixture-record validation belongs
to Task 2.

- [ ] **Step 4: Run the focused test to verify GREEN**

Run `python scripts/test_validate_repository.py` and record that the new schema-artifact check passes.

- [ ] **Step 5: Self-review and commit**

Review for schema/document disagreement, accidental profile/resolver behavior, and non-portable host wording. Commit only this task.

### Task 2: Add representative fixtures and conformance validation

**Files:**
- Create: `evals/risk-classification/r0-documentation.json`
- Create: `evals/risk-classification/r1-refactor.json`
- Create: `evals/risk-classification/r2-feature.json`
- Create: `evals/risk-classification/r3-sensitive-data.json`
- Create: `evals/risk-classification/r4-destructive-effect.json`
- Create: `evals/risk-classification/boundary-stricter-signal.json`
- Create: `evals/risk-classification/human-unknown-input.json`
- Create: `evals/risk-classification/human-conflicting-input.json`
- Create: `evals/risk-classification/human-policy-change.json`
- Create: `evals/risk-classification/human-r4-authorization.json`
- Modify: `scripts/validate_repository.py`
- Modify: `scripts/test_validate_repository.py`

**Interfaces:**
- Consumes: `schemas/risk-classification.schema.json` produced by Task 1.
- Produces: checked-in valid fixture corpus and structural checks that reject missing required fixture coverage, malformed records, unsupported versions, unknown top-level fields, or contradictory human-escalation flags.

- [ ] **Step 1: Write failing fixture-validation tests**

Add tests for a conforming fixture corpus plus invalid unsupported-version, unknown-top-level-field, and missing-human-classification fixture mutations.

- [ ] **Step 2: Run the focused tests to verify RED**

Run `python scripts/test_validate_repository.py` and record the expected failures before adding fixture validation.

- [ ] **Step 3: Add fixtures and minimal structural validation**

Create the ten named valid fixtures. Extend the repository validator with a focused dependency-free validator for this contract and fixture corpus; do not interpret prose, calculate risk, resolve profiles, or add dependencies.

- [ ] **Step 4: Run tests to verify GREEN and broader behavior**

Run `python scripts/test_validate_repository.py`, then `python scripts/validate_repository.py`, and record observed results.

- [ ] **Step 5: Self-review and commit**

Review fixture names, decision explanations, R0-R4 coverage, stricter-signal boundary coverage, and all four human-classification cases. Commit only this task.

## Final verification

- [ ] Run `git diff --check`.
- [ ] Run `python scripts/test_validate_repository.py`.
- [ ] Run `python scripts/validate_repository.py`.
- [ ] Manually validate changed relative Markdown links and headings.
- [ ] Record exact results and unavailable checks in Issue #74; CI is N/A locally until a PR exists.
