"""P3 — validation DAGs."""

from __future__ import annotations

import py_compile
from pathlib import Path

DAG_DIR = Path(__file__).resolve().parents[1] / "airflow" / "dags"


def validate_syntax() -> None:
    for path in DAG_DIR.glob("*.py"):
        py_compile.compile(str(path), doraise=True)


def validate_dagbag() -> None:
    from airflow.models import DagBag

    bag = DagBag(dag_folder=str(DAG_DIR), include_examples=False)
    if bag.import_errors:
        raise RuntimeError(bag.import_errors)


def main() -> None:
    validate_syntax()
    try:
        validate_dagbag()
    except ImportError:
        print("airflow non installé — validation syntaxe uniquement")
    print(f"OK: {len(list(DAG_DIR.glob('*.py')))} fichiers DAG")


if __name__ == "__main__":
    main()