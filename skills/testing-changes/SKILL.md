---
name: testing-changes
description: Test engineering changes with evidence, using TDD by default for deterministic behavior and documented exceptions where it is not productive.
---

# Testing changes

Use this Skill while implementing or correcting an engineering change to select
and record proportionate test evidence. It preserves a deterministic TDD default
without forcing it where it cannot provide useful feedback. It does not invent
test commands, test frameworks, or host-specific mechanics.

## Choose the testing approach

Derive the required checks from the issue, plan, acceptance criteria, and
affected boundary. Use the project's available deterministic test facilities
when they cover the behavior. If no automated check applies, define the strongest
repeatable manual or integration verification available and record its observed
result.

Strict test-driven development is the default for deterministic business logic,
bug fixes, and API behavior. For these changes, follow this sequence:

```text
RED → prove failure → GREEN → prove success → REFACTOR → prove suite still passes
```

Write or update a focused test that expresses the intended behavior, observe it
fail for the original behavior, implement the smallest change that makes it pass,
then run the relevant suite after refactoring. A deterministic bug fix must add
or update regression coverage that fails before the correction and passes after
it, whenever feasible.

TDD is recommended for feature behavior. Strict TDD may be relaxed when it would
not provide useful deterministic feedback, including for prototypes, exploratory
user interfaces, configuration-only changes, generated artifacts, and
appropriate migrations. Record the specific rationale, the behavior not covered
by strict TDD, and the alternative verification before claiming completion. Do
not use an exception merely to defer an available deterministic test.

## Run and interpret checks

Run the relevant focused checks during implementation, then the broader required
checks for the affected boundary. Preserve evidence of the command or procedure,
inputs or environment where material, observed result, and coverage limits. A
passing test is evidence only for behavior it exercises; assess related
acceptance criteria, compatibility, and regression risk separately.

For a bug fix, repeat the original reproduction procedure when feasible in
addition to the regression test. If the defect is intermittent or cannot be
reproduced deterministically, state the observation window or trials, residual
uncertainty, and why deterministic regression coverage is not feasible. Use
[debugging-systematically](../debugging-systematically/SKILL.md) when causal
investigation is still needed.

## Record completion evidence

Record test and alternative-verification evidence in the issue or linked pull
request, including:

- behavior and acceptance criteria covered;
- RED, GREEN, and post-refactor results when strict TDD applies;
- regression coverage for a bug, or the documented feasibility exception;
- relevant suite, lint, typecheck, build, security, and CI outcomes; and
- each unavailable check marked N/A with its rationale.

Testing completion means the observed evidence supports the applicable
acceptance criteria; it does not authorize review approval or pull-request merge.
