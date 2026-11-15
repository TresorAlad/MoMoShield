from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class TransactionView:
    tx_id: str
    account_id: str
    dest_id: str | None
    type: str
    amount_fcfa: float
    operator: str
    city: str
    sim_id: str
    event_time: datetime


@dataclass
class AccountState:
    account_id: str
    last_sim_id: str | None = None
    recent_amounts: list[float] = field(default_factory=list)
    recent_transfers: list[datetime] = field(default_factory=list)
    last_city: str | None = None
    last_city_time: datetime | None = None
    last_balance_hint: float | None = None
    typical_hours: list[int] = field(default_factory=list)

    def avg_amount(self) -> float:
        if not self.recent_amounts:
            return 0.0
        return sum(self.recent_amounts) / len(self.recent_amounts)


@dataclass
class RuleConfig:
    burst_max_60s: int = 5
    amount_multiplier: float = 8.0
    min_history: int = 3
    sim_large_withdrawal: float = 500_000
    geo_min_minutes: float = 90.0
    drain_ratio: float = 0.05
    atypical_amount: float = 750_000
    quiet_hour_start: int = 1
    quiet_hour_end: int = 5


@dataclass
class RuleHit:
    rule_id: str
    score: float
    context: dict[str, Any]