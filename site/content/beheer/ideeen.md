---
title: "Ideeën"
description: "Toekomstige uitbreidingen; nog niet bouwen tot er een besluit is"
git_date: 2026-08-21
---

Eén verzamelplek voor ideeën en latere uitbreidingen. **Nog niet bouwen**
tot er een uitdrukkelijk besluit is. Geen YAML-velden of generatorwijziging
vanuit dit bestand alleen.

Dit is geen how-to en geen paginacontract. Contracten:
[Pagina-opbouw]({{% ref "/beheer/pagina-opbouw" %}}).

## Troparia en kondaken

Bij heiligen en feesten een hoofdstuk (of infobox-regel) met het
bijbehorende **troparion** en **kondakion**, met bron. Past bij zangers
en bij de rest van orthodox-ronl (zangstukken). Nog geen datamodel:
eerst één voorbeeldpagina uitschrijven (grootfeest of een kernheilige).

## Betekenis van feesten

Huidige feestpagina’s zijn kalenderfeit (wat/wanneer). Voor wie niet van
huis uit orthodox is, ontbreekt vaak: wat dit feest zegt over de weg naar
God.

Drie lagen, niet door elkaar:

1. **Gebeurtenis** — bestaande `verhaal` (kort, bron)
2. **Plaats in het jaar** — de kalender doet dit al
3. **Betekenis** — veld `betekenis` (1–3 alinea’s: geheim plus leiding
   van de Kerk; orthodox, weinig jargon; geen preek). Kerkvaders en
   dienstboek primair. Zelfde `bronlaag` als de rest van de pagina.

De twaalf grootfeesten, **Pascha**, Lazarus-zaterdag, de Grote
Week-dagen, de kernfeesten, de Triodion-zondagen (Zacheüs tot Maria
van Egypte, plus Schone Maandag), Thomas tot de Blinde,
Midden-Pinksterfeest, de concilie- en voorvaderzondagen en de
Allerzielen-zaterdagen hebben nu `betekenis`. Voorfeest, nafeest,
synaxis, weken, Boterweek en overige kalenderranden: nog niet.
Bronnen:
[`docs/onderzoek/feest-betekenis-bronnen.md`](https://github.com/orthodox-ronl/heiligen-lage-landen/blob/main/docs/onderzoek/feest-betekenis-bronnen.md).

## Parochiepatronen

Patroon van een kerk is nu geen toelatingsgrond (zie
[uitleg heiligen]({{% ref "/uitleg/heiligen" %}}) en de C-lijst in
[docs/inventaris.md](https://github.com/orthodox-ronl/heiligen-lage-landen/blob/main/docs/inventaris.md)).

Later denkbaar, **onderaan** de heiligen van een datum (na de
Lage-Landen-heiligen), duidelijk gemerkt, met link naar de parochiesite.
Pas als er een onderhouden lijst van parochiesites is. Geen vermenging
met `selectie: voldoet`.

**Volgende:** troparia/kondaken (eerst datamodel/voorbeeldpagina);
eventueel betekenis op kalenderranden alleen als dat geen duplicaat
van het hoofdfest wordt.
