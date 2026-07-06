"""RT-16 (FinOps token-spend costing) and RT-17 (SLA monitoring) core extensions.

`skills/cost-aware-llm-pipeline/SKILL.md` documents an immutable
frozen-dataclass budget tracker, and `skills/cost-tracking/SKILL.md`
documents a JSONL cost-log schema -- both are markdown design docs (the
former's code is a real dataclass sketch, the latter has no Python at
all), neither is an importable cross-agent module. `CostTracker` below
is a new implementation following the immutable-record pattern, keyed by
`correlation_id` so one Kernel run's spend stays joined to its telemetry
trail rather than scoped to a single pipeline call. `SlaMonitor` has no
prior art in ECC-main at all (hosted telemetry/alerting is an explicit
Non-Goal in docs/ECC-2.0-REFERENCE-ARCHITECTURE.md today).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass(frozen=True, slots=True)
class CostRecord:
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


@dataclass
class CostTracker:
    """Per-correlation_id running spend, checked against a budget ceiling."""

    budget_limit_usd: float = 5.00
    _records: Dict[str, Tuple[CostRecord, ...]] = field(default_factory=dict)

    def record(
        self,
        correlation_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_per_1k_usd: float = 0.01,
    ) -> CostRecord:
        cost_usd = (input_tokens + output_tokens) / 1000 * cost_per_1k_usd
        entry = CostRecord(model, input_tokens, output_tokens, cost_usd)
        self._records[correlation_id] = self._records.get(correlation_id, ()) + (entry,)
        return entry

    def total_cost(self, correlation_id: str) -> float:
        return sum(r.cost_usd for r in self._records.get(correlation_id, ()))

    def over_budget(self, correlation_id: str) -> bool:
        return self.total_cost(correlation_id) > self.budget_limit_usd


@dataclass
class SlaMonitor:
    """Flags a correlation_id as SLA-breached once it runs past `max_duration_seconds`."""

    max_duration_seconds: float = 30.0
    _started_at: Dict[str, float] = field(default_factory=dict)

    def start(self, correlation_id: str) -> None:
        self._started_at[correlation_id] = time.monotonic()

    def elapsed(self, correlation_id: str) -> float:
        start = self._started_at.get(correlation_id)
        return 0.0 if start is None else time.monotonic() - start

    def check(self, correlation_id: str) -> bool:
        """Returns True if this correlation_id has breached its SLA window."""
        return self.elapsed(correlation_id) > self.max_duration_seconds
