from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TransactionType(StrEnum):
    CASH_IN = "CASH_IN"
    CASH_OUT = "CASH_OUT"
    TRANSFER = "TRANSFER"
    PAYMENT = "PAYMENT"
    DEBIT = "DEBIT"


class Operator(StrEnum):
    MOOV_MONEY = "MOOV_MONEY"
    MIXX_BY_YAS = "MIXX_BY_YAS"


PAYSIM_DENYLIST = frozenset(
    {
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
        "isFraud",
    }
)


class TransactionEvent(BaseModel):
    tx_id: str
    account_id: str
    dest_id: str | None = None
    type: TransactionType
    amount_fcfa: Decimal = Field(gt=0)
    operator: Operator
    city: str
    sim_id: str
    event_time: datetime
    is_fraud_label: bool

    @field_validator("event_time", mode="before")
    @classmethod
    def parse_event_time(cls, value: str | datetime) -> datetime:
        if isinstance(value, datetime):
            return value
        text = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(text)

    def to_kafka_dict(self) -> dict[str, Any]:
        data = self.model_dump(mode="json")
        data["amount_fcfa"] = float(self.amount_fcfa)
        return data


class FraudAlert(BaseModel):
    alert_id: str
    tx_id: str
    account_id: str
    rule_id: str
    score: float = Field(ge=0, le=1)
    context: dict[str, Any] = Field(default_factory=dict)
    detected_at: datetime

    @field_validator("rule_id")
    @classmethod
    def rule_pattern(cls, value: str) -> str:
        if value not in {f"R{i}" for i in range(1, 7)}:
            raise ValueError(f"rule_id invalide: {value}")
        return value