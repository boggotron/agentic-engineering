# Repository Instructions for Agents

This file records repository-specific constraints. The portable engineering
methodology, lifecycle, and host-capability guidance are canonical in the
[cross-platform repository plan](docs/CROSS_PLATFORM_REPO_PLAN.md). Do not
copy or fork that methodology into repository instruction files.

## Scope and durable state

- Treat GitHub Issues, pull requests, and CI as the durable record of work.
- Keep an implementation issue and its linked pull request current as work
  progresses.
- Do not merge pull requests. A human performs the merge after the work is
  ready for review.

## Current commands

The repository currently has no package manifest or automated lint, test,
build, or evaluation command. Do not invent command names or report an
unexecuted command as passing.

For documentation-only changes, run checks that are available in the checkout:

```sh
git status --short
rg --files -g '*.md'
```

Validate changed relative Markdown links and headings manually until a
repository validation command is added. Record the exact checks run and any
intentionally unavailable checks in the pull request evidence.

## Documentation conventions

- Write portable Markdown and use relative links for repository documents.
- Keep links to planned artifacts clearly labelled as planned when they do not
  yet exist.
- Preserve the separation between shared Skills and thin host-specific
  adapters described in the canonical plan.

## Working conventions

Follow the lifecycle, isolation, review, verification, and human-approval
requirements in the [canonical plan](docs/CROSS_PLATFORM_REPO_PLAN.md).
Use the host's native facilities where available; this repository does not
provide substitute orchestration, worktree, review, or project-state tooling.
