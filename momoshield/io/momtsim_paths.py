"""Résolution CSV MoMTSim (Mendeley / Kaggle)."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT / "data" / "momtsim"
SAMPLE_CSV = ROOT / "tests" / "data" / "momtsim_sample.csv"
KNOWN_FILES = (
    "MoMTSim_20240722202413_1000_dataset.csv",
    "Synthetic_Mobile_Money_Transaction_Dataset.csv",
    "synthetic_mobile_money_transaction_dataset.csv",
    "momtsim_v2.csv",
)
FULL_DATASET_MIN_BYTES = 10_000_000


def momtsim_tier(path: Path) -> str:
    if path.resolve() == SAMPLE_CSV.resolve():
        return "sample"
    if path.name in KNOWN_FILES or path.stat().st_size >= FULL_DATASET_MIN_BYTES:
        return "full"
    return "sample"


def _pick_largest_csv() -> Path | None:
    candidates = list(DEFAULT_DATA_DIR.glob("**/*.csv"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_size)


def resolve_momtsim_csv(explicit: Path | None = None) -> Path:
    if explicit is not None and explicit.is_file():
        return explicit

    env_path = os.getenv("MOMTSIM_CSV")
    if env_path:
        path = Path(env_path)
        if path.is_file():
            return path

    for name in KNOWN_FILES:
        candidate = DEFAULT_DATA_DIR / name
        if candidate.is_file():
            return candidate

    found = _pick_largest_csv()
    if found is not None:
        return found

    if SAMPLE_CSV.is_file():
        return SAMPLE_CSV

    raise FileNotFoundError(
        "MoMTSim introuvable. Exécutez: make download-momtsim "
        "(Kaggle) ou placez un ZIP dans data/momtsim/ (make ingest-momtsim-zip)."
    )