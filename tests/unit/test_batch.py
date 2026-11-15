from __future__ import annotations

from momoshield.batch.consolidation import deduplicate_transactions, reconcile_counts
from momoshield.batch.fraud_evaluation import compute_fraud_metrics
from momoshield.batch.quality_ge import run_ge_expectations


def test_dedup():
    rows = [{"tx_id": "a"}, {"tx_id": "a"}, {"tx_id": "b"}]
    assert len(deduplicate_transactions(rows)) == 2


def test_reconcile():
    assert reconcile_counts(1000, 1000)["ok"] is True
    assert reconcile_counts(1000, 900)["ok"] is False


def test_fraud_metrics():
    m = compute_fraud_metrics({"tx1"}, {"tx1", "tx2"}, {"tx1", "tx2", "tx3"})
    assert m.recall == 0.5
    assert m.precision == 1.0


def test_ge_suite_has_ten_checks():
    result = run_ge_expectations(
        [
            {
                "tx_id": "1",
                "account_id": "a",
                "type": "TRANSFER",
                "amount_fcfa": 10,
                "operator": "MOOV_MONEY",
                "city": "Lomé",
                "sim_id": "s",
                "event_time": "2024-01-01",
                "is_fraud_label": False,
                "dest_id": "b",
            }
        ]
    )
    assert result["total_expectations"] >= 10
    assert result["success"] is True