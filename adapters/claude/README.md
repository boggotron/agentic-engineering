# Claude Code adapter

This directory is the thin Claude Code packaging adapter for the shared
repository [Skills](../../skills/). It supplies Claude Code metadata and
packaging only; the engineering methodology remains canonical in the shared
Skills and repository documentation.

## Why package during installation

Claude Code only preserves plugin symlinks that resolve within the plugin
directory. A committed link from this adapter to `../../skills/` would
therefore be skipped when the plugin is loaded from a local path. The packager
creates a self-contained plugin directory whose Skill files are byte-identical
copies of the shared source at package time. It does not introduce a
Claude-specific methodology fork.

The package layout is deterministic: `.claude-plugin/` and `skills/` are
copied from their canonical sources, and transitive local Markdown dependencies
are copied below `docs/`. Skills remain byte-identical to their canonical
sources; only copied documentation links are rewritten for the package layout.

Author Skills and repository documentation in their canonical locations. Do not
edit a generated package as a source of truth. The
[shared-content check](scripts/check_shared_content.py) packages into a
temporary directory, validates its exact files, SHA-256 digests, and local
Markdown links, then proves that generated `SKILL.md` files are identical to
the shared source. It reports both a file and byte coverage percentage; the
required threshold is 90%, and the expected result is 100%.

## Local development and clean-install check

Prerequisite: a current, authenticated Claude Code installation. The commands
below use Claude Code's documented local-plugin loading mechanism and do not
require a marketplace, MCP server, hook, or repository-specific Claude command.

From a clean clone of this repository:

```sh
python3 adapters/claude/scripts/check_shared_content.py
python3 adapters/claude/scripts/package_plugin.py --output /tmp/agentic-engineering-claude
claude plugin validate /tmp/agentic-engineering-claude
```

To perform an interactive clean-install check, start a fresh Claude Code session
with the generated package:

```sh
claude --plugin-dir /tmp/agentic-engineering-claude
```

For a noninteractive clean-install smoke check, require the controller to
consult both packaged canonical references:

```sh
claude --plugin-dir /tmp/agentic-engineering-claude --no-session-persistence --print 'Use the agentic-engineering:engineering-workflow controller and its linked canonical methodology and capability contract. Reply in exactly two lines: first, the lifecycle stage immediately after PLAN; second, what to select if a native capability is missing or insufficient.'
```

Inside Claude Code, use `/help` to confirm the namespaced Skills are present,
then invoke one, for example:

```text
/agentic-engineering:engineering-workflow
```

If validation or loading reports an error, use the following and retain the
observed output in the linked Issue or pull request:

```sh
claude --debug --plugin-dir /tmp/agentic-engineering-claude
```

The `--plugin-dir` invocation is intentionally a local development and
verification path. Marketplace distribution is not part of this adapter; it
would require a release artifact or marketplace configuration that preserves
the generated, self-contained package.

For the native-plugin layout and local loading behavior, see the
[Claude Code plugin documentation](https://code.claude.com/docs/en/plugins)
and [plugin reference](https://code.claude.com/docs/en/plugins-reference).
