from __future__ import annotations

from datetime import timedelta

from streaming.rules.types import AccountState, RuleConfig, RuleHit, TransactionView


def check_r1_burst(tx: TransactionView, state: AccountState, cfg: RuleConfig) -> RuleHit | None:
    if tx.type != "TRANSFER":
        return None
    window_start = tx.event_time - timedelta(seconds=60)
    recent = [t for t in state.recent_transfers if t >= window_start]
    count = len(recent) + 1
    if count > cfg.burst_max_60s:
        score = min(1.0, count / (cfg.burst_max_60s + 2))
        return RuleHit(rule_id="R1", score=score, context={"transfers_60s": count})
    return None