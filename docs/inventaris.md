# Inventaris heiligen van de Lage Landen

Beslissingslog: wie erin hoort, wie nader onderzocht wordt, wie kandidaat
is om te schrappen, en welke post-schisma-heiligen bewust **niet** in de
catalogus staan. Geen telling van het aantal YAML-bestanden — die wijzigt.

Live overzicht (gegenereerd uit `selectie` op elke heilige):
`/beheer/selectie/`. Scores zelf: `data/heiligen/*.yaml`.
Niemand van de huidige lijst is verwijderd; `kandidaat-schrappen` is alleen
een markering.

Criteria (normatief voor gebruikers):
[Heiligen van de Lage Landen](../site/content/uitleg/heiligen.md).
Velden: [docs/datamodel.md](datamodel.md).

Post-schisma-onderzoek (17 augustus 2026):
[eerste ronde](onderzoek/post-schisma-orthodoxe-heiligen-lage-landen.md),
[aanvulling Russische/ROCOR/parochielijsten](onderzoek/post-schisma-aanvulling-2026-08-17.md).

## Afbakening bij het scoren

- **Voldoet:** vóór het schisma in **huidig Nederland, België of Luxemburg**
  geweest én daar iets gedaan (prediking, stichting, martelaarschap, bestuur
  van kerk of klooster). Niet alleen doorreis.
- **Nader onderzoek:** werk vooral in historische Nederlanden die nu in
  Frankrijk liggen; of de persoon is te legendarisch om de toets hard te
  maken; of de band met de Lage Landen is vooral later bisdom/cultus; of
  de invloed is **indirect** (bijv. opleiding van missionarissen) — deur
  open, geen actieve verzameling.
- **Kandidaat-schrappen:** niet in de Lage Landen geweest; werk elders
  (Boven-Rijn, Heidenheim); of na het schisma westers, zonder orthodoxe
  bijdrage aan NL/BE.

Op de heiligenpagina verschijnt bij *nader onderzoek* en
*kandidaat-schrappen* een uitklap **Plaats in deze kalender**. Bij
*voldoet* niets.

Post-schisma: alleen Orthodox vereerd **én** bijgedragen aan de Orthodoxie
in NL/BE. Een kerk of parochie die naar iemand is genoemd, of een
Nederlandse dienst/vertaling, is daarvoor niet genoeg.

## Besluiten 17 augustus 2026

YAML in `data/heiligen/`. `selectie: voldoet` voor de nieuwe ids.

### Post-schisma — toevoegen

| Id | Naam | Grond |
| --- | --- | --- |
| `johannes-van-shanghai` | Johannes Maximovitsj van Shanghai | Categorie A: institutionele ontwikkeling van de Orthodoxie in Nederland |
| `sophrony-van-essex` | Sophrony (Sacharov) van Essex | Categorie B: liturgie in Gent (14 september 1980); geestelijke raad aan de stichteres van Asten |

Feestdag, `betekenis_lage_landen` en `bronlaag: nagekeken`. Voor Johannes
de keten 1952 (bezoek) / 1954 (opname in zijn bisdom, wijding van Jakob
Akkersdijk, klooster Johannes de Doper in Den Haag) meenemen; het bisdom
van 1965 later toetsen aan synodale stukken. Pervijze (1976, vanuit Den
Haag) is bron voor Nederlandstalige liturgie, geen aparte heilige.

### Post-schisma — niet invoeren

Alleen lokale cultus of patroonschap (C), of invloed uitsluitend via een
andere heilige (D).

| Heilige | Onderzoek | Waarom niet |
| --- | --- | --- |
| Silouan de Athoniet | D/C | Geen persoonlijke relatie met NL/BE; invloed via Sophrony |
| Tichon van Moskou | C | Parochie Nijmegen (2005); ROCOR-stichting is te indirect |
| Sergius van Radonezj | C | Parochie Amsterdam/Haarlem (2022); patroon, geen eigen bijdrage |
| Serafim van Sarov | C | Parochie Namen; kerk Luik (met Alexander Nevski) |
| Porfyrios van Kavsokalivia | C | Parochie Tilburg; geen eigen historische bijdrage |
| Nektarios van Egina | C | Patroon van Eindhoven; geen eigen historische bijdrage |
| Paisios de Athoniet | C | Parochie Lasne; geen eigen historische bijdrage |
| Alexander Nevski | C | Patroon van Rotterdam (en Luik); geen eigen historische bijdrage |
| Dorothea van Kashin | C | Kapel bij Asten; lokale verering |
| Maria van Egypte | C | ROCOR-parochie Aalsmeer |
| Johannes de Doper | C | Patroon van het Haagse missieklooster; universeel, pre-schisma |
| Johannes Chrysostomos | C | Parochie Maastricht (met Servatius); universeel, pre-schisma |
| Nicolaas van Myra | C | Klooster Hemelum e.a.; universeel, pre-schisma |

Pre-schisma patroonheiligen van huidige parochies (Maximos de Belijder,
Theofano, Antonius en Theodosius van Kiev, Nicolaas, Johannes de Doper,
Chrysostomos) horen niet automatisch in de catalogus: alleen
patroonschap volstaat niet. Servatius is geen patroon-alleen: hij
werkte in Maastricht/Tongeren.

Later denkbaar: een gemerkte groep **parochiepatronen** (categorie C/D)
onderaan de daglijst, met link naar de parochiesite. Dat is geen
vervanging van de kernselectie. Zie [docs/voorstellen.md](voorstellen.md).

### Pre-schisma — toevoegen

Alle zeven voldoen aan «in de Lage Landen geweest en daar iets gedaan».

| Id | Naam | Toets |
| --- | --- | --- |
| `servatius` | Servatius van Maastricht / Tongeren | Apostel van de Maasstreek; eerste bisschop van Tongeren |
| `otger` | Otger | Metgezel van Wiro en Plechelm; stichting Odiliënberg |
| `odulphus` | Odulphus | Kanunnik van Utrecht; missie in Friesland (Stavoren) |
| `begga` | Begga | Dochter van Iduberga; stichting Andenne |
| `monulphus` | Monulphus | Bisschop van Maastricht (samen met Gondulphus) |
| `gondulphus` | Gondulphus | Bisschop van Maastricht |
| `rumold` | Rumold van Mechelen | Martelaar / Mechelen |

Bestaande kern met `betekenis_lage_landen` en `bronlaag: nagekeken` waar
minstens één bron niet Wikipedia/heiligen.net is: Willibrord, Bonifatius,
Lambertus, Lebuinus, Adelbert, Gertrudis, Dymphna. Jeroen, Walfridus,
Bavo, Cunera, Werenfrid, Radboud, Oda van de Peel blijven
`bronlaag: encyclopedie` tot een niet-encyclopedische bron is nagetrokken.

## Beleidslijsten (geen catalogusdump)

Toelichting per id staat in de YAML. De groep **voldoet** groeit; die
staat niet hier. Live: `/beheer/selectie/`.

### Nader onderzoek

| Id | Toelichting |
| --- | --- |
| `adelgonda` | Maubeuge; historisch Henegouwen, nu Frankrijk |
| `agricolaus-van-maastricht` | Vroege/legendarische bisschop van Maastricht |
| `aubertus-van-kamerijk` | Kamerijk nu in Frankrijk; bisdom reikte tot Henegouwen |
| `folciunus` | Folquinus van Terwaan; bisdom nu in Frankrijk |
| `medardus` | Noyon (Picardië); band vooral via later bisdom of cultus |
| `quirillus-van-tongern` | Vroege bisschop van Tongeren; of hij historisch is, is onzeker |
| `winnocus` | Wormhout; historisch Vlaanderen, nu Frankrijk |
| `egbert-van-rathmelsigi` | Indirecte invloed via opleiding missie (Rath Melsigi); zelf niet hier |

### Kandidaat-schrappen

Niet verwijderen tot een uitdrukkelijk besluit.

| Id | Toelichting |
| --- | --- |
| `adela-van-vlaanderen` | Gestorven 1079; westerse cultus na het schisma |
| `fridolin` | Boven-Rijn (Säckingen) |
| `walburga` | Abdis van Heidenheim |
| `winnibald` | Heidenheim / Engeland |
| `lioba` | Tauberbischofsheim; Lioba-klooster Egmond is later patroonschap |

## 30 augustus 2026

Icoon Hemelum (zondag heiligen Lage Landen): halo-namen Herlindis, Relindis
en Lioba.

| Id | Naam | Selectie | Toets |
| --- | --- | --- | --- |
| `herlindis` | Herlindis van Aldeneik | voldoet | Eerste abdis Aldeneik/Maaseik; wijding Willibrord |
| `relindis` | Relindis van Aldeneik | voldoet | Tweede abdis Aldeneik; opvolgster van Herlindis |
| `lioba` | Lioba | kandidaat-schrappen | Werk in Germanië; Egmond 1935 is patroonschap |
