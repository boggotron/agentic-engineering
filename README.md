# agentic-engineering

A portable engineering methodology for taking repository work from a GitHub
Issue to a human-ready pull request. It is delivered as nine shared Agent
Skills with thin Codex/ChatGPT and Claude Code adapters. The Skills preserve a
common lifecycle while each host uses its own planning, delegation, isolation,
review, Git, and testing capabilities.

## What this provides

The canonical [`skills/`](skills/) directory contains nine focused Skills:

- `engineering-workflow` — lifecycle controller for Issue-to-PR work;
- `designing-changes` and `planning-implementation` — design and
  dependency-aware planning;
- `executing-tasks`, `testing-changes`, and `debugging-systematically` —
  implementation and investigation;
- `reviewing-changes`, `verifying-completion`, and `finishing-work` —
  independent review and evidence-based completion.

The repository deliberately distributes methodology and thin adapters; it is
not an autonomous engineering service or a replacement orchestration system.
The Codex/ChatGPT adapter is a local Skills plugin, and the Claude Code adapter
packages the same shared Skills for local loading. v1 has no MCP server, hooks,
apps, custom worktree manager, review engine, or project-state database. MCP
and hooks are future-only: introduce either only after documented evidence
establishes that native capabilities and portable fallbacks cannot meet a
material need.

## Install

Clone the full repository; neither adapter supports copying its adapter
directory on its own. Both rely on the canonical [`skills/`](skills/) content.

### Codex or ChatGPT

From the repository root, add the included local marketplace and install the
plugin:

```sh
codex plugin marketplace add "$PWD/adapters/openai"
codex plugin add agentic-engineering@agentic-engineering
codex plugin list --marketplace agentic-engineering
```

Start a new Codex or ChatGPT work thread, then invoke `engineering-workflow`
for Issue-based work. To remove this local installation later:

```sh
codex plugin remove agentic-engineering@agentic-engineering
codex plugin marketplace remove agentic-engineering
```

For a clean-install procedure, expected output, and troubleshooting, see the
[Codex/ChatGPT adapter installation guide](adapters/openai/INSTALL.md) and the
[Codex host guide](docs/host-guides/codex.md).

### Claude Code

From the repository root, package the shared Skills and start Claude Code with
the resulting local plugin:

```sh
python3 adapters/claude/scripts/check_shared_content.py
python3 adapters/claude/scripts/package_plugin.py --output /tmp/agentic-engineering-claude
claude --plugin-dir /tmp/agentic-engineering-claude
```

Inside Claude Code, confirm the Skill is available with `/help`, then invoke
`/agentic-engineering:engineering-workflow`. This is intentionally a local
plugin path: v1 does not publish a persistent Claude Code marketplace package.
On Claude Code versions that support it, you can validate the package before
starting Claude Code:

```sh
claude plugin validate /tmp/agentic-engineering-claude
```

See the [Claude Code adapter guide](adapters/claude/README.md) and [Claude
Code host guide](docs/host-guides/claude-code.md) for verification and
debugging.

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
records the capability-level equivalences and intentional deviations. The
[v0.1 release-readiness gate](docs/v0.1-release-readiness.md) records the
current candidate evidence and any remaining release blockers.

## Repository layout

```text
skills/             Canonical portable Skill content
adapters/openai/    Skills-only Codex and ChatGPT distribution adapter
adapters/claude/    Claude Code packaging adapter
docs/host-guides/   Host-specific quickstarts
docs/               Shared methodology, state, contract, and policy
```
