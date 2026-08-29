# OpenAI host reference

This reference maps the repository's portable methodology to OpenAI-host
capabilities. It does not replace the canonical Skills or grant additional
authority.

| Semantic guarantee | Codex / ChatGPT implementation | Adapter boundary |
| --- | --- | --- |
| Planning | Use the host's native plan and preserve the required plan fields in the GitHub Issue or PR. | This plugin supplies the portable planning Skill; it does not add a planner. |
| Delegation | Use native subagents for bounded, independently reviewable tasks when available. | This plugin does not add an orchestration service. |
| Isolation | Use managed worktrees or another isolated branch/worktree supplied by the host. | This plugin does not manage worktrees. |
| Review | Use native review or a fresh-context reviewer. | This plugin supplies review criteria, not a review engine. |
| GitHub state | Use the available Git and GitHub integration to keep Issues, PRs, and CI current. | GitHub remains the durable control plane. |
| Testing and verification | Run repository-defined checks and record observed evidence. | This plugin does not invent commands or CI. |

Use the canonical [capability contract](../../docs/capability-contract.md) to
decide whether a host-native capability is sufficient and which portable
fallback applies. The shared [engineering workflow Skill](../../skills/engineering-workflow/SKILL.md)
preserves the human-only merge boundary: this adapter must never be interpreted
as authorization to merge a pull request.

## v1 exclusions

The manifest intentionally declares only `skills`. It has no MCP server,
app, hook, credential, or external-service configuration. Those components are
out of scope unless future evidence justifies them under the canonical plan.
