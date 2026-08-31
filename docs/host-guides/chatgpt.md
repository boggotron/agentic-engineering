# ChatGPT host guide

The OpenAI adapter is the supported shared-Skills distribution for ChatGPT and
Codex. It changes neither the engineering lifecycle nor the authority boundary:
GitHub Issues, pull requests, reviews, and CI remain the durable work record,
and human approval and merge remain mandatory.

## Install and verify the shared Skills

The local plugin is in [`adapters/openai`](../../adapters/openai/). Keep a
complete repository checkout: its `skills` directory is a relative symbolic
link to the canonical repository-level `skills/` directory, so copying only
`adapters/openai/` is unsupported.

The supported installation route is the Codex plugin CLI. Substitute the
absolute path to this checkout's `adapters/openai` directory for
`<adapter-path>`:

```sh
codex plugin marketplace add <adapter-path>
codex plugin list --marketplace agentic-engineering --available
codex plugin add agentic-engineering@agentic-engineering
codex plugin list --marketplace agentic-engineering
```

The available-plugin listing must include `agentic-engineering`; after the add
command, the marketplace listing must mark it installed. Start a new ChatGPT
work thread after that installation and use `engineering-workflow` for an
Issue-based workstream. The full clean-install and removal procedure is in the
[OpenAI adapter installation guide](../../adapters/openai/INSTALL.md).

The adapter contains Skills only. It includes no MCP server, hooks, apps,
credentials, orchestration service, or project-state database. MCP and hooks
are intentionally future-only rather than prerequisites for a ChatGPT
workflow.

## Run a durable workflow

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
approval requirements. The [workflow examples](../workflow-examples.md) show
the same durable flow for feature, debugging, and review work.

## ChatGPT capability limits

Host capabilities can vary by workspace and configuration. Detect availability
instead of assuming a particular UI control, worktree feature, subagent mode,
or GitHub integration. A missing capability does not justify new repository
infrastructure: follow the portable fallback in the capability contract and
record the decision durably.
