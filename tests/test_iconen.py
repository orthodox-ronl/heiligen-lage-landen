"""Iconen: lokale PD/CC-bestanden, geen hotlink (stap 7)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import icoon_items, load_entries  # noqa: E402
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
    assert len(schema["properties"]["icoon"]["oneOf"]) == 2


def test_nagekeken_kern_iconen_lokaal_of_weggelaten() -> None:
    by_id = {e["id"]: e for e in load_entries() if e["soort"] == "heilige"}
    for sid in NAGEKEKEN_KERN:
        icoon = (icoon_items(by_id[sid]) or [{}])[0]
        if sid in ZONDER_LEGAAL_BESTAND:
            assert not icoon.get("bestand"), sid
            continue
        assert sid in MET_ICOON, sid
        assert icoon.get("rechten") == "ok", sid
        assert icoon.get("bron"), sid
        assert icoon.get("licentie"), sid
        bestand = str(icoon["bestand"]).replace("\\", "/")
        assert not bestand.lower().startswith(("http://", "https://")), sid
        assert (STATIC / bestand).is_file(), bestand


def test_zondag_heiligen_lage_landen_heeft_lokaal_icoon() -> None:
    by_id = {e["id"]: e for e in load_entries()}
    icoon = icoon_items(by_id["zondag-heiligen-lage-landen"])[0]
    assert icoon.get("rechten") == "ok"
    assert icoon.get("bron")
    assert icoon.get("licentie")
    bestand = str(icoon["bestand"]).replace("\\", "/")
    assert bestand == "iconen/zondag-heiligen-lage-landen.jpg"
    assert (STATIC / bestand).is_file()


def test_gedeeld_bestand_monulphus_gondulphus() -> None:
    by_id = {e["id"]: e for e in load_entries()}
    a = icoon_items(by_id["monulphus"])[0]["bestand"]
    b = icoon_items(by_id["gondulphus"])[0]["bestand"]
    assert a == b == "iconen/monulphus-gondulphus.jpg"


def test_validate_eist_bron_en_licentie() -> None:
    entries = load_entries()
    sample = next(e for e in entries if e["id"] == "willibrord")
    broken = dict(sample)
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
    broken["icoon"] = {
        "bestand": "https://example.org/willibrord.jpg",
        "rechten": "ok",
        "bron": "ergens",
        "licentie": "CC0",
    }
    broken["source_path"] = sample["source_path"]
    errors = collect_content_errors([broken])
    assert any("geen URL" in e for e in errors)


def test_validate_lijst_icoon_indexeert() -> None:
    entries = load_entries()
    sample = next(e for e in entries if e["id"] == "willibrord")
    broken = dict(sample)
    broken["icoon"] = [
        dict(sample["icoon"]),
        {
            "bestand": "iconen/willibrord.jpg",
            "rechten": "ok",
            "bron": "",
            "licentie": "",
        },
    ]
    broken["source_path"] = sample["source_path"]
    errors = collect_content_errors([broken])
    assert any("icoon[1].bron" in e for e in errors)
