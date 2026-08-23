---
title: Heiligen van de Lage Landen (technisch)
description: Selectievelden, bronlaag, id_aliassen; bron is YAML onder data/heiligen/
uitleg_stijl: heiligen-technisch
build:
  list: never
  render: always
git_date: 2026-08-20
---

Technische bijlage bij de [uitleg Heiligen]({{% ref "/uitleg/heiligen" %}}).

Normatief datamodel: [docs/datamodel.md](https://github.com/orthodox-ronl/heiligen-lage-landen/blob/main/docs/datamodel.md).
Schema: `schemas/entry.schema.json`. How-to:
[heiligen en feesten wijzigen]({{% ref "/beheer/how-to-heiligen-feesten" %}}).
Validatie: `python scripts/validate.py`.

Bron: `data/heiligen/<id>.yaml`. Gegenereerde markdown onder
`site/content/heiligen/` niet redigeren.

## Selectiecriteria (normatief)

Zie de gebruikerspagina voor de formulering in gewone taal. In YAML:

```yaml
selectie: voldoet   # voldoet | nader-onderzoek | kandidaat-schrappen
selectie_toelichting: "Kort waarom (beheer; fallback op de pagina)."
selectie_toelichting_publiek: |
  Optioneel: leesbare uitleg op de heiligenpagina.
```

- Ontbreekt `selectie` bij een heilige: behandel als `nader-onderzoek`
  (`scripts/load_entries.py`).
- Bij `nader-onderzoek` of `kandidaat-schrappen` schrijft `generate.py`
  onderaan een uitklap **Plaats in deze kalender** (`<details>`). Gebruik
  `selectie_toelichting_publiek` als die afwijkt van de korte beheerzin.
  Bij `voldoet`: geen uitklap.
- `datum.waarde` is de canonieke gedenkdag (sterfdag bij twijfel).
  Orthodox bekende extra dagen: `datum.extra` → **Andere gedenkdagen**
  op de pagina, niet in de infobox.
- `selectie` zelf komt **niet** in de Hugo-front matter (geen filterveld
  voor bezoekers).
- Overzicht voor beheerders: `/beheer/selectie/` (gegenereerd; live telling).
- `kandidaat-schrappen` verwijdert niets; dat is een markering tot een
  expliciet besluit.
- **Indirecte invloed** (deur open, niet actief verzamelen): typisch
  `nader-onderzoek`, met uitleg op de pagina. Zie gebruikersuitleg.

Beslissingslog (geen catalogusdump):
[docs/inventaris.md](https://github.com/orthodox-ronl/heiligen-lage-landen/blob/main/docs/inventaris.md).
`selectie` staat per heilige in YAML; overzicht `/beheer/selectie/`.

Onbekende YAML-velden op een entry zijn toegestaan (experimenten/notities);
zie [schemas/README.md](https://github.com/orthodox-ronl/heiligen-lage-landen/blob/main/schemas/README.md).

## Betekenis voor de Lage Landen

```yaml
betekenis_lage_landen: |
  Apart stuk: betekenis voor het christendom of de Orthodoxie
  in de Lage Landen.
```

Verplicht bij `bronlaag: nagekeken` voor `soort: heilige`. Als het veld
gezet is, gelden dezelfde referentie-eisen als bij `verhaal` /
`samenvatting`. `generate.py` zet het onder **Betekenis voor de Lage Landen**
(vóór samenvatting/verhaal) en in `entries.json` (veld
`betekenis_lage_landen`, alleen heiligen).

## Bronlaag

`bronlaag: encyclopedie` of `bronlaag: nagekeken` (default: encyclopedie).
Zelfde paginastructuur; de publieke zin zegt hoe stevig de basis is.

`validate.py` weigert `bronlaag: nagekeken` bij een heilige tenzij:

1. `betekenis_lage_landen` niet leeg is, en
2. minstens één referentie **niet** Wikipedia of heiligen.net is
   (`bron_id` `wiki-heiligen` / `hnet`, of url/label met `wikipedia.org` /
   `heiligen.net`; OrthodoxWiki telt wél als eigen bron).

Feesten en vasten: `nagekeken` blijft nagekeken tekst met traceerbare
bronnen.

Verouderd: `status: stub` / `status: curated` (vervangen door bronlaag).

## Eén persoon, één id

Canonieke weergavenamen: `namen.primair` + `namen.alternatief` in het
entry-YAML. Conventie voor wat in `primair` hoort (roepnaam vs.
`van {plaats}`, feesten, geen haakjes):
[Weergavenamen wijzigen]({{% ref "/beheer/how-to-namen" %}}).
Na samenvoegen van dubbele bestanden:

```yaml
id: lebuinus
id_aliassen:
  - lubuinus
```

- `id_aliassen`: oude ids, patroon `[a-z0-9_-]+`, niet het eigen id, niet
  een nog levend entry-id, uniek over de catalogus. Wordt Hugo `aliases`.
- Zet de oude naam(en) ook onder `namen.alternatief`, anders
  vindt zoeken ze niet (Synaxarion en heiligenindex).

## Referenties

Zie [docs/datamodel.md](https://github.com/orthodox-ronl/heiligen-lage-landen/blob/main/docs/datamodel.md).
Wikipedia en heiligen.net mogen aanvullen.

## Plaatsen en rustplaats

```yaml
locaties:
  - utrecht
  - echternach
rustplaats:
  plaats: echternach
  toelichting: "Abdij van Echternach"
```

Plaats-ids staan in `data/plaatsen.yaml` (naam, coördinaten, optioneel
`streek` en `alternatief`). Een `soort: plaats` krijgt een marker als
minstens één heilige die id in `locaties` heeft. Een `soort: streek`
alleen als een heilige die streek-id zelf noemt. Op een heilige: liever
concrete plaatsen; streek-ids alleen als aanvulling of bij gebrek aan
een betere plek. Relieken en bedevaarten horen niet in dit veld.

`generate.py` schrijft `site/static/data/plaatsen.json` en zet
plaatsnamen plus zoektekst op de heiligenpagina.

## Icoon

```yaml
icoon:
  bestand: iconen/willibrord.jpg   # onder site/static/
  rechten: ok                      # alleen dan toont generate de afbeelding
  licentie: "Publiek domein"       # of bv. CC0, CC BY-SA 4.0
  bron: "Wikimedia Commons — File:…"
```

Alleen een **lokaal** bestand. `validate.py` weigert een URL in `bestand`
(geen hotlink vanuit de browser). Zonder duidelijke licentie: het veld
weglaten. Twintigste-eeuwse foto’s en recente iconen zijn meestal nog
beschermd.

How-to: [heiligen en feesten wijzigen]({{% ref "/beheer/how-to-heiligen-feesten" %}}).
