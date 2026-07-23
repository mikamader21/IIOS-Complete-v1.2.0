"""Capability contracts: claims validation, protected-header validation,
wire-token surface validation, and the verification/consumption pipeline.

No production cryptography. Signature verification is delegated to an
injected SignatureVerifier port; the production wiring
(application/governance_service.py) must inject DisabledSignatureVerifier,
which always fails closed. Only tests inject a fake.

Consumption order mirrors docs/23_CAPABILITY_MODEL.md exactly:
  1. envelope shape  -> CAPABILITY_MALFORMED
  2. decode header   -> CAPABILITY_HEADER_INVALID / CAPABILITY_MALFORMED
  3. alg/typ/kid     -> CAPABILITY_ALGORITHM_DENIED / CAPABILITY_TYPE_DENIED /
                        CAPABILITY_KEY_UNKNOWN
  4. signature       -> CAPABILITY_SIGNATURE_INVALID (over the ORIGINAL bytes,
                        never re-canonicalized)
  5. decode claims   -> CAPABILITY_CLAIMS_INVALID
  6. audience/etc    -> CAPABILITY_AUDIENCE_MISMATCH / CAPABILITY_NOT_YET_VALID /
                        CAPABILITY_EXPIRED / CAPABILITY_POLICY_MISMATCH /
                        CAPABILITY_RESOURCE_MISMATCH
  7. server-side state -> CAPABILITY_REVOKED / CAPABILITY_REPLAY_DENIED
  8. atomic consume
"""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from jsonschema.validators import Draft202012Validator

from iios_governance.domain.errors import CryptoNotImplementedError
from iios_governance.domain.models import CapabilityServerState
from iios_governance.domain.reason_codes import (
    CAPABILITY_ALGORITHM_DENIED,
    CAPABILITY_AUDIENCE_MISMATCH,
    CAPABILITY_CLAIMS_INVALID,
    CAPABILITY_CRYPTO_NOT_IMPLEMENTED,
    CAPABILITY_EXPIRED,
    CAPABILITY_HEADER_INVALID,
    CAPABILITY_KEY_UNKNOWN,
    CAPABILITY_MALFORMED,
    CAPABILITY_NOT_YET_VALID,
    CAPABILITY_POLICY_MISMATCH,
    CAPABILITY_REPLAY_DENIED,
    CAPABILITY_RESOURCE_MISMATCH,
    CAPABILITY_REVOKED,
    CAPABILITY_SIGNATURE_INVALID,
    CAPABILITY_TYPE_DENIED,
)
from iios_governance.ports.capability_store import CapabilityStore
from iios_governance.ports.clock import Clock
from iios_governance.ports.signature_verifier import SignatureVerifier

_TOKEN_PATTERN = re.compile(r"^([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)$")
_ISO = "%Y-%m-%dT%H:%M:%SZ"


def _parse(s: str) -> datetime:
    # strptime produces a naive datetime; every timestamp in this format
    # is UTC ('Z' suffix), so attach tzinfo explicitly rather than
    # comparing naive-vs-aware (which raises TypeError).
    return datetime.strptime(s, _ISO).replace(tzinfo=UTC)


class CapabilityDenied(Exception):
    def __init__(self, reason_code: str) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code


def parse_i_json(text: str) -> dict[str, Any]:
    """Parse JSON enforcing the I-JSON (RFC 7493) subset required before
    RFC 8785 JCS canonicalization: no duplicate property names, no NaN/
    Infinity. See docs/23_CAPABILITY_MODEL.md 'I-JSON profile for JCS'."""

    def _reject_constant(token: str) -> float:
        raise ValueError(f"non-I-JSON numeric constant: {token}")

    def _dedupe_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        seen: set[str] = set()
        for key, _ in pairs:
            if key in seen:
                raise ValueError(f"duplicate property name: {key}")
            seen.add(key)
        return dict(pairs)

    return json.loads(text, object_pairs_hook=_dedupe_hook, parse_constant=_reject_constant)


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def validate_header_schema(header: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    return [f"{list(e.path)}: {e.message}" for e in validator.iter_errors(header)]


def validate_claims_schema(claims: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    return [f"{list(e.path)}: {e.message}" for e in validator.iter_errors(claims)]


def validate_token_shape(token: str) -> bool:
    return bool(_TOKEN_PATTERN.match(token))


@dataclass(frozen=True)
class ConsumptionContext:
    presenting_actor: str
    presenting_audience: str
    expected_resource: str
    expected_action: str
    expected_environment: str
    active_policy_version: str
    active_kids: frozenset[str]


class CapabilityService:
    def __init__(
        self,
        *,
        store: CapabilityStore,
        clock: Clock,
        signature_verifier: SignatureVerifier,
        header_schema: dict[str, Any],
        claims_schema: dict[str, Any],
    ) -> None:
        self._store = store
        self._clock = clock
        self._verifier = signature_verifier
        self._header_schema = header_schema
        self._claims_schema = claims_schema

    def register(self, claims: dict[str, Any]) -> None:
        """Register server-side consumption state at issuance time.
        Separate from signing — see docs/23_CAPABILITY_MODEL.md."""
        self._store.create(
            CapabilityServerState(
                capability_id=claims["capability_id"],
                max_uses=claims["max_uses"],
                uses_remaining=claims["max_uses"],
            )
        )

    def revoke(self, capability_id: str) -> None:
        state = self._store.get(capability_id)
        if state is None:
            raise ValueError(f"unknown capability_id {capability_id}")
        state.revoked = True
        state.revoked_at = self._clock.now().strftime(_ISO)
        self._store.save(state)

    def verify_and_consume(self, token: str, ctx: ConsumptionContext) -> dict[str, Any]:
        """Returns the validated claims dict on success. Raises
        CapabilityDenied(reason_code) on any failure — every branch
        fails closed, none fail open."""

        # 1. Envelope shape.
        match = _TOKEN_PATTERN.match(token)
        if not match:
            raise CapabilityDenied(CAPABILITY_MALFORMED)
        protected_b64, payload_b64, signature_b64 = match.groups()

        # 2. Decode + validate protected header — EXACTLY as received.
        try:
            header = parse_i_json(_b64url_decode(protected_b64).decode("utf-8"))
        except Exception as exc:
            raise CapabilityDenied(CAPABILITY_MALFORMED) from exc
        # 'alg' and 'typ' const-mismatches get their own specific reason
        # codes below (step 3) — every OTHER schema violation (missing
        # field, unknown/duplicate property, empty kid) is the generic
        # CAPABILITY_HEADER_INVALID.
        header_errors = [
            e
            for e in validate_header_schema(header, self._header_schema)
            if not e.startswith("['alg']") and not e.startswith("['typ']")
        ]
        if header_errors or "alg" not in header or "typ" not in header or "kid" not in header:
            raise CapabilityDenied(CAPABILITY_HEADER_INVALID)

        # 3. alg / typ / kid.
        if header["alg"] != "Ed25519":
            raise CapabilityDenied(CAPABILITY_ALGORITHM_DENIED)
        if header["typ"] != "iios-capability+jws":
            raise CapabilityDenied(CAPABILITY_TYPE_DENIED)
        if header["kid"] not in ctx.active_kids:
            raise CapabilityDenied(CAPABILITY_KEY_UNKNOWN)

        # 4. Signature over the ORIGINAL bytes — never re-canonicalized.
        try:
            valid = self._verifier.verify(
                protected_b64=protected_b64,
                payload_b64=payload_b64,
                signature_b64=signature_b64,
                kid=header["kid"],
            )
        except CryptoNotImplementedError as exc:
            raise CapabilityDenied(CAPABILITY_CRYPTO_NOT_IMPLEMENTED) from exc
        if not valid:
            raise CapabilityDenied(CAPABILITY_SIGNATURE_INVALID)

        # 5. Decode + validate claims — only after the signature verifies.
        try:
            claims = parse_i_json(_b64url_decode(payload_b64).decode("utf-8"))
        except Exception as exc:
            raise CapabilityDenied(CAPABILITY_CLAIMS_INVALID) from exc
        claims_errors = validate_claims_schema(claims, self._claims_schema)
        if claims_errors:
            raise CapabilityDenied(CAPABILITY_CLAIMS_INVALID)

        # 6. Claim checks.
        if (
            claims["subject"] != ctx.presenting_actor
            or claims["audience"] != ctx.presenting_audience
        ):
            raise CapabilityDenied(CAPABILITY_AUDIENCE_MISMATCH)
        now = self._clock.now()
        not_before = _parse(claims["not_before"])
        expires_at = _parse(claims["expires_at"])
        if now < not_before:
            raise CapabilityDenied(CAPABILITY_NOT_YET_VALID)
        if now >= expires_at:
            raise CapabilityDenied(CAPABILITY_EXPIRED)
        if claims["policy_version"] != ctx.active_policy_version:
            raise CapabilityDenied(CAPABILITY_POLICY_MISMATCH)
        if (
            claims["resource"] != ctx.expected_resource
            or claims["action"] != ctx.expected_action
            or claims["environment"] != ctx.expected_environment
        ):
            raise CapabilityDenied(CAPABILITY_RESOURCE_MISMATCH)

        # 7. Server-side state — revocation, uses, nonce replay.
        state = self._store.get(claims["capability_id"])
        if state is None:
            raise CapabilityDenied(CAPABILITY_REVOKED)  # never registered == cannot be honored
        if state.revoked:
            raise CapabilityDenied(CAPABILITY_REVOKED)
        if state.uses_remaining <= 0:
            raise CapabilityDenied(CAPABILITY_REPLAY_DENIED)
        if claims["nonce"] in state.consumed_nonces:
            raise CapabilityDenied(CAPABILITY_REPLAY_DENIED)

        # 8. Atomic consumption.
        state.uses_remaining -= 1
        state.consumed_nonces.add(claims["nonce"])
        self._store.save(state)

        return claims


class DisabledSignatureVerifier:
    """Production-safe default: always fails closed. No key material,
    no cryptography, no import of any signing library."""

    def verify(self, *, protected_b64: str, payload_b64: str, signature_b64: str, kid: str) -> bool:
        raise CryptoNotImplementedError(
            "Capability signing/verification is intentionally not implemented "
            "in this skeleton — see docs/30_GOVERNANCE_IMPLEMENTATION_SKELETON.md"
        )
