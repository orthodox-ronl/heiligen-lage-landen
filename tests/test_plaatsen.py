"""Plaatsenregister, locatie-ids op heiligen, Leaflet-bestanden."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import load_entries  # noqa: E402
from plaatsen import load_plaatsen, locatie_zoektekst  # noqa: E402

LEAFLET = ROOT / "site" / "static" / "vendor" / "leaflet"


def test_plaatsen_unieke_ids_en_coordinaten() -> None:
    plaatsen = load_plaatsen()
    assert "utrecht" in plaatsen
    assert "vlaanderen" in plaatsen
    assert plaatsen["vlaanderen"]["soort"] == "streek"
    assert plaatsen["frisia"]["soort"] == "streek"
    assert plaatsen["frisia"]["naam"] == "Friesland"
    assert "Frisia" in (plaatsen["frisia"].get("alternatief") or [])
    assert plaatsen["utrecht"]["soort"] == "plaats"
    for rec in plaatsen.values():
        assert -90 <= rec["lat"] <= 90
        assert -180 <= rec["lon"] <= 180


def test_heiligen_locaties_en_rustplaats_bekend() -> None:
    plaatsen = load_plaatsen()
    ids = set(plaatsen)
    heiligen = [e for e in load_entries() if e["soort"] == "heilige"]
    assert heiligen
    for entry in heiligen:
        locs = entry.get("locaties") or []
        assert locs, f"{entry['id']}: locaties ontbreekt"
        for pid in locs:
            assert pid in ids, f"{entry['id']}: onbekende locatie {pid!r}"
        rust = entry.get("rustplaats")
        if rust:
            assert rust["plaats"] in ids, f"{entry['id']}: rustplaats onbekend"


def test_zoektekst_utrecht_en_vlaanderen() -> None:
    plaatsen = load_plaatsen()
    utrecht = locatie_zoektekst(["utrecht"], plaatsen)
    assert "Utrecht" in utrecht
    vlaanderen = locatie_zoektekst(["drongen"], plaatsen)
    assert "Drongen" in vlaanderen
    assert "Vlaanderen" in vlaanderen
    frisia = locatie_zoektekst(["frisia"], plaatsen)
    assert "Frisia" in frisia or "Friesland" in frisia


def test_willibrord_zoek_vindt_frisia() -> None:
    plaatsen = load_plaatsen()
    by_id = {e["id"]: e for e in load_entries() if e["soort"] == "heilige"}
    zoek = locatie_zoektekst(by_id["willibrord"]["locaties"], plaatsen)
    assert "Utrecht" in zoek
    assert "Frisia" in zoek or "Friesland" in zoek


def test_streek_kinderen_voor_kaartvlak() -> None:
    plaatsen = load_plaatsen()
    frisia = {
        rec["id"] for rec in plaatsen.values() if rec.get("streek") == "frisia"
    }
    assert {"dokkum", "hemelum", "leeuwarden", "stavoren"} <= frisia
    vlaanderen = [
        rec for rec in plaatsen.values() if rec.get("streek") == "vlaanderen"
    ]
    assert len(vlaanderen) >= 3
    assert all(plaatsen[rec["streek"]]["soort"] == "streek" for rec in vlaanderen)


def test_leaflet_lokaal_vendored() -> None:
    assert (LEAFLET / "leaflet.js").is_file()
    assert (LEAFLET / "leaflet.css").is_file()
    assert (LEAFLET / "NOTICE.txt").is_file()
    assert (LEAFLET / "images" / "marker-icon.png").is_file()
    assert (LEAFLET / "images" / "marker-icon-2x.png").is_file()
    assert (LEAFLET / "images" / "marker-shadow.png").is_file()
    js = (LEAFLET / "leaflet.js").read_text(encoding="utf-8", errors="replace")
    assert "cdn" not in js[:200].lower()
