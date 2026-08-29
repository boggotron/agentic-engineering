---
name: engineering-workflow
description: Coordinate feature, bug, refactor, migration, or review work from a GitHub Issue through a human-ready pull request. Use when lifecycle, evidence, and human-merge controls must be preserved; not for a standalone answer or an isolated edit with no durable work record.
---

# Engineering workflow

Use this controller to carry a feature, bug, refactor, migration, or review
workstream through the repository engineering lifecycle. The durable record is
the linked GitHub Issue and pull request; local context is only working memory.
Follow the [canonical methodology](../../docs/methodology.md) and
[capability contract](../../docs/capability-contract.md).

## Control contract

- Determine the issue's objective, scope, non-goals, acceptance criteria,
  dependencies, blockers, and current lifecycle stage before acting. Resolve a
  material ambiguity or record its explicit unblock condition.
- Preserve the ordered lifecycle: understand, design, plan, isolate, implement,
  review, verify, CI/PR, ready for human, human approval, then merge.
- Select each needed capability by semantic guarantee: detect an adequate native
  capability first, otherwise use the narrowest portable fallback and record a
  material limitation or serialization decision. Do not add replacement
  orchestration or host-specific mechanics to core work.
- Maintain a dependency-aware plan with scope, non-goals, risks, ownership,
  affected components, acceptance criteria, and observed verification. Update
  the Issue and PR whenever a material decision, blocker, lifecycle change, or
  completion claim occurs.
- Establish an isolated write context before write-heavy implementation.
  Parallelize only bounded work with independent, non-conflicting write sets;
  serialize overlapping writes.
- Implement only approved scope. Use deterministic regression tests where they
  provide useful feedback; when they do not apply, record the rationale and
  alternative verification.
- Require independent review with fresh context where practical. Resolve
  blocking findings, then verify every applicable acceptance criterion and
  required check with observed evidence. Mark an unavailable check `N/A` with
  its rationale.
- Before ready-for-human, ensure the branch, Issue, PR linkage, review, CI, and
  verification evidence are durable and sufficient for a human decision.
  Never approve or merge a pull request; requested changes return to the
  applicable earlier lifecycle stage.

## Route narrowly

Load only the downstream Skill needed for the current stage, when it is
available:

- `designing-changes` or `planning-implementation` for understanding, design,
  or planning;
- `executing-tasks` or `testing-changes` for implementation and testing;
- `debugging-systematically` when investigating a defect or failed check; and
- `reviewing-changes`, `verifying-completion`, or `finishing-work` for the
  corresponding completion stages.

If a downstream Skill is unavailable, preserve the same semantic guarantee by
following the canonical methodology and capability contract. Do not load
unrelated Skills merely because they are installed.
