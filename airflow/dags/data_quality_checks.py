from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator

default_args = {"owner": "momoshield", "retries": 1, "retry_delay": timedelta(minutes=2)}


@dag(
    dag_id="data_quality_checks",
    default_args=default_args,
    schedule="0 4 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["momoshield", "quality"],
)
def data_quality_checks():
    start = EmptyOperator(task_id="start")

    @task()
    def run_ge(**context) -> dict:
        from momoshield.batch.quality_ge import load_staging_rows_for_day, run_ge_expectations

        ds = context["ds"]
        rows = load_staging_rows_for_day(ds)
        result = run_ge_expectations(rows)
        if not result["success"] and result["total_expectations"] > 0 and rows:
            raise ValueError(f"GE failed: {result['failed']}")
        return result

    start >> run_ge()


data_quality_checks()