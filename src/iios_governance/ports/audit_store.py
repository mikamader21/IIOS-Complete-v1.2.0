"""Append-only audit store port. No implementation may expose update/delete
(Constitution Article III.2; docs/25_AUDIT_EVENT_MODEL.md — Immutability)."""

from __future__ import annotations

from typing import Protocol

from iios_governance.domain.models import AuditEvent


class AuditStore(Protocol):
    def append(self, event: AuditEvent) -> None:
        """Append one event. Must raise, never silently drop, on failure."""
        ...

    def last_event_hash(self, *, partition: str) -> str:
        """Return the chain tip's event_hash for `partition`, or the
        genesis sentinel ('0'*64) if the partition is empty."""
        ...

    def iter_chain(self, *, partition: str) -> list[AuditEvent]:
        """Return the partition's events in append order."""
        ...
