"""Dag-centrische ICS-feeds: één VEVENT per burgerlijke dag."""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any, Iterable, Iterator
from urllib.parse import quote

from kalender import (
    format_mmdd,
    gregorian_to_julian_calendar,
    julian_feast_to_civil_date,
    mmdd_from_date,
    pascha_offset_date,
    weekday_relative_date,
)
from vasten import (
    NIVEAU_LABELS,
    VastenIndicatie,
    is_period_entry,
    is_weekly_entry,
    mix_vastenniveau,
)

SITE_PUBLIC_URL = "https://orthodox-ronl.github.io/kalender"

SUBSET_KEYS = {
    frozenset({"heilige", "feest", "vasten"}): "alles",
    frozenset({"heilige"}): "heiligen",
    frozenset({"feest"}): "feesten",
    frozenset({"vasten"}): "vasten",
    frozenset({"heilige", "feest"}): "heiligen-feesten",
    frozenset({"heilige", "vasten"}): "heiligen-vasten",
    frozenset({"feest", "vasten"}): "feesten-vasten",
}

CAL_NAMES = {
    "alles": "Orthodox · Lage Landen",
    "heiligen": "Heiligen Lage Landen",
    "feesten": "Feesten",
    "vasten": "Vasten",
    "heiligen-feesten": "Heiligen en feesten",
    "heiligen-vasten": "Heiligen en vasten",
    "feesten-vasten": "Feesten en vasten",
}

RAND_PREFIXES = ("voorfeest-", "nafeest-", "synaxis-", "teruggave-")
ICS_COMBOS = (
    frozenset({"heilige", "feest", "vasten"}),
    frozenset({"heilige"}),
    frozenset({"feest"}),
    frozenset({"vasten"}),
    frozenset({"heilige", "feest"}),
    frozenset({"heilige", "vasten"}),
    frozenset({"feest", "vasten"}),
)


def subset_key(kinds: frozenset[str]) -> str | None:
    return SUBSET_KEYS.get(kinds)


def calendar_name(key: str, stijl: str) -> str:
    return f"{CAL_NAMES[key]} ({stijl})"


def datum_pagina_url(civil: date, *, stijl: str | None = None) -> str:
    """URL naar de datumpagina; bij oud-feeds stijl=juliaans meegeven."""
    dag = mmdd_from_date(civil)
    url = f"{SITE_PUBLIC_URL}/datum/?datum={civil.year}-{quote(dag)}"
    if stijl == "oud":
        url += "&stijl=juliaans"
    elif stijl == "nieuw":
        url += "&stijl=gregoriaans"
    return url


def _ics_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def _fold(line: str) -> str:
    if len(line) <= 75:
        return line
    parts = [line[:75]]
    rest = line[75:]
    while rest:
        parts.append(" " + rest[:74])
        rest = rest[74:]
    return "\r\n".join(parts)


def _naam(entry: dict[str, Any]) -> str:
    namen = entry.get("namen") or {}
    if namen.get("primair"):
        return str(namen["primair"])
    if entry.get("naam"):
        return str(entry["naam"])
    return str(entry.get("id") or "")


def is_rand_feest(entry: dict[str, Any]) -> bool:
    eid = str(entry.get("id") or "")
    return any(eid.startswith(p) for p in RAND_PREFIXES)


def _mmdd_label(mmdd: str) -> str:
    from generate import mmdd_label

    return mmdd_label(mmdd)


def _iter_civil_days(start: date, end: date) -> Iterator[date]:
    from generate import iter_civil_days

    yield from iter_civil_days(start, end)


def _period_bounds_for_year(
    entry: dict[str, Any], year: int
) -> tuple[date, date] | None:
    from generate import period_bounds_for_year

    return period_bounds_for_year(entry, year)


def _occurrence_years(today: date | None = None) -> list[int]:
    from generate import occurrence_years

    return list(occurrence_years(today))


def suppresses_weekly(entry: dict[str, Any]) -> bool:
    if is_weekly_entry(entry):
        return False
    if entry.get("soort") == "vasten":
        return True
    return bool(entry.get("onderdrukt_wekelijks_vasten"))


def iter_occurrences(
    entry: dict[str, Any],
    stijl: str,
    years: Iterable[int],
) -> Iterator[date]:
    """Burgerlijke voorkomens van één entry, zelfde regels als de oude ICS."""
    dn = entry["datum_norm"]
    vorm = dn.get("vorm") or "dag"
    years = list(years)
    if vorm == "weekdagen":
        weekdagen = set(dn["weekdagen"])
        for year in years:
            for d in _iter_civil_days(date(year, 1, 1), date(year, 12, 31)):
                if d.isoweekday() in weekdagen:
                    yield d
        return

    if vorm == "weekdag_relatief":
        rel_stijl = "oud" if stijl == "oud" else "nieuw"
        for year in years:
            yield weekday_relative_date(
                year,
                dn["anker"],
                dn["weekdag"],
                dn["welke"],
                dn["richting"],
                stijl=rel_stijl,
            )
        return

    if vorm in {"periode", "periode_hybride"}:
        for year in years:
            bounds = _period_bounds_for_year(entry, year)
            if not bounds:
                continue
            start, end = bounds
            if start <= end:
                days = list(_iter_civil_days(start, end))
            else:
                days = list(_iter_civil_days(start, date(year, 12, 31)))
                days += list(_iter_civil_days(date(year, 1, 1), end))
            for d in days:
                feast_mmdd = mmdd_from_date(d)
                if stijl == "oud" and dn.get("van") and dn.get("tot"):
                    yield julian_feast_to_civil_date(year, feast_mmdd)
                else:
                    yield d
        return

    for year in years:
        if entry.get("cyclus") == "paascyclus":
            yield pascha_offset_date(year, dn["paascyclus_offset"])
        elif stijl == "oud":
            yield julian_feast_to_civil_date(year, dn["feestdatum"])
        else:
            month, day = (int(x) for x in dn["feestdatum"].split("-"))
            yield date(year, month, day)


def occurrences_by_date(
    entries: list[dict[str, Any]],
    stijl: str,
    years: Iterable[int],
) -> dict[date, list[dict[str, Any]]]:
    years = list(years)
    by_date: dict[date, list[dict[str, Any]]] = defaultdict(list)
    suppressed: set[date] = set()
    weekly: list[dict[str, Any]] = []
    for entry in entries:
        if is_weekly_entry(entry):
            weekly.append(entry)
            continue
        seen: set[date] = set()
        for civil in iter_occurrences(entry, stijl, years):
            if civil in seen:
                continue
            seen.add(civil)
            by_date[civil].append(entry)
            if suppresses_weekly(entry):
                suppressed.add(civil)
    for entry in weekly:
        seen: set[date] = set()
        for civil in iter_occurrences(entry, stijl, years):
            if civil in seen or civil in suppressed:
                continue
            seen.add(civil)
            by_date[civil].append(entry)
    return by_date


def is_day_type_feest(entry: dict[str, Any]) -> bool:
    if entry.get("soort") != "feest":
        return False
    if is_weekly_entry(entry) or is_period_entry(entry):
        return False
    return True


def _feast_weight(entry: dict[str, Any]) -> tuple[int, str]:
    eid = str(entry.get("id") or "")
    if eid == "pascha":
        return (0, _naam(entry))
    if eid.startswith("grote-") or eid in {"palmzondag", "theofanie", "kerst"}:
        return (1, _naam(entry))
    return (2, _naam(entry))


def _pick_one_feast(feesten: list[dict[str, Any]]) -> dict[str, Any]:
    return min(feesten, key=_feast_weight)


def kop_feesten(day_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Dagtype-feesten voor de SUMMARY (geen periodes, geen vasten)."""
    feesten = [e for e in day_entries if is_day_type_feest(e)]
    named = [e for e in feesten if not is_rand_feest(e)]
    rand = [e for e in feesten if is_rand_feest(e)]
    if named:
        return [_pick_one_feast(named)]
    if rand:
        synaxis = [e for e in rand if str(e.get("id") or "").startswith("synaxis-")]
        pool = synaxis or rand
        return [_pick_one_feast(pool)]
    return []


def kop_heiligen(day_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    heiligen = [e for e in day_entries if e.get("soort") == "heilige"]
    return sorted(heiligen, key=lambda e: _naam(e).casefold())


def kop_entries(day_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Terug compat: feest wint, anders heiligen (zonder daglabel)."""
    return kop_feesten(day_entries) or kop_heiligen(day_entries)


def kop_titel(items: list[dict[str, Any]]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return _naam(items[0])
    return ", ".join(_naam(e) for e in items)


def _mix_mmdd(civil: date, stijl: str) -> str:
    if stijl == "oud":
        _jy, jm, jd = gregorian_to_julian_calendar(civil)
        return format_mmdd(jm, jd)
    return mmdd_from_date(civil)


def vasten_bron_naam(
    indicatie: VastenIndicatie,
    day_entries: list[dict[str, Any]],
) -> str:
    if indicatie.periode_id:
        for e in day_entries:
            if e.get("id") == indicatie.periode_id:
                return _naam(e)
        return indicatie.periode_id
    weekly = [e for e in day_entries if is_weekly_entry(e)]
    if weekly:
        return _naam(weekly[0])
    tekst = indicatie.tekst or ""
    if " — " in tekst:
        return tekst.split(" — ", 1)[1].split(",", 1)[0].strip()
    return ""


def _lezingen_for_civil(
    payload: dict[str, Any] | None,
    civil: date,
    stijl: str,
) -> dict[str, Any] | None:
    if not payload:
        return None
    if stijl == "oud":
        jy, jm, jd = gregorian_to_julian_calendar(civil)
        key_year, key_mmdd = jy, format_mmdd(jm, jd)
    else:
        key_year, key_mmdd = civil.year, mmdd_from_date(civil)
    bucket = (payload.get(stijl) or {}).get(str(key_year)) or {}
    found = bucket.get(key_mmdd)
    return found if isinstance(found, dict) else None


def _ref_line(label: str, refs: list[Any] | None) -> str | None:
    bits: list[str] = []
    for item in refs or []:
        ref = ""
        if isinstance(item, dict):
            ref = str(item.get("ref") or "")
        else:
            ref = str(getattr(item, "ref", "") or "")
        if ref:
            bits.append(ref)
    if not bits:
        return None
    return f"{label}: " + "; ".join(bits)


def day_title(
    day_entries: list[dict[str, Any]],
    *,
    kinds: frozenset[str],
    civil: date,
    stijl: str = "nieuw",
    indicatie: VastenIndicatie | None | object = ...,
    lezingen: dict[str, Any] | None = None,
) -> str | None:
    """SUMMARY voor één dag, of None als de feed die dag overslaat."""
    visible = [
        e
        for e in day_entries
        if e.get("soort") in kinds and e.get("soort") in {"heilige", "feest"}
    ]
    if indicatie is ...:
        indicatie = mix_vastenniveau(
            day_entries,
            civil.isoweekday(),
            _mix_mmdd(civil, stijl),
        )
    show_vasten = "vasten" in kinds and indicatie is not None
    kop = kop_feesten(visible)
    headline = kop_titel(kop)
    if not headline and "feest" in kinds and lezingen and lezingen.get("daglabel"):
        headline = str(lezingen["daglabel"])
    if not headline:
        kop = kop_heiligen(visible)
        headline = kop_titel(kop)
    if not headline and not show_vasten:
        return None
    if not show_vasten:
        return headline or None
    assert isinstance(indicatie, VastenIndicatie)
    label = NIVEAU_LABELS.get(indicatie.niveau, indicatie.niveau)
    if headline:
        return f"{headline} · {label}"
    bron = vasten_bron_naam(indicatie, day_entries)
    if bron:
        return f"{label} · {bron}"
    return label


def _juliaans_regel(entry: dict[str, Any], stijl: str) -> str | None:
    if stijl != "oud":
        return None
    dn = entry.get("datum_norm") or {}
    if dn.get("feestdatum"):
        return f"Feestdatum: {_mmdd_label(dn['feestdatum'])} Juliaans"
    if dn.get("anker"):
        return f"t.o.v. Juliaans {_mmdd_label(dn['anker'])}"
    return None


def day_description(
    day_entries: list[dict[str, Any]],
    *,
    kinds: frozenset[str],
    civil: date,
    stijl: str,
    indicatie: VastenIndicatie | None,
    kop: list[dict[str, Any]],
    lezingen: dict[str, Any] | None = None,
) -> str:
    parts: list[str] = []
    if "vasten" in kinds and indicatie is not None:
        parts.append(indicatie.tekst)
    visible = [
        e
        for e in day_entries
        if e.get("soort") in kinds and e.get("soort") in {"heilige", "feest"}
    ]
    kop_ids = {e.get("id") for e in kop}
    rest = [
        e
        for e in visible
        if e.get("id") not in kop_ids and is_day_type_feest(e)
    ]
    if rest:
        rest_sorted = sorted(rest, key=lambda e: _naam(e).casefold())
        parts.append("Ook: " + ", ".join(_naam(e) for e in rest_sorted))
    if kop:
        jul = _juliaans_regel(kop[0], stijl)
        if jul:
            parts.append(jul)
    if lezingen and lezingen.get("status") == "gevonden":
        apostel = _ref_line("Apostel", lezingen.get("apostel"))
        evangelie = _ref_line("Evangelie", lezingen.get("evangelie"))
        if apostel:
            parts.append(apostel)
        if evangelie:
            parts.append(evangelie)
    elif lezingen and lezingen.get("status") == "geen_liturgie":
        parts.append("Geen liturgie met Apostel/Evangelie van de dag.")
    heiligen = [
        e
        for e in day_entries
        if e.get("soort") == "heilige" and "heilige" in kinds
    ]
    if heiligen:
        heiligen = sorted(heiligen, key=lambda e: _naam(e).casefold())
        label = "Heilige" if len(heiligen) == 1 else "Heiligen"
        parts.append(label + ": " + ", ".join(_naam(e) for e in heiligen))
    parts.append(f"Meer: {datum_pagina_url(civil, stijl=stijl)}")
    return "\n".join(parts)


def build_ics(
    entries: list[dict[str, Any]],
    *,
    cal_name: str,
    stijl: str = "nieuw",
    context_entries: list[dict[str, Any]] | None = None,
    feed_key: str = "alles",
    kinds: frozenset[str] | None = None,
    years: Iterable[int] | None = None,
    lezingen_payload: dict[str, Any] | None = None,
) -> str:
    """Bouw ICS: één hele-dag-afspraak per burgerlijke dag in de subset."""
    if kinds is None:
        kinds = frozenset(e["soort"] for e in entries)
    context = context_entries if context_entries is not None else entries
    year_list = list(years) if years is not None else _occurrence_years()
    if lezingen_payload is None:
        from lezingen import build_lezingen_dagen_payload

        lezingen_payload = build_lezingen_dagen_payload(year_list)
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    grouped = occurrences_by_date(context, stijl, year_list)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//orthodox-ronl//kalender//NL",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_ics_escape(cal_name)}",
        "X-WR-TIMEZONE:UTC",
        "X-PUBLISHED-TTL:P1D",
    ]
    for civil in sorted(grouped):
        day_entries = grouped[civil]
        mix_mmdd = _mix_mmdd(civil, stijl)
        indicatie = mix_vastenniveau(
            day_entries, civil.isoweekday(), mix_mmdd
        )
        lez = _lezingen_for_civil(lezingen_payload, civil, stijl)
        visible = [
            e
            for e in day_entries
            if e.get("soort") in kinds and e.get("soort") in {"heilige", "feest"}
        ]
        feest_kop = kop_feesten(visible)
        if feest_kop:
            kop = feest_kop
        elif "feest" in kinds and lez and lez.get("daglabel"):
            kop = []
        else:
            kop = kop_heiligen(visible)
        summary = day_title(
            day_entries,
            kinds=kinds,
            civil=civil,
            stijl=stijl,
            indicatie=indicatie,
            lezingen=lez,
        )
        if not summary:
            continue
        description = day_description(
            day_entries,
            kinds=kinds,
            civil=civil,
            stijl=stijl,
            indicatie=indicatie,
            kop=kop,
            lezingen=lez,
        )
        url = datum_pagina_url(civil, stijl=stijl)
        uid_key = f"{feed_key}:{stijl}:{civil.isoformat()}"
        uid = str(uuid.uuid5(uuid.NAMESPACE_URL, uid_key))
        dt_start = civil.strftime("%Y%m%d")
        dt_end = (civil + timedelta(days=1)).strftime("%Y%m%d")
        event = [
            "BEGIN:VEVENT",
            f"DTSTART;VALUE=DATE:{dt_start}",
            f"DTEND;VALUE=DATE:{dt_end}",
            f"DTSTAMP:{now}",
            f"UID:{uid}",
            f"SUMMARY:{_ics_escape(summary)}",
            f"DESCRIPTION:{_ics_escape(description)}",
            f"URL:{url}",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ]
        lines.extend(event)
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(line) for line in lines) + "\r\n"


def write_ics(
    entries: list[dict[str, Any]],
    lezingen_payload: dict[str, Any] | None = None,
) -> None:
    from generate import STATIC_ICS, write_text

    STATIC_ICS.mkdir(parents=True, exist_ok=True)
    if lezingen_payload is None:
        from lezingen import build_lezingen_dagen_payload
        from generate import occurrence_years

        lezingen_payload = build_lezingen_dagen_payload(list(occurrence_years()))
    for kinds in ICS_COMBOS:
        key = subset_key(kinds)
        assert key
        for stijl in ("nieuw", "oud"):
            name = calendar_name(key, stijl)
            filename = f"{key}-{stijl}.ics"
            write_text(
                STATIC_ICS / filename,
                build_ics(
                    entries,
                    cal_name=name,
                    stijl=stijl,
                    context_entries=entries,
                    feed_key=key,
                    kinds=kinds,
                    lezingen_payload=lezingen_payload,
                ),
            )
