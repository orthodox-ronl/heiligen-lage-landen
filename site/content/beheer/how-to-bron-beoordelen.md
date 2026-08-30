---
title: "Bron beoordelen"
description: "Checklist: inhoud voor de lezer, aliassen, plaatsen, iconen"
weight: 25
git_date: 2026-08-30
---

Gebruik deze checklist bij **elke** bron (webpagina, lexikon, vita, boek)
die u voor een heilige of feest bekijkt. Zo schrijft u een bruikbare
`inhoud`-zin voor de lezer én vist u aliassen, plaatsen en beeldmateriaal
eruit. Komt u later ergens een bron tegen: zelfde stappen, daarna YAML
bijwerken.

Zie ook [heilige of feest]({{% ref "/beheer/how-to-heiligen-feesten" %}})
en [namen]({{% ref "/beheer/how-to-namen" %}}).

## Checklist

### 1. Identiteit

- Over welke heilige of welk feest gaat het (ons `id`)?
- Welke spellingen, historische namen of epitheta staan in de bron?
- → Kandidaten voor `namen.alternatief` (id/bestandsnaam niet wijzigen).

### 2. Lage Landen

- Waar is hij/zij geweest, gaan werken, gestorven, begraven of sterk vereerd?
- Concrete plaatsen of streken noemen (Utrecht, Dokkum, Tongeren, Frisia, …).
- → `locaties:` / `rustplaats:` met ids uit `data/plaatsen.yaml`; nieuwe
  plaats eerst daar toevoegen.

### 3. Handeling

- Wat deed hij/zij *hier* dat opname in deze kalender rechtvaardigt?
- → Voedt `betekenis_lage_landen` (paginakop **Betekenis voor de Lage Landen**).

### 4. Inhoud voor de lezer

- Wat vind je **concreet** in deze bron: korte vita, lange vita, kaart,
  liturgische tekst, discussie over historiciteit, icoonpagina, …
- → Op de referentie: `inhoud:` (1–3 zinnen) + `geraadpleegd: YYYY-MM-DD`.
- `opmerking:` alleen voor interne notities; die wordt niet getoond als
  `inhoud` gezet is.

### 5. Beeldmateriaal

- Staat er een icoon of portret met **herbruikbare** licentie?
- Op Wikimedia Commons: open de **File:**-pagina, lees de licentie
  (publiek domein, CC0, of CC-BY/-SA met naamsvermelding).
- → Bestand lokaal naar `site/static/iconen/<id>.jpg` (of `.png`); in YAML
  `icoon` met `rechten: ok`, `bron`, `licentie` (mapping of lijst). Geen hotlinks.
  Script: `icoon` — begint met
  licentie (alleen PD/CC0/CC-BY/CC-BY-SA in de repo). How-to:
  [heiligen en feesten]({{% ref "/beheer/how-to-heiligen-feesten" %}})
  (sectie Icoon).

### 6. Bronkwaliteit

- Encyclopedie (Wikipedia, heiligen.net) of steviger (lexikon, vita,
  OrthodoxWiki, vaktekst)?
- → Bepaalt of de entry `bronlaag: nagekeken` mag (bestaande regels in
  how-to heiligen).

### 7. Besluit

- Wel of niet als `referenties[]`-regel opnemen?
- Zo ja: meteen YAML bijwerken (aliassen, plaatsen, `inhoud`, eventueel
  icoon) — niet «later nog eens».

## Voorbeeld `inhoud`

```yaml
- label: "Heiligenlexikon — Bonifatius"
  url: "https://www.heiligenlexikon.de/BiographienB/Bonifatius.html"
  geraadpleegd: "2026-08-20"
  inhoud: >
    Lexikonvita met missie in Frisia en martelaarschap bij Dokkum;
    verwijzingen naar Willibald van Mainz.
```

## Later een bron tegenkomen

Zelfde checklist. Eén bron kan **meerdere** entries raken (bijv. een
overzicht van Friese missionarissen): herhaal stap 1–7 per entry.
