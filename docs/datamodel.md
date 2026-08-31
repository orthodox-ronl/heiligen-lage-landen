# Datamodel

Beheerders: wat u mag wijzigen, wat generate.py overschrijft, en how-to’s
staan op de site onder **Voor beheerders** (`site/content/beheer/`). Dit
bestand blijft de veldsemantiek van entries.

Elke entry is één YAML-bestand in `data/feesten/`, `data/heiligen/` of
`data/vasten/`.

## Datum en stijl (vaste jaarcyclus)

```yaml
datum:
  waarde: "08-15"          # MM-DD = feestdatum
  # stijl weglaten = gregoriaans (default) — alleen documentatie van de invoer
  stijl: juliaans          # of: gregoriaans
  # optioneel expliciet dubbel:
  # gregoriaans: "08-15"
  # juliaans: "08-15"
```

De **feestdatum** is de kalenderdag van het feest (bijv. Ontslapen = 15 augustus).
Die dagnaam is gelijk in de nieuwe (Gregoriaanse) en oude (Juliaanse) kalender.
`stijl` legt alleen vast hoe de beheerder de waarde bedoelde; er wordt géén
automatische +13 op de feestdatum zelf toegepast.

Bij een heilige met **meer gedenkdagen**: `datum.waarde` is canoniek de
**sterfdag** (of, bij twijfel, die dag). Andere dagen alleen in
`datum.extra` als ze **in de Orthodoxe Kerk bekend** zijn (niet een
louter katholieke of lokale datum). Generate zet ze op de pagina onder
**Andere gedenkdagen**; de infobox toont alleen de canonieke dag. Extra
dagen komen niet automatisch op jaarkalender of Synaxarion.

```yaml
datum:
  waarde: "04-24"            # sterfdag = canoniek
  extra:
    - waarde: "12-23"
      toelichting: gedachtenis op de Orthodoxe kalender
```

De offset Gregoriaans−Juliaans is **jaarafhankelijk** (13 tot 2099, 14 vanaf 2100:
`⌊Y/100⌋ − ⌊Y/400⌋ − 2`). Die offset zet vaste feesten op hun **wereldlijke
vierdatum** in de stand Oud (jaarkalender, home, datumpagina, ICS “oud”).
De paascyclus blijft in beide standen op de wereldlijke Orthodoxe Pascha-datum.

## Paascyclus

```yaml
cyclus: paascyclus
datum:
  stijl: gregoriaans       # default; berekende datums zijn wereldlijk
  paascyclus:
    anker: pascha
    offset_dagen: 0        # t.o.v. Orthodox Pascha (negatief = vóór)
```

Orthodox Pascha volgt de Alexandrijnse/Juliaanse computus (Meeus); alle Orthodoxe
kerken delen die datum. ICS en `entries.json` gebruiken **huidig jaar −2 … +5**.
De tabel «Komende jaren» op een feest- of vastenpagina is korter: het
lopende jaar en de vier daarop. Kolom **Datum** (of Van/Tot) is burgerlijk.
Haakjes bevatten alleen de burgerlijke vierdatum van oude-kalenderparochies,
als die verschilt (niet de Juliaanse dagnaam van dezelfde dag, en geen
bijschrift onder de tabel). Paascyclus zonder vast einde: geen haakjes.

## Namen

Canonieke weergavenamen staan **in het entry-YAML** als `namen.primair`
en optioneel `namen.alternatief`. Conventie:
`site/content/beheer/how-to-namen.md`.

Ids (bestandsnamen) blijven stabiel; wijzig de getoonde naam, niet het id.

Eén persoon is één bestand. Andere spellingen en historische namen horen
in `alternatief`. Na een merge van twee ids blijft het canonieke id de
bestandsnaam; de oude id(s) komen in `id_aliassen` (voor oude URL’s) én
als naam in `alternatief` (zoeken en index).

## Vasten

```yaml
soort: vasten
# Wekelijks (ISO-weekdag 1=ma … 7=zo):
cyclus: wekelijks
datum:
  weekdagen: [3]           # woensdag

# Vaste periode (MM-DD … MM-DD):
cyclus: jaar
datum:
  van: "08-01"
  tot: "08-14"

# Paascyclus-periode:
cyclus: paascyclus
datum:
  paascyclus:
    anker: pascha
    van_offset_dagen: -48
    tot_offset_dagen: -1
# of hybride: van_offset_dagen + datum.tot (MM-DD), bv. Apostelvasten
```

Pagina’s onder `/vasten/{id}/`; zichtbaar in synaxarion/agenda/kalender met
aan/uit-filters. ICS: `vasten-*.ics` en combinaties met heiligen/feesten.

Het **Synaxarion** (`/synaxarion/`, optioneel `?dag=MM-DD`) toont alleen de vaste
jaarcyclus. Een **datumpagina** (`/datum/?datum=2026-08-15`) toont wat er
op die dag in dat jaar valt, inclusief paascyclus en wekelijks vasten.

Optioneel op entries:

```yaml
vastenniveau: streng   # streng | wijn_olie | vis | lichter | vrij
onderdrukt_wekelijks_vasten: true   # wo/vr niet apart tonen (impliciet bij niveau: vrij)
```

**Voorrang (weergave, kalenderkleur, ICS):** wekelijks wo/vr-vasten is de
restcategorie. Het verdwijnt als die dag al in een **vastenperiode** valt
(Ontslapen, Geboorte, Apostolisch, Grote Vasten, Grote Week) of in een
vastenvrije periode (`vastenniveau: vrij`). Een named periode *is* het vasten
van die dag; vrijdagvasten niet nog eens apart. ICS zet dat als **één
dagregel** (titel met niveau), niet als losse woensdagvasten naast de periode.

Twee geneste periodes overlappen in de huidige data niet (Grote Vasten eindigt
vóór de Grote Week).

**Effectief niveau (home/datumpagina):** het getoonde niveau is één regel,
niet de som van overlappende vasten.

1. Basis = de dekkende periode. Zonder periode: wo/vr.
2. In een `streng`-periode (Grote Vasten, Ontslapen, Grote Week): weekdag
   `streng`; za/zo `wijn_olie`, **behalve** de Grote Week.
3. In Apostelen- en Geboortevasten (`lichter` als seizoen): ma/wo/vr `streng`,
   di/do `wijn_olie`, za/zo `vis`; 20–24 december geen vis.
4. Een feest met `vastenniveau` **versoepelt alleen**. In de Grote Week niet
   verder dan `wijn_olie`. Lazarus-zaterdag is kaviaar in het typikon; wij
   tonen `wijn_olie`.
5. Buiten een periode: een feest mét `observances: […, vasten]` **legt** het
   vasten op; anders versoepelt het alleen wo/vr of zet het uit (`vrij`).

Rang bij vergelijking: `streng` < `wijn_olie` ≈ `lichter` < `vis` < `vrij`.
**Normatief voor de dagregel:** `data/regels/vasten.yaml`. Cleruspagina:
`/uitleg/vasten/`; technische bijlage: `/uitleg/vasten-technisch/` (niet in het
uitleg-overzicht). How-to: `/beheer/how-to-vasten/`. Code: `scripts/vasten.py`
en `site/assets/js/calendar.js`.

## Lezingen (Apostel / Evangelie)

Normatieve regels: **`docs/specs/lezingen.md`** (traditie Moskou, ROCOR bij
twijfel). Clerus: `/uitleg/lezingen/`; technisch: `/uitleg/lezingen-technisch/`.

Data: `data/lezingen/` (`feest-overrides.yaml`, `weekreeks.yaml`, `rang.yaml`,
`config.yaml`, optioneel `parochies/<id>.yaml`, `meta.yaml`). Actieve
parochielijst in deze repo: `parochie: den-haag` (klooster Den Haag, niet
Groningen); niet stilzwijgend wijzigen. Engine:
`scripts/lezingen.py`. Machine-leesbare voorbeelden in de spec sturen pytest.
Build schrijft `site/static/data/lezingen-dagen.json` (per stijl/jaar/mmdd, met
`daglabel` / `modus` / `override_naam` / `override_laag` / optioneel `rijadovoe`);
UI op vandaag/`/datum/` en overzichtspagina `/lezingenrooster/`.

## Observances (kleuren)

```yaml
observances: [feest, vasten]   # optioneel; default volgt soort
```

Het jaarrooster ondersteunt gecombineerde kleuren (feest+vasten, heilige+vasten).

## Kalenderranden (voorfeest, nafeest, synaxis)

Rond de twaalf grote feesten staan gewone `soort: feest`-entries:

- **voorfeest** — één dag of `van`/`tot` (Kerst 20–24 dec., Theofanie 2–5 jan.)
- **nafeest** — periode tot en met de teruggave (apodosis)
- **synaxis** — dag na Kerst (Moeder Gods), na Theofanie (Johannes), na
  de Aankondiging (Gabriël)
- **Pokrov** (1 okt.) — groot Moeder-Godsfeest in de Moskou-traditie, niet
  één van de twaalf
- **teruggave** van Hemelvaart en Pinksteren (paascyclus); teruggave van
  Pascha bestond al

Palmzondag heeft geen nafeest (Grote Week). De Aankondiging heeft geen lang
nafeest, wel de synaxis van Gabriël. Het nafeest van de Ontmoeting toont de
volle jaarcyclus; in Boterweek of Grote Vasten bekort het typikon die periode.

## Weekdag t.o.v. een feestdatum

Geen derde cyclus (geen «kerstcyclus»). Wel dagen die aan een vaste
feestdatum hangen via de weekdag, met `cyclus: jaar`:

```yaml
datum:
  stijl: juliaans          # zelfde betekenis als bij Kerst: dagnaam
  weekdag_relatief:
    anker: "12-25"         # liturgische MM-DD
    weekdag: 7             # ISO: 1=ma … 7=zo
    welke: 1               # 1 = dichtstbijzijnde, 2 = de volgende
    richting: voor         # of: na
```

Strikt vóór/ná het anker: als 25 december zondag is, is «zondag vóór»
18 december, niet Kerst zelf. In de stand Oud is het anker de Juliaanse
feestdatum; de burgerlijke vierdatum schuift mee.

In deze kalender als **feest-entries** (jaarkalender, datumpagina, ICS;
niet in het Synaxarion):

- `zondag-voorvaderen` — 2e zondag vóór Kerst
- `zondag-vaderen-voor-kerst` — zondag direct vóór Kerst
- `zondag-na-kerst` — zondag ná Kerst
- `zondag-na-theofanie` — zondag ná Theofanie
- `zondag-vaderen-zevende-concilie` — zondag ná 10 oktober (Vaderen van Nicea II)

Zaterdag/zondag rond Kruisverheffing, Theofanie (vóór; zaterdag ná) en
zaterdag vóór Kerst zijn **alleen lezingendagen** (eigen Apostel/Evangelie,
geen eigen feestdienst): `weekdag_relatief` in
`data/lezingen/feest-overrides.yaml`, geen YAML onder `data/feesten/`.
Zie `docs/specs/lezingen.md`.

Functie: `weekday_relative_date` in `scripts/kalender.py`.

## Feesten: betekenis

Optioneel veld `betekenis` (1–3 alinea’s): het **geheim** van het feest
(wat het zegt over de weg naar God) plus kernachtig wat de Kerk die dag
**van de gelovige vraagt** (houding, wijding, waarom van het vasten).
Niet hetzelfde als `verhaal` (gebeurtenis) of de feestdatum (plaats in
het jaar). Geen tweede vastentabel: `vastenniveau` in de infobox is de
regel. Weinig jargon; geen preek. Zelfde bronlaag en
referentieverplichting als verhaal/samenvatting.

**Bronnen (schrijven en `referenties`):** eerst een ontvangen
kerkvader (of de vader in de dienst, zoals Chrysostomos’ paaspreek);
dan dienstboek, oecumenische canon, typikon voor de tafel. Hopko
(*The Orthodox Faith*) is brug, niet de last. Johannes van Shanghai en
Sophrony van Essex alleen als naspraak van die vaders — niet als
enige bron, en niet om hun band met de Lage Landen in `betekenis` uit
te spreken (dat is `betekenis_lage_landen` op hun heiligenpagina).
OrthodoxWiki is vingerwijzing. Zie
[`docs/onderzoek/feest-betekenis-bronnen.md`](onderzoek/feest-betekenis-bronnen.md).

Op de feestpagina als **Betekenis**, ná het verhaal. Nu: de twaalf
grootfeesten, Pascha, Lazarus-zaterdag en de Grote Week-dagen, de
genoemde kernfeesten, de Triodion-zondagen (Zacheüs tot Maria van
Egypte, plus Schone Maandag), Thomas tot de Blinde, en
Midden-Pinksterfeest, de concilie- en voorvaderzondagen, en de
Allerzielen-zaterdagen (vóór Vleesvaarwel en vóór Pinksteren). Geen
`betekenis` op voorfeest, nafeest, synaxis, weken of Boterweek.

Optioneel `goedkeuring`: lijst van personen of organisaties die de
**betekenistekst** hebben goedgekeurd. Ontbreekt of leeg: de kop
Betekenis opent een popover: ontleend aan de (voorkeur)
«Orthodoxe geloof»-referentie, plus dat we nog toets zoeken. Gevuld: de
popover noemt wie goedkeurde, met optionele organisatie, datum en opmerking.
Dit is niet hetzelfde als `bronlaag: nagekeken` (traceerbare bronnen).

```yaml
goedkeuring:
  - naam: "A. N."
    organisatie: "parochie X"   # optioneel
    datum: "2026-08-21"         # optioneel, YYYY-MM-DD
    opmerking: "…"              # optioneel, voor de lezer
```

## Heiligen: selectie en betekenis

Selectiecriteria (wie in de lijst hoort) staan op `/uitleg/heiligen/`;
veldsemantiek hier. How-to: `/beheer/how-to-heiligen-feesten/`.

```yaml
betekenis_lage_landen: |
  Apart stuk: wat deze heilige voor het christendom of de Orthodoxie
  in de Lage Landen betekende.
selectie: voldoet            # of: nader-onderzoek | kandidaat-schrappen
selectie_toelichting: "…"    # beheer; bij nader/kandidaat ook fallback publiek
selectie_toelichting_publiek: "…"  # optioneel; lezersversie
id_aliassen: [lubuinus]      # oude ids na een merge
```

- **`betekenis_lage_landen`** — verplicht bij `bronlaag: nagekeken` voor
  `soort: heilige`. Zelfde referentieverplichting als verhaal.
  Op de heiligenpagina als **Betekenis voor de Lage Landen** (vóór
  verhaal; `samenvatting` komt niet op de heiligenpagina); ook in
  `site/static/data/entries.json` (alleen bij heiligen).
- **`selectie`** — toetsing aan de criteria. Ontbreekt bij een heilige:
  behandel als `nader-onderzoek`. Waarden: `voldoet`, `nader-onderzoek`,
  `kandidaat-schrappen`. Bij de laatste twee: uitklap onderaan de pagina
  (`<details>`). Bij `voldoet`: niets. `kandidaat-schrappen` staat in het
  heiligenoverzicht (groep **Kandidaat**), niet in kalender, ICS of
  datumpagina.
- **`id_aliassen`** — oude `[a-z0-9_-]+` ids; niet gelijk aan het eigen id
  en niet gelijk aan een ander levend entry-id. `generate.py` zet Hugo
  `aliases` (`/heiligen/<oud-id>/`).

Niemand wordt automatisch geschrapt. `kandidaat-schrappen` is een markering
voor een later, expliciet besluit.

Werklijst (beslissingen, geen catalogustelling): [`docs/inventaris.md`](inventaris.md).
`selectie` staat per heilige in YAML; gegenereerd overzicht `/beheer/selectie/`.
Ideeën (troparia, betekenis op andere feestdagen, parochiepatronen):
[`site/content/beheer/ideeen.md`](../site/content/beheer/ideeen.md).

## Referenties

Verhaal, samenvatting, `betekenis` (feest) of `betekenis_lage_landen`
mag alleen als er minstens één referentie is.
Elke referentie heeft `bron_id` en/of `label`, plus een **raadpleegbare locator**:

- `url` — bij voorkeur, of
- `isbn` (+ optioneel `pagina`), of
- `locator` — vrije tekst (archief, app, signatuur, …)

Optioneel:

- `geraadpleegd` — `YYYY-MM-DD`
- `inhoud` — 1–3 zinnen voor de lezer: wat je in deze bron leest of ziet
- `opmerking` — interne notitie; publiek alleen als `inhoud` ontbreekt

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

Sectiekop op de pagina: **Verder lezen en kijken**. Checklist bij bronnen:
`/beheer/how-to-bron-beoordelen/`.
`bron_id` verwijst naar `data/bronnen/bronnen.yaml` (naam/metadata); de locator
hoort **ook** op de referentie zelf te staan.

## Bronlaag

- `encyclopedie` — tekst volgt open naslagwerken (Wikipedia, heiligen.net)
- `nagekeken` — nagekeken tekst met traceerbare bronnen (lexikon, vita, …)

Zelfde paginastructuur; `generate.py` zet een publieke bronzin.
Default als het veld ontbreekt: `encyclopedie`.

Voor **heiligen** geldt `nagekeken` alleen als:

1. `betekenis_lage_landen` aanwezig en niet leeg is, en
2. er minstens één referentie is die **niet** alleen Wikipedia of
   heiligen.net is (die twee mogen aanvullen).

Feesten en vasten: `nagekeken` blijft «nagekeken tekst met traceerbare
bronnen» (referentieverplichting bij verhaal/samenvatting/`betekenis`).

Verouderd: `status: stub` / `status: curated`.

## Plaatsen

Register: [`data/plaatsen.yaml`](../data/plaatsen.yaml). Op een heilige:

```yaml
locaties:
  - utrecht              # plaats-id, geen vrije tekst
rustplaats:
  plaats: maastricht
  toelichting: "Sint-Servaasbasiliek"
```

`soort: plaats` krijgt een marker als minstens één heilige die id in
`locaties` heeft. `soort: streek` (Vlaanderen, Friesland) is vooral voor
zoeken; een marker alleen als een heilige die streek-id zelf in
`locaties` heeft. Op een heilige: liever concrete plaatsen; streek-ids
alleen als aanvulling of bij gebrek aan een betere plek. Optioneel
`streek:` op een plaats koppelt zoeken («Vlaanderen» vindt Drongen).
Geen relieken- of bedevaartenlijst.

## Icoon

Eén icoon (bestaande entries):

```yaml
icoon:
  bestand: iconen/willibrord.jpg   # relatief t.o.v. site/static/
  rechten: ok                      # ok | onbekend | nee
  licentie: "Publiek domein"
  bron: "Wikimedia Commons — File:…"
```

Meerdere afbeeldingen: lijst `iconen` in plaats van `icoon`. Precies één
item `primair: true` (infobox en overzichten). Extra’s blijven lokaal
bewaard; bestandsnamen niet overschrijven.

```yaml
iconen:
  - bestand: iconen/odulphus-hemelum.jpg
    primair: true
    soort: foto                    # foto | reproductie
    plaats: hemelum                # optioneel plaats-id
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

`rechten: ok` is verplicht om te tonen. `bestand` is een lokaal pad, geen
`http(s)`-URL. `bron` en `licentie` zijn verplicht als `bestand` gezet is.
`generate.py` zet het primaire pad plus bijschrift op de entry-pagina;
overige zichtbare items komen als extra infobox-figuren. Ontbreekt een
legaal bestand: veld weglaten. `icoon` en `iconen` niet combineren.
Toevoegen: commando `icoon` (naam of id; parochieplaats + toestemming
mag).
