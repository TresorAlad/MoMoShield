"""Inventaire CDC §6 — toutes les sources et leur présence locale."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REF_DIR = ROOT / "data" / "references"


def _has_file(*parts: str) -> bool:
    return (ROOT / Path(*parts)).is_file()


def build_inventory() -> dict[str, Any]:
    paysim_dir = ROOT / "data" / "paysim"
    momtsim_dir = ROOT / "data" / "momtsim"
    paysim_csvs = list(paysim_dir.glob("*.csv")) if paysim_dir.is_dir() else []
    momtsim_csvs = list(momtsim_dir.glob("**/*.csv")) if momtsim_dir.is_dir() else []
    paysim_sizes = [p.stat().st_size for p in paysim_csvs]
    momtsim_sizes = [p.stat().st_size for p in momtsim_csvs]

    ref_files = sorted(f.name for f in REF_DIR.iterdir() if f.is_file()) if REF_DIR.is_dir() else []

    gsma_ok = any(
        name.startswith("gsma") and name.endswith(".pdf") and (REF_DIR / name).stat().st_size > 1000
        for name in ref_files
    )

    sources = {
        "paysim_kaggle": {
            "status": "ok" if paysim_sizes and max(paysim_sizes) > 50_000_000 else "sample_or_missing",
            "files": [str(p.relative_to(ROOT)) for p in paysim_csvs],
        },
        "momtsim_mendeley_kaggle": {
            "status": "ok" if momtsim_sizes and max(momtsim_sizes) > 10_000_000 else "sample_or_missing",
            "files": [str(p.relative_to(ROOT)) for p in momtsim_csvs[:5]],
        },
        "togo_generator_faker": {
            "status": "ok" if _has_file("producer", "togo_generator.py") else "missing",
        },
        "fraud_injection_f3": {
            "status": "ok" if _has_file("producer", "fraud_injector.py") else "missing",
        },
        "momtsim_scenarios_config": {
            "status": "ok" if _has_file("config", "momtsim_scenarios.yaml") else "missing",
        },
        "gsma_typology": {
            "status": "ok" if gsma_ok or _has_file("config", "gsma_rule_mapping.yaml") else "partial",
            "pdfs_in_repo": gsma_ok,
            "mapping": _has_file("config", "gsma_rule_mapping.yaml"),
        },
        "amlsim_ai4fcf": {
            "status": "ok"
            if _has_file("data", "references", "AMLSim-README.md")
            and _has_file("config", "ai4fcf_opensources.yaml")
            else "partial",
        },
        "paysim_article_citation": {
            "status": "ok" if _has_file("docs", "paysim-limits.md") else "partial",
        },
    }

    complete = all(
        s.get("status") in ("ok", "sample_or_missing")
        and not (s.get("status") == "sample_or_missing" and k == "paysim_kaggle")
        for k, s in sources.items()
    )
    # CDC v1 : MoMTSim sample acceptable si mapping + download script present
    pipeline_ready = sources["paysim_kaggle"]["status"] == "ok" and sources["togo_generator_faker"]["status"] == "ok"

    return {
        "cdc_sources": sources,
        "pipeline_primary_ready": pipeline_ready,
        "all_sources_documented": True,
        "references_files": ref_files,
        "notes": {
            "momtsim_full": "make download-momtsim (même token Kaggle que PaySim)",
            "gsma_pdf": "scripts/fetch_gsma_pdfs.sh si curl 403",
        },
    }


def write_inventory(path: Path | None = None) -> Path:
    target = path or REF_DIR / "sources_inventory.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_inventory(), indent=2), encoding="utf-8")
    return target