---
title: Datumpagina’s (technisch)
description: URL-parameters, entries.json en wat de dagweergave toont
uitleg_stijl: datumpagina-technisch
build:
  list: never
  render: always
git_date: 2026-08-30
---

Technische bijlage bij de [uitleg Datumpagina’s]({{% ref "/uitleg/datumpagina" %}}).

## Adres

`/datum/?datum=2026-08-15`

- `datum` — burgerlijk `jjjj-mm-dd`
- `stijl` — alleen `juliaans` als de oude kalender aan staat

Oude adressen `?jaar=` + `?dag=` (MM-DD) blijven leesbaar; de pagina
zet ze om naar `?datum=`. Alleen `?dag=MM-DD` (feestdag-link zonder
jaar) betekent dat feest in het lopende burgerlijke jaar.

Ontbreekt `datum`, dan vult `site/assets/js/calendar.js` «vandaag»
(startpagina).
De layout is `site/layouts/_default/datum.html`; de body van
`site/content/datum/_index.md` blijft bij genereren staan (handmatig
beheerd).

## Brondata in de browser

De pagina leest `entries.json` (in de HTML ingebed, anders fetch van
`site/static/data/entries.json`). Per entry
staan onder meer `soort`, `cyclus`, `feestdatum`, `occurrences` (paascyclus)
en `period_occurrences` (periodes). Wijzig die JSON **niet** met de hand;
`scripts/generate.py` schrijft hem opnieuw. Zonder JavaScript verwijst de
pagina naar het Synaxarion.

## Wat er op een dag komt

Op de burgerlijke datum van dat jaar, in deze volgorde:

1. Vastenbadge vóór Nieuw/Oud: effectief niveau, of `geen` (`vasten-badge-geen`)
   als `mixVastenniveau` `null` teruggeeft. Bij een named
   periode de periodenaam tussen haakjes, met link naar de entry-pagina
   (`/vasten/…/` of `/feesten/…/` voor vastenvrije weken). Hover/klik op
   de badge opent een korte uitleg (`data-info-tip="vasten-niveau"`).
2. Dagtype: naam van het feest (`soort: feest`, geen periode), anders
   `daglabel` uit `lezingen-dagen.json` (bijv. «23e donderdag na Pinksteren»),
   met popover `data-info-tip="dagtype"`.
   Heeft het eerste dagtype-feest (paascyclus vóór jaarcyclus) een
   `icoon` in `entries.json` (dat is altijd het primaire, `rechten: ok`):
   `renderDagIcoonHtml` zet `figure.today-dag-icoon` ernaast
   (`div.today-dag-hoofd`). Extra items uit YAML `iconen` komen niet
   op deze pagina. Geen icoon bij alleen een weeknaam (`daglabel`).
3. Apostel en Evangelie (zonder kop «Lezingen»); de labels hebben
   `data-info-tip="lezing"` (keuze van de dag: weekreeks / feest /
   menaion). Verwijzingen linken
   naar het hoofdstuk op debijbel.nl (`a.bijbel-link`, vertaling in
   `localStorage` `bijbel-vertaling`, default HSV; ids als op debijbel.nl:
   HSV, NBV, NBV21, BGT, NBG51, NFB, UTT).
4. Alleen als er heiligen zijn: kop «Heilige(n) van de dag»
   (`data-info-tip="heiligen-criterium"`), daaronder de
   lijst, met `icoon` uit `entries.json` als dat veld gezet is
   (`img.today-heilige-icoon`). Extra iconen van dezelfde heilige niet
   in de lijst. Zonder heilige: geen kop, wel `today-geen-heilige` met
   link naar uitleg/heiligen (geen icoon bij die link).

De datum tussen de pijlen (`dayTitleHtml`) heeft de popup over de
burgerlijke dag; *(vandaag)* hoort daarbij. De toon staat ná de pijl naar
de volgende dag (`dayToonHtml`, `data-info-tip="toon"`). Formule:
`octoechosToon` in `calendar.js`, zelfde als `octoechos_toon` in
`scripts/kalender.py`. Zie
[Toon van de week (technisch)]({{% ref "/uitleg/toon-technisch" %}}).

Brondata voor (1) en (4): vaste feesten en heiligen op feestdatum (Nieuw)
of burgerlijke vierdatum (Oud); paascyclus op de berekende datum; vastenperiodes
die die dag dekken, plus wekelijks vasten als er geen periode of vastenvrije
week is.

Effectief vastenniveau: `scripts/vasten.py` / dezelfde mengregel in
`calendar.js`. Zie [Vasten (technisch)]({{% ref "/uitleg/vasten-technisch" %}}).

Het Synaxarion filtert op feestdatum zonder jaar; zie
[Synaxarion (technisch)]({{% ref "/uitleg/synaxarion-technisch" %}}).
