---
title: "Voor beheerders"
description: "Wat staat waar, wat u mag wijzigen, en waar generate.py overheen schrijft"
git_date: 2026-08-21
---

Deze pagina is voor wie de kalender **in de git-repo bijhoudt**: YAML
aanpassen, een heilige toevoegen, een vastenregel of een lezing corrigeren.
Zij is geen uitleg voor wie de site alleen gebruikt. Die uitleg staat onder
[Uitleg]({{% ref "/uitleg" %}}).

Elk onderwerp op Uitleg heeft een **gebruikerspagina** (gewone taal, voor
parochianen en clerus) en een **technische bijlage** (bestanden en code).
De bijlagen staan niet in het uitleg-overzicht. How-to’s voor wijzigingen
staan hieronder.

## Wat waar staat

| Map of bestand | Wat het is |
| --- | --- |
| `data/heiligen/` | Eén YAML-bestand per heilige (bron; incl. `namen:`) |
| `data/feesten/` | Eén YAML-bestand per feest, ook paascyclus (incl. `namen:`) |
| `data/vasten/` | Vastenperiodes en wekelijks wo/vr-vasten (bron; incl. `namen:`) |
| `data/plaatsen.yaml` | Plaatsen voor kaart en zoeken (`locaties:` op een heilige zijn ids hieruit) |
| `data/bronnen/bronnen.yaml` | Catalogus van bronnen (`bron_id`) |
| `data/regels/vasten.yaml` | Normatieve vastenregels + voorbeelden + clerustekst |
| `data/lezingen/` | Lezingenrooster (gedeelde lijst, weekreeks, parochie) |
| `docs/datamodel.md` | Datamodel (velden, cycli, referenties) |
| `docs/inventaris.md` | Beslissingslog (criteria, post-schisma); live telling in `/beheer/selectie/` |
| `site/content/beheer/pagina-opbouw/` | Contracten: wat er op elke paginasoort wel en niet hoort |
| `site/content/beheer/ideeen.md` | Ideeën en latere uitbreidingen; nog niet bouwen |
| `docs/onderzoek/` | Onderzoeksnotities (o.a. post-schisma-heiligen) |
| `docs/specs/lezingen.md` | Normatieve lezingenspec (als die feature er is) |
| `schemas/entry.schema.json` | Schema voor heilige/feest/vasten-YAML |
| `scripts/` | Validatie, generatie, vastenmenging, lezingen |
| `site/content/uitleg/` | Uitlegpagina’s (handmatig, behalve vasten*) |
| `site/layouts/` en `site/assets/` | Vormgeving en kalender-JavaScript |
| `tests/` | pytest |

\* `site/content/uitleg/vasten.md` en `vasten-technisch.md` komen uit
`data/regels/vasten.yaml` via `scripts/generate.py`.

## Wat u wél mag veranderen

Wijzigingen hier blijven staan. Na afloop: valideren, genereren, tests,
committen. Zie [site bouwen en publiceren]({{% ref "/beheer/how-to-publiceren" %}}).

<table class="beheer-tabel beheer-tabel-aanraken">
<thead><tr><th>U wijzigt</th><th>Effect op de site</th></tr></thead>
<tbody>
<tr><td><code>data/heiligen/*.yaml</code>, <code>data/feesten/*.yaml</code></td><td>Naam (<code>namen.primair</code> / <code>alternatief</code>), datum, verhaal, <code>betekenis_lage_landen</code>, referenties, <code>selectie</code>, <code>locaties</code> (plaats-ids), <code>rustplaats</code>, vastenniveau van die entry. Entry-pagina, Synaxarion, jaarkalender, datumpagina, kaart en ICS volgen na <code>generate.py</code>.</td></tr>
<tr><td><code>data/vasten/*.yaml</code></td><td>Wanneer een periode loopt, of wo/vr wekelijks is, welk seizoensniveau de periode heeft. De <em>mengregel</em> (wat er op een dag getoond wordt) zit niet hier, maar in <code>data/regels/vasten.yaml</code> plus code.</td></tr>
<tr><td><code>data/plaatsen.yaml</code></td><td>Plaatsnamen, coördinaten, streek. Kaart en zoeken op het heiligenoverzicht.</td></tr>
<tr><td><code>data/bronnen/bronnen.yaml</code></td><td>Metadata bij <code>bron_id</code>. De locator (<code>url</code> / ISBN / …) hoort óók op de referentie in de entry.</td></tr>
<tr><td><code>data/regels/vasten.yaml</code></td><td>Cleruspagina, technische vastenpagina, en de voorbeelden die pytest toetst. Wijzigt u een verwacht niveau, dan moeten <code>scripts/vasten.py</code> en <code>calendar.js</code> mee — anders falen de tests.</td></tr>
<tr><td><code>data/lezingen/</code></td><td>Welke Apostel en welk Evangelie de site op een dag toont, inclusief parochie-afwijkingen. Zie de how-to lezingen.</td></tr>
<tr><td><code>site/content/uitleg/*.md</code> (niet vasten*)</td><td>Gebruikersuitleg. Technische bijlagen: bestanden <code>*-technisch.md</code>.</td></tr>
<tr><td><code>site/content/beheer/pagina-opbouw/</code></td><td>Paginacontracten. Generate.py schrijft hier niet overheen.</td></tr>
<tr><td><code>site/content/beheer/ideeen.md</code></td><td>Ideeënlijst; geen automatische bouw.</td></tr>
<tr><td><code>site/content/_index.md</code>, <code>kalender/</code>, <code>synaxarion/</code>, <code>datum/</code>, <code>agenda/</code>, <code>uitleg/_index.md</code></td><td>Handmatige sectiepagina’s: de <em>body</em> blijft bij genereren staan. Ontbrekende <code>layout</code> wordt wel gecorrigeerd.</td></tr>
<tr><td><code>site/static/iconen/</code></td><td>Afbeeldingen bij heiligen/feesten. Alleen met <code>icoon.rechten: ok</code> in YAML; geen hotlinks.</td></tr>
<tr><td><code>site/layouts/</code>, <code>site/assets/</code></td><td>Uiterlijk en gedrag in de browser. Vastenmenging in JS moet gelijk blijven aan <code>scripts/vasten.py</code>.</td></tr>
</tbody>
</table>

## Waar u vanaf moet blijven

Dit wordt bij `python scripts/generate.py` (en in CI met `--clean`)
**overschreven**. Redigeren heeft geen blijvend effect; de volgende build
gooit het weg.

<table class="beheer-tabel beheer-tabel-afblijven">
<thead><tr><th>Pad</th><th>Waarom niet aanraken</th></tr></thead>
<tbody>
<tr><td><code>site/content/heiligen/*.md</code></td><td>Gegenereerd uit <code>data/heiligen/</code>. Ook <code>_index.md</code> van deze map.</td></tr>
<tr><td><code>site/content/beheer/selectie.md</code></td><td>Gegenereerd uit <code>selectie</code> op heiligen-YAML.</td></tr>
<tr><td><code>site/content/feesten/*.md</code></td><td>Gegenereerd uit <code>data/feesten/</code>, inclusief <code>_index.md</code>.</td></tr>
<tr><td><code>site/content/vasten/*.md</code></td><td>Gegenereerd uit <code>data/vasten/</code>, inclusief <code>_index.md</code>. (De <em>bron</em> is YAML, niet deze markdown.)</td></tr>
<tr><td><code>site/content/uitleg/vasten.md</code></td><td>Komt uit <code>data/regels/vasten.yaml</code> (<code>render_vasten_clerus</code>).</td></tr>
<tr><td><code>site/content/uitleg/vasten-technisch.md</code></td><td>Zelfde YAML, technische weergave.</td></tr>
<tr><td><code>site/static/data/entries.json</code></td><td>Index voor de kalender in de browser.</td></tr>
<tr><td><code>site/static/data/plaatsen.json</code></td><td>Kaartgegevens; uit <code>data/plaatsen.yaml</code>.</td></tr>
<tr><td><code>site/static/ics/*.ics</code></td><td>Agenda-feeds; bij generate eerst gewist.</td></tr>
<tr><td>gegenereerde dagbestanden onder <code>site/content/datum/</code> (alles behalve <code>_index.md</code>)</td><td>Wordt bij <code>--clean</code> verwijderd.</td></tr>
</tbody>
</table>

`site/content/datum/_index.md` zelf is wél handmatig. Alleen extra bestanden
in die map verdwijnen bij `--clean`.

## Hoe een pagina eruit moet zien

Dit zijn **contracten**: per paginasoort wat er in elk blok wel en niet
hoort. Zij zeggen niet hoe u YAML of code wijzigt — daarvoor blijven de
how-to’s hieronder.

[Pagina-opbouw]({{% ref "/beheer/pagina-opbouw" %}})

Toekomstige uitbreidingen (één lijst, nog niet bouwen):
[Ideeën]({{% ref "/beheer/ideeen" %}}).

## How-to’s

- [Commando's]({{% ref "/beheer/scripts" %}}) — `test`, `validate`, `check`, `serve`, `build`
- [Site bouwen en publiceren]({{% ref "/beheer/how-to-publiceren" %}}) — valideren, genereren, tests, wat CI doet
- [Heilige of feest toevoegen of wijzigen]({{% ref "/beheer/how-to-heiligen-feesten" %}})
- [Bron beoordelen]({{% ref "/beheer/how-to-bron-beoordelen" %}}) — checklist aliassen, plaatsen, `inhoud`, iconen
- [Weergavenamen wijzigen]({{% ref "/beheer/how-to-namen" %}})
- [Vastenregels wijzigen]({{% ref "/beheer/how-to-vasten" %}})
- [Lezingenrooster wijzigen]({{% ref "/beheer/how-to-lezingen" %}})
- [Selectie heiligen]({{% ref "/beheer/selectie" %}}) — gegenereerd overzicht
  (`voldoet` / nader onderzoek / kandidaat); niet voor bezoekers

## Uitleg: twee lagen

| Laag | Voor wie | Waar |
| --- | --- | --- |
| Gebruikers / clerus | Wie de kalender leest of toetst wat we volgen | [Uitleg]({{% ref "/uitleg" %}}) |
| Technisch | Wie YAML of code aanpast | `…-technisch` bij elk onderwerp; niet in het overzicht |
| How-to | Wie een concrete wijziging moet doorvoeren | deze sectie |
