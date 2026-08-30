"""Voeg een lokaal plaatje toe als icoon bij een bestaande heilige of feest.

Eerst licentie/rechten: alleen PD, CC0, CC BY of CC BY-SA komen in de repo.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import load_yaml  # noqa: E402

MAX_ZIJDE = 1600
JPEG_KWALITEIT = 85
STATIC_ICONEN = ROOT / "site" / "static" / "iconen"

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


def canonical_licentie(tekst: str) -> str | None:
    n = _norm(tekst)
    if not n:
        return None
    for _nr, label, aliassen in LICENTIE_KEUZES:
        if n == _norm(label) or n in aliassen:
            return label
    return None


def licentie_is_herbruikbaar(tekst: str) -> bool:
    return canonical_licentie(tekst) is not None


def kies_licentie(term: Terminal) -> str:
    term.zeg("Welke licentie heeft dit plaatje?")
    for nr, label, _a in LICENTIE_KEUZES:
        term.zeg(f"  {nr}) {label}")
    term.zeg("  5) Niet herbruikbaar of onbekend")
    term.zeg("  6) Anders (vrije tekst)")
    while True:
        keuze = term.vraag("Keuze [1-6]: ").casefold()
        if keuze in {"1", "2", "3", "4"}:
            for nr, label, _a in LICENTIE_KEUZES:
                if keuze == nr:
                    return label
        if keuze == "5":
            return NIET_HERBRUIKBAAR
        if keuze == "6":
            vrij = term.vraag("Licentie (vrije tekst): ")
            canon = canonical_licentie(vrij)
            if canon:
                return canon
            if not vrij:
                term.zeg("Lege licentie telt als niet herbruikbaar.")
                return NIET_HERBRUIKBAAR
            term.zeg(
                "Alleen publiek domein, CC0, CC BY of CC BY-SA mogen in de repo."
            )
            if term.ja_nee(
                "Valt deze licentie daaronder (herbruikbaar)?",
                default=False,
            ):
                return vrij.strip()
            return NIET_HERBRUIKBAAR
        term.zeg("Kies 1 tot en met 6.")


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
                return canonical_licentie(raw) or raw.strip()
        elif term.niet_interactief:
            raise Fout(
                "Geen herbruikbare licentie. Geef --licentie "
                "(Publiek domein, CC0, CC BY 4.0 of CC BY-SA 4.0)."
            )
        else:
            raw = kies_licentie(term)
            if raw != NIET_HERBRUIKBAAR:
                return canonical_licentie(raw) or raw.strip()
        term.zeg(
            "Dit plaatje mag niet in de repo. We nemen alleen publiek "
            "domein, CC0, CC BY of CC BY-SA op."
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


def entry_heeft_icoon(path: Path) -> bool:
    data = load_yaml(path)
    if not isinstance(data, dict):
        return False
    icoon = data.get("icoon") or {}
    return bool(str(icoon.get("bestand") or "").strip())


def icoon_yaml_blok(icoon: dict[str, str]) -> str:
    def q(waarde: str) -> str:
        if any(c in waarde for c in ":#{}[]&*?|>!%@`'\"\n"):
            escaped = waarde.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return waarde

    lines = [
        "icoon:",
        f"  bestand: {icoon['bestand']}",
        f"  rechten: {icoon['rechten']}",
        f"  licentie: {q(icoon['licentie'])}",
        f"  bron: {q(icoon['bron'])}",
        "",
    ]
    return "\n".join(lines)


def upsert_icoon_in_yaml(tekst: str, blok: str) -> str:
    if not tekst.endswith("\n"):
        tekst += "\n"
    if not blok.endswith("\n"):
        blok += "\n"
    pat = re.compile(r"^icoon:\n(?:[ \t].*\n)*", re.M)
    if pat.search(tekst):
        return pat.sub(blok, tekst, count=1)
    datum = re.compile(r"^datum:\n(?:[ \t].*\n)*", re.M)
    match = datum.search(tekst)
    if match:
        return tekst[: match.end()] + blok + tekst[match.end() :]
    return tekst.rstrip() + "\n" + blok


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


def verzamel_rest(
    term: Terminal,
    *,
    cli_id: str | None,
    cli_plaatje: Path | None,
    cli_bron: str | None,
    overschrijven: bool | None,
    root: Path,
) -> tuple[str, Path, str, bool]:
    entry_id = (cli_id or "").strip()
    if not entry_id:
        if term.niet_interactief:
            raise Fout("Geef --id.")
        entry_id = term.vraag("Id van de heilige of het feest: ")
    if not entry_id:
        raise Fout("Id ontbreekt.")
    yaml_path = vind_entry(root, entry_id)

    plaatje = cli_plaatje
    if plaatje is None:
        if term.niet_interactief:
            raise Fout("Geef --plaatje.")
        raw = term.vraag("Pad naar het plaatje: ")
        plaatje = Path(raw).expanduser()
    if not plaatje.is_file():
        raise Fout(f"Plaatje niet gevonden: {plaatje}")

    bron = (cli_bron or "").strip()
    if not bron:
        if term.niet_interactief:
            raise Fout("Geef --bron (bijv. Wikimedia Commons — File:… ).")
        bron = term.vraag(
            "Bron (bijv. Wikimedia Commons — File:… of korte fotobeschrijving): "
        )
    if not bron:
        raise Fout("Bron ontbreekt.")

    heeft = entry_heeft_icoon(yaml_path)
    mag_overschrijven = bool(overschrijven)
    if heeft and overschrijven is None:
        if term.niet_interactief:
            raise Fout(
                f"{yaml_path.name} heeft al een icoon. Gebruik --overschrijven."
            )
        mag_overschrijven = term.ja_nee(
            f"{entry_id} heeft al een icoon. Overschrijven?",
            default=False,
        )
        if not mag_overschrijven:
            raise Gestopt("Gestopt: bestaand icoon behouden.")
    if heeft and overschrijven is False:
        raise Gestopt("Gestopt: bestaand icoon behouden.")
    return entry_id, plaatje, bron, mag_overschrijven or not heeft


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Voeg een lokaal plaatje toe als icoon bij een bestaande heilige "
            "of een bestaand feest. Begint met licentie/rechten."
        )
    )
    p.add_argument("--id", help="Entry-id (bestandsnaam zonder .yaml)")
    p.add_argument("--plaatje", type=Path, help="Pad naar het bronplaatje")
    p.add_argument(
        "--licentie",
        help="Publiek domein, CC0, CC BY 4.0 of CC BY-SA 4.0",
    )
    p.add_argument("--bron", help="Bronregel voor het bijschrift")
    p.add_argument(
        "--overschrijven",
        action="store_true",
        help="Bestaand icoon vervangen zonder te vragen",
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
    return p.parse_args(argv)


def run(args: argparse.Namespace, term: Terminal | None = None) -> int:
    term = term or Terminal(niet_interactief=args.niet_interactief)
    term.niet_interactief = args.niet_interactief
    if args.plaatje is not None:
        args.plaatje = args.plaatje.expanduser()
    try:
        licentie = verzamel_licentie(term, args.licentie)
        entry_id, plaatje, bron, _ok = verzamel_rest(
            term,
            cli_id=args.id,
            cli_plaatje=args.plaatje,
            cli_bron=args.bron,
            overschrijven=True if args.overschrijven else None,
            root=args.root,
        )
        yaml_path = vind_entry(args.root, entry_id)
        dest = STATIC_ICONEN
        if args.root != ROOT:
            dest = args.root / "site" / "static" / "iconen"
        dest_file = dest / f"{entry_id}.jpg"
        breed, hoog = prepareer_plaatje(
            plaatje,
            dest_file,
            max_zijde=args.max_zijde,
        )
        relatief = f"iconen/{entry_id}.jpg"
        blok = icoon_yaml_blok(
            {
                "bestand": relatief,
                "rechten": "ok",
                "licentie": licentie,
                "bron": bron,
            }
        )
        tekst = yaml_path.read_text(encoding="utf-8")
        yaml_path.write_text(
            upsert_icoon_in_yaml(tekst, blok),
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
