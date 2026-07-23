"""Shared canonical-checksum helper.

Identical algorithm to scripts/verify_invariant_kernel.py: normalize
CRLF/CR to LF, then SHA-256. This is the versioned-text-file
portability problem (docs/25_AUDIT_EVENT_MODEL.md distinguishes it
from the audit-event JCS canonicalization problem) — one method,
reused here for the policy bundle exactly as ADR-0012 requires,
not reinvented.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def canonical_text_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def canonical_sha256(path: Path) -> str:
    return hashlib.sha256(canonical_text_bytes(path)).hexdigest()
