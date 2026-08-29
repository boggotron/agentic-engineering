# ADR 0001: Use portable Agent Skills as the canonical methodology abstraction

- Status: Accepted
- Date: 2026-08-29
- Related: [canonical methodology](../methodology.md), GitHub Issue #2

## Context

The repository must provide one engineering methodology across Codex, ChatGPT,
and Claude Code. These hosts differ in their planners, subagent orchestration,
isolation mechanisms, review features, Git integrations, and release workflows.
Encoding those mechanisms in the methodology would either require custom
infrastructure or create divergent host-specific processes.

The methodology needs a portable unit that can state behavioral requirements while
letting each host use its own capabilities. It must preserve durable GitHub state,
evidence before completion, independent review, and the human-only merge boundary.

## Decision

The canonical methodology SHALL be authored as portable Agent Skills. Core Skill
content defines semantic guarantees and lifecycle criteria, not host-specific
commands or tool APIs.

OpenAI and Claude distributions SHALL consume the same canonical Skill sources as
far as their formats permit. Host-specific packaging, setup instructions, and
capability mappings belong in thin adapters or reference material. A host MAY use
native planning, worktrees, subagents, review, Git/GitHub integration, and testing
tools when they meet the relevant semantic requirement.

GitHub Issues, PRs, reviews, and CI remain the durable control plane; sessions
and agent context remain ephemeral. No adapter may grant agents authority to merge.

## Consequences

### Positive

- The methodology remains substantially shared across supported hosts.
- Hosts can improve native capabilities without requiring a methodology rewrite.
- The repository avoids duplicating worktree managers, schedulers, review engines,
  and project-state databases.
- Evaluation can assess behavior and evidence rather than identical tool calls.

### Trade-offs

- Adapters must explain how each host meets the portable contract.
- Capability differences can require documented fallbacks or intentional
  deviations.
- Instruction-level methodology may need future structural enforcement only if
  evidence shows repeated non-compliance.

## Alternatives considered

### A custom cross-host orchestration service

Rejected for v1. It duplicates increasingly capable host-native functions and
adds operational burden without improving the required semantic guarantees.

### Separate methodology forks for each host

Rejected. Forks increase drift and make behavior parity difficult to evaluate.
Host-specific mechanics are narrower than the shared process and belong in
adapters.

### A monolithic repository instruction file

Rejected. It prevents progressive disclosure and mixes portable methodology with
repository-local facts. Skills are composable and are the appropriate behavioral
unit.

## Compliance

New core methodology content MUST be host-neutral. A reference to a concrete host
tool is permitted only in an adapter or host guide and MUST describe it as one way
to satisfy a semantic guarantee, not as a mandatory mechanism.
