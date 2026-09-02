# Contributing to agentic-engineering

Thanks for contributing. This repository is building portable engineering
Skills and their thin host adapters. The [cross-platform repository
plan](docs/CROSS_PLATFORM_REPO_PLAN.md) is historical roadmap material; current
shared rules are the [methodology](docs/methodology.md), [security and autonomy
boundaries](docs/security-and-autonomy-boundaries.md), and [capability
contract](docs/capability-contract.md), interpreted through [instruction
precedence](docs/instruction-precedence.md).

## Before you start

Start with a GitHub Issue. Issues are the durable record for the objective,
scope, dependencies, acceptance criteria, and verification requirements. If
the work is not ready to implement, improve the Issue first rather than relying
on chat history or a local note.

Check dependencies before starting. For the project dependency graph and the
meaning of lifecycle states, use the [implementation program](docs/CROSS_PLATFORM_REPO_PLAN.md#7-implementation-program-and-dependency-graph)
and the [GitHub workflow state machine](docs/state-machine.md).

Use the Engineering work Issue template for new implementation work. Apply one
lifecycle label and update it as the work moves through the documented entry and
exit criteria. When work is blocked, record the specific blocker and its unblock
condition instead of leaving the state ambiguous.

## Preparing a change

Use a focused branch and keep each pull request scoped to its linked Issue.
Make commits that explain the change in imperative language. Keep generated,
unrelated, and local-environment changes out of the pull request.

Run the exact repository validation commands documented in the
[command inventory](docs/command-inventory.md):

```sh
python scripts/test_validate_repository.py
python scripts/validate_repository.py
```

For documentation-only changes, also verify Markdown headings and relative
links manually, along with the applicable checkout checks:

```sh
git status --short
rg --files -g '*.md'
```

Follow the portable [security and autonomy boundaries](docs/security-and-autonomy-boundaries.md).
In particular, do not expose secrets, bypass required checks or branch
protection, perform external releases or deployments, or merge a pull request
without the required human approval.

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
[ready-for-human gate](docs/state-machine.md#transition-rules)
are satisfied. Contributors and agents must not merge pull requests.

## Documentation contributions

Use clear, portable Markdown. Prefer repository-relative links, and check that
each link target and fragment resolves in the current checkout. Keep shared
methodology in canonical Skills and shared documentation; host adapters should
only explain how a host meets that shared contract.
