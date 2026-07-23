from __future__ import annotations

import json

import pytest

from iios_governance.adapters.memory.in_memory_capability_store import InMemoryCapabilityStore
from iios_governance.domain.capability_service import (
    CapabilityDenied,
    CapabilityService,
    ConsumptionContext,
    DisabledSignatureVerifier,
    parse_i_json,
    validate_token_shape,
)
from iios_governance.domain.errors import CryptoNotImplementedError
from iios_governance.domain.reason_codes import (
    CAPABILITY_ALGORITHM_DENIED,
    CAPABILITY_AUDIENCE_MISMATCH,
    CAPABILITY_CRYPTO_NOT_IMPLEMENTED,
    CAPABILITY_EXPIRED,
    CAPABILITY_MALFORMED,
    CAPABILITY_NOT_YET_VALID,
    CAPABILITY_POLICY_MISMATCH,
    CAPABILITY_REPLAY_DENIED,
    CAPABILITY_RESOURCE_MISMATCH,
    CAPABILITY_REVOKED,
    CAPABILITY_SIGNATURE_INVALID,
    CAPABILITY_TYPE_DENIED,
)
from tests.governance.fakes import FakeSignatureVerifier, FakeSigner, FixedClock

HEADER = {"alg": "Ed25519", "kid": "test-kid-01", "typ": "iios-capability+jws"}


def _claims(clock: FixedClock, **overrides) -> dict:
    base = {
        "capability_id": "11111111-1111-1111-1111-111111111111",
        "issuer": "iios-governance-api:test",
        "subject": "actor-1",
        "audience": "executor-1",
        "action": "merge:git_protected_branch",
        "resource": "repo:example:branch:feature/x",
        "environment": "staging",
        "policy_version": "0.1.0-mvp",
        "issued_at": clock.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "not_before": clock.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "expires_at": (clock.now()).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "max_uses": 1,
        "correlation_id": "22222222-2222-2222-2222-222222222222",
        "nonce": "33333333-3333-3333-3333-333333333333",
    }
    base.update(overrides)
    return base


@pytest.fixture
def capability_service(
    capability_store: InMemoryCapabilityStore, clock: FixedClock, schema
) -> CapabilityService:
    return CapabilityService(
        store=capability_store,
        clock=clock,
        signature_verifier=FakeSignatureVerifier(),
        header_schema=schema("capability-protected-header.schema.json"),
        claims_schema=schema("capability-claims.schema.json"),
    )


def _default_ctx(claims: dict) -> ConsumptionContext:
    return ConsumptionContext(
        presenting_actor=claims["subject"],
        presenting_audience=claims["audience"],
        expected_resource=claims["resource"],
        expected_action=claims["action"],
        expected_environment=claims["environment"],
        active_policy_version=claims["policy_version"],
        active_kids=frozenset({"test-kid-01"}),
    )


def test_parse_i_json_rejects_duplicate_keys() -> None:
    with pytest.raises(ValueError):
        parse_i_json('{"a": 1, "a": 2}')


def test_parse_i_json_rejects_nan_and_infinity() -> None:
    with pytest.raises(ValueError):
        parse_i_json('{"a": NaN}')
    with pytest.raises(ValueError):
        parse_i_json('{"a": Infinity}')
    with pytest.raises(ValueError):
        parse_i_json('{"a": -Infinity}')


def test_parse_i_json_accepts_well_formed() -> None:
    assert parse_i_json('{"a": 1, "b": "x"}') == {"a": 1, "b": "x"}


def test_token_shape_validation() -> None:
    assert validate_token_shape("a.b.c") is True
    assert validate_token_shape("a.b") is False
    assert validate_token_shape("a.b.c.d") is False
    assert validate_token_shape("a b.c.d") is False
    assert validate_token_shape("a.b.c=") is False  # no padding chars allowed


def test_full_issue_and_consume_cycle(
    capability_service: CapabilityService, clock: FixedClock
) -> None:
    claims = _claims(clock)
    clock.advance(minutes=0)
    claims["expires_at"] = clock.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    clock.set(clock.now())  # ensure not_before == now, then advance for expiry window
    claims["not_before"] = clock.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    from datetime import timedelta

    future = clock.now() + timedelta(minutes=2)
    claims["expires_at"] = future.strftime("%Y-%m-%dT%H:%M:%SZ")

    capability_service.register(claims)
    token = FakeSigner(kid="test-kid-01").sign(HEADER, claims)

    result = capability_service.verify_and_consume(token, _default_ctx(claims))
    assert result["capability_id"] == claims["capability_id"]


def test_malformed_token_rejected(capability_service: CapabilityService, clock: FixedClock) -> None:
    claims = _claims(clock)
    with pytest.raises(CapabilityDenied) as exc:
        capability_service.verify_and_consume("not-a-valid-token", _default_ctx(claims))
    assert exc.value.reason_code == CAPABILITY_MALFORMED


def test_algorithm_downgrade_rejected(
    capability_service: CapabilityService, clock: FixedClock
) -> None:
    from datetime import timedelta

    claims = _claims(clock)
    claims["expires_at"] = (clock.now() + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    capability_service.register(claims)
    bad_header = {**HEADER, "alg": "EdDSA"}
    token = FakeSigner(kid="test-kid-01").sign(bad_header, claims)
    with pytest.raises(CapabilityDenied) as exc:
        capability_service.verify_and_consume(token, _default_ctx(claims))
    assert exc.value.reason_code == CAPABILITY_ALGORITHM_DENIED


def test_wrong_typ_rejected(capability_service: CapabilityService, clock: FixedClock) -> None:
    from datetime import timedelta

    claims = _claims(clock)
    claims["expires_at"] = (clock.now() + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    capability_service.register(claims)
    bad_header = {**HEADER, "typ": "something-else"}
    token = FakeSigner(kid="test-kid-01").sign(bad_header, claims)
    with pytest.raises(CapabilityDenied) as exc:
        capability_service.verify_and_consume(token, _default_ctx(claims))
    assert exc.value.reason_code == CAPABILITY_TYPE_DENIED


def test_unknown_kid_rejected(capability_service: CapabilityService, clock: FixedClock) -> None:
    from datetime import timedelta

    claims = _claims(clock)
    claims["expires_at"] = (clock.now() + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    capability_service.register(claims)
    bad_header = {**HEADER, "kid": "unknown-kid"}
    token = FakeSigner(kid="unknown-kid").sign(bad_header, claims)
    with pytest.raises(CapabilityDenied) as exc:
        capability_service.verify_and_consume(token, _default_ctx(claims))
    assert exc.value.reason_code == "CAPABILITY_KEY_UNKNOWN"


def test_tampered_payload_fails_signature(
    capability_service: CapabilityService, clock: FixedClock
) -> None:
    from datetime import timedelta

    claims = _claims(clock)
    claims["expires_at"] = (clock.now() + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    capability_service.register(claims)
    token = FakeSigner(kid="test-kid-01").sign(HEADER, claims)

    protected, payload, sig = token.split(".")
    tampered_claims = {**claims, "resource": "repo:example:branch:OTHER"}
    import base64

    def b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    tampered_payload = b64url(
        json.dumps(tampered_claims, sort_keys=True, separators=(",", ":")).encode()
    )
    tampered_token = f"{protected}.{tampered_payload}.{sig}"

    with pytest.raises(CapabilityDenied) as exc:
        capability_service.verify_and_consume(tampered_token, _default_ctx(claims))
    assert exc.value.reason_code == CAPABILITY_SIGNATURE_INVALID


def test_expired_capability_denied(
    capability_service: CapabilityService, clock: FixedClock
) -> None:
    from datetime import timedelta

    claims = _claims(clock)
    claims["expires_at"] = (clock.now() + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    capability_service.register(claims)
    token = FakeSigner(kid="test-kid-01").sign(HEADER, claims)

    clock.advance(minutes=2)
    with pytest.raises(CapabilityDenied) as exc:
        capability_service.verify_and_consume(token, _default_ctx(claims))
    assert exc.value.reason_code == CAPABILITY_EXPIRED


def test_not_yet_valid_capability_denied(
    capability_service: CapabilityService, clock: FixedClock
) -> None:
    from datetime import timedelta

    claims = _claims(clock)
    claims["not_before"] = (clock.now() + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    claims["expires_at"] = (clock.now() + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    capability_service.register(claims)
    token = FakeSigner(kid="test-kid-01").sign(HEADER, claims)

    with pytest.raises(CapabilityDenied) as exc:
        capability_service.verify_and_consume(token, _default_ctx(claims))
    assert exc.value.reason_code == CAPABILITY_NOT_YET_VALID


def test_revoked_capability_denied(
    capability_service: CapabilityService, clock: FixedClock
) -> None:
    from datetime import timedelta

    claims = _claims(clock)
    claims["expires_at"] = (clock.now() + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    capability_service.register(claims)
    capability_service.revoke(claims["capability_id"])
    token = FakeSigner(kid="test-kid-01").sign(HEADER, claims)

    with pytest.raises(CapabilityDenied) as exc:
        capability_service.verify_and_consume(token, _default_ctx(claims))
    assert exc.value.reason_code == CAPABILITY_REVOKED


def test_replay_of_consumed_capability_denied(
    capability_service: CapabilityService, clock: FixedClock
) -> None:
    from datetime import timedelta

    claims = _claims(clock)
    claims["expires_at"] = (clock.now() + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    capability_service.register(claims)
    token = FakeSigner(kid="test-kid-01").sign(HEADER, claims)

    capability_service.verify_and_consume(token, _default_ctx(claims))
    with pytest.raises(CapabilityDenied) as exc:
        capability_service.verify_and_consume(token, _default_ctx(claims))
    assert exc.value.reason_code == CAPABILITY_REPLAY_DENIED


def test_audience_mismatch_denied(capability_service: CapabilityService, clock: FixedClock) -> None:
    from datetime import timedelta

    claims = _claims(clock)
    claims["expires_at"] = (clock.now() + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    capability_service.register(claims)
    token = FakeSigner(kid="test-kid-01").sign(HEADER, claims)

    ctx = _default_ctx(claims)
    bad_ctx = ConsumptionContext(**{**ctx.__dict__, "presenting_audience": "someone-else"})
    with pytest.raises(CapabilityDenied) as exc:
        capability_service.verify_and_consume(token, bad_ctx)
    assert exc.value.reason_code == CAPABILITY_AUDIENCE_MISMATCH


def test_policy_version_mismatch_denied(
    capability_service: CapabilityService, clock: FixedClock
) -> None:
    from datetime import timedelta

    claims = _claims(clock)
    claims["expires_at"] = (clock.now() + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    capability_service.register(claims)
    token = FakeSigner(kid="test-kid-01").sign(HEADER, claims)

    ctx = _default_ctx(claims)
    bad_ctx = ConsumptionContext(**{**ctx.__dict__, "active_policy_version": "9.9.9-different"})
    with pytest.raises(CapabilityDenied) as exc:
        capability_service.verify_and_consume(token, bad_ctx)
    assert exc.value.reason_code == CAPABILITY_POLICY_MISMATCH


def test_resource_mismatch_denied(capability_service: CapabilityService, clock: FixedClock) -> None:
    from datetime import timedelta

    claims = _claims(clock)
    claims["expires_at"] = (clock.now() + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    capability_service.register(claims)
    token = FakeSigner(kid="test-kid-01").sign(HEADER, claims)

    ctx = _default_ctx(claims)
    bad_ctx = ConsumptionContext(
        **{**ctx.__dict__, "expected_resource": "repo:example:branch:different"}
    )
    with pytest.raises(CapabilityDenied) as exc:
        capability_service.verify_and_consume(token, bad_ctx)
    assert exc.value.reason_code == CAPABILITY_RESOURCE_MISMATCH


def test_disabled_signature_verifier_fails_closed(clock: FixedClock, schema) -> None:
    from datetime import timedelta

    store = InMemoryCapabilityStore()
    service = CapabilityService(
        store=store,
        clock=clock,
        signature_verifier=DisabledSignatureVerifier(),
        header_schema=schema("capability-protected-header.schema.json"),
        claims_schema=schema("capability-claims.schema.json"),
    )
    claims = _claims(clock)
    claims["expires_at"] = (clock.now() + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    service.register(claims)
    token = FakeSigner(kid="test-kid-01").sign(HEADER, claims)

    with pytest.raises(CapabilityDenied) as exc:
        service.verify_and_consume(token, _default_ctx(claims))
    assert exc.value.reason_code == CAPABILITY_CRYPTO_NOT_IMPLEMENTED


def test_disabled_verifier_raises_crypto_not_implemented_directly() -> None:
    with pytest.raises(CryptoNotImplementedError):
        DisabledSignatureVerifier().verify(
            protected_b64="a", payload_b64="b", signature_b64="c", kid="k"
        )
