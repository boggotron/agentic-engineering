# Repository Instructions for Agents

This thin entry point records repository-specific constraints. The normative
sources are the [methodology](docs/methodology.md), [security and autonomy
boundaries](docs/security-and-autonomy-boundaries.md), and [capability
contract](docs/capability-contract.md); their ranked handling is defined in
[instruction precedence](docs/instruction-precedence.md). Do not copy or fork
that shared guidance into repository instruction files.

## Scope and durable state

- Treat GitHub Issues, pull requests, and CI as the durable record of work.
- Keep an implementation issue and its linked pull request current as work
  progresses.
- Do not merge pull requests. A human performs the merge after the work is
  ready for review.

## Current commands

The authoritative repository commands are listed in the
[command inventory](docs/command-inventory.md). Run these exact commands for
all repository changes:

```sh
python scripts/test_validate_repository.py
python scripts/validate_repository.py
```

For documentation-only changes, the applicable checks are:

```sh
git status --short
rg --files -g '*.md'
```

The repository validator checks relative Markdown links and heading fragments.
For documentation-only changes, supplement that automated coverage with a
manual review of changed headings, links, and rendered readability. Record the
exact checks run and any intentionally unavailable checks in the pull request
evidence.

## Documentation conventions

- Write portable Markdown and use relative links for repository documents.
- Keep links to planned artifacts clearly labelled as planned when they do not
  yet exist.
- Preserve the separation between shared Skills and thin host-specific
  adapters described by the normative sources.

## Working conventions

Follow the lifecycle in the [methodology](docs/methodology.md), the authority
boundaries in the [security and autonomy
boundaries](docs/security-and-autonomy-boundaries.md), and the host selection
rules in the [capability contract](docs/capability-contract.md). Use the host's
native facilities where available; this repository does not provide substitute
orchestration, worktree, review, or project-state tooling.
