"""Idempotency cache port.

Not one of the ports named in the Owner's suggested tree, but required
by the mandatory "duplicate request" test case and by
docs/21_GOVERNANCE_CORE_SPEC.md's Idempotency rule: a repeated
idempotency_key within the window returns the original decision rather
than re-evaluating.
"""

from __future__ import annotations

from typing import Protocol

from iios_governance.domain.models import PolicyDecision


class IdempotencyStore(Protocol):
    def get(self, key_scope: str) -> PolicyDecision | None: ...

    def put(self, key_scope: str, decision: PolicyDecision) -> None: ...
