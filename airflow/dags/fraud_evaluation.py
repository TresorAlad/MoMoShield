from __future__ import annotations

from datetime import datetime

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator

default_args = {"owner": "momoshield", "retries": 1}


@dag(
    dag_id="fraud_evaluation",
    default_args=default_args,
    schedule="0 5 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["momoshield", "fraud"],
)
def fraud_evaluation():
    start = EmptyOperator(task_id="start")

    @task()
    def evaluate() -> dict:
        from momoshield.batch.fraud_evaluation import compute_fraud_metrics

        labeled_fraud = {"tx1", "tx2"}
        alerts = {"tx1", "tx3"}
        all_tx = {"tx1", "tx2", "tx3", "tx4"}
        metrics = compute_fraud_metrics(alerts, labeled_fraud, all_tx)
        return metrics.to_dict()

    start >> evaluate()


fraud_evaluation()