# Durable workflow examples

These examples apply the [canonical methodology](methodology.md) to common
workstreams. They show the required semantic guarantees, not host-specific
commands. Start each from a GitHub Issue, use an available native capability
first, and record material decisions and observed evidence in the linked Issue
and pull request.

## Feature work

1. Confirm the Issue's scope, non-goals, dependencies, acceptance criteria,
   and verification. Record any design decision in the Issue.
2. Use the host's native planning and isolation when they meet the
   [capability contract](capability-contract.md); otherwise create the narrowest
   portable isolated branch/worktree and record that fallback.
3. Implement only the approved scope. Delegate only bounded, independent work;
   serialize overlapping writes. Run applicable project checks and retain their
   observed results.
4. Obtain independent review with fresh context where practical. Resolve
   blocking findings, then record acceptance, verification, and CI evidence in
   the linked PR.
5. Set the Issue to `state:ready-for-human` only when its PR is complete.
   A human, not an agent, approves and merges the PR.

## Bug and debugging work

1. Create or update the Issue with the observed symptom, affected version or
   environment, reproduction evidence, expected behavior, and current impact.
2. Use `debugging-systematically` to form and test hypotheses. Prefer the
   host's native diagnostic and test capabilities; use a documented portable
   fallback if one is unavailable. Keep failed hypotheses and material findings
   in the Issue or PR rather than chat-only notes.
3. For deterministic behavior, add or update a regression test where useful:
   demonstrate the failure, implement the smallest fix, and demonstrate the
   passing result. If strict TDD is not productive, record the rationale and
   alternative verification.
4. Have a fresh reviewer assess the fix, regression risk, and evidence. Record
   the final check results and CI in the PR, then stop at ready-for-human for
   human approval and merge.

## Review work

1. Link the review task to its Issue and pull request. Define the review scope,
   acceptance criteria, required checks, and any risk areas in the durable
   record.
2. Use a host-native independent review capability when it provides fresh
   context; otherwise use a fresh reviewer agent or person. The implementer's
   self-review supplements but does not replace independent review for material
   changes.
3. Record blocking findings on the PR, return implementation to the applicable
   lifecycle stage, and re-run the affected checks after remediation. Record
   resolution evidence and any non-blocking follow-up Issue.
4. Verify that the PR has its Issue linkage, review outcome, acceptance and
   check results, CI status, and justified `N/A` entries. Only then use
   `state:ready-for-human`; agents never approve or merge.

The [GitHub workflow state machine](state-machine.md) defines the lifecycle
labels and ready-for-human gate. The [security and autonomy boundaries](security-and-autonomy-boundaries.md)
define the human-approval boundary for merge and other sensitive actions.
