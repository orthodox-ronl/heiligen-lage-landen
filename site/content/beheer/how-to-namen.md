---
title: "Weergavenamen wijzigen"
description: "Namen in het entry-YAML; ids en bestandsnamen blijven stabiel"
weight: 30
git_date: 2026-08-20
---

De **getoonde naam** van een heilige, feest of vasten staat in het
entry-bestand zelf: `namen.primair` en optioneel `namen.alternatief`.
Het **id** (bestandsnaam van de YAML) blijft gelijk. Zoeken in het Synaxarion
gebruikt ook de alternatieve namen.

How-to entries: [heilige of feest]({{% ref "/beheer/how-to-heiligen-feesten" %}}).

## Waar

In `data/heiligen/<id>.yaml`, `data/feesten/<id>.yaml` of
`data/vasten/<id>.yaml`:

```yaml
namen:
  primair: Aankondiging aan de Moeder Gods
  alternatief:
  - Aankondiging
  - Annunciatie
```

`primair` is verplicht. `alternatief` is een lijst; die namen zijn
zoekbaar en mogen als «ook …» zichtbaar zijn, maar niet de titel van de
pagina.

Er is geen aparte `namen.yaml` meer. Elke term met een eigen naam hoort
een eigen entry-YAML te hebben (of als zoekalias onder een bestaande
entry).

## Conventie voor `primair`

Doel: overal dezelfde logica — korte, herkenbare titel; geen mix van
`Naam`, `Naam van Plaats` en `Naam (van Plaats)` zonder regel.

### Heiligen

- Geen voorvoegsel «heilige» of «sint» in `primair`.
- Standaard: alleen de **roepnaam** (`Willibrord`, `Ludger`, `Bonifatius`)
  als die in *deze* catalogus uniek is en zo gangbaar is.
- Voeg **`van {ankerplaats}`** toe (of een vast epitheton zoals
  `van Shanghai`, `de Belijder`) **alleen** als:
  - er anders verwarring is met een andere entry in deze catalogus, of
  - die toevoeging tot de gewone aanduiding van deze heilige hoort.
- **Geen haakjes:** `Ansfried van Utrecht`, nooit `Ansfried (van Utrecht)`.
- Kies **één** ankerplaats (bisdom, stichting of rustplaats — wat de
  identiteit in onze lijst draagt). Andere toeschrijvingen en spellingen
  horen in `alternatief` (bijv. `Servatius van Tongeren` naast primair
  `Servatius`).

Voorbeelden:

| Situatie | `primair` | `alternatief` (voorbeelden) |
| --- | --- | --- |
| Uniek en gangbaar | `Ludger` | `Liudger` |
| Twee Amalberga’s | `Amalberga van Temse` | `Amalberga` |
| Gangbaar epitheton | `Johannes van Shanghai` | andere vormen |

### Feesten en vasten

- Liturgische of gangbare **dag-/periodenamen** (`Besnijdenis des Heren`,
  `Apostelvasten`). Geen persoons-`van`-patroon.
- Korte zoekvormen in `alternatief` (`Aankondiging`, `Annunciatie`).
- Dagaliassen bij de dag-entry (bijv. `Vleesvaarwel` bij
  `zondag-laatste-oordeel`, `Zuivelvaarwel` bij `vergevingszondag`).
  Een **week** of periode (Boterweek) heeft een eigen YAML.

### Id versus weergave

Het **id** mag `-van-plaats` bevatten (stabiele URL’s). Dat dwingt
`primair` niet: een id `adelbert` kan primair `Adelbert` hebben terwijl
`Adelbert van Egmond` in `alternatief` staat.

## Wat er gebeurt

Na wijzigen:

```text
python scripts/generate.py
```

Overal waar de naam staat (pagina, Synaxarion, kalender, ICS-titel) volgt de
nieuwe primaire naam. Oude ICS-agenda abonnees zien de nieuwe titel na de
volgende publicatie.

## Wat u niet doet

- Het id / de bestandsnaam hernoemen «omdat de spelling anders moet» —
  dat verbreekt links en ICS-uids. Liever `primair` aanpassen en de oude
  spelling onder `alternatief` houden.
- Alleen `site/content/heiligen/<id>.md` aanpassen — die pagina wordt
  overschreven.
- Technische `id_aliassen` als leesbare «ook»-namen gebruiken — dat zijn
  oude ids voor redirects; leesbare namen horen in `alternatief`.
