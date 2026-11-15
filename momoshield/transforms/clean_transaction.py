from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml

from momoshield.contracts.models import Operator, TransactionType
from momoshield.contracts.validate import validate_transaction_dict
from momoshield.transforms import messages_fr as msg

ROOT = Path(__file__).resolve().parents[2]
_TYPES_NEED_DEST = frozenset({TransactionType.TRANSFER, TransactionType.PAYMENT})
_REQUIRED_STRINGS = ("tx_id", "account_id", "city", "sim_id")


class PipelineStep(StrEnum):
    BRONZE_INGRESS = "bronze_ingress"
    STAGING = "staging"
    DBT = "dbt"


@dataclass
class CleanResult:
    row: dict[str, Any] | None
    quarantine: dict[str, Any] | None
    note_transformation: str | None


def _load_defaults() -> dict:
    path = ROOT / "config" / "cities_operators.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _reject(
    raw: dict[str, Any],
    motif: str,
    observation: str,
    etape: PipelineStep,
) -> CleanResult:
    return CleanResult(
        row=None,
        quarantine={
            "raw_payload": raw,
            "motif_rejet": motif,
            "observation": observation[:500],
            "etape_pipeline": etape.value,
            "rejected_at": datetime.now(UTC).isoformat(),
        },
        note_transformation=None,
    )


def clean_transaction(
    raw: dict[str, Any],
    *,
    etape: PipelineStep = PipelineStep.BRONZE_INGRESS,
    source_system: str | None = None,
) -> CleanResult:
    """Nettoyage métier + validation contrat. Pas d'imputation par médiane."""
    note_parts: list[str] = []
    data = dict(raw)

    if source_system:
        data.setdefault("source_system", source_system)

    for field in _REQUIRED_STRINGS:
        if not str(data.get(field, "")).strip():
            return _reject(
                raw,
                msg.MOTIF_CHAMP_OBLIGATOIRE,
                msg.observation_technique(field, data.get(field)),
                etape,
            )

    dest = data.get("dest_id")
    if dest is not None and str(dest).strip() == "":
        data["dest_id"] = None
        dest = None

    try:
        tx_type = TransactionType(str(data.get("type", "")).upper().replace("-", "_"))
        data["type"] = tx_type.value
    except ValueError:
        return _reject(
            raw,
            msg.MOTIF_TYPE_INVALIDE,
            msg.observation_technique("type", data.get("type")),
            etape,
        )

    try:
        Operator(str(data.get("operator", "")))
    except ValueError:
        defaults = _load_defaults()
        if defaults.get("operators"):
            data["operator"] = defaults["operators"][0]
            note_parts.append(msg.OBS_VILLE_DEFAUT)
        else:
            return _reject(
                raw,
                msg.MOTIF_OPERATEUR_INVALIDE,
                msg.observation_technique("operator", data.get("operator")),
                etape,
            )

    if not str(data.get("city", "")).strip():
        defaults = _load_defaults()
        data["city"] = defaults["cities"][0]
        note_parts.append(msg.OBS_VILLE_DEFAUT)

    amount = data.get("amount_fcfa")
    try:
        amount_dec = Decimal(str(amount))
        if amount_dec <= 0:
            raise ValueError("non positif")
        data["amount_fcfa"] = float(amount_dec)
    except (TypeError, ValueError, ArithmeticError):
        return _reject(
            raw,
            msg.MOTIF_MONTANT_INVALIDE,
            msg.observation_technique("amount_fcfa", str(amount)),
            etape,
        )

    if tx_type in _TYPES_NEED_DEST and not data.get("dest_id"):
        return _reject(
            raw,
            msg.MOTIF_DEST_MANQUANT,
            msg.OBS_DEST_AUTORISE_NULL,
            etape,
        )

    if tx_type not in _TYPES_NEED_DEST and not data.get("dest_id"):
        note_parts.append(msg.OBS_DEST_AUTORISE_NULL)

    if not data.get("event_time"):
        return _reject(
            raw,
            msg.MOTIF_CHAMP_OBLIGATOIRE,
            msg.observation_technique("event_time", None),
            etape,
        )

    try:
        event = validate_transaction_dict(data)
    except Exception as exc:  # noqa: BLE001
        return _reject(
            raw,
            msg.MOTIF_VALIDATION_CONTRAT,
            str(exc)[:200],
            etape,
        )

    row = event.to_kafka_dict()
    row["is_fraud_label"] = event.is_fraud_label
    row["event_date"] = event.event_time.date().isoformat()
    row["source_system"] = data.get("source_system", "unknown")
    row["ingested_at"] = datetime.now(UTC).isoformat()
    row["note_transformation"] = " — ".join(note_parts) if note_parts else None

    return CleanResult(row=row, quarantine=None, note_transformation=row["note_transformation"])


def clean_batch(rows: list[dict[str, Any]], **kwargs: Any) -> tuple[list[dict], list[dict]]:
    valid: list[dict] = []
    quarantine: list[dict] = []
    for raw in rows:
        result = clean_transaction(raw, **kwargs)
        if result.row:
            valid.append(result.row)
        if result.quarantine:
            quarantine.append(result.quarantine)
    return valid, quarantine