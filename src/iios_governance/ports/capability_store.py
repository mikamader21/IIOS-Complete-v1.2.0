"""Server-side capability consumption state — deliberately separate from
the signed claims. See docs/23_CAPABILITY_MODEL.md."""

from __future__ import annotations

from typing import Protocol

from iios_governance.domain.models import CapabilityServerState


class CapabilityStore(Protocol):
    def create(self, state: CapabilityServerState) -> None: ...

    def get(self, capability_id: str) -> CapabilityServerState | None: ...

    def save(self, state: CapabilityServerState) -> None: ...
