from __future__ import annotations

from iios_governance.domain.models import PolicyDecision


class InMemoryIdempotencyStore:
    def __init__(self) -> None:
        self._cache: dict[str, PolicyDecision] = {}

    def get(self, key_scope: str) -> PolicyDecision | None:
        return self._cache.get(key_scope)

    def put(self, key_scope: str, decision: PolicyDecision) -> None:
        self._cache[key_scope] = decision
