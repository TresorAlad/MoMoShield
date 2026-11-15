from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FraudMetrics:
    precision: float
    recall: float
    fpr: float
    tp: int
    fp: int
    fn: int
    tn: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "precision": self.precision,
            "recall": self.recall,
            "fpr": self.fpr,
            "tp": self.tp,
            "fp": self.fp,
            "fn": self.fn,
            "tn": self.tn,
        }


def compute_fraud_metrics(
    alert_tx_ids: set[str],
    labeled_fraud: set[str],
    all_labeled_tx: set[str],
) -> FraudMetrics:
    """Évalue les alertes vs is_fraud_label (transactions étiquetées)."""
    tp = len(alert_tx_ids & labeled_fraud)
    fp = len(alert_tx_ids - labeled_fraud)
    fn = len(labeled_fraud - alert_tx_ids)
    tn = len((all_labeled_tx - labeled_fraud) - alert_tx_ids)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0

    return FraudMetrics(
        precision=precision,
        recall=recall,
        fpr=fpr,
        tp=tp,
        fp=fp,
        fn=fn,
        tn=tn,
    )