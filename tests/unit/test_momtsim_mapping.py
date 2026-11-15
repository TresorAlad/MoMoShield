from __future__ import annotations

from producer.momtsim_mapping import MOMTSIM_DENYLIST, momtsim_row_to_event


def test_momtsim_maps_deposit_and_fraud():
    row = {
        "step": "10",
        "transactionType": "withdrawal",
        "amount": "100000",
        "initiator": "UG99",
        "recipient": "",
        "oldBalInitiator": "500000",
        "newBalInitiator": "400000",
        "isFraud": "1",
    }
    event = momtsim_row_to_event(row)
    assert event.type.value == "CASH_OUT"
    assert event.is_fraud_label is True
    assert event.account_id == "UG99"


def test_denylist_documents_leakage_columns():
    assert "newBalInitiator" in MOMTSIM_DENYLIST