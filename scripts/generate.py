"""Genereer Hugo-content, entries.json en ICS-feeds."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date, timedelta
from html import escape as html_escape
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from iconen import extra_iconen, icoon_bestand, primair_icoon  # noqa: E402
from load_entries import heilige_in_kalender, load_entries  # noqa: E402
from plaatsen import (  # noqa: E402
    load_plaatsen,
    locatie_namen,
    locatie_zoektekst,
)
from lezingen import (  # noqa: E402
    SPEC_PATH,
    build_lezingen_dagen_payload,
    spec_body_for_uitleg,
)
from vasten import (  # noqa: E402
    load_vastenregels,
    render_vasten_clerus,
    render_vasten_technisch,
)
from kalender import (  # noqa: E402
    format_mmdd,
    gregorian_to_julian_calendar,
    julian_feast_to_civil_date,
    mmdd_from_date,
    parse_mmdd,
    pascha_offset_date,
    weekday_relative_date,
)

SITE = ROOT / "site"
CONTENT = SITE / "content"
STATIC_DATA = SITE / "static" / "data"
STATIC_ICS = SITE / "static" / "ics"

# ICS / entries.json: huidig jaar −2 … +5 (niet de tabel op de entry-pagina).
ICS_YEAR_BACK = 2
ICS_YEAR_FORWARD = 5
# Body «Komende jaren»: huidig jaar en de vier daarop (vijf rijen).
KOMENDE_JAREN_AANTAL = 5

MONTH_NAMES_NL = [
    "",
    "januari",
    "februari",
    "maart",
    "april",
    "mei",
    "juni",
    "juli",
    "augustus",
    "september",
    "oktober",
    "november",
    "december",
]
MONTH_NAMES_SHORT = [
    "",
    "jan",
    "feb",
    "mrt",
    "apr",
    "mei",
    "jun",
    "jul",
    "aug",
    "sep",
    "okt",
    "nov",
    "dec",
]
_DATE_IN_PROSE = re.compile(
    r"\b(\d{1,2}) ("
    + "|".join(MONTH_NAMES_NL[1:])
    + r")\b(?! \d{3,})(?! \(\d)"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genereer site-content en ICS.")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Wis gegenereerde dag-/entry-mappen vóór genereren.",
    )
    return parser.parse_args()


def mmdd_label(mmdd: str) -> str:
    month, day = (int(x) for x in mmdd.split("-"))
    return f"{day} {MONTH_NAMES_NL[month]}"


def mmdd_label_short(mmdd: str) -> str:
    month, day = (int(x) for x in mmdd.split("-"))
    return f"{day} {MONTH_NAMES_SHORT[month]}"


def burgerlijk_label_short(d: date, *, jaar: int | None = None) -> str:
    label = f"{d.day} {MONTH_NAMES_SHORT[d.month]}"
    if jaar is not None and d.year != jaar:
        label += f" {d.year}"
    return label


def to_short_month_label(label: str) -> str:
    for i, name in enumerate(MONTH_NAMES_NL):
        if name and name in label:
            return label.replace(name, MONTH_NAMES_SHORT[i], 1)
    return label


def wrap_zelfde_vierdatum(inner_html: str) -> str:
    """Zelfde popover als ``zelfde_vierdatum_html``, zonder de inhoud te escapen."""
    return (
        f'<span class="vierdatum-gelijk" tabindex="0" '
        f'data-info-tip="vierdatum-gelijk" '
        f'title="Nieuw en oud op dezelfde burgerlijke dag">'
        f"{inner_html}</span>"
    )


def zelfde_vierdatum_html(inner: str) -> str:
    """Burgerlijke datum waarop nieuw en oud samenvallen; popover legt uit."""
    return wrap_zelfde_vierdatum(html_escape(inner))


def annotate_prose_dates(text: str) -> str:
    """Voeg oude-kalenderhaakjes toe bij liturgische datums in feest-/vastentekst."""

    def repl(match: re.Match[str]) -> str:
        day = int(match.group(1))
        month = MONTH_NAMES_NL.index(match.group(2))
        try:
            date(2001, month, day)
            mmdd = f"{month:02d}-{day:02d}"
            oud = julian_feast_to_civil_date(date.today().year, mmdd)
        except ValueError:
            return match.group(0)
        return f"{match.group(0)} {oud_vierdatum_html(burgerlijk_label_short(oud))}"

    return _DATE_IN_PROSE.sub(repl, text)


def occurrence_years(today: date | None = None) -> range:
    today = today or date.today()
    return range(today.year - ICS_YEAR_BACK, today.year + ICS_YEAR_FORWARD + 1)


def komende_jaren(today: date | None = None) -> range:
    """Vijf burgerlijke jaren: het lopende jaar en de vier daarop."""
    today = today or date.today()
    return range(today.year, today.year + KOMENDE_JAREN_AANTAL)


def burgerlijk_label(d: date, *, jaar: int | None = None) -> str:
    """Burgerlijke datum als '31 mei'; voeg het jaar toe als het van ``jaar`` verschilt."""
    label = f"{d.day} {MONTH_NAMES_NL[d.month]}"
    if jaar is not None and d.year != jaar:
        label += f" {d.year}"
    return label


def oud_vierdatum_html(inner: str) -> str:
    """Alleen de oude burgerlijke datum tussen haakjes; popover legt uit."""
    return (
        f'<span class="vierdatum-oud" tabindex="0" '
        f'data-info-tip="vierdatum-oud" '
        f'title="Datum op de oude kalender">'
        f"({html_escape(to_short_month_label(inner))})</span>"
    )


def cel_nieuw_met_oud(nieuw: str, oud: str | None) -> str:
    """Burgerlijke datum, plus haakjes met alleen de oude datum als die verschilt."""
    if not oud or oud == nieuw:
        return zelfde_vierdatum_html(nieuw)
    return f"{html_escape(nieuw)} {oud_vierdatum_html(oud)}"


def extra_toelichting_na_link(toel: str, feestdatum: str) -> str:
    """Toelichting na de datumlink, zonder herhaalde dagnaam."""
    toel = toel.strip()
    if not toel:
        return ""
    label = mmdd_label(feestdatum)
    if toel.casefold() == label.casefold():
        return ""
    if toel.casefold().startswith(label.casefold()):
        return toel[len(label) :].strip()
    return toel


KOMENDE_JAREN_KOP = "**Komende jaren (burgerlijk):**"


def komende_jaren_tabel_html(
    headers: list[str],
    rows: list[list[str]],
    *,
    raw_rows: bool = False,
) -> list[str]:
    """HTML-tabel voor de body; kolommen blijven onderling uitgelijnd.

    Zet raw_rows=True als cellen al veilige HTML (bijv. datumlinks) bevatten.
    """
    head = "".join(f"<th>{html_escape(h)}</th>" for h in headers)
    body_rows = []
    for row in rows:
        if raw_rows:
            cells = "".join(f"<td>{c}</td>" for c in row)
        else:
            cells = "".join(f"<td>{html_escape(c)}</td>" for c in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return [
        '<div class="table-wrap">',
        '<table class="komende-jaren">',
        f"<thead><tr>{head}</tr></thead>",
        "<tbody>",
        *body_rows,
        "</tbody>",
        "</table>",
        "</div>",
        "",
    ]


def datum_pagina_cell(
    label: str,
    civil: date,
    *,
    stijl: str | None = None,
) -> str:
    """HTML-cel: link naar datumpagina met optionele Nieuw/Oud-stijl."""
    q = f"/datum/?datum={civil.isoformat()}"
    if stijl == "juliaans":
        q += "&stijl=juliaans"
    elif stijl == "gregoriaans":
        q += "&stijl=gregoriaans"
    return f'<a href="{html_escape(q)}">{html_escape(label)}</a>'


def cel_nieuw_met_oud_link(
    nieuw_label: str,
    civil: date,
    oud_label: str | None = None,
    *,
    stijl: str | None = "gregoriaans",
) -> str:
    """Klikbare burgerlijke datum, plus haakjes met oude datum als die verschilt."""
    nieuw_html = datum_pagina_cell(nieuw_label, civil, stijl=stijl)
    if not oud_label or oud_label == nieuw_label:
        return wrap_zelfde_vierdatum(nieuw_html)
    return f"{nieuw_html} {oud_vierdatum_html(oud_label)}"


def _append_occ(bucket: dict[str, list[str]], d: date) -> None:
    """Voeg een burgerlijke dag toe; twee ankerjaren kunnen in één burgerjaar vallen."""
    key = str(d.year)
    mmdd = mmdd_from_date(d)
    days = bucket.setdefault(key, [])
    if mmdd not in days:
        days.append(mmdd)


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def append_icoon_front_matter(
    fm: list[str], entry: dict[str, Any], plaatsen: dict[str, Any]
) -> None:
    """Hugo: icoon = primair; iconen = overige zichtbare items."""
    prim = primair_icoon(entry)
    if not prim:
        return
    rel = icoon_bestand(prim)
    fm.append(f"icoon: {yaml_quote('/' + rel)}")
    bron = str(prim.get("bron") or "").strip()
    if bron:
        fm.append(f"icoon_bron: {yaml_quote(bron)}")
    licentie = str(prim.get("licentie") or "").strip()
    if licentie:
        fm.append(f"icoon_licentie: {yaml_quote(licentie)}")
    toelichting = str(prim.get("toelichting") or "").strip()
    if toelichting:
        fm.append(f"icoon_toelichting: {yaml_quote(toelichting)}")
    extras = extra_iconen(entry)
    if not extras:
        return
    fm.append("iconen:")
    for item in extras:
        fm.append(f"  - bestand: {yaml_quote('/' + icoon_bestand(item))}")
        for key in ("bron", "licentie", "soort", "toelichting"):
            val = str(item.get(key) or "").strip()
            if val:
                fm.append(f"    {key}: {yaml_quote(val)}")
        plaats_id = str(item.get("plaats") or "").strip()
        if plaats_id:
            rec = plaatsen.get(plaats_id) or {}
            naam = str(rec.get("naam") or plaats_id)
            fm.append(f"    plaats: {yaml_quote(naam)}")


def betekenis_bron_labels(entry: dict[str, Any]) -> list[str]:
    """Bronnen waar de betekenistekst op steunt (voorkeur: Orthodoxe geloof)."""
    faith: list[str] = []
    other: list[str] = []
    for ref in entry.get("referenties") or []:
        label = str(ref.get("label") or "").strip()
        if not label:
            continue
        url = str(ref.get("url") or "").lower()
        if "orthodoxe geloof" in label.lower() or "/the-orthodox-faith/" in url:
            faith.append(label)
        else:
            other.append(label)
    return faith or other


def betekenis_heading_html(entry: dict[str, Any]) -> str:
    """Kop Betekenis met popover over goedkeuring (of het ontbreken daarvan)."""
    items = entry.get("goedkeuring") or []
    payload = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    attr = html_escape(payload, quote=True)
    bronnen = json.dumps(
        betekenis_bron_labels(entry),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    bron_attr = html_escape(bronnen, quote=True)
    return (
        '<h2><span class="info-term" tabindex="0" '
        'data-info-tip="betekenis-goedkeuring" '
        f'data-goedkeuring="{attr}" '
        f'data-betekenis-bronnen="{bron_attr}" '
        'title="Over deze betekenistekst">Betekenis</span></h2>'
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


SOORT_DIR = {
    "feest": "feesten",
    "heilige": "heiligen",
    "vasten": "vasten",
}

BRONLAAG_NAGEKEKEN = (
    "> **Bron:** Deze tekst is nagekeken aan een lexikon, vita of "
    "vergelijkbare bron. Wikipedia en heiligen.net mogen aanvullen."
)
BRONLAAG_ENCYCLOPEDIE = (
    "> **Bron:** Deze tekst volgt open naslagwerken (Wikipedia, heiligen.net). "
    "Die worden door velen bijgehouden, maar zijn geen kerkelijke uitgave. "
    "Ze zijn dus niet getoetst aan bijvoorbeeld een lexikon of vita."
)


def bronlaag_van(entry: dict[str, Any]) -> str:
    laag = entry.get("bronlaag") or "encyclopedie"
    return laag if laag in {"nagekeken", "encyclopedie"} else "encyclopedie"


def bronlaag_note_md(entry: dict[str, Any]) -> str:
    if bronlaag_van(entry) == "nagekeken":
        return BRONLAAG_NAGEKEKEN
    return BRONLAAG_ENCYCLOPEDIE


def over_bronnen_md(entry: dict[str, Any]) -> str:
    """Sectie met optionele toelichting + bronlaag-noot."""
    delen: list[str] = ["## Over de bronnen", ""]
    extra = (entry.get("over_bronnen") or "").strip()
    if extra:
        delen.append(extra)
        delen.append("")
    delen.append(bronlaag_note_md(entry))
    delen.append("")
    return "\n".join(delen)

def selectie_note_md(entry: dict[str, Any]) -> str:
    """Uitklap bij nader-onderzoek / kandidaat-schrappen; niets bij voldoet."""
    if entry.get("soort") != "heilige":
        return ""
    sel = str(entry.get("selectie") or "nader-onderzoek").strip()
    if sel not in {"nader-onderzoek", "kandidaat-schrappen"}:
        return ""
    tekst = (
        (entry.get("selectie_toelichting_publiek") or "").strip()
        or (entry.get("selectie_toelichting") or "").strip()
    )
    if not tekst:
        return ""
    if sel == "kandidaat-schrappen":
        samenvatting = (
            "Deze heilige voldoet waarschijnlijk niet aan de criteria "
            "voor de Heiligen van de Lage Landen."
        )
    else:
        samenvatting = (
            "Of deze heilige bij de Heiligen van de Lage Landen hoort, "
            "is nog niet uitgemaakt. De kalender houdt de deur open; "
            "zulke grensgevallen zoeken we niet actief op."
        )
    return (
        '<details class="selectie-details">\n'
        "<summary>Plaats in deze kalender</summary>\n\n"
        f"{samenvatting}\n\n"
        f"{tekst}\n\n"
        "Meer over de criteria en hoe we met twijfel omgaan: "
        "[Heiligen van de Lage Landen](/uitleg/heiligen/).\n"
        "</details>\n"
    )


def entry_permalink(entry: dict[str, Any]) -> str:
    kind = SOORT_DIR[entry["soort"]]
    return f"/{kind}/{entry['id']}/"


def mmdd_in_inclusive_range(mmdd: str, van: str, tot: str) -> bool:
    """True als mmdd in [van, tot] ligt; ondersteunt jaarovergang (van > tot)."""
    if van <= tot:
        return van <= mmdd <= tot
    return mmdd >= van or mmdd <= tot


def iter_civil_days(start: date, end: date):
    """Inclusieve reeks kalenderdagen."""
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def render_refs_md(refs: list[dict[str, Any]]) -> str:
    if not refs:
        return "_Nog geen bronnen._\n"
    lines = []
    for ref in refs:
        label = ref.get("label") or "Bron"
        url = ref.get("url")
        geraadpleegd = ref.get("geraadpleegd")
        inhoud = (ref.get("inhoud") or "").strip()
        opmerking = (ref.get("opmerking") or "").strip()
        # Publiek: inhoud; anders fallback opmerking (oudere data).
        lezerstekst = inhoud or opmerking
        if url:
            line = f"- [{label}]({url})"
        elif ref.get("isbn"):
            pagina = ref.get("pagina")
            line = f"- {label} — ISBN {ref['isbn']}"
            if pagina:
                line += f", p. {pagina}"
        elif ref.get("locator"):
            line = f"- {label} — {ref['locator']}"
        else:
            line = f"- {label}"
        extras = []
        if geraadpleegd:
            extras.append(f"geraadpleegd {geraadpleegd}")
        if lezerstekst:
            extras.append(lezerstekst)
        if extras:
            line += f" — {'; '.join(extras)}"
        lines.append(line)
    return "\n".join(lines) + "\n"


def period_bounds_for_year(
    entry: dict[str, Any], year: int
) -> tuple[date, date] | None:
    """Start/eind (inclusief) van een periode in een burgerlijk jaar."""
    dn = entry["datum_norm"]
    vorm = dn.get("vorm") or "dag"
    if vorm == "periode" and dn.get("van") and dn.get("tot"):
        vm, vd = parse_mmdd(dn["van"])
        tm, td = parse_mmdd(dn["tot"])
        return date(year, vm, vd), date(year, tm, td)
    if entry.get("cyclus") == "paascyclus" and vorm == "periode":
        start = pascha_offset_date(year, dn["van_offset_dagen"])
        end = pascha_offset_date(year, dn["tot_offset_dagen"])
        if start > end:
            return None
        return start, end
    if entry.get("cyclus") == "paascyclus" and vorm == "periode_hybride":
        start = pascha_offset_date(year, dn["van_offset_dagen"])
        tm, td = parse_mmdd(dn["tot_mmdd"])
        end = date(year, tm, td)
        if start > end:
            return None
        return start, end
    return None


# Twaalf grote feesten plus Pascha (boven de twaalf). Voor /feesten/ «naar rang».
GROTE_FEESTEN = frozenset(
    {
        "pascha",
        "palmzondag",
        "hemelvaart",
        "pinksteren",
        "geboorte-moeder-gods",
        "kruisverheffing",
        "tempelgang-moeder-gods",
        "kerst",
        "theofanie",
        "ontmoeting-in-de-tempel",
        "aankondiging",
        "transfiguratie",
        "ontslapen-moeder-gods",
    }
)
HERR_EN_MOEDER_FEESTEN = frozenset({"besnijdenis-des-heren", "pokrov"})
APOSTEL_FEESTEN = frozenset(
    {
        "petrus-en-paulus",
        "geboorte-johannes-doper",
        "onthoofding-johannes-doper",
    }
)
OMLIJSTING_PREFIXEN = ("voorfeest-", "nafeest-", "teruggave-", "synaxis-")


def overzicht_sortering(entry: dict[str, Any]) -> str:
    """Sorteersleutel voor /feesten/ en /vasten/: kerkjaar, daarna paascyclus."""
    dn = entry.get("datum_norm") or {}
    vorm = dn.get("vorm") or "dag"
    eid = str(entry.get("id") or "")
    if entry.get("cyclus") == "wekelijks":
        return f"3-{eid}"
    if entry.get("cyclus") == "paascyclus":
        off = dn.get("paascyclus_offset")
        if off is None:
            off = dn.get("van_offset_dagen")
        if off is None:
            off = 999
        return f"2-{int(off) + 200:04d}-{eid}"
    mmdd = dn.get("feestdatum") or dn.get("van") or dn.get("anker")
    if mmdd and len(str(mmdd)) >= 5:
        m, d = int(str(mmdd)[:2]), int(str(mmdd)[3:5])
        kerk_m = (m - 9) % 12
        return f"1-{kerk_m:02d}-{d:02d}-{eid}"
    if vorm == "weekdagen":
        return f"3-{eid}"
    return f"9-{eid}"


def overzicht_rang(entry: dict[str, Any]) -> str:
    """Groep voor rangschikking «naar rang» op /feesten/."""
    eid = str(entry.get("id") or "")
    if eid in GROTE_FEESTEN:
        return "grote"
    if eid.startswith(OMLIJSTING_PREFIXEN):
        return "omlijsting"
    if eid in HERR_EN_MOEDER_FEESTEN:
        return "heer-moeder"
    if eid in APOSTEL_FEESTEN:
        return "apostelen"
    if entry.get("cyclus") == "paascyclus":
        return "paascyclus"
    return "overig"


def write_entry_page(entry: dict[str, Any]) -> None:
    kind = SOORT_DIR[entry["soort"]]
    title = entry["namen"]["primair"]
    dn = entry["datum_norm"]
    feestdatum = dn.get("feestdatum")
    vorm = dn.get("vorm") or "dag"
    fm = [
        "---",
        f"title: {yaml_quote(title)}",
        f"slug: {entry['id']}",
        f"type: {entry['soort']}",
        f"soort: {entry['soort']}",
        f"entry_id: {entry['id']}",
        f"cyclus: {entry.get('cyclus') or 'jaar'}",
        f"bronlaag: {bronlaag_van(entry)}",
        f"lage_landen: {'true' if entry.get('lage_landen') else 'false'}",
    ]
    if entry.get("soort") == "heilige":
        fm.append(
            f"selectie: {entry.get('selectie') or 'nader-onderzoek'}"
        )
    fm.extend(
        [
            f"source_path: {yaml_quote(entry['source_path'])}",
            f"overzicht_sortering: {yaml_quote(overzicht_sortering(entry))}",
        ]
    )
    if entry.get("soort") == "feest":
        fm.append(f"overzicht_rang: {overzicht_rang(entry)}")
    if feestdatum and vorm == "dag":
        fm.append(f"feestdatum: {feestdatum}")
        oud = julian_feast_to_civil_date(date.today().year, feestdatum)
        fm.append(f"vierdatum_oud: {mmdd_from_date(oud)}")
    if dn.get("van") and dn.get("tot"):
        fm.append(f"van: {dn['van']}")
        fm.append(f"tot: {dn['tot']}")
        jaar = date.today().year
        van_oud = julian_feast_to_civil_date(jaar, dn["van"])
        tot_oud = julian_feast_to_civil_date(jaar, dn["tot"])
        fm.append(f"van_oud: {mmdd_from_date(van_oud)}")
        fm.append(f"tot_oud: {mmdd_from_date(tot_oud)}")
    if dn.get("weekdagen"):
        fm.append("weekdagen:")
        for d in dn["weekdagen"]:
            fm.append(f"  - {d}")
    if vorm == "weekdag_relatief":
        fm.append(f"anker: {dn['anker']}")
        fm.append(f"weekdag: {dn['weekdag']}")
        fm.append(f"welke: {dn['welke']}")
        fm.append(f"richting: {dn['richting']}")
    if entry.get("cyclus") == "paascyclus":
        if dn.get("paascyclus_offset") is not None and vorm == "dag":
            fm.append(f"paascyclus_offset: {dn['paascyclus_offset']}")
        if dn.get("van_offset_dagen") is not None:
            fm.append(f"van_offset_dagen: {dn['van_offset_dagen']}")
        if dn.get("tot_offset_dagen") is not None:
            fm.append(f"tot_offset_dagen: {dn['tot_offset_dagen']}")
        if dn.get("tot_mmdd"):
            fm.append(f"tot: {dn['tot_mmdd']}")
            tot_oud = julian_feast_to_civil_date(date.today().year, dn["tot_mmdd"])
            fm.append(f"tot_oud: {mmdd_from_date(tot_oud)}")
    if entry.get("titels"):
        fm.append("titels:")
        for t in entry["titels"]:
            fm.append(f"  - {yaml_quote(t)}")
    alts = (entry.get("namen") or {}).get("alternatief") or []
    if alts:
        fm.append("alternatief:")
        for a in alts:
            fm.append(f"  - {yaml_quote(a)}")
    loc_ids = list(entry.get("locaties") or [])
    plaatsen = load_plaatsen()
    if loc_ids:
        namen = locatie_namen(loc_ids, plaatsen)
        fm.append("locaties:")
        for naam in namen:
            fm.append(f"  - {yaml_quote(naam)}")
        fm.append("locatie_ids:")
        for pid in loc_ids:
            fm.append(f"  - {pid}")
        fm.append("locatie_items:")
        for pid in loc_ids:
            rec = plaatsen.get(pid) or {}
            naam = rec.get("naam") or pid
            soort = rec.get("soort") or "plaats"
            fm.append(f"  - id: {pid}")
            fm.append(f"    naam: {yaml_quote(naam)}")
            fm.append(f"    soort: {soort}")
        zoek = locatie_zoektekst(loc_ids, plaatsen)
        if zoek:
            fm.append(f"locatie_zoek: {yaml_quote(zoek)}")
    rust = entry.get("rustplaats")
    if rust and rust.get("plaats"):
        rp_naam = locatie_namen([rust["plaats"]], plaatsen)[0]
        fm.append(f"rustplaats_plaats: {yaml_quote(rp_naam)}")
        if rust.get("toelichting"):
            fm.append(f"rustplaats_toelichting: {yaml_quote(rust['toelichting'])}")
    if entry.get("periode"):
        fm.append(f"periode: {yaml_quote(str(entry['periode']).strip())}")
    if entry.get("vastenniveau"):
        fm.append(f"vastenniveau: {entry['vastenniveau']}")
    if entry.get("onderdrukt_wekelijks_vasten"):
        fm.append("onderdrukt_wekelijks_vasten: true")
    append_icoon_front_matter(fm, entry, plaatsen)
    aliases = entry.get("id_aliassen") or []
    if aliases:
        fm.append("aliases:")
        for alias in aliases:
            slug = str(alias).strip().strip("/")
            fm.append(f"  - {yaml_quote(f'/{kind}/{slug}/')}")
    fm.append("---")

    body: list[str] = []

    # Kerngegevens (titel, datum, plaatsen, icoon, …) staan in de Hugo-infobox.
    # Hier alleen toelichting die niet compact in de box past (jaarlijsten e.d.).
    if entry.get("cyclus") == "paascyclus" and vorm in {"periode", "periode_hybride"}:
        van_o = dn["van_offset_dagen"]
        hybride = vorm == "periode_hybride"
        body.append(KOMENDE_JAREN_KOP)
        body.append("")
        rows: list[list[str]] = []
        for y in komende_jaren():
            start = pascha_offset_date(y, van_o)
            if hybride:
                end = date(y, *parse_mmdd(dn["tot_mmdd"]))
                end_oud = julian_feast_to_civil_date(y, dn["tot_mmdd"])
            else:
                end = pascha_offset_date(y, dn["tot_offset_dagen"])
                end_oud = None
            van_l = datum_pagina_cell(
                burgerlijk_label(start, jaar=y), start, stijl="gregoriaans"
            )
            if start > end:
                if hybride and start <= end_oud:
                    tot_l = cel_nieuw_met_oud(
                        "geen dagen",
                        burgerlijk_label(end_oud, jaar=y),
                    )
                else:
                    tot_l = html_escape("geen dagen")
            else:
                tot_l = cel_nieuw_met_oud_link(
                    burgerlijk_label(end, jaar=y),
                    end,
                    burgerlijk_label(end_oud, jaar=y) if end_oud else None,
                    stijl="gregoriaans",
                )
            rows.append([html_escape(str(y)), van_l, tot_l])
        body.extend(
            komende_jaren_tabel_html(
                ["Jaar", "Van", "Tot"],
                rows,
                raw_rows=True,
            )
        )
    elif entry.get("cyclus") == "paascyclus":
        offset = dn["paascyclus_offset"]
        body.append(KOMENDE_JAREN_KOP)
        body.append("")
        rows = []
        for y in komende_jaren():
            d = pascha_offset_date(y, offset)
            rows.append(
                [
                    html_escape(str(y)),
                    datum_pagina_cell(
                        burgerlijk_label(d, jaar=y), d, stijl="gregoriaans"
                    ),
                ]
            )
        body.extend(
            komende_jaren_tabel_html(["Jaar", "Datum"], rows, raw_rows=True)
        )
    elif vorm == "weekdag_relatief":
        body.append(
            "Geen vaste feestdatum; hangt af van de weekdag van het anker."
        )
        body.append("")
        body.append(KOMENDE_JAREN_KOP)
        body.append("")
        rows = []
        for y in komende_jaren():
            d_nieuw = weekday_relative_date(
                y,
                dn["anker"],
                dn["weekdag"],
                dn["welke"],
                dn["richting"],
                stijl="nieuw",
            )
            d_oud = weekday_relative_date(
                y,
                dn["anker"],
                dn["weekdag"],
                dn["welke"],
                dn["richting"],
                stijl="oud",
            )
            rows.append(
                [
                    html_escape(str(y)),
                    cel_nieuw_met_oud_link(
                        burgerlijk_label(d_nieuw, jaar=y),
                        d_nieuw,
                        burgerlijk_label(d_oud, jaar=y),
                        stijl="gregoriaans",
                    ),
                ]
            )
        body.extend(
            komende_jaren_tabel_html(
                ["Jaar", "Datum"],
                rows,
                raw_rows=True,
            )
        )
    elif vorm == "dag" and feestdatum:
        oud = julian_feast_to_civil_date(date.today().year, feestdatum)
        body.append(
            f"**Feestdag:** [{mmdd_label(feestdatum)}](/datum/?dag={feestdatum}) "
            f"{oud_vierdatum_html(burgerlijk_label_short(oud))}"
        )
        body.append("")
        if dn.get("gregoriaans") or dn.get("juliaans"):
            parts = []
            if dn.get("gregoriaans"):
                parts.append(f"Gregoriaans {mmdd_label(dn['gregoriaans'])}")
            if dn.get("juliaans"):
                parts.append(f"Juliaans {mmdd_label(dn['juliaans'])}")
            body.append("**Expliciete notatie:** " + "; ".join(parts))
            body.append("")
        extras = entry.get("datum_extra_norm") or []
        extra_lines = []
        for extra in extras:
            fd = extra.get("feestdatum")
            if not fd:
                continue
            toel = (extra.get("toelichting") or "").strip()
            link = f"[{mmdd_label(fd)}](/datum/?dag={fd})"
            oud_ex = julian_feast_to_civil_date(date.today().year, fd)
            haak = oud_vierdatum_html(burgerlijk_label(oud_ex))
            suffix = extra_toelichting_na_link(toel, fd)
            line = f"- {link} {haak}"
            if suffix:
                line += f" — {suffix}"
            extra_lines.append(line)
        if extra_lines:
            body.append("**Andere gedenkdagen:**")
            body.append("")
            body.extend(extra_lines)
            body.append("")
    betekenis = (entry.get("betekenis_lage_landen") or "").strip()
    if betekenis:
        body.append("## Betekenis voor de Lage Landen")
        body.append("")
        body.append(annotate_prose_dates(betekenis) if entry.get("soort") in {"feest", "vasten"} else betekenis)
        body.append("")
    if entry.get("soort") != "heilige" and entry.get("samenvatting"):
        samenvatting = entry["samenvatting"].strip()
        if entry.get("soort") in {"feest", "vasten"}:
            samenvatting = annotate_prose_dates(samenvatting)
        body.append(samenvatting)
        body.append("")
    if entry.get("verhaal"):
        body.append("## Verhaal")
        body.append("")
        verhaal = entry["verhaal"].strip()
        if entry.get("soort") in {"feest", "vasten"}:
            verhaal = annotate_prose_dates(verhaal)
        body.append(verhaal)
        body.append("")
    if entry.get("soort") == "feest":
        betekenis_feest = (entry.get("betekenis") or "").strip()
        if betekenis_feest:
            body.append(betekenis_heading_html(entry))
            body.append("")
            body.append(betekenis_feest)
            body.append("")
    body.append("## Verder lezen en kijken")
    body.append("")
    body.append(render_refs_md(entry.get("referenties") or []))
    body.append("")
    body.append(over_bronnen_md(entry))
    selectie_blok = selectie_note_md(entry)
    if selectie_blok:
        body.append(selectie_blok)
        body.append("")
    write_text(CONTENT / kind / f"{entry['id']}.md", "\n".join(fm + ["", *body]))


VOORBEELD_HEILIGEN = (
    "willibrord",
    "servatius",
    "gertrudis",
    "johannes-van-shanghai",
)

ZONDAG_HEILIGEN_LL = "zondag-heiligen-lage-landen"
ZONDAG_HEILIGEN_LL_OFFSET = 63  # tweede zondag na Pinksteren


def eerstvolgende_paascyclus_dag(offset: int, today: date | None = None) -> date:
    """Eerstvolgende burgerlijke dag van een paascyclus-offset (vandaag telt mee)."""
    today = today or date.today()
    dit = pascha_offset_date(today.year, offset)
    if dit >= today:
        return dit
    return pascha_offset_date(today.year + 1, offset)


def _zondag_ll_overzicht_zin(
    entries: list[dict[str, Any]],
    today: date | None = None,
) -> str:
    """Zin met link naar de datumpagina van de Zondag van de heiligen van de Lage Landen."""
    feest = next((e for e in entries if e.get("id") == ZONDAG_HEILIGEN_LL), None)
    offset = ZONDAG_HEILIGEN_LL_OFFSET
    naam = "Zondag van de heiligen van de Lage Landen"
    if feest:
        dn = feest.get("datum_norm") or {}
        if "paascyclus_offset" in dn:
            offset = int(dn["paascyclus_offset"])
        naam = (feest.get("namen") or {}).get("primair") or naam
    dag = eerstvolgende_paascyclus_dag(offset, today)
    href = f"/datum/?datum={dag.isoformat()}"
    wanneer = f"{dag.day} {MONTH_NAMES_NL[dag.month]} {dag.year}"
    return (
        f"De lokale Kerk gedenkt deze heiligen op de "
        f'<a href="{html_escape(href)}">{html_escape(naam)}</a>'
        f" ({html_escape(wanneer)})."
    )


def _nl_en_lijst(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} en {items[1]}"
    return ", ".join(items[:-1]) + f" en {items[-1]}"


def write_generated_indexes(
    entries: list[dict[str, Any]] | None = None,
    *,
    today: date | None = None,
) -> None:
    """Sectie-indexes die bij --clean opnieuw worden aangemaakt."""
    entries = list(entries or [])
    heiligen = [e for e in entries if e.get("soort") == "heilige"]
    n_nader = sum(1 for e in heiligen if e.get("selectie") == "nader-onderzoek")
    n_kand = sum(1 for e in heiligen if e.get("selectie") == "kandidaat-schrappen")
    by_id = {e["id"]: e for e in heiligen if heilige_in_kalender(e)}
    voorbeelden: list[str] = []
    for hid in VOORBEELD_HEILIGEN:
        entry = by_id.get(hid)
        if entry is None:
            continue
        naam = entry["namen"]["primair"]
        voorbeelden.append(f"[{naam}]({entry_permalink(entry)})")
    delen = [
        "---",
        'title: "Heiligen van de Lage Landen"',
        "---",
        "",
        '<details class="heiligen-over-lijst">',
        "<summary>Over deze lijst</summary>",
        "",
        "Deze lijst verzamelt heiligen die bij de Lage Landen horen. "
        "Wie vóór het schisma hier predikte, een kerk of klooster stichtte, "
        "of hier leed, hoort erin. Wie na het schisma de Orthodoxie in "
        "Nederland of België heeft helpen opbouwen, hoort er eveneens in. "
        "Niet iedere "
        "heilige van de Kerk staat hier: de patroon van een parochie is "
        "daarvoor niet genoeg. "
        "[Wie erin hoort](/uitleg/heiligen/).",
        "",
    ]
    if n_nader:
        if n_nader == 1:
            delen.append(
                "Er staat **1** naam in **nader onderzoek**. Die blijft in de "
                "kalender tot er een besluit is."
            )
        else:
            delen.append(
                f"Er staan **{n_nader}** namen in **nader onderzoek**. Die "
                "blijven in de kalender tot er een besluit is."
            )
        delen.append("")
    if n_kand:
        if n_kand == 1:
            delen.append(
                "Er staat **1** **kandidaat**. Die hoort waarschijnlijk niet "
                "in de kalender. U ziet die naam alleen als u alle namen "
                "toont. Die naam staat niet op de datumpagina, in het "
                "Synaxarion of in de agenda."
            )
        else:
            delen.append(
                f"Er staan **{n_kand}** **kandidaten**. Die horen "
                "waarschijnlijk niet in de kalender. U ziet ze alleen als u "
                "alle namen toont. Ze staan niet op de datumpagina, in het "
                "Synaxarion of in de agenda."
            )
        delen.append("")
    zondag_zin = _zondag_ll_overzicht_zin(entries, today)
    if zondag_zin:
        delen.extend([zondag_zin, ""])
    if voorbeelden:
        delen.extend(
            [
                f"Enkele bekende namen in deze lijst zijn {_nl_en_lijst(voorbeelden)}.",
                "",
            ]
        )
    delen.extend(
        [
            "U kunt zoeken op naam — ook op een andere naam van dezelfde "
            "heilige — of op plaats, bijvoorbeeld Utrecht, Vlaanderen of "
            "Friesland. De kaart toont die plaatsen. Streken staan cursief, "
            "zodat u ze van steden en dorpen kunt onderscheiden.",
            "",
            "</details>",
            "",
        ]
    )
    write_text(CONTENT / "heiligen" / "_index.md", "\n".join(delen))
    write_text(
        CONTENT / "feesten" / "_index.md",
        """---
title: "Vaste feesten"
---

Grote vaste feesten van de jaarcyclus en de paascyclus.
Standaard in het
<span class="info-term" tabindex="0" data-info-tip="kerkelijk-jaar" title="Van september tot augustus">kerkelijk jaar</span>,
zoals de loop van een synaxarion. Andere volgordes kiest u bij
<span class="info-term" tabindex="0" data-info-tip="feesten-rangschikking" title="Andere volgordes, zoals de registers van een synaxarion">Rangschikking</span>.
""",
    )
    write_text(
        CONTENT / "vasten" / "_index.md",
        """---
title: "Vasten"
---

Vastenperiodes en wekelijkse vastendagen.
""",
    )


SELECTIE_GROEPEN = (
    ("voldoet", "Voldoet"),
    ("nader-onderzoek", "Nader onderzoek"),
    ("kandidaat-schrappen", "Kandidaat om te schrappen"),
)


def render_beheer_selectie(entries: list[dict[str, Any]]) -> str:
    """Markdown-body: heiligen gegroepeerd op selectie (niet publiek)."""
    heiligen = [e for e in entries if e.get("soort") == "heilige"]
    by_sel: dict[str, list[dict[str, Any]]] = {key: [] for key, _title in SELECTIE_GROEPEN}
    for entry in heiligen:
        sel = entry.get("selectie") or "nader-onderzoek"
        by_sel.setdefault(sel, []).append(entry)
    for groep in by_sel.values():
        groep.sort(key=lambda e: (e["namen"]["primair"].casefold(), e["id"]))

    lines = [
        "Gegenereerd uit `selectie` op heiligen-YAML. Niet bedoeld voor bezoekers.",
        "Wijzig het veld in `data/heiligen/`; deze pagina niet redigeren.",
        "",
        f"**{len(heiligen)}** heiligen.",
        "",
    ]
    for key, title in SELECTIE_GROEPEN:
        groep = by_sel.get(key) or []
        lines.append(f"## {title} ({len(groep)})")
        lines.append("")
        if not groep:
            lines.append("_Geen._")
            lines.append("")
            continue
        for entry in groep:
            naam = entry["namen"]["primair"]
            url = entry_permalink(entry)
            src = entry["source_path"]
            item = f"- [{naam}]({url}) (`{src}`)"
            toel = (entry.get("selectie_toelichting") or "").strip()
            if toel:
                item += f" — {toel}"
            lines.append(item)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_beheer_selectie(entries: list[dict[str, Any]]) -> None:
    write_text(
        CONTENT / "beheer" / "selectie.md",
        _dump_hugo_markdown(
            {
                "title": "Selectie heiligen",
                "description": (
                    "Toetsing aan de opnamecriteria; alleen voor wie de repo bijhoudt"
                ),
                "weight": 90,
                "generator": "scripts/generate.py",
            },
            render_beheer_selectie(entries),
        ),
    )


def _split_hugo_markdown(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n") and text != "---":
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        raise ValueError("front matter zonder afsluitende ---")
    fm_raw = text[4:end]
    body = text[end + 4 :]
    if body.startswith("\n"):
        body = body[1:]
    meta = yaml.safe_load(fm_raw) or {}
    if not isinstance(meta, dict):
        raise ValueError("front matter moet een mapping zijn")
    return meta, body


def _dump_hugo_markdown(meta: dict[str, Any], body: str) -> str:
    # Stabiele, leesbare YAML (title eerst, dan layout, dan rest).
    ordered: dict[str, Any] = {}
    if "title" in meta:
        ordered["title"] = meta["title"]
    if "layout" in meta:
        ordered["layout"] = meta["layout"]
    for key, value in meta.items():
        if key in ordered:
            continue
        ordered[key] = value
    dumped = yaml.safe_dump(
        ordered,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).strip()
    body = body if body.endswith("\n") or body == "" else body + "\n"
    body = body.lstrip("\n")
    return f"---\n{dumped}\n---\n\n{body}"


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def ensure_hand_owned_indexes() -> None:
    """Handmatige sectiepagina's: bestaan, niet-lege title, juiste layout.

    Overschrijft geen body en raakt andere front matter niet aan, behalve
    het corrigeren van `layout` als die ontbreekt of afwijkt.
    """
    specs = [
        {
            "path": CONTENT / "_index.md",
            "title": "Heiligen van de Lage Landen",
            "layout": None,
        },
        {
            "path": CONTENT / "kalender" / "_index.md",
            "title": "Jaarkalender",
            "layout": "kalender",
        },
        {
            "path": CONTENT / "synaxarion" / "_index.md",
            "title": "Synaxarion",
            "layout": "synaxarion",
        },
        {
            "path": CONTENT / "datum" / "_index.md",
            "title": "Datum",
            "layout": "datum",
        },
        {
            "path": CONTENT / "agenda" / "_index.md",
            "title": "Agenda",
            "layout": "agenda",
        },
        {
            "path": CONTENT / "uitleg" / "_index.md",
            "title": "Uitleg",
            "layout": None,
        },
        {
            "path": CONTENT / "beheer" / "_index.md",
            "title": "Voor beheerders",
            "layout": None,
        },
    ]

    for spec in specs:
        path: Path = spec["path"]
        default_title: str = spec["title"]
        expected_layout = spec["layout"]
        if not path.exists():
            meta: dict[str, Any] = {"title": default_title}
            if expected_layout:
                meta["layout"] = expected_layout
            write_text(path, _dump_hugo_markdown(meta, ""))
            print(f"Aangemaakt: {_rel(path)}")
            continue
        try:
            meta, body = _split_hugo_markdown(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise SystemExit(f"{_rel(path)}: {exc}") from exc
        title = meta.get("title")
        if not isinstance(title, str) or not title.strip():
            raise SystemExit(
                f"{_rel(path)}: front matter 'title' ontbreekt of is leeg"
            )
        changed = False
        if expected_layout is not None and meta.get("layout") != expected_layout:
            meta["layout"] = expected_layout
            changed = True
        if expected_layout is None and meta.get("layout") == "uitleg":
            # Legacy: oude monolithische uitleg-layout verwijderen.
            del meta["layout"]
            changed = True
        if changed:
            write_text(path, _dump_hugo_markdown(meta, body))
            print(f"Front matter bijgewerkt: {_rel(path)}")


# Onderwerpen onder site/content/uitleg/<id>.md — handmatig, stabiele ids.
ACHTERGROND_TOPICS: list[dict[str, str]] = [
    {
        "id": "nieuw-oud",
        "title": "Nieuwe en Oude kalender",
        "description": "Welke kalender uw parochie volgt, en wat de knop Nieuw/Oud doet",
    },
    {
        "id": "feestdatum",
        "title": "Feestdatum",
        "description": "De naam van een feestdag in het kerkelijk jaar, in nieuw en oud dezelfde",
    },
    {
        "id": "datumpagina",
        "title": "Datumpagina’s",
        "description": "Wat er op één burgerlijke dag in een bepaald jaar valt",
    },
    {
        "id": "synaxarion",
        "title": "Synaxarion",
        "description": "De vaste jaarcyclus: heiligen en feesten die altijd op een kalenderdag horen",
    },
    {
        "id": "feesten",
        "title": "Overzicht van feesten",
        "description": "Hoe de lijst van vaste feesten is gerangschikt, en hoe u een andere volgorde kiest",
    },
    {
        "id": "heiligen",
        "title": "Heiligen van de Lage Landen",
        "description": "Wie in deze kalender staat, hoe stevig de tekst is, en waarom een dag zonder heilige kan",
    },
    {
        "id": "kleuren",
        "title": "Kleuren in de jaarkalender",
        "description": "Wat de kleuren op de jaarkalender betekenen",
    },
    {
        "id": "vasten",
        "title": "Vasten",
        "description": "Waar onze vastenregels vandaan komen, en wat de kalender toont",
    },
    {
        "id": "agenda",
        "title": "Agenda",
        "description": "De kerkelijke kalender op uw telefoon of computer: kiezen, downloaden of abonneren",
    },
    {
        "id": "lezingen",
        "title": "Lezingen van de dag",
        "description": (
            "Apostel en Evangelie volgens Moskou (ROCOR bij twijfel) — "
            "uitleg voor de clerus"
        ),
    },
    {
        "id": "toon",
        "title": "Toon van de week",
        "description": "De acht wekelijkse zangtonen, gerekend vanaf Thomaszondag",
    },
]


def ensure_achtergrond_topics() -> None:
    """Zorg dat bekende uitleg-onderwerpen bestaan met niet-lege title.

    Body en overige front matter blijven onaangeroerd. Ontbrekende bestanden
    krijgen een korte stub. Uitzondering: bij ``lezingen`` wordt alleen de
    *technische* spiegel bijgewerkt; de clerus-pagina blijft handmatig.
    """
    uitleg_dir = CONTENT / "uitleg"
    uitleg_dir.mkdir(parents=True, exist_ok=True)
    for topic in ACHTERGROND_TOPICS:
        path = uitleg_dir / f"{topic['id']}.md"
        if topic["id"] == "lezingen":
            sync_lezingen_uitleg()
            # Valideer clerus-front matter (sync schrijft die niet).
            try:
                meta, _body = _split_hugo_markdown(path.read_text(encoding="utf-8"))
            except ValueError as exc:
                raise SystemExit(f"{_rel(path)}: {exc}") from exc
            title = meta.get("title")
            if not isinstance(title, str) or not title.strip():
                raise SystemExit(
                    f"{_rel(path)}: front matter 'title' ontbreekt of is leeg"
                )
            continue
        if not path.exists():
            meta = {
                "title": topic["title"],
                "description": topic["description"],
            }
            body = (
                f"_{topic['description']}_\n\n"
                "(Tekst nog toe te voegen.)\n"
            )
            write_text(path, _dump_hugo_markdown(meta, body))
            print(f"Aangemaakt: {_rel(path)}")
            continue
        try:
            meta, _body = _split_hugo_markdown(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise SystemExit(f"{_rel(path)}: {exc}") from exc
        title = meta.get("title")
        if not isinstance(title, str) or not title.strip():
            raise SystemExit(
                f"{_rel(path)}: front matter 'title' ontbreekt of is leeg"
            )


def write_vasten_uitleg() -> None:
    """Genereer clerus- en technische vastenpagina uit data/regels/vasten.yaml."""
    regels = load_vastenregels()
    write_text(
        CONTENT / "uitleg" / "vasten.md",
        _dump_hugo_markdown(
            {
                "title": regels["titel"],
                "description": regels["beschrijving"],
                "generator": "data/regels/vasten.yaml",
                "uitleg_stijl": "vasten",
            },
            render_vasten_clerus(regels),
        ),
    )
    tech = regels.get("technisch") or {}
    write_text(
        CONTENT / "uitleg" / "vasten-technisch.md",
        _dump_hugo_markdown(
            {
                "title": tech.get("titel") or "Vasten (technisch)",
                "description": tech.get("beschrijving") or "",
                "generator": "data/regels/vasten.yaml",
                "uitleg_stijl": "vasten-technisch",
                "build": {"list": "never", "render": "always"},
            },
            render_vasten_technisch(regels),
        ),
    )


def sync_lezingen_uitleg() -> None:
    """Schrijf technische uitleg; raak de clerus-pagina niet over.

    - ``uitleg/lezingen.md`` — handmatig (clerus); staat in de inhoudsopgave.
    - ``uitleg/lezingen-technisch.md`` — spiegel van ``docs/specs/lezingen.md``;
      verborgen in de Uitleg-index (``build.list: never``), wel bereikbaar
      via link vanaf de clerus-pagina.
    """
    if not SPEC_PATH.is_file():
        raise SystemExit(f"Ontbreekt: {SPEC_PATH.relative_to(ROOT)}")

    clerus = CONTENT / "uitleg" / "lezingen.md"
    if not clerus.is_file():
        stub_meta = {
            "title": "Lezingen van de dag",
            "description": (
                "Apostel en Evangelie volgens Moskou (ROCOR bij twijfel) — "
                "uitleg voor de clerus"
            ),
        }
        stub_body = (
            "Uitleg voor de clerus (handmatige tekst).\n\n"
            "Technische specificatie: "
            "[Lezingen technisch]({{% ref \"/uitleg/lezingen-technisch\" %}}).\n"
        )
        write_text(clerus, _dump_hugo_markdown(stub_meta, stub_body))
        print(f"Aangemaakt: {_rel(clerus)}")

    tech_path = CONTENT / "uitleg" / "lezingen-technisch.md"
    meta = {
        "title": "Lezingen van de dag (technisch)",
        "description": (
            "Normatieve specificatie: regels, bestanden en implementatiestatus"
        ),
        "build": {"list": "never", "render": "always"},
        "uitleg_stijl": "lezingen-technisch",
    }
    intro = (
        "Deze pagina is de **technische spiegel** van "
        "`docs/specs/lezingen.md`. Wijzig die specificatie (regels + voorbeelden); "
        "daarna moet `scripts/lezingen.py` meekomen — pytest bewaakt dat.\n\n"
        "Voor overleg met de clerus: "
        "[Lezingen van de dag]({{% ref \"/uitleg/lezingen\" %}}).\n\n"
        "---\n\n"
    )
    body = intro + spec_body_for_uitleg()
    write_text(tech_path, _dump_hugo_markdown(meta, body))


def write_plaatsen_json() -> None:
    payload = list(load_plaatsen().values())
    write_text(
        STATIC_DATA / "plaatsen.json",
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    )


def write_lezingen_json() -> dict[str, Any]:
    """Precompute feestoverride-lezingen voor ICS-jaarvenster (nieuw + oud)."""
    years = list(occurrence_years())
    payload = build_lezingen_dagen_payload(years)
    write_text(
        STATIC_DATA / "lezingen-dagen.json",
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    )
    return payload


def write_entries_json(entries: list[dict[str, Any]]) -> None:
    years = list(occurrence_years())
    payload = []
    for entry in entries:
        if not heilige_in_kalender(entry):
            continue
        dn = entry["datum_norm"]
        vorm = dn.get("vorm") or "dag"
        item: dict[str, Any] = {
            "id": entry["id"],
            "soort": entry["soort"],
            "cyclus": entry.get("cyclus") or "jaar",
            "vorm": vorm,
            "naam": entry["namen"]["primair"],
            "alternatief": entry["namen"].get("alternatief") or [],
            "titels": entry.get("titels") or [],
            "samenvatting": (entry.get("samenvatting") or "").strip(),
            "url": entry_permalink(entry),
            "lage_landen": bool(entry.get("lage_landen")),
            "bronlaag": bronlaag_van(entry),
            "observances": entry.get("observances") or [],
            "onderdrukt_wekelijks_vasten": bool(
                entry.get("onderdrukt_wekelijks_vasten")
            ),
            "icoon": icoon_bestand(primair_icoon(entry)) or None,
        }
        if entry.get("soort") == "heilige":
            item["betekenis_lage_landen"] = (
                (entry.get("betekenis_lage_landen") or "").strip()
            )
            loc_ids = list(entry.get("locaties") or [])
            item["locaties"] = loc_ids
            rust = entry.get("rustplaats")
            if rust and rust.get("plaats"):
                item["rustplaats"] = {
                    "plaats": rust["plaats"],
                    "toelichting": rust.get("toelichting") or "",
                }
        if entry.get("vastenniveau"):
            item["vastenniveau"] = entry["vastenniveau"]
        if vorm == "weekdagen":
            item["weekdagen"] = list(dn["weekdagen"])
            item["feestdatum"] = None
        elif vorm == "weekdag_relatief":
            item["anker"] = dn["anker"]
            item["weekdag"] = dn["weekdag"]
            item["welke"] = dn["welke"]
            item["richting"] = dn["richting"]
            item["feestdatum"] = None
            occ: dict[str, list[str]] = {}
            occ_oud: dict[str, list[str]] = {}
            for y in years:
                nieuw = weekday_relative_date(
                    y,
                    dn["anker"],
                    dn["weekdag"],
                    dn["welke"],
                    dn["richting"],
                    stijl="nieuw",
                )
                oud = weekday_relative_date(
                    y,
                    dn["anker"],
                    dn["weekdag"],
                    dn["welke"],
                    dn["richting"],
                    stijl="oud",
                )
                _append_occ(occ, nieuw)
                _append_occ(occ_oud, oud)
            item["occurrences"] = occ
            item["occurrences_oud"] = occ_oud
        elif vorm == "periode" and dn.get("van") and dn.get("tot"):
            item["van"] = dn["van"]
            item["tot"] = dn["tot"]
            item["feestdatum"] = dn["van"]
        elif entry.get("cyclus") == "paascyclus" and vorm in {
            "periode",
            "periode_hybride",
        }:
            item["van_offset_dagen"] = dn["van_offset_dagen"]
            if vorm == "periode":
                item["tot_offset_dagen"] = dn["tot_offset_dagen"]
            else:
                item["tot"] = dn["tot_mmdd"]
            item["feestdatum"] = None
            periods: dict[str, dict[str, str]] = {}
            for y in years:
                bounds = period_bounds_for_year(entry, y)
                if not bounds:
                    continue
                start, end = bounds
                periods[str(y)] = {
                    "van": mmdd_from_date(start),
                    "tot": mmdd_from_date(end),
                }
            item["period_occurrences"] = periods
        elif entry.get("cyclus") == "paascyclus":
            offset = dn["paascyclus_offset"]
            occ: dict[str, str] = {}
            occ_j: dict[str, str] = {}
            for y in years:
                g = pascha_offset_date(y, offset)
                occ[str(y)] = mmdd_from_date(g)
                _jy, jm, jd = gregorian_to_julian_calendar(g)
                occ_j[str(y)] = format_mmdd(jm, jd)
            item["offset_dagen"] = offset
            item["feestdatum"] = None
            item["occurrences"] = occ
            item["occurrences_juliaans"] = occ_j
        else:
            feestdatum = dn["feestdatum"]
            item["feestdatum"] = feestdatum
            item["feestdatum_juliaans"] = dn.get("juliaans")
            item["feestdatum_gregoriaans"] = dn.get("gregoriaans")
        payload.append(item)
    write_text(
        STATIC_DATA / "entries.json",
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    )



def write_ics(
    entries: list[dict[str, Any]],
    lezingen_payload: dict[str, Any] | None = None,
) -> None:
    from ics import write_ics as _write_ics

    _write_ics(entries, lezingen_payload=lezingen_payload)


def clean_generated() -> None:
    for rel in (
        "content/dag",
        "content/heiligen",
        "content/feesten",
        "content/vasten",
        "static/data/entries.json",
        "static/data/lezingen-dagen.json",
        "static/data/plaatsen.json",
    ):
        path = SITE / rel
        if path.is_dir():
            shutil.rmtree(path)
        elif path.is_file():
            path.unlink()
    datum_dir = SITE / "content" / "datum"
    if datum_dir.is_dir():
        for path in datum_dir.iterdir():
            if path.name == "_index.md":
                continue
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
    for ics in (SITE / "static" / "ics").glob("*.ics"):
        ics.unlink()



def main() -> int:
    args = parse_args()
    if args.clean:
        clean_generated()
    entries = load_entries()
    ensure_hand_owned_indexes()
    ensure_achtergrond_topics()
    write_vasten_uitleg()
    write_generated_indexes(entries)
    for entry in entries:
        write_entry_page(entry)
    write_entries_json(entries)
    write_plaatsen_json()
    write_beheer_selectie(entries)
    lez = write_lezingen_json()
    write_ics(entries, lez)
    print(f"Gegenereerd: {len(entries)} entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
