---
title: "Heiligenoverzicht"
description: "Contract: zoeken op naam of plaats, kaart, lijst"
git_date: 2026-08-21
---

**Contract, geen echte inhoud.** Voor wie: bezoeker. Canonieke URL:
`/heiligen/`. Bron: gegenereerde `_index.md` uit YAML + layout
`heiligen/list.html`. Ingang: hoofdnavigatie **Overzichten** → Heiligen.

## Titel en korte inleiding

**Wel:** dat dit de heiligen **van de Lage Landen** zijn. Die
woordgroep krijgt een popover: kort het criterium, plus link naar
[uitleg heiligen]({{% ref "/uitleg/heiligen" %}}). Verder: zoeken vindt
ook andere namen en plaatsen; streken cursief.

**Niet:** de selectielijst (`voldoet` / nader onderzoek / kandidaat);
how-to YAML; een tweede beleidstekst naast de uitleg.

## Zoekveld

**Wel:** zoeken op naam (inclusief alternatieve namen) of plaats.
Label **Zoeken (naam of plaats)** in dezelfde lettergrootte als de
lopende tekst, op dezelfde basislijn als de voorbeeldtekst in het veld.

**Niet:** filter op interne `selectie` of `bronlaag` voor bezoekers.

## Kaart

**Wel:** plaatsen uit `plaatsen.yaml` die aan heiligen hangen; klik
naar de gefilterde lijst. Standaarduitsnede: Nederland en België
(plaatsen daarbuiten mogen buiten beeld vallen). In- en uitzoomen met
Ctrl + muiswiel.

**Niet:** plaatsen zonder heilige in deze catalogus als primaire
inhoud; ruwe coördinaten als leestekst; zoomen met het gewone
muiswiel (dat scrollt de pagina).

## Lijst

**Wel:** naam (link), «ook …» bij andere namen, plaatsen (streek
cursief), feestdatum met haakjes voor de oude burgerlijke datum, klein
icoon indien aanwezig. Alle heiligen in de catalogus (ook grensgevallen).

**Niet:** de vita in de rij; `selectie_toelichting`; GitHub-paden.
