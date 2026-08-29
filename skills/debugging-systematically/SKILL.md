---
name: debugging-systematically
description: Investigate and correct a reproducible defect through evidence, causal reasoning, and regression verification; use for failures, regressions, and unexpected behavior rather than speculative fixes.
---

# Debugging systematically

Use this Skill to turn an observed failure into a verified correction. Preserve
the distinction between observations, hypotheses, and conclusions. Do not
change code, configuration, data, or dependencies merely to make a symptom
disappear before the causal explanation is adequately supported.

## Establish the failure

1. State the expected and actual behavior, affected boundary, observable
   failure signal, and impact. Preserve the original report or a durable link to
   it when it is material.
2. Reproduce the failure with the smallest reliable procedure. Record inputs,
   relevant environment and state, observed output, and whether reproduction is
   deterministic, intermittent, or not yet achieved.
3. If the failure cannot be reproduced, do not claim a fix. Gather the most
   useful additional evidence, such as logs, traces, timestamps, versions,
   configuration, state transitions, or a comparison with a known-good case.
   Record the limit and the next condition needed to reproduce it.

## Gather and reason from evidence

Collect evidence along the execution path before selecting a remedy. Narrow the
failure boundary by comparing successful and failing cases, inspecting relevant
state and contracts, and checking recent or meaningful changes. Prefer direct
observation over assumptions, and preserve evidence that would let another
reviewer repeat the reasoning.

Form one or more falsifiable hypotheses that explain the observed behavior.
For each hypothesis, identify the prediction that would distinguish it from the
alternatives, then run the smallest safe experiment that can test that
prediction. Change one causal variable at a time where practical; avoid bundled
experiments that make the result ambiguous.

Revise or discard hypotheses when evidence contradicts them. A correlation,
mitigation, or passing retry is not a root cause unless it explains why the
failure occurs and is supported by the evidence.

## Correct the cause

Identify the root cause in terms of the violated behavior, contract, state, or
assumption—not only the location where the symptom surfaced. Confirm that the
proposed correction addresses that cause and consider nearby paths that share
it.

Apply the minimum correction that restores the intended behavior without
unrelated cleanup, broad rewrites, or weakened checks. If a larger change is
required, record why the smaller correction is insufficient and return to
design or planning when the scope or risk materially changes.

For a deterministic defect, add or update a regression check that fails for the
original behavior and passes with the correction. When such a check is not
practical, record the reason and use the strongest available repeatable
verification, including the original reproduction procedure where possible.

## Verify and record

Run the regression check and all relevant validation for the affected boundary.
Repeat the original reproduction procedure and verify both that the failure no
longer occurs and that expected behavior remains intact. For intermittent
failures, use an observation window or repeated trials proportionate to the
risk; state the coverage and residual uncertainty rather than treating a single
pass as proof.

Before completion, record durable evidence in the work item's normal tracking
location:

- the failure and reproduction status;
- evidence considered and hypotheses tested;
- root cause and minimum correction;
- regression coverage or the documented exception;
- commands or procedures run, observed results, and unavailable checks with
  rationale; and
- remaining risk, follow-up work, or an explicit unblock condition.

Use the host's available issue, review, and verification capabilities to retain
that record. This Skill requires those outcomes, not any particular tool,
command, or host-specific workflow.
