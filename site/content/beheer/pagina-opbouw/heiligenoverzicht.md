---
title: "Heiligenoverzicht"
description: "Contract: zoeken, filter Opgenomen/Alles, weergave lijst/kaart, tabel"
git_date: 2026-08-30
---

**Contract, geen echte inhoud.** Voor wie: bezoeker. Canonieke URL:
`/heiligen/` (zelfde weergave op `/`). Bron: gegenereerde `_index.md`
uit YAML + partial `heiligen-overzicht.html`. Ingang: sitenaam of
hoofdnavigatie **Heiligen**. De dagkaart van vandaag staat op de
[datumpagina]({{% ref "/beheer/pagina-opbouw/datumpagina" %}}).

## Sticky (sitebreed)

**Wel:** de sitenavbar blijft altijd zichtbaar. Daaronder de
pagina-header.

## Sticky header

**Wel:** titel **Heiligen van de Lage Landen** met popover (criterium,
link naar [uitleg heiligen]({{% ref "/uitleg/heiligen" %}})) en het
**aantal** tussen haakjes (volgt Opgenomen/Alles en de zoekterm);
zoekveld; **Toon:** Opgenomen (default) / Alles, met popover op het
label; **Weergave:** Lijst (default) / Kaart, met popover op het label;
**Sorteren:** Naam (default) / Datum / Plaats, met popover op het
label; een balk **Kaart van plaatsen** onder het zoeken (klikt open tot
een kaart; klapt in bij scrollen naar beneden, behalve in
kaartweergave). Keuzes blijven in `localStorage`.

**Niet:** een aparte zin onder de titel alleen voor die popover; de
uitgeklapte kaart als vast plakblok op een smal scherm; interne tokens
(`voldoet` / `nader-onderzoek` / `kandidaat-schrappen`) op knoppen;
YAML-filter voor bezoekers; knoptekst **Kalender** (dat is de
jaarkalender); standaard Alles op de homepage.

## Titel en korte inleiding

**Wel:** titel zoals hierboven. De rest van de uitleg staat achter
**Over deze lijst**, in welgevormde Nederlandse zinnen, en gaat over
**de lijst zelf**: wie erin hoort en wie niet (met link naar de
uitleg); hoeveel namen in **nader onderzoek** of **kandidaat** staan
als die groepen bestaan; de **datumpagina** van de eerstvolgende
zondag waarop de lokale Kerk de heiligen van de Lage Landen gedenkt
(tweede zondag na Pinksteren); enkele bekende namen als link; hoe
zoeken en de kaart werken; streken cursief.

**Niet:** de interne tokens in de inleiding; how-to YAML; een tweede
beleidstekst naast de uitleg; uitleg van de knoppen Toon/Weergave/
Sorteren (die hoort in de popovers bij die labels); zinnen zonder
persoonsvorm of zonder onderwerp.

## Zoekveld

**Wel:** zoeken op naam (inclusief alternatieve namen) of plaats.
Label **Zoeken (naam of plaats)** in dezelfde lettergrootte als de
lopende tekst, op dezelfde basislijn als de voorbeeldtekst in het veld.

## Kaart

**Wel:** plaatsen uit `plaatsen.yaml` die aan **zichtbare** heiligen
hangen (volgt Opgenomen/Alles en zoeken); klik op een marker filtert de
lijst op die plaats. Standaarduitsnede: Nederland en België (plaatsen
daarbuiten mogen buiten beeld vallen). In- en uitzoomen met Ctrl +
muiswiel. In **Lijst** is de kaart standaard ingeklapt tot de balk;
in **Kaart** staat de kaart groot open. Na openen in lijst: inklappen
bij scrollen naar beneden.

**Niet:** plaatsen zonder heilige in de huidige keuze als primaire
inhoud; ruwe coördinaten als leestekst; zoomen met het gewone
muiswiel (dat scrollt de pagina).

## Tabel

**Wel:** tabelvorm. Kolomkoppen blijven zichtbaar bij scrollen (plakken
onder de pagina-header, niet boven de inleiding). Sorteren op **naam**:
bij **Alles** groepen *In de kalender*, *Nader onderzoek* en
*Kandidaat (niet in de kalender)* (kop alleen als er meer dan één groep
is); binnen een groep één rij per heilige (Naam | Plaatsen |
Feestdatum), met een korte categorie bij nader onderzoek en kandidaat.
Bij **Opgenomen** alleen wie voldoet, zonder groepskoppen. Sorteren op
**datum**: één rij per feestdatum (Dag | Heiligen | Plaatsen); bij elke
maand — ook de eerste zichtbare maand, dus januari als het jaar daar
begint — een dikkere streep met de maandnaam; dagkolom gecentreerd.
Sorteren op **plaats**: één rij per plaats (Plaats | Heiligen |
Feestdatum). Klein icoon indien aanwezig. Feestdatum met haakjes voor
de oude burgerlijke datum indien die verschilt.

**Niet:** de vita in de rij; `selectie_toelichting`; GitHub-paden;
meerdere rijen voor dezelfde datum of plaats bij die sorteermodi;
interne tokens (`kandidaat-schrappen`) in de lezerstekst; kandidaten in
de tabel bij **Opgenomen**.
