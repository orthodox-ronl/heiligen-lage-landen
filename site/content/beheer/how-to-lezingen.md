---
title: "Lezingenrooster wijzigen"
description: "Gedeelde Moskou-lijst versus parochie-overrides; spec en tests"
weight: 50
git_date: 2026-08-21
---

Het lezingenrooster toont **Apostel** en **Evangelie** van de dag
(verwijzingen, geen volle Bijbeltekst). De gedeelde basis volgt Moskou,
bij twijfel ROCOR. Een parochie of klooster mag **daarnaast** een eigen
lijst hebben, zonder de gedeelde lijst te herschrijven.

**Actief in deze repo:** `parochie: den-haag` — het Orthodoxe klooster van
de Heilige Joannes de Voorloper in Den Haag (nu o.a. Silvester op 2 jan.).
Dat is **niet** de parochie Groningen. Wijzig `config.yaml` niet
stilzwijgend. Voor Groningen staat `data/lezingen/parochies/groningen.yaml`
klaar (nog zonder overrides); omzetten is één regel in `config.yaml`.

Clerusuitleg in gewone taal: `/uitleg/lezingen/`. Technische spiegel:
`/uitleg/lezingen-technisch/` (niet in het uitleg-overzicht) en
`docs/specs/lezingen.md`. Publiceren:
[site bouwen]({{% ref "/beheer/how-to-publiceren" %}}).

## Wat u wél wijzigt

| Bestand | Wanneer |
| --- | --- |
| `data/lezingen/parochies/<id>.yaml` | Lokale heilige, tempelfeest, of andere afwijking van het parochieboekje |
| `data/lezingen/config.yaml` | Welke parochielijst actief is (`parochie: <id>`), of leeg = alleen gedeeld |
| `data/lezingen/feest-overrides.yaml` | Gedeelde feestlezingen (Pascha, Kerst, …) — alleen met bron, niet voor één parochie |
| `data/lezingen/weekreeks.yaml` | Doorlopende weekreeks (rijádovoe) — zelden; dit is de tabel zelf |
| `data/lezingen/rang.yaml` | Wat er bij samenval gebeurt (vervangen / toevoegen / negeren) |
| `docs/specs/lezingen.md` | Normatieve spec; pytest leest de voorbeelden onderaan |

Kopieer `data/lezingen/parochies/voorbeeld.yaml` naar
`data/lezingen/parochies/<uw-id>.yaml` en zet in `config.yaml`:

```yaml
parochie: uw-id
```

## Parochie-afwijking (het gebruikelijke verzoek)

Clerus: «Op 2 januari lezen wij Silvester, Apostel … Evangelie …»

1. Open (of maak) `data/lezingen/parochies/<id>.yaml`.
2. Voeg een override toe met dezelfde vorm als de gedeelde lijst:

```yaml
overrides:
  - id: silvester
    match: { mmdd: "01-02" }
    rang: polyeleos
    modus: toevoegen          # of vervangen / negeren; weglaten = auto via rang
    apostel: [{ ref: "Heb. 5:4-10" }]
    evangelie: [{ ref: "Joh. 3:1-15" }]
    regels: [R2, R5]
    bron:
      label: "Parochieboekje …"
      geraadpleegd: "2026-08-16"
```

3. `match` is de **feestdatum** (`mmdd`) of een paascyclus-offset
   (`paascyclus_offset`), niet de burgerlijke vierdatum in de stand Oud.
4. Parochie-overrides krijgen standaard een hogere prioriteit dan de
   gedeelde lijst. U herschrijft Moskou niet; u legt er een lokale regel
   bovenop.
5. `python -m pytest tests/test_lezingen.py -q` (als die tests er zijn) en
   daarna generate / de roosterpagina controleren.

`modus`:

- `vervangen` — alleen de feestlezing
- `toevoegen` — doorlopende lezing én feest (vaak zondag bij vigil/polyeleos)
- `negeren` — alleen de doorlopende lezing
- weglaten — volgt `rang.yaml` (groot feest vervangt; zes stichiria negeert)

## Gedeelde feestlezing

Alleen als de **Moskou-lijst** (of de overeengekomen ROCOR-toets) moet
veranderen, niet voor één parochie. Zet de override in
`data/lezingen/feest-overrides.yaml`, met bron (`url` of drukwerk) en
`geraadpleegd`. Leg een concreet voorbeeld vast in `docs/specs/lezingen.md`
als de spec dat vraagt — pytest bewaakt die blokken.

Zaterdag/zondag vóór en ná Kruisverheffing, zaterdag/zondag vóór
Theofanie, zaterdag ná Theofanie en zaterdag vóór Kerst horen in die
gedeelde lijst (`weekdag_relatief`). Dat zijn lezingendagen, geen
feest-YAML onder `data/feesten/`. **1 september** (`mmdd`) en de
**zondag ná 10 oktober** (`weekdag_relatief` plus feest-YAML, zoals de
zondagen rond Kerst) horen er ook in.

De tweede zondag na Pinksteren (`zondag-heiligen-lage-landen`, offset 63)
staat in de gedeelde lijst als analogie van de Slavische lokale-heiligenzondag
(Moskou: heiligen van het Russische land; dezelfde extra-perikopen). Dat is
geen parochieboekje.

Een parochieboekje (bijv. de Den Haag-index) is een **checklist** tegen
Moskou, geen bron om de gedeelde lijst te kopiëren. Wijkt het boekje in
verzen of in de heiligenkeuze af, dan blijft Moskou; een lokale
uitzondering hoort in `parochies/<id>.yaml` na een uitdrukkelijk besluit.

## Wat u niet doet

- De weekreeks «even» inkorten omdat een lokaal boekje een week overslaat
  — eerst de spec (Lucaanse sprong, отступка / преступка, Theofanie-отступка).
- Een parochieboekje of lezingen-index in `feest-overrides.yaml` zetten.
  Die lijst is gedeeld Moskou; het boekje toetst, het herschrijft niet.
- Gegenereerde HTML of een handmatige kopie van het rooster in
  `site/content/` onderhouden als bron. Bron is YAML + spec.

## Controleren

Na YAML: tests, dan de dag op *Vandaag* / datumpagina / lezingenrooster.
Klopt het niet met het parochieboekje, dan is dat het gesprek met de
clerus: concrete datum, gewenste refs, vervangen of erbij, en een bron.
Daarna de parochie-YAML, niet de gedeelde tabel.
