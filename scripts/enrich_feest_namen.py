"""Vul namen.alternatief op feesten (orthodoxe NL-benamingen)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FEESTEN = ROOT / "data" / "feesten"

# Gangbare andere benamingen (niet: Theofanie≠Transfiguratie/Verheerlijking).
EXTRA: dict[str, list[str]] = {
    "aankondiging": [
        "Aankondiging",
        "Annunciatie",
        "Evangelismos",
        "Aankondiging aan de Theotokos",
    ],
    "allerheiligen-zondag": ["Zondag van Alle Heiligen", "Allerheiligen"],
    "zondag-heiligen-lage-landen": [
        "Zondag van de heiligen van de lokale Kerk",
        "Tweede zondag na Pinksteren",
        "Zondag na Allerheiligen",
    ],
    "allerzielen-zaterdag-pinksteren": [
        "Allerzielen-zaterdag",
        "Zaterdag van de zielen (vóór Pinksteren)",
    ],
    "begin-kerkelijk-jaar": ["Indictie", "Kerkelijk nieuwjaar", "1 september"],
    "besnijdenis-des-heren": ["Besnijdenis", "Besnijdenis van Christus"],
    "geboorte-johannes-doper": [
        "Geboorte van Johannes de Voorloper",
        "Geboorte van de Voorloper",
    ],
    "geboorte-moeder-gods": ["Geboorte van de Theotokos", "Maria Geboorte"],
    "geestesmaandag": [
        "Maandag van de Geest",
        "Dag van de Heilige Geest",
        "Pinkstermaandag",
    ],
    "grote-dinsdag": ["Heilige en Grote Dinsdag"],
    "grote-donderdag": [
        "Heilige en Grote Donderdag",
        "Witte Donderdag",
        "Donderdag van het Mysterie",
    ],
    "grote-maandag": ["Heilige en Grote Maandag"],
    "grote-vrijdag": ["Heilige en Grote Vrijdag", "Goede Vrijdag"],
    "grote-woensdag": ["Heilige en Grote Woensdag"],
    "grote-zaterdag": ["Heilige en Grote Zaterdag"],
    "hemelvaart": ["Hemelvaart", "Hemelvaartsdag"],
    "kerst": [
        "Kerstfeest",
        "Geboorte van Christus",
        "Geboorte des Heren",
        "Kerstmis",
    ],
    "kruisverheffing": [
        "Verheffing van het Heilig Kruis",
        "Universele Kruisverheffing",
    ],
    "lazarus-zaterdag": ["Opwekking van Lazarus"],
    "lichte-maandag": ["Maandag van de Lichte Week"],
    "midden-pinksterfeest": ["Mid-Pinksteren", "Middenfeest"],
    "onthoofding-johannes-doper": [
        "Onthoofding van Johannes de Voorloper",
        "Onthoofding van de Voorloper",
    ],
    "ontmoeting-in-de-tempel": [
        "Ontmoeting",
        "Ontmoeting des Heren",
        "Hypapante",
        "Opdracht in de tempel",
    ],
    "ontslapen-moeder-gods": [
        "Ontslapen",
        "Ontslapen van de Theotokos",
        "Maria Tenhemelopneming",
    ],
    "palmzondag": ["Palmzondag", "Intocht in Jeruzalem", "Vaienzondag"],
    "pascha": [
        "Pascha",
        "Heilige Opstanding",
        "Opstanding van Christus",
        "Orthodox Pasen",
        "Feest van de Opstanding",
    ],
    "petrus-en-paulus": [
        "Petrus en Paulus",
        "Feest van de apostelen Petrus en Paulus",
    ],
    "pinksteren": [
        "Pinksteren",
        "Nederdaling van de Heilige Geest",
        "Feest van de Drie-eenheid",
        "Drie-eenheidsfeest",
    ],
    "schone-maandag": ["Schone Maandag", "Begin van de Grote Vasten"],
    "tempelgang-moeder-gods": [
        "Tempelgang",
        "Intocht van de Moeder Gods in de tempel",
        "Tempelgang van de Theotokos",
    ],
    "teruggave-pascha": [
        "Apodosis van Pascha",
        "Afscheid van Pascha",
        "Teruggave van Pasen",
    ],
    "theofanie": [
        "Theofanie",
        "Doop des Heren",
        "Doop van Christus",
        "Epifanie",
        "Openbaring des Heren",
    ],
    "thomaszondag": [
        "Thomaszondag",
        "Antipascha",
        "Zondag van de ongelovige Thomas",
        "Zondag van Thomas",
    ],
    "transfiguratie": [
        "Transfiguratie",
        "Verheerlijking",
        "Verheerlijking op de berg Thabor",
        "Verheerlijking des Heren",
    ],
    "vergevingszondag": [
        "Vergevingszondag",
        "Zuivelvaarwel",
        "Zondag van de verdrijving uit het paradijs",
    ],
    "zacheus-zondag": ["Zacheüszondag", "Zondag van Zacheüs"],
    "zaterdag-allerzielen-vleesmijding": [
        "Allerzielen-zaterdag",
        "Zaterdag vóór Vleesvaarwel",
    ],
    "zondag-blinde": [
        "Zondag van de blindgeborene",
        "Zondag van de genezing van de blinde",
    ],
    "zondag-gregorius-palamas": [
        "Zondag van Gregorius Palamas",
        "Tweede zondag van de Vasten",
    ],
    "zondag-johannes-klimacus": [
        "Zondag van Johannes Klimacus",
        "Vierde zondag van de Vasten",
    ],
    "zondag-kruisverering": [
        "Zondag van de Kruisverering",
        "Kruisverering",
        "Derde zondag van de Vasten",
    ],
    "zondag-laatste-oordeel": [
        "Zondag van het Laatste Oordeel",
        "Vleesvaarwel",
        "Vleesvaarwelzondag",
    ],
    "zondag-maria-van-egypte": [
        "Zondag van Maria van Egypte",
        "Vijfde zondag van de Vasten",
    ],
    "zondag-myrondraagsters": [
        "Myrondraagsterszondag",
        "Zondag van de myrrhedraagsters",
    ],
    "zondag-orthodoxie": [
        "Zondag van de Orthodoxie",
        "Eerste zondag van de Vasten",
        "Orthodoxiezondag",
    ],
    "zondag-samaritaanse": [
        "Zondag van de Samaritaanse",
        "Zondag van de Samaritaanse vrouw bij de put",
    ],
    "zondag-tollenaar-en-farizeeer": [
        "Zondag van de tollenaar en Farizeeër",
        "Tollenaar en Farizeeër",
    ],
    "zondag-vaderen-eerste-concilie": [
        "Zondag van de Vaderen van Nicea",
        "Zondag van de 318 Vaderen",
    ],
    "zondag-verlamde": [
        "Zondag van de verlamde man",
        "Zondag van de genezing van de verlamde",
    ],
    "zondag-verloren-zoon": ["Verloren zoon", "Zondag van de verloren zoon"],
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().casefold())


def from_primair(primair: str) -> list[str]:
    """Haal korte vorm uit 'X (Y)'; Y alleen als het een echte naam is."""
    m = re.fullmatch(r"(.+?)\s*\((.+)\)\s*", primair.strip())
    if not m:
        return []
    outer, inner = m.group(1).strip(), m.group(2).strip()
    out = [outer]
    low = inner.casefold()
    if not low.startswith(("vóór ", "voor ", "op de ", "begin ")):
        out.append(inner)
    return out


def is_junk_alt(name: str) -> bool:
    low = name.casefold().strip()
    if low.startswith(("vóór ", "voor ", "op de ")):
        return True
    if low in {"bright monday", "dormition", "afscheid van pascha"}:
        return True
    return False


def merge_alts(primair: str, existing: list[str], extras: list[str]) -> list[str]:
    seen = {norm(primair)}
    result: list[str] = []
    for name in existing + extras:
        n = name.strip()
        if not n or is_junk_alt(n):
            continue
        key = norm(n)
        if key in seen:
            continue
        seen.add(key)
        result.append(n)
    return result


def yaml_scalar(s: str) -> str:
    if (
        re.search(r"[:#{}[\],&*?|>!%@`]", s)
        or "(" in s
        or ")" in s
        or "'" in s
        or '"' in s
        or s != s.strip()
    ):
        return json.dumps(s, ensure_ascii=False)
    return s


def rewrite_namen_block(text: str, primair: str, alts: list[str]) -> str:
    m = re.search(r"(?m)^namen:\n", text)
    if not m:
        raise SystemExit("geen namen-blok")
    start = m.start()
    rest = text[m.end() :]
    m2 = re.search(r"(?m)^[a-zA-Z_][a-zA-Z0-9_]*:", rest)
    end = m.end() + m2.start() if m2 else len(text)
    lines = ["namen:\n", f"  primair: {yaml_scalar(primair)}\n"]
    if alts:
        lines.append("  alternatief:\n")
        for a in alts:
            lines.append(f"  - {yaml_scalar(a)}\n")
    return text[:start] + "".join(lines) + text[end:]


def main() -> None:
    changed = 0
    for path in sorted(FEESTEN.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        namen = data.get("namen") or {}
        primair = namen.get("primair") or ""
        existing = list(namen.get("alternatief") or [])
        extras = from_primair(primair) + EXTRA.get(path.stem, [])
        alts = merge_alts(primair, existing, extras)
        if alts == existing:
            continue
        path.write_text(
            rewrite_namen_block(text, primair, alts), encoding="utf-8", newline="\n"
        )
        print(f"{path.stem}: {alts}")
        changed += 1
    print(f"done, {changed} files")


if __name__ == "__main__":
    main()
