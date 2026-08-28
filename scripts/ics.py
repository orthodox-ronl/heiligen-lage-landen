"""Dag-centrische ICS-feeds: één VEVENT per burgerlijke dag."""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from itertools import combinations
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

SITE_PUBLIC_URL = "https://orthodox-ronl.github.io/heiligen-lage-landen"

KIND_ORDER = ("heilige", "feest", "vasten", "vastenvrij")
KIND_FILE = {
    "heilige": "heiligen",
    "feest": "feesten",
    "vasten": "vasten",
    "vastenvrij": "vastenvrij",
}


def subset_key(kinds: frozenset[str]) -> str | None:
    if not kinds or kinds - set(KIND_ORDER):
        return None
    if kinds == frozenset(KIND_ORDER):
        return "alles"
    return "-".join(KIND_FILE[k] for k in KIND_ORDER if k in kinds)


def calendar_title_from_kinds(kinds: frozenset[str]) -> str:
    if kinds == frozenset(KIND_ORDER):
        return "Orthodox · Lage Landen"
    bits: list[str] = []
    if "heilige" in kinds:
        bits.append("Heiligen")
    if "feest" in kinds:
        bits.append("feesten")
    if "vasten" in kinds:
        bits.append("vasten")
    if "vastenvrij" in kinds:
        bits.append("vastenvrij")
    if bits == ["Heiligen"]:
        return "Heiligen Lage Landen"
    if len(bits) == 1:
        return bits[0][:1].upper() + bits[0][1:]
    if len(bits) == 2:
        return f"{bits[0]} en {bits[1]}"
    return f"{', '.join(bits[:-1])} en {bits[-1]}"


STIJL_OUD_HEILIGEN_NIEUW = "oud-heiligen-nieuw"


def calendar_name(key: str, stijl: str) -> str:
    if key == "alles":
        title = "Orthodox · Lage Landen"
    elif key == "heiligen":
        title = "Heiligen Lage Landen"
    else:
        title = key.replace("-", " en ")
        title = title[:1].upper() + title[1:]
    if stijl == STIJL_OUD_HEILIGEN_NIEUW:
        return f"{title} (oud, heiligen nieuw)"
    return f"{title} ({stijl})"


def jaar_stijl(stijl: str) -> str:
    """Kalenderstijl van feesten, vasten en lezingen."""
    if stijl == STIJL_OUD_HEILIGEN_NIEUW:
        return "oud"
    return stijl


def heiligen_stijl_van(stijl: str) -> str:
    if stijl == STIJL_OUD_HEILIGEN_NIEUW:
        return "nieuw"
    return stijl


ICS_COMBOS = tuple(
    frozenset(combo)
    for n in range(1, len(KIND_ORDER) + 1)
    for combo in combinations(KIND_ORDER, n)
)

RAND_PREFIXES = ("voorfeest-", "nafeest-", "synaxis-", "teruggave-")


def datum_pagina_url(civil: date, *, stijl: str | None = None) -> str:
    """URL naar de datumpagina; bij oud-feeds stijl=juliaans meegeven."""
    dag = mmdd_from_date(civil)
    url = f"{SITE_PUBLIC_URL}/datum/?datum={civil.year}-{quote(dag)}"
    year = jaar_stijl(stijl) if stijl else None
    if year == "oud":
        url += "&stijl=juliaans"
    elif year == "nieuw":
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
    *,
    heiligen_stijl: str | None = None,
) -> dict[date, list[dict[str, Any]]]:
    years = list(years)
    year_stijl = jaar_stijl(stijl)
    saint_stijl = heiligen_stijl or heiligen_stijl_van(stijl)
    by_date: dict[date, list[dict[str, Any]]] = defaultdict(list)
    suppressed: set[date] = set()
    weekly: list[dict[str, Any]] = []
    for entry in entries:
        if is_weekly_entry(entry):
            weekly.append(entry)
            continue
        seen: set[date] = set()
        entry_stijl = saint_stijl if entry.get("soort") == "heilige" else year_stijl
        for civil in iter_occurrences(entry, entry_stijl, years):
            if civil in seen:
                continue
            seen.add(civil)
            by_date[civil].append(entry)
            if suppresses_weekly(entry):
                suppressed.add(civil)
    for entry in weekly:
        seen: set[date] = set()
        for civil in iter_occurrences(entry, year_stijl, years):
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


# Twaalf grootfeesten, Pascha, Grote Week, Lazarus-zaterdag, Geestesmaandag.
GROOTFEEST_IDS = frozenset(
    {
        "geboorte-moeder-gods",
        "kruisverheffing",
        "tempelgang-moeder-gods",
        "kerst",
        "theofanie",
        "ontmoeting-in-de-tempel",
        "aankondiging",
        "palmzondag",
        "pascha",
        "hemelvaart",
        "pinksteren",
        "transfiguratie",
        "ontslapen-moeder-gods",
        "lazarus-zaterdag",
        "grote-maandag",
        "grote-dinsdag",
        "grote-woensdag",
        "grote-donderdag",
        "grote-vrijdag",
        "grote-zaterdag",
        "geestesmaandag",
    }
)


def is_grootfeest(entry: dict[str, Any]) -> bool:
    return is_day_type_feest(entry) and str(entry.get("id") or "") in GROOTFEEST_IDS


def _feast_weight(entry: dict[str, Any]) -> tuple[int, str]:
    eid = str(entry.get("id") or "")
    if eid == "pascha":
        return (0, _naam(entry))
    if eid.startswith("grote-") or eid in {"palmzondag", "theofanie", "kerst"}:
        return (1, _naam(entry))
    return (2, _naam(entry))


def _pick_one_feast(feesten: list[dict[str, Any]]) -> dict[str, Any]:
    return min(feesten, key=_feast_weight)


def kop_grootfeesten(day_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    feesten = [e for e in day_entries if is_grootfeest(e)]
    if not feesten:
        return []
    return [_pick_one_feast(feesten)]


def kop_overige_feesten(day_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Dagtype-feesten die geen grootfeest zijn (synaxis, Triodion, …)."""
    feesten = [
        e for e in day_entries if is_day_type_feest(e) and not is_grootfeest(e)
    ]
    named = [e for e in feesten if not is_rand_feest(e)]
    rand = [e for e in feesten if is_rand_feest(e)]
    if named:
        return [_pick_one_feast(named)]
    if rand:
        synaxis = [e for e in rand if str(e.get("id") or "").startswith("synaxis-")]
        pool = synaxis or rand
        return [_pick_one_feast(pool)]
    return []


def kop_feesten(day_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Dagtype-feesten voor de SUMMARY (geen periodes, geen vasten)."""
    return kop_grootfeesten(day_entries) or kop_overige_feesten(day_entries)


def kop_heiligen(day_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    heiligen = [e for e in day_entries if e.get("soort") == "heilige"]
    return sorted(heiligen, key=lambda e: _naam(e).casefold())


def kop_entries(day_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Kop-entries: grootfeest, anders heiligen, anders overige feesten."""
    return (
        kop_grootfeesten(day_entries)
        or kop_heiligen(day_entries)
        or kop_overige_feesten(day_entries)
    )


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


def _show_fast_info(
    kinds: frozenset[str], indicatie: VastenIndicatie | None
) -> bool:
    if indicatie is None:
        return False
    if indicatie.niveau == "vrij":
        return "vastenvrij" in kinds
    return "vasten" in kinds


def day_title(
    day_entries: list[dict[str, Any]],
    *,
    kinds: frozenset[str],
    civil: date,
    stijl: str = "nieuw",
    indicatie: VastenIndicatie | None | object = ...,
    lezingen: dict[str, Any] | None = None,
) -> str | None:
    """SUMMARY voor één dag, of None als de feed die dag overslaat.

    Prioriteit: grootfeest, heilige van de Lage Landen, overige feesten/daglabel.
    Op maandag (geen grootfeest) staat de liturgische week vooraan.
    """
    from lezingen import week_kop_label

    visible = [
        e
        for e in day_entries
        if e.get("soort") in kinds and e.get("soort") in {"heilige", "feest"}
    ]
    year_s = jaar_stijl(stijl)
    if indicatie is ...:
        indicatie = mix_vastenniveau(
            day_entries,
            civil.isoweekday(),
            _mix_mmdd(civil, year_s),
        )
    show_vasten = _show_fast_info(
        kinds, indicatie if isinstance(indicatie, VastenIndicatie) else None
    )
    groot = kop_grootfeesten(visible) if "feest" in kinds else []
    saints = kop_heiligen(visible) if "heilige" in kinds else []
    rest = kop_overige_feesten(visible) if "feest" in kinds else []
    daglabel = ""
    if "feest" in kinds and lezingen and lezingen.get("daglabel"):
        daglabel = str(lezingen["daglabel"])

    headline = ""
    if groot:
        headline = kop_titel(groot)
    elif civil.isoweekday() == 1 and "feest" in kinds:
        week = week_kop_label(civil)
        extra = saints or rest
        extra_t = kop_titel(extra)
        if week and extra_t:
            headline = f"{week} · {extra_t}"
        elif week:
            headline = week
        elif extra_t:
            headline = extra_t
        else:
            headline = daglabel
    elif saints:
        headline = kop_titel(saints)
    elif rest:
        headline = kop_titel(rest)
    else:
        headline = daglabel

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
    if _show_fast_info(kinds, indicatie):
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
    year_s = jaar_stijl(stijl)
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
        mix_mmdd = _mix_mmdd(civil, year_s)
        indicatie = mix_vastenniveau(
            day_entries, civil.isoweekday(), mix_mmdd
        )
        lez = _lezingen_for_civil(lezingen_payload, civil, year_s)
        visible = [
            e
            for e in day_entries
            if e.get("soort") in kinds and e.get("soort") in {"heilige", "feest"}
        ]
        kop = kop_entries(visible)
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
            stijl=year_s,
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
        stijlen = ["nieuw", "oud"]
        if "heilige" in kinds and kinds - {"heilige"}:
            stijlen.append(STIJL_OUD_HEILIGEN_NIEUW)
        for stijl in stijlen:
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
