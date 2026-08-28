"""Zet specifiekere referentie-URLs op alle feest-entries (labels in het Nederlands)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEESTEN = ROOT / "data" / "feesten"
REF_DATE = "2026-08-16"

# Per feast-id: lijst van (label, url). Labels: Nederlands + orthodox jargon.
# URL's mogen Engels zijn (OrthodoxWiki/OCA); labels niet.
BESTE_REFS: dict[str, list[tuple[str, str]]] = {
    "transfiguratie": [
        ("OrthodoxWiki — Transfiguratie", "https://orthodoxwiki.org/Transfiguration"),
        (
            "OCA — Heilige Transfiguratie",
            "https://www.oca.org/saints/lives/2024/08/06/100795-the-holy-transfiguration-of-our-lord-god-and-savior-jesus-christ",
        ),
        (
            "OCA — Het Orthodoxe geloof: Transfiguratie",
            "https://www.oca.org/orthodoxy/the-orthodox-faith/worship/the-church-year/transfiguration",
        ),
    ],
    "kerst": [
        ("OrthodoxWiki — Geboorte van Christus", "https://orthodoxwiki.org/Nativity"),
        (
            "OCA — Geboorte van Christus",
            "https://www.oca.org/saints/lives/2024/12/25/103533-the-nativity-of-our-lord-god-and-savior-jesus-christ",
        ),
    ],
    "theofanie": [
        ("OrthodoxWiki — Theofanie", "https://orthodoxwiki.org/Theophany"),
        (
            "OCA — Heilige Theofanie",
            "https://www.oca.org/saints/lives/2024/01/06/100105-the-holy-theophany-of-our-lord-god-and-savior-jesus-christ",
        ),
    ],
    "aankondiging": [
        ("OrthodoxWiki — Aankondiging", "https://orthodoxwiki.org/Annunciation"),
        (
            "OCA — Aankondiging",
            "https://www.oca.org/saints/lives/2024/03/25/100884-the-annunciation-of-our-most-holy-lady-the-theotokos-and-ever-vi",
        ),
        (
            "OCA — Het Orthodoxe geloof: Aankondiging",
            "https://www.oca.org/orthodoxy/the-orthodox-faith/worship/the-church-year/annunciation",
        ),
    ],
    "ontslapen-moeder-gods": [
        ("OrthodoxWiki — Ontslapen", "https://orthodoxwiki.org/Dormition"),
        (
            "OCA — Ontslapen van de Moeder Gods",
            "https://www.oca.org/saints/lives/2024/08/15/102304-the-dormition-of-our-most-holy-lady-the-mother-of-god-and-ever-v",
        ),
    ],
    "geboorte-moeder-gods": [
        (
            "OrthodoxWiki — Geboorte van de Moeder Gods",
            "https://orthodoxwiki.org/Nativity_of_the_Theotokos",
        ),
        (
            "OCA — Geboorte van de Moeder Gods",
            "https://www.oca.org/saints/lives/2024/09/08/102498-the-nativity-of-our-most-holy-lady-the-mother-of-god-and-ever-vi",
        ),
    ],
    "tempelgang-moeder-gods": [
        (
            "OrthodoxWiki — Tempelgang van de Moeder Gods",
            "https://orthodoxwiki.org/Entrance_of_the_Theotokos",
        ),
        (
            "OCA — Tempelgang van de Moeder Gods",
            "https://www.oca.org/saints/lives/2024/11/21/103341-the-entry-of-the-most-holy-mother-of-god-into-the-temple",
        ),
    ],
    "ontmoeting-in-de-tempel": [
        ("OrthodoxWiki — Ontmoeting in de tempel", "https://orthodoxwiki.org/Presentation"),
        (
            "OCA — Ontmoeting van de Heer in de tempel",
            "https://www.oca.org/saints/lives/2024/02/02/100406-the-meeting-of-our-lord-god-and-savior-jesus-christ-in-the-temple",
        ),
    ],
    "kruisverheffing": [
        (
            "OrthodoxWiki — Kruisverheffing",
            "https://orthodoxwiki.org/Exaltation_of_the_Cross",
        ),
        (
            "OCA — Universele Kruisverheffing",
            "https://www.oca.org/saints/lives/2024/09/14/102545-the-universal-exaltation-of-the-precious-and-life-giving-cross",
        ),
    ],
    "besnijdenis-des-heren": [
        (
            "OrthodoxWiki — Besnijdenis des Heren",
            "https://orthodoxwiki.org/Circumcision_of_our_Lord",
        ),
        (
            "OCA — Besnijdenis des Heren",
            "https://www.oca.org/saints/lives/2024/01/01/100001-the-circumcision-of-our-lord-and-savior-jesus-christ",
        ),
    ],
    "begin-kerkelijk-jaar": [
        ("OrthodoxWiki — Indictie", "https://orthodoxwiki.org/Indiction"),
        (
            "OCA — Begin van het kerkelijk jaar",
            "https://www.oca.org/saints/lives/2024/09/01/102423-church-new-year",
        ),
    ],
    "geboorte-johannes-doper": [
        (
            "OrthodoxWiki — Johannes de Voorloper",
            "https://orthodoxwiki.org/John_the_Forerunner",
        ),
        (
            "OCA — Geboorte van Johannes de Voorloper",
            "https://www.oca.org/saints/lives/2024/06/24/101784-nativity-of-the-holy-glorious-prophet-forerunner-and-baptist-john",
        ),
    ],
    "onthoofding-johannes-doper": [
        (
            "OrthodoxWiki — Onthoofding van Johannes de Voorloper",
            "https://orthodoxwiki.org/Beheading_of_St._John_the_Forerunner",
        ),
        (
            "OCA — Onthoofding van Johannes de Voorloper",
            "https://www.oca.org/saints/lives/2024/08/29/102409-the-beheading-of-the-holy-glorious-prophet-forerunner-and-baptis",
        ),
    ],
    "petrus-en-paulus": [
        ("OrthodoxWiki — Apostel Petrus", "https://orthodoxwiki.org/Apostle_Peter"),
        ("OrthodoxWiki — Apostel Paulus", "https://orthodoxwiki.org/Apostle_Paul"),
        (
            "OCA — Petrus en Paulus",
            "https://www.oca.org/saints/lives/2024/06/29/101838-the-holy-glorious-and-all-praised-leaders-of-the-apostles-peter",
        ),
    ],
    "pascha": [
        ("OrthodoxWiki — Pascha", "https://orthodoxwiki.org/Pascha"),
        (
            "OCA — Heilig Pascha",
            "https://www.oca.org/saints/lives/2025/04/20/27-holy-pascha-the-resurrection-of-our-lord",
        ),
    ],
    "zacheus-zondag": [
        ("OrthodoxWiki — Triodion", "https://orthodoxwiki.org/Lenten_Triodion"),
        ("OrthodoxWiki — Kerkelijk jaar", "https://orthodoxwiki.org/Church_Calendar"),
    ],
    "zondag-tollenaar-en-farizeeer": [
        (
            "OrthodoxWiki — Zondag van de tollenaar en de Farizeeër",
            "https://orthodoxwiki.org/Sunday_of_the_Publican_and_Pharisee",
        ),
        ("OrthodoxWiki — Triodion", "https://orthodoxwiki.org/Lenten_Triodion"),
    ],
    "zondag-verloren-zoon": [
        (
            "OrthodoxWiki — Zondag van de verloren zoon",
            "https://orthodoxwiki.org/Sunday_of_the_Prodigal_Son",
        ),
        ("OrthodoxWiki — Triodion", "https://orthodoxwiki.org/Lenten_Triodion"),
    ],
    "zaterdag-allerzielen-vleesmijding": [
        ("OrthodoxWiki — Vleesvaarwel", "https://orthodoxwiki.org/Meatfare_Sunday"),
        ("OrthodoxWiki — Triodion", "https://orthodoxwiki.org/Lenten_Triodion"),
    ],
    "zondag-laatste-oordeel": [
        (
            "OrthodoxWiki — Zondag van het Laatste Oordeel",
            "https://orthodoxwiki.org/Sunday_of_the_Last_Judgment",
        ),
        ("OrthodoxWiki — Vleesvaarwel", "https://orthodoxwiki.org/Meatfare_Sunday"),
    ],
    "vergevingszondag": [
        ("OrthodoxWiki — Vergevingszondag", "https://orthodoxwiki.org/Forgiveness_Sunday"),
        ("OrthodoxWiki — Zuivelvaarwel", "https://orthodoxwiki.org/Cheesefare_Sunday"),
    ],
    "schone-maandag": [
        ("OrthodoxWiki — Schone Maandag", "https://orthodoxwiki.org/Clean_Monday"),
        ("OrthodoxWiki — Grote Vasten", "https://orthodoxwiki.org/Great_Lent"),
        (
            "OCA — Grote Vasten",
            "https://www.oca.org/orthodoxy/the-orthodox-faith/worship/the-church-year/great-lent",
        ),
    ],
    "zondag-orthodoxie": [
        (
            "OrthodoxWiki — Zondag van de Orthodoxie",
            "https://orthodoxwiki.org/Sunday_of_Orthodoxy",
        ),
        ("OrthodoxWiki — Grote Vasten", "https://orthodoxwiki.org/Great_Lent"),
    ],
    "zondag-gregorius-palamas": [
        ("OrthodoxWiki — Gregorius Palamas", "https://orthodoxwiki.org/Gregory_Palamas"),
        ("OrthodoxWiki — Grote Vasten", "https://orthodoxwiki.org/Great_Lent"),
    ],
    "zondag-kruisverering": [
        (
            "OrthodoxWiki — Zondag van het Heilig Kruis",
            "https://orthodoxwiki.org/Sunday_of_the_Holy_Cross",
        ),
        ("OrthodoxWiki — Grote Vasten", "https://orthodoxwiki.org/Great_Lent"),
    ],
    "zondag-johannes-klimacus": [
        ("OrthodoxWiki — Johannes Klimacus", "https://orthodoxwiki.org/John_Climacus"),
        ("OrthodoxWiki — Grote Vasten", "https://orthodoxwiki.org/Great_Lent"),
    ],
    "zondag-maria-van-egypte": [
        ("OrthodoxWiki — Maria van Egypte", "https://orthodoxwiki.org/Mary_of_Egypt"),
        ("OrthodoxWiki — Grote Vasten", "https://orthodoxwiki.org/Great_Lent"),
    ],
    "lazarus-zaterdag": [
        ("OrthodoxWiki — Lazarus-zaterdag", "https://orthodoxwiki.org/Lazarus_Saturday"),
        ("OrthodoxWiki — Grote Week", "https://orthodoxwiki.org/Holy_Week"),
    ],
    "palmzondag": [
        ("OrthodoxWiki — Palmzondag", "https://orthodoxwiki.org/Palm_Sunday"),
        (
            "OCA — Grote Week",
            "https://www.oca.org/orthodoxy/the-orthodox-faith/worship/the-church-year/holy-week",
        ),
    ],
    "grote-maandag": [
        ("OrthodoxWiki — Grote Week", "https://orthodoxwiki.org/Holy_Week"),
        ("OrthodoxWiki — Lijdensweek", "https://orthodoxwiki.org/Passion_Week"),
        (
            "OCA — Grote Week",
            "https://www.oca.org/orthodoxy/the-orthodox-faith/worship/the-church-year/holy-week",
        ),
    ],
    "grote-dinsdag": [
        ("OrthodoxWiki — Grote Week", "https://orthodoxwiki.org/Holy_Week"),
        ("OrthodoxWiki — Lijdensweek", "https://orthodoxwiki.org/Passion_Week"),
    ],
    "grote-woensdag": [
        ("OrthodoxWiki — Grote Week", "https://orthodoxwiki.org/Holy_Week"),
        ("OrthodoxWiki — Heilige Zalving", "https://orthodoxwiki.org/Holy_Unction"),
    ],
    "grote-donderdag": [
        ("OrthodoxWiki — Grote Week", "https://orthodoxwiki.org/Holy_Week"),
        (
            "OCA — Grote Week",
            "https://www.oca.org/orthodoxy/the-orthodox-faith/worship/the-church-year/holy-week",
        ),
    ],
    "grote-vrijdag": [
        ("OrthodoxWiki — Grote Vrijdag", "https://orthodoxwiki.org/Holy_Friday"),
        (
            "OCA — Grote Vrijdag",
            "https://www.oca.org/orthodoxy/the-orthodox-faith/worship/the-church-year/holy-friday",
        ),
    ],
    "grote-zaterdag": [
        ("OrthodoxWiki — Grote Zaterdag", "https://orthodoxwiki.org/Holy_Saturday"),
        ("OrthodoxWiki — Grote Week", "https://orthodoxwiki.org/Holy_Week"),
    ],
    "lichte-maandag": [
        ("OrthodoxWiki — Lichte Week", "https://orthodoxwiki.org/Bright_Week"),
        ("OrthodoxWiki — Pascha", "https://orthodoxwiki.org/Pascha"),
    ],
    "thomaszondag": [
        ("OrthodoxWiki — Apostel Thomas", "https://orthodoxwiki.org/Apostle_Thomas"),
        ("OrthodoxWiki — Pentecostarion", "https://orthodoxwiki.org/Pentecostarion"),
        ("OrthodoxWiki — Lichte Week", "https://orthodoxwiki.org/Bright_Week"),
    ],
    "zondag-myrondraagsters": [
        (
            "OrthodoxWiki — Zondag van de myrondraagsters",
            "https://orthodoxwiki.org/Sunday_of_Myrrh-bearing_Women",
        ),
        ("OrthodoxWiki — Pentecostarion", "https://orthodoxwiki.org/Pentecostarion"),
    ],
    "zondag-verlamde": [
        ("OrthodoxWiki — Pentecostarion", "https://orthodoxwiki.org/Pentecostarion"),
        ("OrthodoxWiki — Pascha", "https://orthodoxwiki.org/Pascha"),
    ],
    "midden-pinksterfeest": [
        ("OrthodoxWiki — Pentecostarion", "https://orthodoxwiki.org/Pentecostarion"),
        ("OrthodoxWiki — Pinksteren", "https://orthodoxwiki.org/Pentecost"),
    ],
    "zondag-samaritaanse": [
        ("OrthodoxWiki — Pentecostarion", "https://orthodoxwiki.org/Pentecostarion"),
        ("OrthodoxWiki — Pascha", "https://orthodoxwiki.org/Pascha"),
    ],
    "zondag-blinde": [
        ("OrthodoxWiki — Pentecostarion", "https://orthodoxwiki.org/Pentecostarion"),
        ("OrthodoxWiki — Hemelvaart", "https://orthodoxwiki.org/Ascension"),
    ],
    "teruggave-pascha": [
        ("OrthodoxWiki — Teruggave (apodosis)", "https://orthodoxwiki.org/Apodosis"),
        ("OrthodoxWiki — Nafeest", "https://orthodoxwiki.org/Afterfeast"),
        ("OrthodoxWiki — Pascha", "https://orthodoxwiki.org/Pascha"),
    ],
    "hemelvaart": [
        ("OrthodoxWiki — Hemelvaart", "https://orthodoxwiki.org/Ascension"),
        (
            "OCA — Hemelvaart",
            "https://www.oca.org/orthodoxy/the-orthodox-faith/worship/the-church-year/ascension",
        ),
    ],
    "zondag-vaderen-eerste-concilie": [
        (
            "OrthodoxWiki — Eerste Oecumenische Concilie",
            "https://orthodoxwiki.org/First_Ecumenical_Council",
        ),
        ("OrthodoxWiki — Hemelvaart", "https://orthodoxwiki.org/Ascension"),
    ],
    "allerzielen-zaterdag-pinksteren": [
        ("OrthodoxWiki — Pinksteren", "https://orthodoxwiki.org/Pentecost"),
        ("OrthodoxWiki — Pentecostarion", "https://orthodoxwiki.org/Pentecostarion"),
    ],
    "pinksteren": [
        ("OrthodoxWiki — Pinksteren", "https://orthodoxwiki.org/Pentecost"),
        ("OrthodoxWiki — Pentecostarion", "https://orthodoxwiki.org/Pentecostarion"),
    ],
    "geestesmaandag": [
        ("OrthodoxWiki — Pinksteren", "https://orthodoxwiki.org/Pentecost"),
        ("OrthodoxWiki — Kerkelijk jaar", "https://orthodoxwiki.org/Church_Calendar"),
    ],
    "allerheiligen-zondag": [
        ("OrthodoxWiki — Pinksteren", "https://orthodoxwiki.org/Pentecost"),
        ("OrthodoxWiki — Kerkelijk jaar", "https://orthodoxwiki.org/Church_Calendar"),
    ],
}


def apply() -> None:
    for feast_id, refs in BESTE_REFS.items():
        path = FEESTEN / f"{feast_id}.yaml"
        if not path.is_file():
            raise SystemExit(f"Ontbreekt: {path}")
        text = path.read_text(encoding="utf-8")
        head, _, _tail = text.partition("referenties:")
        lines = ["referenties:"]
        for label, url in refs:
            lines.append(f'  - label: "{label}"')
            lines.append(f'    url: "{url}"')
            lines.append(f'    geraadpleegd: "{REF_DATE}"')
        lines.append("")
        path.write_text(head + "\n".join(lines), encoding="utf-8", newline="\n")
        print(f"{feast_id}: {len(refs)} refs")


if __name__ == "__main__":
    apply()
