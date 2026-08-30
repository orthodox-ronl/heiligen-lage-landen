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
    bevestig_entry,
    bron_stem,
    canonical_licentie,
    doel_bestand,
    icoon_yaml_blok,
    kies_licentie,
    licentie_is_herbruikbaar,
    parse_args,
    prepareer_plaatje,
    run,
    upsert_icoon_in_yaml,
    verzamel_licentie,
    vind_entry,
    zoek_entries,
    zoek_plaatsen,
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
    (tmp_path / "data" / "plaatsen.yaml").write_text(
        "plaatsen:\n"
        "  - id: hemelum\n"
        "    naam: Hemelum\n"
        "    lat: 52.8\n"
        "    lon: 5.4\n"
        "    soort: plaats\n"
        "  - id: groningen\n"
        "    naam: Groningen\n"
        "    lat: 53.2\n"
        "    lon: 6.5\n"
        "    soort: plaats\n",
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
    assert licentie_is_herbruikbaar("Toestemming van de parochie te Groningen")
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
    term = Terminal(antwoorden=["6", "j", "4"])
    assert verzamel_licentie(term, None) == "CC BY-SA 4.0"
    assert any("mag niet in de repo" in r for r in term.uitvoer)


def test_licentielus_stoppen() -> None:
    term = Terminal(antwoorden=["6", "n"])
    try:
        verzamel_licentie(term, None)
        raise AssertionError("had moeten stoppen")
    except Gestopt:
        pass


def test_kies_licentie_anders_herbruikbaar() -> None:
    term = Terminal(antwoorden=["7", "CC-BY-SA 4.0"])
    assert kies_licentie(term) == "CC BY-SA 4.0"


def test_kies_licentie_anders_niet_dan_lus() -> None:
    term = Terminal(antwoorden=["7", " Getty Images", "n", "j", "2"])
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
        [
            {
                "bestand": "iconen/x.jpg",
                "rechten": "ok",
                "licentie": "CC0",
                "bron": "test",
            }
        ]
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
        [
            {
                "bestand": "iconen/nieuw.jpg",
                "rechten": "ok",
                "licentie": "CC0",
                "bron": "n",
            }
        ]
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


def test_doel_bestand_eerste_en_extra() -> None:
    assert bron_stem(Path("heiligen-lage-landen-muuricoon-hemelum.png")) == (
        "heiligen-lage-landen-muuricoon-hemelum"
    )
    assert doel_bestand("voorbeeld", Path("foto.png"), []) == "iconen/voorbeeld.jpg"
    assert doel_bestand(
        "voorbeeld",
        Path("muuricoon-hemelum.png"),
        ["iconen/voorbeeld.jpg"],
    ) == "iconen/muuricoon-hemelum.jpg"
    assert doel_bestand(
        "odulphus",
        Path("foto.png"),
        ["iconen/odulphus.jpg"],
        "hemelum",
    ) == "iconen/odulphus-hemelum.jpg"


def test_zoek_naam_en_plaats() -> None:
    treffers = zoek_entries(ROOT, "odulf")
    assert "odulphus" in [t[1] for t in treffers]
    from icoon import laad_plaatsen

    plaatsen = laad_plaatsen(ROOT)
    gevonden = zoek_plaatsen(plaatsen, "leeuwarden")
    assert gevonden[0][1]["id"] == "leeuwarden"
    assert bevestig_entry(
        Terminal(niet_interactief=True),
        ROOT,
        "odulphus",
        niet_interactief=True,
    ) == "odulphus"


def test_help_toont_positioneel_plaatje(capsys) -> None:
    try:
        parse_args(["-h"])
        raise AssertionError("help had moeten stoppen")
    except SystemExit as exc:
        assert exc.code == 0
    tekst = capsys.readouterr().out
    assert "[PLAATJE]" in tekst
    assert "unrecognized arguments" not in tekst


def test_parse_positioneel_plaatje() -> None:
    args = parse_args(["heiligen-lage-landen-muuricoon-hemelum.png", "--id", "x"])
    assert args.plaatje_pos == Path("heiligen-lage-landen-muuricoon-hemelum.png")
    assert args.id == "x"
    alleen = parse_args(["heiligen-lage-landen-muuricoon-hemelum.png"])
    assert alleen.plaatje_pos == Path(
        "heiligen-lage-landen-muuricoon-hemelum.png"
    )


def test_run_tweede_icoon_positioneel(tmp_path: Path) -> None:
    root = _mini_repo(tmp_path, met_icoon=True)
    src = _plaatje(tmp_path / "muuricoon-hemelum.png")
    args = parse_args(
        [
            str(src),
            "--id",
            "voorbeeld",
            "--licentie",
            "CC0",
            "--bron",
            "muur",
            "--niet-interactief",
            "--root",
            str(root),
        ]
    )
    assert run(args, Terminal(niet_interactief=True)) == 0
    yaml_text = (root / "data" / "heiligen" / "voorbeeld.yaml").read_text(
        encoding="utf-8"
    )
    assert "iconen/voorbeeld.jpg" in yaml_text
    assert "iconen/voorbeeld-hemelum.jpg" in yaml_text
    assert "plaats: hemelum" in yaml_text
    assert "iconen:" in yaml_text
    assert "primair: true" in yaml_text
    assert (root / "site" / "static" / "iconen" / "voorbeeld-hemelum.jpg").is_file()


def test_run_parochie_plaats_hemelum(tmp_path: Path) -> None:
    root = _mini_repo(tmp_path)
    src = _plaatje(tmp_path / "foto.png")
    args = parse_args(
        [
            str(src),
            "--id",
            "Voorbeeld",
            "--licentie",
            "toestemming van de parochie",
            "--plaats",
            "hemelum",
            "--niet-interactief",
            "--root",
            str(root),
        ]
    )
    assert run(args, Terminal(niet_interactief=True)) == 0
    yaml_text = (root / "data" / "heiligen" / "voorbeeld.yaml").read_text(
        encoding="utf-8"
    )
    assert "plaats: hemelum" in yaml_text
    assert "soort: foto" in yaml_text
    assert "iconen/voorbeeld-hemelum.jpg" in yaml_text
    assert (root / "site" / "static" / "iconen" / "voorbeeld-hemelum.jpg").is_file()


def test_run_zelfde_doelnaam_eist_overschrijven(tmp_path: Path) -> None:
    root = _mini_repo(tmp_path, met_icoon=True)
    src = _plaatje(tmp_path / "voorbeeld.png")
    args = parse_args(
        [
            str(src),
            "--id",
            "voorbeeld",
            "--licentie",
            "CC0",
            "--bron",
            "nieuw",
            "--niet-interactief",
            "--root",
            str(root),
        ]
    )
    assert run(args, Terminal(niet_interactief=True)) == 1
    args_ok = parse_args(
        [
            str(src),
            "--id",
            "voorbeeld",
            "--licentie",
            "CC0",
            "--bron",
            "nieuw",
            "--overschrijven",
            "--niet-interactief",
            "--root",
            str(root),
        ]
    )
    assert run(args_ok, Terminal(niet_interactief=True)) == 0
    yaml_text = (root / "data" / "heiligen" / "voorbeeld.yaml").read_text(
        encoding="utf-8"
    )
    assert yaml_text.count("icoon:") == 1
    assert "  - bestand:" not in yaml_text
    assert "bron: nieuw" in yaml_text


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
