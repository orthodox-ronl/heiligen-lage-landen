"""UI- en data-afspraken voor jaarkalender, synaxarion, teruggave."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "site" / "assets" / "js" / "calendar.js"
CSS = ROOT / "site" / "assets" / "css" / "site.css"
DATA = ROOT / "data" / "feesten"


def test_jaarkalender_legenda_vier_basiskleuren() -> None:
    kal = (ROOT / "site" / "layouts" / "_default" / "kalender.html").read_text(
        encoding="utf-8"
    )
    assert "day-vastenvrij" in kal
    assert kal.count("<li") == 4


def test_day_beide_heeft_strakke_kleurstop() -> None:
    css = CSS.read_text(encoding="utf-8")
    beide = css.split(".day-beide {", 1)[1].split("}", 1)[0]
    assert "0 50%" in beide
    assert "50% 100%" in beide


def test_synaxarion_stapelt_in_een_rij() -> None:
    js = JS.read_text(encoding="utf-8")
    assert "synaxarion-stack" in js
    assert "function entryImportance" in js
    chunk = js.split("function synaxarionDayRowHtml", 1)[1]
    chunk = chunk.split("function synaxarionEmptyTodayRowHtml", 1)[0]
    assert "synaxarion-stack" in chunk
    assert "rowspan=" not in chunk


def test_heiligen_sorteerknoppen() -> None:
    html = (
        ROOT / "site" / "layouts" / "partials" / "heiligen-overzicht.html"
    ).read_text(encoding="utf-8")
    assert "data-heiligen-sort" in html
    assert 'data-heiligen-sort="naam"' in html
    assert 'data-heiligen-sort="datum"' in html
    assert 'data-heiligen-selectie="kalender"' in html
    assert ">Opgenomen<" in html
    assert 'data-heiligen-weergave="kaart"' in html
    filt = (ROOT / "site" / "assets" / "js" / "entry-filter.js").read_text(
        encoding="utf-8"
    )
    assert "data-heiligen-sort" in filt


def test_teruggave_transfiguratie_bestaat() -> None:
    path = DATA / "teruggave-transfiguratie.yaml"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert 'waarde: "08-13"' in text
    nafeest = (DATA / "nafeest-transfiguratie.yaml").read_text(encoding="utf-8")
    assert "/feesten/teruggave-transfiguratie/" in nafeest


def test_agenda_heeft_vastenvrij_keuze() -> None:
    html = (ROOT / "site" / "layouts" / "_default" / "agenda.html").read_text(
        encoding="utf-8"
    )
    assert 'value="vastenvrij"' in html
    assert 'name="ics-heilige"' in html
    assert 'value="opgenomen"' in html
    assert 'value="nader"' in html
    assert 'value="kandidaat"' in html
    assert 'name="ics-feest"' in html
    assert 'name="ics-vasten"' in html
    js = JS.read_text(encoding="utf-8")
    assert "vastenvrij" in js
    assert "function icsFeedRelpaths" in js
    assert "function feedKey" in js
    assert "Kopieer de agenda-links" not in js
    assert "v2/" in js


def test_vierdatum_gelijk_tip() -> None:
    gen = (ROOT / "scripts" / "generate.py").read_text(encoding="utf-8")
    assert "vierdatum-gelijk" in gen
    assert "function to_short_month_label" in gen or "def to_short_month_label" in gen
    js = JS.read_text(encoding="utf-8")
    assert "vierdatum-gelijk" in js


def test_datumpagina_feesticoon_naast_dagtype() -> None:
    js = JS.read_text(encoding="utf-8")
    assert "function renderDagIcoonHtml" in js
    assert "function dagFeestIcoon" in js
    assert "today-dag-hoofd" in js
    assert "today-dag-icoon" in js
    render_today = js.split("function renderToday", 1)[1].split(
        "function isNarrowViewport", 1
    )[0]
    assert "renderDagIcoonHtml" in render_today
    assert "today-dag-hoofd" in render_today
    heiligen = js.split("function renderHeiligenHtml", 1)[1].split(
        "function renderToday", 1
    )[0]
    assert "today-heilige-icoon" in heiligen
    assert "today-dag-icoon" not in heiligen
    css = CSS.read_text(encoding="utf-8")
    assert ".today-dag-hoofd" in css
    assert ".today-dag-icoon-img" in css
    assert 'grid-template-areas:' in css.split(".today-dag-hoofd {", 1)[1][:400]


def test_jaarkalender_titel_heeft_agenda_popup() -> None:
    kal = (ROOT / "site" / "layouts" / "_default" / "kalender.html").read_text(
        encoding="utf-8"
    )
    assert 'data-info-tip="jaarkalender"' in kal
    js = JS.read_text(encoding="utf-8")
    assert 'kind === "jaarkalender"' in js
    assert 'assetUrl("agenda/")' in js
    assert 'meerUitlegHtml("jaarkalender")' in js
    assert "Kalender op telefoon of tablet" not in js


def test_overzicht_titels_hebben_pagina_popover() -> None:
    layouts = {
        "pagina-feesten": ROOT / "site" / "layouts" / "feesten" / "list.html",
        "pagina-vasten": ROOT / "site" / "layouts" / "vasten" / "list.html",
        "pagina-synaxarion": ROOT
        / "site"
        / "layouts"
        / "_default"
        / "synaxarion.html",
        "pagina-lezingenrooster": ROOT
        / "site"
        / "layouts"
        / "_default"
        / "lezingenrooster.html",
        "pagina-heiligen": ROOT
        / "site"
        / "layouts"
        / "partials"
        / "heiligen-overzicht.html",
        "pagina-agenda": ROOT / "site" / "layouts" / "_default" / "agenda.html",
    }
    js = JS.read_text(encoding="utf-8")
    uitleg = {
        "pagina-feesten": "feesten",
        "pagina-vasten": "vasten",
        "pagina-synaxarion": "synaxarion",
        "pagina-lezingenrooster": "lezingen",
        "pagina-heiligen": "heiligen",
        "pagina-agenda": "agenda",
    }
    for tip, path in layouts.items():
        html = path.read_text(encoding="utf-8")
        assert f'data-info-tip="{tip}"' in html, path.name
        assert f'kind === "{tip}"' in js
        assert f'meerUitlegHtml("{uitleg[tip]}")' in js
    assert "function setPaginaTitelTrigger" in js
    assert 'heading.textContent = "Synaxarion"' not in js


def test_statische_synaxarion_lijst_en_js_fallback() -> None:
    syn = (ROOT / "site" / "layouts" / "_default" / "synaxarion.html").read_text(
        encoding="utf-8"
    )
    assert 'partial "synaxarion-lijst.html"' in syn
    assert 'partial "entries-json.html"' in syn
    kal = (ROOT / "site" / "layouts" / "_default" / "kalender.html").read_text(
        encoding="utf-8"
    )
    assert "js-fallback" in kal
    assert "synaxarion/" in kal
    datum = (ROOT / "site" / "layouts" / "_default" / "datum.html").read_text(
        encoding="utf-8"
    )
    assert "js-fallback" in datum
    assert "Laden…" not in datum
    js = JS.read_text(encoding="utf-8")
    assert "kalender-entries-data" in js
    heiligen = (
        ROOT / "site" / "layouts" / "partials" / "heiligen-overzicht.html"
    ).read_text(encoding="utf-8")
    assert 'class="heiligen-row is-sort-naam"' in heiligen
