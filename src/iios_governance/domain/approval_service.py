"""Approval state machine. docs/24_APPROVAL_MODEL.md.

States: not_required, pending, approved, rejected, expired, revoked, consumed.
Self-approval is a Policy-Engine/Approval-Service check, NEVER a JSON
Schema constraint (Draft 2020-12 cannot express cross-field equality —
see docs/24_APPROVAL_MODEL.md 'Self-approval prevention'). This module
is exactly that check, enforced twice per the ratified design: once
here at decision time, and again by whatever calls consume() at
consumption time.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from iios_governance.domain.errors import SelfApprovalError
from iios_governance.domain.models import Approval, ApprovalState
from iios_governance.domain.reason_codes import (
    SELF_APPROVAL_FORBIDDEN,
)
from iios_governance.ports.approval_store import ApprovalStore
from iios_governance.ports.clock import Clock

_ISO = "%Y-%m-%dT%H:%M:%SZ"


def _fmt(dt: datetime) -> str:
    return dt.strftime(_ISO)


def _parse(s: str) -> datetime:
    # strptime produces a naive datetime; every timestamp in this
    # format is UTC ('Z' suffix), so attach tzinfo explicitly rather
    # than comparing naive-vs-aware (which raises TypeError).
    return datetime.strptime(s, _ISO).replace(tzinfo=UTC)


class ApprovalService:
    def __init__(self, store: ApprovalStore, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def request_approval(
        self,
        *,
        request_id: str,
        correlation_id: str,
        requested_by: str,
        ttl_minutes: int,
        evidence_ref: str | None = None,
    ) -> Approval:
        now = self._clock.now()
        approval = Approval(
            approval_id=str(uuid.uuid4()),
            request_id=request_id,
            correlation_id=correlation_id,
            requested_by=requested_by,
            state=ApprovalState.PENDING,
            created_at=_fmt(now),
            expires_at=_fmt(now + timedelta(minutes=ttl_minutes)),
            evidence_ref=evidence_ref,
        )
        self._store.save(approval)
        return approval

    def _expire_if_due(self, approval: Approval) -> Approval:
        if approval.state == ApprovalState.PENDING:
            now = self._clock.now()
            expires_at = _parse(approval.expires_at)
            if now >= expires_at:
                approval.state = ApprovalState.EXPIRED
                self._store.save(approval)
        return approval

    def decide(
        self,
        *,
        approval_id: str,
        approver_id: str,
        auth_method: str,
        decision: str,
        reason_code: str | None = None,
    ) -> Approval:
        approval = self._store.get(approval_id)
        if approval is None:
            raise ValueError(f"unknown approval_id {approval_id}")
        approval = self._expire_if_due(approval)

        if approver_id == approval.requested_by:
            # Structural rejection — never recorded as a legitimate decision.
            raise SelfApprovalError(SELF_APPROVAL_FORBIDDEN)

        if approval.state != ApprovalState.PENDING:
            raise ValueError(
                f"approval {approval_id} is not pending (state={approval.state.value})"
            )

        now = self._clock.now()
        approval.decisions.append(
            {
                "approver_id": approver_id,
                "auth_method": auth_method,
                "decision": decision,
                "reason_code": reason_code,
                "decided_at": _fmt(now),
            }
        )
        approval.decided_at = _fmt(now)
        approval.state = (
            ApprovalState.APPROVED if decision == "approved" else ApprovalState.REJECTED
        )
        self._store.save(approval)
        return approval

    def consume(self, approval_id: str) -> Approval:
        approval = self._store.get(approval_id)
        if approval is None:
            raise ValueError(f"unknown approval_id {approval_id}")
        approval = self._expire_if_due(approval)
        if approval.state != ApprovalState.APPROVED:
            raise ValueError(
                f"approval {approval_id} cannot be consumed from state={approval.state.value}"
            )
        approval.state = ApprovalState.CONSUMED
        approval.consumed_at = _fmt(self._clock.now())
        self._store.save(approval)
        return approval

    def revoke(self, approval_id: str, *, revoked_by: str, reason: str) -> Approval:
        approval = self._store.get(approval_id)
        if approval is None:
            raise ValueError(f"unknown approval_id {approval_id}")
        if approval.state not in (ApprovalState.APPROVED, ApprovalState.CONSUMED):
            raise ValueError(
                f"approval {approval_id} cannot be revoked from state={approval.state.value}"
            )
        approval.state = ApprovalState.REVOKED
        approval.revoked_at = _fmt(self._clock.now())
        approval.revoked_by = revoked_by
        approval.revocation_reason = reason
        self._store.save(approval)
        return approval

    def get_state(self, approval_id: str) -> ApprovalState:
        approval = self._store.get(approval_id)
        if approval is None:
            raise ValueError(f"unknown approval_id {approval_id}")
        return self._expire_if_due(approval).state
