"""Icoon toevoegen: licentielus, verkleinen, YAML."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from icoon import (  # noqa: E402
    Fout,
    Gestopt,
    Terminal,
    canonical_licentie,
    icoon_yaml_blok,
    kies_licentie,
    licentie_is_herbruikbaar,
    parse_args,
    prepareer_plaatje,
    run,
    upsert_icoon_in_yaml,
    verzamel_licentie,
    vind_entry,
)


def _mini_repo(tmp_path: Path, *, met_icoon: bool = False) -> Path:
    heil = tmp_path / "data" / "heiligen"
    heil.mkdir(parents=True)
    icoon = ""
    if met_icoon:
        icoon = (
            "icoon:\n"
            "  bestand: iconen/voorbeeld.jpg\n"
            "  rechten: ok\n"
            "  licentie: CC0\n"
            "  bron: oud\n"
        )
    (heil / "voorbeeld.yaml").write_text(
        "id: voorbeeld\n"
        "soort: heilige\n"
        "namen:\n"
        "  primair: Voorbeeld\n"
        "datum:\n"
        "  waarde: \"01-01\"\n"
        f"{icoon}"
        "samenvatting: |\n"
        "  Kort.\n",
        encoding="utf-8",
    )
    (tmp_path / "site" / "static" / "iconen").mkdir(parents=True)
    return tmp_path


def _plaatje(path: Path, size: tuple[int, int] = (80, 60)) -> Path:
    Image.new("RGB", size, (20, 80, 40)).save(path, "PNG")
    return path


def test_canonical_licentie_aliassen() -> None:
    assert canonical_licentie("cc-by-sa") == "CC BY-SA 4.0"
    assert canonical_licentie("Public Domain") == "Publiek domein"
    assert licentie_is_herbruikbaar("CC0")
    assert not licentie_is_herbruikbaar("all rights reserved")


def test_verzamel_licentie_cli_ok() -> None:
    term = Terminal(niet_interactief=True)
    assert verzamel_licentie(term, "cc by-sa 4.0") == "CC BY-SA 4.0"


def test_verzamel_licentie_niet_interactief_fout() -> None:
    term = Terminal(niet_interactief=True)
    try:
        verzamel_licentie(term, "alle rechten voorbehouden")
        raise AssertionError("had moeten falen")
    except Fout as exc:
        assert "niet herbruikbaar" in str(exc).casefold()


def test_licentielus_wijzigen_dan_ok() -> None:
    term = Terminal(antwoorden=["5", "j", "4"])
    assert verzamel_licentie(term, None) == "CC BY-SA 4.0"
    assert any("mag niet in de repo" in r for r in term.uitvoer)


def test_licentielus_stoppen() -> None:
    term = Terminal(antwoorden=["5", "n"])
    try:
        verzamel_licentie(term, None)
        raise AssertionError("had moeten stoppen")
    except Gestopt:
        pass


def test_kies_licentie_anders_herbruikbaar() -> None:
    term = Terminal(antwoorden=["6", "CC-BY-SA 4.0"])
    assert kies_licentie(term) == "CC BY-SA 4.0"


def test_kies_licentie_anders_niet_dan_lus() -> None:
    term = Terminal(antwoorden=["6", " Getty Images", "n", "j", "2"])
    assert verzamel_licentie(term, None) == "CC0"


def test_prepareer_verkleint_grote_zijde(tmp_path: Path) -> None:
    src = _plaatje(tmp_path / "groot.png", (2400, 1200))
    dest = tmp_path / "uit.jpg"
    b, h = prepareer_plaatje(src, dest, max_zijde=800)
    assert max(b, h) == 800
    assert dest.is_file()
    with Image.open(dest) as im:
        assert im.size == (800, 400)


def test_prepareer_schaalt_niet_op(tmp_path: Path) -> None:
    src = _plaatje(tmp_path / "klein.png", (100, 80))
    dest = tmp_path / "uit.jpg"
    b, h = prepareer_plaatje(src, dest, max_zijde=1600)
    assert (b, h) == (100, 80)


def test_upsert_icoon_na_datum() -> None:
    tekst = "id: x\ndatum:\n  waarde: \"01-01\"\nsamenvatting: |\n  a\n"
    blok = icoon_yaml_blok(
        {
            "bestand": "iconen/x.jpg",
            "rechten": "ok",
            "licentie": "CC0",
            "bron": "test",
        }
    )
    out = upsert_icoon_in_yaml(tekst, blok)
    assert "icoon:\n  bestand: iconen/x.jpg\n" in out
    assert out.index("icoon:") > out.index("datum:")
    assert out.index("samenvatting:") > out.index("icoon:")


def test_upsert_vervangt_bestaand_icoon() -> None:
    tekst = (
        "id: x\n"
        "icoon:\n"
        "  bestand: iconen/oud.jpg\n"
        "  rechten: ok\n"
        "samenvatting: |\n"
        "  a\n"
    )
    blok = icoon_yaml_blok(
        {
            "bestand": "iconen/nieuw.jpg",
            "rechten": "ok",
            "licentie": "CC0",
            "bron": "n",
        }
    )
    out = upsert_icoon_in_yaml(tekst, blok)
    assert "iconen/nieuw.jpg" in out
    assert "iconen/oud.jpg" not in out
    assert out.count("icoon:") == 1


def test_vind_entry(tmp_path: Path) -> None:
    _mini_repo(tmp_path)
    p = vind_entry(tmp_path, "voorbeeld")
    assert p.name == "voorbeeld.yaml"
    try:
        vind_entry(tmp_path, "ontbreekt")
        raise AssertionError("had moeten falen")
    except Fout:
        pass


def test_run_niet_interactief(tmp_path: Path) -> None:
    root = _mini_repo(tmp_path)
    src = _plaatje(tmp_path / "in.png", (200, 200))
    args = parse_args(
        [
            "--id",
            "voorbeeld",
            "--plaatje",
            str(src),
            "--licentie",
            "CC0",
            "--bron",
            "Wikimedia Commons — File:Voorbeeld.jpg",
            "--niet-interactief",
            "--root",
            str(root),
        ]
    )
    term = Terminal(niet_interactief=True)
    assert run(args, term) == 0
    yaml_text = (root / "data" / "heiligen" / "voorbeeld.yaml").read_text(
        encoding="utf-8"
    )
    assert "iconen/voorbeeld.jpg" in yaml_text
    assert "CC0" in yaml_text
    assert (root / "site" / "static" / "iconen" / "voorbeeld.jpg").is_file()


def test_run_bestaand_icoon_niet_interactief_zonder_vlag(tmp_path: Path) -> None:
    root = _mini_repo(tmp_path, met_icoon=True)
    src = _plaatje(tmp_path / "in.png")
    args = parse_args(
        [
            "--id",
            "voorbeeld",
            "--plaatje",
            str(src),
            "--licentie",
            "CC0",
            "--bron",
            "x",
            "--niet-interactief",
            "--root",
            str(root),
        ]
    )
    assert run(args, Terminal(niet_interactief=True)) == 1


def test_run_cli_slechte_licentie_niet_interactief() -> None:
    args = parse_args(
        [
            "--id",
            "voorbeeld",
            "--plaatje",
            "x.png",
            "--licentie",
            "copyright",
            "--bron",
            "x",
            "--niet-interactief",
        ]
    )
    assert run(args, Terminal(niet_interactief=True)) == 1
