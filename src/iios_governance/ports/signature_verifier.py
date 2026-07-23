"""Signature verification port for capability wire tokens.

No production adapter is registered against this port in this
skeleton — see docs/23_CAPABILITY_MODEL.md Open questions (signing
format/key-custody not yet decided at the product level) and
docs/30_GOVERNANCE_IMPLEMENTATION_SKELETON.md, "Components simulated."
The only concrete implementations are DisabledSignatureVerifier
(production-safe default: always fails closed) and
tests/governance/fakes.py's FakeSignatureVerifier (test-only, not
importable from src/).
"""

from __future__ import annotations

from typing import Protocol


class SignatureVerifier(Protocol):
    def verify(self, *, protected_b64: str, payload_b64: str, signature_b64: str, kid: str) -> bool:
        """Return True only if signature_b64 is a valid signature over
        f'{protected_b64}.{payload_b64}' under the key identified by kid.
        Must raise CryptoNotImplementedError, never return True, when
        real verification is unavailable."""
        ...
