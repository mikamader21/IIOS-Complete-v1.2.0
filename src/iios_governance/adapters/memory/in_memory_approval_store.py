from __future__ import annotations

from iios_governance.domain.models import Approval


class InMemoryApprovalStore:
    def __init__(self) -> None:
        self._approvals: dict[str, Approval] = {}

    def save(self, approval: Approval) -> None:
        self._approvals[approval.approval_id] = approval

    def get(self, approval_id: str) -> Approval | None:
        return self._approvals.get(approval_id)
