from __future__ import annotations

from momoshield.contracts.validate import validate_transaction_dict


def test_schema_example_valid():
    validate_transaction_dict(
        {
            "tx_id": "tx-abcdefgh",
            "account_id": "TG123",
            "dest_id": "TG456",
            "type": "PAYMENT",
            "amount_fcfa": 25000,
            "operator": "MIXX_BY_YAS",
            "city": "Kara",
            "sim_id": "SIM999",
            "event_time": "2024-05-01T08:30:00+00:00",
            "is_fraud_label": True,
        }
    )