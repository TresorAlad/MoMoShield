from __future__ import annotations

from datetime import datetime

from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.empty import EmptyOperator

default_args = {"owner": "momoshield", "retries": 1}


@dag(
    dag_id="backfill_reprocess",
    default_args=default_args,
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    params={
        "start_date": Param("2024-01-01", type="string"),
        "end_date": Param("2024-01-02", type="string"),
    },
    tags=["momoshield", "backfill"],
)
def backfill_reprocess():
    start = EmptyOperator(task_id="start")

    @task()
    def reprocess(**context) -> dict:
        params = context["params"]
        return {
            "start_date": params["start_date"],
            "end_date": params["end_date"],
            "status": "queued",
        }

    start >> reprocess()


backfill_reprocess()