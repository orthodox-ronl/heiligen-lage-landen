---
title: "Agenda"
description: "Contract: kalender op telefoon of computer"
git_date: 2026-09-02
---

**Contract, geen echte inhoud.** Voor wie: bezoeker. Canonieke URL:
`/agenda/`. Bron: handmatig [`site/content/agenda/_index.md`]({{% ref "/agenda" %}})
+ layout (stappen, voorbeeldweek, knoppen). Ingang: popover op de
titel van de [jaarkalender]({{% ref "/beheer/pagina-opbouw/jaarkalender" %}});
niet in de hoofdnavigatie.

## Titel

**Wel:** **Agenda** als info-term, zonder kop in de popover: korte
samenvatting (kalender in de agenda-app; kiezen, abonneren of
downloaden), afgesloten met
([meer uitleg]({{% ref "/uitleg/agenda" %}})).

**Niet:** een kop in de popover die de paginatitel herhaalt.

## Inleiding

**Wel:** één of twee zinnen die op weg helpen (eerst abonneren of
downloaden, daarna nieuw of oud, daarna wat u wilt zien).

**Niet:** de stappen herhalen; kleur van agenda’s (dat staat één keer, bij
de knoppen, alleen bij abonneren); een lijst van alle ruwe
`.ics`-bestanden; beheer-generate-uitleg.

## Stap 1: abonneren of downloaden

**Wel:** abonneren als default (blijft bijgewerkt); downloaden als
momentopname. Deze keuze staat eerst, omdat bij downloaden alle
detailvinkjes mogen (bestand wordt in de browser gemaakt als er geen
vaste feed is). Geen zin onder de kop: compacte popover op de
staptitel, afgesloten met
([meer uitleg]({{% ref "/uitleg/agenda" %}})). Popover op de chiptekst:
abonneren (beperkte mixen, blijft bijgewerkt); downloaden (alle mixen,
tot en met 31 december van huidig jaar + 5).

**Niet:** technische webcal-details vóór de keuze; uitlegzinnen in het
doosje.

## Stap 2: Nieuw of oud

**Wel:** Nieuw of Oud. Compacte popover op de staptitel, met
([meer uitleg]({{% ref "/uitleg/nieuw-oud" %}})). Geen framing alsof de
keuze de stand van de parochie moet volgen.

**Niet:** Pascha laten meeschuiven; «kies de stand van uw parochie».

## Stap 3: wat

**Wel:** heiligen, feesten, vasten, vastenvrij (één of meer), met nested
vinkjes: opgenomen (default aan), nader onderzoek en kandidaat (default
uit); feestgroepen grote / overige / voorfeest/nafeest/synaxis (één
vinkje; default aan; teruggave bij omlijsting); vasten
woensdag/vrijdag (één vinkje), periodes, feestdagen met vasten (default
aan). Kandidaat niet op jaarkalender of datumpagina. Bij **abonneren**
zijn voorfeest/nafeest/synaxis en woensdag/vrijdag wél aanklikbaar
(weglaten mag); andere splitsingen onder Feesten of Vasten mét andere
hoofdssoorten zijn grijs. Popover op de chiptekst (geen kop;
`(meer uitleg)` naar heiligen, feesten of vasten). Compacte popover op
de staptitel naar
([meer uitleg]({{% ref "/uitleg/agenda" %}})). Direct onder deze stap
de voorbeeldweken. Terug naar abonneren met een ongeldige mix zet de
vinkjes terug op de standaard.

**Niet:** universeel menologion als optie; losse vinkjes voor voorfeest,
nafeest, synaxis, woensdag en vrijdag; uitlegzinnen in het doosje.

## Voorbeeldweek

**Wel:** twee blokken, op brede schermen naast elkaar als beide zichtbaar
zijn. Eerst **deze week** (ISO-maandag tot zondag).
Daarna, als de keuze daar aanleiding toe geeft, een tweede week
(`Zo ziet de week van … eruit`) later in het jaar, waarin heilige, feest,
vastenperiode of vastenvrij zichtbaar is al naar gelang de vinkjes.
Titel = app-titel; vastenlabel alleen als aangevinkt én er die dag een
regel is.

**Niet:** website-links in de voorbeeldtitel; een tweede, afwijkende
titellogica; de tweede week tonen als die niet rijker is dan deze week;
twee kolommen op een smal scherm.

## Actie en how-to per app

**Wel:** knop die meeverandert; stappen voor Google, Apple, Outlook,
Android. **Eén keer**, vlak boven de knoppen: één set vinkjes = één
agenda-link = één kleur; een tweede agenda vraagt andere vinkjes en
opnieuw kopiëren. Het ICS-venster is huidig jaar −2 … +5 (niet de
vijfjaren-tabel op een feestdagpagina).

**Niet:** interne feed-bestandsnamen als primaire UI (die horen op de
technische bijlage).
