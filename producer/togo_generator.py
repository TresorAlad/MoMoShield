from __future__ import annotations

import random
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import yaml
from faker import Faker

from momoshield.contracts.models import Operator, TransactionEvent, TransactionType

fake = Faker("fr_FR")


def load_config() -> dict:
    path = Path(__file__).resolve().parents[1] / "config" / "cities_operators.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def generate_transaction(is_fraud: bool = False) -> TransactionEvent:
    cfg = load_config()
    city = random.choice(cfg["cities"])
    operator = Operator(random.choice(cfg["operators"]))
    tx_type = TransactionType(random.choice(cfg["transaction_types"]))
    amount = Decimal(str(random.randint(500, 500_000)))

    # Heures de pointe 8-10 et 17-19
    hour = random.choice(list(range(8, 11)) + list(range(17, 20)) + list(range(0, 24)))
    now = datetime.now(UTC).replace(hour=hour, minute=random.randint(0, 59), second=0)

    return TransactionEvent(
        tx_id=str(uuid.uuid4()),
        account_id=f"TG{fake.random_number(digits=8, fix_len=True)}",
        dest_id=(
            f"TG{fake.random_number(digits=8, fix_len=True)}"
            if tx_type == TransactionType.TRANSFER
            else None
        ),
        type=tx_type,
        amount_fcfa=amount,
        operator=operator,
        city=city,
        sim_id=f"SIM{fake.random_number(digits=10, fix_len=True)}",
        event_time=now,
        is_fraud_label=is_fraud,
    )