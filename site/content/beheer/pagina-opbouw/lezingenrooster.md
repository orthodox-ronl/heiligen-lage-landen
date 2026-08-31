---
title: "Lezingenrooster"
description: "Contract: Apostel en Evangelie over een periode"
git_date: 2026-08-22
---

**Contract, geen echte inhoud.** Voor wie: bezoeker en clerus. Canonieke
URL: `/lezingenrooster/`. Bron: handmatig
[`site/content/lezingenrooster/_index.md`]({{% ref "/lezingenrooster" %}})
+ JS. Ingang: hoofdnavigatie **Overzichten**.

## Sticky (sitebreed)

**Wel:** de sitenavbar blijft altijd zichtbaar. Daaronder de
pagina-header (zie hieronder), ook tijdens scrollen.

## Titel

**Wel:** de naam Lezingenrooster als info-term, zonder kop in de popover:
korte samenvatting (Apostel en Evangelie over een periode), afgesloten
met ([meer uitleg]({{% ref "/uitleg/lezingen" %}})).

## Sticky header

**Wel:** maandnavigatie `‹ {maand jjjj} ›`; Nieuw/Oud; knop Weergave.
Daaronder de kolomkoppen `Dag`, `Liturgische dag`, `Apostel`,
`Evangelie`. Beide lagen blijven zichtbaar tijdens scrollen. De
maandaanduiding volgt de bovenste zichtbare rij.

**Niet:** een tweede, afwijkende lezingenbron zonder dat de uitleg dat
zegt.

## Weergave (paneel)

**Wel:** keuzes die de tabel filteren of indelen (wat de live pagina
aanbiedt). Korte samenvatting op de knop.

**Niet:** YAML-paden; parochie-ids als primaire UI; uitleg van de
lectionarium-verschuiving (otstupka) op dit scherm (dat hoort op
[Lezingen van de dag]({{% ref "/uitleg/lezingen" %}})).

## Lijst

**Wel:** doorlopende dagen over het beschikbare venster; Apostel en
Evangelie als verwijzing (zelfde links als op de datumpagina); dagen
zonder liturgie van dit type als korte status; maandovergangen met een
scheidingslijn en gecentreerd label `{maand jjjj}`; in de dagkolom
alleen het dagnummer (bijv. `5`), horizontaal en verticaal
gecentreerd; **één rij per burgerlijke dag**; de dag van **vandaag**
herkenbaar aan een gouden rand om de dagcel (zoals in de jaarkalender).
Bij bezoek is die rij in beeld; daarna op/neer scrollen.

**Niet:** volledige Bijbeltekst; heiligenvita’s in de roosterrij;
selectiestatus; volledige datums zoals `5 augustus` in de dagkolom;
zware achtergrondmarkering van de hele rij.
