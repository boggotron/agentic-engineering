# Install and clean-install verification

## Prerequisites

Use a complete checkout of this repository. The plugin's `skills` path is a
relative symbolic link to the canonical repository-level `skills/` directory,
so copying only `adapters/openai/` is not a supported installation method.

The commands below use a repository-local marketplace. They do not create or
edit a personal marketplace. Substitute the absolute path to this checkout's
`adapters/openai` directory for `<adapter-path>`.

## Install

```sh
codex plugin marketplace add <adapter-path>
codex plugin add agentic-engineering@agentic-engineering
```

Start a new Codex or ChatGPT work thread after installation so the host can
load the newly installed Skills.

## Clean-install procedure

Run this sequence in a disposable Codex configuration or after removing a
previous installation:

```sh
codex plugin remove agentic-engineering@agentic-engineering
codex plugin marketplace remove agentic-engineering
codex plugin marketplace add <adapter-path>
codex plugin list --marketplace agentic-engineering --available
codex plugin add agentic-engineering@agentic-engineering
codex plugin list --marketplace agentic-engineering
```

The first two commands can report that nothing is installed or configured; in
that case continue with the add/list/install steps. Successful listing must
show the `agentic-engineering` plugin, and successful installation must mark it
installed. Test in a new thread by invoking one of the listed Skills.

## Verify the source package before installation

```sh
python3 <plugin-creator-skill-root>/scripts/validate_plugin.py <adapter-path>
```

Run this optional development check when the Codex plugin-creator Skill is
available. It checks the OpenAI plugin manifest and every linked canonical
Skill manifest. It does not prove how a future remote marketplace snapshot will
handle symbolic links; retain the full-checkout installation boundary described
above.
