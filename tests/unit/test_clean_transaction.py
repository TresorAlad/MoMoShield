from __future__ import annotations

from momoshield.transforms.clean_transaction import clean_transaction


def test_clean_accepts_cash_out_without_dest():
    raw = {
        "tx_id": "test_tx_001",
        "account_id": "A1",
        "dest_id": None,
        "type": "CASH_OUT",
        "amount_fcfa": 1000,
        "operator": "MOOV_MONEY",
        "city": "Lomé",
        "sim_id": "S1",
        "event_time": "2024-01-01T10:00:00+00:00",
        "is_fraud_label": False,
    }
    result = clean_transaction(raw)
    assert result.row is not None
    assert result.quarantine is None
    assert result.note_transformation


def test_clean_rejects_transfer_without_dest():
    raw = {
        "tx_id": "test_tx_002",
        "account_id": "A1",
        "dest_id": None,
        "type": "TRANSFER",
        "amount_fcfa": 1000,
        "operator": "MOOV_MONEY",
        "city": "Lomé",
        "sim_id": "S1",
        "event_time": "2024-01-01T10:00:00+00:00",
        "is_fraud_label": False,
    }
    result = clean_transaction(raw)
    assert result.row is None
    assert result.quarantine is not None