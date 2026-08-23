---
title: Feestdatum (technisch)
description: YAML-invoer van vaste dagen; stijl is documentatie, geen +13 op de dagnaam
uitleg_stijl: feestdatum-technisch
build:
  list: never
  render: always
git_date: 2026-08-20
---

Technische bijlage bij de [uitleg Feestdatum]({{% ref "/uitleg/feestdatum" %}}).

Normatief datamodel: [docs/datamodel.md](https://github.com/orthodox-ronl/heiligen-lage-landen/blob/main/docs/datamodel.md).
How-to: [heiligen en feesten wijzigen]({{% ref "/beheer/how-to-heiligen-feesten" %}}).

## Vaste dag

```yaml
datum:
  waarde: "08-15"          # MM-DD = feestdatum (dagnaam)
  # stijl weglaten = gregoriaans (default) — alleen documentatie van de invoer
  stijl: juliaans
```

`stijl` legt vast hoe de beheerder `waarde` bedoelde. Er wordt géén
automatische offset op de feestdatum zelf toegepast. De offset speelt pas
als de site de **burgerlijke vierdatum** in de stand Oud berekent.

Optioneel expliciet beide notaties:

```yaml
datum:
  gregoriaans: "08-15"
  juliaans: "08-15"
```

## Paascyclus

Dagen zonder vaste feestdatum:

```yaml
cyclus: paascyclus
datum:
  paascyclus:
    anker: pascha
    offset_dagen: 0        # t.o.v. Orthodox Pascha (negatief = vóór)
```

Bereik in generatie en ICS: huidig jaar −2 … +5. Functies:
`pascha_offset_date` in `scripts/kalender.py`.

## Weekdag t.o.v. een feestdatum

```yaml
cyclus: jaar
datum:
  weekdag_relatief:
    anker: "12-25"
    weekdag: 7
    welke: 1
    richting: voor
```

`weekday_relative_date` in `scripts/kalender.py`. Stand Oud: anker is de
Juliaanse feestdatum van dat jaar. Niet in het Synaxarion. Zaterdag/zondag
rond Kruisverheffing en Theofanie, en zaterdag vóór Kerst: alleen
lezingenoverrides, geen feest-YAML. Zondag ná 10 oktober: wél feest-YAML.

## Ids

Bestandsnaam = `id` = `[a-z0-9_-]+`. Weergavenamen staan in het
entry-bestand (`namen.primair` / `alternatief`). Zie
[namen wijzigen]({{% ref "/beheer/how-to-namen" %}}).
