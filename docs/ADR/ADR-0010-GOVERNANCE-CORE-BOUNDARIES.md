# ADR-0010 — Governance Core Boundaries

Status: Proposed for Owner ratification
Date: 22 July 2026
Owner: IIOS Owner

## Context

Foundation v1.2.1 ratified the Master Charter, Constitution, and Invariant Kernel, and put repository controls (branch protection, CI verification, PreToolUse hooks) in place. `PROJECT_STATE.md`'s acceptance criteria still list "Governance API interfaces are specified before implementation" and "Audit and cost event schemas are specified before implementation" as open. Before any Governance Core backend is written, the Constitution's abstract principles (deny-by-default, fail-closed, separation of policy/decision/authorization/execution/audit, no self-approval, no capability-implies-authority) need to become concrete, testable technical contracts. This ADR records the boundary decisions made while producing `docs/21_GOVERNANCE_CORE_SPEC.md` through `docs/26_KILL_SWITCH_SPEC.md` and `governance/schemas/`.

## Decision

1. **The Orchestrator is subordinate to Governance and cannot self-approve.** No `actor_type` value in `action-request.schema.json` grants the Orchestrator an approval role; this is a schema-level fact, not just a documented convention, so it cannot be worked around by simply choosing a different actor type at implementation time without also changing the ratified schema.
2. **Audit Authority remains independent**, per ADR-0009: it receives evidence, it is never the Orchestrator's command parent, and it is never a peer the Orchestrator can bypass or instruct to suppress a record.
3. **The Action Classifier's LLM-assisted hint is strictly advisory.** The authoritative class is always computed by deterministic table lookup against the Policy Engine, cross-checked against the Invariant Kernel — never trusted from a model's self-report, per Constitution Article III and AGENTS.md's "critical rules require deterministic enforcement outside the LLM."
4. **The MVP Policy Engine format is custom JSON rules**, not Open Policy Agent/Rego, Cedar, or Casbin. See `docs/22_POLICY_ENGINE_EVALUATION.md` for the comparison and the mandatory conditions the format must satisfy regardless of implementer. This keeps the Governance Core specification within the currently-approved scope (no new infrastructure/runtime dependency) and reuses the checksum/manifest/verifier pattern already ratified for the Invariant Kernel. **This recommendation is explicitly reversible**, not an irreversible implementation commitment: it is subject to confirmation at implementation time and to security review, and may be superseded by a future ADR if measured rule-set complexity outgrows it.
5. **Capability Tokens never carry secret values** and are bound to `(subject, action, resource, environment)` with no cross-resource validity — a reclassified or scope-changed action always requires a fresh evaluation, never a reused capability.
6. **Approval requires self-approval prevention** (`approver_id != requested_by`). This is a cross-field comparison JSON Schema Draft 2020-12 cannot express, so it is not schema-enforced; `approval.schema.json` documents it via `$comment` only. Enforcement is the Policy Engine's evaluation-time check plus the Approval Service's independent re-check at consumption time (reason code `SELF_APPROVAL_FORBIDDEN`), not left to policy-authoring discipline — see `docs/24_APPROVAL_MODEL.md`. Approver authentication remains independent of the requester's channel.
7. **Audit is an append-only hash chain.** Its canonicalization is a distinct problem from the Invariant Kernel's checksum: the Kernel fix (`scripts/verify_invariant_kernel.py`, v1.2.1) normalizes CRLF/CR to LF to make a **versioned text file** hash identically across checkouts; an audit event is a **programmatically produced JSON value**, where the open problem is serializer-dependent key order, whitespace, and number formatting, not line endings. The recommended design is RFC 8785 (JSON Canonicalization Scheme), not implemented in this change — see `docs/25_AUDIT_EVENT_MODEL.md`.
8. **The Kill Switch's activation path is independent of Governance API availability**, by design — a kill switch that requires the system it might need to kill to be healthy first is not a kill switch.
9. **Nothing in this ADR or its companion specifications authorizes implementation.** `PROJECT_STATE.md` records Governance Core as "specified, not implemented" after this change; a future ADR is required before writing the actual service, database, or endpoint code.

## Alternatives considered and discarded

- **Skip a written classifier/policy spec and let the Orchestrator's model reason about action class at runtime.** Discarded: violates Constitution Article III.6 (deterministic enforcement outside the LLM) and AGENTS.md's non-negotiable invariants directly; a model's self-assessed risk is not evidence.
- **Adopt Open Policy Agent for the MVP policy engine now.** Discarded for MVP: adds an infrastructure dependency and operational surface beyond "Current allowed scope" in `AGENTS.md` (which lists a "policy-engine skeleton," not a third-party policy runtime) before there is measured complexity to justify it. Left open as a documented future migration path in `docs/22_POLICY_ENGINE_EVALUATION.md`.
- **Allow the Orchestrator a narrow "emergency self-approval" for time-critical Class C actions.** Discarded: directly contradicts Constitution Article III.11 ("No agent approves its own privilege expansion") and the Master Charter's "capability never implies authority." A time-critical need is addressed by a short approval TTL and clear escalation to the Owner, not by weakening the approval boundary.
- **Merge Audit Authority into the Governance API as one component.** Discarded per ADR-0009's existing decision: keeping Audit independent, receiving evidence rather than being asked permission, is what lets Audit detect a compromised or misbehaving Governance/Orchestrator pair rather than trusting the same component to both act and grade its own homework.
- **Use free-text `explanation` strings as the authoritative decision record.** Discarded: the quality requirements in `docs/21_GOVERNANCE_CORE_SPEC.md` fix machine-readable `reason_codes` and `matched_rules`/`matched_invariants` as authoritative; `explanation` is display-only, so a decision remains reproducible and testable without parsing prose.

## Consequences

Implementing the eventual Governance API, Policy Engine, Approval Service, Capability issuance, Audit sink, and Kill Switch becomes a matter of building to an already-reviewed contract rather than designing authorization semantics under implementation pressure. The specification also gives `scripts/verify_foundation.py` concrete new artifacts whose *presence* (not runtime behavior) it can check, extending the existing verification pattern without adding a new verification philosophy.

The cost is that this is a substantial specification surface (6 documents, 1 ADR, 6 JSON Schemas) that must stay in sync with each other and with the Constitution/Invariant Kernel as the project evolves; a future amendment to any of the referenced Constitution articles requires revisiting this ADR's boundary decisions, not just the Constitution text.

## Security/financial impact

None directly — no service is deployed, no credential is created, no financial capability exists. The specification's entire design intent is to reduce future security/financial risk by fixing deny-by-default, fail-closed, no-self-approval, and audit-immutability as structural properties before any code exists that could violate them under implementation time pressure.

## Evidence

- `docs/21_GOVERNANCE_CORE_SPEC.md` — Governance API, Action Classifier, Orchestrator Boundary, 20-case decision matrix, conceptual test matrix.
- `docs/22_POLICY_ENGINE_EVALUATION.md` — Policy Engine format, precedence, technology comparison.
- `docs/23_CAPABILITY_MODEL.md`, `docs/24_APPROVAL_MODEL.md`, `docs/25_AUDIT_EVENT_MODEL.md`, `docs/26_KILL_SWITCH_SPEC.md` — component specifications.
- `governance/schemas/*.json` — the six JSON Schema contracts, Draft 2020-12.
- `python scripts/verify_invariant_kernel.py` and `python scripts/verify_foundation.py` — pass unchanged; `invariants.json` untouched by this change (see delivery report).

## Rollback/review date

Rollback: revert this branch before merge; nothing outside `docs/21`-`docs/26`, this ADR, `governance/schemas/`, and the permitted status-file updates is touched, so rollback is a clean branch discard with no effect on `main`, the Invariant Kernel, or any ratified document.
Review date: before Governance Core implementation begins, and at any future Constitution or Invariant Kernel amendment that touches Article III, IV, or VIII.
