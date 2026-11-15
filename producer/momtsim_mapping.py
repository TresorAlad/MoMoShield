from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from decimal import Decimal

from momoshield.contracts.models import Operator, TransactionEvent, TransactionType

MOMTSIM_DENYLIST = frozenset(
    {
        "oldBalInitiator",
        "newBalInitiator",
        "oldBalRecipient",
        "newBalRecipient",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
        "isFraud",
        "isFlaggedFraud",
        "fraudTypeCode",
        "isSuccessful",
    }
)

TYPE_MAP = {
    "DEPOSIT": TransactionType.CASH_IN,
    "CASH_IN": TransactionType.CASH_IN,
    "WITHDRAWAL": TransactionType.CASH_OUT,
    "CASH_OUT": TransactionType.CASH_OUT,
    "TRANSFER": TransactionType.TRANSFER,
    "PAYMENT": TransactionType.PAYMENT,
    "DEBIT": TransactionType.DEBIT,
}


def momtsim_tx_id(row: dict) -> str:
    payload = "|".join(
        [
            str(row.get("step", "")),
            str(row.get("transactionType", row.get("type", ""))),
            str(row.get("amount", "")),
            str(row.get("initiator", row.get("nameOrig", ""))),
            str(row.get("recipient", row.get("nameDest", ""))),
        ]
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def _norm_type(raw: str) -> TransactionType:
    key = raw.upper().replace("-", "_").replace(" ", "_")
    if key in TYPE_MAP:
        return TYPE_MAP[key]
    if key == "DEPOSIT":
        return TransactionType.CASH_IN
    if key == "WITHDRAWAL":
        return TransactionType.CASH_OUT
    return TransactionType.TRANSFER


def momtsim_row_to_event(
    row: dict,
    default_operator: Operator = Operator.MOOV_MONEY,
    default_city: str = "Lomé",
) -> TransactionEvent:
    raw_type = str(
        row.get("transactionType") or row.get("type") or row.get("transaction_type") or "transfer"
    )
    tx_type = _norm_type(raw_type)

    amount = float(row.get("amount", row.get("amount_fcfa", 1000)))
    # Jeu calibré Afrique de l'Est — conversion documentée (comme PaySim)
    amount_fcfa = amount * 2.2 if amount < 1_000_000 else amount

    step = int(row.get("step", 1))
    base = datetime(2021, 6, 1, tzinfo=UTC)
    event_time = base.replace(hour=min(step % 24, 23))

    account = row.get("initiator") or row.get("nameOrig") or row.get("account_id") or "acc_unknown"
    dest = row.get("recipient") or row.get("nameDest") or row.get("dest_id") or ""
    dest_id = str(dest).strip() or None

    label = row.get("is_fraud_label", row.get("isFraud", row.get("isFraudulent", 0)))
    is_fraud = bool(int(label or 0))

    return TransactionEvent(
        tx_id=str(row.get("tx_id") or momtsim_tx_id(row)),
        account_id=str(account),
        dest_id=dest_id,
        type=tx_type,
        amount_fcfa=Decimal(str(round(max(amount_fcfa, 1), 2))),
        operator=default_operator,
        city=str(row.get("city") or default_city),
        sim_id=str(row.get("sim_id") or f"SIM_{str(account)[:8]}"),
        event_time=event_time,
        is_fraud_label=is_fraud,
    )