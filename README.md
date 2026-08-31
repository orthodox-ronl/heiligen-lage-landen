# Heiligen van de Lage Landen

Overzicht van **heiligen van de Lage Landen**, met orthodoxe **vaste feesten**
(jaarcyclus) en kalender.
MVP: vaste feesten + heiligen van de Lage Landen + Orthodoxe paascyclus
(ICS: huidig jaar −2 … +5).

- Productie: https://orthodox-ronl.github.io/heiligen-lage-landen/
- Preview (niet-`main`): https://orthodox-ronl.github.io/heiligen-lage-landen/preview/

## Wat zit erin

| Onderdeel | Inhoud |
| --------- | ------ |
| Data      | YAML onder `data/` (feesten, heiligen, bronnen) |
| Build     | `validate` / `generate.py` → Hugo-content + ICS |
| Site      | Hugo in `site/` |
| Agenda    | ICS-feeds `/ics/v2/*-{nieuw,oud}.ics` (oud = burgerlijk +13); oude `/ics/*.ics` zijn vervallen-herinneringen |

Datums: default **Gregoriaans** invoer; optioneel `datum.stijl`. Feestdatum =
dagnaam (gelijk in nieuw/oud). Zie [docs/datamodel.md](docs/datamodel.md),
[docs/inventaris.md](docs/inventaris.md) (wie erin hoort),
de pagina **Uitleg** (voor wie de kalender gebruikt) en **Voor beheerders**
(`/beheer/`: wat u mag wijzigen, wat generate overschrijft, how-to’s).

## Commando's

Org-conventie: [repo-scripts](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/repo-scripts.md).
Toolchain: Python **3.14**, Hugo Extended **0.160.1**. In de repo-root (`.\scripts` op PATH):

| Commando | Doel |
| -------- | ---- |
| `test` | pytest |
| `validate` | YAML tegen schema en inhoudelijke regels |
| `check` | CI-spiegel: pytest + validate + generate + Hugo minify |
| `serve` | lokale preview (validate + generate + Hugo server) |
| `build` | statische site in `generated\site` |
| `icoon` | lokaal plaatje als icoon bij bestaande heilige of feest |

```cmd
cd /d C:\Git\orthodox-groningen\heiligen-lage-landen
check
serve
```

Zelfde lijst op de site: **Voor beheerders** → [Commando's](https://orthodox-ronl.github.io/heiligen-lage-landen/beheer/scripts/).

## GitHub Pages

Push naar `main` → productie. Push naar een andere branch → preview onder `/preview/`.
In repo-settings: **Pages → Deploy from a branch → `gh-pages` → `/`**.

## Licentie

Code/scripts: Apache 2.0. Inhoud (YAML/teksten): zie bronvermeldingen per entry; respecteer rechten van externe bronnen en iconen.
