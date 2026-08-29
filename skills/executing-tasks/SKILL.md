---
name: executing-tasks
description: Execute an approved engineering plan safely, using native coordination and isolated write work without creating replacement orchestration.
---

# Executing tasks

Use this Skill after design and planning have made a task ready for
implementation. It turns an approved, dependency-aware plan into bounded work
while preserving isolation, durable GitHub state, and the human merge boundary.
It defines execution guarantees, not a scheduler, task system, or host-specific
workflow.

## Start from an executable task

Confirm that the task's objective, scope, acceptance criteria, dependencies,
affected components, tests, and verification are known from the durable work
record. Do not begin a task with an unresolved prerequisite or a material
ambiguity. Record a blocker and its explicit unblock condition instead.

Before write-heavy work, establish an isolated change boundary attributable to
the work item. Select a detected native isolation capability when it meets that
guarantee; otherwise use the narrowest portable fallback. Keep the issue and
linked pull request current when task status, a material decision, a blocker, or
scope changes.

## Coordinate work safely

Prefer a detected native capability for planning, delegation, isolation, and
task coordination. A delegated task must have an explicit objective, bounded
scope, owner, expected handoff, and verification. Do not add a custom scheduler,
worktree manager, project-state store, or orchestration service merely to
coordinate implementation.

Parallelize read-only investigation and independently reviewable work when the
results do not depend on each other. Parallel implementation is allowed only
when every concurrent write set is isolated and non-conflicting. Serialize
overlapping write-heavy work by default; record any material serialization or
fallback decision in the durable work record.

Use a fresh execution context for a bounded task when it improves independence,
reduces stale assumptions, or gives a reviewer a clearer handoff. Fresh context
is an aid to correctness, not a reason to lose the task's scope, dependencies,
or evidence. When native delegation is unavailable or not useful, execute the
same bounded tasks sequentially and record a material limitation when it affects
delivery or verification.

## Implement and hand off

Implement only the approved scope. Keep changes small and attributable to the
task, and return to design or planning before proceeding if an implementation
discovery materially changes the chosen approach, dependency order, risk, or
acceptance criteria.

Use [testing-changes](../testing-changes/SKILL.md) for the applicable testing
discipline. Before handing a completed task to review, record the implementation
result, observed checks, acceptance-criteria evidence, deviations, and remaining
risks in the issue or linked pull request. A task is ready for independent review
only when its required tests pass or a justified exception and alternative
verification are recorded. Do not approve or merge a pull request.
