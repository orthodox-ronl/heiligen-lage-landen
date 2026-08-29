# Schema’s en YAML-bronnen

Alle **inhoud** die we beheren hoort in YAML onder `data/`. Gegenereerde
markdown onder `site/content/` is een afdruk — daar niet redigeren.

## Principe: soepel opslaan, strikt tonen

- **Opslaan:** je mag op entries (en waar het schema dat toelaat) extra
  velden zetten voor notities, onderzoek, experimenten. Die breken de
  site niet: `generate.py` en de UI lezen alleen bekende velden.
- **Valideren:** bekende velden blijven genormeerd (`validate` of
  `python scripts/validate.py`
  + JSON Schema). Onbekende **top-level** velden op een entry zijn
  toegestaan (`additionalProperties: true` in `entry.schema.json`).
- **Tonen:** pagina-indelingen kunnen later wijzigen zonder dat je data
  hoeft te splitsen; de YAML blijft de bron.

## Overzicht

| Bron | Schema / norm | Wat hoort erin | Wat niet |
| --- | --- | --- | --- |
| `data/heiligen/*.yaml`, `data/feesten/*.yaml`, `data/vasten/*.yaml` | [`entry.schema.json`](entry.schema.json) | Id, `namen`, datum/cyclus, tekst, selectie (heiligen), locaties, referenties | Handmatige `site/content/…/*.md`; losse HTML |
| `data/plaatsen.yaml` | [`plaatsen.schema.json`](plaatsen.schema.json) | Plaats/streek-ids, coördinaten, weergavenaam | Vrije plaatsnamen in `locaties:` op een entry |
| `data/regels/vasten.yaml` | Clerus/technisch: `/uitleg/vasten/` | Normatieve vastenregels + voorbeelden | Ad-hoc uitzonderingen zonder YAML |
| `data/lezingen/` | [`docs/specs/lezingen.md`](../docs/specs/lezingen.md) | Overrides, weekreeks, parochie-afwijkingen | Handmatig Apostel/Evangelie op datumpagina’s |
| `data/bronnen/` (indien aanwezig) | Datamodel | Gedeelde bron-metadata | URL’s zonder `bron_id` waar het register bestaat |

How-to’s: `site/content/beheer/`. Datamodel: `docs/datamodel.md`.

## Auteurs: wanneer welk veld (entries)

Gebruik dit als beslisboom. Details en voorbeelden staan in de how-to’s.

| Veld | Zet erin als… | Zet er níet in als… |
| --- | --- | --- |
| `namen.primair` / `alternatief` | Je de getoonde titel of zoekaliassen wijzigt | Je alleen het id wilt “mooier” maken (id blijft stabiel) |
| `samenvatting` | Eén alinea “wie is dit” | Lange vita (dat is `verhaal`) |
| `betekenis_lage_landen` | Je specifiek de band met NL/BE/LUX uitlegt (kop: Betekenis voor de Lage Landen) | Algemene heiligenvita zonder LL-band |
| `betekenis` | Feest: 1–3 alinea’s geheim + leiding (vaders/dienstboek primair; grootfeesten t/m Allerzielen-zaterdagen, zie bronnennota) | Heilige (`betekenis_lage_landen`); herhaling van `verhaal`; voorfeest/nafeest/synaxis/weken; tweede vastentabel |
| `goedkeuring` | Feest: wie de betekenistekst goedkeurde (popover op de kop Betekenis) | Heilige/vasten; `bronlaag: nagekeken` als vervanging van een echte toets |
| `verhaal` | Je een leesbaar verhaal hebt met referentie | Ongestaafde AI-tekst zonder bron |
| `selectie` | Heilige: scoort tegen de criteria | Feest/vasten (niet van toepassing) |
| `selectie_toelichting` | Korte reden voor beheer (+ fallback publiek) | Lange essay (gebruik `_publiek`) |
| `selectie_toelichting_publiek` | Bezoekers meer context nodig hebben dan de korte zin | Status `voldoet` (wordt niet getoond) |
| `locaties` | Concrete plaats-ids; streek alleen als aanvulling | Vrije tekst, bedevaarten, “heel Europa” |
| `rustplaats` | Traditionele rustplaats van het lichaam | Reliekenverspreiding |
| `referenties[].inhoud` | Je de lezer vertelt wat die bron biedt | Alleen een kale URL zonder nut |
| `over_bronnen` | Je bronkeuze of vita-discussie toelicht (onder «Over de bronnen») | Herhaling van de hele vita |
| `referenties` | Elke inhoudelijke claim die je toevoegt | Lege “bronnen” zonder locator |
| `bronlaag` | `nagekeken` na lexikon/vita; anders `encyclopedie` | “Voelt betrouwbaar” zonder bron |
| `icoon` / `iconen` | Lokaal bestand met `rechten: ok`, bron en licentie | Hotlink-URL; extra’s zonder `primair` bij meer dan één |
| Extra top-level veld | Notitie/experiment dat de site nog niet toont | Iets dat wél op de site moet (dan eerst schema + generate) |

## JSON Schema valideren

```text
validate
```

Valideert entries tegen `entry.schema.json`. Plaatsen: zie tests
`tests/test_plaatsen.py` en `plaatsen.schema.json` (documentatie +
toekomstige strikte checks).
