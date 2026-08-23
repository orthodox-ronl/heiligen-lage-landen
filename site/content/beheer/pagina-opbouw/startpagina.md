---
title: "Startpagina (Vandaag)"
description: "Contract: identiteit van de site plus de dagkaart van vandaag"
git_date: 2026-08-21
---

**Contract, geen echte inhoud.** Voor wie: bezoeker. Canonieke URL: `/`.
Bron: handmatig `site/content/_index.md` (URL `/`) plus dezelfde
JS-dagkaart als de datumpagina.

De startpagina *is* de datumpagina van de huidige burgerlijke dag. Alle
slots van [Datumpagina]({{% ref "/beheer/pagina-opbouw/datumpagina" %}})
gelden hier ook. Extra, alleen hier:

## Sitenaam (kop)

**Wel:** orthodox kruis (zelfde merkteken als de andere
orthodox-ronl-sites) links van de sitenaam. De sitenaam is een link
naar vandaag. Het kruis opent een popover: wat de site is, en dat ze
nog jong is (teksten nog niet nagekeken door mensen die van huis uit
orthodox zijn; die toets wordt gezocht). Eerste bezoek aan `/`: de
popover gaat vanzelf open en sluit na klik of enkele seconden; daarna
gedraagt het kruis zich als elke andere info-tip. Terugkerende
gebruikers: geen identiteitszin in de body.

**Niet:** een tweede navigatie; interne padnamen (`data/`, YAML);
«ras-orthodoxen» in de UI.

## Identiteitszin (body van `_index.md`)

**Gesloten.** De zin in HTML-commentaar blijft commentaar (niet
zichtbaar). Identiteit hoort bij de sitenaam-popover, niet in de body.

## Dagkaart

Zie [Datumpagina]({{% ref "/beheer/pagina-opbouw/datumpagina" %}})
(titelrij sticky onder de sitenavbar, vasten, Nieuw/Oud, dagtype,
lezingen, heiligen).
