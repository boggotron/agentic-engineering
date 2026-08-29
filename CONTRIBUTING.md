# Contributing to agentic-engineering

Thanks for contributing. This repository is building portable engineering
Skills and their thin host adapters. The intended structure and the canonical
cross-host methodology are documented in the
[cross-platform repository plan](docs/CROSS_PLATFORM_REPO_PLAN.md).

## Before you start

Start with a GitHub Issue. Issues are the durable record for the objective,
scope, dependencies, acceptance criteria, and verification requirements. If
the work is not ready to implement, improve the Issue first rather than relying
on chat history or a local note.

Check dependencies before starting. For the project dependency graph and the
meaning of lifecycle states, use the [implementation program](docs/CROSS_PLATFORM_REPO_PLAN.md#7-implementation-program-and-dependency-graph)
and [GitHub Issues state machine](docs/CROSS_PLATFORM_REPO_PLAN.md#4-github-issues-state-machine).

## Preparing a change

Use a focused branch and keep each pull request scoped to its linked Issue.
Make commits that explain the change in imperative language. Keep generated,
unrelated, and local-environment changes out of the pull request.

The repository does not currently define automated lint, test, build, or eval
commands. Until it does, use the checks that are applicable to the change and
state unavailable automated checks as `N/A` with a short justification. For
documentation changes, verify Markdown headings and relative links manually.

## Pull requests

Open or update a pull request only when it links the implementation Issue and
contains enough evidence for another person to reproduce the result. Include:

- the linked Issue (for example, `Closes #123`);
- a concise implementation summary;
- each acceptance criterion and its outcome;
- exact test and verification commands, their results, and justified `N/A`
  checks;
- independent-review status and any resolved findings;
- known risks or follow-up work; and
- `Human merge required: YES`.

Keep the Issue and pull request state current while work progresses. A change
is ready for a human only after the verification and review requirements in the
[Definition of Ready for Human](docs/CROSS_PLATFORM_REPO_PLAN.md#definition-of-ready-for-human)
are satisfied. Contributors and agents must not merge pull requests.

## Documentation contributions

Use clear, portable Markdown. Prefer repository-relative links, and check that
each link target and fragment resolves in the current checkout. Keep shared
methodology in canonical Skills and shared documentation; host adapters should
only explain how a host meets that shared contract.
