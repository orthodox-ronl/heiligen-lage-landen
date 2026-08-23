# Lezingen van de dag (Apostel en Evangelie)

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

## Machine-leesbare voorbeelden

Pytest leest blokken ` ```lezingen-voorbeeld ` … ` ``` `.  
`status: implemented` moet slagen; `status: pending` wordt overgeslagen.

```lezingen-voorbeeld
id: pascha-2025
status: implemented
jaar: 2025
mmdd: "04-20"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Hand. 1:1-8"
  evangelie:
    - ref: "Joh. 1:1-17"
  regels:
    - R2
bron:
  label: "Azbyka — ukazatel’ (Pascha)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: theofanie-nieuw
status: implemented
jaar: 2026
mmdd: "01-06"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Tit. 2:11-14; 3:4-7"
  evangelie:
    - ref: "Matt. 3:13-17"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka / MP — Theofanie"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: palmzondag-2025
status: implemented
jaar: 2025
mmdd: "04-13"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Fil. 4:4-9"
  evangelie:
    - ref: "Joh. 12:1-18"
  regels:
    - R2
bron:
  label: "Azbyka — ukazatel’ (Palmzondag)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: pinksteren-2025
status: implemented
jaar: 2025
mmdd: "06-08"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Hand. 2:1-11"
  evangelie:
    - ref: "Joh. 7:37-52; 8:12"
  regels:
    - R2
bron:
  label: "Azbyka — ukazatel’ (Pinksteren)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: kerst-nieuw
status: implemented
jaar: 2026
mmdd: "12-25"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Gal. 4:4-7"
  evangelie:
    - ref: "Matt. 2:1-12"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka — ukazatel’ (Kerst)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: weekdag-na-pinksteren-voorbeeld
status: implemented
jaar: 2025
mmdd: "06-16"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Rom. 2:28-3:18"
  evangelie:
    - ref: "Matt. 6:31-34; 7:9-11"
  regels:
    - R3
bron:
  label: "Messia — ukazatel’ (2e week na Pinksteren, maandag)"
  url: "https://messia.ru/spravki/kalendar/lkcioprc.htm"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: ontslapen-vervangt-rijadovoe-2025
status: implemented
jaar: 2025
mmdd: "08-15"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Fil. 2:5-11"
  evangelie:
    - ref: "Luc. 10:38-42; 11:27-28"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka — Ontslapen (groot feest vervangt vrijdag-rijádovoe)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
notitie: "R5 vervangen: onderdrukte rijádovoe was 2 Kor. 1:12-20 / Matt. 22:23-33."
```

```lezingen-voorbeeld
id: elia-op-zondag-toevoegen-2025
status: implemented
jaar: 2025
mmdd: "07-20"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Rom. 12:6-14"
    - ref: "Jak. 5:10-20"
  evangelie:
    - ref: "Matt. 9:1-8"
    - ref: "Luc. 4:22-30"
  regels:
    - R3
    - R2
    - R5
bron:
  label: "Menaion Elia + 6e zondag na Pinksteren (polyeleos auto/toevoegen)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: aankondiging-op-pascha-1991-oud
status: implemented
jaar: 1991
mmdd: "03-25"
stijl: oud
verwacht:
  apostel:
    - ref: "Hand. 1:1-8"
    - ref: "Heb. 2:11-18"
  evangelie:
    - ref: "Joh. 1:1-17"
    - ref: "Luc. 1:24-38"
  regels:
    - R2
    - R5
bron:
  label: "Typikon — Kyriopascha 1991 (Juliaanse 25 maart = Pascha)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: aankondiging-op-grote-zaterdag-2018-oud
status: implemented
jaar: 2018
mmdd: "03-25"
stijl: oud
verwacht:
  apostel:
    - ref: "Rom. 6:3-11"
    - ref: "Heb. 2:11-18"
  evangelie:
    - ref: "Matt. 28:1-20"
    - ref: "Luc. 1:24-38"
  regels:
    - R2
    - R5
bron:
  label: "Typikon — Aankondiging op grote zaterdag 2018"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: winter-eindreeks-2025-02-01
status: implemented
jaar: 2025
mmdd: "02-01"
stijl: nieuw
verwacht:
  apostel:
    - ref: "1 Tess. 5:14-23"
  evangelie:
    - ref: "Luc. 17:3-10"
  regels:
    - R3
bron:
  label: "Doorlopende 32e week na Pinksteren (geen Theofanie-отступка in 2025)"
  url: "https://azbyka.ru/otstupka-i-prestupka"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: theofanie-otstupka-2024
status: implemented
jaar: 2024
mmdd: "01-22"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Heb. 8:7-13"
  evangelie:
    - ref: "Mark. 8:11-21"
  regels:
    - R3
    - R3-theofanie-otstupka
bron:
  label: "Azbyka / Bogaiskov — Богоявленская отступка (N=5, eerste herhalingsweek = 30)"
  url: "https://azbyka.ru/otstupka-i-prestupka"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: pokrov-nieuw
status: implemented
jaar: 2026
mmdd: "10-01"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Heb. 9:1-7"
  evangelie:
    - ref: "Luc. 10:38-42; 11:27-28"
  regels:
    - R2
    - R5
bron:
  label: "OCA / Azbyka — Pokrov (1 okt.)"
  url: "https://www.oca.org/saints/lives/2024/10/01/102824-the-protection-of-our-most-holy-lady-the-mother-of-god-and-ever"
  geraadpleegd: "2026-08-17"
```

```lezingen-voorbeeld
id: synaxis-moeder-gods-nieuw
status: implemented
jaar: 2026
mmdd: "12-26"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Heb. 2:11-18"
  evangelie:
    - ref: "Matt. 2:13-23"
  regels:
    - R2
    - R5
bron:
  label: "OCA / Azbyka — Synaxis Moeder Gods (26 dec.)"
  url: "https://www.oca.org/saints/lives/2024/12/26/103616-synaxis-of-the-most-holy-mother-of-god"
  geraadpleegd: "2026-08-17"
```

```lezingen-voorbeeld
id: synaxis-johannes-doper-nieuw
status: implemented
jaar: 2026
mmdd: "01-07"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Hand. 19:1-8"
  evangelie:
    - ref: "Joh. 1:29-34"
  regels:
    - R2
    - R5
bron:
  label: "OCA / Azbyka — Synaxis Johannes de Doper (7 jan.)"
  url: "https://www.oca.org/saints/lives/2024/01/07/100109-synaxis-of-the-holy-glorious-prophet-forerunner-and-baptist-john"
  geraadpleegd: "2026-08-17"
```

```lezingen-voorbeeld
id: zondag-voorvaderen-2026
status: implemented
jaar: 2026
mmdd: "12-13"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Kol. 3:4-11"
  evangelie:
    - ref: "Luc. 14:16-24"
  regels:
    - R2
    - R5
bron:
  label: "OCA / Azbyka — Zondag van de Voorvaderen"
  url: "https://www.oca.org/saints/lives/2024/12/15/103535-sunday-of-the-forefathers"
  geraadpleegd: "2026-08-17"
```

```lezingen-voorbeeld
id: zondag-vaderen-voor-kerst-2026
status: implemented
jaar: 2026
mmdd: "12-20"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Heb. 11:9-10, 17-23, 32-40"
  evangelie:
    - ref: "Matt. 1:1-25"
  regels:
    - R2
    - R5
bron:
  label: "OCA / Azbyka — Zondag vóór Kerst"
  url: "https://www.oca.org/saints/lives/2024/12/22/103536-sunday-before-the-nativity-of-our-lord"
  geraadpleegd: "2026-08-17"
```

```lezingen-voorbeeld
id: zaterdag-voor-kruisverheffing-2026
status: implemented
jaar: 2026
mmdd: "09-12"
stijl: nieuw
verwacht:
  apostel:
    - ref: "1 Kor. 2:6-9"
  evangelie:
    - ref: "Matt. 10:37-11:1"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka / OCA — Zaterdag vóór Kruisverheffing"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-21"
```

```lezingen-voorbeeld
id: zondag-voor-kruisverheffing-2026
status: implemented
jaar: 2026
mmdd: "09-13"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Gal. 6:11-18"
  evangelie:
    - ref: "Joh. 3:13-17"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka / OCA — Zondag vóór Kruisverheffing"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-21"
```

```lezingen-voorbeeld
id: zaterdag-na-kruisverheffing-2026
status: implemented
jaar: 2026
mmdd: "09-19"
stijl: nieuw
verwacht:
  apostel:
    - ref: "1 Kor. 1:26-29"
  evangelie:
    - ref: "Joh. 8:21-30"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka / OCA — Zaterdag na Kruisverheffing"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-21"
```

```lezingen-voorbeeld
id: zondag-na-kruisverheffing-2026
status: implemented
jaar: 2026
mmdd: "09-20"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Gal. 2:16-20"
  evangelie:
    - ref: "Mark. 8:34-9:1"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka / OCA — Zondag na Kruisverheffing"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-21"
```

```lezingen-voorbeeld
id: zaterdag-voor-theofanie-2026
status: implemented
jaar: 2026
mmdd: "01-03"
stijl: nieuw
verwacht:
  apostel:
    - ref: "1 Tim. 3:14-4:5"
  evangelie:
    - ref: "Matt. 3:1-11"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka — Zaterdag vóór Theofanie"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-21"
```

```lezingen-voorbeeld
id: zondag-voor-theofanie-2026
status: implemented
jaar: 2026
mmdd: "01-04"
stijl: nieuw
verwacht:
  apostel:
    - ref: "2 Tim. 4:5-8"
  evangelie:
    - ref: "Mark. 1:1-8"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka — Zondag vóór Theofanie"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-21"
```

```lezingen-voorbeeld
id: zaterdag-na-theofanie-2026
status: implemented
jaar: 2026
mmdd: "01-10"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Ef. 6:10-17"
  evangelie:
    - ref: "Matt. 4:1-11"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka — Zaterdag na Theofanie"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-21"
```

```lezingen-voorbeeld
id: zaterdag-voor-kerst-2026
status: implemented
jaar: 2026
mmdd: "12-19"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Gal. 3:8-12"
  evangelie:
    - ref: "Luc. 13:18-29"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka — Zaterdag vóór Kerst"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-21"
```

```lezingen-voorbeeld
id: begin-kerkelijk-jaar-2026
status: implemented
jaar: 2026
mmdd: "09-01"
stijl: nieuw
verwacht:
  apostel:
    - ref: "1 Tim. 2:1-7"
  evangelie:
    - ref: "Luc. 4:16-22"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka / OCA — Begin kerkelijk jaar (indictie)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-21"
```

```lezingen-voorbeeld
id: zondag-vaderen-zevende-concilie-2026
status: implemented
jaar: 2026
mmdd: "10-11"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Tit. 3:8-15"
    - ref: "Heb. 13:7-16"
  evangelie:
    - ref: "Joh. 17:1-13"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka / OCA — Vaderen van het 7e Oecumenische Concilie"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-21"
```
