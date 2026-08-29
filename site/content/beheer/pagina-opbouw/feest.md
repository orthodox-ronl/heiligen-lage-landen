---
title: "Feest (detail)"
description: "Contract: pagina van één feest (jaarcyclus of paascyclus)"
git_date: 2026-08-21
---

**Contract, geen echte inhoud.** Voor wie: bezoeker. Canonieke URL:
`/feesten/<id>/`. Bron: gegenereerd uit `data/feesten/<id>.yaml`.

## Titel

**Wel:** primaire feestnaam.

**Niet:** een preekachtige ondertitel; interne id als titel.

## Infobox

**Wel:** icoon alleen met lokale licentie. Soort: Feest. Datum: feestdag
(burgerlijk, met tussen haakjes alleen de oude-kalenderdatum en popover),
periode, paascyclus-offset of «zondag vóór/na …» — wat bij dit feest
hoort. Vastenlabel van díe entry als dat in YAML staat.

**Niet:** Lage-Landen-selectie (feesten hebben dat veld niet als
opnamecriterium); hotlinks; «Soort» plus nog eens dezelfde zin in de
body.

## Datumtoelichting in de body

**Wel:** bij paascyclus of weekdag-relatief: een **tabel** «Komende
jaren» (burgerlijk), zodat de infobox niet overloopt. Vijf rijen: het
**lopende burgerlijke jaar** en de vier daarop. Kolommen bij één dag:
Jaar, Datum. Bij een periode: Jaar, Van, Tot. Bij een datum die op de
oude kalender burgerlijk anders valt: die burgerlijke datum tussen
haakjes, met popover (geen bijschrift onder de tabel). Paascyclus
zonder vast einde: geen haakjes. Geen opsomming met copypaste-jaren
van het ICS-venster.

**Niet:** een Juliaanse dagnaam van dezelfde burgerlijke dag als tweede
kolom; «oude kalender» als tekst in de haakjes; een bijschrift onder de
tabel; een tweede, afwijkende canonieke feestdatum; meer of minder dan
die vijf jaren; het ICS-bereik (huidig −2 … +5) op deze pagina; een
tweede knop Nieuw/Oud op deze pagina.

Bij vaste dag: **Feestdag:** in de body mag (zelfde dag als de infobox,
inclusief haakjes met alleen de oude burgerlijke datum;
zie [Heilige]({{% ref "/beheer/pagina-opbouw/heilige" %}})).

## Betekenis

**Wel:** 1–3 alinea’s ná het verhaal: het geheim van het feest én
kernachtig wat de Kerk die dag van de gelovige vraagt (houding,
wijding, waarom van het vasten — geen tweede vastentabel). Orthodox,
weinig jargon, geen preek. Alleen als YAML `betekenis` heeft. Nu: de
twaalf grootfeesten, Pascha, Lazarus-zaterdag en Grote Week-dagen, de
kernfeesten Allerheiligen, Geestesmaandag, Pokrov, Petrus en Paulus,
Johannes (geboorte en onthoofding), Besnijdenis, begin kerkelijk jaar,
de Triodion-zondagen (Zacheüs tot Maria van Egypte, plus Schone
Maandag), Thomas tot de Blinde, Midden-Pinksterfeest, de concilie- en
voorvaderzondagen, de Allerzielen-zaterdagen, en de Zondag van de
heiligen van de Lage Landen.
Bronnen: kerkvaders
en dienstboek eerst; Hopko als brug; Johannes van Shanghai of Sophrony
alleen als naspraak, niet als enige bron. Zelfde bronlaag als de rest
van de pagina. De kop
**Betekenis** heeft een popover: ontbreekt `goedkeuring`, dan dat de
tekst is ontleend aan de genoemde bron(nen) en dat we nog iemand
zoeken die van huis uit orthodox is om haar te toetsen; anders wie
goedkeurde (en eventuele opmerking).

**Niet:** herhaling van het verhaal; preek; troparion/kondakion;
«Betekenis voor de Lage Landen» (feesten hebben dat niet). Geen
apart betekenis-stuk op voorfeest, nafeest, synaxis, weken of Boterweek.
Troparia: [Ideeën]({{% ref "/beheer/ideeen" %}}).
Verwar `goedkeuring` niet met `bronlaag`.

## Samenvatting en verhaal

**Wel:** korte aanduiding; gebeurtenis (wat de Kerk op die dag viert).

**Niet:** selectiebeleid heiligen; lokale parochieaankondigingen.

## Verder lezen en Over de bronnen

Zelfde criteria als [Heilige]({{% ref "/beheer/pagina-opbouw/heilige" %}}):
referenties voor de lezer; bronlaag-zin; geen how-to.
