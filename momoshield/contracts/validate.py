"""Validation contrat + synchro JSON Schema."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from momoshield.contracts.models import PAYSIM_DENYLIST, TransactionEvent

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "config" / "schemas" / "transaction_v1.json"
DICT_PATH = ROOT / "docs" / "data-dictionary.md"


def load_transaction_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_transaction_dict(payload: dict) -> TransactionEvent:
    for key in payload:
        if key in PAYSIM_DENYLIST:
            raise ValueError(f"Champ PaySim interdit: {key}")
    schema = load_transaction_schema()
    jsonschema.validate(instance=payload, schema=schema)
    return TransactionEvent.model_validate(payload)


def validate_contract_artifacts() -> None:
    """P2 CI : schéma présent + champs requis documentés."""
    if not SCHEMA_PATH.is_file():
        raise FileNotFoundError(SCHEMA_PATH)
    if not DICT_PATH.is_file():
        raise FileNotFoundError(DICT_PATH)
    required = set(load_transaction_schema().get("required", []))
    doc = DICT_PATH.read_text(encoding="utf-8")
    missing = [field for field in required if f"`{field}`" not in doc]
    if missing:
        raise ValueError(f"Champs manquants dans data-dictionary: {missing}")


if __name__ == "__main__":
    validate_contract_artifacts()
    print("contract validation OK")