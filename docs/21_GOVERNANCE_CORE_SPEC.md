# IIOS Governance Core — Specification

**Version:** 0.1.0
**Status:** Specified, not implemented
**Parent authority:** `docs/00_MASTER_CHARTER.md`, `docs/01_CONSTITUTION.md`, `governance/invariant-kernel/`

## Purpose

Convert the Constitution and Invariant Kernel into implementable, reviewable, testable technical contracts before any Governance Core code is written. Nothing in this document or its companions (`docs/22_POLICY_ENGINE_EVALUATION.md` through `docs/26_KILL_SWITCH_SPEC.md`) authorizes running software. No backend, database, migration, MCP, model call, or external connector is created by this change.

## Companion documents

| Document | Scope |
|---|---|
| `docs/22_POLICY_ENGINE_EVALUATION.md` | Policy Engine format, precedence, evaluation, technology comparison |
| `docs/23_CAPABILITY_MODEL.md` | Capability Tokens |
| `docs/24_APPROVAL_MODEL.md` | Approval Service |
| `docs/25_AUDIT_EVENT_MODEL.md` | Audit Events, hash chain |
| `docs/26_KILL_SWITCH_SPEC.md` | Kill Switch |
| `docs/ADR/ADR-0010-GOVERNANCE-CORE-BOUNDARIES.md` | Boundary decisions and alternatives discarded |
| `governance/schemas/` | The JSON Schema contracts this specification defines |

## Position in the authority hierarchy

Per `docs/00_MASTER_CHARTER.md`:

```text
Owner
  └── Master Charter
       └── Constitution
            ├── Invariant Kernel        (governance/invariant-kernel/, unchanged by this spec)
            ├── Governance / Policy Engine   ← this specification
            │    └── Orchestrator
            ├── Approval Authority       ← Approval Service (docs/24)
            └── Audit Authority          ← Audit Events (docs/25), independent observer
```

The Governance Core does not sit above the Invariant Kernel and cannot alter it. Every decision below first checks the Kernel; a Kernel match always wins over any downstream policy (see `docs/22_POLICY_ENGINE_EVALUATION.md` — Precedence).

## A. Governance API

### Responsibilities

Authenticate the actor, classify the request (Action Classifier, below), evaluate it against the Invariant Kernel and Policy Engine, check budget context, request approval when the class requires it, issue a short-lived scoped Capability Token when allowed, and record the decision as an Audit Event. The Governance API is the only component authorized to issue Capability Tokens.

### Explicit limits

The Governance API:

- never executes an action itself — it authorizes or denies;
- never touches the Vault, Graphify index, or model providers directly;
- never approves its own requests — approval is a distinct authenticated role (`docs/24_APPROVAL_MODEL.md`);
- never returns a secret value in a decision, capability, or audit event — only references;
- never grants an action that the Invariant Kernel denies, regardless of policy configuration.

### Inputs and outputs

Input: `governance/schemas/action-request.schema.json`.
Output: `governance/schemas/policy-decision.schema.json`, plus, when applicable, a record conforming to `approval.schema.json` and/or the three capability contracts (`capability-claims.schema.json`, `capability-protected-header.schema.json`, `capability-token.schema.json` — see `docs/23_CAPABILITY_MODEL.md`), plus one or more `audit-event.schema.json` records.

### Authentication

Actor identity is established before classification. Minimum actor types: `owner`, `orchestrator`, `runtime`, `service`, `hermes_profile`, `claude_code`, `claude_cowork` (see `action-request.schema.json#/$defs/actor`). Concrete authentication mechanism (session, mTLS, signed service token) is an implementation decision deferred to the build phase; this spec fixes only that `auth_method` is recorded and that approver authentication is always on a channel independent from the requester's (`docs/24_APPROVAL_MODEL.md`).

### Authorization

Deny-by-default. Authorization is a function of `(actor, action_class, Invariant Kernel, policy_version, approval_state, budget_state)`. No authorization decision may be inferred from conversation history, prior behavior, or silence (Constitution Article I.3).

### Errors

Errors are structured, machine-readable, and never leak internal state, stack traces, or secret material. Every error path that blocks an action MUST still emit a `policy_decision` audit event with `decision: deny` or `require_approval` and a `reason_codes` entry — a swallowed error is a Constitution Article III.9 violation ("failed validation cannot be narrated as success").

### Idempotency

Every action-request carries an `idempotency_key`. A repeated key within the idempotency window (implementation-defined TTL, default proposal: 24 hours) MUST return the original `policy-decision` record (`replayed: true`) rather than re-evaluating, re-approving, or re-issuing a capability. This prevents duplicate execution from client retries and is required for the "duplicate request" and "replay" test cases below.

### Fail-closed

Exactly the rule already ratified in `docs/03_GOVERNANCE_SECURITY.md`: Governance API or Policy Engine unavailability blocks all Class B, C and D actions. Class A may continue only under a valid, unexpired cached policy explicitly authorizing offline read-only operation. No cached policy may authorize financial writes, external writes, secret access, or production changes. This applies uniformly across every component in this specification — it is not re-litigated per component.

### Traceability

`correlation_id` is mandatory on every request and MUST be identical across the action-request, policy-decision, approval, capability-token, and every resulting audit-event. `request_id` identifies one logical submission; `idempotency_key` identifies retries of the same logical submission.

### Health checks

- **Liveness**: process responds. Does not imply authorization is possible.
- **Readiness**: Invariant Kernel loaded and checksum-verified (`scripts/verify_invariant_kernel.py` logic), current policy bundle loaded and schema-valid, audit sink reachable. If readiness fails, the Governance API MUST refuse all requests except its own health endpoint — this is itself the fail-closed rule applied to the service's own startup state.

## B. Action Classifier

### Classes

Exactly Constitution Article IV, unchanged:

- **Class A** — automatic read-only.
- **Class B** — controlled reversible.
- **Class C** — explicit human approval.
- **Class D** — prohibited in current phase.

### Determinism

The classifier may receive an LLM-produced `classifier_hint` (`action-request.schema.json#/classifier_hint`), but the hint is advisory only and is never the authorization decision. The authoritative class is computed by deterministic table lookup on `(verb, resource_type, environment)` against the Policy Engine's rule set, cross-checked against the Invariant Kernel. This satisfies Constitution Article III's "deterministic enforcement outside the LLM" and AGENTS.md's "critical rules require deterministic enforcement outside the LLM."

### Ambiguous classification

If `(verb, resource_type, environment)` does not match a known rule, the request is classified at the strictest class that could plausibly apply — never defaulted to A or B. In practice this means: unknown financial or authority-adjacent resource types resolve to D; unknown but clearly non-authority resource types with a write verb resolve to C; unknown read-only resource types resolve to C, not A (Class A requires an explicit allowlist match, per the existing MVP action matrix in `docs/03_GOVERNANCE_SECURITY.md`). An unmatched request always emits a `reason_codes` entry `UNCLASSIFIED_RESOURCE` and is never silently allowed.

### Multiple actions in one request

An action-request decomposes into `items` (`action-request.schema.json#/items`). The request-level class is the maximum (strictest) class across items. `overall_decision` follows the same maximum unless `decomposable: true` is set, in which case Governance MAY return independent `item_decisions` and the caller is responsible for only executing items marked `allow`.

### Risk increase during execution

A capability is issued for one classified item at one point in time. If execution surfaces new information matching a `risk_signals` entry (e.g. a tool result reveals the target is actually a production resource, or contains a secret reference), the executor MUST stop and submit a fresh action-request; the original capability does not cover the reclassified action, and continuing on it is itself a Class D violation ("bypass approval"). This is a structural rule, not a suggestion: capability tokens are scoped to the exact `resource` string (`docs/23_CAPABILITY_MODEL.md`), so a changed resource cannot validate against the old token.

### Reclassification after tool results

Same rule as above, generalized: any new fact discovered mid-task that would change `(verb, resource_type, environment)` or trigger a `risk_signals` entry forces re-evaluation before the next side-effecting step. The Orchestrator Boundary (below) is responsible for enforcing this at the execution layer; the Governance API enforces it by refusing to accept a capability whose `resource` no longer matches.

## C. Orchestrator Boundary

Full detail in `docs/ADR/ADR-0010-GOVERNANCE-CORE-BOUNDARIES.md`; summary here for completeness of the Governance Core picture.

**Can:**
- decompose an already-approved objective into subtasks;
- request a capability per subtask from the Governance API;
- emit `execution_result` audit events for each subtask;
- retry a failed subtask up to the policy-defined retry limit, using a fresh `idempotency_key` derived deterministically from the original (never duplicating billed side effects).

**Cannot:**
- approve its own requests. The Orchestrator can never hold an approver role because `action-request.schema.json#/$defs/actor/actor_type` is a closed enum that never grants `owner` or `delegated_approval_authority` to `orchestrator` — that enum restriction is a genuine schema-level guarantee. The separate rule that one approver cannot approve their own request (`approver_id != requested_by`) is a cross-field comparison JSON Schema cannot express; it is enforced by the Policy Engine at decision time and re-checked by the Approval Service at consumption time, with reason code `SELF_APPROVAL_FORBIDDEN` (`docs/24_APPROVAL_MODEL.md` — Self-approval prevention);
- ignore or downgrade a `deny` or `require_approval` decision;
- fabricate, cache indefinitely, or reuse a capability past `expires_at` or `max_uses`;
- delegate beyond the policy-defined delegation depth limit (Cost Governance "delegation limit", `docs/12_COST_GOVERNANCE.md`);
- delete, edit, or reorder an audit event;
- instruct the Audit Authority to suppress or alter a record. Audit is a one-way evidence sink from the Orchestrator's perspective (ADR-0009).

**On Governance failure**: the Orchestrator halts the affected task, does not retry into a fail-closed wall, and surfaces the block to the Control Center (`docs/11_CONTROL_CENTER_PRD.md`) rather than silently succeeding with degraded guarantees.

## Secret handling: value vs. reference

"Handle a secret" is not one action class — it is two distinct verbs with different consequences, and every document and decision case in this specification distinguishes them explicitly rather than using "secret access" as a single blurred category:

- **`secret_value.read`** — obtaining the raw secret value into a context a model, agent, or runtime can see, log, or forward. **Prohibited for agents and models, unconditionally**, per Constitution INV-004 ("Secrets cannot be exposed to models or logs by default") and AGENTS.md's non-negotiable invariants. This is not a Class C-with-approval action — no approval elevates it to allowed. Reason code `SECRET_VALUE_DISCLOSURE_FORBIDDEN`. The only path a raw value ever takes is Secret Manager → the specific authorized execution process that needs it to perform one already-authorized operation (e.g. the process making an authenticated API call), never through a model's context, a capability payload, an audit event, or a log line.
- **`secret_reference.use`** — authorizing a scoped operation that *uses* a secret without the requester ever seeing its value (e.g. "use the FundingPips API key to make this one authorized read call," or Secret Manager fetching a value directly into an isolated execution process). This is **Class C**: requires approval and a capability, exactly like any other Class C action (case #10 below), but what is approved is the *use*, not disclosure of the *value*. Reason code `SECRET_REFERENCE_APPROVAL_REQUIRED` when the required approval/capability is missing.

Consequences that follow from this distinction:

- Secret Manager delivers the secret value **directly to the authorized execution process**, never routed through a model's context window or the Orchestrator's own visibility, even when the Orchestrator requested the operation.
- Every output, log line, and audit `evidence` field that could contain a secret value is redacted before it reaches any model, agent, or human-facing surface — redaction happens at the boundary, not as a downstream cleanup step.
- A model or agent receives only the **result** of a secret-using operation (success/failure, a non-sensitive status, or a further non-sensitive reference), never the secret value itself, regardless of how the operation was framed or requested.

## 20 mandatory decision cases

Class per Constitution Article IV and the MVP action matrix in `docs/03_GOVERNANCE_SECURITY.md`. "Capability" = required for the action to execute; "n/a" = pure computation touching no external or protected resource. "Not executable" = the action is definitionally gated on a live Governance Core that does not exist yet, so any such request today resolves to `deny` by absence of a service able to issue the capability — this is fail-closed, not a gap.

| # | Case | Class | Decision | Policy basis | Approval | Capability | Audit event(s) | On Governance unavailable |
|---|---|---|---|---|---|---|---|---|
| 1 | Read prop-firm account balance | A | allow | Read-only credential, egress allowlist | not_required | yes, reusable within TTL, read-only scope | request_received, policy_decision, capability_issued, execution_result | Allowed only under valid unexpired offline-read cached policy; else deny |
| 2 | Calculate drawdown | A | allow | Deterministic engine, tested | not_required | n/a (no external/protected resource touched) | request_received, policy_decision, execution_result | Same as above; pure computation may proceed if inputs already held locally, else deny |
| 3 | Open a trade order | D | deny | INV-002, Constitution Art. IV-D | n/a | none | request_received, policy_decision (deny) | deny (unconditional; D is never contingent on availability) |
| 4 | Modify a stop loss | D | deny | INV-002, AGENTS.md non-negotiable invariants | n/a | none | request_received, policy_decision (deny) | deny |
| 5 | Withdraw capital | D | deny | INV-002 | n/a | none | request_received, policy_decision (deny) | deny |
| 6 | Create a Git branch | B | allow | Sandboxed, Git branch review | not_required | yes, scoped to repo + branch prefix | request_received, policy_decision, capability_issued, execution_result | deny (B fails closed) |
| 7 | Edit code on a feature branch | B | allow | Sandboxed, Docker, review | not_required | yes, scoped to repo + branch | request_received, policy_decision, capability_issued, execution_result | deny |
| 8 | Merge to `main` | C | require_approval | Protected branch, CI verification gate (`.github/workflows/verify-foundation.yml`) | pending → approved | single-use, scoped to exact commit SHA + target branch | request_received, policy_decision, approval_requested, approval_decided, capability_issued, capability_consumed, execution_result | deny |
| 9 | Deploy to production | C | require_approval | CI/CD gate | pending → approved | single-use, scoped to release artifact hash + environment=production | same pattern as #8 | deny |
| 10 | Read a secret — split by verb, see "Secret handling" above | `secret_reference.use`: C. `secret_value.read`: prohibited, no class permits it | `secret_reference.use`: require_approval. `secret_value.read`: deny, unconditional | `secret_reference.use`: INV-004, Secret Manager scoping. `secret_value.read`: INV-004 as an absolute bar, not a Class C gate | `secret_reference.use`: pending → approved. `secret_value.read`: n/a — approval cannot authorize this verb | `secret_reference.use`: single-use, minimized scope, delivered directly to the authorized process. `secret_value.read`: none issuable | same pattern as #8 for `secret_reference.use`; `evidence` references the secret's metadata, never its value. `secret_value.read` gets `policy_decision` deny (`SECRET_VALUE_DISCLOSURE_FORBIDDEN`) | deny for both |
| 11 | Rotate an API key | C (`secret_reference.use` — the rotation operation itself, not disclosure of the old or new value) | require_approval | Secret Manager audit | pending → approved | single-use | same pattern as #8; old/new key values never appear in the request, decision, capability, or audit trail | deny |
| 12 | Activate an MCP connector | C | require_approval | Manifest/source review, version pinning | pending → approved | single-use, scoped to connector id + pinned version | same pattern as #8 | deny |
| 13 | Send an email | C | require_approval | "External message" until an explicit ratified policy narrows it | pending → approved | single-use, scoped to recipient + template | same pattern as #8 | deny |
| 14 | Make.com — list/query scenario metadata (read-only) | A, only via a technically read-only, allowlisted connector | allow (once such a connector exists; not implemented here) | ADR-0011 — Make.com | not_required | yes, reusable within TTL, read-only scope | request_received, policy_decision, capability_issued, execution_result | deny |
| 14b | Make.com — run, activate, deactivate, edit, or create a scenario | C (not executable today) | deny | ADR-0008 Cowork boundary + ADR-0011 — Make.com; external write requires live Governance mediation, which does not exist yet | pending (cannot progress) | none issuable | request_received, policy_decision (deny, `GOVERNANCE_MEDIATION_UNAVAILABLE`) | deny |
| 15 | Migrate Supabase schema | C | require_approval | Backup + migration tool control (`docs/10_INFRASTRUCTURE.md`) | pending → approved | single-use | same pattern as #8 | deny |
| 16 | Modify the Constitution | D, categorically outside Governance API's authorization surface | deny | Constitution Art. III.1; only an out-of-band Owner ratification process (Git PR + ADR + version increment) can change it | n/a — not an approvable action type | none — no capability class exists for this | request_received, policy_decision (deny, `PROTECTED_AUTHORITY_PATH`) | deny |
| 17 | Modify the Invariant Kernel | D, categorically outside Governance API's authorization surface | deny | Constitution Art. III.1; same out-of-band process as #16 | n/a | none | request_received, policy_decision (deny, `PROTECTED_AUTHORITY_PATH`) | deny |
| 18 | Delete an audit record | D | deny | Constitution Art. III.2; Audit storage exposes no delete operation at all — structural, not policy | n/a | none | request_received, policy_decision (deny, `AUDIT_IMMUTABLE`) | deny |
| 19 | Budget overspend detected | cross-cutting | deny (further requests in scope) | `docs/12_COST_GOVERNANCE.md` hard caps | n/a for the block itself; raising the cap is a new Class C request to the Owner | none issuable in the exceeded scope | budget_exceeded, then policy_decision (deny) for each subsequent request in scope | deny (budget block persists; unrelated to Governance's own availability) |
| 20 | Governance itself unavailable | cross-cutting | deny for B/C/D; A limited | Fail-closed rule, `docs/03_GOVERNANCE_SECURITY.md` | n/a | none issuable | governance_unavailable, queued locally and replayed into the hash chain once Governance returns | this case IS the unavailability |

## Quality requirements (binding on all companion documents and schemas)

- Deny-by-default everywhere; absence of a matching allow rule is a deny.
- Fail-closed everywhere; see rule above.
- JSON Schema Draft 2020-12 for every schema in `governance/schemas/`.
- Identifiers are UUID-formatted strings; enums are closed (`additionalProperties: false` where the shape is fully known).
- Timestamps are RFC 3339, UTC, `Z` suffix.
- Financial amounts are decimal strings matching `^[0-9]+(\.[0-9]+)?$`, never floating-point numbers.
- Idempotency keys on every mutating request.
- Correlation IDs identical across a request's full record set.
- Reason codes are machine-readable (`^[A-Z][A-Z0-9_]{2,63}$`), never free text alone.
- No provider or vendor name is hardcoded into policy or schema (`docs/06_MODEL_ROUTING.md`, `config/model-registry.json` pattern extended here).
- No credential, token secret, or raw key material appears in any schema instance.
- Decisions must be reproducible from `(action-request, policy_version, kernel_checksum)` alone — no dependency on private model reasoning at evaluation time.

## Conceptual test matrix

Test runner intentionally not implemented in this change. Table defines the required conceptual coverage; component documents add scenario-specific edge cases.

| Scenario | Setup | Expected `overall_decision` | Expected audit behavior | Notes |
|---|---|---|---|---|
| Allow | Class A item, valid actor, budget in range | `allow` | `policy_decision` allow, `capability_issued` if resource touched | Baseline happy path |
| Deny | Class D item | `deny` | `policy_decision` deny, `reason_codes` includes an `INV-*` or class code | Kernel match short-circuits policy evaluation |
| Require approval | Class C item, no prior approval | `require_approval` | `policy_decision` require_approval, `approval_requested` | No capability issued until `approval.state == approved` |
| Expired approval | Approval `state: expired`, capability requested after `expires_at` | `deny` | `approval_expired`, `policy_decision` deny (`APPROVAL_EXPIRED`) | Expired approval never auto-renews |
| Expired capability | Capability `expires_at` in the past presented at consumption | `deny` | `policy_decision` deny (`CAPABILITY_EXPIRED`) at consumption check | Server-side check, not client-trusted |
| Duplicate request | Same `idempotency_key` resubmitted inside TTL | Same `decision_id` returned, `replayed: true` | No new `policy_decision` audit event; existing one referenced | Prevents double execution |
| Replay | Same fully-formed action-request signature replayed outside idempotency TTL | Re-evaluated fresh | New `policy_decision` under current `policy_version` | A stale request is not automatically re-honored under an old policy |
| Capability replay | Same `capability_id` + `nonce` presented again after a successful consumption, still within `expires_at` | `deny` | `capability_consumed` (result: blocked, `CAPABILITY_REPLAY_DENIED`) | Distinct from expiry: a valid, unexpired, correctly-signed envelope is still denied because it was already consumed — see `docs/23_CAPABILITY_MODEL.md` |
| Policy mismatch | `policy_version` on a presented capability does not match current active policy | `deny` | `policy_decision` deny (`POLICY_VERSION_MISMATCH`) | Prevents use of a capability issued under a superseded policy |
| Budget exceeded | Task/profile/domain over its cap | `deny` for further requests in scope | `budget_exceeded`, then `policy_decision` deny per subsequent request | Raising the cap is itself Class C |
| Governance unavailable | Policy Engine/Kernel unreachable | `deny` for B/C/D; `allow` for A only under valid cached offline policy | `governance_unavailable`, queued for hash-chain replay | Never returns `allow` for B/C/D on a guess |
| Audit unavailable | Audit sink unreachable | `deny` | No event recorded live; local queue only if queuing itself is possible, else deny | No execution without an audit path — evidence is a precondition, not an afterthought |
| Kill switch active | Any active `L1`-`L5` level covering the request's scope | `deny` | `kill_switch_activated` already logged; new request gets `policy_decision` deny (`KILL_SWITCH_ACTIVE`) | Scope-matched, see `docs/26_KILL_SWITCH_SPEC.md` |
| Semantic modification of the Kernel | `invariants.json` canonical hash != `manifest.json` expected hash | `deny` for everything except read of governed docs | `kernel_integrity_violation`, then fail-closed for all subsequent requests until resolved | Mirrors `scripts/verify_invariant_kernel.py` behavior at the service level |

## Open questions for the Owner

All seven items below were **resolved by Owner decision, ratified in `docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md`** (23 July 2026). Kept here as a historical record of what was asked; see ADR-0011 for the concrete answers.

1. ~~Idempotency window default~~ — **Resolved**: 24h default, configurable up to 7 days (ADR-0011 — Idempotency).
2. ~~Concrete actor authentication mechanism~~ — **Resolved**: OIDC+MFA+WebAuthn for humans, mTLS with short-lived workload identity for services/agents/runtimes (ADR-0011 — Actor authentication).
3. ~~Default Class C approval TTL~~ — **Resolved**: 15 min default, 60 min max in non-production for reversible actions only (ADR-0011 — Class C approvals).
4. ~~Whether `required_approvals > 1` is needed for any MVP action~~ — **Resolved**: single approver (Owner) for MVP; multi-approver support remains in the model but deferred past MVP (ADR-0011 — Class C approvals).
5. ~~Capability signing algorithm and key custody~~ — **Resolved**: JWS Compact Serialization, `alg: Ed25519` (fully-specified identifier, not the polymorphic `EdDSA`), `kid`/`typ` mandatory in the protected header; private key in KMS/HSM/external Vault, 90-day rotation, 24h key-overlap ceiling (ADR-0011 — Capability envelope format, corrected 23 July 2026; `docs/23_CAPABILITY_MODEL.md`).
6. ~~Exact kill-switch periodic test cadence~~ — **Resolved**: L1/L2 monthly staging, L3 quarterly staging, L4 semiannual staging + annual production tabletop, L5 annual tabletop; a real L5 activation drill needs separate explicit Owner authorization (ADR-0011 — Kill Switch test cadence).
7. ~~Whether Make-scenario execution (#14) should remain permanently Class C-gated, or a narrower read-only Class A carve-out created~~ — **Resolved**: read-only metadata listing/query may be Class A via a technically read-only allowlisted connector; every mutating scenario action is Class C; no new subclass created for MVP (ADR-0011 — Make.com).

### Still open (not addressed by ADR-0011)

- Exact pinned version of the `jsonschema` Python library (library and validator class are decided; the version pin is implementation-time work — `governance/schemas/README.md`).
- Governance API's concrete transport/protocol (HTTP/REST, gRPC, or other) and framework — actor authentication *method* is decided (OIDC/mTLS), the wire protocol is not.
- Policy bundle's own structural schema (analogous to `governance/invariant-kernel/schema.json`) — format conditions are fixed (`docs/22_POLICY_ENGINE_EVALUATION.md`), the concrete schema document does not exist yet.
- External signature/anchoring for audit hash-chain tamper-resistance beyond tamper-evidence (`docs/25_AUDIT_EVENT_MODEL.md` — Integrity today vs. tamper resistance tomorrow) — not addressed by this ADR.

## Status

Governance Core: **specified, not implemented**. No service, database, migration, or endpoint exists. This document and its companions are reviewable, testable contracts for a future implementation phase that requires its own ADR-linked authorization to begin.
