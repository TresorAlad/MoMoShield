from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class SliSample:
    name: str
    value: float
    recorded_at: datetime

    def to_row(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "recorded_at": self.recorded_at.isoformat(),
        }


def latency_p95_ms(samples_ms: list[float]) -> float:
    if not samples_ms:
        return 0.0
    ordered = sorted(samples_ms)
    idx = int(0.95 * (len(ordered) - 1))
    return ordered[idx]