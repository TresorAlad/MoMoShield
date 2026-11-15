from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from pathlib import Path

import yaml

from streaming.rules import r1_burst, r2_amount, r3_sim_swap, r4_geo, r5_drain, r6_hour
from streaming.rules.types import AccountState, RuleConfig, RuleHit, TransactionView

RULE_CHECKS: list[Callable[[TransactionView, AccountState, RuleConfig], RuleHit | None]] = [
    r1_burst.check_r1_burst,
    r2_amount.check_r2_amount,
    r3_sim_swap.check_r3_sim_swap,
    r4_geo.check_r4_geo,
    r5_drain.check_r5_drain,
    r6_hour.check_r6_atypical_hour,
]


def load_rule_config(path: Path | None = None) -> RuleConfig:
    root = Path(__file__).resolve().parents[2]
    config_path = path or root / "config" / "fraud_rules.yaml"
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return RuleConfig(
        burst_max_60s=raw["burst"]["max_transfers_per_60s"],
        amount_multiplier=raw["amount_anomaly"]["multiplier_vs_avg"],
        min_history=raw["amount_anomaly"]["min_history_tx"],
        sim_large_withdrawal=raw["sim_swap"]["large_withdrawal_fcfa"],
        geo_min_minutes=raw["geo_inconsistency"]["min_travel_minutes"],
        drain_ratio=raw["account_drain"]["balance_ratio_threshold"],
        atypical_amount=raw["atypical_hour"]["unusual_hour_amount_fcfa"],
        quiet_hour_start=raw["atypical_hour"]["quiet_hours"]["start"],
        quiet_hour_end=raw["atypical_hour"]["quiet_hours"]["end"],
    )


def update_state(state: AccountState, tx: TransactionView) -> None:
    state.last_sim_id = tx.sim_id
    state.recent_amounts.append(tx.amount_fcfa)
    state.recent_amounts = state.recent_amounts[-50:]
    if tx.type == "TRANSFER":
        state.recent_transfers.append(tx.event_time)
        cutoff = tx.event_time - timedelta(seconds=120)
        state.recent_transfers = [t for t in state.recent_transfers if t >= cutoff]
    state.last_city = tx.city
    state.last_city_time = tx.event_time
    state.typical_hours.append(tx.event_time.hour)
    if state.last_balance_hint is None:
        state.last_balance_hint = tx.amount_fcfa * 3
    if tx.type == "CASH_IN":
        state.last_balance_hint += tx.amount_fcfa
    elif tx.type in ("CASH_OUT", "TRANSFER", "PAYMENT", "DEBIT"):
        state.last_balance_hint = max(0.0, state.last_balance_hint - tx.amount_fcfa)


class RuleEngine:
    def __init__(self, config: RuleConfig | None = None) -> None:
        self.config = config or load_rule_config()

    def evaluate(self, tx: TransactionView, state: AccountState) -> list[RuleHit]:
        hits: list[RuleHit] = []
        for check in RULE_CHECKS:
            hit = check(tx, state, self.config)
            if hit:
                hits.append(hit)
        update_state(state, tx)
        return hits


def evaluate_transaction(
    tx: TransactionView,
    state: AccountState,
    config: RuleConfig | None = None,
) -> list[RuleHit]:
    return RuleEngine(config).evaluate(tx, state)