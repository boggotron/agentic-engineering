# agentic-engineering

Portable Agent Skills for carrying repository work from a GitHub Issue to a
human-ready pull request. The Skills preserve a common engineering lifecycle
across Codex, ChatGPT, and Claude Code while letting each host use its native
planning, delegation, isolation, review, Git, and testing capabilities.

## What this provides

The canonical [`skills/`](skills/) directory contains nine focused Skills:

- `engineering-workflow` — lifecycle controller for Issue-to-PR work;
- `designing-changes` and `planning-implementation` — design and
  dependency-aware planning;
- `executing-tasks`, `testing-changes`, and `debugging-systematically` —
  implementation and investigation;
- `reviewing-changes`, `verifying-completion`, and `finishing-work` —
  independent review and evidence-based completion.

The repository deliberately distributes thin adapters, not a replacement
orchestration system. The OpenAI adapter is a skills-only local plugin; the
Claude adapter packages the same shared Skills for local loading. v1 has no
MCP server, hooks, apps, custom worktree manager, review engine, or project
state database. MCP and hooks are future-only: introduce either only after
documented evidence establishes that native capabilities and portable fallbacks
cannot meet a material need.

## Start here

1. Read the [canonical methodology](docs/methodology.md) and
   [capability contract](docs/capability-contract.md).
2. Choose the guide for your host:
   [Codex](docs/host-guides/codex.md), [ChatGPT](docs/host-guides/chatgpt.md),
   or [Claude Code](docs/host-guides/claude-code.md).
3. Start meaningful engineering work from a GitHub Issue and use the
   `engineering-workflow` Skill to establish scope, dependencies, and
   verification before writing.

## The workflow in brief

GitHub Issues, pull requests, reviews, and CI are the durable work record;
conversation and local plans are not. For every material workstream:

1. Confirm the Issue is ready, including scope, non-goals, dependencies,
   acceptance criteria, and verification.
2. Use the host's native capability first. If it cannot preserve the required
   guarantee, use the narrowest portable fallback and record the limitation in
   the Issue or PR.
3. Create an isolated write context before implementation. Parallelize only
   bounded work with independent write sets.
4. Implement, test as applicable, obtain independent fresh-context review,
   and record observed verification and CI evidence in the linked PR.
5. Stop at `state:ready-for-human`. Only a human may approve and merge the PR.

See the [GitHub workflow state machine](docs/state-machine.md),
[security and autonomy boundaries](docs/security-and-autonomy-boundaries.md),
[contribution guide](CONTRIBUTING.md), and [workflow examples](docs/workflow-examples.md)
for the complete requirements. The [Superpowers parity review](docs/superpowers-parity.md)
records the capability-level equivalences and intentional deviations.

## Repository layout

```text
skills/             Canonical portable Skill content
adapters/openai/    Skills-only Codex and ChatGPT distribution adapter
adapters/claude/    Claude Code packaging adapter
docs/host-guides/   Host-specific quickstarts
docs/               Shared methodology, state, contract, and policy
```
