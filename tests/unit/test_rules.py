from __future__ import annotations

from datetime import UTC, datetime, timedelta

from streaming.rules.engine import RuleEngine, load_rule_config
from streaming.rules.types import AccountState, TransactionView


def _tx(**kwargs) -> TransactionView:
    defaults = {
        "tx_id": "t1",
        "account_id": "acc1",
        "dest_id": "dest1",
        "type": "TRANSFER",
        "amount_fcfa": 1000.0,
        "operator": "MOOV_MONEY",
        "city": "Lomé",
        "sim_id": "SIM1",
        "event_time": datetime(2024, 6, 1, 12, 0, tzinfo=UTC),
    }
    defaults.update(kwargs)
    return TransactionView(**defaults)


def test_r1_burst_triggers():
    cfg = load_rule_config()
    engine = RuleEngine(cfg)
    state = AccountState(account_id="acc1")
    base = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)
    hits_total = []
    for i in range(cfg.burst_max_60s + 2):
        hits = engine.evaluate(_tx(event_time=base + timedelta(seconds=i * 5)), state)
        hits_total.extend(hits)
    assert any(h.rule_id == "R1" for h in hits_total)


def test_r2_amount_anomaly():
    engine = RuleEngine()
    state = AccountState(account_id="acc1", recent_amounts=[1000, 1100, 900, 950])
    hits = engine.evaluate(_tx(amount_fcfa=50000), state)
    assert any(h.rule_id == "R2" for h in hits)


def test_r3_sim_swap():
    engine = RuleEngine()
    state = AccountState(account_id="acc1", last_sim_id="SIM_OLD")
    hits = engine.evaluate(
        _tx(type="CASH_OUT", amount_fcfa=600000, sim_id="SIM_NEW"), state
    )
    assert any(h.rule_id == "R3" for h in hits)


def test_r4_geo_impossible():
    engine = RuleEngine()
    t0 = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)
    state = AccountState(
        account_id="acc1",
        last_city="Lomé",
        last_city_time=t0 - timedelta(minutes=5),
    )
    hits = engine.evaluate(_tx(city="Kara", event_time=t0), state)
    assert any(h.rule_id == "R4" for h in hits)


def test_r5_drain():
    engine = RuleEngine()
    state = AccountState(account_id="acc1", last_balance_hint=100000)
    hits = engine.evaluate(_tx(type="CASH_OUT", amount_fcfa=98000), state)
    assert any(h.rule_id == "R5" for h in hits)


def test_r6_quiet_hour():
    engine = RuleEngine()
    state = AccountState(account_id="acc1")
    hits = engine.evaluate(
        _tx(
            amount_fcfa=800000,
            event_time=datetime(2024, 6, 1, 3, 0, tzinfo=UTC),
        ),
        state,
    )
    assert any(h.rule_id == "R6" for h in hits)