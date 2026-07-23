from __future__ import annotations

from typing import Protocol

from iios_governance.domain.models import Approval


class ApprovalStore(Protocol):
    def save(self, approval: Approval) -> None: ...

    def get(self, approval_id: str) -> Approval | None: ...
