---
title: "Synaxarion"
description: "Contract: vaste jaarcyclus, zoeken en bladeren"
git_date: 2026-08-22
---

**Contract, geen echte inhoud.** Voor wie: bezoeker. Canonieke URL:
`/synaxarion/`. Bron: handmatig
[`site/content/synaxarion/_index.md`]({{% ref "/synaxarion" %}}) + JS.

Dit is de ingang op **feestdatum** (wat altijd bij 15 augustus hoort),
niet op één burgerlijk jaar. Zie
[Datumpagina]({{% ref "/beheer/pagina-opbouw/datumpagina" %}}) voor het
verschil.

## Sticky (sitebreed)

**Wel:** de sitenavbar blijft altijd zichtbaar. Daaronder de
pagina-header (zie hieronder), ook tijdens scrollen.

## Titel

**Wel:** de naam Synaxarion; geen tweede ondertitel die het tot
menaion maakt.

**Niet:** hymnen, diensten, typikon-rubrieken.

## Sticky header

**Wel (maandmodus):** `‹ {maand} ›`; Nieuw/Oud (bepaalt welke
feestdatum «vandaag» is); knop Weergave; kolomkoppen `Dag`, `Naam`,
`Soort`. De maandaanduiding volgt de bovenste zichtbare rij.

**Wel (alfabet / zoeken):** letterchips of zoekcontext in de header;
zelfde kolomkoppen; filters in Weergave.

## Weergave (paneel)

**Wel:** filter heiligen / feesten / vasten; zoeken (ook andere namen);
bladeren op maand of alfabet. Label van het zoekveld in dezelfde
lettergrootte en op dezelfde basislijn als de voorbeeldtekst in het
veld.

**Niet:** dagen van de paascyclus, wekelijks wo/vr-vasten, of zondagen
die van de weekdag van Kerst/Theofanie afhangen (die horen bij een
jaar → datumpagina).

## Lijst (maandmodus)

**Wel:** doorlopende vaste jaarcyclus (januari–december); eerste kolom
`Dag` met dagnummer (horizontaal en verticaal gecentreerd); **één rij
per feestdatum** met namen en soorten van die dag in de overige
kolommen, onder elkaar in dezelfde volgorde (belangrijkste boven:
genoemd feest, heilige, voor-/nafeest of teruggave, vastenperiode);
maandovergangen met scheidingslijn en gecentreerd maandlabel; de
feestdatum van **vandaag** herkenbaar aan een gouden rand om de dagcel
(zoals in de jaarkalender). Bij bezoek is die rij in beeld.

**Niet:** `selectie:` of «kandidaat-schrappen»; beheerpaden; de volle
vita in de lijst; een regel «{maand}: {n} items»; meerdere rijen voor
dezelfde feestdatum; zware achtergrondmarkering van de hele rij.

## Dagweergave (`?dag=MM-DD`)

**Wel:** de entries van die feestdatum; navigatie vorige/volgende dag;
link naar dezelfde dag in het lopende burgerlijke jaar.
