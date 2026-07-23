# IIOS Workflow Registry

**Status:** Specified — no workflow below is automated
**Parent authority:** `AUTONOMY_PROTOCOL.md`, `docs/21_GOVERNANCE_CORE_SPEC.md`

## Purpose

Specify the standard shape of IIOS's recurring operational workflows before any of them are automated. Each entry is a contract for how the workflow *should* run once its dependencies exist; none is implemented as running automation today.

---

```text
workflow_id: WF-FEATURE-DELIVERY
name: Feature delivery
trigger: A `ready` BACKLOG.md task with resolved dependencies.
steps: Plan → implement → test → security review → documentation review → commit → push →
  open PR → observe CI → update work state.
actors: Developer Brain/Agent, Test Engineer Agent, Security Reviewer Agent, Documentation
  Auditor Agent.
approvals: Merge to main requires explicit authorization (AUTONOMY_PROTOCOL.md).
evidence: PR diff, CI results, test output.
outputs: Merged (once authorized) feature, updated BACKLOG.md/work state.
failure_behavior: Stop at the failing step; do not merge; report the exact error.
audit_events: Not yet implemented — will map to Governance Core audit events once Phase 3
  exists.
```

```text
workflow_id: WF-BUG-FIX
name: Bug fix
trigger: A confirmed defect, filed as a BACKLOG.md task.
steps: Reproduce → root-cause → fix on a feature branch → regression test → PR → CI.
actors: Developer Brain/Agent, Test Engineer Agent.
approvals: Merge requires explicit authorization.
evidence: Reproduction steps, regression test, PR diff.
outputs: Fix PR with a test proving the defect is resolved and won't silently regress.
failure_behavior: If root cause is unclear, this is a real technical blocker
  (AUTONOMY_PROTOCOL.md stop condition), not a guess-and-patch situation.
audit_events: Not yet implemented.
```

```text
workflow_id: WF-SECURITY-INCIDENT
name: Security incident
trigger: A Critical/High finding from Security Reviewer Agent or Risk and Audit Brain, or
  an external report.
steps: Contain (kill switch if needed, docs/26_KILL_SWITCH_SPEC.md) → assess → fix →
  verify → postmortem.
actors: Risk and Audit Brain, Security Reviewer Agent, Owner (for kill-switch activation).
approvals: Kill-switch activation is Owner-authenticated, independent of Governance
  availability (docs/26_KILL_SWITCH_SPEC.md).
evidence: Incident timeline, kill-switch event, fix PR, postmortem.
outputs: Contained incident, documented postmortem, fix merged once authorized.
failure_behavior: Never narrate a partial fix as resolution (Constitution Article III.9).
audit_events: kill_switch_activated / kill_switch_recovered once Phase 3 exists; today,
  manual incident log.
```

```text
workflow_id: WF-ADR-CREATION
name: ADR creation
trigger: An architectural decision needing a durable record (per `templates/ADR.md`).
steps: Draft using templates/ADR.md → context/decision/alternatives/consequences →
  security/financial impact → evidence → propose for ratification.
actors: The Brain/Agent proposing the decision; Owner ratifies.
approvals: Owner ratification required before Status moves from Proposed to Ratified.
evidence: The ADR document itself, referenced evidence (test output, prior art).
outputs: A new `docs/ADR/ADR-NNNN-*.md` file.
failure_behavior: An ADR proposing a Charter/Constitution/Kernel change is itself a stop
  condition requiring direct Owner engagement, not autonomous drafting-to-ratification.
audit_events: Git history is the audit trail for ADRs.
```

```text
workflow_id: WF-RELEASE
name: Release
trigger: A merged PR set that constitutes a coherent version per `CHANGELOG.md` convention.
steps: Update CHANGELOG.md/PROJECT_STATE.md → verify CI green → tag → push tag.
actors: Developer Brain/Agent prepares; Owner authorizes the tag (AUTONOMY_PROTOCOL.md —
  "a release tag, unless expressly authorized" is a stop condition).
approvals: Explicit Owner authorization for the tag itself, every time.
evidence: CI results, verifier output, protected-file diff-empty checks.
outputs: A new Git tag.
failure_behavior: No tag is created if any verifier or CI check fails.
audit_events: Git tag + CHANGELOG.md entry.
```

```text
workflow_id: WF-KNOWLEDGE-INGESTION
name: Knowledge ingestion
trigger: A new source document or research output needing Vault representation.
steps: Extract → classify (type/authority/date/confidence/sensitivity) → draft Vault note →
  human review → promote.
actors: Research Agent, Knowledge Curator Agent; Owner or delegated reviewer promotes.
approvals: A generated note cannot mark itself reviewed/approved (Constitution Article
  V.5).
evidence: Source document, provenance metadata.
outputs: A reviewed Vault note.
failure_behavior: An unreviewable or unsourced claim stays flagged, not promoted.
audit_events: Vault note history (Git-backed once Vault sync exists, Phase 4).
```

```text
workflow_id: WF-AGENT-CREATION
name: Agent creation
trigger: A gap identified in `docs/AGENT_REGISTRY.md` for a needed capability.
steps: Propose spec (agent_id, parent Brain, scope, permissions, prohibitions) → review →
  ratify via ADR if it changes authority boundaries → implement (future phase).
actors: Developer Brain proposes; Governance Brain reviews; Owner ratifies if authority-
  relevant.
approvals: Any new agent expanding tool/permission scope requires Owner ratification
  (`docs/SELF_EVOLUTION_PROTOCOL.md` — Prohibited without Owner: "propose new agents" is
  allowed, activating one with expanded scope is not, without Owner sign-off).
evidence: The agent's registry entry, an ADR if authority-relevant.
outputs: A new `docs/AGENT_REGISTRY.md` entry, status `specified`.
failure_behavior: An agent proposal implying self-approval or Class D capability is refused
  outright.
audit_events: Git history for the registry change.
```

```text
workflow_id: WF-SKILL-CREATION
name: Skill creation
trigger: A gap identified in `docs/SKILL_CATALOG.md`.
steps: Propose spec (skill_id, owner Brain, purpose, inputs/outputs, tools, risks, tests) →
  review → catalog.
actors: The Brain identifying the gap; Documentation Auditor Agent reviews consistency.
approvals: Cataloging alone needs no Owner approval (derived documentation, autonomy-
  permitted); activation/implementation follows the skill-evolution pipeline in
  `docs/09_SKILL_EVOLUTION_PIPELINE.md` and `docs/SELF_EVOLUTION_PROTOCOL.md`.
evidence: The skill's catalog entry.
outputs: A new `docs/SKILL_CATALOG.md` entry, status `cataloged`.
failure_behavior: A skill proposal is never auto-promoted to production
  (`docs/09_SKILL_EVOLUTION_PIPELINE.md`).
audit_events: Git history for the catalog change.
```

```text
workflow_id: WF-POLICY-CHANGE
name: Policy change
trigger: A proposed change to the Policy Engine's rule bundle (not the Kernel).
steps: Draft rule change → run mandatory test suite → equivalence test against prior
  version → propose new policy_version → Owner ratifies.
actors: Governance Brain, Policy Test Agent; Owner ratifies.
approvals: Explicit Owner ratification before the new version becomes active
  (`docs/22_POLICY_ENGINE_EVALUATION.md` — Mandatory tests).
evidence: Test suite results, equivalence-test diff.
outputs: A new active `policy_version`.
failure_behavior: Any test-suite failure or Kernel conflict blocks activation.
audit_events: policy_decision events reference the new `policy_version` once active
  (Phase 3+).
```

```text
workflow_id: WF-SECRET-ROTATION
name: Secret rotation
trigger: Scheduled rotation window (e.g. 90-day capability-signing key rotation,
  ADR-0011) or a suspected compromise.
steps: Generate new key/secret in KMS/HSM/Vault → publish new public material (e.g. JWKS)
  → run overlap window → retire old material.
actors: Owner or delegated Approval Authority only — this is Class C
  (`docs/21_GOVERNANCE_CORE_SPEC.md` case #11).
approvals: Explicit Owner approval; a capability, not a standing permission.
evidence: Rotation event, overlap-window timestamps.
outputs: New active signing material; old material retired after the ceiling
  (24h for capability keys, ADR-0011).
failure_behavior: A rotation that cannot confirm the old key is safely retired blocks
  closure of the rotation task.
audit_events: capability_issued/capability_revoked-adjacent events once Phase 3 exists.
```

```text
workflow_id: WF-KILLSWITCH-TEST
name: Kill-switch test
trigger: Scheduled drill cadence (ADR-0011 — Kill Switch test cadence) or an ad hoc
  verification request.
steps: Announce as drill → activate the target level in the target environment → verify
  effects → recover → record event pair.
actors: Owner (activation/recovery authentication is Owner-only or explicitly delegated,
  `docs/26_KILL_SWITCH_SPEC.md`).
approvals: A real L5 activation drill requires separate, explicit Owner authorization
  beyond the standing cadence.
evidence: kill_switch_activated / kill_switch_recovered event pair, `reason` marked as
  drill.
outputs: Confirmed (or failed) kill-switch effect at the tested level.
failure_behavior: A failed drill is itself the finding — reported, not hidden, and treated
  as a Critical gap until fixed.
audit_events: kill_switch_activated, kill_switch_recovered.
```

```text
workflow_id: WF-TRADING-ANALYSIS
name: Trading analysis
trigger: A request for ICT-methodology bias/setup analysis.
steps: Fetch read-only market data → analyze per the Owner's ICT methodology → produce
  bias/setup report.
actors: Trading Analyst Agent.
approvals: None — Class A, read-only, automatic within budget.
evidence: Market data snapshot, analysis reasoning.
outputs: Bias/setup analysis for human decision-making.
failure_behavior: If asked to also execute a trade, refuse and escalate as Class D.
audit_events: Not yet implemented; will be a Class A execution_result once Phase 3+8 exist.
```

```text
workflow_id: WF-PROPFIRM-REVIEW
name: Prop-firm account review
trigger: Scheduled monitoring cadence or an ad hoc status request.
steps: Fetch read-only account data → compute drawdown/rule status → report.
actors: Prop Firm Risk Agent.
approvals: None — Class A, read-only.
evidence: Account data snapshot.
outputs: Status report, alerts if approaching breach.
failure_behavior: A data-feed failure is reported as unavailable, not silently skipped.
audit_events: Not yet implemented.
```

```text
workflow_id: WF-BLOCKCHAIN-REPORT
name: Blockchain intelligence report
trigger: A research/audit request.
steps: Gather on-chain data → analyze → cite → report.
actors: Blockchain Intelligence Agent.
approvals: None — Class A, read-only research.
evidence: On-chain data references.
outputs: Research/audit report.
failure_behavior: Insufficient evidence for a claim means the claim is marked uncertain,
  not asserted.
audit_events: Not yet implemented.
```

```text
workflow_id: WF-REGULATORY-UPDATE
name: Regulatory update
trigger: Scheduled monitoring cadence or a specific jurisdiction query.
steps: Monitor sources → digest changes → flag compliance-relevant items.
actors: Regulatory Monitor Agent.
approvals: None — Class A, read-only research.
evidence: Source citations, jurisdiction/date metadata.
outputs: Regulatory digest.
failure_behavior: Never presented as licensed legal/compliance advice.
audit_events: Not yet implemented.
```

```text
workflow_id: WF-COST-REVIEW
name: Cost review
trigger: Scheduled cadence or an anomalous-spend alert.
steps: Aggregate cost events → compare to budget caps → report variance.
actors: Cost Controller Agent.
approvals: Raising a budget cap itself is Class C, Owner-only.
evidence: Cost event log.
outputs: Cost/budget status report.
failure_behavior: An anomalous-spend signal triggers immediate reporting, not batching
  into the next scheduled cadence.
audit_events: budget_exceeded once Phase 3 exists.
```
