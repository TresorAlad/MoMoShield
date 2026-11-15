from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from momoshield.contracts.models import Operator, TransactionEvent, TransactionType


def inject_burst(account_id: str, count: int = 8) -> list[TransactionEvent]:
    base = datetime.now(UTC)
    events: list[TransactionEvent] = []
    for i in range(count):
        events.append(
            TransactionEvent(
                tx_id=str(uuid.uuid4()),
                account_id=account_id,
                dest_id=f"TG_DEST_{i}",
                type=TransactionType.TRANSFER,
                amount_fcfa=Decimal("5000"),
                operator=Operator.MOOV_MONEY,
                city="Lomé",
                sim_id="SIM_BURST",
                event_time=base + timedelta(seconds=i * 5),
                is_fraud_label=True,
            )
        )
    return events


def inject_sim_swap_withdrawal(account_id: str) -> list[TransactionEvent]:
    now = datetime.now(UTC)
    return [
        TransactionEvent(
            tx_id=str(uuid.uuid4()),
            account_id=account_id,
            dest_id=None,
            type=TransactionType.CASH_OUT,
            amount_fcfa=Decimal("600000"),
            operator=Operator.MIXX_BY_YAS,
            city="Lomé",
            sim_id="SIM_OLD",
            event_time=now - timedelta(hours=2),
            is_fraud_label=False,
        ),
        TransactionEvent(
            tx_id=str(uuid.uuid4()),
            account_id=account_id,
            dest_id=None,
            type=TransactionType.CASH_OUT,
            amount_fcfa=Decimal("550000"),
            operator=Operator.MIXX_BY_YAS,
            city="Lomé",
            sim_id="SIM_NEW",
            event_time=now,
            is_fraud_label=True,
        ),
    ]


def momtsim_scenario_pack(account_id: str = "TG_MOMTSIM_DEMO") -> list[TransactionEvent]:
    """Scénarios inspirés MoMTSim (SIM swap, géo impossible, rafale)."""
    events: list[TransactionEvent] = []
    events.extend(inject_burst(account_id, count=5))
    events.extend(inject_sim_swap_withdrawal(account_id))
    events.extend(inject_geo_impossible(account_id))
    return events


def inject_geo_impossible(account_id: str) -> list[TransactionEvent]:
    now = datetime.now(UTC)
    return [
        TransactionEvent(
            tx_id=str(uuid.uuid4()),
            account_id=account_id,
            dest_id=None,
            type=TransactionType.PAYMENT,
            amount_fcfa=Decimal("12000"),
            operator=Operator.MOOV_MONEY,
            city="Lomé",
            sim_id="SIM_GEO",
            event_time=now - timedelta(minutes=10),
            is_fraud_label=False,
        ),
        TransactionEvent(
            tx_id=str(uuid.uuid4()),
            account_id=account_id,
            dest_id=None,
            type=TransactionType.PAYMENT,
            amount_fcfa=Decimal("15000"),
            operator=Operator.MOOV_MONEY,
            city="Kara",
            sim_id="SIM_GEO",
            event_time=now,
            is_fraud_label=True,
        ),
    ]