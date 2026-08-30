"""Voeg een lokaal plaatje toe als icoon bij een bestaande heilige of feest.

Eerst: bestaat het bronbestand? Daarna licentie/rechten (PD, CC, of
toestemming van een parochie/klooster). Extra icoon = zelfde YAML, niet
een nieuw bestand naast de entry.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from iconen import icoon_bestand, iconen_van  # noqa: E402
from load_entries import load_yaml  # noqa: E402

MAX_ZIJDE = 1600
JPEG_KWALITEIT = 85
STATIC_ICONEN = ROOT / "site" / "static" / "iconen"
PAROCHIE = "parochie-toestemming"
STEM_RUIS = frozenset(
    {
        "muuricoon",
        "icoon",
        "iconen",
        "icon",
        "foto",
        "photo",
        "plaatje",
        "image",
        "img",
        "jpeg",
        "jpg",
        "png",
        "webp",
    }
)
GEEN_PLAATJE = {".yaml", ".yml", ".md", ".json", ".txt", ".py", ".cmd"}

# Canonieke weergave → herkenningsaliassen (lower).
LICENTIE_KEUZES: list[tuple[str, str, tuple[str, ...]]] = [
    ("1", "Publiek domein", ("publiek domein", "public domain", "pd", "pdm")),
    ("2", "CC0", ("cc0", "cc-0", "cc 0")),
    ("3", "CC BY 4.0", ("cc by 4.0", "cc-by 4.0", "cc-by-4.0", "cc by", "cc-by")),
    ("4", "CC BY-SA 4.0", ("cc by-sa 4.0", "cc-by-sa 4.0", "cc-by-sa-4.0", "cc by-sa", "cc-by-sa")),
]

NIET_HERBRUIKBAAR = "niet-herbruikbaar"


class Gestopt(Exception):
    """De gebruiker wil stoppen."""


class Fout(Exception):
    """Ontbrekende gegevens of ongeldige invoer."""


class Terminal:
    """Invoer: echte terminal, of voorgeprogrammeerde antwoorden (tests)."""

    def __init__(
        self,
        antwoorden: list[str] | None = None,
        *,
        niet_interactief: bool = False,
        stdin_fn: Callable[[str], str] | None = None,
    ) -> None:
        self.antwoorden = None if antwoorden is None else list(antwoorden)
        self.niet_interactief = niet_interactief
        self.stdin_fn = stdin_fn or input
        self.uitvoer: list[str] = []

    def zeg(self, tekst: str) -> None:
        print(tekst)
        self.uitvoer.append(tekst)

    def vraag(self, prompt: str) -> str:
        if self.niet_interactief and self.antwoorden is None:
            raise Fout(f"Ontbreekt (niet-interactief): {prompt.rstrip(': ')}")
        if self.antwoorden is not None:
            if not self.antwoorden:
                raise Fout(f"Geen antwoord meer voor: {prompt.rstrip(': ')}")
            waarde = self.antwoorden.pop(0).strip()
            self.zeg(f"{prompt}{waarde}")
            return waarde
        try:
            return self.stdin_fn(prompt).strip()
        except EOFError as exc:
            raise Gestopt("Geen invoer.") from exc

    def ja_nee(self, vraag: str, *, default: bool | None = None) -> bool:
        hint = "j/n"
        if default is True:
            hint = "J/n"
        elif default is False:
            hint = "j/N"
        while True:
            raw = self.vraag(f"{vraag} ({hint}): ").casefold()
            if not raw and default is not None:
                return default
            if raw in {"j", "ja", "y", "yes"}:
                return True
            if raw in {"n", "nee", "no"}:
                return False
            self.zeg("Antwoord met j of n.")


def _norm(tekst: str) -> str:
    t = tekst.strip().casefold()
    t = t.replace("—", "-").replace("–", "-")
    t = re.sub(r"\s+", " ", t)
    return t


def toestemming_licentie(tekst: str) -> bool:
    n = _norm(tekst)
    return n == PAROCHIE or n.startswith("toestemming van")


def canonical_licentie(tekst: str) -> str | None:
    n = _norm(tekst)
    if not n:
        return None
    for _nr, label, aliassen in LICENTIE_KEUZES:
        if n == _norm(label) or n in aliassen:
            return label
    return None


def licentie_is_herbruikbaar(tekst: str) -> bool:
    return canonical_licentie(tekst) is not None or toestemming_licentie(tekst)


def kies_licentie(term: Terminal) -> str:
    term.zeg("Welke licentie heeft dit plaatje?")
    for nr, label, _a in LICENTIE_KEUZES:
        term.zeg(f"  {nr}) {label}")
    term.zeg("  5) Toestemming van parochie of klooster")
    term.zeg("  6) Niet herbruikbaar of onbekend")
    term.zeg("  7) Anders (vrije tekst)")
    while True:
        keuze = term.vraag("Keuze [1-7]: ").casefold()
        if keuze in {"1", "2", "3", "4"}:
            for nr, label, _a in LICENTIE_KEUZES:
                if keuze == nr:
                    return label
        if keuze == "5":
            return PAROCHIE
        if keuze == "6":
            return NIET_HERBRUIKBAAR
        if keuze == "7":
            vrij = term.vraag("Licentie (vrije tekst): ")
            canon = canonical_licentie(vrij)
            if canon:
                return canon
            if toestemming_licentie(vrij):
                return vrij.strip()
            if not vrij:
                term.zeg("Lege licentie telt als niet herbruikbaar.")
                return NIET_HERBRUIKBAAR
            term.zeg(
                "Alleen publiek domein, CC0, CC BY, CC BY-SA of toestemming "
                "van een parochie/klooster mogen in de repo."
            )
            if term.ja_nee(
                "Valt deze licentie daaronder (herbruikbaar)?",
                default=False,
            ):
                return vrij.strip()
            return NIET_HERBRUIKBAAR
        term.zeg("Kies 1 tot en met 7.")


def verzamel_licentie(
    term: Terminal,
    cli_licentie: str | None,
) -> str:
    """Eerste stap: mag dit plaatje in de repo? Lus tot ja of stop."""
    pending = (cli_licentie or "").strip() or None
    while True:
        if pending is not None:
            raw = pending
            pending = None
            if licentie_is_herbruikbaar(raw):
                if toestemming_licentie(raw) and not canonical_licentie(raw):
                    return PAROCHIE if _norm(raw) == PAROCHIE else raw.strip()
                return canonical_licentie(raw) or raw.strip()
        elif term.niet_interactief:
            raise Fout(
                "Geen herbruikbare licentie. Geef --licentie "
                "(PD, CC0, CC BY, CC BY-SA of toestemming van een parochie)."
            )
        else:
            raw = kies_licentie(term)
            if raw != NIET_HERBRUIKBAAR:
                return canonical_licentie(raw) or raw.strip()
        term.zeg(
            "Dit plaatje mag niet in de repo. We nemen publiek domein, "
            "CC0, CC BY, CC BY-SA of toestemming van een parochie/klooster op."
        )
        if term.niet_interactief:
            raise Fout("Licentie is niet herbruikbaar; afgebroken.")
        if not term.ja_nee("Licentie of rechten wijzigen?", default=True):
            raise Gestopt("Gestopt: geen herbruikbare licentie.")


def vind_entry(root: Path, entry_id: str) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", entry_id):
        raise Fout(f"Ongeldig id: {entry_id!r}")
    gevonden = [
        p
        for p in (
            root / "data" / "heiligen" / f"{entry_id}.yaml",
            root / "data" / "feesten" / f"{entry_id}.yaml",
        )
        if p.is_file()
    ]
    if not gevonden:
        raise Fout(
            f"Geen heilige of feest met id {entry_id!r} "
            "(data/heiligen/ of data/feesten/)."
        )
    if len(gevonden) > 1:
        raise Fout(f"Id {entry_id!r} bestaat als heilige én feest.")
    return gevonden[0]


def entry_icoon_items(path: Path) -> list[dict]:
    data = load_yaml(path)
    if not isinstance(data, dict):
        return []
    return iconen_van(data)


def laad_plaatsen(root: Path) -> dict[str, dict[str, Any]]:
    path = root / "data" / "plaatsen.yaml"
    raw = load_yaml(path) if path.is_file() else {}
    items = (raw or {}).get("plaatsen") or []
    out: dict[str, dict[str, Any]] = {}
    for item in items:
        if isinstance(item, dict) and item.get("id"):
            out[str(item["id"])] = item
    return out


def score_tekst(query: str, *velden: str) -> int:
    q = _norm(query)
    if not q:
        return 0
    q_id = q.replace(" ", "-")
    q_tokens = [t for t in q.replace("-", " ").split() if t]
    best = 0
    for veld in velden:
        n = _norm(str(veld or ""))
        if not n:
            continue
        n_id = n.replace(" ", "-")
        n_tokens = [t for t in n.replace("-", " ").split() if t]
        if q == n or q_id == n_id:
            best = max(best, 100)
            continue
        if q_id in n_id or n_id in q_id or q in n or n in q:
            best = max(best, 80)
        if q_tokens and all(t in n_tokens or t in n_id for t in q_tokens):
            best = max(best, 85)
        elif q_tokens and sum(1 for t in q_tokens if t in n_id) >= 2:
            best = max(best, 60)
    return best


def wil_stoppen(tekst: str) -> bool:
    return _norm(tekst) in {"stop", "einde", "quit", "q"}


def zoek_entries(root: Path, query: str) -> list[tuple[int, str, str, str]]:
    """(score, id, weergavenaam, soort)."""
    treffers: dict[str, tuple[int, str, str, str]] = {}
    for sub in ("heiligen", "feesten"):
        folder = root / "data" / sub
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.yaml")):
            data = load_yaml(path)
            if not isinstance(data, dict):
                continue
            eid = str(data.get("id") or path.stem)
            namen = data.get("namen") or {}
            prim = str(namen.get("primair") or eid)
            alts = [str(a) for a in (namen.get("alternatief") or [])]
            soort = str(data.get("soort") or sub.rstrip("en"))
            sc = score_tekst(query, eid, prim, *alts)
            if sc:
                oud = treffers.get(eid)
                if oud is None or sc > oud[0]:
                    treffers[eid] = (sc, eid, prim, soort)
    return sorted(treffers.values(), key=lambda t: (-t[0], t[1]))


def zoek_plaatsen(
    plaatsen: dict[str, dict[str, Any]], query: str
) -> list[tuple[int, dict[str, Any]]]:
    treffers: list[tuple[int, dict[str, Any]]] = []
    for rec in plaatsen.values():
        alts = [str(a) for a in (rec.get("alternatief") or [])]
        sc = score_tekst(query, str(rec.get("id") or ""), str(rec.get("naam") or ""), *alts)
        if sc:
            treffers.append((sc, rec))
    treffers.sort(key=lambda t: (-t[0], str(t[1].get("id") or "")))
    return treffers


def query_zonder_plaats_en_ruis(query: str, plaats_ids: set[str]) -> str:
    """Strip plaats-id en woorden als muuricoon uit een zoekzin of stam."""
    tokens = [t for t in _norm(query).replace("-", " ").split() if t]
    if not tokens:
        return ""
    keep = [t for t in tokens if t not in plaats_ids and t not in STEM_RUIS]
    return " ".join(keep) if keep else " ".join(tokens)


def hints_uit_pad(pad: Path, plaatsen: dict[str, dict[str, Any]]) -> tuple[str, str | None]:
    """Zoekzin voor de entry, plus een plaats-id als die in de bestandsnaam zit."""
    stem = bron_stem(pad)
    tokens = [t for t in stem.split("-") if t]
    plaats_id = None
    rest: list[str] = []
    for token in tokens:
        if plaats_id is None and token in plaatsen:
            plaats_id = token
            continue
        if token in STEM_RUIS:
            continue
        rest.append(token)
    query = " ".join(rest) if rest else stem.replace("-", " ")
    return query, plaats_id


def parochie_bronregel(plaats: dict[str, Any]) -> str:
    pid = str(plaats.get("id") or "")
    naam = str(plaats.get("naam") or pid)
    if pid == "hemelum":
        return "Russisch Orthodox klooster van de H. Nicolaas te Hemelum"
    return f"Orthodoxe parochie te {naam}"


def _entry_weergave(path: Path) -> tuple[str, str, str]:
    eid = path.stem
    data = load_yaml(path) or {}
    naam = str((data.get("namen") or {}).get("primair") or eid)
    soort = str(data.get("soort") or "")
    return eid, naam, soort


def _probeer_direct(root: Path, query: str) -> Path | None:
    eid_guess = query.replace(" ", "-").casefold()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", eid_guess):
        return None
    try:
        return vind_entry(root, eid_guess)
    except Fout:
        return None


def bevestig_entry(
    term: Terminal,
    root: Path,
    query: str,
    *,
    niet_interactief: bool,
) -> str:
    q = (query or "").strip()
    plaats_ids = set(laad_plaatsen(root))
    while True:
        if not q:
            if niet_interactief:
                raise Fout("Id of naam ontbreekt.")
            q = term.vraag(
                "Heilige of feest (naam of id; leeg of stop = afbreken): "
            )
            if not q or wil_stoppen(q):
                raise Gestopt("Gestopt: geen entry gekozen.")
            continue
        schoon = query_zonder_plaats_en_ruis(q, plaats_ids)
        direct = _probeer_direct(root, q) or _probeer_direct(root, schoon)
        if direct is not None:
            eid, naam, soort = _entry_weergave(direct)
            if niet_interactief:
                return eid
            term.zeg(f"Gevonden: {naam} ({eid}, {soort}).")
            if term.ja_nee("Klopt dit?", default=True):
                return eid
            q = term.vraag(
                "Andere naam of id (leeg of stop = afbreken): "
            )
            if not q or wil_stoppen(q):
                raise Gestopt("Gestopt: geen entry gekozen.")
            continue
        treffers = zoek_entries(root, q)
        if not treffers and schoon and schoon != _norm(q):
            treffers = zoek_entries(root, schoon)
        if not treffers:
            if niet_interactief:
                raise Fout(f"Geen heilige of feest gevonden voor {q!r}.")
            term.zeg(
                f"Geen treffer voor {q!r}. Probeer een andere naam, "
                "of leeg/stop om af te breken."
            )
            q = term.vraag("Heilige of feest (naam of id): ")
            if not q or wil_stoppen(q):
                raise Gestopt("Gestopt: geen entry gekozen.")
            continue
        if niet_interactief:
            if len(treffers) == 1 or (
                treffers[0][0] >= 85
                and (len(treffers) == 1 or treffers[0][0] > treffers[1][0])
            ):
                return treffers[0][1]
            ids = ", ".join(t[1] for t in treffers[:5])
            raise Fout(f"Meerdere treffers voor {q!r}: {ids}. Geef --id.")
        if len(treffers) == 1:
            _sc, eid, naam, soort = treffers[0]
            term.zeg(f"Gevonden: {naam} ({eid}, {soort}).")
            if term.ja_nee("Klopt dit?", default=True):
                return eid
            q = term.vraag(
                "Andere naam of id (leeg of stop = afbreken): "
            )
            if not q or wil_stoppen(q):
                raise Gestopt("Gestopt: geen entry gekozen.")
            continue
        term.zeg("Treffers:")
        for i, (_sc, eid, naam, soort) in enumerate(treffers[:8], start=1):
            term.zeg(f"  {i}) {naam} ({eid}, {soort})")
        raw = term.vraag(
            "Keuze [nummer], andere naam, of stop: "
        )
        if not raw or wil_stoppen(raw):
            raise Gestopt("Gestopt: geen entry gekozen.")
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= min(8, len(treffers)):
                gekozen = treffers[idx - 1]
                term.zeg(f"Gekozen: {gekozen[2]} ({gekozen[1]}).")
                if term.ja_nee("Klopt dit?", default=True):
                    return gekozen[1]
                q = ""
                continue
            term.zeg("Dat nummer staat niet in de lijst.")
            continue
        q = raw


def kies_plaats(
    term: Terminal,
    plaatsen: dict[str, dict[str, Any]],
    query: str,
    *,
    verplicht: bool,
    niet_interactief: bool,
) -> dict[str, Any] | None:
    while True:
        q = (query or "").strip()
        if not q:
            if verplicht and niet_interactief:
                raise Fout(
                    "Geef --plaats (bijv. hemelum, groningen, zwolle, leeuwarden)."
                )
            if not verplicht:
                return None
            query = term.vraag(
                "Plaats van de parochie (leeg of stop = afbreken): "
            )
            if not query or wil_stoppen(query):
                raise Gestopt("Gestopt: geen plaats gekozen.")
            continue
        treffers = zoek_plaatsen(plaatsen, q)
        if not treffers:
            if niet_interactief:
                raise Fout(
                    f"Onbekende plaats {q!r}. Ids staan in data/plaatsen.yaml."
                )
            term.zeg(
                f"Geen plaats voor {q!r}. Probeer opnieuw, of leeg/stop."
            )
            query = term.vraag("Plaats: ")
            if not query or wil_stoppen(query):
                raise Gestopt("Gestopt: geen plaats gekozen.")
            continue
        rec = treffers[0][1]
        if niet_interactief:
            if treffers[0][0] < 70:
                raise Fout(f"Plaats {q!r} is niet eenduidig.")
            return rec
        naam = str(rec.get("naam") or rec.get("id"))
        pid = str(rec.get("id") or "")
        term.zeg(f"Plaats: {naam} ({pid}).")
        if term.ja_nee(
            "Klopt dit? (parochie of klooster waarvan het plaatje stamt)",
            default=True,
        ):
            return rec
        query = term.vraag("Andere plaats (leeg of stop = afbreken): ")
        if not query or wil_stoppen(query):
            raise Gestopt("Gestopt: geen plaats gekozen.")


def yaml_quote_icoon(waarde: str) -> str:
    if any(c in waarde for c in ":#{}[]&*?|>!%@`'\"\n"):
        escaped = waarde.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return waarde


def icoon_yaml_blok(items: list[dict[str, str]]) -> str:
    if not items:
        return ""
    extra = any(
        item.get("soort")
        or item.get("plaats")
        or item.get("toelichting")
        or item.get("primair")
        for item in items
    )
    q = yaml_quote_icoon

    def regels(icoon: dict[str, str], *, lijst: bool) -> list[str]:
        pref = "  - " if lijst else "  "
        nest = "    " if lijst else "  "
        lines = [f"{pref}bestand: {icoon['bestand']}"]
        if str(icoon.get("primair") or "") in {"true", "True"} or icoon.get("primair") is True:
            lines.append(f"{nest}primair: true")
        if icoon.get("soort"):
            lines.append(f"{nest}soort: {icoon['soort']}")
        if icoon.get("plaats"):
            lines.append(f"{nest}plaats: {icoon['plaats']}")
        lines.append(f"{nest}rechten: {icoon['rechten']}")
        lines.append(f"{nest}licentie: {q(str(icoon['licentie']))}")
        lines.append(f"{nest}bron: {q(str(icoon['bron']))}")
        if icoon.get("toelichting"):
            lines.append(f"{nest}toelichting: {q(str(icoon['toelichting']))}")
        return lines

    if len(items) == 1 and not extra:
        icoon = items[0]
        return "\n".join(
            [
                "icoon:",
                *regels(icoon, lijst=False),
                "",
            ]
        )
    lines = ["iconen:"]
    for icoon in items:
        lines.extend(regels(icoon, lijst=True))
    lines.append("")
    return "\n".join(lines)


def upsert_icoon_in_yaml(tekst: str, blok: str) -> str:
    if not tekst.endswith("\n"):
        tekst += "\n"
    if not blok.endswith("\n"):
        blok += "\n"
    for naam in ("iconen", "icoon"):
        pat = re.compile(rf"^{naam}:\n(?:[ \t].*\n)*", re.M)
        tekst = pat.sub("", tekst, count=1)
    datum = re.compile(r"^datum:\n(?:[ \t].*\n)*", re.M)
    match = datum.search(tekst)
    if match:
        return tekst[: match.end()] + blok + tekst[match.end() :]
    return tekst.rstrip() + "\n" + blok


def bron_stem(bron: Path) -> str:
    ruw = bron.stem.strip().casefold()
    ruw = ruw.replace("—", "-").replace("–", "-")
    ruw = re.sub(r"[^a-z0-9]+", "-", ruw).strip("-")
    if ruw and re.fullmatch(r"[a-z0-9][a-z0-9_-]*", ruw):
        return ruw
    return ""


def doel_bestand(
    entry_id: str,
    bron: Path,
    bestaande: list[str],
    plaats_id: str | None = None,
) -> str:
    """Eerste icoon: ``iconen/<id>.jpg``. Extra of parochiefoto: stam of ``<id>-<plaats>``."""
    gebruikt = {b.replace("\\", "/") for b in bestaande}
    if plaats_id:
        return f"iconen/{entry_id}-{plaats_id}.jpg"
    stem = bron_stem(bron)
    if not bestaande:
        return f"iconen/{entry_id}.jpg"
    if stem:
        return f"iconen/{stem}.jpg"
    n = 2
    naam = f"iconen/{entry_id}-{n}.jpg"
    while naam in gebruikt:
        n += 1
        naam = f"iconen/{entry_id}-{n}.jpg"
    return naam


def prepareer_plaatje(
    bron: Path,
    doel: Path,
    *,
    max_zijde: int = MAX_ZIJDE,
    kwaliteit: int = JPEG_KWALITEIT,
) -> tuple[int, int]:
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise Fout(
            "Pillow ontbreekt. Installeer met: pip install -r requirements.txt"
        ) from exc
    if not bron.is_file():
        raise Fout(f"Plaatje niet gevonden: {bron}")
    with Image.open(bron) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode in {"RGBA", "LA"} or (
            im.mode == "P" and "transparency" in im.info
        ):
            rgba = im.convert("RGBA")
            achter = Image.new("RGB", rgba.size, (0, 0, 0))
            achter.paste(rgba, mask=rgba.split()[-1])
            im = achter
        else:
            im = im.convert("RGB")
        b, h = im.size
        langste = max(b, h)
        if langste > max_zijde:
            schaal = max_zijde / langste
            im = im.resize(
                (max(1, round(b * schaal)), max(1, round(h * schaal))),
                Image.Resampling.LANCZOS,
            )
        doel.parent.mkdir(parents=True, exist_ok=True)
        im.save(doel, "JPEG", quality=kwaliteit, optimize=True)
        return im.size


def controleer_bronplaatje(pad: Path) -> Path:
    """Bestaand beeldbestand; YAML is geen icoon-bron."""
    p = pad.expanduser()
    if not p.is_absolute():
        p = Path.cwd() / p
    p = p.resolve(strict=False)
    suffix = p.suffix.lower()
    if suffix in GEEN_PLAATJE:
        raise Fout(
            f"{p} is geen plaatje ({suffix}).\n"
            "Een extra icoon hoort in dezelfde heilige- of feestyaml "
            "(veld iconen:), niet als nieuw yaml-bestand. "
            "Hemelum-foto van de Zondag van de heiligen van de Lage Landen: "
            "bron is jpg/png; doel is site/static/iconen/"
            "zondag-heiligen-lage-landen-hemelum.jpg in "
            "data/feesten/zondag-heiligen-lage-landen.yaml."
        )
    if p.is_dir():
        raise Fout(f"{p} is een map, geen plaatje.")
    if not p.is_file():
        raise Fout(
            f"Plaatje niet gevonden: {p}\n"
            "Geef een bestaand jpg/png-bestand (volledig pad of relatief "
            "ten opzichte van de repo-root)."
        )
    return p


def eis_bronplaatje(term: Terminal, cli: Path | None) -> Path:
    if cli is not None:
        return controleer_bronplaatje(cli)
    if term.niet_interactief:
        raise Fout("Geef het plaatje als pad (icoon foto.jpg) of --plaatje.")
    while True:
        raw = term.vraag("Pad naar het plaatje (leeg of stop = afbreken): ")
        if not raw or wil_stoppen(raw):
            raise Gestopt("Gestopt: geen plaatje.")
        try:
            return controleer_bronplaatje(Path(raw))
        except Fout as exc:
            term.zeg(f"Fout: {exc}")


def cli_plaatje(args: argparse.Namespace) -> Path | None:
    pos = args.plaatje_pos
    opt = args.plaatje_opt
    if pos is not None and opt is not None:
        raise Fout("Geef het plaatje als pad of als --plaatje, niet beide.")
    gekozen = opt if opt is not None else pos
    if gekozen is None:
        return None
    return gekozen.expanduser()


def verzamel_rest(
    term: Terminal,
    *,
    cli_id: str | None,
    plaatje: Path,
    cli_bron: str | None,
    cli_plaats: str | None,
    cli_toelichting: str | None,
    overschrijven: bool | None,
    parochie: bool,
    root: Path,
) -> tuple[str, Path, str, str, int | None, dict[str, str]]:
    plaatsen = laad_plaatsen(root)
    hint_query, hint_plaats = hints_uit_pad(plaatje, plaatsen)

    plaats_rec = None
    plaats_query = (cli_plaats or "").strip() or (hint_plaats or "")
    if parochie or plaats_query:
        if not plaats_query and not term.niet_interactief:
            plaats_query = term.vraag(
                "Plaats van de parochie (hemelum, groningen, zwolle, …): "
            )
        plaats_rec = kies_plaats(
            term,
            plaatsen,
            plaats_query,
            verplicht=parochie,
            niet_interactief=term.niet_interactief,
        )

    query = (cli_id or "").strip()
    if not query:
        if term.niet_interactief:
            raise Fout("Geef --id of een naam die uniek is.")
        suggestie = hint_query
        prompt = "Heilige of feest (naam of id): "
        if suggestie:
            term.zeg(f"Uit bestandsnaam: {suggestie}.")
        query = term.vraag(prompt)
        if not query and suggestie:
            query = suggestie
    entry_id = bevestig_entry(
        term, root, query, niet_interactief=term.niet_interactief
    )
    yaml_path = vind_entry(root, entry_id)

    bron = (cli_bron or "").strip()
    if not bron and plaats_rec is not None:
        bron = parochie_bronregel(plaats_rec)
        if not term.niet_interactief:
            term.zeg(f"Bronvoorstel: {bron}")
            andere = term.vraag("Bron [Enter = voorstel]: ")
            if andere:
                bron = andere
    if not bron:
        if term.niet_interactief:
            raise Fout("Geef --bron (bijv. Wikimedia Commons — File:… ).")
        bron = term.vraag(
            "Bron (bijv. Wikimedia Commons — File:… of korte fotobeschrijving): "
        )
    if not bron:
        raise Fout("Bron ontbreekt.")

    toelichting = (cli_toelichting or "").strip()
    if not toelichting and plaats_rec is not None and not term.niet_interactief:
        toelichting = term.vraag("Korte toelichting [Enter = overslaan]: ")

    extra: dict[str, str] = {}
    if plaats_rec is not None:
        extra["plaats"] = str(plaats_rec["id"])
        extra["soort"] = "foto"
        if toelichting:
            extra["toelichting"] = toelichting
    elif toelichting:
        extra["toelichting"] = toelichting

    items = entry_icoon_items(yaml_path)
    bestaande = [
        str(item.get("bestand") or "").replace("\\", "/").strip()
        for item in items
        if str(item.get("bestand") or "").strip()
    ]
    relatief = doel_bestand(
        entry_id, plaatje, bestaande, extra.get("plaats")
    )
    vervang_index: int | None = None
    if relatief in bestaande:
        vervang_index = bestaande.index(relatief)
        if overschrijven is False:
            raise Gestopt("Gestopt: bestaand icoon behouden.")
        if overschrijven is not True:
            if term.niet_interactief:
                raise Fout(
                    f"{relatief} staat al op deze entry. Gebruik --overschrijven."
                )
            if not term.ja_nee(
                f"{relatief} staat al op {entry_id}. Overschrijven?",
                default=False,
            ):
                raise Gestopt("Gestopt: bestaand icoon behouden.")
    return entry_id, plaatje, bron, relatief, vervang_index, extra


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="icoon",
        description=(
            "Voeg een lokaal plaatje toe als icoon bij een bestaande heilige "
            "of een bestaand feest. Naam mag in plaats van id; het script "
            "zoekt en vraagt bij één treffer J/n, anders een lijst, tot het "
            "klopt of u stopt (leeg, stop, q). Begint met: bestaat het plaatje?"
        ),
    )
    p.add_argument(
        "plaatje_pos",
        nargs="?",
        type=Path,
        metavar="PLAATJE",
        help="Pad naar het bronplaatje",
    )
    p.add_argument(
        "--id",
        help="Entry-id of naam (zoekt; geen treffer = opnieuw tot stop)",
    )
    p.add_argument(
        "--plaatje",
        dest="plaatje_opt",
        type=Path,
        metavar="PAD",
        help="Pad naar het bronplaatje (alternatief voor het losse pad)",
    )
    p.add_argument(
        "--licentie",
        help="PD, CC0, CC BY, CC BY-SA, of toestemming van een parochie",
    )
    p.add_argument("--bron", help="Bronregel voor het bijschrift")
    p.add_argument(
        "--plaats",
        help="Plaats-id of naam van de parochie (hemelum, groningen, …)",
    )
    p.add_argument("--toelichting", help="Korte bijschriftregel")
    p.add_argument(
        "--overschrijven",
        action="store_true",
        help="Icoon met dezelfde doelnaam vervangen zonder te vragen",
    )
    p.add_argument(
        "--niet-interactief",
        action="store_true",
        help="Niet vragen; ontbrekende gegevens zijn een fout",
    )
    p.add_argument(
        "--max-zijde",
        type=int,
        default=MAX_ZIJDE,
        help=f"Langste zijde in pixels (standaard {MAX_ZIJDE})",
    )
    p.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help=argparse.SUPPRESS,
    )
    args, extra = p.parse_known_args(argv)
    over = [a for a in extra if str(a).startswith("-")]
    paden = [Path(a) for a in extra if not str(a).startswith("-")]
    if over or len(paden) > 1:
        p.error("unrecognized arguments: " + " ".join(extra))
    if paden:
        if args.plaatje_pos is not None:
            p.error("unrecognized arguments: " + " ".join(extra))
        args.plaatje_pos = paden[0]
    return args


def run(args: argparse.Namespace, term: Terminal | None = None) -> int:
    term = term or Terminal(niet_interactief=args.niet_interactief)
    term.niet_interactief = args.niet_interactief
    try:
        plaatje = eis_bronplaatje(term, cli_plaatje(args))
        licentie = verzamel_licentie(term, args.licentie)
        parochie = toestemming_licentie(licentie)
        entry_id, plaatje, bron, relatief, vervang_index, extra = verzamel_rest(
            term,
            cli_id=args.id,
            plaatje=plaatje,
            cli_bron=args.bron,
            cli_plaats=args.plaats,
            cli_toelichting=args.toelichting,
            overschrijven=True if args.overschrijven else None,
            parochie=parochie,
            root=args.root,
        )
        if parochie and licentie == PAROCHIE:
            licentie = f"Toestemming van {bron}"
        yaml_path = vind_entry(args.root, entry_id)
        dest = STATIC_ICONEN
        if args.root != ROOT:
            dest = args.root / "site" / "static" / "iconen"
        dest_file = dest / Path(relatief).name
        breed, hoog = prepareer_plaatje(
            plaatje,
            dest_file,
            max_zijde=args.max_zijde,
        )
        nieuw = {
            "bestand": relatief,
            "rechten": "ok",
            "licentie": licentie,
            "bron": bron,
            **extra,
        }
        items: list[dict[str, str]] = []
        for item in entry_icoon_items(yaml_path):
            if not icoon_bestand(item):
                continue
            kopie = {
                "bestand": icoon_bestand(item),
                "rechten": str(item.get("rechten") or "ok"),
                "licentie": str(item.get("licentie") or ""),
                "bron": str(item.get("bron") or ""),
            }
            for key in ("soort", "plaats", "toelichting"):
                if item.get(key):
                    kopie[key] = str(item[key])
            if item.get("primair") is True:
                kopie["primair"] = True  # type: ignore[assignment]
            items.append(kopie)
        if vervang_index is not None:
            items[vervang_index] = nieuw
        else:
            items.append(nieuw)
        if len(items) > 1 and not any(i.get("primair") is True for i in items):
            items[0]["primair"] = True  # type: ignore[assignment]
        tekst = yaml_path.read_text(encoding="utf-8")
        yaml_path.write_text(
            upsert_icoon_in_yaml(tekst, icoon_yaml_blok(items)),
            encoding="utf-8",
            newline="\n",
        )
        term.zeg(
            f"Icoon gezet: {yaml_path.relative_to(args.root)} → {relatief} "
            f"({breed}×{hoog} px)."
        )
        return 0
    except Gestopt as exc:
        term.zeg(str(exc) or "Gestopt.")
        return 2
    except Fout as exc:
        term.zeg(f"Fout: {exc}")
        return 1


def main(argv: list[str] | None = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
