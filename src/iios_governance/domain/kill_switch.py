"""Kill Switch. docs/26_KILL_SWITCH_SPEC.md.

Standalone — does not depend on the Orchestrator or GovernanceService;
GovernanceService queries it, never the reverse. Activation/recovery
authentication is independent of Governance API availability by
design (a kill switch that needs the thing it might kill to be
healthy first is not a kill switch).

Logs are never deleted. Every activation/recovery is expected to be
recorded to the AuditChain by the caller (application layer) — this
module does not delete or bypass that; it has no delete path at all.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Level = Literal["L1", "L2", "L3", "L4", "L5"]
_VALID_LEVELS: tuple[Level, ...] = ("L1", "L2", "L3", "L4", "L5")
_VALID_AUTH_METHODS = frozenset({"owner_session", "owner_out_of_band", "delegated_token"})


@dataclass
class KillSwitchActivation:
    level: Level
    scope_type: str
    scope_ref: str | None
    actor: str
    auth_method: str
    reason: str
    activated_at: str
    recovered_at: str | None = None


class KillSwitchDeniedError(Exception):
    pass


class KillSwitch:
    def __init__(self) -> None:
        self._active: dict[Level, KillSwitchActivation] = {}

    def activate(
        self,
        *,
        level: Level,
        scope_type: str,
        scope_ref: str | None,
        actor: str,
        auth_method: str,
        reason: str,
        now_iso: str,
    ) -> KillSwitchActivation:
        if level not in _VALID_LEVELS:
            raise ValueError(f"invalid level {level!r}")
        if auth_method not in _VALID_AUTH_METHODS:
            raise KillSwitchDeniedError(
                "kill switch activation requires Owner-grade authentication"
            )
        activation = KillSwitchActivation(
            level=level,
            scope_type=scope_type,
            scope_ref=scope_ref,
            actor=actor,
            auth_method=auth_method,
            reason=reason,
            activated_at=now_iso,
        )
        self._active[level] = activation
        return activation

    def recover(
        self, *, level: Level, actor: str, auth_method: str, now_iso: str
    ) -> KillSwitchActivation:
        if auth_method not in _VALID_AUTH_METHODS:
            raise KillSwitchDeniedError("kill switch recovery requires Owner-grade authentication")
        activation = self._active.get(level)
        if activation is None:
            raise ValueError(f"level {level} is not active")
        activation.recovered_at = now_iso
        del self._active[level]
        return activation

    def is_blocking(self, *, scope_type: str, scope_ref: str | None) -> Level | None:
        """Returns the blocking level, if any, for the given request scope."""
        for level, activation in self._active.items():
            if level in ("L3", "L4", "L5"):
                return level  # blocks everything
            if activation.scope_type == scope_type and activation.scope_ref == scope_ref:
                return level  # L1/L2 — scope-matched only
        return None

    def active_levels(self) -> tuple[Level, ...]:
        return tuple(sorted(self._active.keys()))
