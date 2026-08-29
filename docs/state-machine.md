# GitHub workflow state machine

GitHub Issues, pull requests, reviews, and CI are the durable workflow record.
An agent session may perform work, but it must record material decisions,
blockers, and completion evidence here before ending.

## Labels and states

Apply exactly one lifecycle label to an active implementation issue:

| Label | Use when | Exit condition |
| --- | --- | --- |
| `state:backlog` | Work has been identified but is not designed. | Objective and initial scope are understood. |
| `state:design` | A material design decision remains. | Chosen approach and acceptance criteria are durable. |
| `state:planned` | Design is accepted and executable work is being planned. | Tasks, dependencies, tests, and verification are defined. |
| `state:ready` | The Definition of Ready is satisfied. | Isolated implementation begins. |
| `state:in-progress` | Implementation is active. | Change is ready for independent review. |
| `state:review` | An independent review is in progress. | Blocking findings are resolved and review evidence is recorded. |
| `state:verification` | Required checks and acceptance validation are running. | Evidence is complete and the PR/CI gate passes. |
| `state:ready-for-human` | PR, evidence, review, and required CI are complete. | A human approves, requests changes, or merges. |
| `state:done` | The human has merged the accepted PR. | Terminal. |
| `state:blocked` | A specific external dependency or decision prevents progress. | The issue records its unblock condition and returns to the prior active state. |

`state:blocked` may replace any active lifecycle label. Record the blocker and
the explicit condition that removes it in the issue body or a dated comment.
Use supporting labels such as `type:skill`, `type:adapter`, `type:ci`,
`type:docs`, `host:openai`, `host:claude`, `cross-platform`, and priority labels
as useful; they do not replace the lifecycle label.

## Transition rules

1. Start from an Issue. Its objective, value, scope, non-goals, dependencies,
   decisions, acceptance criteria, tests, and verification must be explicit.
2. Move to `state:ready` only when the Definition of Ready is satisfied: scope
   and non-goals are clear, dependencies are understood, acceptance criteria and
   verification are testable, and no unresolved decision can invalidate the work.
3. Use an isolated branch or equivalent boundary for write-heavy implementation.
   Keep the issue state and linked PR current throughout implementation.
4. Before `state:ready-for-human`, record the implementation summary, all
   acceptance-criterion results, required test/lint/typecheck/build/security
   results (or justified N/A), independent review outcome, CI result, known
   risks, and the linked PR.
5. Required CI must be green before `state:ready-for-human`. If the repository
   has no applicable required CI, state that fact and record the alternative
   verification; an absent check is not a passing check.
6. Only a human approves and merges. After merge, close the Issue and set
   `state:done`; agents must never perform the merge transition.

The canonical lifecycle and detailed stage entry/exit criteria are in the
[methodology](methodology.md). This document defines how that lifecycle is
represented in GitHub.
