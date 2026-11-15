from __future__ import annotations

import pytest

from momoshield.contracts.validate import validate_contract_artifacts, validate_transaction_dict
from producer.paysim_mapping import paysim_row_to_event


def test_validate_contract_artifacts_ok():
    validate_contract_artifacts()


def test_paysim_ignores_balance_columns():
    """Le CSV Kaggle contient des soldes : on les ignore, on ne les mappe pas."""
    event = paysim_row_to_event(
        {
            "step": 1,
            "type": "TRANSFER",
            "amount": 100,
            "nameOrig": "a",
            "nameDest": "b",
            "oldbalanceOrg": 99999,
            "newbalanceOrig": 1,
            "isFraud": 1,
        }
    )
    assert event.is_fraud_label is True


def test_transaction_schema_ok():
    payload = {
        "tx_id": "tx-12345678",
        "account_id": "acc1",
        "dest_id": "acc2",
        "type": "TRANSFER",
        "amount_fcfa": 1000,
        "operator": "MOOV_MONEY",
        "city": "Lomé",
        "sim_id": "SIM1",
        "event_time": "2024-01-01T12:00:00+00:00",
        "is_fraud_label": False,
    }
    event = validate_transaction_dict(payload)
    assert event.tx_id == "tx-12345678"