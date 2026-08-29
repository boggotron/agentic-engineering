# OpenAI adapter

This is the v1, skills-only OpenAI distribution of
[agentic-engineering](../../README.md). It supplies the shared methodology to
Codex and ChatGPT without adding MCP servers, apps, hooks, orchestration, or
another project-state system.

## Canonical source relationship

`skills` is a relative symbolic link to the repository's canonical
[`skills/`](../../skills/) directory. The adapter therefore loads these nine
Skills without copying or forking their behavioral content:

- `engineering-workflow`
- `designing-changes`
- `planning-implementation`
- `executing-tasks`
- `testing-changes`
- `debugging-systematically`
- `reviewing-changes`
- `verifying-completion`
- `finishing-work`

The plugin validator resolves the link and validates every referenced
`SKILL.md`. Keep this adapter in a full repository checkout: a packaging tool
that copies only `adapters/openai/` without preserving its relative symbolic
link cannot load the shared Skills. Such a distribution is unsupported until a
format that can safely reference repository-level Skill sources is available.

See [installation and clean-install verification](INSTALL.md) and the
[OpenAI host reference](HOST_REFERENCE.md).
