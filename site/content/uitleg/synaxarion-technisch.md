---
title: Synaxarion (technisch)
description: "Technische bijlage: URL’s, layout en welke cycli het Synaxarion toont"
uitleg_stijl: synaxarion-technisch
build:
  list: never
  render: always
git_date: 2026-08-20
---

Technische bijlage bij de [uitleg Synaxarion]({{% ref "/uitleg/synaxarion" %}}).

## Adressen

- `/synaxarion/` — bladeren (maand of alfabet) en zoeken
- `/synaxarion/?dag=08-15` — vaste cyclus van die feestdatum (MM-DD)

Layout: `site/layouts/_default/synaxarion.html`. De bladerlijst (maanden)
staat in de HTML via `site/static/data/synaxarion.json` (na `generate.py`).
Zoeken, alfabet en `?dag=` blijven JavaScript; die leest
`entries.json` (in de pagina ingebed, anders via fetch).

## Welke entries

Het Synaxarion toont entries met een vaste plaats in het jaar:

- heiligen en feesten met `datum.waarde` (MM-DD)
- vaste vastenperiodes met `van`/`tot` in het burgerlijke jaar

Niet: paascyclus, wekelijkse vasten, of “zondag na Kerst”-achtige regels.

## Iconen in de lijst

In de Synaxarion-tabel toont `synaxarionTableHtml` een klein icoon als
`entries.json` een lokaal bestand met `rechten: ok` heeft.

## Koppeling met de datumpagina

Onderaan een vaste dag staan links naar Synaxarion en datumpagina. Die
scheiden vaste cyclus (zonder jaar) van “wat valt er op deze burgerlijke dag
in dit jaar”.
