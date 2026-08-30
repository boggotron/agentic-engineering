# Canonical engineering methodology

This document is the authoritative, host-neutral engineering process for this
repository. It defines the outcomes an agent must achieve; it does not prescribe
particular commands, tools, or agent harness features.

The methodology applies to Codex, ChatGPT, Claude Code, and any future host.
Host-specific guides may explain how a host meets these requirements, but may not
weaken them. The canonical methodology abstraction is portable Agent Skills; see
[ADR 0001](architecture-decisions/0001-portable-agent-skills.md).

## Normative language

The terms **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are normative. A
documented exception is required whenever a MUST cannot be met. A SHOULD may be
departed from only with a recorded, task-specific rationale.

## Durable state and authority

GitHub Issues, pull requests, review records, and CI results are the durable
workflow state. Agent sessions, local plans, shell history, and subagent context
are ephemeral working memory and MUST NOT be the only record of a material
decision, blocker, implementation state, or completion claim.

Every meaningful implementation unit MUST have a GitHub Issue. The issue records
scope, dependencies, acceptance criteria, lifecycle state, blockers, and the
linked PR. The PR records implementation, review, and verification evidence.

Agents MAY perform ordinary repository-scoped implementation, testing, review,
commits, pushes, PR updates, and CI remediation when authorized by their host and
repository policy. Agents MUST NOT merge a PR. Merge requires explicit human
approval after the work is ready for human review.

The [security and autonomy boundaries](security-and-autonomy-boundaries.md)
classify which actions may be autonomous, which need human approval, and the
safeguards for destructive operations, secrets, external effects, and GitHub
controls. Those boundaries apply equally to every host adapter.

## Invariants

1. **Native first.** Before adding orchestration or infrastructure, an agent MUST
   determine whether its host already supplies the required capability and MUST
   prefer that native capability when it preserves the required semantic
   guarantee.
2. **Semantic guarantees, not mechanics.** The process specifies outcomes such as
   isolated write work and independent review. It MUST NOT require a particular
   worktree command, planner, reviewer implementation, or subagent API.
3. **Evidence before completion.** An agent MUST base a completion claim on
   observed evidence, not predictions such as “should work” or “looks correct.”
4. **Human merge boundary.** A PR MUST reach a ready-for-human state before a
   human approves and merges it; an agent has no authority to cross that boundary.
5. **Independent review.** Where practical, review MUST use fresh context or a
   host-native independent reviewer. The implementer MUST resolve blocking
   findings before ready-for-human.
6. **Safe parallelism.** Read-only and independent work MAY run in parallel.
   Overlapping write-heavy work MUST be serialized unless the write sets are
   isolated and non-conflicting.
7. **No unnecessary replacement infrastructure.** The methodology MUST NOT
   reimplement host-native planning, worktree, subagent, review, or Git/GitHub
   capabilities merely to impose a common interface.

## Lifecycle

The lifecycle is ordered as follows:

```text
UNDERSTAND → DESIGN → PLAN → ISOLATE → IMPLEMENT → REVIEW → VERIFY → CI / PR
→ READY FOR HUMAN → HUMAN APPROVAL → MERGE
```

`READY FOR HUMAN` is a control state between CI/PR and human approval. It makes
the human gate explicit without changing the required lifecycle order. A host may
meet a stage with native facilities, a portable fallback, or a documented manual
procedure, provided that the stage's entry and exit criteria are met.

### UNDERSTAND

**Entry:** A request or issue exists.

**Required work:** Establish the objective, scope, non-goals, constraints,
dependencies, affected users or systems, and the current repository context.
Resolve material ambiguity or record it as a blocker.

**Exit:** The issue has a testable problem statement and enough context to make a
design decision. Unknowns that could materially change the work are resolved or
the issue is marked blocked with an explicit unblock condition.

### DESIGN

**Entry:** UNDERSTAND has exited.

**Required work:** Select an approach proportionate to the change, evaluate
meaningful alternatives for consequential decisions, identify architecture,
security, data, migration, compatibility, and operational effects, and define
testable acceptance criteria.

**Exit:** The selected approach and rationale are recorded durably. No unresolved
design decision can materially invalidate implementation.

### PLAN

**Entry:** DESIGN has exited.

**Required work:** Produce an executable plan that identifies tasks, ownership,
dependencies, affected components, risks, tests, verification, and safe
parallelism. Prefer the host's native planning capability when it preserves this
contract.

**Exit:** The plan has a safe execution order, concrete verification for each
material task, and no unaddressed dependency.

### ISOLATE

**Entry:** PLAN has exited and write-heavy implementation is about to begin.

**Required work:** Establish a branch, worktree, dedicated checkout, or an
equivalent isolated change boundary. Coordinate any concurrent work so write sets
do not conflict.

**Exit:** The implementation environment is attributable to the issue and can be
reviewed independently without accidental inclusion of unrelated changes.

### IMPLEMENT

**Entry:** ISOLATE has exited.

**Required work:** Implement only the approved scope, keep GitHub state current,
and use the testing policy below. Record material deviations from design or plan
and return to an earlier lifecycle stage when they affect correctness or scope.

**Exit:** The implementation satisfies its acceptance criteria locally, required
tests are present or a documented exception exists, and the change is ready for
independent review.

### REVIEW

**Entry:** IMPLEMENT has exited.

**Required work:** Perform independent review of specification compliance,
correctness, regression risk, test quality, maintainability, security,
reliability, and material performance or observability concerns.

**Exit:** Review evidence is recorded, all blocking findings are resolved, and
non-blocking follow-ups are explicitly tracked. If review changes the solution
materially, return to IMPLEMENT and repeat applicable checks.

### VERIFY

**Entry:** REVIEW has exited.

**Required work:** Run and record the verification specified by the issue and
plan. This normally includes acceptance-criteria checks, relevant tests, lint,
type checking, build, security checks, and regression checks. A check that does
not apply MUST be marked N/A with a rationale.

**Exit:** Observed results demonstrate that all acceptance criteria pass and that
required checks pass or have a justified N/A status.

### CI / PR

**Entry:** VERIFY has exited.

**Required work:** Commit and push the isolated change, create or update a PR
linked to the issue, and wait for required CI. Remediate CI or review findings and
repeat affected lifecycle stages.

**Exit:** The PR is linked to its issue, required CI is passing, and the PR
contains implementation, review, and verification evidence.

### READY FOR HUMAN

**Entry:** CI / PR has exited.

**Required work:** Confirm that implementation, acceptance criteria, required
checks, independent review, CI, issue linkage, and completion evidence are all
complete. Set the durable issue/PR state to ready for human review according to
repository conventions.

**Exit:** A human can decide to approve or request changes without relying on an
agent's private context. This state is not approval and does not authorize merge.

### HUMAN APPROVAL

**Entry:** The work is READY FOR HUMAN.

**Required work:** A human evaluates the PR and explicitly approves it or requests
changes. Requested changes return the work to the applicable earlier stage.

**Exit:** An explicit human approval exists under repository policy.

### MERGE

**Entry:** HUMAN APPROVAL has exited and repository merge requirements are met.

**Required work:** A human performs the merge.

**Exit:** The resulting change is on the target branch and the issue is updated to
its completed state. Agents MUST NOT perform this stage.

## Testing policy

For deterministic business logic, bug fixes, and API behavior, agents MUST use
test-driven development by default:

```text
RED → prove failure → GREEN → prove success → REFACTOR → prove suite still passes
```

TDD is recommended for feature behavior. Strict TDD MAY be relaxed for prototypes,
exploratory user interfaces, configuration-only changes, generated artifacts, and
appropriate migrations when it would not provide useful deterministic feedback.
The issue or PR MUST record the rationale and the alternative verification used.

## Completion evidence

Before claiming completion or setting READY FOR HUMAN, record the observed command
or review result, outcome, and any justified N/A check. Evidence normally covers:

- acceptance criteria;
- relevant tests and regression checks;
- lint, typecheck, and build where applicable;
- security checks where applicable;
- independent review and resolution of blocking findings;
- CI result; and
- issue and PR linkage.

The absence of an applicable automated check is not evidence of success. The
alternative verification and its observed result MUST be recorded.
