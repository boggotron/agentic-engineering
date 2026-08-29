---
name: designing-changes
description: Design a proposed engineering change before implementation when ambiguity, consequences, or system impact need an explicit, durable decision.
---

# Designing changes

Use this Skill after understanding the request and before planning or
implementation when the change has material ambiguity, meaningful alternatives,
or consequential effects. Its outcome is a proportionate, durable design
decision—not an implementation plan or a replacement for the host's planning
facilities.

## Decide whether design work is needed

First inspect the issue or request, relevant repository context, constraints,
and dependencies. Treat ambiguity as material when resolving it could change
scope, correctness, architecture, security, data handling, migration,
compatibility, operations, or the verification approach. Resolve it through
design work before implementation, or record a blocker with its unblock
condition.

For a trivial, well-understood change, explicitly record why architecture
ceremony is unnecessary and proceed directly to an appropriately small plan.
This bypass does not waive the need for clear scope, acceptance criteria, or
verification.

## Produce a proportionate design

State the selected approach, its rationale, relevant constraints, architecture
impact, and testable acceptance criteria. Assess security, data, migration,
compatibility, and operational effects when they apply; mark each inapplicable
area as such with a short rationale.

For a consequential decision, compare the meaningful alternatives, including
their trade-offs and why the selected approach is preferred. Do not create a
comparison merely to add ceremony when there is no credible alternative.

Record material decisions, assumptions, unresolved risks, and blockers in the
durable work record required by the project (normally the linked issue or its
approved design artifact). Keep ephemeral session notes from being the sole
record of a decision that affects implementation.

## Hand off to planning

The design is ready for planning when its selected approach is clear enough that
no unresolved decision could materially invalidate implementation, and its
acceptance criteria make the intended result observable. If later work changes
the design materially, update the durable record and revisit planning before
implementation continues.
