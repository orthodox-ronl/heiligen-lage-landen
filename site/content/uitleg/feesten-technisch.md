---
title: Overzicht van feesten (technisch)
description: "Rangschikking op /feesten/: layout, JS, groepen en URL"
uitleg_stijl: feesten-technisch
build:
  list: never
  render: always
git_date: 2026-08-30
---

Technische bijlage bij de [uitleg Overzicht van feesten]({{% ref "/uitleg/feesten" %}}).

## Pagina

- `/feesten/` — layout `site/layouts/feesten/list.html` (niet de
  vasten-index; die blijft `_default/list.html`)
- Standaardvolgorde zonder JavaScript: `Params.overzicht_sortering`
  (kerkelijk jaar, daarna paascyclus, daarna wekelijks), gezet in
  `scripts/generate.py`
- Met JavaScript: `site/assets/js/feesten-overzicht.js` herschikt de
  bestaande rijen en zet groepskoppen

## Keuze van de bezoeker

Query: `?rangschikking=` met `kerkelijk` (default, parameter weggelaten),
`burgerlijk`, `rang` of `naam`. De URL wint van `localStorage`
(`feesten-rangschikking`). `history.replaceState`, geen extra history-stap.

Nieuw/Oud (`stijl`) blijft een andere as; de JS-sortering gebruikt de
feestdatum (`data-mmdd`), niet de burgerlijke vierdatum.

## Groep «naar rang»

Front matter `overzicht_rang` (alleen `soort: feest`), functie
`overzicht_rang` in `generate.py`:

| Waarde | Wie |
| --- | --- |
| `grote` | ids in `GROTE_FEESTEN` (twaalf plus Pascha) |
| `omlijsting` | id begint met `voorfeest-`, `nafeest-`, `teruggave-`, `synaxis-` |
| `heer-moeder` | o.a. Besnijdenis, Pokrov |
| `apostelen` | Petrus en Paulus, geboorte en onthoofding van Johannes |
| `paascyclus` | overige `cyclus: paascyclus` |
| `overig` | rest van de jaarcyclus |

Binnen een groep: kerkelijk jaar, daarna naam. Op één dag: rang, dan naam.

Popovers: `data-info-tip="feesten-rangschikking"` en `kerkelijk-jaar` in
`calendar.js`.
