---
title: Vasten (technisch)
description: Koppeling tussen de vastenuitleg, de YAML-regels en de kalendercode
generator: data/regels/vasten.yaml
uitleg_stijl: vasten-technisch
build:
  list: never
  render: always
---

Dit is de technische bijlage bij de [vastenuitleg voor overleg]({{% ref "/uitleg/vasten" %}}).
De cleruspagina beschrijft de regels in gewone taal. Hier staat hoe die regels
in de site vastliggen, zodat een wijziging in de voorbeelden de tests rood
maakt tot de code meegaat.

Bronbestand: `data/regels/vasten.yaml`. Daarna `python3 scripts/generate.py`
(beide uitlegpagina’s worden opnieuw geschreven). De mengregel staat in
`scripts/vasten.py` en, gespiegeld, in `site/assets/js/calendar.js`.
How-to: [vastenregels wijzigen]({{% ref "/beheer/how-to-vasten" %}}).

## Regel-ids

Elke regel heeft een stabiel id (`R-…`). Wijzig je `verwachte_niveau` in `data/regels/vasten.yaml`, dan falen de tests tot `scripts/vasten.py` en `site/assets/js/calendar.js` meegaan.

### R-periode-boven-wekelijks — Een vastenperiode vervangt woensdag- en vrijdagvasten

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-03-20 | `streng` | Vrijdag in de Grote Vasten; het wekelijkse vrijdagvasten wordt niet apart getoond. |
| 2026-08-07 | `streng` | Vrijdag in het Ontslapen-vasten. |
| 2026-07-14 | geen vasten | Dinsdag in juli; geen vastenperiode en geen woensdag of vrijdag. |
| 2026-07-15 | `wijn_olie` | Woensdag in juli; wekelijks woensdagvasten. |

### R-streng-weekend-olie — Zaterdag en zondag in een strenge periode

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-03-21 | `wijn_olie` | Zaterdag in de Grote Vasten. |
| 2026-04-11 | `streng` | Grote Zaterdag; geen weekendversoepeling. |
| 2026-04-10 | `streng` | Grote Vrijdag. |

### R-lichter-weekschema — Apostelen- en Geboortevasten

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-11-20 | `streng` | Vrijdag in het Geboortevasten. |
| 2026-11-17 | `wijn_olie` | Dinsdag in het Geboortevasten. |
| 2026-02-20 | `lichter` | Vrijdag in de Boterweek (zuivel, geen vlees). |

### R-geboortevasten-20-24 — Geboortevasten van 20 tot en met 24 december

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-12-20 | `wijn_olie` | Zondag 20 december, nog Geboortevasten, geen vis. |

### R-feest-versoepelt — Een feest versoepelt, het maakt de periode niet strenger

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-03-25 | `vis` | Aankondiging op woensdag in de Grote Vasten. |
| 2026-08-06 | `vis` | Transfiguratie in het Ontslapen-vasten. |
| 2026-11-21 | `vis` | Tempelgang, een zaterdag in het Geboortevasten (vis volgt al uit het weekschema). |
| 2026-04-05 | `vis` | Palmzondag, tussen de Grote Vasten en de Grote Week. |

### R-lazarus-geen-vis — Lazarus-zaterdag

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-04-04 | `wijn_olie` | Lazarus-zaterdag in 2026. |

### R-grote-week-cap — In de Grote Week geen vis, ook niet op de Aankondiging

Synthetische toets (geen burgerlijke datum):

- weekdag 2, `03-25` → `wijn_olie` — Voorbeeld voor overleg: Aankondiging op Grote Dinsdag.

### R-vastenfeest-buiten-periode — Sommige feesten zijn zelf een vastendag

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-09-14 | `streng` | Kruisverheffing op maandag. |
| 2026-08-29 | `streng` | Onthoofding van Johannes op zaterdag. |
| 2026-12-25 | `vrij` | Kerst op vrijdag; geen vrijdagvasten. |
| 2026-09-08 | geen vasten | Geboorte van de Moeder Gods op dinsdag; die dag is geen vastendag. |

### R-vastenvrije-weken — Vastenvrije weken

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-04-13 | `vrij` | Maandag van de Lichte Week. |

## Niveaus in de data

| Id | Label |
|---|---|
| `streng` | streng |
| `wijn_olie` | wijn en olie |
| `vis` | vis |
| `lichter` | lichter |
| `vrij` | vastenvrij |

Ontbreekt een regel (`mix_vastenniveau` geeft `None`, `verwachte_niveau: null`), dan toont de datumpagina **geen vasten** (`vasten-badge-geen`); ICS vermeldt vasten niet.
