---
title: Jaarkalender (technisch)
description: Layout, calendar.js, kleurenklassen en het ICS-venster
uitleg_stijl: jaarkalender-technisch
build:
  list: never
  render: always
git_date: 2026-08-31
---

Technische bijlage bij de [uitleg Jaarkalender]({{% ref "/uitleg/jaarkalender" %}}).

## Pagina

- `/kalender/` — layout `site/layouts/_default/kalender.html`
- Body van `site/content/kalender/_index.md` blijft bij genereren staan
- Raster: `site/assets/js/calendar.js` (jaargrid); zonder JavaScript:
  verwijzing naar Synaxarion en Agenda
- Data: `entries.json` (in de HTML ingebed, anders fetch)

Titel-popover: `data-info-tip="jaarkalender"` (geen kop in de popover;
samenvatting plus link naar deze uitleg, daaronder Agenda).

## Venster

Zelfde periode als de ICS-feeds: huidig burgerlijk jaar −2 … +5. Geen
jaartal-navigatie in de sticky header; de bezoeker scrollt. Tussen
december van jaar *j* en januari van *j*+1 een jaarovergangslijn.

## Kleuren

Zelfde klassen als
[Kleuren (technisch)]({{% ref "/uitleg/kleuren-technisch" %}}). «Vandaag»
is een omlijning, geen extra legendaitem.

## Tests

`tests/test_kalender_verbeteringen.py` (legenda, titel-popover),
`tests/test_uitleg_splitsing.py` (zelfde swatches als de uitleg Kleuren).
