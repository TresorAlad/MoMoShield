from __future__ import annotations

from streaming.rules.types import AccountState, RuleConfig, RuleHit, TransactionView


def check_r5_drain(tx: TransactionView, state: AccountState, cfg: RuleConfig) -> RuleHit | None:
    if tx.type not in ("TRANSFER", "CASH_OUT"):
        return None
    if state.last_balance_hint is None or state.last_balance_hint <= 0:
        return None
    remaining_ratio = (state.last_balance_hint - tx.amount_fcfa) / state.last_balance_hint
    if remaining_ratio <= cfg.drain_ratio:
        return RuleHit(
            rule_id="R5",
            score=0.9,
            context={
                "balance_hint_before": state.last_balance_hint,
                "amount_fcfa": tx.amount_fcfa,
                "remaining_ratio": remaining_ratio,
            },
        )
    return None