"""Budget tracking port.

Not one of the ports named in the Owner's suggested tree, but required
by the mandatory "budget exceeded" test case and
docs/21_GOVERNANCE_CORE_SPEC.md case #19. A real implementation is
Cost Governance's job (docs/12_COST_GOVERNANCE.md); this port only
lets the decision pipeline ask "is this scope over its cap right now."
"""

from __future__ import annotations

from typing import Protocol


class BudgetTracker(Protocol):
    def is_exceeded(self, *, scope: str) -> bool: ...
