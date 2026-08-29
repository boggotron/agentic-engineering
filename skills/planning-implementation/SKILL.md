---
name: planning-implementation
description: Produce a dependency-aware, verifiable implementation plan using native host planning while preserving the portable plan contract.
---

# Planning implementation

Use this Skill after design has selected an approach and before write-heavy
implementation. Use the host's native planning capability when available to
produce and maintain the plan. This Skill defines the information the plan must
contain; it does not prescribe a planner, task-tracker, file format, or custom
planning system.

## Plan contract

Record the following for every material plan in the durable work record required
by the project:

- **Goal:** the intended outcome and value.
- **Status and ownership:** the plan's current lifecycle status and accountable
  owner.
- **Scope:** included behavior, systems, and boundaries.
- **Non-goals:** intentionally excluded work.
- **Architecture impact:** the affected design, interfaces, and invariants, or
  an explicit statement that there is no material impact.
- **Dependencies:** prerequisite issues, decisions, services, artifacts, or
  external conditions, including their status.
- **Risks:** meaningful delivery, correctness, compatibility, operational, or
  rollback risks and their mitigation or escalation path.
- **Security implications:** applicable trust, authorization, privacy, secret,
  or threat-model effects; otherwise a justified N/A statement.
- **Data implications:** applicable data ownership, retention, integrity,
  schema, or privacy effects; otherwise a justified N/A statement.
- **Migration implications:** applicable rollout, compatibility, backfill,
  rollback, or transition effects; otherwise a justified N/A statement.
- **Tasks:** independently reviewable units, each with its objective, affected
  components or files, dependencies, accountable owner, current status,
  acceptance criteria, tests, and verification.

Plans may use a project-approved issue, checklist, planning artifact, or
equivalent native plan representation, provided all contract fields remain
discoverable. Do not replace native planning with a parallel scheduler or
project-state store.

## Shape the execution

Order tasks by their dependencies so that no task starts on an unaddressed
prerequisite. Make task boundaries small enough for a reviewer to assess their
purpose and evidence independently, but avoid splitting work solely to increase
task count. Identify tasks that may proceed in parallel only when their work is
independent or their write sets are isolated and non-conflicting; serialize
overlapping write-heavy work by default.

Give every material task concrete, observable acceptance criteria and a
verification method. Specify relevant tests and checks, or record a justified
N/A outcome and an alternative verification method. Include review and required
CI or delivery evidence when they are part of completion.

## Keep the plan current

Record the plan and material updates in the project's durable work state,
normally the linked issue and pull request. If a new dependency, risk, or
design decision changes execution order, scope, or correctness, update the plan
before continuing. A plan is ready for implementation when it has a safe order,
each material task has verification, and no dependency is left unaddressed.
