"""Resolutie van Apostel- en Evangelielezingen (Moskou / ROCOR-fallback).

Normatieve regels: docs/specs/lezingen.md
Data: data/lezingen/
"""

from __future__ import annotations

import calendar
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

from kalender import (
    gregorian_to_julian_calendar,
    mmdd_from_date,
    parse_mmdd,
    pascha_offset_date,
    orthodox_pascha,
    weekday_relative_date,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "docs" / "specs" / "lezingen.md"
DATA_DIR = REPO_ROOT / "data" / "lezingen"
VOORBEELD_FENCE = re.compile(
    r"```lezingen-voorbeeld\s*\n(.*?)```",
    re.DOTALL,
)

WEEKDAG_NL = {
    1: "Maandag",
    2: "Dinsdag",
    3: "Woensdag",
    4: "Donderdag",
    5: "Vrijdag",
    6: "Zaterdag",
    7: "Zondag",
}

# Vaste override-id → Nederlandse liturgische dagnaam
OVERRIDE_NAMEN: dict[str, str] = {
    "pascha": "Pascha",
    "lichte-maandag": "Lichte maandag",
    "thomaszondag": "Thomaszondag",
    "zondag-myrondraagsters": "Zondag van de myrondraagsters",
    "zondag-verlamde": "Zondag van de verlamde",
    "midden-pinksterfeest": "Midden-Pinksterfeest",
    "zondag-samaritaanse": "Zondag van de Samaritaanse",
    "zondag-blinde": "Zondag van de blinde",
    "hemelvaart": "Hemelvaart",
    "zondag-vaderen-eerste-concilie": "Zondag van de heilige Vaderen (Eerste Concilie)",
    "pinksteren": "Pinksteren",
    "geestesmaandag": "Maandag van de Heilige Geest",
    "allerheiligen-zondag": "Allerheiligenzondag",
    "zondag-heiligen-lage-landen": "Zondag van de heiligen van de Lage Landen",
    "zondag-laatste-oordeel": "Zondag van het Laatste Oordeel",
    "vergevingszondag": "Vergevingszondag",
    "zondag-orthodoxie": "Zondag van de Orthodoxie",
    "zondag-gregorius-palamas": "Zondag van Gregorius Palamas",
    "zondag-kruisverering": "Zondag van de Kruisverering",
    "zondag-johannes-klimacus": "Zondag van Johannes Klimacus",
    "zondag-maria-van-egypte": "Zondag van Maria van Egypte",
    "lazarus-zaterdag": "Lazaruszaterdag",
    "palmzondag": "Palmzondag",
    "grote-donderdag": "Heilige grote donderdag",
    "grote-zaterdag": "Heilige grote zaterdag",
    "besnijdenis-des-heren": "Besnijdenis des Heren",
    "theofanie": "Theofanie",
    "zaterdag-voor-theofanie": "Zaterdag vóór Theofanie",
    "zondag-voor-theofanie": "Zondag vóór Theofanie",
    "zaterdag-na-theofanie": "Zaterdag na Theofanie",
    "ontmoeting-in-de-tempel": "Ontmoeting in de tempel",
    "aankondiging": "Aankondiging",
    "geboorte-johannes-doper": "Geboorte van Johannes de Doper",
    "petrus-en-paulus": "Petrus en Paulus",
    "transfiguratie": "Transfiguratie",
    "ontslapen-moeder-gods": "Ontslapen van de Moeder Gods",
    "onthoofding-johannes-doper": "Onthoofding van Johannes de Doper",
    "begin-kerkelijk-jaar": "Begin van het kerkelijk jaar",
    "geboorte-moeder-gods": "Geboorte van de Moeder Gods",
    "kruisverheffing": "Kruisverheffing",
    "zaterdag-voor-kruisverheffing": "Zaterdag vóór Kruisverheffing",
    "zondag-voor-kruisverheffing": "Zondag vóór Kruisverheffing",
    "zaterdag-na-kruisverheffing": "Zaterdag na Kruisverheffing",
    "zondag-na-kruisverheffing": "Zondag na Kruisverheffing",
    "tempelgang-moeder-gods": "Tempelgang van de Moeder Gods",
    "kerst": "Kerst",
    "synaxis-moeder-gods": "Synaxis van de Moeder Gods",
    "synaxis-johannes-doper": "Synaxis van Johannes de Doper",
    "pokrov": "Pokrov",
    "zondag-vaderen-zevende-concilie": "Zondag van de heilige Vaderen van het Zevende Concilie",
    "synaxis-gabriel": "Synaxis van de aartsengel Gabriël",
    "zondag-voorvaderen": "Zondag van de Voorvaderen",
    "zaterdag-voor-kerst": "Zaterdag vóór Kerst",
    "zondag-vaderen-voor-kerst": "Zondag van de heilige Vaderen (vóór Kerst)",
    "zondag-na-kerst": "Zondag na Kerst",
    "zondag-na-theofanie": "Zondag na Theofanie",
    "elia-profeet": "Profeet Elia",
    "aankondiging-op-pascha": "Aankondiging op Pascha (Kyriopascha)",
    "aankondiging-op-palmzondag": "Aankondiging op Palmzondag",
    "aankondiging-op-grote-zaterdag": "Aankondiging op grote zaterdag",
    "aankondiging-in-grote-week": "Aankondiging in de Grote Week",
    "nicolaas-wonderdoener": "Nicolaas de Wonderdoener",
    "george-grootmartelaar": "George de Grootmartelaar",
    "demetrius-grootmartelaar": "Demetrius de Grootmartelaar",
    "synaxis-aartsengel-michael": "Synaxis van de aartsengel Michaël",
    "drie-hiërarchen": "Drie Hiërarchen",
    "serafim-van-sarov": "Serafim van Sarov",
    "vladimir-gelijkaan-apostelen": "Vladimir, gelijkaan de apostelen",
    "silvester": "Silvester van Rome",
}

# Menaion-polyeleos zonder feest-YAML: wel lezing, geen dagtype/kopregel.
MENAION_KOP_IDS = frozenset(
    {
        "elia-profeet",
        "nicolaas-wonderdoener",
        "george-grootmartelaar",
        "demetrius-grootmartelaar",
        "synaxis-aartsengel-michael",
        "drie-hiërarchen",
        "serafim-van-sarov",
        "vladimir-gelijkaan-apostelen",
        "silvester",
    }
)


RANG_PATH = DATA_DIR / "rang.yaml"
_RANG_CFG: dict[str, Any] | None = None


def load_rang_config() -> dict[str, Any]:
    global _RANG_CFG
    if _RANG_CFG is not None:
        return _RANG_CFG
    if RANG_PATH.is_file():
        _RANG_CFG = load_yaml(RANG_PATH) or {}
    else:
        _RANG_CFG = {
            "rangen": {
                "groot": {"prioriteit": 100, "default_modus": "vervangen"},
                "polyeleos": {"prioriteit": 70, "default_modus": "auto"},
            },
            "auto": {"zondag": "toevoegen", "weekdag": "vervangen"},
        }
    return _RANG_CFG


def rang_prioriteit(rang: str) -> int:
    cfg = load_rang_config().get("rangen") or {}
    info = cfg.get(rang) or {}
    return int(info.get("prioriteit") or 0)


def default_modus_voor_rang(rang: str) -> str:
    cfg = load_rang_config().get("rangen") or {}
    info = cfg.get(rang) or {}
    return str(info.get("default_modus") or "vervangen")


@dataclass
class LezingRef:
    ref: str
    zacalo: int | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"ref": self.ref}
        if self.zacalo is not None:
            out["zacalo"] = self.zacalo
        return out


@dataclass
class LezingenResultaat:
    apostel: list[LezingRef] = field(default_factory=list)
    evangelie: list[LezingRef] = field(default_factory=list)
    regels: list[str] = field(default_factory=list)
    override_id: str | None = None
    daglabel: str = ""
    toelichting: str = ""
    status: str = "onbekend"  # gevonden | geen_liturgie | onbekend
    rang: str | None = None
    modus: str | None = None  # vervangen | toevoegen | negeren
    rijadovoe: dict[str, Any] | None = None  # onderdrukte of meegenomen basis

    def as_dict(self) -> dict[str, Any]:
        oid = self.override_id
        if oid and oid in MENAION_KOP_IDS:
            override_laag = "menaion"
        elif oid:
            override_laag = "feest"
        else:
            override_laag = None
        out: dict[str, Any] = {
            "apostel": [a.as_dict() for a in self.apostel],
            "evangelie": [e.as_dict() for e in self.evangelie],
            "regels": list(self.regels),
            "override_id": oid,
            "override_naam": OVERRIDE_NAMEN.get(oid) if oid else None,
            "override_laag": override_laag,
            "daglabel": self.daglabel,
            "toelichting": self.toelichting,
            "status": self.status,
            "rang": self.rang,
            "modus": self.modus,
        }
        if self.rijadovoe is not None:
            out["rijadovoe"] = self.rijadovoe
        return out


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_overrides() -> list[dict[str, Any]]:
    """Gedeelde feestoverrides + optionele parochie-lijst.

    Volgorde: eerst ``feest-overrides.yaml``, daarna
    ``parochies/<parochie-id>.yaml`` (als ``config.yaml`` een ``parochie`` zet).
    Bij meerdere matches wint nog steeds de hoogste ``prioriteit`` (R5).
    """
    path = DATA_DIR / "feest-overrides.yaml"
    out: list[dict[str, Any]] = []
    if path.is_file():
        raw = load_yaml(path) or {}
        out.extend(list(raw.get("overrides") or []))

    cfg_path = DATA_DIR / "config.yaml"
    parochie_id = ""
    if cfg_path.is_file():
        cfg = load_yaml(cfg_path) or {}
        parochie_id = str(cfg.get("parochie") or "").strip()
    if parochie_id:
        p_path = DATA_DIR / "parochies" / f"{parochie_id}.yaml"
        if not p_path.is_file():
            raise FileNotFoundError(
                f"Parochie-lezingen ontbreken: {p_path.relative_to(REPO_ROOT)}"
            )
        raw_p = load_yaml(p_path) or {}
        for ov in raw_p.get("overrides") or []:
            if not isinstance(ov, dict):
                continue
            item = dict(ov)
            # Parochiekeuzes winnen standaard van gedeelde overrides.
            if "prioriteit" not in item:
                item["prioriteit"] = 300
            out.append(item)
    return out


_WEEKREEKS: dict[tuple[str, int, int], dict[str, Any]] | None = None


def load_weekreeks() -> dict[tuple[str, int, int], dict[str, Any]]:
    global _WEEKREEKS
    if _WEEKREEKS is not None:
        return _WEEKREEKS
    path = DATA_DIR / "weekreeks.yaml"
    out: dict[tuple[str, int, int], dict[str, Any]] = {}
    if path.is_file():
        raw = load_yaml(path) or {}
        for row in raw.get("dagen") or []:
            key = (str(row["periode"]), int(row["week"]), int(row["weekdag"]))
            out[key] = row
    _WEEKREEKS = out
    return out


def _refs(items: list[dict[str, Any]] | None) -> list[LezingRef]:
    out: list[LezingRef] = []
    for item in items or []:
        out.append(
            LezingRef(
                ref=str(item["ref"]).strip(),
                zacalo=item.get("zacalo"),
            )
        )
    return out


def _mmdd_for_offset(year: int, offset: int, stijl: str) -> str:
    civil = pascha_offset_date(year, offset)
    if stijl == "oud":
        _jy, jm, jd = gregorian_to_julian_calendar(civil)
        return f"{jm:02d}-{jd:02d}"
    return mmdd_from_date(civil)


def _civil_date(jaar: int, mmdd: str, stijl: str) -> date:
    """Wereldlijke datum bij gegeven kalenderdagnaam."""
    month, day = parse_mmdd(mmdd)
    if stijl == "oud":
        from kalender import julian_calendar_to_gregorian

        return julian_calendar_to_gregorian(jaar, month, day)
    return date(jaar, month, day)


def _iso_weekday(d: date) -> int:
    """1=ma … 7=zo."""
    return d.isoweekday()


def lucaanse_sprong_maandag(jaar: int) -> date:
    """Maandag na de zondag na Kruisverheffing (14 sept., feestdatum).

    Als 14 sept. zelf zondag is, geldt de *volgende* zondag als
    «Неделя по Воздвижении».
    """
    exaltation = date(jaar, 9, 14)
    if exaltation.isoweekday() == 7:
        nedelya = exaltation + timedelta(days=7)
    else:
        # eerstvolgende zondag strikt na 14 sept.
        nedelya = exaltation + timedelta(days=(7 - exaltation.isoweekday()))
    return nedelya + timedelta(days=1)


def lucaanse_aanpassing(jaar: int) -> str:
    """Moskou: отступка / преступка / normaal o.b.v. Juliaanse Pascha-datum.

    Azbyka: Pascha ≤ 30 maart (Juliaans) → отступка; ≥ 7 april → преступка;
    31 maart–6 april → geen van beide. De sprong naar Luc. week 18 op de
    Lucaanse maandag blijft in alle gevallen gelden.
    """
    from kalender import orthodox_pascha_julian

    jm, jd = orthodox_pascha_julian(jaar)
    if jm < 4 or (jm == 3 and jd <= 30):
        return "otstupka"
    if jm == 4 and jd >= 7:
        return "prestupka"
    return "normaal"


def gospel_week_na_pinksteren(
    apostol_week: int,
    civil: date,
    luke_mon: date,
) -> tuple[int, list[str]]:
    """Bepaal Evangelie-tabelweek + R3-tags (Lucaanse sprong / отступка).

    Vóór de Lucaanse maandag: Matteüs-reeks (weken 1–17). Als de doorlopende
    week al ≥ 18 is (vroege Pascha), herhaal binnen 1–17 (отступка) — anders
    zou je per ongeluk Lucasse tabelrijen vóór de sprong lezen.
    Vanaf de Lucaanse maandag: Luc. vanaf week 18. Vanaf tabelweek 30 (winter):
    weer dezelfde week als de Apostel (Marcus-eindreeks), ook als de Lucaanse
    maandag van *dit* burgerlijke jaar nog in de toekomst ligt.
    """
    regels = ["R3"]
    aanpassing = lucaanse_aanpassing(civil.year)

    # Winterreeks (weken 30–33): Marcus e.d. — niet Matteüs-wrap of Luc.+N.
    if apostol_week >= 30:
        return apostol_week, regels

    if civil >= luke_mon:
        gospel_week = 18 + (civil - luke_mon).days // 7
        regels.append("R3-lucaans")
        if aanpassing == "prestupka":
            regels.append("R3-prestupka")
        elif aanpassing == "otstupka":
            regels.append("R3-otstupka")
        return gospel_week, regels

    if apostol_week >= 18:
        # Отступка vóór de sprong: blijf in Matteüs 1–17.
        gospel_week = ((apostol_week - 1) % 17) + 1
        regels.append("R3-otstupka")
        return gospel_week, regels

    return apostol_week, regels


# Tabelweken die herhaald worden bij Theofanie-/winter-отступка (Bogaiskov /
# MP-kalender): N ontbrekende weken vóór Tollenaar-zondag.
THEOFANIE_OTSTUPKA_WEEKEN: dict[int, list[int]] = {
    1: [33],
    2: [32, 33],
    3: [31, 32, 33],
    4: [30, 31, 32, 33],
    5: [30, 31, 17, 32, 33],
}


def theofanie_otstupka_context(
    civil: date,
) -> tuple[date, date, int] | None:
    """Winter-/Theofanie-отступка-venster.

    Retourneert ``(maandag_week_34, tollenaar_zondag, N)`` met ``N`` in 1..5,
    of ``None`` als er geen отступка is of de dag vóór week 34 valt.
    """
    pascha_up = orthodox_pascha(civil.year)
    if civil >= pascha_up:
        return None
    publican = pascha_up + timedelta(days=-70)
    if civil >= publican:
        return None

    pascha_prev = orthodox_pascha(pascha_up.year - 1)
    pentecost = pascha_prev + timedelta(days=49)
    fri33 = pentecost + timedelta(days=(33 - 1) * 7 + 5)
    mon34 = fri33 + timedelta(days=3)
    if civil < mon34:
        return None

    n = 0
    d = mon34
    while d < publican:
        n += 1
        d += timedelta(days=7)
    n = min(5, n)
    if n <= 0:
        return None
    return mon34, publican, n


def apply_theofanie_otstupka(
    civil: date,
    apostol_week: int,
    weekday: int,
) -> tuple[int, int, list[str]] | None:
    """Herschaal tabelweken na week 33 tot Tollenaar-zondag (Theofanie-отступка).

    Weekdagen én zondagen met doorlopende week &gt; 33 gebruiken de vaste
    herhalingsreeks van lengte N (1..5). Eerdere weken blijven onaangeroerd.
    """
    del weekday  # zelfde mapping voor alle weekdagen in deze weken
    ctx = theofanie_otstupka_context(civil)
    if ctx is None:
        return None
    _mon34, _publican, n = ctx
    if apostol_week <= 33:
        return None
    k = apostol_week - 34
    seq = THEOFANIE_OTSTUPKA_WEEKEN[n]
    if k < 0 or k >= len(seq):
        return None
    mapped = seq[k]
    return mapped, mapped, ["R3", "R3-theofanie-otstupka"]


def _week_index_pascha(offset: int) -> tuple[int, int] | None:
    """(week, weekdag) in paasperiode; week 1 = Pascha-zondag … week 8 = Pinksteren."""
    if offset < 0 or offset > 49:
        return None
    week = offset // 7 + 1
    rem = offset % 7
    weekday = 7 if rem == 0 else rem
    return week, weekday


def _week_index_na_pinksteren(offset_from_pentecost: int) -> tuple[int, int] | None:
    """(week, weekdag) na Pinksteren; week 1 ma = Geestesmaandag, zo = Allerheiligen."""
    if offset_from_pentecost < 1:
        return None
    week = (offset_from_pentecost - 1) // 7 + 1
    weekday = (offset_from_pentecost - 1) % 7 + 1
    return week, weekday


def _week_index_triodion(offset: int) -> tuple[str, int, int] | None:
    """(periode, week, weekdag) voor Triodion/vasten (negatieve Pascha-offset).

    Tollenaar-zondag = -70 -> tabel week 33; Vergeving = -49 -> week 36;
    Grote Vasten week 1 ma = -48.
    """
    if offset == -70:
        return ("na_pinksteren", 33, 7)
    if offset == -63:
        return ("na_pinksteren", 34, 7)
    if offset == -56:
        return ("na_pinksteren", 35, 7)
    if offset == -49:
        return ("na_pinksteren", 36, 7)
    if -69 <= offset <= -64:
        return ("na_pinksteren", 34, offset + 70)
    if -62 <= offset <= -57:
        return ("na_pinksteren", 35, offset + 63)
    if -55 <= offset <= -50:
        return ("na_pinksteren", 36, offset + 56)
    if -48 <= offset <= -9:
        rel = offset - (-48)
        week = rel // 7 + 1
        weekday = rel % 7 + 1
        if week > 6:
            return None
        return ("vasten", week, weekday)
    if -6 <= offset <= -2:
        return ("vasten", 7, offset + 7)
    return None


def _pascha_anker_voor_civil(civil: date) -> date:
    """Pascha dat de lezingencyclus voor ``civil`` verankert.

    Vóór Tollenaar-zondag (Pascha − 70) hoort de dag nog bij de Pinksterreeks
    van het *vorige* Pascha; vanaf Tollenaar bij het komende Pascha.
    """
    pascha = orthodox_pascha(civil.year)
    publican = pascha + timedelta(days=-70)
    if civil < publican:
        return orthodox_pascha(civil.year - 1)
    if civil > pascha + timedelta(days=320):
        return orthodox_pascha(civil.year + 1)
    return pascha


def _ordinal_nl(n: int) -> str:
    return f"{n}e"


def week_kop_label(civil: date) -> str | None:
    """Korte weeknaam voor agenda-kop (maandag), of None."""
    pascha = _pascha_anker_voor_civil(civil)
    offset = (civil - pascha).days
    if 1 <= offset <= 6:
        return "Lichte Week"
    if 0 < offset < 49:
        week = offset // 7 + 1
        return f"{_ordinal_nl(week)} week van Pascha"
    pentecost = pascha + timedelta(days=49)
    if civil > pentecost:
        off_p = (civil - pentecost).days
        idx = _week_index_na_pinksteren(off_p)
        if idx:
            week, _wd = idx
            return f"{_ordinal_nl(week)} week na Pinksteren"
    if -48 <= offset <= -9:
        rel = offset - (-48)
        week = rel // 7 + 1
        return f"{_ordinal_nl(week)} week van de Grote Vasten"
    if -6 <= offset <= -2:
        return "Grote Week"
    if -69 <= offset <= -64:
        return "Week na de tollenaar"
    if -62 <= offset <= -57:
        return "Week van de verloren zoon"
    if -55 <= offset <= -50:
        return "Boterweek"
    return None


def liturgische_daglabel(
    jaar: int,
    mmdd: str,
    stijl: str = "nieuw",
    *,
    override_id: str | None = None,
) -> str:
    """Nederlandse aanduiding van de liturgische dag."""
    if (
        override_id
        and override_id in OVERRIDE_NAMEN
        and override_id not in MENAION_KOP_IDS
    ):
        return OVERRIDE_NAMEN[override_id]

    civil = _civil_date(jaar, mmdd, stijl)
    pascha = _pascha_anker_voor_civil(civil)

    offset = (civil - pascha).days
    weekday = _iso_weekday(civil)
    wd_name = WEEKDAG_NL[weekday]

    if override_id and override_id not in MENAION_KOP_IDS:
        return OVERRIDE_NAMEN.get(override_id, override_id)

    # Named Sundays by offset (fallback when no override)
    named = {
        0: "Pascha",
        7: "Thomaszondag",
        14: "Zondag van de myrondraagsters",
        21: "Zondag van de verlamde",
        24: "Midden-Pinksterfeest",
        28: "Zondag van de Samaritaanse",
        35: "Zondag van de blinde",
        39: "Hemelvaart",
        42: "Zondag van de heilige Vaderen",
        49: "Pinksteren",
        50: "Maandag van de Heilige Geest",
        56: "Allerheiligenzondag",
        63: "Zondag van de heiligen van de Lage Landen",
        -70: "Zondag van de tollenaar en de farizeeër",
        -63: "Zondag van de verloren zoon",
        -56: "Zondag van het Laatste Oordeel",
        -49: "Vergevingszondag",
        -8: "Lazaruszaterdag",
        -7: "Palmzondag",
        -3: "Heilige grote donderdag",
        -2: "Heilige grote vrijdag",
        -1: "Heilige grote zaterdag",
    }
    if offset in named:
        return named[offset]

    if 1 <= offset <= 6:
        return f"{wd_name} van de Lichte Week"
    if 0 < offset < 49 and weekday == 7:
        n = offset // 7 + 1  # 2..8
        return f"{_ordinal_nl(n)} zondag van Pascha"
    if 0 < offset < 49:
        week = offset // 7 + 1
        return f"{_ordinal_nl(week)} {wd_name.lower()} van Pascha"

    pentecost = pascha + timedelta(days=49)
    if civil >= pentecost:
        off_p = (civil - pentecost).days
        if off_p == 0:
            return "Pinksteren"
        week, wd = _week_index_na_pinksteren(off_p) or (0, 0)
        if week and wd == 7:
            return f"{_ordinal_nl(week)} zondag na Pinksteren"
        if week:
            return f"{_ordinal_nl(week)} {wd_name.lower()} na Pinksteren"

    if offset < 0:
        # Lent weekdays
        if -48 <= offset <= -9:
            rel = offset - (-48)
            week = rel // 7 + 1
            return f"{_ordinal_nl(week)} {wd_name.lower()} van de Grote Vasten"
        if -6 <= offset <= -2:
            return f"Heilige grote {wd_name.lower()}"
        if -70 < offset < 0 and weekday == 7:
            return "Zondag (Triodion)"

    return wd_name


def _lookup_weekreeks(
    periode: str,
    week: int,
    weekdag: int,
) -> dict[str, Any] | None:
    return load_weekreeks().get((periode, week, weekdag))


def _resolve_weekreeks(
    jaar: int,
    mmdd: str,
    stijl: str,
) -> LezingenResultaat | None:
    civil = _civil_date(jaar, mmdd, stijl)
    pascha = _pascha_anker_voor_civil(civil)

    offset = (civil - pascha).days
    pentecost = pascha + timedelta(days=49)
    regels = ["R3"]

    # --- Paasperiode inkl. Pinksteren ---
    if 0 <= offset <= 49:
        idx = _week_index_pascha(offset)
        if not idx:
            return None
        week, weekday = idx
        row = _lookup_weekreeks("pascha", week, weekday)
        if not row:
            return None
        return LezingenResultaat(
            apostel=_refs(row.get("apostel")),
            evangelie=_refs(row.get("evangelie")),
            regels=regels,
            daglabel=liturgische_daglabel(jaar, mmdd, stijl),
            toelichting="R3 paasperiode",
            status="gevonden",
        )

    # --- Na Pinksteren (tot Triodion) ---
    if civil > pentecost:
        off_p = (civil - pentecost).days
        idx = _week_index_na_pinksteren(off_p)
        if not idx:
            return None
        apostol_week, weekday = idx

        # Winter: Theofanie-отступка herschaalt tabelweken na week 33.
        theo = apply_theofanie_otstupka(civil, apostol_week, weekday)
        table_week_for_label = apostol_week
        if theo is not None:
            apostol_week, gospel_week, regels = theo
            table_week_for_label = apostol_week
        else:
            luke_mon = lucaanse_sprong_maandag(civil.year)
            gospel_week, regels = gospel_week_na_pinksteren(
                apostol_week, civil, luke_mon
            )

        a_row = _lookup_weekreeks("na_pinksteren", apostol_week, weekday)
        g_row = _lookup_weekreeks("na_pinksteren", gospel_week, weekday)
        if not a_row and not g_row:
            return None

        status = "gevonden"
        apostel = _refs((a_row or {}).get("apostel"))
        evangelie = _refs((g_row or {}).get("evangelie"))
        if (a_row or {}).get("status") == "geen_liturgie" and not apostel and not evangelie:
            status = "geen_liturgie"

        daglabel = liturgische_daglabel(jaar, mmdd, stijl)
        if theo is not None:
            wd_name = WEEKDAG_NL[weekday]
            daglabel = (
                f"{_ordinal_nl(table_week_for_label)} {wd_name.lower()} "
                "na Pinksteren (Theofanie-otstupka)"
            )

        return LezingenResultaat(
            apostel=apostel,
            evangelie=evangelie,
            regels=regels,
            daglabel=daglabel,
            toelichting="+".join(regels),
            status=status if (apostel or evangelie or status == "geen_liturgie") else "onbekend",
        )

    # --- Triodion / vasten ---
    if offset < 0:
        idx = _week_index_triodion(offset)
        if not idx:
            return None
        periode, week, weekday = idx
        row = _lookup_weekreeks(periode, week, weekday)
        if not row:
            return None
        if row.get("status") == "geen_liturgie":
            return LezingenResultaat(
                regels=["R4"],
                daglabel=liturgische_daglabel(jaar, mmdd, stijl),
                toelichting="Geen liturgie met Apostel/Evangelie van de dag",
                status="geen_liturgie",
            )
        return LezingenResultaat(
            apostel=_refs(row.get("apostel")),
            evangelie=_refs(row.get("evangelie")),
            regels=["R3"],
            daglabel=liturgische_daglabel(jaar, mmdd, stijl),
            toelichting="R3 triodion/vasten",
            status="gevonden",
        )

    return None


def _override_matches(
    ov: dict[str, Any],
    jaar: int,
    mmdd: str,
    stijl: str,
) -> bool:
    match = ov.get("match") or {}
    has_mmdd = "mmdd" in match
    has_off = "paascyclus_offset" in match
    has_off_in = "paascyclus_offset_in" in match
    rel = match.get("weekdag_relatief")

    if rel:
        civil = _civil_date(jaar, mmdd, stijl)
        rel_stijl = "oud" if stijl == "oud" else "nieuw"
        # Zondag ná Kerst kan op 1 januari vallen (ankerjaar − 1).
        # Zaterdag/zondag vóór Theofanie kan in december van het vorige
        # burgerlijke jaar vallen (ankerjaar + 1 t.o.v. die decemberdag).
        for y in (jaar - 1, jaar, jaar + 1):
            want = weekday_relative_date(
                y,
                str(rel["anker"]),
                int(rel["weekdag"]),
                int(rel.get("welke") or 1),
                str(rel["richting"]),
                stijl=rel_stijl,
            )
            if civil == want:
                return True
        return False

    if has_mmdd and has_off_in:
        offsets = [int(x) for x in (match.get("paascyclus_offset_in") or [])]
        for off in offsets:
            want = _mmdd_for_offset(jaar, off, stijl)
            if mmdd == str(match["mmdd"]) and mmdd == want:
                return True
        return False
    if has_mmdd and has_off:
        # Feestdatum valt op deze beweeglijke dag (bijv. Aankondiging × Pascha).
        want_off = _mmdd_for_offset(jaar, int(match["paascyclus_offset"]), stijl)
        return mmdd == str(match["mmdd"]) and mmdd == want_off
    if has_off:
        want = _mmdd_for_offset(jaar, int(match["paascyclus_offset"]), stijl)
        return want == mmdd
    if has_mmdd:
        return match["mmdd"] == mmdd
    return False


def _pick_override(
    jaar: int,
    mmdd: str,
    stijl: str,
    overrides: list[dict[str, Any]],
) -> dict[str, Any] | None:
    hits = [ov for ov in overrides if _override_matches(ov, jaar, mmdd, stijl)]
    if not hits:
        return None

    def sort_key(ov: dict[str, Any]) -> int:
        if ov.get("prioriteit") is not None:
            return int(ov["prioriteit"])
        return rang_prioriteit(str(ov.get("rang") or "groot"))

    hits.sort(key=sort_key, reverse=True)
    return hits[0]


def _resolve_modus(ov: dict[str, Any], civil: date) -> str:
    """Bepaal vervangen | toevoegen | negeren voor deze override + weekdag."""
    explicit = ov.get("modus")
    if explicit in {"vervangen", "toevoegen", "negeren"}:
        return str(explicit)
    rang = str(ov.get("rang") or "groot")
    default = default_modus_voor_rang(rang)
    if default != "auto":
        return default
    auto = load_rang_config().get("auto") or {}
    if civil.isoweekday() == 7:
        return str(auto.get("zondag") or "toevoegen")
    return str(auto.get("weekdag") or "vervangen")


def _rijadovoe_snapshot(basis: LezingenResultaat | None) -> dict[str, Any] | None:
    if basis is None or basis.status not in {"gevonden", "geen_liturgie"}:
        return None
    return {
        "apostel": [a.as_dict() for a in basis.apostel],
        "evangelie": [e.as_dict() for e in basis.evangelie],
        "status": basis.status,
        "regels": list(basis.regels),
    }


def resolve_lezingen(
    jaar: int,
    mmdd: str,
    stijl: str = "nieuw",
    *,
    overrides: list[dict[str, Any]] | None = None,
) -> LezingenResultaat:
    """Bepaal lezingen voor een kalenderdag.

    ``stijl``: ``nieuw`` (Gregoriaanse/wereldlijke MM-DD voor paascyclus) of
    ``oud`` (Juliaanse dagnaam voor paascyclus). Vaste MM-DD-overrides matchen
    altijd op de feestdatum-dagnaam.

    R5: bij feestoverride + bestaande rijádovoe geldt ``modus`` (vervangen /
    toevoegen / negeren), afgeleid van ``rang`` tenzij expliciet gezet.
    """
    parse_mmdd(mmdd)
    if stijl not in {"nieuw", "oud"}:
        raise ValueError(f"onbekende stijl {stijl!r}")

    ovs = overrides if overrides is not None else load_overrides()
    civil = _civil_date(jaar, mmdd, stijl)
    basis = _resolve_weekreeks(jaar, mmdd, stijl)
    ov = _pick_override(jaar, mmdd, stijl, ovs)

    if ov is None:
        if basis is not None and basis.status in {"gevonden", "geen_liturgie"}:
            if not basis.daglabel:
                basis.daglabel = liturgische_daglabel(jaar, mmdd, stijl)
            return basis
        return LezingenResultaat(
            status="onbekend",
            daglabel=liturgische_daglabel(jaar, mmdd, stijl),
            toelichting="Geen override en geen weekreeks-treffer.",
            regels=[],
        )

    oid = str(ov.get("id") or "")
    rang = str(ov.get("rang") or "groot")
    modus = _resolve_modus(ov, civil)
    feast_a = _refs(ov.get("apostel"))
    feast_e = _refs(ov.get("evangelie"))
    label = liturgische_daglabel(jaar, mmdd, stijl, override_id=oid)
    snap = _rijadovoe_snapshot(basis)
    base_ok = (
        basis is not None
        and basis.status == "gevonden"
        and (basis.apostel or basis.evangelie)
    )

    if modus == "negeren":
        if basis is not None and basis.status in {"gevonden", "geen_liturgie"}:
            out = basis
            out.daglabel = label or out.daglabel
            out.override_id = oid
            out.rang = rang
            out.modus = modus
            if "R5" not in out.regels:
                out.regels = list(out.regels) + ["R5"]
            out.toelichting = "R5 negeren: rijádovoe behouden"
            return out
        return LezingenResultaat(
            status="onbekend",
            daglabel=label,
            override_id=oid,
            rang=rang,
            modus=modus,
            toelichting="R5 negeren zonder rijádovoe",
        )

    if modus == "toevoegen" and base_ok:
        return LezingenResultaat(
            apostel=list(basis.apostel) + feast_a,
            evangelie=list(basis.evangelie) + feast_e,
            regels=["R3", "R2", "R5"],
            override_id=oid,
            daglabel=label,
            toelichting="R5 toevoegen: rijádovoe + feest",
            status="gevonden",
            rang=rang,
            modus=modus,
            rijadovoe=snap,
        )

    # vervangen (default), of toevoegen zonder bruikbare basis
    regels = [str(r) for r in (ov.get("regels") or ["R2"])]
    displaced = False
    if base_ok:
        displaced = [a.ref for a in feast_a] != [a.ref for a in basis.apostel] or [
            e.ref for e in feast_e
        ] != [e.ref for e in basis.evangelie]
    if displaced and "R5" not in regels:
        regels = list(regels) + ["R5"]
    return LezingenResultaat(
        apostel=feast_a,
        evangelie=feast_e,
        regels=regels,
        override_id=oid,
        daglabel=label,
        toelichting="R5 vervangen" if displaced else "+".join(regels),
        status="gevonden",
        rang=rang,
        modus="vervangen" if modus == "toevoegen" else modus,
        rijadovoe=snap if displaced else None,
    )


def parse_spec_voorbeelden(text: str | None = None) -> list[dict[str, Any]]:
    """Parse ```lezingen-voorbeeld```-blokken uit de normatieve spec."""
    if text is None:
        text = SPEC_PATH.read_text(encoding="utf-8")
    out: list[dict[str, Any]] = []
    for block in VOORBEELD_FENCE.findall(text):
        data = yaml.safe_load(block)
        if not isinstance(data, dict):
            raise ValueError("lezingen-voorbeeld moet een YAML-mapping zijn")
        if "id" not in data or "status" not in data:
            raise ValueError("lezingen-voorbeeld vereist id en status")
        out.append(data)
    return out


def spec_body_for_uitleg(text: str | None = None) -> str:
    """Spec-inhoud zonder de machine-leesbare voorbeeldsectie (die blijft in docs)."""
    if text is None:
        text = SPEC_PATH.read_text(encoding="utf-8")
    marker = "## Machine-leesbare voorbeelden"
    idx = text.find(marker)
    if idx < 0:
        body = text
    else:
        body = text[:idx].rstrip() + "\n"
    lines = body.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        if lines and lines[0].strip() == "":
            lines = lines[1:]
    return "\n".join(lines).rstrip() + "\n"


def resultaat_matches_verwacht(
    result: LezingenResultaat,
    verwacht: dict[str, Any],
) -> list[str]:
    """Return list of mismatch messages (empty = ok)."""
    errors: list[str] = []
    exp_a = [str(x["ref"]) for x in (verwacht.get("apostel") or [])]
    exp_e = [str(x["ref"]) for x in (verwacht.get("evangelie") or [])]
    got_a = [a.ref for a in result.apostel]
    got_e = [e.ref for e in result.evangelie]
    if got_a != exp_a:
        errors.append(f"apostel: got {got_a!r}, expected {exp_a!r}")
    if got_e != exp_e:
        errors.append(f"evangelie: got {got_e!r}, expected {exp_e!r}")
    exp_r = [str(r) for r in (verwacht.get("regels") or [])]
    if exp_r and list(result.regels) != exp_r:
        errors.append(f"regels: got {result.regels!r}, expected {exp_r!r}")
    return errors


def iter_year_mmdds(jaar: int, stijl: str) -> list[str]:
    """Alle geldige MM-DD in ``jaar`` voor de gekozen stijl."""
    out: list[str] = []
    if stijl == "nieuw":
        for month in range(1, 13):
            days = calendar.monthrange(jaar, month)[1]
            for day in range(1, days + 1):
                out.append(f"{month:02d}-{day:02d}")
        return out
    from kalender import julian_calendar_to_gregorian

    cursor = julian_calendar_to_gregorian(jaar, 1, 1)
    end = julian_calendar_to_gregorian(jaar + 1, 1, 1)
    while cursor < end:
        _jy, jm, jd = gregorian_to_julian_calendar(cursor)
        if _jy == jaar:
            out.append(f"{jm:02d}-{jd:02d}")
        cursor += timedelta(days=1)
    return out


def build_lezingen_dagen_payload(
    years: range | list[int],
    *,
    overrides: list[dict[str, Any]] | None = None,
    full_year: bool = True,
) -> dict[str, Any]:
    """Precompute lezingen: stijl → jaar → mmdd → resultaat (+ daglabel)."""
    ovs = overrides if overrides is not None else load_overrides()
    out: dict[str, Any] = {"nieuw": {}, "oud": {}}
    for stijl in ("nieuw", "oud"):
        by_year: dict[str, dict[str, Any]] = {}
        for year in years:
            by_mmdd: dict[str, Any] = {}
            if full_year:
                mmdds = iter_year_mmdds(year, stijl)
            else:
                mmdds = []
                for ov in ovs:
                    match = ov.get("match") or {}
                    if "paascyclus_offset" in match:
                        mmdds.append(
                            _mmdd_for_offset(
                                year, int(match["paascyclus_offset"]), stijl
                            )
                        )
                    elif "mmdd" in match:
                        mmdds.append(str(match["mmdd"]))
                mmdds = list(dict.fromkeys(mmdds))
            for mmdd in mmdds:
                try:
                    result = resolve_lezingen(year, mmdd, stijl, overrides=ovs)
                except ValueError:
                    continue
                if result.status == "onbekend" and not result.daglabel:
                    continue
                payload = result.as_dict()
                by_mmdd[mmdd] = payload
            if by_mmdd:
                by_year[str(year)] = by_mmdd
        out[stijl] = by_year
    return out
