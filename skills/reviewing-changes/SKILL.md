---
name: reviewing-changes
description: Independently review a proposed engineering change against its issue, design, and implementation evidence before verification or PR readiness.
---

# Reviewing changes

Use this Skill after implementation and before completion verification. Its
outcome is an independent, durable assessment of whether the change is safe to
verify—not an implementation plan, a substitute for host-native review, or an
approval to merge.

## Establish an independent review

Use an available host-native review capability first. Otherwise, use a reviewer
with fresh context who did not make the change. Give the reviewer the issue,
design or plan, diff, relevant repository context, and verification evidence;
do not ask it to defer to the implementer's conclusion. If independent review
is impractical, record why, the alternative review performed, and the residual
risk in the durable work record.

Review the actual change and its affected behavior, not only a summary. Compare
it with the approved scope, non-goals, acceptance criteria, and relevant
interfaces. Check, as applicable:

- specification and acceptance-criterion compliance;
- correctness, edge cases, error handling, and regression risk;
- test coverage and the quality of tests or other verification;
- maintainability, clarity, scope discipline, and compatibility;
- security, privacy, data-handling, reliability, performance, and observability
  effects; and
- whether documentation, migration, rollout, or operational implications are
  accurately addressed.

Mark an inapplicable dimension N/A with a brief reason; do not imply it was
reviewed by omission.

## Resolve findings and preserve the record

Record review evidence in the linked Issue or pull request: reviewer
independence or limitation, material inputs inspected, findings and severity,
and the observed outcome. A finding that can affect correctness, security,
data integrity, compatibility, required behavior, or release safety is
blocking unless the project's documented process classifies it otherwise.

Return blocking findings to implementation. Correct them, run the checks made
necessary by the correction, and obtain another independent review of the
affected result. Do not advance while a blocking finding is unresolved.
Track accepted non-blocking findings or follow-up work durably, with ownership
or a concrete next action when material. A clean review is evidence only after
the reviewer has examined the final relevant diff.

Hand off to `verifying-completion` only when the review outcome is recorded,
blocking findings are resolved, and any non-blocking residual risk is explicit.
