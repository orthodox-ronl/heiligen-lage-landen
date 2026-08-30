"""Gebruikersuitleg versus technische bijlage; beheerdershome."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate import ACHTERGROND_TOPICS, CONTENT, _split_hugo_markdown  # noqa: E402

UITLEG = CONTENT / "uitleg"
BEHEER = CONTENT / "beheer"

# Onderwerpen met een handmatige gebruikerspagina + technische bijlage.
# Vasten is gegenereerd; de splitsing daarvan staat in tests/test_vasten.py.
HANDMATIGE_ONDERWERPEN = (
    "nieuw-oud",
    "feestdatum",
    "datumpagina",
    "synaxarion",
    "feesten",
    "heiligen",
    "kleuren",
    "agenda",
    "toon",
)

TECHNISCHE_SPOREN = (
    "data/",
    "scripts/",
    ".yaml",
    ".py",
    "calendar.js",
    "?jaar=",
    "?dag=",
    "MM-DD",
    "+13",
    "wo/vr",
    "→",
)

HOW_TOS = (
    "how-to-publiceren",
    "how-to-heiligen-feesten",
    "how-to-namen",
    "how-to-vasten",
    "how-to-lezingen",
)

PAGINA_OPBOUW_SLUGS = (
    "startpagina",
    "datumpagina",
    "jaarkalender",
    "lezingenrooster",
    "synaxarion",
    "heiligenoverzicht",
    "heilige",
    "feest",
    "vastenperiode",
    "overzichten-feesten-vasten",
    "agenda",
    "uitleg-overzicht",
    "uitleg-onderwerp",
    "uitleg-technisch",
    "beheer",
)


def _meta_body(path: Path) -> tuple[dict, str]:
    return _split_hugo_markdown(path.read_text(encoding="utf-8"))


def test_elk_handmatig_onderwerp_heeft_technische_bijlage() -> None:
    for topic in HANDMATIGE_ONDERWERPEN:
        user = UITLEG / f"{topic}.md"
        tech = UITLEG / f"{topic}-technisch.md"
        assert user.is_file(), user
        assert tech.is_file(), tech
        umeta, ubody = _meta_body(user)
        tmeta, tbody = _meta_body(tech)
        assert umeta.get("build", {}).get("list") != "never"
        assert tmeta.get("build", {}).get("list") == "never"
        assert tmeta.get("build", {}).get("render") == "always"
        assert tmeta.get("uitleg_stijl") == f"{topic}-technisch"
        assert f"/uitleg/{topic}-technisch" in ubody
        assert f"/uitleg/{topic}" in tbody


def test_gebruikerspaginas_zonder_technische_sporen() -> None:
    for topic in HANDMATIGE_ONDERWERPEN:
        _meta, body = _meta_body(UITLEG / f"{topic}.md")
        hoofd, voet = body, ""
        if "## Voor wie de site bijhoudt" in body:
            hoofd, voet = body.split("## Voor wie de site bijhoudt", 1)
        for spoor in TECHNISCHE_SPOREN:
            assert spoor not in hoofd, f"{topic}: {spoor!r} in gebruikersdeel"
        assert "technische pagina" in voet


def test_technische_bijlagen_niet_in_uitleg_overzicht_front_matter() -> None:
    for path in UITLEG.glob("*-technisch.md"):
        meta, _body = _meta_body(path)
        assert meta.get("build", {}).get("list") == "never", path.name


def test_beheer_home_onderscheidt_aanraken_en_overschrijven() -> None:
    meta, body = _meta_body(BEHEER / "_index.md")
    assert meta["title"] == "Voor beheerders"
    assert "data/heiligen/" in body
    assert "data/regels/vasten.yaml" in body
    assert "site/content/heiligen/*.md" in body
    assert "site/content/uitleg/vasten.md" in body
    assert "entries.json" in body
    assert "plaatsen.yaml" in body
    assert "plaatsen.json" in body
    assert "beheer-tabel-aanraken" in body
    assert "beheer-tabel-afblijven" in body
    for slug in HOW_TOS:
        assert f"/beheer/{slug}" in body
    assert "/beheer/selectie" in body
    assert "site/content/beheer/selectie.md" in body
    assert "/beheer/pagina-opbouw" in body
    assert "/beheer/ideeen" in body
    assert "site/content/beheer/pagina-opbouw/" in body
    assert "site/content/beheer/ideeen.md" in body
    assert "## Hoe een pagina eruit moet zien" in body
    assert "how-to" in body.lower()
    _, _, rest = body.partition("## Hoe een pagina eruit moet zien")
    contract, _, howtos = rest.partition("## How-to’s")
    assert "contracten" in contract.lower()
    assert "niet hoe u YAML" in contract or "niet hoe u YAML of code" in contract
    assert "{{% ref \"/beheer/pagina-opbouw\" %}}" in contract
    assert "{{% ref \"/beheer/how-to-publiceren\" %}}" in howtos
    assert "pagina-opbouw" not in howtos
    assert "{{% ref \"/beheer/ideeen\" %}}" in contract


def test_pagina_opbouw_index_is_contract_geen_how_to() -> None:
    path = BEHEER / "pagina-opbouw" / "_index.md"
    assert path.is_file(), path
    meta, body = _meta_body(path)
    assert meta["title"] == "Pagina-opbouw"
    assert "contracten" in body.lower()
    assert "how-to" in body.lower()
    assert "/beheer" in body
    assert "hoofdnavigatie" in body.lower()
    for slug in PAGINA_OPBOUW_SLUGS:
        assert f"/beheer/pagina-opbouw/{slug}" in body, slug


def test_pagina_opbouw_skeletten_bestaan_met_wel_niet() -> None:
    banner = "**Contract, geen echte inhoud.**"
    for slug in PAGINA_OPBOUW_SLUGS:
        path = BEHEER / "pagina-opbouw" / f"{slug}.md"
        assert path.is_file(), path
        meta, body = _meta_body(path)
        assert isinstance(meta.get("title"), str) and meta["title"].strip()
        assert banner in body, slug
        assert "**Wel:**" in body or "**Wel (" in body, slug
        assert "**Niet:**" in body or "**Niet (" in body, slug


def test_heilige_skelet_uitklap_selectie() -> None:
    _meta, body = _meta_body(BEHEER / "pagina-opbouw" / "heilige.md")
    assert "## Plaats in deze kalender" in body
    assert "**Gesloten.**" in body
    assert "`<details>`" in body or "<details>" in body
    assert "voldoet" in body
    assert "kandidaat-schrappen" in body
    assert "/beheer/selectie" in body
    assert "**Gesloten.**" in body
    assert "Andere gedenkdagen" in body
    assert "Voorstel (nog niet uitvoeren)" not in body


def test_pagina_opbouw_niet_in_hoofdnav() -> None:
    html = (ROOT / "site" / "layouts" / "_default" / "baseof.html").read_text(
        encoding="utf-8"
    )
    start = html.index('aria-label="Hoofdnavigatie"')
    end = html.index("</nav>", start)
    nav = html[start:end]
    assert "pagina-opbouw" not in nav
    assert "beheer/" not in nav


def test_how_tos_bestaan() -> None:
    for slug in HOW_TOS:
        path = BEHEER / f"{slug}.md"
        assert path.is_file(), path
        meta, body = _meta_body(path)
        assert isinstance(meta.get("title"), str) and meta["title"].strip()
        assert "python scripts/" in body or "generate.py" in body or "data/" in body


def test_how_to_lezingen_zonder_hugo_ref_naar_ontbrekende_paginas() -> None:
    text = (BEHEER / "how-to-lezingen.md").read_text(encoding="utf-8")
    assert 'ref "/uitleg/lezingen' not in text
    assert "data/lezingen/" in text
    assert "parochies/" in text


def test_uitleg_index_wijst_naar_beheer() -> None:
    _meta, body = _meta_body(UITLEG / "_index.md")
    assert "/beheer" in body
    assert "geen" in body.lower()
    assert "Lage Landen" in body
    assert "typikon" in body.lower()


def test_uitleg_overzicht_groepeert_onderwerpen() -> None:
    layout = (ROOT / "site" / "layouts" / "uitleg" / "list.html").read_text(
        encoding="utf-8"
    )
    assert "Op één dag" in layout
    assert "Heiligen van hier" in layout
    assert "Kalender gebruiken" in layout
    assert "Reageren" in layout
    for slug in (
        "datumpagina",
        "toon",
        "lezingen",
        "vasten",
        "heiligen",
        "nieuw-oud",
        "feestdatum",
        "synaxarion",
        "feesten",
        "kleuren",
        "agenda",
        "reactie",
    ):
        assert f'"{slug}"' in layout


def test_sitenaam_popover_wijst_naar_uitleg() -> None:
    js = (ROOT / "site" / "assets" / "js" / "calendar.js").read_text(
        encoding="utf-8"
    )
    assert 'kind === "site"' in js
    assert "Nederlandersmet" not in js
    assert "Lage Landen" in js
    assert 'assetUrl("uitleg/")' in js


def test_achtergrond_topics_hebben_geen_technische_ids() -> None:
    ids = {t["id"] for t in ACHTERGROND_TOPICS}
    assert "vasten-technisch" not in ids
    for topic in HANDMATIGE_ONDERWERPEN:
        assert topic in ids
        assert f"{topic}-technisch" not in ids


def test_agenda_pagina_heeft_geen_lijst_vaste_feeds() -> None:
    layout = (ROOT / "site" / "layouts" / "_default" / "agenda.html").read_text(
        encoding="utf-8"
    )
    js = (ROOT / "site" / "assets" / "js" / "calendar.js").read_text(encoding="utf-8")
    assert "ics-all-links" not in layout
    assert "Alle vaste feeds" not in layout
    assert 'name="ics-modus"' in layout
    assert "Kopieer de agenda-link" in layout
    assert "Download de kalender" in layout
    assert "ics-voorbeeld-week" in layout
    assert "Open in Apple Agenda" in layout
    assert "function icsDayTitle" in js
    assert "ics-all-links" not in js
    assert "heiligen-feesten-nieuw" not in js


def test_jaarkalender_en_uitleg_zelfde_legenda_swatches() -> None:
    kal = (ROOT / "site" / "layouts" / "_default" / "kalender.html").read_text(
        encoding="utf-8"
    )
    uitleg = (CONTENT / "uitleg" / "kleuren.md").read_text(encoding="utf-8")
    css = (ROOT / "site" / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    for cls in (
        "day-feest",
        "day-heilige",
        "day-vasten",
        "day-vastenvrij",
    ):
        assert cls in kal, cls
        assert cls in uitleg, cls
    assert "day-beide" not in kal
    assert "day-today" not in kal
    assert "day-beide" not in uitleg
    assert "kalender-sticky-title-row" in kal
    assert "legend-chip" in kal
    assert "legend-label-short" in kal
    assert ".kalender-sticky-title-row" in css
    assert ".kalender-page .legend.compact" not in css


def test_generate_raakt_pagina_opbouw_niet() -> None:
    src = (ROOT / "scripts" / "generate.py").read_text(encoding="utf-8")
    assert "pagina-opbouw" not in src


def test_datum_url_canoniek_jjjj_mm_dd() -> None:
    js = (ROOT / "site" / "assets" / "js" / "calendar.js").read_text(encoding="utf-8")
    assert 'params.get("datum")' in js
    assert 'datum: year + "-" + mmdd' in js
    assert 'pageUrl("datum/", { jaar: year, dag: mmdd' not in js


def test_synaxarion_start_huidige_maand_zonder_itemtelling() -> None:
    js = (ROOT / "site" / "assets" / "js" / "calendar.js").read_text(encoding="utf-8")
    assert "getMonth() + 1" in js
    assert 'activeMonth = "01"' not in js
    assert ": ${count} item(s)." not in js


def test_heiligenkaart_ctrl_zoom_en_nl_be() -> None:
    js = (ROOT / "site" / "assets" / "js" / "heiligen-kaart.js").read_text(
        encoding="utf-8"
    )
    assert "ctrlKey" in js
    assert "[49.45, 2.4]" in js
    assert "fitBounds(group.getBounds()" not in js


def test_zoeklabel_zelfde_lettergrootte() -> None:
    css = (ROOT / "site" / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    assert ".search-label" in css
    assert "font-size: inherit" in css
    assert "font-size: 0.9rem;\n  margin-bottom: 0.25rem;" not in css


def test_startpagina_identiteit_via_popover() -> None:
    _meta, body = _meta_body(BEHEER / "pagina-opbouw" / "startpagina.md")
    assert "heiligenoverzicht" in body
    assert "dagkaart van vandaag staat **niet** hier" in body


def test_nieuw_oud_uitleg_beschrijft_haakjes() -> None:
    _meta, body = _meta_body(UITLEG / "nieuw-oud.md")
    hoofd, _voet = body.split("## Voor wie de site bijhoudt", 1)
    assert "Op een feest- of vastenpagina" in hoofd
    assert "tussen haakjes" in hoofd
    assert "Willibrord" in hoofd
    assert "Pinksteren" in hoofd
    assert "westers" in hoofd.lower()
    _fmeta, fbody = _meta_body(UITLEG / "feestdatum.md")
    fhoofd = fbody.split("## Voor wie de site bijhoudt", 1)[0]
    assert "geen tweede feestdatum" in fhoofd
    assert "/uitleg/nieuw-oud" in fhoofd
