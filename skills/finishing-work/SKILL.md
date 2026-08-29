---
name: finishing-work
description: Prepare a verified workstream for human review by completing durable Issue, pull-request, and CI readiness evidence without merging.
---

# Finishing work

Use this Skill after review and completion verification to prepare a linked
Issue and pull request for a human decision. Its terminal state is
`ready-for-human`; it never authorizes approval or merge.

## Complete the PR and CI gate

Confirm that the isolated branch contains the intended final change and that a
pull request is linked to its implementation Issue. Keep both records current
with a concise implementation summary, scope-relevant risks, and all completion
evidence. Ensure the PR makes clear that a human merge is required.

Wait for required CI and required repository checks, using the host's native
facilities when available. Record the observed CI/check result and relevant
revision. If CI or review reports a failure or requested change, return to the
applicable lifecycle stage, remediate within approved scope, and repeat the
affected review and verification. If a required check is unavailable or no
applicable CI exists, record that status as `N/A` with the reason and the
alternative verification; do not describe it as passing.

## Apply the ready-for-human gate

Before setting the durable state to `ready-for-human`, confirm and record each
of these outcomes for the final revision:

- implementation is complete and within the linked Issue's approved scope;
- every acceptance criterion has observed passing evidence;
- applicable tests, regression checks, lint, type check, build, and security
  checks pass, or each has a justified N/A result;
- independent review is recorded and all blocking findings are resolved;
- required CI is passing, or its explicitly unavailable/inapplicable status and
  alternative verification are recorded;
- the Issue and PR are linked and contain reproducible completion evidence; and
- known risks, limitations, and non-blocking follow-ups are visible to the
  human reviewer.

If any item is missing or inconclusive, do not mark ready for human. Record the
blocker and its explicit unblock condition, then resume from the earliest stage
needed to resolve it.

Once the gate passes, update the Issue and PR to the repository's
`ready-for-human` convention. Stop at that boundary. A human may approve,
request changes, or merge; an agent must not approve on a human's behalf or
perform the merge.
