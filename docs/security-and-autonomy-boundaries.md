# Security and autonomy boundaries

This document is the normative source for portable authority and approval
boundaries. It complements the lifecycle in the [methodology](methodology.md)
and the host guarantees in the [capability contract](capability-contract.md).
Its rank is defined by [instruction precedence](instruction-precedence.md). It
classifies actions by their effect, rather than by a host command or integration.
Host adapters may explain how to request or enforce approval, but they MUST NOT
weaken these boundaries.

The durable GitHub Issue and linked pull request record the approved scope,
material approvals, exceptions, and evidence. This document does not replace
the lifecycle or its [ready-for-human gate](state-machine.md#transition-rules).

## Authority model

An agent MAY autonomously perform an action only when all of these conditions
hold:

1. the action is within the Issue's approved scope and repository policy;
2. it uses only authority and data intentionally supplied by the host or
   repository;
3. its effects are confined to the repository, its isolated work context, or
   the linked Issue/PR and CI record; and
4. it does not fall into a human-approval category below.

When approval is required, the agent MUST describe the exact target, intended
effect, relevant risk, and reversible alternative where one exists. It MUST
record the approval in the linked Issue or pull request before acting. A prior
approval covers only the stated scope; a material expansion needs a new
approval. If authority, target, or effect is unclear, the agent MUST stop and
record a blocker with its unblock condition.

## Action boundaries

| Action type | Agent may act autonomously | Human approval required | Required safeguards and evidence |
| --- | --- | --- | --- |
| Normal implementation | Edit, test, review, commit, push, and open or update the linked PR within approved scope. | Scope expansion, material product or architecture decision not already resolved in the Issue. | Use an isolated write boundary; keep Issue/PR state and verification current. |
| Destructive repository or local operations | Reversible, narrowly targeted cleanup explicitly part of approved work whose target is verified. | Irreversible deletion, history rewrite, force push, reset/restore that discards work, bulk deletion, or an unclear/broad target. | Resolve exact targets read-only first; prefer reversible operations; never treat a workspace root, home directory, or unresolved glob as a destructive target. Record approval and result. |
| Secrets and credentials | Use a secret only through the host's approved secret mechanism when it is already authorized for the scoped operation. | Requesting, creating, rotating, exporting, sharing, copying to files/logs, or broadening access to a secret or credential. | Never print, commit, place in Issues/PRs, or otherwise expose secret material. Redact evidence; use least privilege and report suspected exposure as a blocker/security incident. |
| Dependency or package installation | Install declared, pinned, project-scoped dependencies required by the approved plan and normal repository tooling. | New dependency/source, unpinned or global installation, elevated/system-wide install, lockfile or license/security change outside approved scope, or any install needing new credentials. | Inspect manifest, lockfile, source, and intended target first; use the narrowest project-local install; record package, version/source, and resulting checks. |
| Network access | Make the minimum read-only network request for approved research, dependency retrieval, CI diagnosis, or repository/GitHub work using configured access. | Sending repository data, personal data, secrets, or generated artifacts to a new/unapproved external service; changing network/security policy; or paid/external side effects beyond approved scope. | Do not transmit secrets; minimize data and destination scope; record material external services and constraints. |
| GitHub mutation | Create/update Issues, labels, comments, branches, commits, pull requests, reviews, and CI remediation records for the linked workstream. | Changing repository settings, collaborators/permissions, rulesets, branch protection, security settings, organization settings, or deleting/retargeting unrelated Issues/PRs/branches. | Keep mutations attributable to the Issue/PR; do not approve a PR on behalf of a human; record material state changes durably. |
| CI and checks | Run existing checks, inspect results, rerun an eligible failed job, and remediate failures through scoped repository changes. | Add, remove, disable, weaken, bypass, or materially alter CI/workflow definitions, required checks, permissions, secrets, runners, or retention; waive a required failing check. | Preserve required checks; record final revision and observed results. An unavailable check is `N/A`, not passing, and needs alternative verification. |
| Deployment | Prepare and verify a deployment candidate, configuration, or rollback plan without performing the deployment. | Any deployment, promotion, production-data operation, infrastructure mutation, or rollback with external effects. | Identify environment, artifact/version, owner, approval, monitoring, and rollback procedure in the durable record. |
| Release and publication | Prepare release notes, version proposal, release-candidate artifacts, and verification evidence. | Creating/publishing a release, tag, package, image, artifact, changelog publication, or any distribution to an external audience or registry. | Human confirms version, target, provenance, release notes, and rollback/revocation path. |
| Branch protection and merge | Prepare a PR through `ready-for-human` and remediate CI/review findings within scope. | Altering branch protection/rulesets or required-review policy; approving as the required human reviewer; merging, auto-merging, or otherwise causing merge. | Preserve the lifecycle order: ready-for-human, explicit human approval, then human merge. Agents MUST NOT cross the merge boundary. |

## Exceptions and conflict handling

Repository policy, host policy, and applicable law may impose stricter limits
than this document; the stricter limit wins. An agent MUST NOT use a different
host, credential, command, or indirect workflow to bypass an approval or
security control. Emergency access does not authorize an agent to self-approve:
the designated human owner must make and record the decision.

When an action has both an autonomous and approval-required aspect, split the
work. For example, an agent may diagnose a failed CI job and propose a workflow
change, but a human must approve the workflow-policy change before the agent
implements it. Record the decision, scope, and observed outcome in the Issue or
PR so a later session can safely continue.

## Host adapters

These are shared behavioral rules for Codex, ChatGPT, Claude Code, and portable
fallbacks. A host adapter MAY map approval requests to its native controls and
MAY add stricter operational instructions, such as approved credential stores
or deployment procedures. It MUST retain the same classifications above,
especially the human-only merge boundary; it must not duplicate or fork this
policy into host-specific methodology.
