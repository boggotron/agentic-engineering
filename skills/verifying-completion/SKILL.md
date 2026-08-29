---
name: verifying-completion
description: Verify an implemented change with observed, criterion-by-criterion evidence before CI and pull-request readiness.
---

# Verifying completion

Use this Skill after independent review and before declaring a workstream ready
for a human. It requires observed evidence for the completed change; it does
not replace project test commands, CI, or a human merge decision.

## Verify the final result

Start from the issue's acceptance criteria and the plan's stated verification.
For every criterion, run or perform the relevant check against the final change
and record the procedure, observed result, and pass/fail status. Re-run affected
checks after any material review or CI remediation; prior evidence does not
automatically cover a changed result.

Run and record applicable checks for the affected boundary, including:

- acceptance behavior and relevant regression checks;
- tests, lint, type checking, and build;
- security, dependency, privacy, migration, compatibility, performance,
  reliability, and observability checks when applicable; and
- documentation, configuration, generated-output, or manual checks where those
  are the relevant verification method.

Use project-defined commands and host-native capabilities where available. Do
not invent checks or report an expected result as observed. When a required
check is unavailable or inapplicable, record `N/A`, the reason, and the
strongest available alternative verification. An absent automated check is not
evidence of success.

## Record completion evidence

Place the evidence in the linked Issue and pull request so a human can assess
the final state without private context. Include the acceptance-criterion
matrix, exact commands or repeatable procedures, observed outputs or results,
environmental limits that matter, justified N/A outcomes, and known residual
risk or follow-up work. Link the final diff or revision when the durable system
does not already make it unambiguous.

Do not claim completion while any acceptance criterion fails, required check is
failing, verification is inconclusive, a blocking review finding remains, or a
material prerequisite is unresolved. Return to the appropriate earlier stage,
record the blocker and explicit unblock condition, then repeat affected review
and verification when the result changes.

Hand off to `finishing-work` only when the final observed evidence demonstrates
that all applicable criteria and checks pass or have a justified N/A status.
