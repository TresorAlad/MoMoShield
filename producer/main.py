from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from collections.abc import Iterator
from pathlib import Path

from momoshield.io.momtsim_paths import momtsim_tier, resolve_momtsim_csv
from momoshield.io.paysim_paths import paysim_tier, resolve_paysim_csv
from producer.fraud_injector import inject_burst, momtsim_scenario_pack
from producer.kafka_publish import (
    build_producer,
    publish_json,
    publish_to_dlq,
    validate_before_publish,
)
from producer.momtsim_mapping import momtsim_row_to_event
from producer.paysim_mapping import paysim_row_to_event
from producer.togo_enrich import enrich_togo_context
from producer.togo_generator import generate_transaction

RAW_TOPIC = os.getenv("KAFKA_TOPIC_RAW", "transactions.raw")
DEFAULT_PRODUCER_MODE = os.getenv("PRODUCER_MODE", "hybrid")
DLQ_TOPIC = os.getenv("KAFKA_TOPIC_DLQ", "transactions.dlq")
ENRICH_TOGO = os.getenv("PAYSIM_ENRICH_TOGO", "1") != "0"


def _maybe_enrich(event):  # noqa: ANN001
    return enrich_togo_context(event) if ENRICH_TOGO else event


def _iter_csv_rows(csv_path: Path) -> Iterator[dict]:
    while True:
        with csv_path.open(encoding="utf-8") as handle:
            yield from csv.DictReader(handle)


def _publish_event(producer, event) -> None:  # noqa: ANN001
    try:
        payload = validate_before_publish(event)
        publish_json(producer, RAW_TOPIC, event.account_id, payload)
    except Exception as exc:  # noqa: BLE001
        publish_to_dlq(producer, DLQ_TOPIC, str(exc)[:200], event.model_dump_json())


def replay_csv(
    csv_path: Path,
    rate: float,
    loop: bool,
    row_to_event,
) -> None:
    producer = build_producer()
    delay = 1.0 / max(rate, 0.1)

    while True:
        with csv_path.open(encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                try:
                    event = row_to_event(row)
                    if ENRICH_TOGO:
                        event = enrich_togo_context(event)
                    _publish_event(producer, event)
                except Exception as exc:  # noqa: BLE001
                    publish_to_dlq(producer, DLQ_TOPIC, str(exc)[:200], str(row)[:2000])
                producer.poll(0)
                if delay > 0:
                    time.sleep(delay)
        if not loop:
            break
    producer.flush(10)


def run_synthetic(rate: float, fraud_every: int) -> None:
    producer = build_producer()
    delay = 1.0 / max(rate, 0.1)
    n = 0
    for event in inject_burst("TG_FRAUD_DEMO", count=6):
        _publish_event(producer, event)

    while True:
        is_fraud = fraud_every > 0 and n % fraud_every == 0
        event = generate_transaction(is_fraud=is_fraud)
        _publish_event(producer, event)
        producer.poll(0)
        n += 1
        time.sleep(delay)


def run_hybrid(
    paysim_path: Path,
    momtsim_path: Path,
    rate: float,
    fraud_every: int,
    scenario_every: int,
) -> None:
    """CDC §6 complet : Togo + PaySim + MoMTSim + paquets fraude."""
    producer = build_producer()
    delay = 1.0 / max(rate, 0.1)
    paysim_rows = _iter_csv_rows(paysim_path)
    momtsim_rows = _iter_csv_rows(momtsim_path)
    n = 0

    for event in momtsim_scenario_pack():
        _publish_event(producer, event)

    while True:
        if n > 0 and scenario_every > 0 and n % scenario_every == 0:
            for event in momtsim_scenario_pack(f"TG_SCENARIO_{n}"):
                _publish_event(producer, event)

        slot = n % 3
        if slot == 0:
            is_fraud = fraud_every > 0 and n % fraud_every == 0
            event = generate_transaction(is_fraud=is_fraud)
        elif slot == 1:
            event = _maybe_enrich(paysim_row_to_event(next(paysim_rows)))
        else:
            event = _maybe_enrich(momtsim_row_to_event(next(momtsim_rows)))

        _publish_event(producer, event)
        producer.poll(0)
        n += 1
        time.sleep(delay)


def main() -> None:
    parser = argparse.ArgumentParser(description="MoMoShield producer")
    parser.add_argument(
        "--mode",
        choices=["synthetic", "paysim", "momtsim", "hybrid"],
        default=DEFAULT_PRODUCER_MODE,
    )
    parser.add_argument("--csv", type=Path, default=None, help="CSV PaySim (mode paysim)")
    parser.add_argument("--momtsim-csv", type=Path, default=None, help="CSV MoMTSim")
    parser.add_argument("--rate", type=float, default=100.0)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--fraud-every", type=int, default=500)
    parser.add_argument("--scenario-every", type=int, default=2500, help="Paquets MoMTSim")
    args = parser.parse_args()

    if args.mode == "synthetic":
        run_synthetic(args.rate, args.fraud_every)
        return

    if args.mode == "paysim":
        csv_path = resolve_paysim_csv(args.csv)
        tier = paysim_tier(csv_path)
        print(f"Rejeu PaySim ({tier}) : {csv_path}", file=sys.stderr)
        if not args.loop and tier == "sample":
            args.loop = True
        replay_csv(csv_path, args.rate, args.loop, paysim_row_to_event)
        return

    if args.mode == "momtsim":
        csv_path = resolve_momtsim_csv(args.momtsim_csv)
        tier = momtsim_tier(csv_path)
        print(f"Rejeu MoMTSim ({tier}) : {csv_path}", file=sys.stderr)
        if not args.loop and tier == "sample":
            args.loop = True
        replay_csv(csv_path, args.rate, args.loop, momtsim_row_to_event)
        return

    paysim_path = resolve_paysim_csv(args.csv)
    momtsim_path = resolve_momtsim_csv(args.momtsim_csv)
    print(
        f"Hybrid CDC — PaySim ({paysim_tier(paysim_path)}) {paysim_path.name} + "
        f"MoMTSim ({momtsim_tier(momtsim_path)}) {momtsim_path.name} + Togo",
        file=sys.stderr,
    )
    run_hybrid(paysim_path, momtsim_path, args.rate, args.fraud_every, args.scenario_every)


if __name__ == "__main__":
    main()