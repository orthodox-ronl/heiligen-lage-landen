"""Lees site/data/iconen_instellingen.yaml (zelfde bron als Hugo)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from load_entries import load_yaml

ROOT = Path(__file__).resolve().parents[1]
INSTELLINGEN = ROOT / "site" / "data" / "iconen_instellingen.yaml"


def iconen_instellingen(pad: Path | None = None) -> dict[str, Any]:
    data = load_yaml(pad or INSTELLINGEN)
    return data if isinstance(data, dict) else {}


def bronvermelding_aan(pad: Path | None = None) -> bool:
    """True = toon iconen met rechten: bronvermelding."""
    return bool(iconen_instellingen(pad).get("bronvermelding"))
