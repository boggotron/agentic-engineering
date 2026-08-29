# Cross-Platform Agentic Engineering Repository Plan

## Purpose

This repository will define a single, portable engineering methodology that can be followed by Codex, ChatGPT, and Claude Code without forcing any agent to reimplement capabilities that its host already provides natively.

The methodology retains the strongest process guarantees from Superpowers—structured design, planning, test discipline, systematic debugging, independent review, and evidence-before-completion—while treating worktrees, planning engines, subagent orchestration, code review engines, Git operations, and other execution mechanics as host responsibilities wherever possible.

GitHub is the durable control plane. Agent sessions are ephemeral workers. Every meaningful implementation unit starts from a GitHub Issue, moves through explicit lifecycle states, produces a PR, passes review and verification, and stops at a human approval boundary before merge.

Parent Epic: #1

---

## 1. Architectural decision

### Canonical abstraction

The cross-platform methodology will be implemented as a collection of portable Agent Skills.

For OpenAI, those Skills will be distributed as a skills-only Plugin for Codex and ChatGPT.

For Claude Code, the same core Skill content will be packaged through Claude's plugin/skills mechanism, with only thin host-specific adapter/reference material.

### Why this shape

- Skills are the correct unit for composable behavioral methodology.
- Progressive disclosure keeps context smaller than one monolithic instruction file.
- A Plugin is the distribution/versioning boundary for the OpenAI ecosystem.
- Core Skill content can remain substantially identical across hosts.
- Host adapters can map semantic requirements to native capabilities without forking the methodology.
- MCP and lifecycle hooks are deliberately excluded from v1 unless later evidence shows they materially improve enforcement or orchestration.

### Target repository structure

```text
agentic-engineering/
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── CONTRIBUTING.md
│
├── docs/
│   ├── methodology.md
│   ├── state-machine.md
│   ├── capability-contract.md
│   ├── architecture-decisions/
│   └── host-guides/
│       ├── codex.md
│       ├── chatgpt.md
│       └── claude-code.md
│
├── skills/
│   ├── engineering-workflow/
│   ├── designing-changes/
│   ├── planning-implementation/
│   ├── executing-tasks/
│   ├── testing-changes/
│   ├── debugging-systematically/
│   ├── reviewing-changes/
│   ├── verifying-completion/
│   └── finishing-work/
│
├── adapters/
│   ├── openai/
│   │   └── .codex-plugin/
│   └── claude/
│
├── evals/
│   ├── planning/
│   ├── testing/
│   ├── debugging/
│   ├── review/
│   └── verification/
│
├── schemas/
│   ├── plan.schema.json
│   └── completion-evidence.schema.json
│
├── templates/
└── .github/
    ├── ISSUE_TEMPLATE/
    ├── PULL_REQUEST_TEMPLATE.md
    └── workflows/
```

---

## 2. Canonical engineering lifecycle

The methodology must preserve the following lifecycle regardless of host:

```text
UNDERSTAND
    ↓
DESIGN
    ↓
PLAN
    ↓
ISOLATE
    ↓
IMPLEMENT
    ↓
REVIEW
    ↓
VERIFY
    ↓
CI / PR
    ↓
READY FOR HUMAN
    ↓
HUMAN APPROVAL
    ↓
MERGE
```

The lifecycle is semantic, not mechanical. A host may satisfy a stage using native features.

Examples:

- Codex may use native managed worktrees for ISOLATE.
- Claude Code may use its own worktree/branch workflow.
- Codex may use native review capabilities for REVIEW.
- Claude Code may use a fresh reviewer agent.

The methodology defines the guarantee that must be preserved, not the exact command used to satisfy it.

---

## 3. Core invariants

1. **Native first.** Before implementing orchestration or infrastructure, check whether the host already provides the required capability.
2. **Methodology belongs in Skills.** `AGENTS.md` and `CLAUDE.md` contain repository-specific facts, commands, and constraints only.
3. **GitHub is durable state.** Long-lived work state lives in Issues, PRs, and CI, not agent conversation history.
4. **Evidence before completion.** Completion claims require observed verification evidence.
5. **TDD where appropriate.** Deterministic behavior and bug fixes default to RED → GREEN → REFACTOR, with explicit exceptions where strict TDD is not productive.
6. **Independent review.** Review should use fresh context or a host-native independent reviewer wherever practical.
7. **Parallelize safely.** Independent/read-heavy work can run in parallel; overlapping write-heavy work is serialized by default.
8. **No autonomous merge.** Agents may work through PR readiness and CI remediation but cannot cross the human merge boundary.
9. **No unnecessary infrastructure.** v1 does not include a custom MCP orchestration service, custom worktree manager, custom review engine, or separate project-state database.
10. **Cross-host portability.** Target at least 90% shared core Skill content between OpenAI and Claude distributions.

---

## 4. GitHub Issues state machine

GitHub Issues are the canonical state record for implementation work.

Recommended state labels:

```text
state:backlog
state:design
state:planned
state:ready
state:in-progress
state:review
state:verification
state:blocked
state:ready-for-human
state:done
```

Recommended supporting labels:

```text
type:epic
type:architecture
type:skill
type:adapter
type:eval
type:ci
type:docs

priority:p0
priority:p1
priority:p2

host:openai
host:claude
cross-platform
```

Canonical transitions:

```text
backlog
   ↓
design
   ↓
planned
   ↓
ready
   ↓
in-progress
   ↓
review
   ↓
verification
   ↓
ready-for-human
   ↓
[HUMAN MERGE]
   ↓
done
```

Any active state may move to `blocked`, but the issue must record the blocker and explicit unblock condition.

### Definition of Ready

An issue cannot enter `state:ready` until:

- objective is explicit;
- scope and non-goals are defined;
- dependencies are understood;
- acceptance criteria are testable;
- architecture is sufficiently understood;
- verification is specified;
- no unresolved design decision would materially invalidate implementation.

### Definition of Ready for Human

A PR cannot reach `state:ready-for-human` until:

```text
Implementation complete          PASS
Acceptance criteria              PASS
Tests                            PASS
Lint/typecheck/build             PASS or justified N/A
Security checks                  PASS or justified N/A
Independent review               PASS
Blocking findings resolved       PASS
CI                               PASS
PR linked to Issue               PASS
Completion evidence recorded     PASS
```

Merge itself remains an explicit human action.

---

## 5. Capability contract

The repository must define semantic capabilities and map them to host-native implementations.

| Semantic requirement | Codex / ChatGPT | Claude Code | Portable fallback |
|---|---|---|---|
| Planning | Native planning | Native planning | Structured plan contract |
| Subagents | Native subagents | Native agents | Sequential execution |
| Isolation | Managed worktrees | Native/Git isolation | Git worktree or dedicated branch |
| Review | Native review + agents | Reviewer agents | Fresh-context review |
| Skills | Native Agent Skills | Native Skills | Repository instruction fallback |
| Git/GitHub | Native/tool integration | Native/CLI/MCP as available | Git CLI/API |
| Testing | Shell/tools | Shell/tools | Project test commands |
| Verification | Shell/tools + CI | Shell/tools + CI | Evidence protocol |

Core Skills must never hard-code host-specific commands except in host adapter/reference files.

---

## 6. Skill architecture

### `engineering-workflow`

Controller Skill. It detects engineering task type and current lifecycle stage, loads only the relevant downstream Skills, prefers native host capabilities, requires isolation for write-heavy implementation, and enforces review/verification/human-merge boundaries.

Issue: #5

### `designing-changes`

Requires sufficient understanding of the existing system, resolution of material ambiguity, exploration of alternatives for consequential decisions, identification of constraints, and explicit acceptance criteria.

Issue: #6

### `planning-implementation`

Defines the plan contract while delegating plan generation to the host's native planning capability.

Every material plan contains:

- Goal
- Scope
- Non-goals
- Architecture impact
- Dependencies
- Risks
- Security implications
- Data implications
- Migration implications
- Per-task objective
- Affected components/files
- Dependencies
- Acceptance criteria
- Tests
- Verification

Issue: #6

### `executing-tasks`

Defines execution policy rather than implementing a custom scheduler.

- Parallelize independent/read-heavy tasks.
- Parallelize isolated implementation only when write sets do not conflict.
- Serialize overlapping write-heavy work by default.
- Prefer native host subagent orchestration.
- Use fresh execution context for independently reviewable tasks where useful.

Issue: #7

### `testing-changes`

Default deterministic workflow:

```text
RED
↓
prove failure
↓
GREEN
↓
prove success
↓
REFACTOR
↓
prove suite still passes
```

Strict TDD is required by default for deterministic business logic, bug fixes, and API behavior; recommended for feature behavior; and may be relaxed for prototypes, exploratory UI, configuration, generated artifacts, or appropriate migrations with rationale.

Issue: #7

### `debugging-systematically`

Required debugging discipline:

```text
Reproduce
↓
Gather evidence
↓
Form hypothesis
↓
Test hypothesis
↓
Identify root cause
↓
Apply minimum correction
↓
Regression verification
```

Issue: #8

### `reviewing-changes`

Defines review semantics rather than review implementation.

Review dimensions:

- specification compliance;
- functional correctness;
- regression risk;
- test quality;
- maintainability;
- security;
- reliability;
- performance where material;
- observability where material.

Issue: #9

### `verifying-completion`

Hard gate prohibiting claims such as “should work” or “looks correct” in place of observed evidence.

Expected evidence includes tests, lint, typecheck, build, security checks, acceptance criteria, review, and CI.

Issue: #9

### `finishing-work`

Final workflow:

```text
verify branch
↓
run final checks
↓
confirm issue acceptance criteria
↓
commit/push
↓
create or update PR
↓
wait for CI
↓
address findings
↓
READY FOR HUMAN MERGE
```

The Skill must not duplicate host worktree lifecycle management and must never merge autonomously.

Issue: #9

---

## 7. Implementation program and dependency graph

### Phase 0 — Architecture foundation

- #2 `[A] Define canonical methodology and invariants`
- #3 `[B] Define capability contract and host abstraction`
- #4 `[C] Establish repository policy and contribution conventions`
- #12 `[K] Implement GitHub Issues/PR state machine and templates`

These form the first implementation wave.

### Phase 1 — Core Skills

- #5 `[D] Implement engineering-workflow controller Skill`
- #6 `[E] Implement design and planning Skills`
- #7 `[F] Implement execution and testing Skills`
- #8 `[G] Implement systematic debugging Skill`
- #9 `[H] Implement review, verification, and finishing Skills`

These may proceed substantially in parallel after the methodology/capability contracts stabilize.

### Phase 2 — Host packaging

- #10 `[I] Package canonical Skills as an OpenAI skills-only Plugin`
- #11 `[J] Package canonical Skills for Claude Code`

Both distributions should consume the same canonical Skill sources and keep host-specific material in adapter/reference files.

### Phase 3 — CI and evaluation

- #13 `[L] Add CI validation for Skills, packaging, docs, schemas, and evals`
- #14 `[M] Build cross-agent behavioral evaluation harness`

### Phase 4 — Hardening

- #15 `[N] Evaluate parity and intentional deviations from Superpowers`
- #16 `[O] Define security and autonomy boundaries`

### Phase 5 — Documentation and release readiness

- #17 `[P] Create cross-platform documentation and quickstarts`
- #18 `[Q] Prepare v0.1 release readiness gate`

### Dependency overview

```text
#1 EPIC
│
├── #2 Methodology ─────┬── #5 Workflow
│                      ├── #6 Design/Planning
│                      ├── #7 Execution/Testing
│                      ├── #8 Debugging
│                      └── #9 Review/Verification
│
├── #3 Capability ──────┬── #10 OpenAI
│                      └── #11 Claude
│
├── #4 Repo Policy
├── #12 GitHub State Machine
│
├── #13 CI
│
├── #14 Cross-Agent Evals
│       ↑ #5–#11
│
├── #15 Superpowers Parity
│       ↑ #14
│
├── #16 Security Review
│       ↑ #5/#9/#12
│
├── #17 Documentation
│       ↑ #10/#11/#12
│
└── #18 v0.1 Release
        ↑ #13/#14/#15/#16/#17
```

---

## 8. GitHub templates

### Implementation Issue contract

Every implementation issue should capture:

- Objective
- Business/user value
- Scope
- Non-goals
- Dependencies
- Design decisions
- Acceptance criteria
- Testing requirements
- Verification requirements
- Related issues
- Related PR

### Pull Request contract

Every PR should capture:

- `Closes #...`
- Implementation summary
- Acceptance criteria
- Test evidence
- Verification evidence
- Review status
- CI status
- Known risks
- `Human merge required: YES`

Issue #12 implements these templates and state conventions.

---

## 9. Evaluation strategy

Behavioral evaluation must test semantic methodology compliance rather than identical host tool calls.

Required scenarios:

1. ambiguous feature requiring design;
2. trivial task that should avoid over-planning;
3. deterministic bug requiring a regression test;
4. difficult debugging task;
5. parallelizable research task;
6. conflicting write-heavy task;
7. review-only request;
8. agent attempting completion without evidence;
9. runtime with native worktrees;
10. runtime without native isolation.

The v0.1 target is at least 90% behavioral-eval pass rate.

Issue: #14

---

## 10. Superpowers parity strategy

After the portable methodology and host adapters are working, perform an explicit parity review using the matrix:

| Superpowers capability | Repository equivalent | Parity | Intentional deviation | Rationale | Native-host replacement |
|---|---|---|---|---|---|

Every omission or deviation must be intentional and documented. The goal is not literal implementation parity; the goal is preservation of valuable engineering guarantees while eliminating duplication of modern host-native functionality.

Issue: #15

---

## 11. Security and autonomy model

The methodology must explicitly define agent authority for:

- destructive shell commands;
- secrets and credentials;
- dependency/package installation;
- network access;
- GitHub mutations;
- CI workflow modifications;
- deployments;
- releases;
- branch protection;
- merge.

The v1 policy is that agents can autonomously perform normal implementation, testing, review, PR creation/update, and CI remediation within repository boundaries, while merge remains human-only. Additional high-impact operations must be explicitly categorized during the security review.

Issue: #16

---

## 12. v1 non-goals

Do not initially build:

- an engineering MCP server;
- custom multi-agent orchestration;
- a separate project-state database;
- custom worktree management;
- a custom code-review engine;
- autonomous merge;
- complex lifecycle hooks;
- host-specific forks of the methodology.

MCP should be reconsidered only if GitHub proves insufficient for cross-session orchestration, centralized telemetry, approval-state enforcement, or controlled external service actions.

Hooks should be reconsidered only if behavioral evals show that instruction-level methodology is routinely bypassed and structural enforcement is warranted.

---

## 13. Success metrics

- At least 90% shared core Skill content across OpenAI and Claude distributions.
- 100% of implementation PRs linked to GitHub Issues.
- 100% of `ready-for-human` PRs contain verification evidence.
- Zero autonomous merges.
- At least 90% behavioral-eval pass rate before v0.1.
- Zero unnecessary reimplementations of host-native worktree/subagent/review capabilities.
- 100% of intentional Superpowers deviations documented.

---

## 14. Initial execution order

### Wave 1 — start first

1. #2 Canonical methodology and invariants
2. #3 Capability contract and host abstraction
3. #4 Repository policy and contribution conventions
4. #12 GitHub Issues/PR state machine and templates

These four issues should establish the stable contracts required by the remainder of the repository.

### Wave 2 — core behavior

Once #2 and #3 are stable enough for implementation:

- #5 controller Skill
- #6 design/planning Skills
- #7 execution/testing Skills
- #8 debugging Skill
- #9 review/verification/finishing Skills

These tasks can be developed concurrently where their file ownership is isolated.

### Wave 3 — packaging

After the relevant core Skills stabilize:

- #10 OpenAI skills-only Plugin
- #11 Claude Code packaging

### Wave 4 — independent validation

- #13 CI
- #14 cross-agent evals
- #15 Superpowers parity review
- #16 security/autonomy review

### Wave 5 — documentation and candidate release

- #17 documentation/quickstarts
- #18 v0.1 release-readiness gate

No agent should merge the release candidate. The final repository state should be presented to a human as READY FOR HUMAN with complete evidence.

---

## 15. Decision record

The v1 implementation is therefore:

```text
Canonical portable Agent Skills
            │
            ├── OpenAI skills-only Plugin
            │       ├── Codex
            │       └── ChatGPT
            │
            └── Claude Code plugin/skills adapter

GitHub Issues + PRs + Actions
            │
            └── durable work state and independent verification

Host-native planning/subagents/worktrees/review
            │
            └── preferred execution substrate

Human
            │
            └── final merge authority
```

This architecture intentionally keeps the engineering methodology portable while allowing each agent harness to improve independently underneath it.
