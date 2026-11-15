from __future__ import annotations

import json
import os
from typing import Any

from momoshield.contracts.models import TransactionEvent
from momoshield.contracts.validate import validate_transaction_dict


def validate_before_publish(event: TransactionEvent) -> dict[str, Any]:
    payload = event.to_kafka_dict()
    validate_transaction_dict(payload)
    return payload


def publish_json(producer: Any, topic: str, key: str, payload: dict) -> None:
    producer.produce(topic, key=key.encode("utf-8"), value=json.dumps(payload).encode("utf-8"))
    producer.poll(0)


def publish_to_dlq(producer: Any, topic: str, error_code: str, raw: str) -> None:
    message = {"error_code": error_code, "payload": raw}
    producer.produce(topic, value=json.dumps(message).encode("utf-8"))
    producer.poll(0)


def build_producer() -> Any:
    from confluent_kafka import Producer

    conf = {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"),
        "client.id": "momoshield-producer",
    }
    return Producer(conf)