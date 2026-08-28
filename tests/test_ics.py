"""Dag-centrische ICS: één VEVENT per burgerlijke dag."""

from __future__ import annotations

import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ics import (  # noqa: E402
    ICS_COMBOS,
    SITE_PUBLIC_URL,
    build_ics,
    calendar_name,
    day_title,
    subset_key,
)
from kalender import julian_feast_to_civil_date  # noqa: E402
from lezingen import build_lezingen_dagen_payload  # noqa: E402
from load_entries import load_entries  # noqa: E402

YEARS = [2025, 2026]
ALLES = frozenset({"heilige", "feest", "vasten", "vastenvrij"})
VASTEN = frozenset({"vasten"})
VASTENVRIJ = frozenset({"vastenvrij"})
HEILIGEN = frozenset({"heilige"})

_ENTRIES: list | None = None
_PAYLOAD: dict | None = None


def _entries():
    global _ENTRIES
    if _ENTRIES is None:
        _ENTRIES = load_entries()
    return _ENTRIES


def _payload():
    global _PAYLOAD
    if _PAYLOAD is None:
        _PAYLOAD = build_lezingen_dagen_payload(YEARS)
    return _PAYLOAD


def _unfold(text: str) -> str:
    lines = text.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    for line in lines:
        if line.startswith(" ") and out:
            out[-1] += line[1:]
        else:
            out.append(line)
    return "\n".join(out)


def parse_events(ics: str) -> dict[str, dict[str, str]]:
    text = _unfold(ics)
    events: dict[str, dict[str, str]] = {}
    cur: dict[str, str] = {}
    for line in text.split("\n"):
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line.startswith("DTSTART"):
            cur["start"] = line.rsplit(":", 1)[-1]
        elif line.startswith("SUMMARY:"):
            cur["summary"] = line[8:].replace("\\n", "\n").replace("\\,", ",")
        elif line.startswith("DESCRIPTION:"):
            cur["description"] = line[12:].replace("\\n", "\n").replace("\\,", ",")
        elif line.startswith("URL:"):
            cur["url"] = line[4:]
        elif line == "END:VEVENT":
            events[cur["start"]] = cur
    return events


def _build(kinds: frozenset[str], stijl: str = "nieuw", years: list[int] | None = None):
    entries = _entries()
    key = {
        ALLES: "alles",
        VASTEN: "vasten",
        HEILIGEN: "heiligen",
        VASTENVRIJ: "vastenvrij",
    }[kinds]
    return build_ics(
        entries,
        cal_name=calendar_name(key, stijl),
        stijl=stijl,
        context_entries=entries,
        feed_key=key,
        kinds=kinds,
        years=years or YEARS,
        lezingen_payload=_payload(),
    )


def test_albericus_in_grote_vasten_is_een_dagregel() -> None:
    events = parse_events(_build(ALLES))
    ev = events["20260304"]
    assert ev["summary"] == "Albericus van Utrecht · streng"
    assert "Grote Vasten" in ev["description"]
    assert "Heilige: Albericus van Utrecht" in ev["description"]
    assert ev["description"].split("\n")[-1].startswith("Meer:")
    assert "debijbel.nl" not in ev["description"]
    assert ev["url"].startswith(SITE_PUBLIC_URL)
    assert "datum=2026-03-04" in ev["url"]
    assert "stijl=gregoriaans" in ev["url"]
    assert "jaar=" not in ev["url"]


def test_aankondiging_in_grote_vasten_heeft_vis() -> None:
    events = parse_events(_build(ALLES))
    assert events["20260325"]["summary"] == "Aankondiging aan de Moeder Gods · vis"


def test_willibrord_zonder_vastensuffix() -> None:
    events = parse_events(_build(ALLES))
    ev = events["20261107"]
    assert ev["summary"] == "Willibrord"
    assert "Willibrord" in ev["description"]
    assert "Apostel:" in ev["description"]
    assert "Evangelie:" in ev["description"]
    assert "debijbel.nl" not in ev["description"]
    assert ev["description"].split("\n")[-1].startswith("Meer:")


def test_pascha_een_balk_met_vastenvrij() -> None:
    events = parse_events(_build(ALLES))
    ev = events["20260412"]
    assert ev["summary"].startswith("Pascha")
    assert "vastenvrij" in ev["summary"]
    assert "Lichte Week" in ev["description"]


def test_synaxis_en_nafeest_een_titel() -> None:
    events = parse_events(_build(ALLES))
    ev = events["20260107"]
    assert ev["summary"] == "Synaxis van Johannes de Doper · wijn en olie"
    assert not ev["summary"].startswith("Nafeest")
    assert ev["description"].split("\n")[-1].startswith("Meer:")


def test_vasten_only_grote_vasten_en_lege_dinsdag() -> None:
    events = parse_events(_build(VASTEN))
    assert events["20260304"]["summary"] == "streng · Grote Vasten"
    assert events["20260307"]["summary"] == "wijn en olie · Grote Vasten"
    assert "20260113" not in events


def test_lichte_week_niet_in_alleen_vasten() -> None:
    events = parse_events(_build(VASTEN))
    assert "20260412" not in events
    assert "20260413" not in events


def test_lichte_week_in_vastenvrij() -> None:
    events = parse_events(_build(VASTENVRIJ))
    ev = events["20260412"]
    assert "vastenvrij" in ev["summary"].lower()


def test_heiligen_only_geen_vastenprefix() -> None:
    events = parse_events(_build(HEILIGEN))
    assert events["20260304"]["summary"] == "Albericus van Utrecht"
    assert "streng" not in events["20260304"]["summary"]


def test_oud_kerst_op_zeven_januari_zonder_juliaans_in_titel() -> None:
    civil = julian_feast_to_civil_date(2025, "12-25")
    assert civil == date(2026, 1, 7)
    events = parse_events(_build(ALLES, stijl="oud"))
    ev = events[civil.strftime("%Y%m%d")]
    assert "Kerst" in ev["summary"]
    assert "Juliaans" not in ev["summary"]
    assert "Juliaans" in ev["description"]
    assert "stijl=juliaans" in ev["url"]
    assert f"datum={civil.isoformat()}" in ev["url"]


def _assert_een_event_per_dag(ics: str) -> None:
    starts = []
    for line in _unfold(ics).split("\n"):
        if line.startswith("DTSTART"):
            starts.append(line.rsplit(":", 1)[-1])
    counts = Counter(starts)
    assert counts, "verwacht minstens één afspraak"
    assert max(counts.values()) == 1


def test_een_event_per_dag() -> None:
    _assert_een_event_per_dag(_build(ALLES))


def test_een_event_per_dag_oud() -> None:
    _assert_een_event_per_dag(_build(ALLES, stijl="oud"))


def test_alle_feeds_een_event_per_dag() -> None:
    entries = _entries()
    payload = _payload()
    for kinds in ICS_COMBOS:
        key = subset_key(kinds)
        assert key
        for stijl in ("nieuw", "oud"):
            ics = build_ics(
                entries,
                cal_name=calendar_name(key, stijl),
                stijl=stijl,
                context_entries=entries,
                feed_key=key,
                kinds=kinds,
                years=YEARS,
                lezingen_payload=payload,
            )
            _assert_een_event_per_dag(ics)


def test_calname_en_ttl_en_url() -> None:
    ics = _build(ALLES)
    assert "X-WR-CALNAME:Orthodox · Lage Landen (nieuw)" in _unfold(ics)
    assert "X-PUBLISHED-TTL:P1D" in ics
    assert "URL:https://orthodox-ronl.github.io/heiligen-lage-landen/datum/" in _unfold(ics)


def test_day_title_leeg_zonder_subset() -> None:
    assert (
        day_title(
            [],
            kinds=HEILIGEN,
            civil=date(2026, 1, 13),
        )
        is None
    )


def test_maandag_toont_weeknaam() -> None:
    events = parse_events(_build(ALLES))
    ev = events["20260608"]
    assert ev["summary"].startswith("2e week na Pinksteren")
    assert "Medardus" in ev["summary"]


def test_geestesmaandag_niet_weeknaam() -> None:
    events = parse_events(_build(ALLES))
    ev = events["20260601"]
    assert ev["summary"].startswith("Maandag van de Heilige Geest")


def test_oud_vijftien_juli_is_otger_niet_vladimir() -> None:
    events = parse_events(_build(ALLES, stijl="oud"))
    ev = events["20260728"]
    assert "Otger" in ev["summary"]
    assert "Vladimir" not in ev["summary"]


def test_otger_plechelm_op_vijftien_juli() -> None:
    events = parse_events(_build(ALLES))
    ev = events["20260715"]
    assert "Otger" in ev["summary"]
    assert "Plechelm" in ev["summary"]


def test_oud_heiligen_nieuw_willibrord_op_zeven_november() -> None:
    from ics import STIJL_OUD_HEILIGEN_NIEUW

    events = parse_events(_build(ALLES, stijl=STIJL_OUD_HEILIGEN_NIEUW))
    assert "Willibrord" in events["20261107"]["summary"]
    assert "20261120" not in events or "Willibrord" not in events.get(
        "20261120", {}
    ).get("summary", "")
    kerst = julian_feast_to_civil_date(2025, "12-25")
    assert kerst == date(2026, 1, 7)
    assert "Kerst" in events[kerst.strftime("%Y%m%d")]["summary"]
    ics = _build(ALLES, stijl=STIJL_OUD_HEILIGEN_NIEUW)
    assert "heiligen nieuw" in _unfold(ics)
