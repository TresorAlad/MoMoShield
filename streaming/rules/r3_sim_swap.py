from __future__ import annotations

from streaming.rules.types import AccountState, RuleConfig, RuleHit, TransactionView


def check_r3_sim_swap(tx: TransactionView, state: AccountState, cfg: RuleConfig) -> RuleHit | None:
    if tx.type != "CASH_OUT":
        return None
    if state.last_sim_id and state.last_sim_id != tx.sim_id:
        if tx.amount_fcfa >= cfg.sim_large_withdrawal:
            return RuleHit(
                rule_id="R3",
                score=0.85,
                context={
                    "previous_sim": state.last_sim_id,
                    "new_sim": tx.sim_id,
                    "amount_fcfa": tx.amount_fcfa,
                    "window_hours": 24,
                },
            )
    return None