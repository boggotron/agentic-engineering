# Agentic Engineering V2 architecture and workstream plan

**Status:** Finalized for pull-request review

**Scope:** Formal V1-to-V2 architecture, asset evaluation, and proposed Issue/Epic portfolio

**Decision boundary:** This document proposes work. It does not create Issues or Epics,
change repository policy, publish a plugin, or authorize implementation or merge. The
resolved decisions below become implementation authority only after a human reviews and
merges the pull request that adopts this plan.

## Executive summary

V1 establishes a strong portable methodology: GitHub is durable state, Skills hold
progressively disclosed workflow guidance, host-native capabilities are preferred,
verification must be observed, concurrent writes require isolation, and merge remains
human-only. Those foundations should remain.

V2 should turn that methodology into an enforceable, risk-adaptive assurance system.
The key architectural change is to distinguish three control classes:

1. **Judgment guidance** belongs in Skills: understanding, design, decomposition,
   debugging, qualitative review, and escalation reasoning.
2. **Machine-enforceable invariants** belong in schemas, policy checks, CI, rulesets,
   host permissions, hooks, budgets, and circuit breakers.
3. **Consequential decisions** remain human-owned: merge, production effects,
   destructive operations, security-policy changes, secret authority, and explicit
   acceptance of material residual risk.

The V2 target is not blind trust or maximum agent count. It is bounded autonomy whose
scope, evidence, cost, effects, and recovery path are visible and enforceable. A human
should receive a pull request only after the applicable deterministic gates pass,
independent review evidence exists, residual risk is explicit, and the final revision is
unambiguously tied to the evidence.

## Source basis

The recommendations in this plan are derived from the repository's V1 design and the
following primary or authoritative sources:

- [OpenAI Codex project instructions](https://developers.openai.com/codex/guides/agents-md/),
  [Skills](https://developers.openai.com/codex/skills/),
  [plugins](https://developers.openai.com/codex/plugins/),
  [hooks](https://developers.openai.com/codex/hooks/), and
  [subagents](https://developers.openai.com/codex/subagents/).
- [Claude Code memory](https://code.claude.com/docs/en/memory),
  [Skills](https://code.claude.com/docs/en/skills),
  [subagents](https://code.claude.com/docs/en/sub-agents),
  [hooks](https://code.claude.com/docs/en/hooks),
  [permissions](https://code.claude.com/docs/en/permissions),
  [worktrees](https://code.claude.com/docs/en/worktrees), and
  [scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks).
- [NIST Secure Software Development Framework 1.1](https://csrc.nist.gov/pubs/sp/800/218/final),
  the [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework),
  and its Generative AI profile.
- [OWASP ASVS 5.0](https://owasp.org/www-project-application-security-verification-standard/),
  [OWASP SAMM](https://owaspsamm.org/model/), and the
  [OWASP Top 10 for LLM and GenAI applications](https://genai.owasp.org/llm-top-10/).
- [SLSA 1.2](https://slsa.dev/spec/v1.2/),
  [OpenSSF Scorecard](https://scorecard.dev/), and
  [Sigstore](https://docs.sigstore.dev/) for supply-chain integrity and provenance.
- GitHub guidance for [CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners),
  [rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets),
  [Actions hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions),
  and code scanning.
- [OpenTelemetry](https://opentelemetry.io/docs/concepts/observability-primer/)
  for traces, metrics, and logs, and
  [Conventional Commits 1.0](https://www.conventionalcommits.org/en/v1.0.0/)
  for machine- and human-readable change history.
- Official project guidance for [Gitleaks](https://github.com/gitleaks/gitleaks),
  [OSV-Scanner](https://google.github.io/osv-scanner/),
  [Semgrep Community Edition](https://semgrep.dev/docs/),
  [Trivy](https://trivy.dev/docs/latest/), [Syft](https://github.com/anchore/syft),
  [zizmor](https://docs.zizmor.sh/), [actionlint](https://github.com/rhysd/actionlint),
  [OWASP ZAP](https://www.zaproxy.org/docs/), and
  [NVIDIA garak](https://github.com/NVIDIA/garak) informs the default-tool decision.

External standards must be version-pinned when converted into normative controls.
The framework should periodically review those pins without silently changing the
requirements for work already in progress.

## Prohibited policy claims and architecture regressions

The following ideas from the explanatory video must not become core policy. V2 evals
must contain negative scenarios that fail if an agent or Skill relies on them:

- A Skill can reduce variance but cannot guarantee that an agent will not hallucinate.
- An AI reviewer produces probabilistic evidence, not objective proof.
- A host's automatic permission mode is not universally safe and must not replace
  effect-based authority, least privilege, isolation, or human approval boundaries.
- A folder or project name is a context boundary, not write or security isolation.
- A maximum iteration count is only one part of resource and runaway-loop control.
- Recursive execution does not mean the underlying model learns or improves itself.
- “Acceptable at 80%” is not a sufficient automation rule. Consequence, reversibility,
  blast radius, verification strength, observability, data sensitivity, and recovery
  cost must govern automation.
- Agent count is not a maturity metric. More agents may increase cost, correlated
  error, conflict, and reviewer load.
- Implementer self-review cannot satisfy independent review.
- No process may claim to be secure against all known threats. Security claims must
  name the threat model, control set, version, evidence, limitations, and residual risk.

## V2 target architecture

```text
Human intent and approved scope
              |
              v
Repository facts and authority policy
              |
              v
Risk and capability classification -----> repository/risk control profile
              |                                      |
              v                                      v
Portable workflow Skills ----------------> required gates and budgets
              |                                      |
              v                                      v
Host-native orchestration -------------> isolation + scoped permissions
              |                                      |
              v                                      v
Implementation -------------------------> deterministic local checks
              |                                      |
              v                                      v
Independent review + conditional security/adversarial evaluation
              |
              v
Final-revision evidence bundle ---------> CI + repository rulesets
              |
              v
Ready for human review -----------------> human approval and human merge
```

### Layer 1: canonical policy and precedence

- `docs/methodology.md` becomes the single normative lifecycle source.
- `docs/security-and-autonomy-boundaries.md` remains the normative authority source.
- `docs/capability-contract.md` remains the host-neutral capability source.
- `AGENTS.md` and `CLAUDE.md` stay thin and contain only repository facts, current
  commands, instruction precedence, and links/imports to the canonical sources.
- `docs/CROSS_PLATFORM_REPO_PLAN.md` becomes an architecture history and roadmap,
  not a competing normative source.
- Every normative document declares an owner, version, review date, and precedence.

### Layer 2: risk and repository profiles

Every workstream is classified before planning. The classifier uses change type,
affected boundary, data and secret exposure, external effects, privilege, reversibility,
blast radius, compatibility, and verification strength. A conservative tie-breaker
selects the stricter applicable profile.

Proposed risk levels:

| Level | Typical example | Minimum treatment |
| --- | --- | --- |
| R0 | Typographical documentation correction | Focused review and document validation |
| R1 | Internal refactor with strong tests | Tests, lint/types/build, independent review |
| R2 | User-visible feature or dependency change | Full applicable checks, security triage, rollback assessment |
| R3 | Authentication, authorization, sensitive data, migration, CI or infrastructure | Threat model, security review, expanded tests, explicit human approval points |
| R4 | Production/destructive effect, security-control weakening, secret authority | Human authorization before action; tightly constrained execution or proposal-only |

Repository profiles select applicable controls without pretending every project needs
the same scanners. Initial profiles must cover documentation, general application,
web/API, library/package, infrastructure-as-code, container/service, data migration,
and AI-enabled systems. OWASP ASVS controls apply to relevant web/application surfaces;
NIST SSDF and supply-chain controls apply more broadly.

The initial operating model assumes one repository owner and only collaborators to whom
that owner deliberately grants access. Human-only merge and consequential-approval
boundaries still apply. CODEOWNERS, required-review counts, and separation-of-duty
controls should therefore scale with the number and trust level of collaborators rather
than pretending a larger organization already exists.

### Supported hosts, surfaces, and compatibility policy

V2 supports the surfaces through which this repository is expected to be used:

- Codex in T3 Code, the terminal CLI, the ChatGPT desktop app, and the web/cloud surface;
- ChatGPT in the desktop app and on the web; and
- Claude Code in the terminal, Claude desktop integration, and Claude Code on the web.

Versioned clients use a rolling **N/N-1** policy: certify the operator's installed stable
release and its immediately preceding stable release, making N-1 the minimum. A newer
upstream release is a canary until the compatibility suite passes; it does not silently
move the support floor. Continuously delivered web/cloud surfaces do not expose a stable
client version, so they are tested against the current service and gated by capability
detection. Missing optional capabilities must select a documented fallback or produce a
clear unsupported result; they must never weaken a required invariant.

The observed baseline on 2026-09-01 is:

| Surface | Installed/observed N | Minimum N-1 decision |
| --- | --- | --- |
| Codex CLI | `0.151.0` | `0.150.1` |
| Claude Code CLI | `2.1.236` | `2.1.235` |
| ChatGPT desktop for macOS | `26.825.41651` | Immediately preceding signed vendor build; record its exact build in the compatibility fixture before implementation |
| Claude desktop for macOS | `1.40609.0` | Immediately preceding signed vendor build; record its exact build in the compatibility fixture before implementation |
| T3 Code Alpha | `0.0.37` | `0.0.36`, if obtainable; otherwise `0.0.37` is the only certified alpha build and capability fallbacks are mandatory |
| Codex/ChatGPT/Claude Code web | Current service | Not semantically versioned; current-service contract tests |

At the snapshot date, package registries reported Codex CLI `0.152.0` and Claude Code
`2.1.252` as newer than the installed baselines. Updating operator software is outside
this plan's authority. P1-09 must test those releases as canaries and move N only through
a reviewed compatibility-matrix update. Desktop predecessor builds must not be guessed;
their signed artifact identity is a required discovery result.

### Layer 3: lifecycle and control-state machine

The V1 lifecycle remains recognizable but gains explicit classification, authorization,
and failure states:

```text
INTAKE -> CLASSIFY -> UNDERSTAND -> DESIGN -> PLAN -> AUTHORIZE -> ISOLATE
       -> IMPLEMENT -> LOCAL_VERIFY -> INDEPENDENT_REVIEW
       -> CONDITIONAL_SECURITY_REVIEW -> FINAL_VERIFY -> CI_PR
       -> READY_FOR_HUMAN -> HUMAN_APPROVAL -> HUMAN_MERGE

Any active state -> BLOCKED | BUDGET_EXHAUSTED | POLICY_DENIED | CANCELLED
Any changed final revision -> earliest affected review/verification state
```

Each transition has machine-readable entry criteria, required artifacts, actor/role,
allowed effects, exit criteria, and failure transitions. `READY_FOR_HUMAN` is derived
from evidence for one immutable revision; it is not a model-authored assertion.

### Layer 4: execution, isolation, and permissions

- Prefer host-native worktrees and sandboxes when they satisfy the capability contract.
- Treat concurrent writes as conflicting unless their isolated write sets and
  integration owner are explicit.
- Give delegated agents bounded objective, scope, inputs, output contract, allowed
  tools, risk/budget envelope, and handoff requirements.
- Apply effect-based permission controls outside model context. Prompt instructions
  supplement but never replace host enforcement.
- Connectors and MCP servers remain optional. Add one only for a demonstrated gap and
  document authentication, data flow, external effects, failure behavior, and least
  privilege.

### Layer 5: verification and independent evaluation

V2 uses a verification ladder:

1. **Structural validation:** manifests, schemas, links, package contents, policy files.
2. **Deterministic behavior:** format, lint, types, build, unit/integration/contract/E2E
   checks, and change-specific acceptance tests.
3. **Security and supply chain:** secret, SAST, dependency, license, IaC, container,
   SBOM, provenance, and other profile-selected controls.
4. **Independent model evaluation:** specification coverage, edge cases, architecture,
   maintainability, security reasoning, and test quality using a rubric and evidence.
5. **Human review:** consequential judgment and residual-risk acceptance.

Deterministic failure cannot be overruled by an AI grade. Critical invariants are
must-pass rather than components of an average score. Probabilistic grades include
confidence, evidence references, disagreement, and an escalation threshold.

#### Default open-source security tool baseline

The framework should standardize control outcomes and evidence formats, not make one
scanner irreplaceable. Defaults must be free/open-source, actively maintained,
non-interactive, locally or CI runnable, version-pinned, capable of machine-readable
output, and usable without uploading private source by default. Each adapter records the
tool, version, rules/database identity, configuration, coverage, exit status, findings,
and suppressions. Third-party CI code runs with least privilege and without unrelated
secrets; prefer a verified standalone binary or container pinned by digest over a
mutable action tag. Tool replacement is allowed when an equivalent control and evidence
contract is demonstrated.

| Scope | Default | Treatment |
| --- | --- | --- |
| All non-documentation code profiles | Gitleaks | Secret detection over the diff and applicable history; SARIF/JSON evidence; a finding triggers credential-rotation guidance rather than implying deletion alone repairs exposure. |
| Repositories with dependency manifests/lockfiles | OSV-Scanner | Known-vulnerability and dependency-license evidence from supported ecosystems; policy distinguishes fixable, unfixable, disputed, and accepted findings. |
| Supported source languages | Semgrep Community Edition | Local SAST with version-pinned, license-reviewed rules checked into or digest-locked by the repository; no mandatory cloud account or source upload. Language-native analyzers may supplement or replace it when their coverage is stronger. |
| GitHub Actions present | actionlint and zizmor | Syntax/semantic workflow validation plus security analysis; run offline unless an explicitly approved online audit is required. |
| Infrastructure-as-code or container/service | Trivy | Misconfiguration and image/filesystem vulnerability scanning. Execute a pinned binary/container in a read-only, no-secret job; do not rely on a mutable third-party action reference. |
| Releasable package, plugin, service, or image | Syft | CycloneDX JSON and/or SPDX JSON SBOM generation. V2 defines the evidence contract; P1-03 activates release generation and attestation immediately after V2. |
| Runnable web/API service | OWASP ZAP Baseline | Passive baseline against an authorized disposable/test target. Active scanning is opt-in, scoped to non-production by default, and requires explicit authority because it can alter state. |
| AI-enabled system with a callable model/application boundary | NVIDIA garak plus checked-in harness scenarios | Conditional adversarial probing selected from the threat model, with budgets and non-production targets. Product-specific prompt injection, tool authority, output handling, data leakage, memory poisoning, and excessive-agency tests remain mandatory because a generic scanner is incomplete. |
| Repository posture | OpenSSF Scorecard CLI | Periodic advisory assessment and dependency due diligence; individual score totals do not become a merge gate or substitute for named controls. |

Documentation-only changes do not run irrelevant code scanners. Data migrations require
the applicable application/database checks plus migration-specific integrity, backup,
rollback, rehearsal, and authorization evidence. OWASP ASVS 5.0 requirements are mapped
individually using versioned identifiers; neither an OWASP Top 10 label nor a scanner
result permits a claim of complete OWASP coverage. Suppressions require owner, rationale,
scope, expiry/review date, and compensating evidence. Any default tool that is abandoned,
compromised, relicensed incompatibly, or unable to meet the evidence contract is
quarantined pending human-reviewed replacement.

### Layer 6: evidence, provenance, and observability

The final evidence bundle should contain at least:

- work item and immutable revision identifiers;
- risk/repository profile and policy version;
- plan, decisions, approvals, and scope changes;
- actor and reviewer provenance without storing hidden reasoning;
- acceptance-criterion-to-evidence mapping;
- exact commands/procedures, environment, status, and relevant artifact references;
- deterministic checks and security findings with tool/ruleset versions;
- independent review findings, severity, resolution, and residual disagreement;
- resource usage, retries, timeouts, circuit-breaker events, and exceptions;
- known limitations, rollback/recovery notes, and final gate decision.

Use content digests and append-only CI/PR artifacts where practical. Supply-chain
release evidence should align with SLSA provenance and support signing/attestation when
the repository publishes artifacts. Telemetry should expose traces, metrics, and logs
without retaining secrets, full private prompts, or unnecessary model transcripts.

### Layer 7: bounded autonomous operation

Every loop, routine, goal, or delegated graph receives a budget envelope:

- token and monetary budget;
- wall-clock deadline;
- iteration and retry limits;
- tool-call and external-side-effect limits;
- concurrency and fan-out limits;
- context/input-size limit;
- no-progress and repeated-failure detection;
- cancellation, checkpoint, and escalation behavior.

Scheduled and event-driven work additionally requires idempotency keys, concurrency
policy, stale-work detection, deduplication, backoff, resumability, and a durable result
destination. Budget exhaustion is a normal control-state transition, not an invitation
for the model to weaken validation or silently choose a cheaper standard.

## Asset-by-asset V1 evaluation

| Asset | V1 assessment | V2 disposition |
| --- | --- | --- |
| `AGENTS.md` | Correctly thin, but its command inventory is stale and its canonical-source statement conflicts with other files. | Revise under P0-01 and P0-02; add generated/validated command inventory metadata. |
| `CLAUDE.md` | Thin adapter is appropriate, but it should use the documented import/precedence pattern and identify host-only differences. | Revise under P0-02 and P0-12. |
| `docs/methodology.md` | Strong lifecycle and evidence foundations. It lacks risk classification, budgets, explicit authorization, evidence identity, and failure states. | Major compatible revision; preserve human merge and native-first invariants. |
| `docs/capability-contract.md` | Good semantic abstraction. Runtime limits, hooks/policy enforcement, telemetry, scheduling, and artifact provenance are missing capabilities. | Extend; do not encode host commands in the core contract. |
| `docs/state-machine.md` | Useful durable labels but too coarse for authorization, budget, policy denial, conditional security review, and revision invalidation. | Extend with schema-backed transition rules. |
| `docs/security-and-autonomy-boundaries.md` | One of V1's strongest assets: effect-based authority and human-only consequential actions. | Retain and extend with profile mappings, agent-specific threats, evidence integrity, and external-data controls. |
| `docs/CROSS_PLATFORM_REPO_PLAN.md` | Valuable architectural history but currently competes with `methodology.md` as a canonical source. | Mark historical/roadmap status and link to normative sources. |
| `engineering-workflow` | Good controller and narrow routing. It cannot currently derive gates, budgets, or state transitions from a risk profile. | Revise after schemas and profiles exist. |
| `designing-changes` | Sound proportional-design guidance. | Add threat, recovery, external-effect, and automation-suitability decisions. |
| `planning-implementation` | Strong plan contract. | Make it schema-backed; add risk/profile, budgets, integration owner, rollback, and evidence plan. |
| `executing-tasks` | Good bounded-task and non-conflicting-write policy. | Add execution leases, budget envelope, cancellation, idempotency, and integration handoff. |
| `testing-changes` | Appropriate TDD default with exceptions. | Map required test depth to risk/repository profiles; add negative and abuse-case testing where applicable. |
| `debugging-systematically` | Evidence-driven and already strong. | Retain with small additions for telemetry correlation and stop/budget criteria. |
| `reviewing-changes` | Good rubric and blocking findings, but reviewer independence is asserted rather than proven. | Add reviewer provenance, conflict rules, disagreement handling, and severity schema. |
| `verifying-completion` | Correctly prioritizes observed evidence. | Produce and validate a final-revision evidence bundle rather than prose-only evidence. |
| `finishing-work` | Preserves the human boundary. | Require a machine-derived readiness result, reviewer-friendly narrative, and immutable revision linkage. |
| OpenAI adapter | Skills-only design is appropriately minimal, but the relative symlink requires a full checkout and is not a self-contained release artifact. | Build a deterministic, self-contained package while preserving canonical-source generation. |
| Claude adapter | Generated Skills are byte-identical, but the package omits the canonical docs referenced by the controller Skill. | Package required references and validate the complete dependency graph. |
| Evaluation catalog/runner | Inspectable semantic rubric is a useful seed, but recorded booleans and a compliant fixture do not evaluate real host behavior. | Replace/extend with executable scenarios, evidence capture, independent grading, and critical gates. |
| Repository validator/CI | Dependency-free validation is valuable. It validates optional schemas only when present and does not validate packaged semantic dependencies or real agent behavior. | Extend in layers and keep fast structural checks separate from expensive behavioral/security suites. |
| Issue form | Captures basic design and verification data. | Add classification, owner, authority, security/data/recovery fields, dependencies, and schema export. |
| PR template | Captures gates but not the requested concise narrative or per-file what/why explanation. | Revise under P0-11 and populate evidence fields from structured artifacts. |

## Workstream classification rule

A proposed **Issue** is a bounded change with one principal deliverable that can be
implemented and reviewed without delegating multiple independently releasable parts.
An **Epic** contains multiple assets, host implementations, control families, or child
deliverables whose order and integration must be managed explicitly.

## Highest-priority workstreams

### P0-01 — Correct repository command and capability facts

**Classification:** Issue

**Why this is high priority:** `AGENTS.md` says no automated validator or evaluation
command exists while those commands are present and used by CI. Agents following the
instruction can skip the repository's real verification path.

**Plan:** Reconcile `AGENTS.md`, contributor documentation, CI, and the actual scripts.
Define one authoritative command inventory with applicability and expected evidence.
Add a validator that detects referenced commands that do not exist and important
repository commands omitted from the instruction file. Do not claim that a command
passes unless it was run against the relevant revision.

**End state:** Every host receives current, verified repository commands; drift causes
CI to fail with an actionable message.

**Acceptance outline:** Command inventory matches checkout and CI; stale-command
regression test exists; documentation-only N/A behavior is explicit; no invented
package command is introduced.

### P0-02 — Establish a single normative source and precedence model

**Classification:** Issue

**Why this is high priority:** The plan, methodology, controller Skill, and instruction
files make inconsistent canonical-source claims. Conflicting instructions produce
unpredictable behavior in both Codex and Claude Code.

**Plan:** Designate `methodology.md`, `security-and-autonomy-boundaries.md`, and
`capability-contract.md` as the three normative sources for lifecycle, authority, and
capabilities. Mark the repository plan as architectural history/roadmap. Document
repository, nested, user, host, memory, and explicit-user precedence without attempting
to override host/system policy. Add contradiction and broken-import checks.

**End state:** A contributor or agent can identify the controlling rule and resolve a
conflict deterministically; duplicate methodology text is unnecessary.

**Acceptance outline:** Precedence table and conflict tests exist; Codex and Claude
load-path tests pass; every core Skill references packaged canonical material.

### P0-03 — Repair Claude package semantic completeness

**Classification:** Issue

**Why this is high priority:** The generated plugin copies `skills/` but not the
canonical documents referenced through `../../docs/...`. A Skill can load while its
normative dependencies are missing.

**Plan:** Compute the transitive local dependency graph for every packaged Skill, copy
the required references into deterministic package paths, and rewrite links only during
packaging if needed. Validate links and content digests inside the built artifact. Add a
clean-environment behavioral smoke test that exercises the controller's references.

**End state:** The Claude plugin is self-contained, portable, and semantically
equivalent to the canonical source at a declared revision.

**Acceptance outline:** No local link escapes or breaks; packaged docs are digest-linked
to source; clean-install and representative invocation pass; divergence fails CI.

### P0-04 — Produce a self-contained OpenAI plugin artifact

**Classification:** Epic

**Why this is high priority:** The current adapter works only within a full repository
checkout whose relative symlink remains intact. That prevents reliable distribution,
versioning, signing, and reproducible installation.

**Plan:** Define a canonical package builder shared in concept with the Claude builder;
generate rather than hand-fork Skills; include required references and plugin metadata;
test clean installation on supported Codex/ChatGPT surfaces; define artifact version,
digest, compatibility metadata, and release evidence; preserve a local-authoring mode.

**Likely child Issues:** Package format and dependency graph; deterministic builder;
OpenAI manifest/metadata validation; clean-install matrix; release artifact provenance.

**End state:** A versioned plugin can be installed without the source checkout and can
be traced back to one canonical repository revision.

### P0-05 — Build an executable cross-host behavioral evaluation system

**Classification:** Epic

**Why this is high priority:** V1 validates manually entered semantic booleans, not
actual Codex or Claude behavior. A compliant fixture proves the scorer, not the harness.

**Plan:** Create versioned scenario datasets with positive, negative, adversarial, and
metamorphic variants. Run supported hosts in disposable repositories with controlled
tools and capture observable traces and artifacts. Grade deterministic facts in code;
use independent model graders only for qualitative criteria; calibrate them against
human-labelled examples; measure false positives/negatives, variance, and regression.
Redact secrets and avoid retaining hidden reasoning.

**Likely child Issues:** Scenario schema; disposable fixture repositories; Codex
runner; Claude runner; deterministic assertions; model-grader protocol; human
calibration set; regression reporting; cost-controlled CI tiers.

**End state:** A release claim describes observed host behavior and confidence, not a
self-reported checklist.

### P0-06 — Replace aggregate-only scoring with critical invariant gates

**Classification:** Issue

**Why this is high priority:** A 90% average can pass while the system autonomously
merges, leaks a secret, bypasses CI, or acts destructively.

**Plan:** Mark critical invariants as must-pass: human-only merge, effect authority,
secret non-disclosure, no bypass of failed required checks, immutable evidence/revision
binding, write isolation when required, and independent review for material changes.
Retain aggregate metrics only for non-critical behavioral quality. Define severity,
waiver authority, expiration, and re-evaluation rules.

**End state:** No weighted average can conceal a safety-boundary failure.

**Acceptance outline:** One failed critical scenario fails the suite; waivers require
named human authority and durable rationale; score reports separate safety from quality.

### P0-07 — Introduce risk classification and repository control profiles

**Classification:** Epic

**Why this is high priority:** “Proportionate” verification is currently left to model
judgment without a taxonomy. That permits inconsistent under-testing or unnecessary
ceremony.

**Plan:** Define R0–R4 change risk, repository profiles, conservative escalation rules,
and a machine-readable mapping from classification to required checks, reviewers,
authority, budgets, and evidence. Align profiles with NIST SSDF, OWASP ASVS/SAMM, SLSA,
and applicable repository constraints. Require a human decision when material inputs
are unknown or when a change alters its own profile/enforcement.

**Likely child Issues:** Risk schema; repository profiles; control registry; classifier
Skill; issue-form integration; gate resolver; representative classification evals.

**End state:** Two agents classify equivalent changes consistently, and the required
verification derives from policy rather than improvisation.

### P0-08 — Establish a security assurance program

**Classification:** Epic

**Why this is high priority:** The authority boundary is strong, but V1 has no
threat-model process, security Skill, control catalogue, scanner selection, severity
policy, or supply-chain assurance profile.

**Plan:** Create a versioned security-control registry covering secure coding,
dependency/supply chain, CI/build, secrets, infrastructure/runtime, privacy/data, and
AI-specific threats. Add threat modelling and security review Skills. Map controls to
repository/risk profiles, evidence types, tools, and blocking severity. Include prompt
injection, excessive agency, sensitive-information disclosure, improper output handling,
poisoning, and unbounded consumption where AI systems are in scope. Implement the
profile-aware default-tool baseline above behind replaceable evidence contracts. Add
fixture-based scanner acceptance tests, pinned acquisition and checksum verification,
least-privilege execution, false-positive/suppression handling, update cadence, and a
tool-compromise/replacement runbook. Automated scanning supplements requirement-level
verification, threat modelling, abuse cases, and human security judgment.

**Likely child Issues:** Threat-model schema/Skill; control registry; severity and waiver
policy; default scanner adapters; scanner supply-chain hardening; SBOM evidence contract;
AI-system profile; security regression evals; tool-health and replacement procedure.

**End state:** A security claim identifies exactly which versioned controls ran, what
they covered, findings and severity, exceptions, and residual risk.

### P0-09 — Add resource budgets, circuit breakers, and routine safety

**Classification:** Epic

**Why this is high priority:** V1 has no protection against runaway loops, repeated
failure, excessive fan-out, token spend, or unsafe scheduled execution. OWASP treats
unbounded consumption as a distinct GenAI risk.

**Plan:** Define the common budget envelope and control-state transitions. Add no-progress
detection, bounded retries with backoff, cancellation, checkpoint/resume, and exception
routing. Specify idempotency, deduplication, concurrency, stale-run, and durable-result
requirements for routines. Map portable requirements to host-native facilities without
making one host's automatic mode mandatory.

**Likely child Issues:** Budget schema; circuit-breaker policy; loop/routine contract;
host mappings; cost/usage telemetry; runaway and duplicate-execution evals.

**End state:** Automation stops predictably before exceeding authority or budget and
leaves enough evidence for safe continuation or human intervention.

### P0-10 — Define structured evidence and transition schemas

**Classification:** Epic

**Why this is high priority:** V1 relies heavily on prose and has no committed schema
directory. Evidence cannot be validated, aggregated, revision-bound, or reliably handed
between sessions.

**Plan:** Define versioned schemas for work classification, plan, task handoff, decision,
approval, check result, finding, review, exception, transition, run summary, and final
readiness. Support human-readable rendering from the same data. Validate schema presence,
compatibility, references, and migrations. Align provenance fields with SLSA/in-toto
concepts without copying irrelevant build-specific fields.

**Likely child Issues:** Schema architecture; core schemas; validator; renderers;
compatibility/versioning policy; CI/PR artifact publication.

**End state:** A readiness report is reproducible from structured evidence tied to the
final revision, while the PR remains readable without opening raw JSON.

### P0-11 — Upgrade the pull-request narrative contract

**Classification:** Issue

**Why this is high priority:** The existing template records gates but does not give the
requested concise explanation or per-file what/why account. Reviewer reconstruction
time becomes the bottleneck at higher autonomy.

**Plan:** Require a three-to-five-sentence summary covering problem, solution, resulting
behavior, and material trade-offs. Add grouped per-file entries with one “what changed”
and one “why” sentence. Preserve acceptance, evidence, security, migration, rollback,
known-risk, and human-merge sections. Generate mechanical evidence tables from P0-10,
but require the narrative to be checked against the final diff.

**End state:** A reviewer can understand intent, inspect evidence, and identify attention
areas without reconstructing the session.

**Acceptance outline:** Template and examples exist; generated/lock files may be grouped;
diff-to-file-list validation detects omissions; prose never substitutes for gate data.

### P0-12 — Govern durable memory and stale context

**Classification:** Epic

**Why this is high priority:** V1 states that sessions are ephemeral but does not define
what agents may remember, source precedence, freshness, invalidation, provenance, or
privacy. Stale memory can silently override current repository facts.

**Plan:** Separate normative policy, repository facts, task evidence, operator
preferences, and agent-generated observations. Define allowed content, source, owner,
scope, created/validated timestamps, expiry, supersession, sensitivity, and invalidation
triggers. Current repository state and explicit scoped instructions outrank memory.
Treat auto memory as untrusted context until corroborated. Add audit and deletion paths;
never store secrets or hidden reasoning.

**Likely child Issues:** Memory model/schema; precedence mapping; Claude adapter; Codex
adapter; stale-memory detector; privacy/redaction policy; conflict evals.

**End state:** Every durable memory item is attributable, scoped, reviewable, expirable,
and unable to weaken current policy.

### P0-13 — Enforce independent review integrity

**Classification:** Epic

**Why this is high priority:** V1 asks for fresh context but does not prove that the
reviewer was independent, saw the final diff, or avoided the implementer's conclusions.

**Plan:** Define implementer/reviewer role separation, allowed context, reviewer
provenance, final-revision binding, severity, disagreement, and re-review triggers.
Prefer different context and, for high risk, diverse prompts/models or human/code-owner
review. Do not expose the implementer's verdict before an independent first pass when
that would anchor the reviewer. Use CODEOWNERS/rulesets where appropriate, while keeping
human approval distinct from AI review.

**Likely child Issues:** Review schema; reviewer role/Skill; host-native mappings;
anti-anchoring protocol; severity/disagreement rules; high-risk code-owner gate;
independence evals.

**End state:** Review evidence proves who/what reviewed which revision, under which
rubric and limitations, and no agent can satisfy the gate by reviewing its own summary.

## Additional lower-priority workstreams

These gaps were not all in the original highest-priority list, but they materially affect
the V2 end state.

### P1-01 — Selective deterministic hook enforcement

**Classification:** Epic

Add small, auditable host adapters for controls that behavioral evals show agents can
forget: policy checks before sensitive tools, evidence capture after checks, secret
redaction, and completion-gate validation. Hooks must be hash/trust reviewed, fail
safely, avoid duplicate conflicting enforcement, and never become a hidden parallel
methodology.

### P1-02 — CI and repository-policy baseline

**Classification:** Epic

Create profile-selected reusable CI, least-privilege workflow permissions, pinned action
dependencies, concurrency controls, secret/code/dependency scanning, and ruleset guidance.
Protect changes to policy, workflows, Skills, schemas, adapters, and CODEOWNERS with
appropriate ownership. Agents may propose but not autonomously weaken these controls.

### P1-03 — Release integrity, SBOM, and artifact provenance

**Classification:** Epic

This is the first post-V2 milestone and begins immediately after the V2 release decision.
Generate checksums, SBOMs where applicable, SLSA-aligned build provenance, and
Sigstore-compatible signed/attested release artifacts. Verify the artifact rather than
only the source tree. Keep release, tag, signing-identity authority, and publication
human-authorized. Deferral must not require a V2 core redesign because P0-04 and P0-10
must already expose artifact identity and provenance extension points.

### P1-04 — Commit, branch, and change-history standard

**Classification:** Issue

Adopt or explicitly decline Conventional Commits; define coherent commit boundaries,
issue references, breaking-change notation, generated-change treatment, branch naming,
and revert guidance. Enforce only the adopted subset and avoid rewriting published
history autonomously.

### P1-05 — Harness observability and quality metrics

**Classification:** Epic

Define privacy-preserving traces, metrics, and logs for lifecycle duration, first-pass
gate rate, escaped defects, review findings, rollback/rework, cost, retries, budget stops,
human intervention, and evaluator disagreement. Optimize for quality-adjusted outcomes,
not agent count, token volume, or lines changed.

### P1-06 — Recovery, migration, and rollout discipline

**Classification:** Epic

Add migration/rollout and recovery Skills plus evidence fields for compatibility,
backfill, canarying, observability, rollback, data integrity, and irreversible steps.
High-risk migrations remain human-controlled even when implementation is automated.

### P1-07 — Data governance and privacy profile

**Classification:** Epic

Define data classification, minimization, retention, residency, connector transmission,
logging/redaction, test-data, deletion, and approval requirements. Integrate with the
security profile but keep privacy impact and authority visible as separate concerns.

### P1-08 — Capability discovery and repository bootstrap

**Classification:** Epic

Create a bounded reconnaissance/bootstrap workflow that discovers real commands,
languages, CI, repository protections, host capabilities, and missing controls. It must
produce a proposed profile for human review rather than silently installing tools or
rewriting policy.

### P1-09 — Compatibility and deprecation matrix

**Classification:** Issue

Implement the N/N-1 policy and surface matrix above. Inventory exact signed desktop
predecessor builds; execute clean-install and capability-contract tests across T3 Code,
terminal, desktop, and web/cloud surfaces; run newer upstream versions as canaries;
declare graceful fallbacks; and time-bound support for deprecated manifest, hook,
scheduling, or plugin behavior. A release-number comparison alone cannot satisfy this
workstream: each used capability must have a positive test and a missing-capability test.

### P1-10 — Optional GitHub and observability connector

**Classification:** Epic

After P0 schemas and native-host mappings exist, perform a native-first gap analysis for
GitHub issue/PR/project state and observability export. Record each unmet use case,
available native capability, data flow, permissions, latency/reliability need, and cost.
Only then design an optional thin connector adapter for the demonstrated gaps, using the
same capability and evidence contracts as every host. Separate read-only collection
from state-changing tools; request least-privilege scopes; redact/minimize transmitted
data; define retries, idempotency, rate limits, audit events, revocation, and fail-closed
behavior for required evidence. Prefer OpenTelemetry-compatible export rather than a
second internal telemetry model.

Likely child Issues are the native-capability/gap analysis, connector threat model and
data-flow review, read-only GitHub adapter, optional write operations with explicit human
authority, OpenTelemetry exporter, contract tests, and install/revocation documentation.
The go/no-go decision remains human-owned after the gap analysis. If P0-10 evidence
schemas and `capability-contract.md` expose connector-neutral interfaces as required,
including this connector later does not require a significant V2 core change. If those
extension points prove insufficient, the connector is deferred rather than allowed to
fork the methodology.

## Epic and Issue authoring contract

No Epic or Issue is authorized by this document. When the owner authorizes their
creation, each record must be independently executable rather than relying on this plan
or prior chat context being present. Every Epic and Issue must include:

- a plain-language problem, priority rationale, objective, and observable end state;
- classification, dependencies, affected assets, locked decisions, and authoritative
  version-pinned references;
- exact in-scope work and non-goals, including prohibited policy claims above;
- acceptance criteria, critical invariants, required checks, evidence outputs, and
  final-revision binding;
- risk/repository profile, security/data/privacy considerations, authority boundaries,
  rollback/recovery needs, budgets, and stop/escalation conditions;
- host/surface compatibility requirements and required fallback behavior;
- a bounded decomposition with inputs, allowed write scope, output contract, and
  integration owner for every delegable task; and
- expected pull-request narrative and the exact unavailable checks that must be reported.

The intended execution shape is GPT-5.6 Terra Medium as orchestrator with GPT-5.6 Terra
Low subagents for narrow, well-specified tasks. Model names are delivery metadata, not a
portable methodology dependency. Terra Low assignments must be independently
verifiable, low-ambiguity, bounded in files/effects, and non-overlapping when concurrent;
architecture, security exceptions, cross-workstream integration, final verification,
and consequential decisions remain with the orchestrator or human as applicable. An
Issue is not ready to start until a worker can determine what to change, what not to
change, how to prove completion, and when to stop without reconstructing omitted context.

## Proposed dependency order

```text
P0-01 command truth -----+
P0-02 precedence --------+--> P0-03/P0-04 packaging
                         |
P0-07 risk profiles -----+--> P0-08 security assurance
                         +--> P0-09 budgets/routines
                         +--> P0-10 schemas/evidence
                                      |
                                      +--> P0-05 executable evals
                                      +--> P0-06 critical gates
                                      +--> P0-11 PR contract
                                      +--> P0-13 review integrity

P0-12 memory governance depends on P0-02 and P0-10.
P1 enforcement, CI, observability, and release work follow the relevant P0 policy/schema
definitions rather than defining competing contracts. P1-03 is the first immediate
post-V2 milestone. P1-10 begins with its native-first gap analysis after P0-10 and P1-05
define connector-neutral evidence and telemetry interfaces.
```

P0-01 through P0-04 are early correctness and packaging repairs. P0-07 and P0-10 are
the architectural spine. P0-05 should not be considered complete until it executes the
critical negative scenarios from P0-06, P0-08, P0-09, P0-12, and P0-13.

## V2 release gates

V2 is ready for a human release decision only when:

- every plugin artifact is self-contained, reproducible, and traceable to source;
- all critical invariants pass on every supported host/fallback path;
- risk and repository profiles deterministically select required gates;
- representative positive, negative, adversarial, and failure-recovery scenarios run
  against real host behavior;
- deterministic checks take precedence over probabilistic evaluation;
- reviewer independence and final-revision binding are proven;
- budgets and circuit breakers stop runaway, duplicate, and no-progress execution;
- structured evidence renders a complete human-readable PR report;
- security controls and claims identify their standards, versions, coverage, findings,
  exceptions, and residual risk;
- required N/N-1 client and current web-service compatibility scenarios pass, with
  capability-based fallbacks tested;
- memory cannot silently override current repository policy or state;
- no agent can approve, auto-merge, merge, publish, deploy, weaken protections, or accept
  material residual risk without the required human decision; and
- a human reviewer can independently verify why the final revision was considered ready.

## Resolved human decisions

The repository owner resolved the planning decisions on 2026-09-01:

1. The proposed P0/P1 priorities are accepted.
2. The proposed Issue/Epic classifications are accepted.
3. V2's initial repository profiles are documentation, general application, web/API,
   library/package, infrastructure-as-code, container/service, data migration, and
   AI-enabled systems. The initial human governance model is owner plus deliberately
   invited collaborators.
4. Supported access surfaces are T3 Code, terminal, desktop, and web as applicable to
   Codex, ChatGPT, and Claude Code. Versioned clients follow the N/N-1 policy and the
   observed baseline recorded above; web services use current-service capability tests.
5. Artifact signing and provenance are staged as the first milestone immediately after
   V2. V2 must include the artifact identity and extension points needed to avoid rework.
6. The profile-aware open-source baseline above is accepted as the planning default.
   Tools remain replaceable implementations of versioned controls, not security claims.
7. V2 includes a planned optional GitHub/observability connector after a native-first
   gap analysis. Its go/no-go decision is deferred; the core must remain connector-neutral.

The next authorized repository action is to put this finalized plan through pull-request
review. Creating Epics or Issues remains explicitly deferred until the owner gives a
separate instruction.
