---
title: "Heiligenoverzicht"
description: "Contract: zoeken op naam of plaats, kaart, tabel"
git_date: 2026-08-23
---

**Contract, geen echte inhoud.** Voor wie: bezoeker. Canonieke URL:
`/heiligen/`. Bron: gegenereerde `_index.md` uit YAML + layout
`heiligen/list.html`. Ingang: hoofdnavigatie **Overzichten** → Heiligen.

## Sticky (sitebreed)

**Wel:** de sitenavbar blijft altijd zichtbaar. Daaronder de
pagina-header (zoeken, sorteren, kolomkoppen).

## Titel en korte inleiding

**Wel:** dat dit de heiligen **van de Lage Landen** zijn. Die
woordgroep krijgt een popover: kort het criterium, plus link naar
[uitleg heiligen]({{% ref "/uitleg/heiligen" %}}). Verder: zoeken vindt
ook andere namen en plaatsen; streken cursief.

**Niet:** de selectielijst (`voldoet` / nader onderzoek / kandidaat);
how-to YAML; een tweede beleidstekst naast de uitleg.

## Sticky header

**Wel:** zoekveld; sorteerkeuze Naam (default) / Datum / Plaats;
kolomkoppen die bij de sorteerkeuze horen.

**Niet:** filter op interne `selectie` of `bronlaag` voor bezoekers.

## Zoekveld

**Wel:** zoeken op naam (inclusief alternatieve namen) of plaats.
Label **Zoeken (naam of plaats)** in dezelfde lettergrootte als de
lopende tekst, op dezelfde basislijn als de voorbeeldtekst in het veld.

## Kaart

**Wel:** plaatsen uit `plaatsen.yaml` die aan heiligen hangen; klik
naar de gefilterde lijst. Standaarduitsnede: Nederland en België
(plaatsen daarbuiten mogen buiten beeld vallen). In- en uitzoomen met
Ctrl + muiswiel.

**Niet:** plaatsen zonder heilige in deze catalogus als primaire
inhoud; ruwe coördinaten als leestekst; zoomen met het gewone
muiswiel (dat scrollt de pagina).

## Tabel (onder de kaart)

**Wel:** tabelvorm. Sorteren op **naam**: één rij per heilige
(Naam | Plaatsen | Feestdatum). Sorteren op **datum**: één rij per
feestdatum (Dag | Heiligen | Plaatsen), maandovergangen met
scheidingslijn; dagkolom gecentreerd. Sorteren op **plaats**: één rij
per plaats (Plaats | Heiligen | Feestdatum). Klein icoon indien
aanwezig. Alle heiligen in de catalogus (ook grensgevallen).

**Niet:** de vita in de rij; `selectie_toelichting`; GitHub-paden;
meerdere rijen voor dezelfde datum of plaats bij die sorteermodi.
