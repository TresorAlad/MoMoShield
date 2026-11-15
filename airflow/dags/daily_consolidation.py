from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator

default_args = {
    "owner": "momoshield",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
}


@dag(
    dag_id="daily_consolidation",
    default_args=default_args,
    schedule="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["momoshield", "batch"],
)
def daily_consolidation():
    start = EmptyOperator(task_id="start")

    @task()
    def consolidate(**context) -> dict:
        from momoshield.batch.bronze_loader import consolidate_day

        ds = context["ds"]
        return consolidate_day(ds)

    result = consolidate()
    start >> result


daily_consolidation()