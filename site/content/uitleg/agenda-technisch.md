---
title: Agenda (technisch)
description: ICS-feeds, bestandsnamen en wat generate.py overschrijft
uitleg_stijl: agenda-technisch
build:
  list: never
  render: always
git_date: 2026-09-02
---

Technische bijlage bij de [uitleg Agenda]({{% ref "/uitleg/agenda" %}}).

How-to: [site bouwen en publiceren]({{% ref "/beheer/how-to-publiceren" %}}).

## Feeds

`scripts/ics.py` (aanroep vanuit `scripts/generate.py`) schrijft:

- **Huidige feeds:** `site/static/ics/v2/<sleutel>-<stijl>.ics`
- **Oude paden** (`site/static/ics/<sleutel>-<stijl>.ics`, zonder `v2/`):
  **tombstone** — geen kalenderdagen meer, wel herinneringen naar `/agenda/`

Die bestanden worden bij elke generate **gewist en opnieuw gezet**.
Niet met de hand redigeren. Inhoud is **dag-centrisch** (één `VEVENT`
per burgerlijke dag), behalve tombstones (enkele herinneringsdagen).

### v2-sleutels

De vier hoofdssoorten blijven `heiligen` / `feesten` / `vasten` /
`vastenvrij` (combinaties met koppelteken; `alles` = alle vier).

Daarbinnen, defaults van de agendapagina:

- heiligen = alleen `selectie: voldoet` (Opgenomen)
- feesten = grote + overige + omlijsting (voorfeest, nafeest inclusief
  teruggave, synaxis)
- vasten = week (woensdag/vrijdag) + periodes + feestdagen met vasten
- vastenvrij = aan

Afwijkende subfilters krijgen eigen sleutels (`heiligen-nader`,
`feesten-grote`, `feesten-grote-overige`, `vasten-week`, …). Extra
heiligen-vinkjes bovenop een verder standaard mix, en het weglaten van
omlijsting of van woensdag/vrijdag, zitten in **hetzelfde** bestand
(niet een tweede feed naast `alles`).
`v2_relpaths` in `scripts/ics.py` is de norm; `icsFeedRelpaths` in
`calendar.js` is de spiegel. Elke keuze is **één** URL. Andere
kruiscombinaties van extra vinkjes onder Feesten of Vasten mét andere
hoofdssoorten worden niet als extra bestand gebouwd; de pagina maakt
die vinkjes bij abonneren grijs.

`stijl` is `nieuw` of `oud`. De agendapagina bouwt de knop uit de keuzes van de
bezoeker. Geen lijst van alle feeds op de pagina.
UI: `site/layouts/_default/agenda.html` en `calendar.js`.

Oude `oud-heiligen-nieuw`-feeds (v2 én paden zonder `v2/`) zijn tombstones
naar `/agenda/`.

Vasten in de feed zijn dagen met een vastenniveau anders dan `vrij`,
gefilterd op de aangevinkte vastensoorten. Vastenvrij is alleen
`niveau: vrij`. Een gewone dinsdag zonder vasten zit in geen van beide.

- **Abonneren:** de knop kopieert de HTTPS-URL. Apple: `webcal:` op
  dezelfde feed.
- **Downloaden:** dezelfde URL.

`X-WR-CALNAME` is kort, bijvoorbeeld `Orthodox · Lage Landen (nieuw)`.
`UID` van v2-feeds is `uuid5` van `v2:{sleutel}:{stijl}:{datum}`.

## Tombstones

Oude URL’s blijven bestaan zodat abonnementen een zichtbare melding
krijgen in plaats van stille, verouderde dagen. `X-WR-CALNAME`:
`Vervallen — nieuwe link op de site`. Enkele hele-dag-afspraken
(vandaag, +7, +30, volgende 1 september) met link naar `/agenda/`.
Die paden **niet** opnieuw vullen met echte kalenderdagen.

## Gedrag

Eén hele-dag-afspraak per burgerlijke dag die in de subset iets toont.
`SUMMARY` volgt `day_title` in `scripts/ics.py` (spiegel `icsDayTitle` in
`calendar.js`): grootfeest, anders heilige van de Lage Landen, anders
overig feest of `daglabel`. Op maandag (geen grootfeest) komt
`week_kop_label` vooraan. Vastenlabels komen uit `mix_vastenniveau` in
`scripts/vasten.py` en staan alleen in `SUMMARY`/`DESCRIPTION` als er
een regel is én de bijbehorende vasten-subfilter aan staat.
`URL` wijst naar de datumpagina.

`DESCRIPTION` volgt de datumpagina-box zonder website-links in de regels:
vastenregel, overige dagtype-feesten (`Ook:`), Apostel/Evangelie als
verwijzingstekst, heiligen (kandidaat met toevoeging `(kandidaat)`),
laatste regel `Meer:` naar de datumpagina.

Kandidaat-heiligen (`selectie: kandidaat-schrappen`) zitten niet op
jaarkalender, datumpagina of Synaxarion; in ICS alleen in feeds waar
die subfilter aan staat.

- **nieuw:** vaste feesten op de feestdatum (burgerlijk = dagnaam);
  paascyclus op de berekende Orthodoxe datum.
- **oud:** vaste feesten op Juliaanse feestdatum → burgerlijke vierdatum;
  paascyclus ongewijzigd; Juliaanse dagnaam in de `DESCRIPTION`, niet in
  de titel.
- Wekelijks vasten: burgerlijke weekdag, in beide stijlen. In een
  vastenperiode wint de periode in `mix_vastenniveau`; staat **periodes**
  uit en **woensdag en vrijdag** aan, dan telt weer het wekelijkse vasten.

`X-PUBLISHED-TTL:P1D`. `TRANSP:TRANSPARENT`. Geen `VALARM`.

Bereik: huidig jaar −2 … +5 (`ICS_YEAR_BACK` / `ICS_YEAR_FORWARD`).
De vijfjaren-tabel op een feestdagpagina is een ander venster (lopend
jaar … +4).

`site/content/agenda/_index.md` is handmatig (body blijft staan).
