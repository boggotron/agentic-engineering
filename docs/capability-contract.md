# Capability contract and host abstraction

- **Owner:** `@boggotron`
- **Version:** `1.0`
- **Review date:** `2026-09-02`

## Purpose

This contract specifies the capabilities an engineering host must provide to
follow the repository methodology. It describes the required outcome, not a
particular tool, command, or API. A host satisfies a capability when it
preserves the semantic guarantee defined here and records the evidence required
by the methodology.

This document is the normative source for portable semantic capabilities. It
complements the lifecycle in the [methodology](methodology.md) and authority
boundaries in the [security and autonomy
boundaries](security-and-autonomy-boundaries.md); [instruction
precedence](instruction-precedence.md) defines their rank.

The contract applies to Codex, ChatGPT, Claude Code, and a portable fallback
environment. It supports the native-first invariant: use a host-provided
capability when it meets the semantic requirement; add local infrastructure
only when detection shows that no adequate native capability is available.

## Capability matrix

| Capability | Semantic definition | Codex / ChatGPT native implementation | Claude Code native implementation | Portable fallback |
| --- | --- | --- | --- | --- |
| Planning | Produce and maintain an explicit, dependency-aware implementation plan with scope, non-goals, acceptance criteria, verification, and status. | Native planning and task-plan facilities. | Native planning mode and plan artifacts. | A version-controlled structured plan or issue checklist. |
| Agents | Delegate bounded, independently reviewable work while retaining a coordinating owner and a clear result handoff. | Native Codex subagents. | Native Claude Code agents/subagents. | Sequential execution by one agent; document the omitted parallelism. |
| Isolation | Prevent unrelated or concurrent write-heavy changes from sharing a mutable working tree or branch. | Managed worktrees or an isolated branch supplied by the host. | Native worktree/branch workflow. | Git worktree; if unavailable, a dedicated branch with serialized writes. |
| Review | Evaluate a completed change with context independent from the implementer, covering the applicable review dimensions and resolving blocking findings. | Native review capability and/or a fresh Codex reviewer agent. | Fresh reviewer agent or native review workflow. | A fresh-context reviewer, preferably a different person or agent. |
| Skills | Load reusable, scoped methodology instructions with progressive disclosure and repository-local context. | Native Agent Skills, including skills-only plugin distribution. | Native Claude Skills and plugin/skills distribution. | Repository instruction files and documented, manual invocation order. |
| Git / GitHub | Use branches, commits, Issues, pull requests, and CI as durable engineering records and controls. | Native Git/GitHub integration or available Git and GitHub tools. | Native Git integration plus GitHub CLI, API, or MCP when available. | Git CLI and GitHub web/API access. |
| Testing | Run the relevant deterministic checks and report observed results; use a regression test for deterministic bugs where appropriate. | Shell and project test tools. | Shell and project test tools. | Project test commands or a documented manual test procedure. |
| Verification | Independently establish that acceptance criteria and completion gates pass with observed evidence before claiming completion. | Shell/tools, CI status, and native verification/review support. | Shell/tools, CI status, and reviewer evidence. | Commands, CI, and a recorded evidence checklist. |

### Capability requirements

The matrix rows are normative. A substitution is valid only when it provides
the semantic definition in the second column; matching a tool name is not
sufficient. In particular:

- Planning must expose dependencies and verification, not merely a to-do list.
- Delegation must have a bounded task, ownership, and handoff; an untracked
  background task does not satisfy the agents capability.
- Isolation must protect overlapping write-heavy work. Independent read-only
  research may share a workspace when it cannot mutate repository state.
- Review must use fresh context where practical. Self-review supplements but
  does not replace independent review for material changes.
- GitHub Issues and PRs are the durable work-state record. Agent conversation
  history is not a substitute.
- Verification is an evidence gate: a claim that a change “should work” is not
  verification.

## Native-first selection algorithm

Use this algorithm for each required capability and whenever a host or tool
environment changes.

1. Identify the semantic requirement from this contract and the lifecycle
   stage that needs it.
2. Detect the host-native capability and its relevant limits (for example,
   whether it can create isolated worktrees, run tests, or access GitHub).
3. Confirm that the native capability satisfies the semantic definition and
   repository safety constraints. Prefer it when it does.
4. If it is missing or insufficient, select the narrowest documented portable
   fallback that preserves the same guarantee.
5. Record any material limitation, fallback, or intentional serialization in
   the Issue/PR evidence so a later session can understand the decision.
6. Only propose new repository infrastructure after the preceding detection
   and fallback checks show a repeated, material gap. The proposal must state
   why native facilities and portable fallbacks are inadequate.

This sequence is mandatory. An agent must not build a scheduler, worktree
manager, review engine, state database, or orchestration service merely because
the host implementation is unfamiliar. The current v1 policy explicitly
prefers host-native planning, agents, isolation, review, Git/GitHub, and CI.

## Host-reference conventions

Core Skills define portable outcomes and constraints. They must not require a
host-specific command, tool name, plugin, file path, or UI interaction. For
example, a core Skill may require “create isolated working context for
write-heavy work,” but may not prescribe a particular Codex or Claude command.

Apply these conventions when authoring or reviewing core Skills:

1. Express requirements as capability outcomes using the names in this
   contract (for example, `isolation`, `review`, or `verification`).
2. Refer to a host adapter/reference only when an operator needs concrete,
   host-specific instructions. Keep that material outside canonical core Skill
   content.
3. Use conditional language for optional capabilities: detect first, then use
   the native implementation or the portable fallback.
4. Keep host-specific installation, authentication, invocation syntax, and UI
   instructions in `adapters/openai/`, `adapters/claude/`, or a corresponding
   `docs/host-guides/` reference.
5. Do not fork behavioral policy by host. Any intentional variation must name
   the unchanged semantic guarantee, the host constraint, and the fallback or
   compensating control.

The following pattern is required in core Skill text:

```text
Require: independent review before ready-for-human.
Select: a detected native review capability; otherwise use a fresh-context reviewer.
Record: reviewer identity/context and resolved blocking findings in PR evidence.
```

The following pattern is prohibited in core Skill text:

```text
Run a named host command or invoke a named host-only tool to perform review.
```

## Representative workflow checks

These walkthroughs show equivalent semantics, not identical mechanics. They
are the minimum verification scenarios for this contract.

| Workflow | Codex / ChatGPT path | Claude Code path | Contract result |
| --- | --- | --- | --- |
| Implement a write-heavy Issue | Use native planning, delegate bounded read-only work if useful, create a managed isolated worktree, implement and test, request native/fresh review, update Issue/PR and CI evidence. | Use native planning, delegate bounded work if useful, use its branch/worktree workflow, implement and test, request a fresh reviewer agent, update Issue/PR and CI evidence. | The same plan, isolation, testing, independent review, verification, and durable GitHub state are present. |
| Host lacks subagents | Detect that native agents are unavailable and execute the bounded tasks sequentially; retain plan and evidence. | Detect that native agents are unavailable and execute sequentially; retain plan and evidence. | Delegation is replaced by documented serialization without changing ownership or verification gates. |
| Host lacks managed worktrees | Detect the limitation and use a dedicated Git worktree or isolated branch with serialized writes. | Detect the limitation and use a dedicated Git worktree or isolated branch with serialized writes. | Write-heavy work remains isolated; no custom worktree manager is introduced. |

## Non-goals

This contract does not standardize host commands, build a custom orchestration
layer, or guarantee that every host exposes the same tools. It standardizes the
engineering guarantees that adapters and fallbacks must preserve. It also does
not authorize autonomous merging: the human merge boundary remains invariant.

## Maintenance

Update this contract before changing a core Skill when a new semantic
capability, host constraint, or fallback affects portability. Adapter-specific
details should be updated in their host reference first; changing a core Skill
requires preserving the capability definitions and conventions above.
