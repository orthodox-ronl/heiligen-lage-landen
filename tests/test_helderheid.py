"""Fase 1: navigatie, uitleg, bronlaag, issue-templates."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate import CONTENT  # noqa: E402

SITE = ROOT / "site"
SCHEMA = ROOT / "schemas" / "entry.schema.json"
ISSUES = ROOT / ".github" / "ISSUE_TEMPLATE"


def test_nav_heeft_heiligen_en_uitleg() -> None:
    html = (SITE / "layouts" / "_default" / "baseof.html").read_text(encoding="utf-8")
    assert 'href="{{ "" | relURL }}">Heiligen</a>' in html
    assert ">Vandaag</a>" not in html
    assert ">Agenda</a>" not in html
    assert "Overzichten" in html
    assert 'href="{{ "feesten/" | relURL }}">Feesten</a>' in html
    assert 'href="{{ "vasten/" | relURL }}">Vasten</a>' in html
    assert 'aria-label="Hoofdnavigatie"' in html
    assert ">Uitleg</a>" in html
    assert ">Help</a>" not in html
    # relURL "kalender/" + canonifyURLs botst met Pages-base /kalender/
    assert 'href="{{ "kalender/" | absURL }}">Kalender</a>' in html
    assert 'href="{{ "kalender/" | relURL }}">Kalender</a>' not in html
    assert "brand-mark" in html
    assert "images/favicon-32x32.png" in html
    assert 'data-home=' in html
    heiligen_pos = html.find(">Heiligen</a>")
    dropdown_pos = html.find("<details")
    assert 0 <= heiligen_pos < dropdown_pos
    panel = html[html.find("<details") : html.find("</details>")]
    assert ">Heiligen</a>" not in panel
    assert ">Feesten</a>" in panel
    assert ">Vasten</a>" in panel
    assert ">Synaxarion</a>" in panel
    assert ">Lezingenrooster</a>" in panel
    before = html[:dropdown_pos]
    assert ">Synaxarion</a>" not in before
    assert ">Lezingenrooster</a>" not in before


def test_site_intro_popover_tekst() -> None:
    js = (SITE / "assets" / "js" / "calendar.js").read_text(encoding="utf-8")
    assert "site-intro-gezien" in js
    assert "van huis uit orthodox" in js
    assert "betekenis-goedkeuring" in js
    assert "maybeShowSiteIntro" in js
    assert "ontleend aan" in js
    assert 'kind === "vierdatum-oud"' in js
    assert "oude-kalenderparochies" in js
    assert "Oude kalender" in js
    assert "Over deze site" in js
    assert 'assetUrl("heiligen/")' in js


def test_homepage_is_heiligenoverzicht() -> None:
    home = (SITE / "layouts" / "index.html").read_text(encoding="utf-8")
    listing = (SITE / "layouts" / "heiligen" / "list.html").read_text(
        encoding="utf-8"
    )
    assert 'partial "heiligen-overzicht.html"' in home
    assert 'GetPage "/heiligen"' in home
    assert 'partial "heiligen-overzicht.html"' in listing
    nav = (SITE / "layouts" / "_default" / "baseof.html").read_text(
        encoding="utf-8"
    )
    assert 'href="{{ "" | relURL }}">Heiligen</a>' in nav
    assert 'href="{{ "datum/" | relURL }}">Vandaag</a>' not in nav
    js = (SITE / "assets" / "js" / "calendar.js").read_text(encoding="utf-8")
    assert 'pageUrl("datum/"' in js
    assert 'if (isToday) return pageUrl("", params);' not in js


def test_footer_heeft_reactie() -> None:
    html = (SITE / "layouts" / "partials" / "footer.html").read_text(encoding="utf-8")
    assert "uitleg/reactie/" in html


def test_schema_bronlaag_geen_stub() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    enum = schema["properties"]["bronlaag"]["enum"]
    assert set(enum) == {"nagekeken", "encyclopedie"}
    assert "status" not in schema["properties"]


def test_lege_dag_linkt_naar_uitleg_heiligen() -> None:
    js = (SITE / "assets" / "js" / "calendar.js").read_text(encoding="utf-8")
    assert "Waarom niet iedere heilige hier staat" in js
    assert "today-geen-heilige" in js
    assert 'achtergrondLink(' in js
    assert '"heiligen"' in js


def test_issue_templates_bestaan() -> None:
    names = {p.name for p in ISSUES.glob("*.yml")}
    assert "config.yml" in names
    assert "heilige-voorstellen.yml" in names
    assert "correctie.yml" in names
    assert "vraag.yml" in names
    vraag = (ISSUES / "vraag.yml").read_text(encoding="utf-8")
    assert "Uw vraag of opmerking" in vraag


def test_reactie_pagina_wijst_naar_email() -> None:
    hugo = (SITE / "hugo.toml").read_text(encoding="utf-8")
    text = (CONTENT / "uitleg" / "reactie.md").read_text(encoding="utf-8")
    form = (SITE / "layouts" / "shortcodes" / "reactie-form.html").read_text(
        encoding="utf-8"
    )
    assert 'feedback_email = "orthodoxronl@duck.com"' in hugo
    assert "reactie-form" in text
    assert "e-mail" in text.lower()
    assert "issues/new/choose" in text
    assert "data-email" in form
    assert "mailto:" in form
    assert 'value="anders"' in form
    assert "Iets anders" in form


def test_uitleg_heiligen_noemt_parochiepatronen() -> None:
    text = (CONTENT / "uitleg" / "heiligen.md").read_text(encoding="utf-8")
    hoofd = text.split("## Voor wie de site bijhoudt")[0]
    assert "Patroon van een parochie" in text
    assert "Nektarios" in text
    assert "bronlaag" not in hoofd
    assert "kaart" in hoofd
    assert "data/" not in hoofd


_LAYOUT_ACTION = re.compile(r"\{\{/\*.*?\*/\}\}|\{\{-?\s*(.*?)\s*-?\}\}", re.S)


def test_layouts_with_heeft_geen_else_if() -> None:
    """Go-templates: `with` ondersteunt geen `else if` (Hugo: unexpected <if>)."""
    errors: list[str] = []
    for path in (SITE / "layouts").rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        stack: list[str] = []
        for match in _LAYOUT_ACTION.finditer(text):
            if match.group(0).startswith("{{/*"):
                continue
            inner = (match.group(1) or "").strip()
            if not inner:
                continue
            first = inner.split()[0]
            if first in {"if", "with", "range", "block", "define"}:
                stack.append(first)
            elif first == "end":
                if stack:
                    stack.pop()
            elif first == "else":
                rest = inner[4:].lstrip()
                if rest.startswith("if") and stack and stack[-1] != "if":
                    rel = path.relative_to(SITE)
                    errors.append(f"{rel}: else if na {stack[-1]}")
    assert errors == []


def test_lijsten_tonen_vierdatum_oud_van_de_entry() -> None:
    default_list = (SITE / "layouts" / "_default" / "list.html").read_text(
        encoding="utf-8"
    )
    heiligen_list = (SITE / "layouts" / "partials" / "heiligen-overzicht.html").read_text(
        encoding="utf-8"
    )
    listing = (SITE / "layouts" / "heiligen" / "list.html").read_text(
        encoding="utf-8"
    )
    assert 'partial "heiligen-overzicht.html"' in listing
    assert "{{ if .Params.feestdatum }}" in default_list
    assert "Params.overzicht_sortering" in default_list
    assert "vierdatum-gelijk.html" in default_list
    assert "{{ else if and .Params.van .Params.tot }}" in default_list
    assert ".Params.vierdatum_oud" in default_list
    assert ".Params.van_oud" in default_list
    assert ".Params.tot_oud" in default_list
    assert "vierdatum-oud.html" in default_list
    assert "$.Params.vierdatum_oud" not in default_list
    assert "vierdatum_oud" in heiligen_list
    assert "heiligen-data" in heiligen_list
    filter_js = (SITE / "assets" / "js" / "entry-filter.js").read_text(
        encoding="utf-8"
    )
    assert "vierdatum_oud" in filter_js
    assert "vierdatum-oud" in filter_js
