"""Laden en normaliseren van YAML-entries."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from kalender import normalize_dates, parse_mmdd

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
ENTRY_SUBDIRS = ("feesten", "heiligen", "vasten")


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_bronnen() -> dict[str, dict[str, Any]]:
    path = DATA_ROOT / "bronnen" / "bronnen.yaml"
    raw = load_yaml(path) or {}
    items = raw.get("bronnen") or []
    out: dict[str, dict[str, Any]] = {}
    for item in items:
        bron_id = item["id"]
        out[bron_id] = item
    return out


def iter_entry_files() -> list[Path]:
    files: list[Path] = []
    for sub in ENTRY_SUBDIRS:
        folder = DATA_ROOT / sub
        if folder.is_dir():
            files.extend(sorted(folder.glob("*.yaml")))
    return files


def load_raw_entries() -> list[tuple[Path, dict[str, Any]]]:
    result: list[tuple[Path, dict[str, Any]]] = []
    for path in iter_entry_files():
        data = load_yaml(path)
        if not isinstance(data, dict):
            raise ValueError(f"{path}: root moet een mapping zijn")
        result.append((path, data))
    return result


def _resolve_referenties(
    entry: dict[str, Any],
    bronnen: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    refs = list(entry.get("referenties") or [])
    resolved: list[dict[str, Any]] = []
    for ref in refs:
        item = dict(ref)
        bron_id = item.get("bron_id")
        if bron_id:
            bron = bronnen.get(bron_id)
            if not bron:
                raise ValueError(f"Onbekende bron_id: {bron_id}")
            item.setdefault("label", bron.get("naam") or bron_id)
            if bron.get("url") and "url" not in item:
                item["url"] = bron["url"]
        resolved.append(item)
    return resolved


def _stijl(datum: dict[str, Any], path: Path) -> str:
    stijl = (datum.get("stijl") or "gregoriaans").strip().lower()
    if stijl not in {"gregoriaans", "juliaans"}:
        raise ValueError(f"{path}: onbekende stijl {stijl!r}")
    return stijl


def normalize_entry(
    path: Path,
    raw: dict[str, Any],
    bronnen: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    entry = dict(raw)
    entry_id = entry.get("id") or path.stem
    entry["id"] = entry_id
    if not ID_RE.match(entry_id):
        raise ValueError(f"{path}: ongeldige id {entry_id!r}")

    soort = entry.get("soort")
    if soort not in {"heilige", "feest", "vasten"}:
        raise ValueError(f"{path}: onbekende soort {soort!r}")

    datum = dict(entry.get("datum") or {})
    cyclus = entry.get("cyclus")
    if not cyclus:
        if datum.get("weekdagen"):
            cyclus = "wekelijks"
        elif datum.get("paascyclus"):
            cyclus = "paascyclus"
        else:
            cyclus = "jaar"
    entry["cyclus"] = cyclus
    paas = datum.get("paascyclus")
    weekdagen = datum.get("weekdagen")

    if weekdagen:
        if cyclus != "wekelijks":
            raise ValueError(f"{path}: datum.weekdagen vereist cyclus: wekelijks")
        days = sorted({int(d) for d in weekdagen})
        if any(d < 1 or d > 7 for d in days):
            raise ValueError(f"{path}: weekdagen moeten 1–7 (ISO) zijn")
        entry["datum_norm"] = {
            "stijl": _stijl(datum, path),
            "feestdatum": None,
            "weekdagen": days,
            "vorm": "weekdagen",
        }
        entry["datum_extra_norm"] = []
    elif paas:
        if cyclus != "paascyclus":
            raise ValueError(f"{path}: datum.paascyclus vereist cyclus: paascyclus")
        anker = paas.get("anker") or "pascha"
        if anker != "pascha":
            raise ValueError(f"{path}: alleen anker 'pascha' wordt ondersteund")
        stijl = _stijl(datum, path)
        if "offset_dagen" in paas:
            offset = int(paas["offset_dagen"])
            entry["datum_norm"] = {
                "stijl": stijl,
                "feestdatum": None,
                "paascyclus_offset": offset,
                "paascyclus_anker": anker,
                "vorm": "dag",
            }
        elif "van_offset_dagen" in paas:
            van_o = int(paas["van_offset_dagen"])
            if "tot_offset_dagen" in paas:
                tot_o = int(paas["tot_offset_dagen"])
                entry["datum_norm"] = {
                    "stijl": stijl,
                    "feestdatum": None,
                    "paascyclus_offset": van_o,
                    "paascyclus_anker": anker,
                    "van_offset_dagen": van_o,
                    "tot_offset_dagen": tot_o,
                    "vorm": "periode",
                }
            elif datum.get("tot"):
                parse_mmdd(datum["tot"])
                entry["datum_norm"] = {
                    "stijl": stijl,
                    "feestdatum": None,
                    "paascyclus_offset": van_o,
                    "paascyclus_anker": anker,
                    "van_offset_dagen": van_o,
                    "tot_mmdd": datum["tot"],
                    "vorm": "periode_hybride",
                }
            else:
                raise ValueError(
                    f"{path}: paascyclus.van_offset_dagen vereist "
                    "tot_offset_dagen of datum.tot"
                )
        else:
            raise ValueError(f"{path}: paascyclus zonder bruikbare offsets")
        entry["datum_extra_norm"] = []
    elif datum.get("weekdag_relatief"):
        rel = datum["weekdag_relatief"]
        if not isinstance(rel, dict):
            raise ValueError(f"{path}: datum.weekdag_relatief moet een mapping zijn")
        anker = str(rel.get("anker") or "").strip()
        parse_mmdd(anker)
        weekdag = int(rel.get("weekdag"))
        if weekdag < 1 or weekdag > 7:
            raise ValueError(f"{path}: weekdag_relatief.weekdag moet 1–7 zijn")
        welke = int(rel.get("welke") or 1)
        if welke < 1:
            raise ValueError(f"{path}: weekdag_relatief.welke moet ≥ 1 zijn")
        richting = str(rel.get("richting") or "").strip()
        if richting not in {"voor", "na"}:
            raise ValueError(
                f"{path}: weekdag_relatief.richting moet 'voor' of 'na' zijn"
            )
        entry["datum_norm"] = {
            "stijl": _stijl(datum, path),
            "feestdatum": None,
            "vorm": "weekdag_relatief",
            "anker": anker,
            "weekdag": weekdag,
            "welke": welke,
            "richting": richting,
        }
        entry["datum_extra_norm"] = []
    elif datum.get("van") and datum.get("tot"):
        if cyclus not in {"jaar", "wekelijks"}:
            # vaste jaarcyclus-periode
            pass
        parse_mmdd(datum["van"])
        parse_mmdd(datum["tot"])
        entry["datum_norm"] = {
            "stijl": _stijl(datum, path),
            "feestdatum": datum["van"],
            "van": datum["van"],
            "tot": datum["tot"],
            "vorm": "periode",
        }
        entry["datum_extra_norm"] = []
    else:
        if "waarde" not in datum:
            raise ValueError(f"{path}: datum.waarde ontbreekt")
        stijl = datum.get("stijl") or "gregoriaans"
        dates = normalize_dates(datum["waarde"], stijl)
        if datum.get("gregoriaans"):
            parse_mmdd(datum["gregoriaans"])
            dates["gregoriaans"] = datum["gregoriaans"]
        if datum.get("juliaans"):
            parse_mmdd(datum["juliaans"])
            dates["juliaans"] = datum["juliaans"]
        dates["vorm"] = "dag"
        entry["datum_norm"] = dates

        extra_norm: list[dict[str, Any]] = []
        for extra in datum.get("extra") or []:
            e_stijl = extra.get("stijl") or stijl
            e_dates = normalize_dates(extra["waarde"], e_stijl)
            extra_norm.append(
                {
                    **e_dates,
                    "toelichting": extra.get("toelichting") or "",
                }
            )
        entry["datum_extra_norm"] = extra_norm

    entry["referenties"] = _resolve_referenties(entry, bronnen)
    bronlaag = entry.get("bronlaag") or "encyclopedie"
    if bronlaag not in {"nagekeken", "encyclopedie"}:
        raise ValueError(f"{path}: onbekende bronlaag {bronlaag!r}")
    entry["bronlaag"] = bronlaag
    betekenis = entry.get("betekenis_lage_landen")
    entry["betekenis_lage_landen"] = (
        str(betekenis).strip() if betekenis is not None else ""
    )
    betekenis_feest = entry.get("betekenis")
    entry["betekenis"] = (
        str(betekenis_feest).strip() if betekenis_feest is not None else ""
    )
    raw_goed = entry.get("goedkeuring") or []
    if raw_goed and not isinstance(raw_goed, list):
        raise ValueError(f"{path}: goedkeuring moet een lijst zijn")
    goed: list[dict[str, str]] = []
    for i, item in enumerate(raw_goed):
        if not isinstance(item, dict):
            raise ValueError(f"{path}: goedkeuring[{i}] moet een mapping zijn")
        naam = str(item.get("naam") or "").strip()
        if not naam:
            raise ValueError(f"{path}: goedkeuring[{i}].naam ontbreekt")
        rec: dict[str, str] = {"naam": naam}
        org = str(item.get("organisatie") or "").strip()
        if org:
            rec["organisatie"] = org
        opm = str(item.get("opmerking") or "").strip()
        if opm:
            rec["opmerking"] = opm
        dat = str(item.get("datum") or "").strip()
        if dat:
            rec["datum"] = dat
        goed.append(rec)
    entry["goedkeuring"] = goed
    aliases = entry.get("id_aliassen") or []
    if not isinstance(aliases, list):
        raise ValueError(f"{path}: id_aliassen moet een lijst zijn")
    entry["id_aliassen"] = [str(a).strip() for a in aliases if str(a).strip()]
    locs = entry.get("locaties") or []
    if not isinstance(locs, list):
        raise ValueError(f"{path}: locaties moet een lijst zijn")
    entry["locaties"] = [str(x).strip() for x in locs if str(x).strip()]
    rust = entry.get("rustplaats")
    if rust:
        if not isinstance(rust, dict):
            raise ValueError(f"{path}: rustplaats moet een mapping zijn")
        plaats = str(rust.get("plaats") or "").strip()
        toel = str(rust.get("toelichting") or "").strip()
        if not plaats:
            raise ValueError(f"{path}: rustplaats.plaats ontbreekt")
        entry["rustplaats"] = {"plaats": plaats, "toelichting": toel}
    else:
        entry["rustplaats"] = None
    if entry.get("soort") == "heilige":
        sel = entry.get("selectie") or "nader-onderzoek"
        allowed = {"voldoet", "nader-onderzoek", "kandidaat-schrappen"}
        if sel not in allowed:
            raise ValueError(f"{path}: onbekende selectie {sel!r}")
        entry["selectie"] = sel
        toel = entry.get("selectie_toelichting")
        entry["selectie_toelichting"] = str(toel).strip() if toel else ""
    entry["lage_landen"] = bool(
        entry.get("lage_landen", entry.get("soort") == "heilige")
    )
    entry["observances"] = list(entry.get("observances") or [])
    if not entry["observances"]:
        if entry["soort"] == "heilige":
            entry["observances"] = ["heilige"]
        elif entry["soort"] == "vasten":
            entry["observances"] = ["vasten"]
        else:
            entry["observances"] = ["feest"]
    entry["onderdrukt_wekelijks_vasten"] = bool(
        entry.get("onderdrukt_wekelijks_vasten")
    )
    niveau = entry.get("vastenniveau")
    if niveau is not None:
        allowed = {"streng", "wijn_olie", "vis", "lichter", "vrij"}
        if niveau not in allowed:
            raise ValueError(f"{path}: onbekend vastenniveau {niveau!r}")
        entry["vastenniveau"] = niveau
        if niveau == "vrij":
            entry["onderdrukt_wekelijks_vasten"] = True
    # Vastenperiode vervangt wo/vr als aparte observantie.
    if entry["soort"] == "vasten" and (entry.get("cyclus") or "jaar") != "wekelijks":
        entry["onderdrukt_wekelijks_vasten"] = True
    entry["source_path"] = str(path.relative_to(REPO_ROOT)).replace("\\", "/")

    namen = dict(entry.get("namen") or {})
    primair = str(namen.get("primair") or "").strip()
    if not primair:
        raise ValueError(f"{path}: namen.primair ontbreekt")
    alts = [
        str(a).strip()
        for a in (namen.get("alternatief") or [])
        if str(a).strip() and str(a).strip().casefold() != primair.casefold()
    ]
    entry["namen"] = {"primair": primair, "alternatief": alts}
    return entry


def _sort_key(entry: dict[str, Any]) -> tuple:
    dn = entry["datum_norm"]
    vorm = dn.get("vorm") or "dag"
    if entry.get("cyclus") == "wekelijks":
        return (2, tuple(dn.get("weekdagen") or []), entry["id"])
    if entry.get("cyclus") == "paascyclus":
        return (1, dn.get("paascyclus_offset") or 0, entry["id"])
    if vorm == "periode":
        return (0, dn.get("van") or dn.get("feestdatum") or "", 0, "", entry["id"])
    if vorm == "weekdag_relatief":
        return (
            0,
            dn.get("anker") or "",
            int(dn.get("welke") or 1),
            dn.get("richting") or "",
            entry["id"],
        )
    return (0, dn.get("feestdatum") or "", 0, "", entry["id"])


def load_entries() -> list[dict[str, Any]]:
    bronnen = load_bronnen()
    entries = [
        normalize_entry(path, raw, bronnen)
        for path, raw in load_raw_entries()
    ]
    ids = [e["id"] for e in entries]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"Dubbele id's: {sorted(dupes)}")
    return sorted(entries, key=_sort_key)
