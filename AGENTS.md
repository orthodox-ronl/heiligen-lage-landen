# AGENTS.md — heiligen-lage-landen

Orthodoxe heiligen- en feestkalender (statische Hugo-site) voor
[orthodox-ronl](https://github.com/orthodox-ronl).

Org-context: [bron/AGENTS.md](https://github.com/orthodox-ronl/bron/blob/main/AGENTS.md).
Terminologie: [bron/docs/specs/terminologie.md](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/terminologie.md).
Scripts: [bron/docs/specs/repo-scripts.md](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/repo-scripts.md).

## Commando's

In de repo-root (`.\scripts` op PATH). Toolchain: Python 3.14, Hugo Extended 0.160.1.

```cmd
cd /d C:\Git\orthodox-groningen\heiligen-lage-landen
test
check
serve
build
icoon
```

| Commando | Doel |
| -------- | ---- |
| `test` | pytest |
| `validate` | YAML/schema-validatie |
| `check` | CI-spiegel (pytest + validate + generate + hugo minify) |
| `serve` | lokale Hugo-preview |
| `build` | statische site in `generated\site` |
| `icoon` | lokaal plaatje als icoon bij bestaande heilige of feest |

## Architectuur

- Brondata: `data/` (YAML); veldrichtlijnen: `schemas/` (+ `schemas/README.md`)
- Validatie/generatie: `scripts/`
- Site: `site/` (Hugo)
- Uitleg: `site/content/uitleg/` (gebruikers) + `*-technisch.md` (niet in het overzicht)
- Beheerders: `site/content/beheer/`
- CI: `.github/workflows/pages.yml` (main → prod, andere branch → `/preview/`)
