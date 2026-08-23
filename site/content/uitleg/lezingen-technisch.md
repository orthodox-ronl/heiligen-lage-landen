---
title: Lezingen van de dag (technisch)
description: 'Normatieve specificatie: regels, bestanden en implementatiestatus'
build:
  list: never
  render: always
uitleg_stijl: lezingen-technisch
---

Deze pagina is de **technische spiegel** van `docs/specs/lezingen.md`. Wijzig die specificatie (regels + voorbeelden); daarna moet `scripts/lezingen.py` meekomen — pytest bewaakt dat.

Voor overleg met de clerus: [Lezingen van de dag]({{% ref "/uitleg/lezingen" %}}).

---

Normatieve specificatie voor [kalender](https://github.com/orthodox-ronl/heiligen-lage-landen).
Wijzigingen hier zijn bindend voor `scripts/lezingen.py`. Publieke pagina’s:

- **Clerus:** `/uitleg/lezingen/` — regels in gewone taal (geen YAML).
- **Technisch:** `/uitleg/lezingen-technisch/` — deze specificatie (spiegel);
  niet in de inhoudsopgave van Uitleg, wel bereikbaar via de clerus-pagina.

De machine-leesbare voorbeelden (onderaan dit bestand) sturen pytest; die
blokken staan niet op de technische uitlegpagina.

## Traditiebeleid

1. **Primair:** praktijk van de Russische Orthodoxe Kerk (Moskou) —
   *Богослужебные указания* en de kerkkalender van het Издательство Московской
   Патриархии.
2. **Bij twijfel of lacune:** ROCOR (toetsen o.a. aan Holy Trinity Orthodox
   Calendar / Jordanville).
3. Geen Grieks/Antiocheens als default.

De site toont **verwijzingen** (boek + verzen; optioneel зачало-nummer), geen
volledige Bijbeltekst.

## Begrippen

- **Rijádovoe / doorlopende lezing:** Apostel en Evangelie van de weekreeks
  (na Pascha of na Pinksteren), niet van een heilige.
- **Feestlezing:** lezing die bij een feest of (hoog) heiligenfeest hoort.
- **Зачало:** liturgische perikoop-nummering in Apostel/Evangelie-boeken.
- **«От полу»:** begin midden in een genummerd зачало (zie Azbyka).

## Regels (fase 0+)

### R1 — Kalendercontext

Beweeglijke dagen (paascyclus) worden berekend t.o.v. **Orthodox Pascha**
(Alexandrijnse/Juliaanse computus → burgerlijke datum). Vaste feesten gebruiken
de **feestdatum** (MM-DD-dagnaam), consistent met de rest van deze site
(nieuw/oud); zie uitleg Nieuw/Oud.

### R2 — Bekende feestoverride

Als voor de dag een feestoverride bestaat in `data/lezingen/feest-overrides.yaml`
(match op paascyclus-offset of vaste MM-DD), dan gelden die Apostel- en
Evangelielezingen. Ze **vervangen** de doorlopende lezing tenzij R5 een andere
`modus` voorschrijft (`toevoegen` / `negeren`).

**Parochielijsten:** optioneel `data/lezingen/config.yaml` → `parochie: <id>`
laadt `data/lezingen/parochies/<id>.yaml` met dezelfde override-vorm. Die
entries krijgen standaard `prioriteit: 300` (boven de gedeelde lijst), zodat
parochiefeesten (bijv. H. Silvester) het roosteren kunnen bijsturen zonder de
Moskou-basis te herschrijven. Zie § Parochie-overrides.

### R3 — Doorlopende weekreeks

Buiten feestoverrides: Apostel/Evangelie volgens de week na Pascha of na
Pinksteren en de weekdag (ma–zo), uit `data/lezingen/weekreeks.yaml`
(Messia/Brussel-tabellen; Moskou voor de Lucaanse sprong).

**Lucaanse sprong (Moskou):** vanaf de **maandag na de zondag na
Kruisverheffing** (14 sept.) volgt het Evangelie de Lucasse reeks vanaf
tabelweek 18; de Apostel blijft de doorlopende weektelling na Pinksteren.

**Отступка / преступка** (Azbyka, o.b.v. *Juliaanse* Pascha-datum):

| Juliaanse Pascha | Effect |
|------------------|--------|
| ≤ 30 maart | **отступка** — vóór de sprong blijven Matteüs-weken 1–17 (herhalen als de telling al ≥ 18 is); sprong naar Luc. 18 blijft |
| 31 maart – 6 april | normaal |
| ≥ 7 april | **преступка** — sprong naar Luc. 18 terwijl de Apostel-telling nog &lt; 17 kan zijn |

Tags in het resultaat: `R3-lucaans`, eventueel `R3-otstupka` / `R3-prestupka`.

**Theofanie-/winter-отступка** (Bogoyavlenskaya): zolang tabelweken 32–33 nog
vóór Tollenaar-zondag vallen, blijven die de gewone rijádovoe (geen herhaling).
Pas als er tussen het einde van tabelweek 33 en Tollenaar-zondag 1–5
weekdagenweken tekortkomen, worden die gevuld met herhaling van de eindreeks.
Volgorde (Bogaiskov / MP):

| N | Herhaalde tabelweken (ma→zo) |
|---|------------------------------|
| 1 | 33 |
| 2 | 32, 33 |
| 3 | 31, 32, 33 |
| 4 | 30, 31, 32, 33 |
| 5 | 30, 31, 17, 32, 33 |

Tag: `R3-theofanie-otstupka`. Voorbeeld zonder отступка: 1–8 feb 2025 (32e/33e
week); met N=5: vanaf ma 22 jan 2024.

### R4 — Vasten / geen liturgie

Op sommige vastendagen is er geen liturgie met Apostel/Evangelie van het type
“van de dag” (bijv. weekdagen in de Grote Vasten: OT-lezingen op uren). De
engine markeert dat als `status: geen_liturgie` wanneer de weekreeks dat
aangeeft.

### R5 — Rang en samenval

Bij samenval van feest/heilige en rijádovoe (of meerdere overrides) volgt
Moskou-rang. Configuratie: `data/lezingen/rang.yaml`.

| Rang | Standaard-modus |
|------|-----------------|
| `groot` | `vervangen` — alleen feestlezing |
| `vigil` / `polyeleos` / `doxologie` | `auto`: **zondag** → `toevoegen` (rijádovoe + feest); **weekdag** → `vervangen` |
| `zesstichiria` / `gewoon` | `negeren` — alleen rijádovoe |

Overrides mogen `rang` en/of expliciete `modus` zetten. Bij meerdere matches
wint de hoogste `prioriteit`. Wanneer een feest de rijádovoe **vervangt**
(andere perikopen), vermeldt het resultaat `R5` en optioneel het onderdrukte
`rijadovoe`-blok. Bij twijfel: ROCOR-kalender en voorbeeld hier vastleggen.

### R6 — Bronvermelding

Elke override en elk goedgekeurd voorbeeld noemt de geraadpleegde bron (URL of
drukwerk) en `geraadpleegd`-datum.

## Verantwoording / bronnen

| Bron | URL | Rol |
|------|-----|-----|
| MP-kalender | http://calendar.rop.ru | Officiële lezingen / BU |
| Патриархия — BU | https://patriarchia.ru/bu/tomorrow | Dagelijkse aanwijzingen |
| Azbyka — ukazatel’ | https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda | Index per periode |
| Azbyka — schema | https://azbyka.ru/shemy/tserkovnye_chtenyja.shtml | Jaarorde / Lucaanse sprong |
| Azbyka — зачало | https://azbyka.ru/zachala | Terminologie |
| Holy Trinity calendar | https://www.holytrinityorthodox.com/calendar/ | ROCOR-controle |
| Jordanville | https://jordanville.org/daily-orthodox-calendar/ | ROCOR-controle |

Drukwerk (jaarlijks): *Богослужебные указания* (Издательство Московской Патриархии).

## Implementatiestatus

| Regel | Status in code |
|-------|----------------|
| R1 | deels (kalenderhulp via `kalender.py`) |
| R2 | ja (feestoverrides + UI vandaag/datum) |
| R3 | ja (weekreeks + Lucaanse sprong; zie rooster) |
| R4 | deels (`geen_liturgie` via weekreeks) |
| R5 | ja (`rang.yaml` + modus vervangen/toevoegen/negeren) |
| R6 | documentair (data + voorbeelden) |

## Parochie-overrides

Gedeelde basis: `data/lezingen/feest-overrides.yaml`.

Optioneel per parochie:

```yaml
# data/lezingen/config.yaml
parochie: den-haag   # of leeg = alleen gedeelde lijst
```

```yaml
# data/lezingen/parochies/den-haag.yaml
parochie: den-haag
naam: "Orthodox klooster van de Heilige Joannes de Voorloper, Den Haag"
overrides:
  - id: silvester
    match: { mmdd: "01-02" }
    rang: polyeleos
    modus: toevoegen          # of vervangen / negeren / weglaten (= auto via rang)
    apostel: [{ ref: "Heb. 5:4-10" }]
    evangelie: [{ ref: "Joh. 3:1-15" }]
    regels: [R2, R5]
    bron:
      label: "Apostel (klooster Johannes de Voorloper, Den Haag, 1995)"
      geraadpleegd: "2026-08-16"
```

Matchvelden (zelfde als gedeeld): `mmdd`, `paascyclus_offset`,
`paascyclus_offset_in` (met optioneel `stijl: oud`), en
`weekdag_relatief` (`anker`, `weekdag`, `welke`, `richting`) voor de
zaterdag of zondag vóór/ná een vaste feestdatum. Relatief t.o.v. Theofanie of
een ander anker als vaste offset: vooralsnog via `mmdd` of
`weekdag_relatief`; een apart `theofanie_offset`-veld is niet nodig zolang
`anker: "01-06"` volstaat. Match loopt over ankerjaar − 1, 0 en + 1
(zondag ná Kerst op 1 jan.; zaterdag/zondag vóór Theofanie in december).

**Zondagen rond Kerst** (Voorvaderen; Heilige Vaderen vóór Kerst; zondag
ná Kerst; zondag ná Theofanie) en **zondag ná 10 oktober** (Vaderen van
het Zevende Concilie): gemodelleerd als `datum.weekdag_relatief` en als
lezingenoverride met hetzelfde matchveld. Bij samenval met een
grootfeest (Besnijdenis, synaxis) wint dat feest (`prioriteit` 90 vs 100);
geen gegokte combinatielezing. **1 september** (begin kerkelijk jaar) is
een vaste feestdatum (`mmdd: "09-01"`).

**Lezingendagen zonder eigen feestdienst** (geen stichira/canon, géén
`soort: feest`-entries, alleen overrides via `weekdag_relatief`,
`prioriteit` 90):

| Anker | Dagen |
| --- | --- |
| 14 sept. | zaterdag/zondag vóór en ná Kruisverheffing |
| 6 jan. | zaterdag/zondag vóór Theofanie; zaterdag ná Theofanie |
| 25 dec. | zaterdag vóór Kerst |

Bij samenval wint het grootfeest (Theofanie, Kerst, Besnijdenis, synaxis,
Geboorte Moeder Gods, Kruisverheffing zelf). De zondag ná Kruisverheffing
is tevens het anker van de Lucaanse sprong (R3). Perikopen volgen Moskou
(Azbyka); een parochieboekje is checklist, geen bron om de gedeelde lijst
te herschrijven. Wijkt een boekje in verzen af (bijv. zaterdag ná
Kruisverheffing, Onthoofding, zaterdag vóór Theofanie), dan blijft Moskou.

Voorbeeldbestand (niet actief tenzij gekozen): `data/lezingen/parochies/voorbeeld.yaml`.
Actief in deze repo: `parochie: den-haag` (Orthodox klooster Johannes de
Voorloper, Den Haag — niet Groningen). `parochies/groningen.yaml` staat
klaar zonder overrides; omzetten is één regel in `config.yaml`. Niet
stilzwijgend wijzigen.
