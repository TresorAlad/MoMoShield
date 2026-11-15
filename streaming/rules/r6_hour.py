from __future__ import annotations

from streaming.rules.types import AccountState, RuleConfig, RuleHit, TransactionView


def check_r6_atypical_hour(
    tx: TransactionView, state: AccountState, cfg: RuleConfig
) -> RuleHit | None:
    hour = tx.event_time.hour
    in_quiet = cfg.quiet_hour_start <= hour < cfg.quiet_hour_end
    if not in_quiet:
        return None
    if tx.amount_fcfa < cfg.atypical_amount:
        return None
    return RuleHit(
        rule_id="R6",
        score=0.75,
        context={"hour_utc": hour, "amount_fcfa": tx.amount_fcfa},
    )