---
title: "Pagina-opbouw"
description: "Contracten: wat er op elke paginasoort wel en niet hoort"
git_date: 2026-08-21
---

Dit zijn **contracten**, geen how-to’s. Een contract zegt wat er op een
paginasoort in elk blok wel en niet hoort. Hoe u YAML of code wijzigt,
staat onder [Voor beheerders]({{% ref "/beheer" %}}) bij de how-to’s.

Kop, hoofdnavigatie en footer zijn sitebreed. De sitenavbar blijft op
**alle** pagina’s zichtbaar tijdens scrollen. Pagina-afhankelijke
headerregels (titel, filters, kolomkoppen) blijven eveneens sticky;
wat erin staat staat in het contract van die paginasoort. Keuzes en
selecties horen in die header; bij meer dan een paar opties komt er
een knop **Weergave** met uitklapformulier.

De contracten hieronder gaan over het middenstuk van elke soort. Deze
pagina’s staan **niet** in de hoofdnavigatie; de ingang is de footer →
Voor beheerders.

**Contract, geen echte inhoud** staat bovenaan elk skelet. Een open
keuze (als die er is) staat als **Open besluit**: tot die keuze geen
live wijziging vanwege dat slot.

| Soort | Voor wie | Canonieke URL | Bron |
| --- | --- | --- | --- |
| [Startpagina (heiligenoverzicht)]({{% ref "/beheer/pagina-opbouw/startpagina" %}}) | Bezoeker | `/` | Layout + heiligenindex |
| [Datumpagina]({{% ref "/beheer/pagina-opbouw/datumpagina" %}}) | Bezoeker | `/datum/?datum=jjjj-mm-dd` | Handmatig `_index.md` + JS |
| [Jaarkalender]({{% ref "/beheer/pagina-opbouw/jaarkalender" %}}) | Bezoeker | `/kalender/` | Handmatig + JS |
| [Lezingenrooster]({{% ref "/beheer/pagina-opbouw/lezingenrooster" %}}) | Bezoeker / clerus | `/lezingenrooster/` (nav: Overzichten) | Handmatig + JS |
| [Synaxarion]({{% ref "/beheer/pagina-opbouw/synaxarion" %}}) | Bezoeker | `/synaxarion/` (nav: Overzichten) | Handmatig + JS |
| [Heiligenoverzicht]({{% ref "/beheer/pagina-opbouw/heiligenoverzicht" %}}) | Bezoeker | `/` en `/heiligen/` | Gegenereerde index + layout |
| [Heilige (detail)]({{% ref "/beheer/pagina-opbouw/heilige" %}}) | Bezoeker | `/heiligen/<id>/` | Gegenereerd uit YAML |
| [Feest (detail)]({{% ref "/beheer/pagina-opbouw/feest" %}}) | Bezoeker | `/feesten/<id>/` | Gegenereerd uit YAML |
| [Vastenperiode (detail)]({{% ref "/beheer/pagina-opbouw/vastenperiode" %}}) | Bezoeker | `/vasten/<id>/` | Gegenereerd uit YAML |
| [Feesten- en vastenoverzicht]({{% ref "/beheer/pagina-opbouw/overzichten-feesten-vasten" %}}) | Bezoeker | `/feesten/`, `/vasten/` (nav: Overzichten) | Gegenereerde indexen |
| [Agenda]({{% ref "/beheer/pagina-opbouw/agenda" %}}) | Bezoeker | `/agenda/` (via jaarkalender-titel) | Handmatig + layout |
| [Uitleg-overzicht]({{% ref "/beheer/pagina-opbouw/uitleg-overzicht" %}}) | Bezoeker | `/uitleg/` | Handmatig + layout |
| [Uitleg-onderwerp]({{% ref "/beheer/pagina-opbouw/uitleg-onderwerp" %}}) | Bezoeker / clerus | `/uitleg/<onderwerp>/` | Handmatig (`vasten.md` gegenereerd) |
| [Uitleg-technisch]({{% ref "/beheer/pagina-opbouw/uitleg-technisch" %}}) | Beheerder | `/uitleg/<onderwerp>-technisch/` | Handmatig; niet in het overzicht |
| [Beheer]({{% ref "/beheer/pagina-opbouw/beheer" %}}) | Beheerder | `/beheer/`, how-to’s, `/beheer/selectie/` | Handmatig; selectie gegenereerd |
