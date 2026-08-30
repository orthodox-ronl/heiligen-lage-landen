"""Rangschikking op /feesten/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate import (  # noqa: E402
    APOSTEL_FEESTEN,
    GROTE_FEESTEN,
    overzicht_rang,
    overzicht_sortering,
)

SITE = ROOT / "site"


def test_grote_feesten_zijn_de_twaalf_plus_pascha() -> None:
    assert "pascha" in GROTE_FEESTEN
    assert "kerst" in GROTE_FEESTEN
    assert "pinksteren" in GROTE_FEESTEN
    assert "pokrov" not in GROTE_FEESTEN
    assert "voorfeest-kerst" not in GROTE_FEESTEN
    assert len(GROTE_FEESTEN) == 13


def test_overzicht_rang_groepen() -> None:
    assert overzicht_rang({"id": "kerst", "cyclus": "jaar"}) == "grote"
    assert overzicht_rang({"id": "pascha", "cyclus": "paascyclus"}) == "grote"
    assert overzicht_rang({"id": "voorfeest-kerst", "cyclus": "jaar"}) == "omlijsting"
    assert overzicht_rang({"id": "synaxis-moeder-gods", "cyclus": "jaar"}) == "omlijsting"
    assert overzicht_rang({"id": "pokrov", "cyclus": "jaar"}) == "heer-moeder"
    assert overzicht_rang({"id": "petrus-en-paulus", "cyclus": "jaar"}) == "apostelen"
    assert "petrus-en-paulus" in APOSTEL_FEESTEN
    assert overzicht_rang({"id": "thomaszondag", "cyclus": "paascyclus"}) == "paascyclus"
    assert overzicht_rang({"id": "begin-kerkelijk-jaar", "cyclus": "jaar"}) == "overig"


def test_kerkelijk_jaar_zet_september_voor_januari() -> None:
    sept = overzicht_sortering(
        {"id": "a", "cyclus": "jaar", "datum_norm": {"feestdatum": "09-01"}}
    )
    jan = overzicht_sortering(
        {"id": "b", "cyclus": "jaar", "datum_norm": {"feestdatum": "01-06"}}
    )
    assert sept < jan


def test_feesten_layout_heeft_rangschikking() -> None:
    html = (SITE / "layouts" / "feesten" / "list.html").read_text(encoding="utf-8")
    assert "Params.overzicht_sortering" in html
    assert 'data-feesten-rangschikking="kerkelijk"' in html
    assert 'data-feesten-rangschikking="burgerlijk"' in html
    assert 'data-feesten-rangschikking="rang"' in html
    assert 'data-feesten-rangschikking="naam"' in html
    assert 'data-info-tip="feesten-rangschikking"' in html
    assert "feesten-overzicht.js" in html
    assert 'id="feesten-lijst"' in html
    default_list = (SITE / "layouts" / "_default" / "list.html").read_text(
        encoding="utf-8"
    )
    assert "data-feesten-rangschikking" not in default_list


def test_feesten_js_url_en_groepen() -> None:
    js = (SITE / "assets" / "js" / "feesten-overzicht.js").read_text(encoding="utf-8")
    assert "rangschikking" in js
    assert "feesten-rangschikking" in js
    assert "kerkelijk" in js
    assert "Grote feesten" in js
    assert "if (bucket !== 0)" in js
    assert "el.dataset.sortering" in js


def test_popovers_en_uitleg_bestaan() -> None:
    cal = (SITE / "assets" / "js" / "calendar.js").read_text(encoding="utf-8")
    assert 'kind === "feesten-rangschikking"' in cal
    assert 'kind === "kerkelijk-jaar"' in cal
    assert 'kind === "synaxarion-bladeren"' in cal
    syn = (SITE / "layouts" / "_default" / "synaxarion.html").read_text(
        encoding="utf-8"
    )
    assert 'data-info-tip="synaxarion-bladeren"' in syn
    uitleg = (SITE / "layouts" / "uitleg" / "list.html").read_text(encoding="utf-8")
    assert '"feesten"' in uitleg
