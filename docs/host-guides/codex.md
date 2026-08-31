# Codex host guide

Use the OpenAI adapter to load the shared Skills in Codex. The adapter provides
methodology only: it does not add an MCP server, hook, app, planner, worktree
manager, review engine, or GitHub state store. Those v1 exclusions are
intentional; MCP and hooks are future-only and need evidence of a material gap
before they are proposed.

## Install the local plugin

Keep a complete checkout of this repository. The adapter's `skills` directory
is a relative symbolic link to the canonical repository-level `skills/`
directory, so installing a copied `adapters/openai/` directory is unsupported.

From a checkout, substitute the absolute path to its `adapters/openai`
directory for `<adapter-path>`:

```sh
codex plugin marketplace add <adapter-path>
codex plugin add agentic-engineering@agentic-engineering
```

Start a new Codex thread after installation, then invoke an appropriate Skill
for the current stage. The complete clean-install procedure and expected
installation checks are in the [OpenAI adapter installation guide](../../adapters/openai/INSTALL.md).

## Run an Issue workstream

1. Start from the GitHub Issue, not a chat-only task. Confirm its objective,
   scope, non-goals, dependencies, acceptance criteria, and verification.
2. Invoke `engineering-workflow` to coordinate the lifecycle. Use a downstream
   Skill only for the active stage, such as `planning-implementation` before
   code changes or `reviewing-changes` after implementation.
3. Detect and prefer Codex-native planning, bounded subagents, managed
   worktrees, review, Git/GitHub access, and shell testing when they satisfy
   the [capability contract](../capability-contract.md). If a required native
   capability is unavailable, use the documented portable fallback and record
   the limitation in the Issue or PR.
4. Before write-heavy work, establish a managed worktree or another isolated
   branch/worktree. Serialize overlapping writes; independent bounded work may
   be delegated in parallel.
5. Update the Issue and linked PR with material decisions, blockers, review,
   CI, and observed verification. A fresh-context reviewer or adequate native
   review is required where practical.
6. Set the work to ready for human review only after the evidence gate passes.
   Do not approve or merge the PR: approval and merge are human-only.

The [workflow state machine](../state-machine.md) defines the durable GitHub
states, and the [security and autonomy boundaries](../security-and-autonomy-boundaries.md)
define what actions require human approval.
See the [workflow examples](../workflow-examples.md) for concise feature,
debugging, and review paths.

## Verify an adapter change

Use the verification procedure in [INSTALL.md](../../adapters/openai/INSTALL.md),
including its optional plugin validator when the plugin-creator Skill is
available. That validator checks the manifest and linked Skill manifests; it
does not prove remote marketplace behavior for symbolic links.
