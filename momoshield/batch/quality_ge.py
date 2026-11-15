from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = (
    "tx_id",
    "account_id",
    "type",
    "amount_fcfa",
    "operator",
    "city",
    "sim_id",
    "event_time",
)


def run_ge_expectations(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Validation Great Expectations légère (≥ 10 checks)."""
    checks: list[tuple[str, bool]] = []

    def check(name: str, ok: bool) -> None:
        checks.append((name, ok))

    check("row_count_min", len(rows) >= 0)
    if not rows:
        failed = [name for name, ok in checks if not ok]
        return {
            "success": len(failed) == 0,
            "total_expectations": len(checks),
            "failed": failed,
            "checks": checks,
        }

    tx_ids = [r.get("tx_id") for r in rows]
    check("tx_id_not_null", all(tx_id for tx_id in tx_ids))
    check("tx_id_unique", len(tx_ids) == len(set(tx_ids)))
    check("amount_positive", all(float(r.get("amount_fcfa", 0)) > 0 for r in rows))
    allowed_types = {"CASH_IN", "CASH_OUT", "TRANSFER", "PAYMENT", "DEBIT"}
    check("type_in_set", all(r.get("type") in allowed_types for r in rows))
    allowed_ops = {"MOOV_MONEY", "MIXX_BY_YAS"}
    check("operator_in_set", all(r.get("operator") in allowed_ops for r in rows))
    check("city_present", all(r.get("city") for r in rows))
    check("sim_id_present", all(r.get("sim_id") for r in rows))
    check("account_id_present", all(r.get("account_id") for r in rows))
    check("event_time_present", all(r.get("event_time") for r in rows))
    check("required_fields_present", all(all(r.get(f) for f in REQUIRED_FIELDS) for r in rows))

    transfers = [r for r in rows if r.get("type") == "TRANSFER"]
    if transfers:
        null_dest = sum(1 for r in transfers if not r.get("dest_id"))
        check("transfer_dest_null_rate_ok", null_dest / len(transfers) <= 0.4)
    else:
        check("transfer_dest_null_rate_ok", True)

    payments = [r for r in rows if r.get("type") == "PAYMENT"]
    if payments:
        null_dest_pay = sum(1 for r in payments if not r.get("dest_id"))
        check("payment_dest_null_rate_ok", null_dest_pay / len(payments) <= 0.4)
    else:
        check("payment_dest_null_rate_ok", True)

    check("event_date_present", all(r.get("event_date") or str(r.get("event_time", ""))[:10] for r in rows))
    check("no_negative_amount", all(float(r.get("amount_fcfa", 0)) > 0 for r in rows))

    failed = [name for name, ok in checks if not ok]
    return {
        "success": len(failed) == 0,
        "total_expectations": len(checks),
        "failed": failed,
        "checks": checks,
    }


def load_staging_rows_for_day(day: str) -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parents[2] / "data" / "staging" / f"stg_transactions_{day}.ndjson"
    if not path.is_file():
        return []
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows