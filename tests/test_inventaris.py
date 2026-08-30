"""Inventaris: elke heilige heeft een expliciete selectie; beleidsgroepen vast."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import load_entries  # noqa: E402

HEILIGEN = ROOT / "data" / "heiligen"

KANDIDAAT = {
    "adela-van-vlaanderen",
    "fridolin",
    "lioba",
    "walburga",
    "winnibald",
}
NADER = {
    "adelgonda",
    "agricolaus-van-maastricht",
    "aubertus-van-kamerijk",
    "egbert-van-rathmelsigi",
    "folciunus",
    "medardus",
    "quirillus-van-tongern",
    "winnocus",
}


def test_elke_heilige_heeft_selectie_in_yaml() -> None:
    paths = sorted(HEILIGEN.glob("*.yaml"))
    assert paths, "geen heiligen-YAML"
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "\nselectie: " in text, path.name


def test_selectie_groepen_kloppen() -> None:
    by_id = {e["id"]: e for e in load_entries() if e["soort"] == "heilige"}
    kandidaat = {i for i, e in by_id.items() if e["selectie"] == "kandidaat-schrappen"}
    nader = {i for i, e in by_id.items() if e["selectie"] == "nader-onderzoek"}
    voldoet = {i for i, e in by_id.items() if e["selectie"] == "voldoet"}
    assert kandidaat == KANDIDAAT
    assert nader == NADER
    assert set(by_id) == voldoet | nader | kandidaat
    assert not (voldoet & KANDIDAAT)
    assert not (voldoet & NADER)
    assert "willibrord" in voldoet
    assert "servatius" in voldoet
    assert "johannes-van-shanghai" in voldoet
    assert "sophrony-van-essex" in voldoet
    assert by_id["willibrord"]["selectie_toelichting"]
    assert "indirect" in by_id["egbert-van-rathmelsigi"]["selectie_toelichting"].lower() or (
        "Indirecte" in by_id["egbert-van-rathmelsigi"]["selectie_toelichting"]
    )
    assert by_id["egbert-van-rathmelsigi"]["selectie"] == "nader-onderzoek"


def test_inventaris_geen_vaste_catalogustelling() -> None:
    text = (ROOT / "docs" / "inventaris.md").read_text(encoding="utf-8")
    assert "Huidige catalogus" not in text
    assert "/beheer/selectie/" in text
