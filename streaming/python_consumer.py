"""Consumer Python (profil core) — équivalent logique Spark."""

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path

from momoshield.contracts.validate import validate_transaction_dict
from streaming.rules.engine import RuleEngine
from streaming.rules.types import AccountState, TransactionView

ALERT_TOPIC = os.getenv("KAFKA_TOPIC_ALERTS", "transactions.alerts")
RAW_TOPIC = os.getenv("KAFKA_TOPIC_RAW", "transactions.raw")
BRONZE_DIR = Path(os.getenv("BRONZE_DIR", "/data/bronze"))


def tx_from_payload(payload: dict) -> TransactionView:
    validated = validate_transaction_dict(payload)
    return TransactionView(
        tx_id=validated.tx_id,
        account_id=validated.account_id,
        dest_id=validated.dest_id,
        type=validated.type.value,
        amount_fcfa=float(validated.amount_fcfa),
        operator=validated.operator.value,
        city=validated.city,
        sim_id=validated.sim_id,
        event_time=validated.event_time,
    )


def write_bronze_line(payload: dict) -> None:
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    day = payload.get("event_time", "")[:10] or datetime.now(UTC).strftime("%Y-%m-%d")
    path = BRONZE_DIR / f"transactions_{day}.ndjson"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def write_bronze_alert(alert: dict) -> None:
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    day = alert.get("detected_at", "")[:10] or datetime.now(UTC).strftime("%Y-%m-%d")
    path = BRONZE_DIR / f"alerts_{day}.ndjson"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(alert) + "\n")


def run_consumer() -> None:
    from confluent_kafka import Consumer, Producer

    consumer = Consumer(
        {
            "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"),
            "group.id": "momoshield-streaming-core",
            "auto.offset.reset": "earliest",
        }
    )
    producer = Producer({"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")})
    consumer.subscribe([RAW_TOPIC])

    engine = RuleEngine()
    states: dict[str, AccountState] = {}
    seen_alerts: set[tuple[str, str]] = set()

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue
        payload = json.loads(msg.value().decode("utf-8"))
        write_bronze_line(payload)
        tx = tx_from_payload(payload)
        state = states.setdefault(tx.account_id, AccountState(account_id=tx.account_id))
        detected_at = datetime.now(UTC)
        for hit in engine.evaluate(tx, state):
            key = (tx.tx_id, hit.rule_id)
            if key in seen_alerts:
                continue
            seen_alerts.add(key)
            alert = {
                "alert_id": str(uuid.uuid4()),
                "tx_id": tx.tx_id,
                "account_id": tx.account_id,
                "rule_id": hit.rule_id,
                "score": hit.score,
                "context": hit.context,
                "detected_at": detected_at.isoformat(),
            }
            write_bronze_alert(alert)
            producer.produce(
                ALERT_TOPIC,
                key=tx.account_id.encode(),
                value=json.dumps(alert).encode(),
            )
        producer.poll(0)


if __name__ == "__main__":
    run_consumer()