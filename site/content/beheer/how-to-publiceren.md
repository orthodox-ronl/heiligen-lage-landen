---
title: "Site bouwen en publiceren"
description: "Valideren, genereren, tests, en wat de build overschrijft"
weight: 10
git_date: 2026-08-20
---

Korte reeks voordat u een wijziging in de data of de uitleg publiceert.
Overzicht van paden: [Voor beheerders]({{% ref "/beheer" %}}).

## Lokaal

Vanuit de root van de repo (`.\scripts` op PATH; Python 3.14, Hugo Extended 0.160.1).
Commando's: [Commando's]({{% ref "/beheer/scripts" %}}).

1. `check` — pytest, validate, generate `--clean`, Hugo minify (zelfde blocking stappen als CI)
2. Lokaal bekijken: `serve` (of na een groene check alleen de server als de generated content al bestaat: opnieuw `serve`)

Als `validate` of `test` rood is, niet pushen naar `main`. Een verkeerd
verwacht vastenniveau is meestal: YAML-voorbeeld aangepast, code nog niet.

## Wat generate.py doet

- **Schrijft opnieuw:** `site/content/heiligen/`, `feesten/`, `vasten/`
  (inclusief hun `_index.md`), `site/content/uitleg/vasten.md`,
  `vasten-technisch.md`, `site/static/data/entries.json`,
  `site/static/data/synaxarion.json`,
  `site/static/data/plaatsen.json`, `site/static/ics/*.ics`.
- **Laat staan (body):** `site/content/_index.md`, `kalender/_index.md`,
  `synaxarion/_index.md`, `datum/_index.md`, `agenda/_index.md`,
  `uitleg/_index.md`, en de overige uitleg-markdown (behalve vasten*).
- **Corrigeert alleen layout** op die handmatige indexes als die ontbreekt
  of afwijkt.

Met `--clean` verdwijnen bovendien extra bestanden onder
`site/content/datum/` (niet `_index.md`) en de oude ICS-files voordat ze
opnieuw worden gezet.

## Publiceren

Push naar `main` → productie
(https://orthodox-ronl.github.io/heiligen-lage-landen/).

Push naar een andere branch → preview onder `/preview/`.

CI (`.github/workflows/pages.yml`) doet: pytest → validate →
`generate.py --clean` → Hugo → deploy naar `gh-pages`. U hoeft lokaal geen
`generated/` te committen. `validate.yml` (pull requests) draait dezelfde
pytest- en generate-stappen. Lokaal: `check`.

## Veelgemaakte fout

Tekst «even snel» aanpassen op een heiligenpagina onder
`site/content/heiligen/`. Die pagina is een afdruk. Bij de volgende generate
is de wijziging weg. Zet de tekst in `data/heiligen/<id>.yaml` (inclusief
`namen:`).
