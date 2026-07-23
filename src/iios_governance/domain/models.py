"""Typed in-process representations mirroring governance/schemas/*.json.

These are internal convenience types for the domain logic. The JSON
Schemas in governance/schemas/ remain the normative wire contracts;
these dataclasses are constructed only from data that already passed
schema validation (see application/decision_pipeline.py).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ActionClass(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"

    def is_stricter_than(self, other: ActionClass) -> bool:
        order = {ActionClass.A: 0, ActionClass.B: 1, ActionClass.C: 2, ActionClass.D: 3}
        return order[self] > order[other]


class DecisionOutcome(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"

    @property
    def strictness(self) -> int:
        # Higher = stricter/safer. Used to combine multiple item outcomes
        # into one overall_decision per docs/21_GOVERNANCE_CORE_SPEC.md.
        return {"allow": 0, "require_approval": 1, "deny": 2}[self.value]


class ApprovalState(StrEnum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"
    CONSUMED = "consumed"


@dataclass(frozen=True)
class Actor:
    actor_id: str
    actor_type: str
    auth_method: str
    on_behalf_of: str | None = None


@dataclass(frozen=True)
class ActionItem:
    item_id: str
    verb: str
    resource_type: str
    resource_ref: str
    environment: str
    reason: str | None = None
    risk_signals: tuple[str, ...] = ()


@dataclass(frozen=True)
class ActionRequest:
    request_id: str
    idempotency_key: str
    correlation_id: str
    actor: Actor
    requested_at: str
    items: tuple[ActionItem, ...]
    budget_context: dict[str, Any] | None = None
    classifier_hint: dict[str, Any] | None = None
    decomposable: bool = False


@dataclass(frozen=True)
class ItemDecision:
    item_id: str
    action_class: ActionClass
    outcome: DecisionOutcome
    reason_codes: tuple[str, ...]
    matched_invariants: tuple[str, ...] = ()
    matched_rules: tuple[str, ...] = ()
    approval_id: str | None = None
    capability_id: str | None = None


@dataclass(frozen=True)
class PolicyDecision:
    decision_id: str
    request_id: str
    correlation_id: str
    idempotency_key: str
    policy_version: str
    kernel_checksum: str
    evaluated_at: str
    item_decisions: tuple[ItemDecision, ...]
    overall_decision: DecisionOutcome
    reason_codes: tuple[str, ...] = ()
    replayed: bool = False
    explanation: str = ""
    fail_closed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "idempotency_key": self.idempotency_key,
            "policy_version": self.policy_version,
            "kernel_checksum": self.kernel_checksum,
            "evaluated_at": self.evaluated_at,
            "replayed": self.replayed,
            "overall_decision": self.overall_decision.value,
            "item_decisions": [
                {
                    "item_id": d.item_id,
                    "action_class": d.action_class.value,
                    "outcome": d.outcome.value,
                    "reason_codes": list(d.reason_codes),
                    "matched_invariants": list(d.matched_invariants),
                    "matched_rules": list(d.matched_rules),
                    "approval_id": d.approval_id,
                    "capability_id": d.capability_id,
                }
                for d in self.item_decisions
            ],
            "reason_codes": list(self.reason_codes),
            "explanation": self.explanation,
            "fail_closed": self.fail_closed,
        }


@dataclass
class Approval:
    approval_id: str
    request_id: str
    correlation_id: str
    requested_by: str
    state: ApprovalState
    created_at: str
    expires_at: str
    required_approvals: int = 1
    decisions: list[dict[str, Any]] = field(default_factory=list)
    evidence_ref: str | None = None
    decided_at: str | None = None
    revoked_at: str | None = None
    revoked_by: str | None = None
    revocation_reason: str | None = None
    consumed_at: str | None = None


@dataclass
class CapabilityServerState:
    """Server-side consumption state. Deliberately separate from the
    signed claims — see docs/23_CAPABILITY_MODEL.md 'What is NOT in the
    payload, and why'."""

    capability_id: str
    max_uses: int
    uses_remaining: int
    revoked: bool = False
    revoked_at: str | None = None
    consumed_nonces: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    event_type: str
    timestamp: str
    actor: str
    correlation_id: str
    previous_event_hash: str
    request_id: str | None = None
    action_class: str | None = None
    policy_version: str | None = None
    decision: str | None = None
    reason_codes: tuple[str, ...] = ()
    approval_id: str | None = None
    capability_id: str | None = None
    tool: str | None = None
    resource: str | None = None
    result: str | None = None
    cost: dict[str, str] | None = None
    evidence: dict[str, Any] | None = None
    event_hash: str = ""

    def to_dict(self, *, include_hash: bool = True) -> dict[str, Any]:
        d = {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "action_class": self.action_class,
            "policy_version": self.policy_version,
            "decision": self.decision,
            "reason_codes": list(self.reason_codes),
            "approval_id": self.approval_id,
            "capability_id": self.capability_id,
            "tool": self.tool,
            "resource": self.resource,
            "result": self.result,
            "cost": self.cost,
            "evidence": self.evidence,
            "previous_event_hash": self.previous_event_hash,
        }
        if include_hash:
            d["event_hash"] = self.event_hash
        return d


GENESIS_HASH = "0" * 64
