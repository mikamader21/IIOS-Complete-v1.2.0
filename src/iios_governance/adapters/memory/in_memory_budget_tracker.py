from __future__ import annotations


class InMemoryBudgetTracker:
    """Test/skeleton-only. Real cost aggregation is Cost Governance's job
    (docs/12_COST_GOVERNANCE.md) — this adapter only lets a scope be
    marked exceeded for testing the pipeline's reaction to it."""

    def __init__(self) -> None:
        self._exceeded: set[str] = set()

    def mark_exceeded(self, scope: str) -> None:
        self._exceeded.add(scope)

    def clear(self, scope: str) -> None:
        self._exceeded.discard(scope)

    def is_exceeded(self, *, scope: str) -> bool:
        return scope in self._exceeded
