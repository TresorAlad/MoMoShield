from __future__ import annotations

import os
from datetime import UTC, datetime

import pandas as pd


def database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql://momoshield:momoshield_dev@localhost:15432/momoshield",
    )


def query(sql: str, params: dict | None = None) -> pd.DataFrame:
    import psycopg

    with psycopg.connect(database_url()) as conn:
        return pd.read_sql(sql, conn, params=params)


def has_data() -> bool:
    try:
        n = query("SELECT count(*) AS n FROM staging.stg_transactions").iloc[0, 0]
        return int(n) > 0
    except Exception:
        return False


def kpi_summary() -> dict:
    row = query(
        """
        SELECT
            count(*)::bigint AS nb_transactions,
            coalesce(sum(amount_fcfa), 0)::double precision AS montant_total,
            coalesce(avg(amount_fcfa), 0)::double precision AS montant_moyen,
            coalesce(sum(CASE WHEN is_fraud_label THEN 1 ELSE 0 END), 0)::bigint AS nb_fraude_label,
            count(DISTINCT operator)::int AS nb_operateurs,
            count(DISTINCT city)::int AS nb_villes,
            max(event_time) AS derniere_operation
        FROM staging.stg_transactions
        """
    ).iloc[0]
    alertes = query("SELECT count(*)::bigint AS n FROM staging.stg_alerts").iloc[0, 0]
    out = row.to_dict()
    out["nb_alertes"] = int(alertes)
    if out.get("nb_transactions"):
        out["taux_fraude_pct"] = 100.0 * float(out["nb_fraude_label"]) / float(out["nb_transactions"])
        out["taux_alerte_pct"] = 100.0 * float(alertes) / float(out["nb_transactions"])
    else:
        out["taux_fraude_pct"] = 0.0
        out["taux_alerte_pct"] = 0.0
    if pd.notna(out.get("derniere_operation")):
        dt = pd.Timestamp(out["derniere_operation"])
        if dt.tzinfo is not None:
            dt = dt.tz_convert("UTC")
        now = pd.Timestamp.now(tz="UTC")
        delta_h = (now - dt).total_seconds() / 3600.0
        out["fraicheur_heures"] = max(float(delta_h), 0.0)
    else:
        out["fraicheur_heures"] = None
    return out


def transactions() -> pd.DataFrame:
    return query(
        """
        SELECT
            tx_id, account_id, dest_id, type, amount_fcfa, operator, city,
            event_time, event_date, is_fraud_label, note_transformation
        FROM staging.stg_transactions
        """
    )


def alerts() -> pd.DataFrame:
    return query(
        """
        SELECT alert_id, tx_id, account_id, rule_id, score, detected_at, event_date
        FROM staging.stg_alerts
        ORDER BY detected_at DESC
        """
    )


def volume_par_heure() -> pd.DataFrame:
    return query(
        """
        SELECT
            date_trunc('hour', event_time) AS heure,
            count(*) AS nb_transactions,
            sum(amount_fcfa) AS montant_fcfa,
            sum(CASE WHEN is_fraud_label THEN 1 ELSE 0 END) AS nb_fraude
        FROM staging.stg_transactions
        GROUP BY 1
        ORDER BY 1
        """
    )


def alertes_par_regle() -> pd.DataFrame:
    return query(
        """
        SELECT rule_id AS regle, count(*) AS nb_alertes, avg(score)::float AS score_moyen
        FROM staging.stg_alerts
        GROUP BY 1
        ORDER BY nb_alertes DESC
        """
    )


def alertes_croisees() -> pd.DataFrame:
    return query(
        """
        SELECT a.rule_id AS regle, t.operator AS operateur, count(*) AS nb_alertes
        FROM staging.stg_alerts a
        JOIN staging.stg_transactions t ON t.tx_id = a.tx_id
        GROUP BY 1, 2
        """
    )


def alertes_scores() -> pd.DataFrame:
    return query(
        """
        SELECT a.score, a.rule_id AS regle, t.amount_fcfa, t.city AS ville, t.operator AS operateur
        FROM staging.stg_alerts a
        JOIN staging.stg_transactions t ON t.tx_id = a.tx_id
        """
    )


def par_operateur() -> pd.DataFrame:
    return query(
        """
        SELECT
            operator AS operateur,
            count(*) AS nb_transactions,
            sum(amount_fcfa) AS montant_total,
            sum(CASE WHEN is_fraud_label THEN 1 ELSE 0 END) AS nb_fraude,
            avg(amount_fcfa)::float AS montant_moyen
        FROM staging.stg_transactions
        GROUP BY 1
        ORDER BY nb_transactions DESC
        """
    )


def par_ville() -> pd.DataFrame:
    return query(
        """
        SELECT
            city AS ville,
            count(*) AS nb_transactions,
            sum(amount_fcfa) AS montant_total,
            sum(CASE WHEN is_fraud_label THEN 1 ELSE 0 END) AS nb_fraude
        FROM staging.stg_transactions
        GROUP BY 1
        ORDER BY nb_transactions DESC
        LIMIT 20
        """
    )


def carte_villes() -> pd.DataFrame:
    return query(
        """
        SELECT
            t.city AS ville,
            count(*)::int AS nb_transactions,
            coalesce(sum(t.amount_fcfa), 0)::float AS montant_total,
            sum(CASE WHEN t.is_fraud_label THEN 1 ELSE 0 END)::int AS nb_fraude,
            count(DISTINCT a.alert_id)::int AS nb_alertes
        FROM staging.stg_transactions t
        LEFT JOIN staging.stg_alerts a ON a.tx_id = t.tx_id
        GROUP BY 1
        ORDER BY nb_transactions DESC
        """
    )


def par_type() -> pd.DataFrame:
    return query(
        """
        SELECT
            type AS type_operation,
            count(*) AS nb_transactions,
            avg(amount_fcfa)::float AS montant_moyen,
            percentile_cont(0.5) WITHIN GROUP (ORDER BY amount_fcfa) AS montant_mediane
        FROM staging.stg_transactions
        GROUP BY 1
        """
    )


def heatmap_ville_operateur() -> pd.DataFrame:
    return query(
        """
        SELECT city AS ville, operator AS operateur, count(*) AS nb
        FROM staging.stg_transactions
        GROUP BY 1, 2
        """
    )


def evolution_jour() -> pd.DataFrame:
    return query(
        """
        SELECT
            event_date AS jour,
            count(*) AS nb_transactions,
            sum(amount_fcfa) AS montant,
            sum(CASE WHEN is_fraud_label THEN 1 ELSE 0 END) AS nb_fraude,
            avg(CASE WHEN dest_id IS NULL THEN 1.0 ELSE 0.0 END)::float AS taux_sans_dest
        FROM staging.stg_transactions
        GROUP BY 1
        ORDER BY 1
        """
    )


def mart_fraude_dims() -> pd.DataFrame:
    for relation in (
        "staging_analytics.mart_fraude_par_dimensions",
        "analytics.mart_fraud_by_dimensions",
    ):
        try:
            return query(f"SELECT * FROM {relation}")
        except Exception:
            continue
    return pd.DataFrame()


def comptes_a_risque(limit: int = 25) -> pd.DataFrame:
    return query(
        """
        SELECT
            t.account_id AS compte,
            count(distinct a.alert_id) AS nb_alertes,
            count(*) AS nb_transactions,
            max(a.score)::float AS score_max,
            sum(t.amount_fcfa) AS montant_total
        FROM staging.stg_transactions t
        LEFT JOIN staging.stg_alerts a ON a.account_id = t.account_id
        GROUP BY 1
        HAVING count(distinct a.alert_id) > 0
        ORDER BY nb_alertes DESC, score_max DESC
        LIMIT %(limit)s
        """,
        {"limit": limit},
    )