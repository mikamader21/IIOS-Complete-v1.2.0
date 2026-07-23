"""Canonicalization port for the audit hash chain.

RFC 8785 (JSON Canonicalization Scheme) is REQUIRED for production per
docs/25_AUDIT_EVENT_MODEL.md and docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md.
No production adapter is registered against this port in this skeleton —
no RFC 8785-conformant, independently maintained Python library could be
verified with sufficient confidence during this task (see
docs/30_GOVERNANCE_IMPLEMENTATION_SKELETON.md, "Components simulated").
Only a test-only, explicitly non-conformant canonicalizer exists
(tests/governance/fakes.py), never imported from src/.
"""

from __future__ import annotations

from typing import Any, Protocol


class Canonicalizer(Protocol):
    def canonicalize(self, obj: dict[str, Any]) -> bytes:
        """Return canonical UTF-8 bytes for obj. Must be deterministic:
        same logical value in, same bytes out, regardless of key
        insertion order."""
        ...
