"""Effectief vastenniveau voor één kalenderdag.

Normatieve regels: ``data/regels/vasten.yaml`` (uitlegpagina én tests).
Spiegel de mengregel in ``site/assets/js/calendar.js`` (``mixVastenniveau``).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
REGELS_PATH = REPO_ROOT / "data" / "regels" / "vasten.yaml"

NIVEAU_RANK = {
    "streng": 0,
    "wijn_olie": 1,
    "vis": 2,
    "lichter": 3,
    "vrij": 4,
}

# lichter ≈ wijn_olie als seizoenstag, zodat vis een echte versoepeling is.
COMPARE_RANK = {
    "streng": 0,
    "wijn_olie": 1,
    "lichter": 1,
    "vis": 2,
    "vrij": 3,
}

NIVEAU_LABELS = {
    "streng": "streng",
    "wijn_olie": "wijn en olie",
    "vis": "vis",
    "lichter": "lichter",
    "vrij": "vastenvrij",
}

GROTE_WEEK_ID = "grote-week"
GEBOORTE_VASTEN_ID = "geboorte-vasten"


def load_vastenregels() -> dict[str, Any]:
    return yaml.safe_load(REGELS_PATH.read_text(encoding="utf-8"))


def _naam(entry: dict[str, Any]) -> str:
    if entry.get("naam"):
        return str(entry["naam"])
    namen = entry.get("namen") or {}
    if namen.get("primair"):
        return str(namen["primair"])
    return str(entry.get("id") or "")


def _vorm(entry: dict[str, Any]) -> str:
    if entry.get("vorm"):
        return str(entry["vorm"])
    dn = entry.get("datum_norm") or {}
    return str(dn.get("vorm") or "dag")


def is_weekly_entry(entry: dict[str, Any]) -> bool:
    return _vorm(entry) == "weekdagen"


def is_period_entry(entry: dict[str, Any]) -> bool:
    vorm = _vorm(entry)
    if vorm in {"periode", "periode_hybride"}:
        return True
    if entry.get("van") and entry.get("tot"):
        return True
    if entry.get("period_occurrences"):
        return True
    return False


def _observances(entry: dict[str, Any]) -> list[str]:
    obs = entry.get("observances")
    if obs:
        return list(obs)
    soort = entry.get("soort")
    if soort == "heilige":
        return ["heilige"]
    if soort == "vasten":
        return ["vasten"]
    return ["feest"]


def _more_lenient(a: str, b: str) -> str:
    return a if COMPARE_RANK[a] >= COMPARE_RANK[b] else b


def _stricter(a: str, b: str) -> str:
    return a if COMPARE_RANK[a] <= COMPARE_RANK[b] else b


def period_daily_base(
    entry: dict[str, Any],
    weekday: int,
    *,
    in_grote_week: bool,
    mmdd: str | None,
) -> tuple[str, bool]:
    """Dagniveau uit een periode, vóór feestversoepeling.

    Geeft ``(niveau, weekend)`` terug. ``weekend`` is True als za/zo de
    basis versoepelt (olie in een strenge periode, vis in Apostelen-/Geboortevasten).
    """
    tag = str(entry.get("vastenniveau") or "streng")
    soort = entry.get("soort")
    if tag == "vrij":
        return "vrij", False
    if tag == "lichter" and soort == "vasten":
        if weekday in (6, 7):
            base, weekend = "vis", True
        elif weekday in (2, 4):
            base, weekend = "wijn_olie", False
        else:
            base, weekend = "streng", False
        if (
            entry.get("id") == GEBOORTE_VASTEN_ID
            and mmdd
            and "12-20" <= mmdd <= "12-24"
            and COMPARE_RANK[base] > COMPARE_RANK["wijn_olie"]
        ):
            base = "wijn_olie"
        return base, weekend
    if tag == "lichter":
        return "lichter", False
    if (
        weekday in (6, 7)
        and COMPARE_RANK.get(tag, 0) == COMPARE_RANK["streng"]
        and not in_grote_week
    ):
        return "wijn_olie", True
    return tag, False


@dataclass(frozen=True)
class VastenIndicatie:
    niveau: str
    tekst: str
    periode_id: str | None = None
    versoepeld_door_id: str | None = None
    weekend: bool = False


def _tekst(
    *,
    niveau: str,
    bron: str,
    versoepeld_door: str | None = None,
    weekend: bool = False,
    weekday: int | None = None,
) -> str:
    if niveau == "vrij":
        return f"Vastenvrij — {bron}"
    label = NIVEAU_LABELS.get(niveau, niveau)
    line = f"Vasten: {label} — {bron}"
    if versoepeld_door:
        line += f", versoepeld ({versoepeld_door})"
    elif weekend and weekday == 6:
        line += " (zaterdag)"
    elif weekend and weekday == 7:
        line += " (zondag)"
    return line


def mix_vastenniveau(
    day_entries: list[dict[str, Any]],
    weekday: int,
    mmdd: str | None = None,
) -> VastenIndicatie | None:
    """Bepaal het geldende vastenniveau voor de entries van één dag.

    ``weekday`` is ISO: 1=maandag … 7=zondag.
    ``mmdd`` is de kalenderdag (MM-DD) in dezelfde stijl als de entries;
    nodig voor Geboortevasten 20–24 december.
    ``day_entries`` zijn de entries die die dag raken (wekelijks al
    weggelaten als een periode het onderdrukt).
    """
    periods = [
        e
        for e in day_entries
        if is_period_entry(e)
        and not is_weekly_entry(e)
        and (e.get("soort") == "vasten" or e.get("vastenniveau"))
    ]
    weekly = [e for e in day_entries if is_weekly_entry(e)]
    day_feasts = [
        e
        for e in day_entries
        if e.get("vastenniveau")
        and not is_period_entry(e)
        and not is_weekly_entry(e)
    ]

    vrij_periods = [e for e in periods if e.get("vastenniveau") == "vrij"]
    if vrij_periods:
        bron = vrij_periods[0]
        return VastenIndicatie(
            niveau="vrij",
            tekst=_tekst(niveau="vrij", bron=_naam(bron)),
            periode_id=bron.get("id"),
        )

    in_grote_week = any(e.get("id") == GROTE_WEEK_ID for e in periods)

    if periods:
        base_entry = min(
            periods,
            key=lambda e: COMPARE_RANK.get(e.get("vastenniveau") or "streng", 0),
        )
        base, weekend = period_daily_base(
            base_entry,
            weekday,
            in_grote_week=in_grote_week,
            mmdd=mmdd,
        )

        relaxers = [
            e
            for e in day_feasts
            if COMPARE_RANK[str(e["vastenniveau"])] > COMPARE_RANK[base]
        ]
        versoepeld = None
        effective = base
        if relaxers:
            versoepeld = max(
                relaxers, key=lambda e: COMPARE_RANK[str(e["vastenniveau"])]
            )
            effective = str(versoepeld["vastenniveau"])

        if in_grote_week and COMPARE_RANK[effective] > COMPARE_RANK["wijn_olie"]:
            effective = "wijn_olie"

        return VastenIndicatie(
            niveau=effective,
            tekst=_tekst(
                niveau=effective,
                bron=_naam(base_entry),
                versoepeld_door=_naam(versoepeld) if versoepeld else None,
                weekend=weekend and not versoepeld,
                weekday=weekday,
            ),
            periode_id=base_entry.get("id"),
            versoepeld_door_id=(versoepeld or {}).get("id") if versoepeld else None,
            weekend=weekend and not versoepeld,
        )

    tightening = [e for e in day_feasts if "vasten" in _observances(e)]
    relaxing = [e for e in day_feasts if "vasten" not in _observances(e)]

    if tightening:
        chosen = min(
            tightening, key=lambda e: COMPARE_RANK[str(e["vastenniveau"])]
        )
        niveau = str(chosen["vastenniveau"])
        if weekly:
            niveau = _stricter(
                niveau, str(weekly[0].get("vastenniveau") or "wijn_olie")
            )
        return VastenIndicatie(
            niveau=niveau,
            tekst=_tekst(niveau=niveau, bron=_naam(chosen)),
            versoepeld_door_id=None,
        )

    if weekly:
        weekly_level = str(weekly[0].get("vastenniveau") or "wijn_olie")
        if relaxing:
            chosen = max(
                relaxing, key=lambda e: COMPARE_RANK[str(e["vastenniveau"])]
            )
            feast_level = str(chosen["vastenniveau"])
            effective = _more_lenient(weekly_level, feast_level)
            if effective == "vrij":
                return VastenIndicatie(
                    niveau="vrij",
                    tekst=_tekst(niveau="vrij", bron=_naam(chosen)),
                )
            if COMPARE_RANK[feast_level] > COMPARE_RANK[weekly_level]:
                return VastenIndicatie(
                    niveau=effective,
                    tekst=_tekst(
                        niveau=effective,
                        bron=_naam(weekly[0]),
                        versoepeld_door=_naam(chosen),
                    ),
                    versoepeld_door_id=chosen.get("id"),
                )
        return VastenIndicatie(
            niveau=weekly_level,
            tekst=_tekst(niveau=weekly_level, bron=_naam(weekly[0])),
        )

    vrij_feasts = [e for e in relaxing if e.get("vastenniveau") == "vrij"]
    if vrij_feasts:
        chosen = vrij_feasts[0]
        return VastenIndicatie(
            niveau="vrij",
            tekst=_tekst(niveau="vrij", bron=_naam(chosen)),
        )

    return None


def entries_on_civil_date(
    entries: list[dict[str, Any]], day: date
) -> list[dict[str, Any]]:
    """Entries die op deze burgerlijke dag vallen (wekelijks al onderdrukt)."""
    from generate import period_bounds_for_year
    from kalender import mmdd_from_date, pascha_offset_date

    mmdd = mmdd_from_date(day)
    matched: list[dict[str, Any]] = []
    suppressed = False
    for e in entries:
        dn = e["datum_norm"]
        vorm = dn.get("vorm") or "dag"
        if vorm == "weekdagen":
            continue
        bounds = period_bounds_for_year(e, day.year)
        hit = False
        if bounds:
            start, end = bounds
            if start <= end:
                hit = start <= day <= end
            else:
                hit = day >= start or day <= end
        elif e.get("cyclus") == "paascyclus" and vorm == "dag":
            hit = pascha_offset_date(day.year, dn["paascyclus_offset"]) == day
        elif dn.get("feestdatum") == mmdd:
            hit = True
        if not hit:
            continue
        matched.append(e)
        if e.get("onderdrukt_wekelijks_vasten") or (
            e["soort"] == "vasten" and vorm != "weekdagen"
        ):
            suppressed = True
    if not suppressed:
        for e in entries:
            dn = e["datum_norm"]
            if dn.get("vorm") == "weekdagen" and day.isoweekday() in dn["weekdagen"]:
                matched.append(e)
    return matched


def indicatie_op_datum(
    entries: list[dict[str, Any]], day: date
) -> VastenIndicatie | None:
    from kalender import mmdd_from_date

    return mix_vastenniveau(
        entries_on_civil_date(entries, day),
        day.isoweekday(),
        mmdd_from_date(day),
    )


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
WEEKDAY_NAMES_NL = [
    "",
    "maandag",
    "dinsdag",
    "woensdag",
    "donderdag",
    "vrijdag",
    "zaterdag",
    "zondag",
]


def nl_datum(iso: str) -> str:
    year, month, day = (int(p) for p in iso.split("-"))
    weekday = date(year, month, day).isoweekday()
    return f"{WEEKDAY_NAMES_NL[weekday]} {day} {MONTH_NAMES_NL[month]} {year}"


def _badge(niveau: str | None) -> str:
    if niveau is None:
        return '<span class="vasten-badge vasten-badge-geen">geen vasten</span>'
    label = NIVEAU_LABELS.get(niveau, niveau)
    return f'<span class="vasten-badge vasten-badge-{niveau}">{label}</span>'


def _clerus_voorbeelden(voorbeelden: list[dict[str, Any]]) -> list[str]:
    rows = [v for v in voorbeelden if v.get("datum")]
    if not rows:
        return []
    lines = [
        "",
        '<table class="vasten-tabel">',
        "<thead><tr><th>Wanneer</th><th>Op de kalender</th><th>Toelichting</th></tr></thead>",
        "<tbody>",
    ]
    for v in rows:
        toel = escape(v.get("toelichting") or "")
        lines.append(
            "<tr>"
            f"<td>{escape(nl_datum(v['datum']))}</td>"
            f"<td>{_badge(v.get('verwachte_niveau'))}</td>"
            f"<td>{toel}</td>"
            "</tr>"
        )
    lines.extend(["</tbody>", "</table>", ""])
    return lines


def render_vasten_clerus(regels: dict[str, Any] | None = None) -> str:
    """Markdown-body voor de cleruspagina ``site/content/uitleg/vasten.md``."""
    data = regels if regels is not None else load_vastenregels()
    lines: list[str] = []
    lines.append(data["inleiding"].strip())
    lines.append("")
    lines.append("## Waar de regels vandaan komen")
    lines.append("")
    lines.append(data["bronkeuze"].strip())
    lines.append("")
    lines.append("## Wat de kalender kan tonen")
    lines.append("")
    lines.append('<ul class="vasten-niveaus">')
    for n in data["niveaus"]:
        lines.append(
            "<li>"
            f"{_badge(n['id'])}"
            f"<p>{escape(n['betekenis'].strip())}</p>"
            "</li>"
        )
    geen = data.get("geen_regel") or {}
    if geen.get("betekenis"):
        lines.append(
            "<li>"
            f"{_badge(None)}"
            f"<p>{escape(str(geen['betekenis']).strip())}</p>"
            "</li>"
        )
    lines.append("</ul>")
    lines.append("")
    lines.append("## De regels")
    lines.append("")
    for regel in data["regels"]:
        lines.append(f'<section class="vasten-regel" id="regel-{regel["id"]}">')
        lines.append("")
        lines.append(f"### {regel['titel']}")
        lines.append("")
        lines.append(regel["tekst"].strip())
        lines.extend(_clerus_voorbeelden(regel.get("voorbeelden") or []))
        lines.append("</section>")
        lines.append("")
    vereenv = data.get("vereenvoudigingen") or []
    if vereenv:
        lines.append("## Wat we vereenvoudigen")
        lines.append("")
        for item in vereenv:
            lines.append(f"- {item.strip()}")
        lines.append("")
    nog = data.get("nog_niet") or []
    if nog:
        lines.append("## Wat nog niet in de kalender staat")
        lines.append("")
        lines.append(
            "Dit volgt het typikon nog niet. Na overleg kunnen we een punt "
            "hieronder tot regel maken; dan past de kalender mee."
        )
        lines.append("")
        for item in nog:
            lines.append(f"- {item.strip()}")
        lines.append("")
    lines.append("## Bronnen")
    lines.append("")
    for ref in data.get("referenties") or []:
        label = escape(ref["label"])
        url = ref.get("url")
        note = (ref.get("opmerking") or "").strip()
        href = f'<a href="{escape(url, quote=True)}">{label}</a>' if url else label
        note_html = f'<p class="vasten-bron-note">{escape(note)}</p>' if note else ""
        lines.append(
            f'<div class="vasten-bron">{href}{note_html}</div>'
        )
        lines.append("")
    lines.append("## Voor wie de site bijhoudt")
    lines.append("")
    lines.append(
        "De koppeling tussen deze tekst, de voorbeelden en de programmacode "
        "staat op de [technische pagina bij deze uitleg]({{% ref \"/uitleg/vasten-technisch\" %}}). "
        "Stap-voor-stap: [vastenregels wijzigen]({{% ref \"/beheer/how-to-vasten\" %}})."
    )
    lines.append("")
    return "\n".join(lines)


def render_vasten_technisch(regels: dict[str, Any] | None = None) -> str:
    """Markdown-body voor ``site/content/uitleg/vasten-technisch.md``."""
    data = regels if regels is not None else load_vastenregels()
    tech = data.get("technisch") or {}
    lines: list[str] = []
    lines.append(tech.get("inleiding", "").strip())
    lines.append("")
    lines.append("## Regel-ids")
    lines.append("")
    lines.append(
        "Elke regel heeft een stabiel id (`R-…`). Wijzig je `verwachte_niveau` "
        "in `data/regels/vasten.yaml`, dan falen de tests tot `scripts/vasten.py` "
        "en `site/assets/js/calendar.js` meegaan."
    )
    lines.append("")
    for regel in data["regels"]:
        lines.append(f"### R-{regel['id']} — {regel['titel']}")
        lines.append("")
        voorbeelden = regel.get("voorbeelden") or []
        dated = [v for v in voorbeelden if v.get("datum")]
        synthetic = [v for v in voorbeelden if not v.get("datum")]
        if dated:
            lines.append("| Datum | Verwacht | Toelichting |")
            lines.append("|---|---|---|")
            for v in dated:
                toel = (v.get("toelichting") or "").replace("|", "\\|")
                raw = v.get("verwachte_niveau")
                niveau_s = "geen vasten" if raw is None else f"`{raw}`"
                lines.append(f"| {v['datum']} | {niveau_s} | {toel} |")
            lines.append("")
        if synthetic:
            lines.append("Synthetische toets (geen burgerlijke datum):")
            lines.append("")
            for v in synthetic:
                raw = v.get("verwachte_niveau")
                lines.append(
                    f"- weekdag {v.get('weekday')}, `{v.get('mmdd')}` → "
                    f"`{raw}` — {v.get('toelichting') or ''}"
                )
            lines.append("")
    lines.append("## Niveaus in de data")
    lines.append("")
    lines.append("| Id | Label |")
    lines.append("|---|---|")
    for n in data["niveaus"]:
        lines.append(f"| `{n['id']}` | {n['label']} |")
    lines.append("")
    lines.append(
        "Ontbreekt een regel (`mix_vastenniveau` geeft `None`, "
        "`verwachte_niveau: null`), dan toont de datumpagina "
        "**geen vasten** (`vasten-badge-geen`); ICS vermeldt vasten niet."
    )
    lines.append("")
    return "\n".join(lines)


# Alias: oudere imports.
render_vasten_uitleg = render_vasten_clerus
