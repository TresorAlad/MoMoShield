from __future__ import annotations

from producer.fraud_injector import inject_burst, inject_geo_impossible
from producer.paysim_mapping import paysim_row_to_event
from producer.togo_generator import generate_transaction


def test_paysim_mapping():
    event = paysim_row_to_event(
        {"type": "TRANSFER", "amount": 100, "nameOrig": "a", "nameDest": "b", "step": 5}
    )
    assert event.amount_fcfa > 0
    assert event.city == "Lomé"


def test_generator():
    tx = generate_transaction()
    assert tx.operator.value in ("MOOV_MONEY", "MIXX_BY_YAS")


def test_inject_burst_labeled_fraud():
    events = inject_burst("TG_TEST", count=3)
    assert all(e.is_fraud_label for e in events)


def test_inject_geo():
    events = inject_geo_impossible("TG_GEO")
    assert len(events) == 2
    assert events[-1].is_fraud_label