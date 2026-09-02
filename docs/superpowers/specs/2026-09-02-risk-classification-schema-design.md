# Risk Classification Schema Design

> **Issue:** #74 — [P0-07.1] Define R0-R4 risk schema and conservative classifier inputs
> **Status:** Approved for implementation by the P0 architecture-spine owner on 2026-09-02.

## Goal

Provide a small, versioned, machine-readable contract that records the facts used to
classify a proposed change as R0 through R4, makes escalation explainable, and refuses
to let uncertainty or confidence silently lower the selected risk.

## Scope

This change creates a JSON Schema contract, a companion normative document, and
representative JSON fixtures. It also adds dependency-free repository validation for
the contract's required artifacts and fixture conformance.

The schema has three top-level areas:

- `schema_version`, fixed at `1` for this initial contract;
- `inputs`, containing the required classification facts: change types, affected
  boundaries, data and secret exposure, external effects, privilege changes,
  reversibility, blast radius, compatibility impact, verification strength, and
  unknown or conflicting material inputs; and
- `decision`, containing an R0-R4 `risk_level`, a non-empty rationale, and an
  escalation record when a higher level was selected.

Risk levels retain the V2-plan meanings: R0 is a typographical documentation
correction; R1 is an internal refactor with strong tests; R2 is a user-visible feature
or dependency change; R3 includes authentication, authorization, sensitive data,
migration, CI, or infrastructure; and R4 includes production/destructive effects,
security-control weakening, or secret authority.

## Conservative decision rules

The schema records facts and a declared result; it is not an executable classifier or
a control/profile resolver. Its normative companion requires a classifier to select
the highest applicable level, use the stricter result for tied or conflicting signals,
and escalate rather than infer a lower level from missing material information.
`confidence` may describe evidence quality but is deliberately not a risk-reducing
input. A decision must be marked for human classification when material inputs are
unknown or conflict, when a change alters risk-profile/classifier/enforcement policy,
or when the decision would authorize an R4 action. Existing authority rules still
govern whether a human authorization is required before an action.

## Compatibility and ownership

The artifact is additive. Consumers MUST reject unsupported `schema_version` values
and unknown top-level fields; this protects later profile (#75/#76) and classifier
integration (#77) work from accidental contract drift. Repository profiles, required
checks, budgets, security controls, structured evidence/transition schemas (P0-10),
and executable classifier integration are explicitly not defined here.

## Verification

Fixtures cover one representative positive decision per risk level, a boundary case
where competing signals select the stricter level, and adversarial human-classification
cases for unknown facts, conflicting facts, policy/enforcement changes, and R4 action
authorization. Repository validation verifies that the required contract and fixtures
exist, parse, and conform to the schema shape; regression tests cover valid and invalid
fixture cases. The existing repository test and validation commands provide final
evidence.
