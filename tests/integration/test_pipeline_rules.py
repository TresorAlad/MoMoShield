from __future__ import annotations

import pytest

from producer.fraud_injector import inject_burst
from streaming.rules.engine import RuleEngine
from streaming.rules.types import AccountState, TransactionView


@pytest.mark.integration
def test_injected_burst_triggers_r1():
    engine = RuleEngine()
    state = AccountState(account_id="TG_FRAUD_DEMO")
    hits = []
    for event in inject_burst("TG_FRAUD_DEMO", count=8):
        tx = TransactionView(
            tx_id=event.tx_id,
            account_id=event.account_id,
            dest_id=event.dest_id,
            type=event.type.value,
            amount_fcfa=float(event.amount_fcfa),
            operator=event.operator.value,
            city=event.city,
            sim_id=event.sim_id,
            event_time=event.event_time,
        )
        hits.extend(engine.evaluate(tx, state))
    assert any(h.rule_id == "R1" for h in hits)