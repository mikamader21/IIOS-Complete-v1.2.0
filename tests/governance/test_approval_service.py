from __future__ import annotations

import pytest

from iios_governance.domain.approval_service import ApprovalService
from iios_governance.domain.errors import SelfApprovalError
from iios_governance.domain.models import ApprovalState
from tests.governance.fakes import FixedClock


def test_approval_lifecycle_approve_then_consume(approval_service: ApprovalService) -> None:
    approval = approval_service.request_approval(
        request_id="r1", correlation_id="c1", requested_by="orchestrator-1", ttl_minutes=15
    )
    assert approval.state == ApprovalState.PENDING

    approved = approval_service.decide(
        approval_id=approval.approval_id,
        approver_id="owner",
        auth_method="owner_session",
        decision="approved",
    )
    assert approved.state == ApprovalState.APPROVED

    consumed = approval_service.consume(approval.approval_id)
    assert consumed.state == ApprovalState.CONSUMED


def test_self_approval_is_rejected(approval_service: ApprovalService) -> None:
    approval = approval_service.request_approval(
        request_id="r1", correlation_id="c1", requested_by="orchestrator-1", ttl_minutes=15
    )
    with pytest.raises(SelfApprovalError):
        approval_service.decide(
            approval_id=approval.approval_id,
            approver_id="orchestrator-1",  # same as requested_by
            auth_method="owner_session",
            decision="approved",
        )
    # The approval must remain pending — a rejected-at-the-gate attempt
    # is never recorded as a legitimate decision.
    assert approval_service.get_state(approval.approval_id) == ApprovalState.PENDING


def test_expired_approval_cannot_be_approved(
    approval_service: ApprovalService, clock: FixedClock
) -> None:
    approval = approval_service.request_approval(
        request_id="r1", correlation_id="c1", requested_by="orchestrator-1", ttl_minutes=15
    )
    clock.advance(minutes=16)

    assert approval_service.get_state(approval.approval_id) == ApprovalState.EXPIRED
    with pytest.raises(ValueError):
        approval_service.decide(
            approval_id=approval.approval_id,
            approver_id="owner",
            auth_method="owner_session",
            decision="approved",
        )


def test_double_consumption_is_rejected(approval_service: ApprovalService) -> None:
    approval = approval_service.request_approval(
        request_id="r1", correlation_id="c1", requested_by="orchestrator-1", ttl_minutes=15
    )
    approval_service.decide(
        approval_id=approval.approval_id,
        approver_id="owner",
        auth_method="owner_session",
        decision="approved",
    )
    approval_service.consume(approval.approval_id)

    with pytest.raises(ValueError):
        approval_service.consume(approval.approval_id)


def test_rejected_approval_cannot_be_consumed(approval_service: ApprovalService) -> None:
    approval = approval_service.request_approval(
        request_id="r1", correlation_id="c1", requested_by="orchestrator-1", ttl_minutes=15
    )
    approval_service.decide(
        approval_id=approval.approval_id,
        approver_id="owner",
        auth_method="owner_session",
        decision="rejected",
    )
    assert approval_service.get_state(approval.approval_id) == ApprovalState.REJECTED
    with pytest.raises(ValueError):
        approval_service.consume(approval.approval_id)


def test_revocation_after_approval(approval_service: ApprovalService) -> None:
    approval = approval_service.request_approval(
        request_id="r1", correlation_id="c1", requested_by="orchestrator-1", ttl_minutes=15
    )
    approval_service.decide(
        approval_id=approval.approval_id,
        approver_id="owner",
        auth_method="owner_session",
        decision="approved",
    )
    revoked = approval_service.revoke(
        approval.approval_id, revoked_by="owner", reason="test revocation"
    )
    assert revoked.state == ApprovalState.REVOKED


def test_unknown_approval_id_raises_on_every_operation(approval_service: ApprovalService) -> None:
    for op in (
        lambda: approval_service.decide(
            approval_id="nope", approver_id="x", auth_method="owner_session", decision="approved"
        ),
        lambda: approval_service.consume("nope"),
        lambda: approval_service.revoke("nope", revoked_by="x", reason="y"),
        lambda: approval_service.get_state("nope"),
    ):
        with pytest.raises(ValueError):
            op()


def test_cannot_consume_a_pending_approval(approval_service: ApprovalService) -> None:
    approval = approval_service.request_approval(
        request_id="r1", correlation_id="c1", requested_by="orchestrator-1", ttl_minutes=15
    )
    with pytest.raises(ValueError):
        approval_service.consume(approval.approval_id)


def test_cannot_revoke_a_pending_approval(approval_service: ApprovalService) -> None:
    approval = approval_service.request_approval(
        request_id="r1", correlation_id="c1", requested_by="orchestrator-1", ttl_minutes=15
    )
    with pytest.raises(ValueError):
        approval_service.revoke(approval.approval_id, revoked_by="owner", reason="test")


def test_approval_service_uses_injectable_clock_only(
    approval_service: ApprovalService, clock: FixedClock
) -> None:
    approval = approval_service.request_approval(
        request_id="r1", correlation_id="c1", requested_by="orchestrator-1", ttl_minutes=15
    )
    assert approval.created_at == clock.now().strftime("%Y-%m-%dT%H:%M:%SZ")
