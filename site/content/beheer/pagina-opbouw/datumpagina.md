---
title: "Datumpagina"
description: "Contract: één burgerlijke dag in één jaar"
git_date: 2026-08-30
---

**Contract, geen echte inhoud.** Voor wie: bezoeker. Canonieke URL:
`/datum/?datum=2026-07-01` (burgerlijk `jjjj-mm-dd`). Optioneel
`&stijl=juliaans`. Bron: handmatig
[`site/content/datum/_index.md`]({{% ref "/datum" %}}) + JS. Zonder
JavaScript: verwijzing naar het Synaxarion (vaste cyclus, geen jaartal).
De
[startpagina]({{% ref "/beheer/pagina-opbouw/startpagina" %}}) is het
heiligenoverzicht, niet de dagkaart. De datumpagina staat niet in de
hoofdnavigatie; u komt er via de jaarkalender of via een feestdatum.

Oude adressen `?jaar=` + `?dag=` blijven leesbaar en worden omgezet naar
`?datum=`. Een feestdag-link zonder jaar (`?dag=MM-DD`) betekent: dat
feest in het lopende burgerlijke jaar.

## Titelrij

**Wel:** weekdag, burgerlijke datum, jaar; «(vandaag)» als het vandaag
is (met popover en korte uitleg over oude/nieuwe kalender en verwijzing naar uitgebreide uitleg); pijlen naar vorige/volgende dag; toon van de week (Toon 1–8) met
korte uitleg in popover. De titelrij blijft zichtbaar tijdens scrollen
(onder de sitenavbar).

**Niet:** feestdatum in plaats van de burgerlijke datum; interne
offset-getallen; een tweede paginatitel onder de rij.

## Balk: vasten + Nieuw/Oud

**Wel:** **één** label voor die dag: een vastenregel (`vastenvrij`,
`vis`, `streng`, …) of het grijze **geen vasten** als er geen regel is.
Popover met korte uitleg en verwijzing naar uitgebreide uitleg. Bij een
periode: de naam van die periode tussen haakjes, als link. Knoppen
Nieuw / Oud; korte hulp bij Nieuw/Oud in popover.

**Niet:** twee vasten tegelijk (periode én wekelijks wo/vr); uitleg van
het hele typikon op deze pagina; Pascha meeschuiven met Oud.

## Dagtype

**Wel:** wat voor liturgische dag het is (week na Pinksteren, zondag
van het Triodion, of de naam van het feest). De feestdagnaam hier niet
nog eens herhalen als die al het dagtype *is*. Heeft het feest van de
dag een primair icoon (`rechten: ok`): dat icoon **naast** het dagtype
(onder het dagtype op smal scherm), als link naar de feestpagina. Extra
afbeeldingen van hetzelfde feest niet hier.

**Niet:** selectiestatus van heiligen; YAML-ids; een tweede samenvatting
van het feestverhaal; een icoonmuur; het icoon van een heilige van de
Lage Landen als held van de dag.

## Apostel en Evangelie

**Wel:** verwijzingen (boek en verzen) als links naar een
Bijbelvertaling; keuze van vertaling; of een korte zin als er geen
liturgie van dit type is. Bij tekst 'Apostel' en 'Evangelie' een
popover met korte uitleg en verwijzing naar gedetailleerdere uitleg
waar staat hoe de keuze tot stand is gekomen.

**Niet:** de volle Bijbeltekst op deze site; lokale parochiepolitiek
buiten de gekozen lezingenlijst.

## Heiligen van de Lage Landen

**Wel:** kop *Heilige van de dag* of *Heiligen van de dag* plus namen
(link naar de heiligenpagina), klein **primair** icoon als we er een
hebben. Extra iconen van dezelfde heilige niet in deze lijst. Zijn
er geen Lage-Landen-heiligen: géén kop, wél een korte zin met link
waarom de dag leeg kan zijn — zonder icoon bij die cataloguslink.

**Niet:** universeel menologion; parochiepatronen (nog geen onderdeel);
heiligen met `selectie: kandidaat-schrappen` (die staan alleen in het
overzicht); interne `selectie:`-waarden in de lijst; alle extra
reproducties naast de naam.
