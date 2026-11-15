#!/usr/bin/env python3
"""Profilage rapide de l'échantillon PaySim (S2)."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


def main() -> None:
    path = Path(__file__).resolve().parents[1] / "tests" / "data" / "paysim_sample.csv"
    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    types = Counter(r["type"] for r in rows)
    fraud = sum(int(r.get("isFraud", 0)) for r in rows)
    print(f"rows={len(rows)} types={dict(types)} fraud_rate={fraud / len(rows):.2%}")


if __name__ == "__main__":
    main()