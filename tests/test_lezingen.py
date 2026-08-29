"""Contracttests: docs/specs/lezingen.md voorbeelden ↔ scripts/lezingen.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from kalender import orthodox_pascha, mmdd_from_date  # noqa: E402
from lezingen import (  # noqa: E402
    SPEC_PATH,
    parse_spec_voorbeelden,
    resolve_lezingen,
    resultaat_matches_verwacht,
    spec_body_for_uitleg,
)


def test_spec_exists() -> None:
    assert SPEC_PATH.is_file()
    assert "R2" in SPEC_PATH.read_text(encoding="utf-8")


def test_parse_voorbeelden_nonempty() -> None:
    voorbeelden = parse_spec_voorbeelden()
    assert len(voorbeelden) >= 3
    statuses = {v["status"] for v in voorbeelden}
    assert "implemented" in statuses


def test_pascha_2025_mmdd_matches_computus() -> None:
    assert mmdd_from_date(orthodox_pascha(2025)) == "04-20"


@pytest.mark.parametrize(
    "voorbeeld",
    [v for v in parse_spec_voorbeelden() if v.get("status") == "implemented"],
    ids=lambda v: v["id"],
)
def test_implemented_voorbeelden(voorbeeld: dict) -> None:
    result = resolve_lezingen(
        int(voorbeeld["jaar"]),
        str(voorbeeld["mmdd"]),
        str(voorbeeld.get("stijl") or "nieuw"),
    )
    assert result.status == "gevonden", voorbeeld["id"]
    errors = resultaat_matches_verwacht(result, voorbeeld["verwacht"])
    assert not errors, f"{voorbeeld['id']}: " + "; ".join(errors)


def test_theofanie_otstupka_2024() -> None:
    """Na week 33: herhalingsreeks N=5 begint 22 jan 2024 met tabelweek 30."""
    r = resolve_lezingen(2024, "01-22", "nieuw")
    assert "R3-theofanie-otstupka" in r.regels
    assert [a.ref for a in r.apostel] == ["Heb. 8:7-13"]
    assert [e.ref for e in r.evangelie] == ["Mark. 8:11-21"]
    # Week 17 in het midden van N=5
    r2 = resolve_lezingen(2024, "02-05", "nieuw")
    assert "R3-theofanie-otstupka" in r2.regels
    assert [a.ref for a in r2.apostel] == ["Ef. 1:22-2:3"]


def test_theofanie_otstupka_afwezig_2025() -> None:
    """2025: Tollenaar valt vóór maandag van week 34 — geen winter-отступка."""
    r = resolve_lezingen(2025, "01-13", "nieuw")
    assert "R3-theofanie-otstupka" not in r.regels
    assert [a.ref for a in r.apostel] == ["Heb. 8:7-13"]


def test_februari_2025_eindreeks_niet_leeg() -> None:
    """Regressie: dagen vóór Tollenaar blijven op de Pinksterreeks (32e/33e week)."""
    r1 = resolve_lezingen(2025, "02-01", "nieuw")
    assert r1.status == "gevonden"
    assert "R3" in r1.regels
    assert r1.apostel and r1.evangelie
    r3 = resolve_lezingen(2025, "02-03", "nieuw")
    assert r3.status == "gevonden"
    assert r3.apostel and r3.evangelie
    r2 = resolve_lezingen(2025, "02-02", "nieuw")
    assert r2.override_id == "ontmoeting-in-de-tempel"


def test_den_haag_silvester_toevoegen() -> None:
    """Actieve parochie den-haag: Silvester op 2 jan bij rijádovoe."""
    r = resolve_lezingen(2026, "01-02", "nieuw")
    assert r.override_id == "silvester"
    assert r.modus == "toevoegen"
    assert "Heb. 5:4-10" in [a.ref for a in r.apostel]
    assert "Joh. 3:1-15" in [e.ref for e in r.evangelie]


def test_parochie_override_wint_van_gedeeld(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from lezingen import load_overrides

    monkeypatch.setattr("lezingen.DATA_DIR", tmp_path)
    (tmp_path / "parochies").mkdir()
    (tmp_path / "feest-overrides.yaml").write_text(
        "overrides:\n"
        "  - id: basis\n"
        "    match: { mmdd: \"01-02\" }\n"
        "    apostel: [{ ref: \"BASIS-A\" }]\n"
        "    evangelie: [{ ref: \"BASIS-E\" }]\n"
        "    regels: [R2]\n",
        encoding="utf-8",
    )
    (tmp_path / "config.yaml").write_text("parochie: test\n", encoding="utf-8")
    (tmp_path / "parochies" / "test.yaml").write_text(
        "overrides:\n"
        "  - id: silvester-lokaal\n"
        "    match: { mmdd: \"01-02\" }\n"
        "    apostel: [{ ref: \"LOKAAL-A\" }]\n"
        "    evangelie: [{ ref: \"LOKAAL-E\" }]\n"
        "    regels: [R2]\n",
        encoding="utf-8",
    )
    ovs = load_overrides()
    assert len(ovs) == 2
    assert ovs[1]["prioriteit"] == 300
    r = resolve_lezingen(2026, "01-02", "nieuw", overrides=ovs)
    assert r.override_id == "silvester-lokaal"
    assert [a.ref for a in r.apostel] == ["LOKAAL-A"]


def test_pending_voorbeelden_are_skipped_by_filter() -> None:
    pending = [v for v in parse_spec_voorbeelden() if v["status"] == "pending"]
    # Mag leeg zijn als alle voorbeelden geïmplementeerd zijn.
    assert isinstance(pending, list)


def test_weekreeks_fills_ordinary_weekday() -> None:
    r = resolve_lezingen(2025, "07-02", "nieuw")
    assert r.status == "gevonden"
    assert "R3" in r.regels
    assert r.apostel and r.evangelie


def test_lucaanse_sprong_switches_gospel() -> None:
    from lezingen import lucaanse_sprong_maandag

    assert lucaanse_sprong_maandag(2025).isoformat() == "2025-09-22"
    r = resolve_lezingen(2025, "09-22", "nieuw")
    assert r.status == "gevonden"
    assert "R3-lucaans" in r.regels
    assert r.evangelie and r.evangelie[0].ref.startswith("Luc.")


def test_r5_ontslapen_vervangt() -> None:
    r = resolve_lezingen(2025, "08-15", "nieuw")
    assert r.modus == "vervangen"
    assert "R5" in r.regels
    assert r.rijadovoe is not None
    assert [a.ref for a in r.apostel] == ["Fil. 2:5-11"]


def test_r5_elia_zondag_toevoegen() -> None:
    r = resolve_lezingen(2025, "07-20", "nieuw")
    assert r.modus == "toevoegen"
    assert r.regels == ["R3", "R2", "R5"]
    assert [a.ref for a in r.apostel] == ["Rom. 12:6-14", "Jak. 5:10-20"]


def test_lucaanse_aanpassing_classificatie() -> None:
    from lezingen import lucaanse_aanpassing

    assert lucaanse_aanpassing(2010) == "otstupka"  # Julian 22 maart
    assert lucaanse_aanpassing(2025) == "prestupka"  # Julian 7 april
    assert lucaanse_aanpassing(2026) == "otstupka"  # Julian 30 maart


def test_otstupka_voor_sprong_blijft_matteus() -> None:
    """2010: vroege Pascha — dag vóór Lucaanse maandag nog Matteüs, geen Luc.-tag."""
    from lezingen import lucaanse_sprong_maandag
    from datetime import timedelta

    luke = lucaanse_sprong_maandag(2010)
    before = luke - timedelta(days=1)
    mmdd = f"{before.month:02d}-{before.day:02d}"
    r = resolve_lezingen(2010, mmdd, "nieuw")
    assert r.status == "gevonden"
    assert "R3-lucaans" not in r.regels
    assert r.evangelie and not r.evangelie[0].ref.startswith("Luc.")
    # Op de sprongdag zelf: Luc. + otstupka-tag
    r2 = resolve_lezingen(2010, f"{luke.month:02d}-{luke.day:02d}", "nieuw")
    assert "R3-lucaans" in r2.regels
    assert "R3-otstupka" in r2.regels
    assert r2.evangelie[0].ref.startswith("Luc.")


def test_prestupka_tag_na_sprong() -> None:
    r = resolve_lezingen(2025, "09-22", "nieuw")
    assert "R3-lucaans" in r.regels
    assert "R3-prestupka" in r.regels
    assert r.evangelie and r.evangelie[0].ref.startswith("Luc.")


def test_aankondiging_op_pascha_oud_1991() -> None:
    r = resolve_lezingen(1991, "03-25", "oud")
    assert r.override_id == "aankondiging-op-pascha"
    assert [a.ref for a in r.apostel] == ["Hand. 1:1-8", "Heb. 2:11-18"]


def test_nicolaas_polyeleos_weekdag_vervangt() -> None:
    # 6 dec 2025 is zaterdag → polyeleos auto → vervangen
    r = resolve_lezingen(2025, "12-06", "nieuw")
    assert r.override_id == "nicolaas-wonderdoener"
    assert r.modus == "vervangen"
    assert [a.ref for a in r.apostel] == ["Heb. 13:17-21"]


def test_spec_body_for_uitleg_strips_examples() -> None:
    body = spec_body_for_uitleg()
    assert "```lezingen-voorbeeld" not in body
    assert "### R2" in body or "## Regels" in body


def test_liturgische_daglabel_na_pinksteren_en_triodion() -> None:
    from datetime import timedelta

    from lezingen import liturgische_daglabel, week_kop_label

    pascha = orthodox_pascha(2026)
    pentecost = pascha + timedelta(days=49)
    thu23 = pentecost + timedelta(days=22 * 7 + 4)
    assert liturgische_daglabel(
        thu23.year, mmdd_from_date(thu23), "nieuw"
    ) == "23e donderdag na Pinksteren"
    verloren = pascha + timedelta(days=-63)
    assert liturgische_daglabel(
        verloren.year, mmdd_from_date(verloren), "nieuw"
    ) == "Zondag van de verloren zoon"
    ma2 = pentecost + timedelta(days=8)
    assert week_kop_label(ma2) == "2e week na Pinksteren"


def test_menaion_override_niet_als_daglabel() -> None:
    from lezingen import resolve_lezingen

    r = resolve_lezingen(2026, "07-15", "nieuw")
    assert r.override_id == "vladimir-gelijkaan-apostelen"
    assert "Vladimir" not in (r.daglabel or "")
    d = r.as_dict()
    assert d["override_laag"] == "menaion"
    assert d["override_naam"] == "Vladimir, gelijkaan de apostelen"


def test_feest_override_laag_in_json() -> None:
    from lezingen import resolve_lezingen

    r = resolve_lezingen(2026, "01-01", "nieuw")
    d = r.as_dict()
    assert d["override_id"] == "besnijdenis-des-heren"
    assert d["override_laag"] == "feest"
    assert d["override_naam"] == "Besnijdenis des Heren"


def test_weekreeks_galaten_zaterdag_26_is_schone_ref() -> None:
    import yaml

    raw = yaml.safe_load(
        (ROOT / "data" / "lezingen" / "weekreeks.yaml").read_text(encoding="utf-8")
    )
    row = next(
        r
        for r in raw["dagen"]
        if r["periode"] == "na_pinksteren"
        and r["week"] == 26
        and r["weekdag"] == 6
    )
    assert row["apostel"][0]["ref"] == "Gal. 3:8-12"
