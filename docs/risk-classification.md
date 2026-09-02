# Risk classification record

- **Owner:** `@boggotron`
- **Version:** `1.0`
- **Review date:** `2026-09-02`

`schemas/risk-classification.schema.json` defines version 1 of the portable
record used to explain a change-risk decision. It records facts and a decision;
it does not implement a classifier, select a repository profile, resolve
controls, or authorize an action.

## Risk levels

| Level | Meaning |
| --- | --- |
| R0 | Typographical documentation correction. |
| R1 | Internal refactor with strong tests. |
| R2 | User-visible feature or dependency change. |
| R3 | Authentication, authorization, sensitive data, migration, CI, or infrastructure change. |
| R4 | Production or destructive effect, security-control weakening, or secret authority. |

## Required inputs and decision

Every record supplies change type, affected boundary, data and secret exposure,
external effects, privilege, reversibility, blast radius, compatibility,
verification strength, material unknowns, material conflicts, and whether the
change alters classification or enforcement. Security-control changes also state
whether the control is strengthened, unchanged, weakened, or unknown. The decision supplies one R0-R4
level, a non-empty rationale, evidence confidence, the human-classification
flag, and applicable escalation reasons.

Set `action_authorization_required` only when the record would request
authorization to perform an action. That input is valid only for an R4 decision
and requires both `human_classification_required: true` and
`r4_action_authorization`; that reason is prohibited when the flag is false.
An R4 classification remains a human-classification matter even when no action
authorization is requested.

`schema_version` is the integer `1`. Consumers must reject another version and
unknown top-level fields rather than silently interpret a changed contract.

## Conservative classification

Classify from all applicable inputs. Select the highest applicable risk level;
when signals tie, conflict, or otherwise support different levels, retain the
stricter result. `confidence` communicates the quality of evidence only. It
MUST NOT lower a selected level or waive an escalation.

Do not infer a lower risk from an omitted material fact. A record requires
human classification when material inputs are unknown, material inputs conflict,
the proposed change alters risk-profile/classifier/enforcement policy, or an R4
action would be authorized. Unknown is representable for every material input
category and has the same conservative escalation effect as an explicit material
unknown. A weakened security control is R4. Record every applicable reason (not
only the first) in
`decision.escalation_reasons`. A human classification is a decision record; it
does not itself authorize an action. The applicable authority policy continues
to determine whether authorization is mandatory before the action.

## Boundaries

This contract is deliberately independent of repository profiles, controls,
budgets, and structured evidence/transition schemas. Those subjects are owned
by later P0-07 and P0-10 work. Classifier integration may consume this record
but must not alter version-1 semantics without a versioned schema change and
human review.
