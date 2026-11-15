from __future__ import annotations

from streaming.rules.types import AccountState, RuleConfig, RuleHit, TransactionView


def check_r2_amount(tx: TransactionView, state: AccountState, cfg: RuleConfig) -> RuleHit | None:
    if len(state.recent_amounts) < cfg.min_history:
        return None
    avg = state.avg_amount()
    if avg <= 0:
        return None
    if tx.amount_fcfa > avg * cfg.amount_multiplier:
        ratio = tx.amount_fcfa / avg
        score = min(1.0, ratio / (cfg.amount_multiplier * 2))
        return RuleHit(
            rule_id="R2",
            score=score,
            context={"amount_fcfa": tx.amount_fcfa, "avg_fcfa": avg, "ratio": ratio},
        )
    return None