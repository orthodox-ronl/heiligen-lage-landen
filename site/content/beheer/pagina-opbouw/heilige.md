---
title: "Heilige (detail)"
description: "Contract: vita-pagina van één heilige van de Lage Landen"
git_date: 2026-08-21
---

**Contract, geen echte inhoud.** Voor wie: bezoeker. Canonieke URL:
`/heiligen/<id>/`. Bron: gegenereerd uit `data/heiligen/<id>.yaml`
(`generate.py`). Deze markdown niet redigeren.

Volgorde hieronder is de slotvolgorde. Generator en YAML volgen dit
contract.

## Titel

**Wel:** primaire weergavenaam.

**Niet:** «Icoon in parochie» in de titel; interne id als titel.

## Infobox

**Wel:** icoon alleen met lokale licentie (`rechten: ok`) plus bron en
licentie in het bijschrift. Daarna, voor zover bekend: titel(s); ook-namen;
feestdag (link naar datumpagina; tussen haakjes alleen de burgerlijke
datum op de oude kalender, met popover); leefde; plaatsen (streek cursief, link
naar het overzicht); rustplaats (waar het lichaam traditioneel rust, geen
verspreide relieken).

**Niet:** `selectie`; `bronlaag` als label in de box; «Soort: Heilige»
(dat volgt al uit de sectie); hotlink naar een icoon elders.

## Feestdag in de body

**Gesloten.** De infobox heeft Feestdag; de body herhaalt die regel
(**Feestdag:** met link). Dat is bewust: de box is naslag, de body is
leesvolgorde.

**Wel:** dezelfde canonieke dag als in de infobox, inclusief haakjes met
alleen de oude burgerlijke datum; bij geen vaste dag:
dezelfde vijfjaren-tabel als op een feest (lopend jaar plus vier). Extra
gedenkdagen (orthodox bekend)
als **Andere gedenkdagen**, niet als tweede canonieke Feestdag.

**Niet:** een andere canonieke datum dan in de infobox; een katholieke
of lokale datum die in de Orthodoxe Kerk niet bekend is.

## Meerdere gedenkdagen

Sommige heiligen hebben meer dan één dag (verschil orthodox/katholiek,
of meerdere orthodoxe gedachtenissen). **Canoniek** is de sterfdag
(bij Johannes de Doper: de Onthoofding). Andere dagen noemen we als
zij **ook in de Orthodoxe Kerk** bekend zijn: in YAML `datum.extra`,
op de pagina onder **Andere gedenkdagen**.

In YAML is `datum.waarde` die canonieke dag. Extra dagen komen niet
als tweede infobox-Feestdag.

## Betekenis voor de Lage Landen

**Wel:** wat deze heilige voor het christendom of de Orthodoxie **in de
Lage Landen** deed of betekende (prediking, stichting, martelaarschap,
bestuur, opbouw van de Orthodoxie hier). Feiten, in gewone taal.

**Niet:** interne statuswoorden (`kandidaat-schrappen`,
`nader-onderzoek`, `selectiegrens`); «vandaar schrappen»; de
redeneertrant van de inventaris. Dat hoort op
[Uitleg heiligen]({{% ref "/uitleg/heiligen" %}}) (beleid) en
[Selectie heiligen]({{% ref "/beheer/selectie" %}}) (status per id).

## Samenvatting

**Wel:** korte aanduiding wie dit is (zonder kop, zoals nu), consistent
met infobox-datum.

**Niet:** het hele verhaal; selectie-oordeel.

## Verhaal

**Wel:** vita in het kort, brongebaseerd.

**Niet:** preek; beleid wie erin hoort; YAML-veldnames.

## Verder lezen en kijken

**Wel:** referenties met `inhoud` voor de lezer (wat u in die bron
vindt); werkende locator.

**Niet:** interne `opmerking` als die de `inhoud` vervangt; kale URL
zonder toelichting als `inhoud` ontbreekt terwijl we die wél kunnen
schrijven.

## Over de bronnen

**Wel:** optionele toelichting `over_bronnen`; daarna de zin over
bronlaag (nagekeken vs. open naslagwerk) in gewone taal.

**Niet:** `bron_id`-catalogusdump; how-to «zo voegt u een bron toe».

## Plaats in deze kalender

**Gesloten.** Bij `selectie: voldoet`: **niets** op de pagina.

Bij `nader-onderzoek` of `kandidaat-schrappen`: onderaan een
**uitklap** (`<details>`), standaard dicht. Daarin:

- een korte samenvatting van de status (twijfel, of waarschijnlijk
  niet bij de criteria);
- wat daarvoor het argument is (lezersversie, geen interne tokens);
- een verwijzing naar [Heiligen van de Lage Landen]({{% ref "/uitleg/heiligen" %}})
  (ontwerpkeuze en hoe we met twijfel omgaan).

**Wel:** gewone taal; geen automatische verwijdering.

**Niet:** de tokens `kandidaat-schrappen` / `nader-onderzoek` in de
lezerstekst; dit blok bij heiligen die voldoen; het oordeel in
**Betekenis voor de Lage Landen**.

YAML-status blijft op `/beheer/selectie/` en in het entry-bestand.
