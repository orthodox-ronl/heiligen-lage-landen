---
title: "Heilige of feest toevoegen of wijzigen"
description: "YAML onder data/, namen in het entry-bestand; nooit de gegenereerde markdown"
weight: 20
git_date: 2026-08-31
---

Heiligen en feesten bestaan als **bron** in YAML. De pagina’s die u op de
site ziet, zijn een afdruk. Wijzig de YAML; laat `site/content/heiligen/`
en `site/content/feesten/` met rust.

Datamodel: [docs/datamodel.md](https://github.com/orthodox-ronl/heiligen-lage-landen/blob/main/docs/datamodel.md).
Schema’s (velden + auteursrichtlijnen):
[schemas/README.md](https://github.com/orthodox-ronl/heiligen-lage-landen/blob/main/schemas/README.md).
Schema entry: `schemas/entry.schema.json`. Publiceren:
[site bouwen]({{% ref "/beheer/how-to-publiceren" %}}).

## Nieuw id

1. Kies een id: alleen `a-z`, `0-9`, `_` en `-`, beginnend met een letter
   of cijfer. Voorbeeld: `willibrord`, `ontslapen-moeder-gods`.
2. Dat id is de **bestandsnaam** zonder `.yaml` en blijft stabiel. Wijzig
   later liever de getoonde naam dan het id.
3. Zet `namen.primair` (en optioneel `alternatief`) in hetzelfde YAML-bestand.
   Zie [namen wijzigen]({{% ref "/beheer/how-to-namen" %}}).

## Bestand

- Heilige: `data/heiligen/<id>.yaml` met `soort: heilige`
- Feest: `data/feesten/<id>.yaml` met `soort: feest`

Minimaal: `id`, `soort`, `datum`, `namen.primair`. Voor een verhaal,
samenvatting (feest/vasten), `betekenis` (feest) of
`betekenis_lage_landen` is minstens één **referentie**
verplicht, met een locator: `url`, of `isbn`, of `locator`.

### Vaste dag

```yaml
id: willibrord
soort: heilige
bronlaag: encyclopedie   # nagekeken: zie onder
cyclus: jaar
lage_landen: true
datum:
  waarde: "11-07"
  stijl: gregoriaans     # documentatie van de invoer; default gregoriaans
```

`stijl` schakelt de site niet tussen Nieuw en Oud. Zie
[Feestdatum (technisch)]({{% ref "/uitleg/feestdatum-technisch" %}}).

Meerdere gedenkdagen: `datum.waarde` is de **sterfdag** (canoniek).
Andere dagen alleen in `datum.extra` als ze in de Orthodoxe Kerk bekend
zijn. Zie het [contract Heilige]({{% ref "/beheer/pagina-opbouw/heilige" %}}).

```yaml
datum:
  waarde: "04-24"
  extra:
    - waarde: "12-23"
      toelichting: gedachtenis op de Orthodoxe kalender
```

Plaatsen: ids uit `data/plaatsen.yaml`, geen vrije plaatsnamen.

```yaml
locaties:
  - utrecht
  - echternach
rustplaats:
  plaats: echternach
  toelichting: "Abdij van Echternach"
```

Zet bij voorkeur **concrete plaatsen**. Een **streek**-id (`frisia`,
`vlaanderen`) alleen als aanvulling, of als er geen betere plek bekend is.
De weergavenaam van een streek is herkenbaar Nederlands (`Friesland`);
historische vormen (`Frisia`) staan in `alternatief` en blijven zoekbaar.

`rustplaats` is alleen waar het lichaam traditioneel rust. Geen relieken.

### Paascyclus

```yaml
cyclus: paascyclus
datum:
  paascyclus:
    anker: pascha
    offset_dagen: 0      # 0 = Pascha; negatief = dagen vóór
```

Periodes (vasten of een week) gebruiken `van_offset_dagen` /
`tot_offset_dagen`, of hybride `van_offset_dagen` plus `datum.tot` (MM-DD),
zoals het Apostelvasten.

Voorfeest, nafeest en synaxis rond de twaalf zijn gewone feest-YAML
(één dag of `van`/`tot`).

### Weekdag t.o.v. een feestdatum

Zondagen vóór/ná Kerst (en ná Theofanie) hebben geen vaste MM-DD:

```yaml
cyclus: jaar
datum:
  stijl: juliaans
  weekdag_relatief:
    anker: "12-25"
    weekdag: 7           # ISO: 1=ma … 7=zo
    welke: 1             # 1 = dichtstbijzijnde, 2 = de volgende
    richting: voor       # of: na
```

Strikt vóór/ná het anker: als 25 december zondag is, is «zondag vóór»
18 december. Zie `docs/datamodel.md`. Zaterdag/zondag rond
Kruisverheffing en Theofanie, en zaterdag vóór Kerst, gebruiken dezelfde
`weekdag_relatief`-vorm, maar alleen in de lezingenlijst — geen
feest-YAML. De zondag ná 10 oktober (Vaderen van het Zevende Concilie)
is wél een feest-entry, net als de zondagen rond Kerst. Zie
[lezingen wijzigen]({{% ref "/beheer/how-to-lezingen" %}}).

## Namen

```yaml
namen:
  primair: Willibrord
  alternatief:
  - Willibrordus
```

`primair` is verplicht in het entry-bestand. Zoekaliassen en andere
spellingen horen onder `alternatief`. Zie
[namen wijzigen]({{% ref "/beheer/how-to-namen" %}}).

## Vasten op een feest

Optioneel:

```yaml
vastenniveau: vis        # streng | wijn_olie | vis | lichter | vrij
observances: [feest, vasten]
```

`vastenniveau` op een feest **versoepelt** in een periode, of legt vasten
op buiten een periode als `observances` vasten bevat (Kruisverheffing,
Onthoofding). De mengregel zelf wijzigt u niet hier. Zie
[vastenregels]({{% ref "/beheer/how-to-vasten" %}}).

## Referenties

Bij het lezen van een bron: checklist
[Bron beoordelen]({{% ref "/beheer/how-to-bron-beoordelen" %}})
(aliassen, plaatsen, `inhoud`, icoon).

```yaml
referenties:
  - bron_id: oca-calendar
    url: "https://www.oca.org/saints/lives"
    geraadpleegd: "2026-08-16"
    inhoud: "Korte vita en feestdag in de OCA-kalender."
  - label: "Handboek X"
    isbn: "978-…"
    pagina: "120–124"
    geraadpleegd: "2026-08-16"
    inhoud: "Hoofdstuk over de missie in Frisia."
```

`bron_id` wijst naar `data/bronnen/bronnen.yaml`. De locator hoort **ook**
op de referentie in de entry, niet alleen in de catalogus. Sectiekop op de
pagina: **Verder lezen en kijken**.

## Heiligen: selectie, betekenis, bronlaag

Criteria in gewone taal: [Heiligen van de Lage Landen]({{% ref "/uitleg/heiligen" %}}).
Velden: [technisch]({{% ref "/uitleg/heiligen-technisch" %}}) en
[docs/datamodel.md](https://github.com/orthodox-ronl/heiligen-lage-landen/blob/main/docs/datamodel.md).

Pagina-opbouw (na de infobox): zie het
[contract Heilige]({{% ref "/beheer/pagina-opbouw/heilige" %}})
(en [Feest]({{% ref "/beheer/pagina-opbouw/feest" %}})).
Huidige generatorvolgorde bij heiligen: feestdag-link → **Betekenis voor
de Lage Landen** (`betekenis_lage_landen`) → verhaal →
verder lezen → **Over de bronnen** → (alleen bij nader/kandidaat) uitklap
**Plaats in deze kalender**. Bij feesten: feestdag (of de vijfjaren-tabel
komende jaren) →
samenvatting → verhaal → **Betekenis** (`betekenis`, alleen als het veld
er is) → verder lezen → **Over de bronnen**.

```yaml
betekenis_lage_landen: |
  Wat deze heilige voor het christendom of de Orthodoxie
  in de Lage Landen betekende.
selectie: voldoet          # of nader-onderzoek | kandidaat-schrappen
selectie_toelichting: "…"  # beheer; bij nader/kandidaat ook fallback publiek
selectie_toelichting_publiek: "…"  # optioneel; lezersversie
```

- Ontbreekt `selectie`: behandel als `nader-onderzoek`. Zet het veld als u
  een heilige toetst. `kandidaat-schrappen` verwijdert niets; die heiligen
  staan in het overzicht als **kandidaat**, niet op de datumpagina of in
  ICS/agenda.
- Bij `nader-onderzoek` / `kandidaat-schrappen` verschijnt onderaan een
  uitklap (`<details>`) **Plaats in deze kalender**: korte status, waarom,
  link naar de uitleg-criteria. Bij `voldoet`: niets. Tekst:
  `selectie_toelichting_publiek`, anders `selectie_toelichting`.
- Extra top-level YAML-velden mogen (notities/experimenten); ze komen niet
  op de site tot generate/UI ze kent. Zie
  [schemas/README.md](https://github.com/orthodox-ronl/heiligen-lage-landen/blob/main/schemas/README.md).
- Beslissingslog: [docs/inventaris.md](https://github.com/orthodox-ronl/heiligen-lage-landen/blob/main/docs/inventaris.md)
  (geen vaste aantallen). Live overzicht:
  [Selectie heiligen]({{% ref "/beheer/selectie" %}}).
- `betekenis_lage_landen` is een **apart** stuk, niet hetzelfde als
  `verhaal`. Op heiligenpagina’s staat geen `samenvatting`.

`bronlaag: encyclopedie` — tekst volgt Wikipedia/heiligen.net; zelfde
pagina-opbouw als nagekeken.
`bronlaag: nagekeken` bij een **heilige** alleen als:

1. `betekenis_lage_landen` niet leeg is, en
2. minstens één referentie niet Wikipedia of heiligen.net is
   (die twee mogen aanvullen; OrthodoxWiki telt wél).

Feesten: `nagekeken` blijft nagekeken tekst met traceerbare bronnen.

`validate.py` weigert een heilige die `nagekeken` is zonder die lat.

## Feesten: betekenis

Optioneel veld `betekenis` (1–3 alinea’s): het geheim van het feest
(weg naar God) plus wat de Kerk die dag vraagt. Niet het verhaal
(gebeurtenis) en niet de feestdatum. Geen tweede vastentabel
(`vastenniveau` in de infobox). Weinig jargon; geen preek. Zelfde
bronlaag als de rest van de pagina. Kop op de pagina: **Betekenis**,
ná het verhaal.

Schrijf vanuit ontvangen **kerkvaders** en het **dienstboek**. Hopko
(*The Orthodox Faith*) is brug. Johannes van Shanghai of Sophrony
alleen als zij dezelfde vader naspreken — niet als enige bron, en niet
om hun band met de Lage Landen in deze tekst te noemen. Locators en
volgorde: [bronnennota](https://github.com/orthodox-ronl/heiligen-lage-landen/blob/main/docs/onderzoek/feest-betekenis-bronnen.md).

Voorbeeld: Theofanie. Grootfeesten, Pascha, Heilige Week-dagen, de
kernfeesten, de Triodion-zondagen, Thomas tot de Blinde,
Midden-Pinksterfeest, concilie- en voorvaderzondagen en Allerzielen
in de bronnennota hebben het veld.
Voorfeest, nafeest, synaxis, weken en Boterweek niet. Contract:
[Feest]({{% ref "/beheer/pagina-opbouw/feest" %}}).

```yaml
betekenis: |
  Geheim van het feest, daarna de leiding van de Kerk (1–3 alinea’s).
goedkeuring:
  - naam: "A. N."
    organisatie: "parochie X"
    datum: "2026-08-21"
    opmerking: "Kort voorbehoud of bevestiging."
```

`goedkeuring` is optioneel. Leeg of weggelaten: de kop **Betekenis**
zegt in een popover dat de tekst is ontleend aan de
«Orthodoxe geloof»-bron (anders de andere referenties) en dat we nog
toets zoeken. Zet iemand pas in dit veld na een expliciete toets van
díe betekenistekst. Niet hetzelfde als `bronlaag: nagekeken`.

## Icoon

Bestand onder `site/static/` (doorgaans `site/static/iconen/<id>.jpg`).
Alleen tonen als `rechten: ok`, met `bron` en `licentie`. Geen URL als
afbeeldingsbron: een plaatje op een andere site mag u niet zomaar in de
browser laden (auteursrecht, kapotte links, hotlink-blokkades).

### Script

Vanuit de repo-root (`.\scripts` op PATH):

```cmd
icoon heiligen-lage-landen-muuricoon-hemelum.png
```

U hoeft het id niet te kennen: naam, alias of (deel van) de bestandsnaam
is genoeg. Voorbeeld: `heiligen lage landen` vindt
`zondag-heiligen-lage-landen` (Zondag van de heiligen van de Lage Landen).
Eén treffer: het script vraagt **Klopt dit? (J/n)**. Meerdere treffers:
een genummerde lijst. Geen treffer of verkeerde keuze: opnieuw typen tot
het lukt. Leeg, `stop` of `q` breekt af.

Het script controleert **eerst** of het bronplaatje bestaat. Ontbreekt
het pad, dan stopt het meteen (geen licentievraag). Een `.yaml` is geen
plaatje: extra icoon hoort **niet** in een tweede feestbestand.

**Niet:** `data/feesten/zondag-heiligen-lage-landen-hemelum.yaml`.
**Wel:** zelfde entry `data/feesten/zondag-heiligen-lage-landen.yaml`,
veld `iconen:`, bestand `site/static/iconen/zondag-heiligen-lage-landen-hemelum.jpg`
(naast het bestaande `zondag-heiligen-lage-landen.jpg`). Zelfde patroon
als Odulphus (`odulphus.yaml` + `iconen/odulphus-hemelum.jpg`).

Plaatsnamen zoals `hemelum`, `groningen`, `zwolle`, `leeuwarden` in de
bestandsnaam of als antwoord zijn plaats-ids: het plaatje stamt uit die
(Russisch-)orthodoxe parochie of dat klooster, met toestemming. Kies bij
licentie **Toestemming van parochie of klooster**; het script vult `plaats`,
`soort: foto`, `bron` en `licentie` in en laat u die bevestigen.

`--niet-interactief` eist unieke naam of `--id`, en bij toestemming `--plaats`.

**Commons-checklist**

1. Zoek op [Wikimedia Commons](https://commons.wikimedia.org/) (naam +
   heilige / icon).
2. Open de **File:**-pagina; lees licentie en attribuutvereisten.
3. Toegestaan voor ons: publiek domein, CC0, of CC-BY / CC-BY-SA met
   naamsvermelding in `bron` / `licentie`.
4. Download het bestand; bewaar onder `site/static/iconen/<id>.…`.
5. Zet in YAML `rechten: ok` en verwijs naar de File-pagina als `bron`.

```yaml
icoon:
  bestand: iconen/willibrord.jpg
  rechten: ok
  licentie: "Publiek domein"
  bron: "Wikimedia Commons — File:Willibrord (Paris, BN Lat. 10510).jpg"
```

**Meerdere plaatjes** (eigen foto naast een bestaande reproductie):
overschrijf het oude bestand niet. Nieuwe naam
`iconen/<id>-<korte-id>.jpg`. YAML-veld `iconen` in plaats van `icoon`,
met precies één `primair: true`. `soort: foto` of `reproductie`.
Optioneel `plaats` (id uit `plaatsen.yaml`) en `toelichting`. Eigen
foto’s: toestemming van parochie/klooster (en zo nodig de iconograaf);
zet dat in `bron` / `licentie`.

```yaml
iconen:
  - bestand: iconen/odulphus-hemelum.jpg
    primair: true
    soort: foto
    plaats: hemelum
    rechten: ok
    licentie: "Toestemming van het klooster"
    bron: "Russisch Orthodox klooster van de H. Nicolaas te Hemelum"
    toelichting: "Icoon in het klooster te Hemelum."
  - bestand: iconen/odulphus.jpg
    soort: reproductie
    rechten: ok
    licentie: "Publiek domein"
    bron: "Wikimedia Commons — File:Odulphus.jpg"
```

Ontbreekt een legaal bestand: laat `icoon` / `iconen` weg. Dat geldt ook
voor obscure lokale heiligen zonder duidelijk PD/CC-portret (geen
verkeerde persoon, geen hedendaags synaxarion-CDN). «Icoon in parochie»
hoort niet in `titels`. Bron beoordelen (stap beeldmateriaal):
[Bron beoordelen]({{% ref "/beheer/how-to-bron-beoordelen" %}}).

**Feesten — prioriteit (selectiever dan heiligen)**

| Prioriteit | Wat | Icoon? |
| --- | --- | --- |
| Hoog | Grootfeesten en kernfeesten met vaste iconografie (Pascha, Kerst, Theofanie, Transfiguratie, …) | Eigen traditioneel feesticoon (PD/CC) |
| Midden | Themamatige zondagen (Orthodoxie, Palmzondag, …) | Alleen als er een duidelijk thema-icoon is |
| Laag | Voorfeest / nafeest / teruggave | Liever **zelfde bestand** als het hoofdfest, of weglaten |
| Laagste | Weken, vastenperiodes, abstracte periodes (boterweek, vastenvrije week, …) | Meestal **weglaten** (geen portret) |

Gedeeld bestand (zoals bij Monulphus/Gondulphus):

```yaml
# data/feesten/voorfeest-kerst.yaml
icoon:
  bestand: iconen/kerst.jpg   # zelfde als kerst
  rechten: ok
  licentie: "Publiek domein"
  bron: "Wikimedia Commons — File:Russian nativity icon.jpg"
```

## Dubbele ids samenvoegen

Eén persoon = één bestand. Houd het canonieke id (bestandsnaam). Zet oude
ids in `id_aliassen` en de oude namen onder `namen.alternatief`:

```yaml
id: lebuinus
id_aliassen:
  - lubuinus
```

`id_aliassen` mag het eigen id niet herhalen en geen id dat nog als
apart YAML-bestand bestaat. Verwijder het oude bestand in dezelfde
wijziging. `generate.py` zet oude ids om in Hugo-aliases en schrijft
`betekenis_lage_landen` onder **Betekenis voor de Lage Landen**. Selectie
staat op [Selectie heiligen]({{% ref "/beheer/selectie" %}}); bij
`nader-onderzoek` / `kandidaat-schrappen` een uitklap onderaan de
publieke pagina, niet bij `voldoet`.

## Controleren

```text
check
```

Of stapsgewijs: `validate`, daarna generate via `serve` / `build`, of `test`.

Daarna de entry op de site: overzicht (groep), Synaxarion en datumpagina
(alleen als `selectie` niet `kandidaat-schrappen` is), eventueel ICS.
