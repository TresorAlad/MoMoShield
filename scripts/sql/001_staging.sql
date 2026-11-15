-- Schéma staging MoMoShield (PostgreSQL)

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS quarantine;

CREATE TABLE IF NOT EXISTS staging.stg_transactions (
    tx_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    dest_id TEXT,
    type TEXT NOT NULL,
    amount_fcfa NUMERIC(18, 2) NOT NULL,
    operator TEXT NOT NULL,
    city TEXT NOT NULL,
    sim_id TEXT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    event_date DATE NOT NULL,
    is_fraud_label BOOLEAN NOT NULL DEFAULT FALSE,
    source_system TEXT,
    note_transformation TEXT,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staging.stg_alerts (
    alert_id TEXT PRIMARY KEY,
    tx_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    score DOUBLE PRECISION NOT NULL,
    context JSONB,
    detected_at TIMESTAMPTZ NOT NULL,
    event_date DATE NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tx_id, rule_id)
);

CREATE TABLE IF NOT EXISTS quarantine.invalid_transactions (
    id SERIAL PRIMARY KEY,
    rejected_at TIMESTAMPTZ NOT NULL,
    motif_rejet TEXT NOT NULL,
    observation TEXT,
    etape_pipeline TEXT NOT NULL,
    raw_payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_stg_tx_event_date ON staging.stg_transactions (event_date);
CREATE INDEX IF NOT EXISTS idx_stg_alert_tx ON staging.stg_alerts (tx_id);
CREATE INDEX IF NOT EXISTS idx_quarantine_rejected_at ON quarantine.invalid_transactions (rejected_at);