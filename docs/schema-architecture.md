# Structured evidence schema architecture

This document defines the common contract for structured evidence. It implements
Issue #87 and is the composition boundary for the later P0-10 evidence-family
issues. It does not define their payloads or change risk, CI, security, or
budget policy.

## Envelope

Each evidence artifact is one JSON object conforming to
[`../schemas/evidence-envelope.schema.json`](../schemas/evidence-envelope.schema.json).
The common envelope owns identity, provenance, policy, repository/revision
binding, references, and extensions. A family owns only the object under
`payload`; a family schema composes the envelope with an `allOf` constraint on
that object.

The envelope has these required fields:

| Field | Meaning |
| --- | --- |
| `schema` and `schema_version` | Stable envelope identifier and SemVer version used to interpret the record. |
| `evidence_type` and `id` | Namespaced family type and stable artifact identity. |
| `repository` and `revision` | Repository URI and immutable full Git object ID to which this evidence is bound. |
| `policy` | Applicable policy identifier and policy SemVer version. |
| `produced_at` and `actor` | UTC production time plus accountable actor and role. |
| `payload` | Family-owned evidence data. |

`provenance` records observable source metadata, never hidden reasoning, full
private prompts, credentials, or secrets. Timestamps use RFC 3339 UTC (`Z`).
Git revisions carry their algorithm explicitly. The contract accepts
`git-sha1` with a 40-character lowercase hexadecimal object ID and
`git-sha256` with a 64-character lowercase hexadecimal object ID. The current
repository reports Git object format `sha1`; a future algorithm must be added
to both the schema and compatibility registry before it is accepted.

## Versioning and compatibility

The format is JSON Schema Draft 2020-12. Its exact supported versions and
compatibility policy are in
[`../schemas/evidence-compatibility.json`](../schemas/evidence-compatibility.json).
The initial contract supports `evidence-envelope` `1.0.0` and major `1`.

Within a major version, a consumer may accept a later minor/patch version only
when the registry explicitly marks that major supported. Producers must not
silently claim a newer semantic contract merely because its version parses as
SemVer. Unknown top-level envelope fields are invalid. Forward-compatible data
belongs only in `extensions`, keyed by a reverse-DNS namespace; consumers that
do not recognize an extension preserve it without assigning semantics.

Changing a required field, its meaning, validation behavior, digest algorithm,
revision semantics, reference semantics, or extension rules is a major change.
Adding an optional envelope field is a minor change only when old consumers can
ignore it without weakening an invariant. A deprecated field remains readable
through its declared supported major and has a documented replacement before
removal in the next major.

## Migration

Evidence is immutable. Migration creates a new envelope at the target version,
with a `references` entry whose `relation` is `derived-from`, whose target
identifies the source artifact, and whose digest verifies the source bytes.
The original remains available and interpretable under its original registry
entry. A migration that cannot retain this source reference is unsupported and
must fail rather than present transformed evidence as original evidence.

## Artifact digests and references

A `sha256:` digest is SHA-256 over the exact UTF-8 bytes of the referenced
artifact, including whitespace and its final newline. It is not a digest of a
parsed or reformatted JSON value. A local reference target is resolved relative
to the evidence file; it must exist, remain inside the supplied evidence root,
and match the declared digest. A missing target or mismatch is a stale reference.
Any absolute URI target, including `file:` URIs, is an explicit external
reference. The dependency-free
local validator does not fetch it and reports it as unsupported, rather than
misreporting it as a stale local path. External reference validation requires a
separately retained artifact and a digest-verifying verifier.

References may only use the registered relations `derived-from`, `supports`,
`supersedes`, and `describes`. Each relation explains the dependency without
changing the target's revision binding. `derived-from` is mandatory for a
migrated representation.

## Validation strategy and fixtures

`scripts/validate_evidence_schema.py` uses only the Python standard library.
It validates stable envelope and registry invariants plus the cross-artifact
rules that JSON Schema cannot express. The fixture corpus intentionally includes
both expected successes and expected failures:

| Fixture | Expected result | Demonstrated rule |
| --- | --- | --- |
| `valid.json` | valid | Minimum revision-bound envelope. |
| `extension.json` | valid | Explicit, namespaced extension and valid digest reference. |
| `malformed.json` | invalid | Malformed immutable Git revision. |
| `incompatible-version.json` | invalid | Unsupported major version. |
| `stale-reference.json` | invalid | Digest mismatch for an existing reference target. |
| `migrated.json` | valid | Migration metadata has a digest-verified `derived-from` source. |
| `migration-without-derived-from.json` | invalid | A migration cannot use another reference relation in place of its source link. |
| `external-reference.json` | invalid | The local validator reports URL retrieval as explicitly unsupported. |

Family payload validation, rendering, CI publication, and remote artifact
retrieval are planned downstream work and are intentionally not implied by a
successful envelope validation.
