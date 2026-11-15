from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

from momoshield.batch.consolidation import deduplicate_transactions, reconcile_counts
from momoshield.transforms.clean_transaction import PipelineStep, clean_batch

ROOT = Path(__file__).resolve().parents[2]


def bronze_transaction_path(bronze_dir: Path, day: str) -> Path:
    return bronze_dir / f"transactions_{day}.ndjson"


def bronze_alert_path(bronze_dir: Path, day: str) -> Path:
    return bronze_dir / f"alerts_{day}.ndjson"


def read_ndjson(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_bronze_day(
    bronze_dir: Path,
    day: str,
    *,
    source_system: str | None = None,
) -> dict[str, Any]:
    """Lit bronze, déduplique, nettoie, écrit quarantaine locale."""
    bronze_dir = Path(bronze_dir)
    raw_rows = read_ndjson(bronze_transaction_path(bronze_dir, day))
    deduped = deduplicate_transactions(raw_rows)
    cleaned, quarantine = clean_batch(
        deduped,
        etape=PipelineStep.BRONZE_INGRESS,
        source_system=source_system,
    )

    quarantine_dir = ROOT / "data" / "quarantine"
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    qpath = quarantine_dir / f"invalid_{day}.ndjson"
    with qpath.open("w", encoding="utf-8") as handle:
        for row in quarantine:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    reconciled = reconcile_counts(len(raw_rows), len(cleaned))

    return {
        "day": day,
        "bronze_count": len(raw_rows),
        "silver_count": len(cleaned),
        "quarantine_count": len(quarantine),
        "transactions": cleaned,
        "quarantine_path": str(qpath),
        "reconcile": reconciled,
    }


def upsert_staging_postgres(
    transactions: list[dict[str, Any]],
    alerts: list[dict[str, Any]],
    quarantine: list[dict[str, Any]],
    database_url: str,
) -> None:
    import psycopg

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            for row in transactions:
                cur.execute(
                    """
                    INSERT INTO staging.stg_transactions (
                        tx_id, account_id, dest_id, type, amount_fcfa, operator,
                        city, sim_id, event_time, event_date, is_fraud_label,
                        source_system, note_transformation, ingested_at
                    ) VALUES (
                        %(tx_id)s, %(account_id)s, %(dest_id)s, %(type)s, %(amount_fcfa)s,
                        %(operator)s, %(city)s, %(sim_id)s, %(event_time)s, %(event_date)s,
                        %(is_fraud_label)s, %(source_system)s,
                        %(note_transformation)s, %(ingested_at)s
                    )
                    ON CONFLICT (tx_id) DO NOTHING
                    """,
                    {
                        **row,
                        "event_time": row["event_time"],
                    },
                )
            for alert in alerts:
                detected = alert.get("detected_at", datetime.utcnow().isoformat())
                event_date = alert.get("event_date") or detected[:10]
                cur.execute(
                    """
                    INSERT INTO staging.stg_alerts (
                        alert_id, tx_id, account_id, rule_id, score, context,
                        detected_at, event_date, ingested_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (tx_id, rule_id) DO NOTHING
                    """,
                    (
                        alert["alert_id"],
                        alert["tx_id"],
                        alert["account_id"],
                        alert["rule_id"],
                        alert["score"],
                        json.dumps(alert.get("context", {})),
                        detected,
                        event_date,
                    ),
                )
            for q in quarantine:
                cur.execute(
                    """
                    INSERT INTO quarantine.invalid_transactions (
                        rejected_at, motif_rejet, observation, etape_pipeline, raw_payload
                    ) VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        q.get("rejected_at", datetime.utcnow().isoformat()),
                        q["motif_rejet"],
                        q.get("observation"),
                        q["etape_pipeline"],
                        json.dumps(q.get("raw_payload", {})),
                    ),
                )
        conn.commit()


def consolidate_day(day: str | None = None) -> dict[str, Any]:
    """Point d'entrée batch : bronze → staging fichier + Postgres optionnel."""
    bronze_dir = Path(os.getenv("BRONZE_DIR", "/data/bronze"))
    day = day or date.today().isoformat()
    result = load_bronze_day(bronze_dir, day)
    alerts = read_ndjson(bronze_alert_path(bronze_dir, day))

    database_url = os.getenv("DATABASE_URL")
    if database_url and result["transactions"]:
        qrows = read_ndjson(Path(result["quarantine_path"]))
        try:
            upsert_staging_postgres(result["transactions"], alerts, qrows, database_url)
            result["postgres"] = True
        except Exception as exc:  # noqa: BLE001
            result["postgres"] = False
            result["postgres_error"] = str(exc)[:200]

    staging_dir = ROOT / "data" / "staging"
    staging_dir.mkdir(parents=True, exist_ok=True)
    out = staging_dir / f"stg_transactions_{day}.ndjson"
    with out.open("w", encoding="utf-8") as handle:
        for row in result["transactions"]:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    result["staging_file"] = str(out)
    return result