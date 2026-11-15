from __future__ import annotations

from typing import Any


def deduplicate_transactions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Idempotent : garde la première occurrence par tx_id."""
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for row in rows:
        tx_id = row["tx_id"]
        if tx_id in seen:
            continue
        seen.add(tx_id)
        out.append(row)
    return out


def reconcile_counts(bronze_count: int, silver_count: int, tolerance: float = 0.001) -> dict:
    if bronze_count == 0 and silver_count == 0:
        return {"ok": True, "delta_ratio": 0.0}
    delta = abs(bronze_count - silver_count)
    base = max(bronze_count, 1)
    ratio = delta / base
    return {
        "ok": ratio <= tolerance,
        "delta_ratio": ratio,
        "bronze": bronze_count,
        "silver": silver_count,
    }