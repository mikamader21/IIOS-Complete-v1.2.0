"""Test-only fakes. NOT imported from anywhere under src/ — grep the
repository for "from tests" or "import tests" under src/ to confirm.

FakeSignatureVerifier and FakeSigner exist ONLY so capability
consumption logic can be exercised without real cryptography. They are
explicitly non-productive: FakeSigner's "signature" is not
cryptographically meaningful (HMAC over a fixed test-only shared
secret), and FakeSignatureVerifier only accepts signatures produced by
the matching FakeSigner instance.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

_TEST_ONLY_SHARED_SECRET = b"test-only-not-a-real-key-do-not-use-outside-tests"


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


class FakeSigner:
    """NOT a production signer. HMAC-SHA256 over a hardcoded test
    secret standing in for Ed25519. Used only to construct well-formed
    wire tokens in tests."""

    def __init__(self, kid: str = "test-kid-01") -> None:
        self.kid = kid

    def sign(self, header: dict, claims: dict) -> str:
        header_b64 = b64url_encode(
            json.dumps(header, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        payload_b64 = b64url_encode(
            json.dumps(claims, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        sig = hmac.new(_TEST_ONLY_SHARED_SECRET, signing_input, hashlib.sha256).digest()
        sig_b64 = b64url_encode(sig)
        return f"{header_b64}.{payload_b64}.{sig_b64}"


class FakeSignatureVerifier:
    """NOT a production verifier. Only accepts FakeSigner-produced
    signatures. Never imported from src/."""

    def verify(self, *, protected_b64: str, payload_b64: str, signature_b64: str, kid: str) -> bool:
        signing_input = f"{protected_b64}.{payload_b64}".encode("ascii")
        expected = hmac.new(_TEST_ONLY_SHARED_SECRET, signing_input, hashlib.sha256).digest()
        pad = "=" * (-len(signature_b64) % 4)
        presented = base64.urlsafe_b64decode(signature_b64 + pad)
        return hmac.compare_digest(expected, presented)


class DeterministicTestCanonicalizer:
    """NOT RFC 8785 JCS. A minimal sort-keys + compact-separators
    canonicalizer, deterministic enough for hash-chain tests but not
    a claim of JCS conformance. See ports/canonicalizer.py docstring."""

    def canonicalize(self, obj: dict) -> bytes:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
            "utf-8"
        )


@dataclass
class FixedClock:
    """Injectable clock — tests never depend on real wall-clock time."""

    _now: datetime = field(default_factory=lambda: datetime(2026, 1, 1, tzinfo=UTC))

    def now(self) -> datetime:
        return self._now

    def advance(self, **kwargs: float) -> None:
        self._now = self._now + timedelta(**kwargs)

    def set(self, dt: datetime) -> None:
        self._now = dt
