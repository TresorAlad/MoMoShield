-- Extension staging / quarantaine (après init de base)
CREATE SCHEMA IF NOT EXISTS quarantine;

ALTER TABLE IF EXISTS staging.stg_transactions
    ADD COLUMN IF NOT EXISTS source_system TEXT,
    ADD COLUMN IF NOT EXISTS note_transformation TEXT,
    ADD COLUMN IF NOT EXISTS ingested_at TIMESTAMPTZ DEFAULT NOW();

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

CREATE SCHEMA IF NOT EXISTS reference;