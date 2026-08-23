"""Fase 3: toon in de titel, lijsticonen, geen iconen in de jaarkalender-popover."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "site" / "assets" / "js" / "calendar.js"
HEILIGEN_OVERZICHT = ROOT / "site" / "layouts" / "partials" / "heiligen-overzicht.html"


def test_titel_toont_toon() -> None:
    js = JS.read_text(encoding="utf-8")
    assert "function octoechosToon" in js
    assert "function dayToonHtml" in js
    assert 'data-info-tip="toon"' in js
    assert "afterHtml: dayToonHtml" in js
    assert 'achtergrondUrl("toon")' in js
    title_html_start = js.index("function dayTitleHtml")
    title_html = js[title_html_start : js.index("function dayToonHtml")]
    assert "Toon" not in title_html
    assert "p.today" in title_html
    nav = js[js.index("function titleNavHtml") : js.index("function updateHeading")]
    assert "${opts.titleHtml}" in nav
    assert "(opts.afterHtml || \"\")" in nav
    assert nav.index("${opts.titleHtml}") < nav.index("›")


def test_lijsticonen_in_synaxarion_en_heiligenoverzicht() -> None:
    js = JS.read_text(encoding="utf-8")
    assert "class=\"list-icoon\"" in js or "class='list-icoon'" in js
    assert "synaxarion-table" in js
    assert "function synaxarionTableHtml" in js
    html = HEILIGEN_OVERZICHT.read_text(encoding="utf-8")
    assert "list-icoon" in (
        ROOT / "site" / "assets" / "js" / "entry-filter.js"
    ).read_text(encoding="utf-8")
    assert ".Params.icoon" in html
    assert "heiligen-data" in html


def test_rooster_en_synaxarion_hebben_weergave_paneel() -> None:
    rooster = (
        ROOT / "site" / "layouts" / "_default" / "lezingenrooster.html"
    ).read_text(encoding="utf-8")
    synaxarion = (
        ROOT / "site" / "layouts" / "_default" / "synaxarion.html"
    ).read_text(encoding="utf-8")
    assert "rooster-title-nav" not in rooster
    assert 'id="rooster-heading"' in rooster
    assert "weergave-trigger" in rooster
    assert "rooster-action-bar" in rooster
    assert "weergave-trigger" in synaxarion
    assert "synaxarion-action-bar" in synaxarion
    js = JS.read_text(encoding="utf-8")
    assert "function wireWeergavePanel" in js
    assert "function closeAllWeergavePanels" in js
    assert "rooster-title-nav" not in js


def test_jaarkalender_popover_zonder_iconen() -> None:
    js = JS.read_text(encoding="utf-8")
    start = js.index("function fillKalenderDagPopover")
    rest = js[start + 10 :]
    end = rest.index("\n  function ")
    body = rest[:end]
    assert "icoon" not in body
    assert "list-icoon" not in body


def test_bijbel_deeplink_in_calendar_js() -> None:
    js = JS.read_text(encoding="utf-8")
    assert "www.debijbel.nl/bijbel/" in js
    assert "class=\"bijbel-link\"" in js or "class='bijbel-link'" in js
    assert "bijbel-vertaling" in js
