"""RT-2 (RBAC) and RT-13 (emergency kill switch) core extensions.

Both `skills/llm-trading-agent-security/SKILL.md` and `skills/safety-guard/
SKILL.md` document circuit-breaker/guard patterns (consecutive-failure
thresholds, block-and-log behavior) but are markdown design docs with
illustrative or incomplete code -- not importable modules. `KillSwitch`
below is a new, complete implementation of that documented pattern,
generalized to any agent rather than one scoped to crypto-trading PnL or
coding-session tool calls. `RbacRegistry` is likewise new: no RBAC engine
exists anywhere in ECC-main today (`workspace-surface-audit` is a
read-only surface scanner with prose output, not an access-control list).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set


class PermissionDeniedError(Exception):
    """Raised when an agent attempts an action outside its granted scope."""


@dataclass
class RbacRegistry:
    """Minimal per-agent action allowlist.

    Seed via `grant()`; any future structured resource inventory (e.g. a
    machine-readable export of workspace-surface-audit's findings) can
    populate this registry, but no such structured export exists today.
    """

    _grants: Dict[str, Set[str]] = field(default_factory=dict)

    def grant(self, agent_id: str, action: str) -> None:
        self._grants.setdefault(agent_id, set()).add(action)

    def revoke(self, agent_id: str, action: str) -> None:
        self._grants.get(agent_id, set()).discard(action)

    def is_allowed(self, agent_id: str, action: str) -> bool:
        return action in self._grants.get(agent_id, set())

    def require(self, agent_id: str, action: str) -> None:
        if not self.is_allowed(agent_id, action):
            raise PermissionDeniedError(f"{agent_id!r} is not granted {action!r}")


@dataclass
class KillSwitch:
    """Fleet-wide circuit breaker: trips after too many consecutive failures.

    Generalizes the consecutive-loss-threshold design documented for
    trading agents into a domain-agnostic halt condition any agent module
    can share, rather than re-implementing its own ad hoc breaker.
    """

    max_consecutive_failures: int = 3
    _consecutive_failures: int = 0
    _tripped: bool = False
    _trip_reason: str = ""

    def record_success(self) -> None:
        self._consecutive_failures = 0

    def record_failure(self, reason: str = "") -> None:
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.max_consecutive_failures:
            self._tripped = True
            self._trip_reason = reason or f"{self._consecutive_failures} consecutive failures"

    def is_tripped(self) -> bool:
        return self._tripped

    def trip_reason(self) -> str:
        return self._trip_reason

    def reset(self) -> None:
        self._consecutive_failures = 0
        self._tripped = False
        self._trip_reason = ""
