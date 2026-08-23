---
title: "Startpagina (heiligenoverzicht)"
description: "Contract: het overzicht van heiligen van de Lage Landen is de voordeur"
git_date: 2026-08-23
---

**Contract, geen echte inhoud.** Voor wie: bezoeker. Canonieke URL: `/`.
Bron: layout `index.html` toont dezelfde inhoud als
[Heiligenoverzicht]({{% ref "/beheer/pagina-opbouw/heiligenoverzicht" %}})
(`site.GetPage "/heiligen"` + partial `heiligen-overzicht.html`).
`site/content/_index.md` levert alleen de sitenaam in de kop; de
inleiding komt uit de gegenereerde heiligenindex.

De startpagina *is* het heiligenoverzicht (titel, aantal, criterium,
kaart, zoeken, tabel). De dagkaart van vandaag staat **niet** hier;
die hoort op [Datumpagina]({{% ref "/beheer/pagina-opbouw/datumpagina" %}})
(`/datum/`, nav **Vandaag**).

## Sitenaam (kop)

**Wel:** orthodox kruis (zelfde merkteken als de andere
orthodox-ronl-sites) links van de sitenaam. Sitenaam:
**Heiligen van de Lage Landen — orthodoxe kalender**, link naar `/`
(dit overzicht). Het kruis opent een popover: eerst het
heiligenoverzicht, dan dat de kalender daarbij hoort, en dat de site
nog jong is. Eerste bezoek aan `/`: de popover gaat vanzelf open.
In de popover: link naar het overzicht en naar Uitleg.

**Niet:** een tweede navigatie; interne padnamen; «ras-orthodoxen».

## Overzicht

Zelfde slots als [Heiligenoverzicht]({{% ref "/beheer/pagina-opbouw/heiligenoverzicht" %}}).
`/heiligen/` blijft dezelfde weergave (bestaande links).

**Niet:** de volledige dagkaart; YAML-paden; selectielijst.
