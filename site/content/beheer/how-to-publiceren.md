---
title: "Site bouwen en publiceren"
description: "Valideren, genereren, tests, en wat de build overschrijft"
weight: 10
git_date: 2026-08-20
---

Korte reeks voordat u een wijziging in de data of de uitleg publiceert.
Overzicht van paden: [Voor beheerders]({{% ref "/beheer" %}}).

## Lokaal

Vanuit de root van de repo:

1. `python -m pip install -r requirements.txt` (eenmalig of na wijziging van dependencies)
2. `python scripts/validate.py` — YAML tegen het schema en inhoudelijke regels (referenties, iconen)
3. `python -m pytest -q` — onder meer vastenvoorbeelden en handmatige `_index.md`
4. `python scripts/generate.py` — schrijft entry-pagina’s, `entries.json`, `plaatsen.json`, ICS, en de twee vasten-uitlegpagina’s
5. Optioneel met schoonmaak: `python scripts/generate.py --clean` (wist eerst gegenereerde mappen; zelfde eindresultaat als CI)
6. Site bekijken: `scripts/serve.cmd` (Windows) of Hugo serve na generate

Als validate of pytest rood is, niet pushen naar `main`. Een verkeerd
verwacht vastenniveau is meestal: YAML-voorbeeld aangepast, code nog niet.

## Wat generate.py doet

- **Schrijft opnieuw:** `site/content/heiligen/`, `feesten/`, `vasten/`
  (inclusief hun `_index.md`), `site/content/uitleg/vasten.md`,
  `vasten-technisch.md`, `site/static/data/entries.json`,
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
pytest- en generate-stappen.

## Veelgemaakte fout

Tekst «even snel» aanpassen op een heiligenpagina onder
`site/content/heiligen/`. Die pagina is een afdruk. Bij de volgende generate
is de wijziging weg. Zet de tekst in `data/heiligen/<id>.yaml` (inclusief
`namen:`).
