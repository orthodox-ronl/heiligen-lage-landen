"""Iconen: lokale PD/CC-bestanden, geen hotlink (stap 7)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from iconen import icoon_bestand, primair_icoon, zichtbare_iconen  # noqa: E402
from iconen_instellingen import bronvermelding_aan  # noqa: E402
from load_entries import load_entries  # noqa: E402
from validate import collect_content_errors  # noqa: E402

from test_kerninhoud import NAGEKEKEN_KERN  # noqa: E402

STATIC = ROOT / "site" / "static"
SCHEMA = ROOT / "schemas" / "entry.schema.json"

MET_ICOON = {
    "willibrord",
    "bonifatius",
    "lambertus",
    "lebuinus",
    "adelbert",
    "gertrudis",
    "dymphna",
    "servatius",
    "odulphus",
    "begga",
    "monulphus",
    "gondulphus",
    "rumold",
    "johannes-van-shanghai",
    "sophrony-van-essex",
    "otger",
}

ZONDER_LEGAAL_BESTAND: set[str] = set()


def test_schema_verbiedt_url_als_bestand() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    item = schema["$defs"]["icoonItem"]
    bestand = item["properties"]["bestand"]
    assert "url" not in item["properties"]
    assert "[Hh][Tt][Tt][Pp]" in bestand.get("pattern", "")
    assert "iconen" in schema["properties"]
    assert item["properties"]["soort"]["enum"] == ["reproductie", "foto"]
    assert item["properties"]["rechten"]["enum"] == [
        "ok",
        "onbekend",
        "nee",
        "bronvermelding",
    ]


def test_bronvermelding_alleen_met_flag() -> None:
    entry = {
        "iconen": [
            {
                "bestand": "iconen/a.jpg",
                "rechten": "bronvermelding",
                "primair": True,
                "bron": "Voorbeeld-site",
                "licentie": "Bronvermelding",
            },
            {
                "bestand": "iconen/b.jpg",
                "rechten": "ok",
                "bron": "Commons",
                "licentie": "PD",
            },
        ]
    }
    assert icoon_bestand(primair_icoon(entry)) == "iconen/b.jpg"
    assert icoon_bestand(primair_icoon(entry, bronvermelding=True)) == (
        "iconen/a.jpg"
    )
    assert len(zichtbare_iconen(entry)) == 1
    assert len(zichtbare_iconen(entry, bronvermelding=True)) == 2


def test_repo_iconen_instellingen_standaard_uit() -> None:
    assert bronvermelding_aan() is False


def test_nagekeken_kern_iconen_lokaal_of_weggelaten() -> None:
    by_id = {e["id"]: e for e in load_entries() if e["soort"] == "heilige"}
    for sid in NAGEKEKEN_KERN:
        prim = primair_icoon(by_id[sid])
        if sid in ZONDER_LEGAAL_BESTAND:
            assert prim is None, sid
            continue
        assert sid in MET_ICOON, sid
        assert prim is not None, sid
        assert prim.get("rechten") == "ok", sid
        assert prim.get("bron"), sid
        assert prim.get("licentie"), sid
        bestand = icoon_bestand(prim)
        assert not bestand.lower().startswith(("http://", "https://")), sid
        assert (STATIC / bestand).is_file(), bestand


def test_gedeeld_bestand_monulphus_gondulphus() -> None:
    by_id = {e["id"]: e for e in load_entries()}
    a = by_id["monulphus"]["icoon"]["bestand"]
    b = by_id["gondulphus"]["icoon"]["bestand"]
    assert a == b == "iconen/monulphus-gondulphus.jpg"


def test_odulphus_heeft_foto_en_reproductie() -> None:
    by_id = {e["id"]: e for e in load_entries()}
    items = by_id["odulphus"]["iconen"]
    assert items[0]["bestand"] == "iconen/odulphus-hemelum.jpg"
    assert items[0]["primair"] is True
    assert items[0]["soort"] == "foto"
    assert items[0]["plaats"] == "hemelum"
    assert items[1]["bestand"] == "iconen/odulphus.jpg"
    assert items[1]["soort"] == "reproductie"
    assert icoon_bestand(primair_icoon(by_id["odulphus"])) == (
        "iconen/odulphus-hemelum.jpg"
    )
    assert (STATIC / "iconen" / "odulphus-hemelum.jpg").is_file()
    assert (STATIC / "iconen" / "odulphus.jpg").is_file()
    assert "icoon" not in by_id["odulphus"]


def test_validate_eist_bron_en_licentie() -> None:
    entries = load_entries()
    sample = next(e for e in entries if e["id"] == "willibrord")
    broken = dict(sample)
    broken.pop("iconen", None)
    broken["icoon"] = {
        "bestand": "iconen/willibrord.jpg",
        "rechten": "ok",
        "bron": "",
        "licentie": "",
    }
    broken["source_path"] = sample["source_path"]
    errors = collect_content_errors([broken])
    assert any("icoon.bron" in e for e in errors)
    assert any("icoon.licentie" in e for e in errors)


def test_validate_weigert_hotlink() -> None:
    entries = load_entries()
    sample = next(e for e in entries if e["id"] == "willibrord")
    broken = dict(sample)
    broken.pop("iconen", None)
    broken["icoon"] = {
        "bestand": "https://example.org/willibrord.jpg",
        "rechten": "ok",
        "bron": "ergens",
        "licentie": "CC0",
    }
    broken["source_path"] = sample["source_path"]
    errors = collect_content_errors([broken])
    assert any("geen URL" in e for e in errors)


def test_validate_weigert_icoon_en_iconen_samen() -> None:
    entries = load_entries()
    sample = next(e for e in entries if e["id"] == "willibrord")
    item = dict(sample["iconen"][0])
    broken = dict(sample)
    broken["icoon"] = item
    broken["iconen"] = [dict(item), dict(item)]
    broken["iconen"][0]["primair"] = True
    broken["source_path"] = sample["source_path"]
    errors = collect_content_errors([broken])
    assert any("niet beide" in e for e in errors)


def test_validate_accepteert_bronvermelding() -> None:
    entries = load_entries()
    sample = next(e for e in entries if e["id"] == "willibrord")
    errors = collect_content_errors([sample])
    assert not any("rechten" in e and "willibrord" in e for e in errors)
    items = sample["iconen"]
    assert any(i.get("rechten") == "bronvermelding" for i in items)


def test_validate_eist_een_primair_bij_meerdere() -> None:
    entries = load_entries()
    sample = next(e for e in entries if e["id"] == "willibrord")
    broken = dict(sample)
    broken.pop("icoon", None)
    item = {
        "bestand": "iconen/willibrord.jpg",
        "rechten": "ok",
        "bron": "x",
        "licentie": "PD",
    }
    broken["iconen"] = [dict(item), dict(item)]
    broken["source_path"] = sample["source_path"]
    errors = collect_content_errors([broken])
    assert any("primair: true verplicht" in e for e in errors)
