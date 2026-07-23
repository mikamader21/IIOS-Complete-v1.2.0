from __future__ import annotations

import pytest

from iios_governance.domain.kill_switch import KillSwitch, KillSwitchDeniedError, Level

_ALL_LEVELS: tuple[Level, ...] = ("L1", "L2", "L3", "L4", "L5")


@pytest.mark.parametrize("level", _ALL_LEVELS)
def test_activation_requires_owner_grade_auth(level: Level) -> None:
    ks = KillSwitch()
    with pytest.raises(KillSwitchDeniedError):
        ks.activate(
            level=level,
            scope_type="task",
            scope_ref="t1",
            actor="orchestrator",
            auth_method="signed_capability",  # not Owner-grade
            reason="test",
            now_iso="2026-01-01T00:00:00Z",
        )


@pytest.mark.parametrize("level", _ALL_LEVELS)
def test_activation_and_recovery_with_owner_auth(level: Level) -> None:
    ks = KillSwitch()
    ks.activate(
        level=level,
        scope_type="task",
        scope_ref="t1",
        actor="owner",
        auth_method="owner_session",
        reason="test drill",
        now_iso="2026-01-01T00:00:00Z",
    )
    assert level in ks.active_levels()

    ks.recover(
        level=level, actor="owner", auth_method="owner_session", now_iso="2026-01-01T00:05:00Z"
    )
    assert level not in ks.active_levels()


def test_l1_l2_block_only_matching_scope() -> None:
    ks = KillSwitch()
    ks.activate(
        level="L1",
        scope_type="task",
        scope_ref="task-A",
        actor="owner",
        auth_method="owner_session",
        reason="misbehaving task",
        now_iso="2026-01-01T00:00:00Z",
    )
    assert ks.is_blocking(scope_type="task", scope_ref="task-A") == "L1"
    assert ks.is_blocking(scope_type="task", scope_ref="task-B") is None


def test_l3_to_l5_block_everything() -> None:
    for level in ("L3", "L4", "L5"):
        ks = KillSwitch()
        ks.activate(
            level=level,
            scope_type="all_workers",
            scope_ref=None,
            actor="owner",
            auth_method="owner_session",
            reason="systemic issue",
            now_iso="2026-01-01T00:00:00Z",
        )
        assert ks.is_blocking(scope_type="task", scope_ref="anything") == level
        assert ks.is_blocking(scope_type="actor", scope_ref="someone-else") == level


def test_recovery_requires_owner_grade_auth() -> None:
    ks = KillSwitch()
    ks.activate(
        level="L1",
        scope_type="task",
        scope_ref="t1",
        actor="owner",
        auth_method="owner_session",
        reason="test",
        now_iso="2026-01-01T00:00:00Z",
    )
    with pytest.raises(KillSwitchDeniedError):
        ks.recover(
            level="L1",
            actor="orchestrator",
            auth_method="signed_capability",
            now_iso="2026-01-01T00:05:00Z",
        )
    # Still active — a denied recovery attempt has no effect.
    assert "L1" in ks.active_levels()


def test_recovering_inactive_level_raises() -> None:
    ks = KillSwitch()
    with pytest.raises(ValueError):
        ks.recover(
            level="L2", actor="owner", auth_method="owner_session", now_iso="2026-01-01T00:00:00Z"
        )


def test_kill_switch_has_no_delete_method_for_logs() -> None:
    # Structural: this module exposes no way to delete or truncate
    # anything — confirmed by checking its public surface.
    public_methods = {name for name in dir(KillSwitch) if not name.startswith("_")}
    assert not any("delete" in m or "purge" in m or "clear" in m for m in public_methods)
