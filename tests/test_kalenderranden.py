"""Kalenderranden: voorfeest, nafeest, synaxis, Pokrov (stap 6)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import load_entries  # noqa: E402
from lezingen import resolve_lezingen  # noqa: E402

FEESTEN = ROOT / "data" / "feesten"

VERWACHT = {
    "voorfeest-geboorte-moeder-gods": ("09-07", None),
    "nafeest-geboorte-moeder-gods": ("09-09", "09-12"),
    "voorfeest-kruisverheffing": ("09-13", None),
    "nafeest-kruisverheffing": ("09-15", "09-21"),
    "pokrov": ("10-01", None),
    "voorfeest-tempelgang-moeder-gods": ("11-20", None),
    "nafeest-tempelgang-moeder-gods": ("11-22", "11-25"),
    "voorfeest-kerst": ("12-20", "12-24"),
    "synaxis-moeder-gods": ("12-26", None),
    "nafeest-kerst": ("12-26", "12-31"),
    "voorfeest-theofanie": ("01-02", "01-05"),
    "synaxis-johannes-doper": ("01-07", None),
    "nafeest-theofanie": ("01-07", "01-14"),
    "voorfeest-ontmoeting-in-de-tempel": ("02-01", None),
    "nafeest-ontmoeting-in-de-tempel": ("02-03", "02-09"),
    "voorfeest-aankondiging": ("03-24", None),
    "synaxis-gabriel": ("03-26", None),
    "voorfeest-transfiguratie": ("08-05", None),
    "nafeest-transfiguratie": ("08-07", "08-13"),
    "voorfeest-ontslapen-moeder-gods": ("08-14", None),
    "nafeest-ontslapen-moeder-gods": ("08-16", "08-23"),
}

PAAS = {
    "nafeest-hemelvaart": (40, 47),
    "teruggave-hemelvaart": (47, None),
    "teruggave-pinksteren": (55, None),
}

NIET_IN_SYNAXARION_ALS_VASTE_DAG = (
    "zondag-voorvaderen",
    "zondag-vaderen-voor-kerst",
    "zondag-na-kerst",
    "zondag-na-theofanie",
    "zondag-vaderen-zevende-concilie",
)


def test_kalenderrand_bestanden_bestaan() -> None:
    for eid in (*VERWACHT, *PAAS):
        assert (FEESTEN / f"{eid}.yaml").is_file(), eid


def test_zondagen_rond_kerst_zijn_weekdag_relatief() -> None:
    by_id = {e["id"]: e for e in load_entries()}
    for eid in NIET_IN_SYNAXARION_ALS_VASTE_DAG:
        assert by_id[eid]["datum_norm"]["vorm"] == "weekdag_relatief"
    datamodel = (ROOT / "docs" / "datamodel.md").read_text(encoding="utf-8")
    assert "weekdag_relatief" in datamodel


def test_vaste_randen_datums() -> None:
    by_id = {e["id"]: e for e in load_entries()}
    for eid, (van, tot) in VERWACHT.items():
        entry = by_id[eid]
        assert entry["soort"] == "feest"
        assert entry["cyclus"] == "jaar"
        dn = entry["datum_norm"]
        if tot is None:
            assert dn["vorm"] == "dag"
            assert dn["feestdatum"] == van
        else:
            assert dn["vorm"] == "periode"
            assert dn["van"] == van
            assert dn["tot"] == tot


def test_paascyclus_randen() -> None:
    by_id = {e["id"]: e for e in load_entries()}
    hemelvaart = by_id["nafeest-hemelvaart"]["datum_norm"]
    assert hemelvaart["vorm"] == "periode"
    assert hemelvaart["van_offset_dagen"] == 40
    assert hemelvaart["tot_offset_dagen"] == 47
    assert by_id["teruggave-hemelvaart"]["datum_norm"]["paascyclus_offset"] == 47
    assert by_id["teruggave-pinksteren"]["datum_norm"]["paascyclus_offset"] == 55


def test_zondag_heiligen_lage_landen_tweede_na_pinksteren() -> None:
    by_id = {e["id"]: e for e in load_entries()}
    entry = by_id["zondag-heiligen-lage-landen"]
    assert entry["soort"] == "feest"
    assert entry["datum_norm"]["paascyclus_offset"] == 63
    assert "Lage Landen" in entry["namen"]["primair"]
    r = resolve_lezingen(2026, "06-14", "nieuw")
    assert r.override_id == "zondag-heiligen-lage-landen"
    assert r.modus == "toevoegen"
    assert [a.ref for a in r.apostel] == ["Rom. 2:10-16", "Heb. 11:33-12:2"]
    assert [e.ref for e in r.evangelie] == ["Matt. 4:18-23", "Matt. 4:25-5:12"]
    from lezingen import liturgische_daglabel

    assert liturgische_daglabel(2026, "06-14", "nieuw") == (
        "Zondag van de heiligen van de Lage Landen"
    )


def test_palmzondag_zonder_nafeest() -> None:
    assert not (FEESTEN / "nafeest-palmzondag.yaml").exists()
    assert not (FEESTEN / "voorfeest-palmzondag.yaml").exists()
    assert not (FEESTEN / "nafeest-aankondiging.yaml").exists()


def test_pokrov_en_synaxis_lezingen() -> None:
    pokrov = resolve_lezingen(2026, "10-01", "nieuw")
    assert pokrov.override_id == "pokrov"
    assert [a.ref for a in pokrov.apostel] == ["Heb. 9:1-7"]
    synaxis = resolve_lezingen(2026, "12-26", "nieuw")
    assert synaxis.override_id == "synaxis-moeder-gods"
    johannes = resolve_lezingen(2026, "01-07", "nieuw")
    assert johannes.override_id == "synaxis-johannes-doper"
