---
title: "Heiligenoverzicht"
description: "Contract: zoeken op naam of plaats, kaart, tabel"
git_date: 2026-08-23
---

**Contract, geen echte inhoud.** Voor wie: bezoeker. Canonieke URL:
`/heiligen/` (zelfde weergave op `/`). Bron: gegenereerde `_index.md`
uit YAML + partial `heiligen-overzicht.html`. Ingang: sitenaam of
hoofdnavigatie **Heiligen**. **Vandaag** in de nav opent de
[datumpagina]({{% ref "/beheer/pagina-opbouw/datumpagina" %}}).

## Sticky (sitebreed)

**Wel:** de sitenavbar blijft altijd zichtbaar. Daaronder de
pagina-header (zoeken, sorteren, kolomkoppen).

## Titel en korte inleiding

**Wel:** titel **Heiligen van de Lage Landen**. Inleiding: hoeveel
heiligen erin staan; dat dit heiligen **van de Lage Landen** zijn (die
woordgroep krijgt een popover: kort het criterium, plus link naar
[uitleg heiligen]({{% ref "/uitleg/heiligen" %}})); wie hier predikte,
stichtte of leed, of na het schisma de Orthodoxie hier hielp opbouwen;
niet iedere heilige van de Kerk; enkele bekende namen als link; zoeken
vindt ook andere namen en plaatsen; streken cursief.

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
aanwezig. Feestdatum met haakjes voor de oude burgerlijke datum indien
die verschilt. Alle heiligen in de catalogus (ook grensgevallen).

**Niet:** de vita in de rij; `selectie_toelichting`; GitHub-paden;
meerdere rijen voor dezelfde datum of plaats bij die sorteermodi.
