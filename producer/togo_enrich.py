from __future__ import annotations

import random
from pathlib import Path

import yaml

from momoshield.contracts.models import Operator, TransactionEvent

_ROOT = Path(__file__).resolve().parents[1]
_CONFIG = _ROOT / "config" / "cities_operators.yaml"


def load_togo_config() -> dict:
    return yaml.safe_load(_CONFIG.read_text(encoding="utf-8"))


def enrich_togo_context(event: TransactionEvent) -> TransactionEvent:
    """Ajoute contexte togolais manquant dans PaySim (CDC §6)."""
    cfg = load_togo_config()
    data = event.model_dump()
    data["city"] = random.choice(cfg["cities"])
    data["operator"] = Operator(random.choice(cfg["operators"]))
    if not data.get("sim_id") or str(data["sim_id"]).startswith("sim_"):
        data["sim_id"] = f"SIM{random.randint(10**9, 10**10 - 1)}"
    return TransactionEvent.model_validate(data)