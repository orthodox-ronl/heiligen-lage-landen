---
title: "Commando's"
description: "Lokale scripts: test, validate, check, serve, build, icoon"
weight: 5
git_date: 2026-08-30
---

Voor wie de kalender in git bijhoudt. Org-conventie:
[repo-scripts](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/repo-scripts.md)
(Python 3.14, Hugo Extended 0.160.1, `.\scripts` op PATH).

Werk in de **repo-root**:

```cmd
cd /d C:\Git\orthodox-groningen\heiligen-lage-landen
```

| Commando | Doel |
| -------- | ---- |
| `test` | pytest (o.a. vastenvoorbeelden en handmatige `_index.md`) |
| `validate` | YAML tegen het schema en inhoudelijke regels (referenties, iconen) |
| `check` | CI-spiegel: pytest + validate + generate `--clean` + Hugo minify. Groen ≈ veilig om te pushen |
| `serve` | lokale preview (validate + generate + Hugo op http://127.0.0.1:1313/) |
| `build` | zelfde generate-keten als publiceren, output in `generated\site` |
| `icoon` | lokaal plaatje als icoon bij bestaande heilige of feest (eerst licentie/rechten) |

Scripts installeren ontbrekende Python-packages zelf. Ontbreekt Python, Hugo of `.\scripts` op PATH, dan stopt het commando met een hersteltekst.

Voor push naar `main`: `check` groen. Zie [Site bouwen en publiceren]({{% ref "/beheer/how-to-publiceren" %}}) voor wat generate overschrijft.

`icoon` begint met licentie/rechten; zonder PD, CC0, CC BY of CC BY-SA
stopt het, tenzij u die gegevens wijzigt. Het pad mag als eerste
argument: `icoon foto.png`. How-to:
[heilige of feest]({{% ref "/beheer/how-to-heiligen-feesten" %}}) (Icoon).
