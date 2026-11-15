from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator

default_args = {
    "owner": "momoshield",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
}


@dag(
    dag_id="dbt_transformations",
    default_args=default_args,
    schedule="0 3 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["momoshield", "dbt"],
)
def dbt_transformations():
    start = EmptyOperator(task_id="start")

    @task()
    def run_dbt() -> str:
        return "dbt run --profiles-dir /opt/airflow/dbt"

    start >> run_dbt()


dbt_transformations()