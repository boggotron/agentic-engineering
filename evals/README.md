# Cross-agent behavioral evaluations

This directory evaluates whether an agent preserved the repository's portable
engineering methodology. It evaluates semantic outcomes, not matching host
commands or tool calls. The scenario catalog covers the ten v0.1 scenarios
required by the [cross-platform repository plan](../docs/CROSS_PLATFORM_REPO_PLAN.md#9-evaluation-strategy).

## Run an evaluation

An evaluator records one observation for every catalog scenario. Each
`semantic` object must contain every named check with a boolean result.
`host_mechanics` is optional descriptive evidence (for example, the native
worktree facility or portable fallback selected); it is never scored.

```sh
python3 evals/run.py --results evals/examples/compliant.json
python3 evals/run.py --results path/to/observations.json --json
```

The runner exits zero only when semantic checks pass at least the catalog's
90% target. It exits nonzero for a below-target result or invalid/incomplete
observations. The denominator is the complete set of semantic checks across
all ten scenarios, so partial compliance is visible without treating a
host-specific implementation detail as a behavioral failure.

## Evaluation protocol

1. Give the scenario prompt to the host/agent under evaluation and retain its
   response or durable work evidence.
2. A human or independent evaluator records pass/fail for each semantic check
   from that evidence. Do not infer a pass from a plausible claim.
3. Record mechanics separately only to explain the host capability or fallback
   used. A different adequate native tool is not a failure.
4. Run the harness and attach the input, report, and any deliberate limitations
   to the relevant Issue or PR.

The catalog is data rather than an automated language judge: it keeps the
normative rubric inspectable and lets different hosts be evaluated fairly.

## Verify the harness

```sh
python3 -m unittest evals/test_run.py
```

The tests prove all ten scenarios are required, a fully compliant observation
passes, host-mechanics changes do not affect compliance, and a semantic result
below 90% fails.
