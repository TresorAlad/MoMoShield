from __future__ import annotations

from producer.paysim_mapping import paysim_row_to_event
from producer.togo_enrich import enrich_togo_context, load_togo_config


def test_enrich_togo_sets_city_and_operator():
    cities = load_togo_config()["cities"]
    row = {
        "step": "1",
        "type": "TRANSFER",
        "amount": "100",
        "nameOrig": "C123",
        "nameDest": "M456",
        "isFraud": "0",
    }
    event = enrich_togo_context(paysim_row_to_event(row))
    assert event.city in cities
    assert event.operator.value in ("MOOV_MONEY", "MIXX_BY_YAS")