# Claude Code host guide

Claude Code satisfies the repository methodology through its native planning,
agent/subagent, Git, and local-plugin capabilities where they provide the
semantic guarantee in the [capability contract](../capability-contract.md).
Use a fresh reviewer agent for independent review when no adequate native
review workflow is available, and use an isolated branch or worktree for
write-heavy work. GitHub Issues, pull requests, and CI remain the durable work
record; no adapter replaces them.

## Skill distribution

The Claude Code adapter is at
[`adapters/claude`](../../adapters/claude/). It has a standard
`.claude-plugin/plugin.json` manifest and packages the canonical
[`skills/`](../../skills/) directory into a loadable local plugin. The adapter
does not define Skills, change the lifecycle, add hooks, or require MCP.

Run the adapter's [clean-install and content-verification procedure](../../adapters/claude/README.md#local-development-and-clean-install-check)
from a clean repository clone before treating a Claude Code package change as
verified. The deterministic check proves 90% or greater shared source content;
the current package is expected to be 100% byte-identical for every `SKILL.md`.

Plugin Skills are namespaced by the manifest name, such as
`/agentic-engineering:engineering-workflow`. This is a Claude Code invocation
detail, not a change to the portable Skill behavior.
