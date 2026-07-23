from __future__ import annotations

from iios_governance.domain.models import CapabilityServerState


class InMemoryCapabilityStore:
    def __init__(self) -> None:
        self._states: dict[str, CapabilityServerState] = {}

    def create(self, state: CapabilityServerState) -> None:
        self._states[state.capability_id] = state

    def get(self, capability_id: str) -> CapabilityServerState | None:
        return self._states.get(capability_id)

    def save(self, state: CapabilityServerState) -> None:
        self._states[state.capability_id] = state
