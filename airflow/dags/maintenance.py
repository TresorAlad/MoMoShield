from __future__ import annotations

from datetime import datetime

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator

default_args = {"owner": "momoshield", "retries": 1}


@dag(
    dag_id="maintenance",
    default_args=default_args,
    schedule="@weekly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["momoshield", "maintenance"],
)
def maintenance():
    start = EmptyOperator(task_id="start")

    @task()
    def compact() -> str:
        return "compact_parquet_done"

    start >> compact()


maintenance()