"""Append-only, hash-chained audit events.

docs/25_AUDIT_EVENT_MODEL.md:
  - event_hash = SHA-256(canonicalize(event without event_hash)), where
    canonicalize is RFC 8785 JCS in production (not implemented here —
    see ports/canonicalizer.py). previous_event_hash IS included in
    the hashed material.
  - genesis event: previous_event_hash = '0'*64.
  - chain verification: recompute each event_hash, confirm linkage.
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Any

from iios_governance.domain.models import GENESIS_HASH, AuditEvent
from iios_governance.ports.audit_store import AuditStore
from iios_governance.ports.canonicalizer import Canonicalizer
from iios_governance.ports.clock import Clock

_ISO = "%Y-%m-%dT%H:%M:%SZ"


class AuditChain:
    def __init__(self, store: AuditStore, canonicalizer: Canonicalizer, clock: Clock) -> None:
        self._store = store
        self._canonicalizer = canonicalizer
        self._clock = clock

    def append(
        self, *, partition: str, event_type: str, actor: str, correlation_id: str, **fields: Any
    ) -> AuditEvent:
        previous_hash = self._store.last_event_hash(partition=partition)
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=self._clock.now().strftime(_ISO),
            actor=actor,
            correlation_id=correlation_id,
            previous_event_hash=previous_hash,
            **fields,
        )
        payload = event.to_dict(include_hash=False)
        digest = hashlib.sha256(self._canonicalizer.canonicalize(payload)).hexdigest()
        event = AuditEvent(
            **{**payload, "reason_codes": tuple(payload["reason_codes"]), "event_hash": digest}
        )
        self._store.append(event)
        return event

    def verify_chain(self, *, partition: str) -> tuple[bool, int | None]:
        """Returns (ok, index_of_first_break_or_None). Recomputes every
        event_hash and confirms previous_event_hash linkage."""
        events = self._store.iter_chain(partition=partition)
        expected_previous = GENESIS_HASH
        for i, event in enumerate(events):
            if event.previous_event_hash != expected_previous:
                return False, i
            payload = event.to_dict(include_hash=False)
            recomputed = hashlib.sha256(self._canonicalizer.canonicalize(payload)).hexdigest()
            if recomputed != event.event_hash:
                return False, i
            expected_previous = event.event_hash
        return True, None
