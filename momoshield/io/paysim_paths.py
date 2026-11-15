"""Résolution du chemin CSV PaySim (Kaggle)."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT / "data" / "paysim"
SAMPLE_CSV = ROOT / "tests" / "data" / "paysim_sample.csv"
# Noms vus sur Kaggle (archive.zip ou `kaggle datasets download`)
KAGGLE_FILENAMES = (
    "PS_20174319_1491204399457.csv",
    "PS_20174392719_1491204439457_log.csv",
)
FULL_DATASET_MIN_BYTES = 50_000_000  # ~200 Mo attendu sur Kaggle


def paysim_tier(path: Path) -> str:
    """full | sample — pour basculer hybrid / avertissements."""
    if path.resolve() == SAMPLE_CSV.resolve():
        return "sample"
    if path.name in KAGGLE_FILENAMES or path.stat().st_size >= FULL_DATASET_MIN_BYTES:
        return "full"
    return "sample"


def _pick_full_csv() -> Path | None:
    candidates = list(DEFAULT_DATA_DIR.glob("*.csv"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_size)


def resolve_paysim_csv(explicit: Path | None = None) -> Path:
    if explicit is not None and explicit.is_file():
        return explicit

    env_path = os.getenv("PAYSIM_CSV")
    if env_path:
        path = Path(env_path)
        if path.is_file():
            return path

    for name in KAGGLE_FILENAMES:
        kaggle_path = DEFAULT_DATA_DIR / name
        if kaggle_path.is_file():
            return kaggle_path

    found = _pick_full_csv()
    if found is not None:
        return found

    if SAMPLE_CSV.is_file():
        return SAMPLE_CSV

    raise FileNotFoundError(
        "PaySim introuvable. Exécutez: make download-paysim "
        "(ou définissez PAYSIM_CSV vers votre fichier Kaggle)."
    )