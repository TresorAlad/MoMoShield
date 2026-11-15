CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS meta;

CREATE TABLE IF NOT EXISTS staging.stg_transactions (
    tx_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    dest_id TEXT,
    type TEXT NOT NULL,
    amount_fcfa NUMERIC(18, 2) NOT NULL CHECK (amount_fcfa > 0),
    operator TEXT NOT NULL,
    city TEXT NOT NULL,
    sim_id TEXT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    is_fraud_label BOOLEAN NOT NULL DEFAULT FALSE,
    event_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.fct_transactions_daily (
    event_date DATE PRIMARY KEY,
    tx_count BIGINT NOT NULL,
    total_amount_fcfa NUMERIC(22, 2) NOT NULL,
    fraud_label_count BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.mart_fraud_by_dimensions (
    id SERIAL PRIMARY KEY,
    event_date DATE NOT NULL,
    city TEXT NOT NULL,
    operator TEXT NOT NULL,
    type TEXT NOT NULL,
    tx_count BIGINT NOT NULL,
    fraud_count BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS meta.ge_validation_runs (
    run_id TEXT PRIMARY KEY,
    run_date DATE NOT NULL,
    suite_name TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    details JSONB
);

CREATE TABLE IF NOT EXISTS meta.fraud_metrics (
    id SERIAL PRIMARY KEY,
    run_date DATE NOT NULL,
    precision NUMERIC(8, 6),
    recall NUMERIC(8, 6),
    fpr NUMERIC(8, 6),
    tp INT,
    fp INT,
    fn INT,
    tn INT
);

CREATE TABLE IF NOT EXISTS meta.sli_samples (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);