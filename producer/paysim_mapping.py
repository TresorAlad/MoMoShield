from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from decimal import Decimal

from momoshield.contracts.models import Operator, TransactionEvent, TransactionType

PAYSIM_TYPE_MAP = {
    "CASH_IN": TransactionType.CASH_IN,
    "CASH_OUT": TransactionType.CASH_OUT,
    "TRANSFER": TransactionType.TRANSFER,
    "PAYMENT": TransactionType.PAYMENT,
    "DEBIT": TransactionType.DEBIT,
}


def paysim_tx_id(row: dict) -> str:
    """Id stable par ligne PaySim (le CSV Kaggle n'a pas de tx_id)."""
    payload = "|".join(
        [
            str(row.get("step", "")),
            str(row.get("type", "")),
            str(row.get("amount", "")),
            str(row.get("nameOrig", "")),
            str(row.get("nameDest", "")),
        ]
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def paysim_row_to_event(
    row: dict,
    default_operator: Operator = Operator.MOOV_MONEY,
) -> TransactionEvent:
    # Colonnes soldes / isFraud lues uniquement pour label ou ignore — jamais en features règles.
    raw_type = str(row.get("type", "TRANSFER")).upper().replace("-", "_")
    tx_type = PAYSIM_TYPE_MAP.get(raw_type, TransactionType.TRANSFER)
    amount = float(row.get("amount", row.get("amount_fcfa", 1000)))
    # Conversion fictive USD→FCFA documentée CDC
    amount_fcfa = amount * 600

    step = int(row.get("step", 1))
    base = datetime(2020, 1, 1, tzinfo=UTC)
    event_time = base.replace(hour=min(step % 24, 23))

    return TransactionEvent(
        tx_id=str(row.get("tx_id") or paysim_tx_id(row)),
        account_id=str(row.get("nameOrig") or row.get("account_id") or "acc_unknown"),
        dest_id=str(row.get("nameDest") or row.get("dest_id") or "") or None,
        type=tx_type,
        amount_fcfa=Decimal(str(round(amount_fcfa, 2))),
        operator=default_operator,
        city=str(row.get("city", "Lomé")),
        sim_id=str(row.get("sim_id") or f"sim_{row.get('nameOrig', 'x')[:8]}"),
        event_time=event_time,
        is_fraud_label=bool(int(row.get("is_fraud_label", row.get("isFraud", 0)) or 0)),
    )