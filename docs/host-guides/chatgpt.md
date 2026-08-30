# ChatGPT host guide

The OpenAI adapter supplies the same portable Skills to ChatGPT as it does to
Codex. It changes neither the engineering lifecycle nor the authority boundary:
GitHub Issues, pull requests, reviews, and CI remain the durable work record,
and human approval and merge remain mandatory.

## Access the shared Skills

The repository's OpenAI distribution is a skills-only local plugin in
[`adapters/openai`](../../adapters/openai/). Its documented installation path
uses the Codex plugin CLI; follow the [OpenAI adapter installation guide](../../adapters/openai/INSTALL.md)
from a complete repository checkout, then start a new ChatGPT work thread so
the host can load the newly installed Skills.

The adapter relies on a relative symbolic link to the canonical `skills/`
directory. Do not copy only `adapters/openai/` as an installation artifact.
It includes no MCP server, hooks, apps, credentials, orchestration service, or
project-state database. MCP and hooks are intentionally future-only rather
than prerequisites for a ChatGPT workflow.

## Run a durable workflow

Use `engineering-workflow` for a feature, bug, refactor, migration, or review
workstream with a linked GitHub Issue. It routes to a focused Skill for the
current stage instead of loading every Skill at once.

1. Read the Issue and identify scope, non-goals, dependency state, acceptance
   criteria, verification, and blockers.
2. Prefer a host-native plan, bounded delegation, isolated write context,
   review method, and Git/GitHub access when each preserves the relevant
   semantic guarantee. Use the narrowest portable fallback if a capability is
   not available, and record a material limitation or serial execution choice
   in the Issue or PR.
3. Keep the linked Issue and PR current through design, implementation,
   independent review, verification, and CI. Chat history is not a durable
   substitute for these records.
4. Record observed results for acceptance validation and every applicable
   check. Mark unavailable checks `N/A` with a rationale and alternative
   verification.
5. Stop at ready-for-human. An agent must never approve, merge, auto-merge, or
   otherwise cause the merge.

Use the [capability contract](../capability-contract.md) for fallback choices,
the [state machine](../state-machine.md) for lifecycle state, and the
[security and autonomy boundaries](../security-and-autonomy-boundaries.md) for
approval requirements.

## ChatGPT capability limits

Host capabilities can vary by workspace and configuration. Detect availability
instead of assuming a particular UI control, worktree feature, subagent mode,
or GitHub integration. A missing capability does not justify new repository
infrastructure: follow the portable fallback in the capability contract and
record the decision durably.
