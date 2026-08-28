"""Catalogus paascyclus-dagen (offsets t.o.v. Orthodox Pascha = 0)."""

from __future__ import annotations

from typing import Any

# offset_dagen: dagen na Pascha (negatief = vóór).
# observances: kleuren/lagen voor later (feest/vasten); multi-kleur UI staat op TODO.
PAASCYCLUS: list[dict[str, Any]] = [
    {
        "id": "zacheus-zondag",
        "offset_dagen": -77,
        "namen": {"primair": "Zacheüs-zondag"},
        "observances": ["feest"],
        "samenvatting": "Begin van de voorbereiding op de Grote Vasten; evangelie van Zacheüs.",
        "verhaal": (
            "De zondag van Zacheüs opent in veel Orthodoxe tradities de reeks "
            "Triodion-zondagen die naar de Grote Vasten leiden. Het evangelie "
            "(Lc. 19) over de tollenaar die Christus wil zien, nodigt uit tot "
            "bekering en verlangen naar Gods aanwezigheid."
        ),
    },
    {
        "id": "zondag-tollenaar-en-farizeeer",
        "offset_dagen": -70,
        "namen": {"primair": "Zondag van de tollenaar en de Farizeeër"},
        "observances": ["feest"],
        "samenvatting": "Opening van het Triodion; les over ootmoedig gebed.",
        "verhaal": (
            "Met deze zondag begint het liturgische boek Triodion. De gelijkenis "
            "(Lc. 18) stelt de nederige tollenaar tegenover de zelfgenoegzame "
            "Farizeeër: rechtvaardiging komt door berouw, niet door opscheppen "
            "over verdiensten."
        ),
    },
    {
        "id": "zondag-verloren-zoon",
        "offset_dagen": -63,
        "namen": {"primair": "Zondag van de verloren zoon"},
        "observances": ["feest"],
        "samenvatting": "Gelijkenis van de barmhartige vader; oproep tot terugkeer.",
        "verhaal": (
            "De Kerk leest de gelijkenis van de verloren zoon (Lc. 15). God "
            "wacht als een vader op wie terugkeert. In de voorvasten klinkt zo "
            "het thema van bekering en thuiskomst."
        ),
    },
    {
        "id": "zaterdag-allerzielen-vleesmijding",
        "offset_dagen": -57,
        "namen": {"primair": "Allerzielen-zaterdag (vóór Vleesvaarwel)"},
        "observances": ["feest"],
        "samenvatting": "Gedachtenis van alle overledenen vóór de Vleesvaarwelzondag.",
        "verhaal": (
            "Op deze zaterdag gedenkt de Kerk allen die in geloof zijn "
            "ontslapen. De voorvasten verbindt zo gebed voor de levenden met "
            "voorbede voor de doden."
        ),
    },
    {
        "id": "zondag-laatste-oordeel",
        "offset_dagen": -56,
        "namen": {
            "primair": "Zondag van het Laatste Oordeel (Vleesvaarwel)",
            "alternatief": [
                "Vleesvaarwelzondag",
                "Zondag van het Laatste Oordeel",
                "Vleesvaarwel",
            ],
        },
        "observances": ["feest"],
        "samenvatting": "Laatste dag met vlees; evangelie van het Laatste Oordeel.",
        "verhaal": (
            "Vleesvaarwelzondag is de laatste dag waarop traditioneel vlees "
            "wordt gegeten vóór de vasten. Het evangelie van het Laatste Oordeel "
            "(Mt. 25) herinnert eraan dat liefde tot de naaste meetelt voor Gods "
            "oordeel. Daarna volgt de Boterweek."
        ),
    },
    {
        "id": "vergevingszondag",
        "offset_dagen": -49,
        "namen": {
            "primair": "Vergevingszondag",
            "alternatief": [
                "Zondag van de verdrijving uit het paradijs",
                "Vergevingszondag",
                "Zuivelvaarwel",
            ],
        },
        "observances": ["feest"],
        "samenvatting": "Einde van de Boterweek; wederzijdse vergeving vóór de Grote Vasten.",
        "verhaal": (
            "Op Vergevingszondag vraagt de gemeenschap elkaar om vergeving en "
            "begint ’s avonds de Grote Vasten. De Kerk gedenkt de verdrijving "
            "uit het paradijs en wijst op terugkeer door vasten, gebed en "
            "barmhartigheid. Kaas, eieren en andere zuivelproducten worden "
            "na deze dag traditioneel gemeden tot Pascha."
        ),
    },
    {
        "id": "schone-maandag",
        "offset_dagen": -48,
        "namen": {"primair": "Schone Maandag (begin Grote Vasten)"},
        "observances": ["vasten"],
        "samenvatting": "Eerste dag van de Grote Vasten.",
        "verhaal": (
            "Schone Maandag opent de veertigdagenvasten. De nadruk ligt op "
            "reiniging van hart en gewoonten: gebed, onthouding en aalmoezen "
            "als weg naar Pascha."
        ),
    },
    {
        "id": "zondag-orthodoxie",
        "offset_dagen": -42,
        "namen": {"primair": "Eerste zondag van de Vasten (Zondag van de Orthodoxie)"},
        "observances": ["feest", "vasten"],
        "samenvatting": "Herstel van de iconenverering; eerste vastenzondag.",
        "verhaal": (
            "Deze zondag viert het herstel van de iconen in 843 na de "
            "iconoclastische strijd. De Orthodoxy-processie belijdt het geloof "
            "van de Kerk en de rechtmatigheid van heilige beelden als vensters "
            "op de incarnatie."
        ),
    },
    {
        "id": "zondag-gregorius-palamas",
        "offset_dagen": -35,
        "namen": {"primair": "Tweede zondag van de Vasten (Gregorius Palamas)"},
        "observances": ["feest", "vasten"],
        "samenvatting": "Gedachtenis van de heilige Gregorius Palamas.",
        "verhaal": (
            "De tweede vastenzondag eert Gregorius Palamas (†1359), leraar van "
            "het hesychasme en de onderscheiding tussen Gods wezen en energieën. "
            "Zijn theologie verbindt vasten met werkelijke gemeenschap met God."
        ),
    },
    {
        "id": "zondag-kruisverering",
        "offset_dagen": -28,
        "namen": {"primair": "Derde zondag van de Vasten (Kruisverering)"},
        "observances": ["feest", "vasten"],
        "samenvatting": "Midden in de vasten: verering van het Heilig Kruis.",
        "verhaal": (
            "Halverwege de vasten wordt het Kruis ter verering opgesteld. Het "
            "sterkt de gelovigen op weg naar Golgotha en Pascha: wie Christus "
            "wil volgen, neemt het kruis op en vindt daarin leven."
        ),
    },
    {
        "id": "zondag-johannes-klimacus",
        "offset_dagen": -21,
        "namen": {"primair": "Vierde zondag van de Vasten (Johannes Klimacus)"},
        "observances": ["feest", "vasten"],
        "samenvatting": "Gedachtenis van Johannes van de Ladder.",
        "verhaal": (
            "Johannes Klimacus, auteur van *De Ladder van de goddelijke opgang*, "
            "wijst de ascetische treden van bekering. De vierde vastenzondag "
            "houdt zijn voorbeeld voor ogen in de strijd van de veertigdagen."
        ),
    },
    {
        "id": "zondag-maria-van-egypte",
        "offset_dagen": -14,
        "namen": {"primair": "Vijfde zondag van de Vasten (Maria van Egypte)"},
        "observances": ["feest", "vasten"],
        "samenvatting": "Gedachtenis van de heilige Maria van Egypte.",
        "verhaal": (
            "Maria van Egypte, van zondares tot woestijnheilige, belichaamt "
            "radicale bekering. Haar leven wordt in de vasten gelezen als hoop "
            "voor wie laat tot inkeer komt."
        ),
    },
    {
        "id": "lazarus-zaterdag",
        "offset_dagen": -8,
        "namen": {"primair": "Lazarus-zaterdag"},
        "observances": ["feest", "vasten"],
        "samenvatting": "Opwekking van Lazarus; vooravond van Palmzondag.",
        "verhaal": (
            "Christus wekt Lazarus uit de doden (Joh. 11) als voorteken van "
            "zijn eigen opstanding. Liturgisch eindigt hier de veertigdagenvasten "
            "streng genomen; de Heilige Week breekt aan."
        ),
    },
    {
        "id": "palmzondag",
        "offset_dagen": -7,
        "namen": {"primair": "Palmzondag (Intocht in Jeruzalem)"},
        "observances": ["feest"],
        "samenvatting": "Christus’ intocht in Jeruzalem; begin van de Heilige Week.",
        "verhaal": (
            "Met palmtakken en hosanna’s viert de Kerk de intocht van de Heer "
            "in Jeruzalem. Tegelijk opent Palmzondag de Heilige Week die naar "
            "het lijden en Pascha leidt."
        ),
    },
    {
        "id": "grote-maandag",
        "offset_dagen": -6,
        "namen": {"primair": "Grote Maandag"},
        "observances": ["vasten"],
        "samenvatting": "Eerste dag van de Heilige Week; Jozef de Alschone; onvruchtbare vijgenboom.",
        "verhaal": (
            "In de Heilige Week richt de liturgie zich op Christus’ weg naar "
            "het kruis. Grote Maandag gedenkt onder meer de kuise Jozef en de "
            "les van de onvruchtbare vijgenboom."
        ),
    },
    {
        "id": "grote-dinsdag",
        "offset_dagen": -5,
        "namen": {"primair": "Grote Dinsdag"},
        "observances": ["vasten"],
        "samenvatting": "Heilige Week; gelijkenissen van waakzaamheid.",
        "verhaal": (
            "Grote Dinsdag houdt de gelijkenissen van de tien maagden en de "
            "talentenvoor ogen: waakzaamheid en trouw terwijl de Bruidegom nadert."
        ),
    },
    {
        "id": "grote-woensdag",
        "offset_dagen": -4,
        "namen": {"primair": "Grote Woensdag"},
        "observances": ["vasten"],
        "samenvatting": "Zalving te Bethanië; verraad van Judas.",
        "verhaal": (
            "De vrouw die Christus zalft en Judas die hem verraadt, staan "
            "tegenover elkaar. De Kerk nodigt uit tot berouw en liefde, niet "
            "tot berekening."
        ),
    },
    {
        "id": "grote-donderdag",
        "offset_dagen": -3,
        "namen": {"primair": "Grote Donderdag"},
        "observances": ["feest", "vasten"],
        "samenvatting": "Laatste Avondmaal; voetwassing; overlevering aan het lijden.",
        "verhaal": (
            "Christus stelt het mysterie van zijn Lichaam en Bloed in, wast "
            "de voeten van de leerlingen en gaat vrijwillig het lijden in. "
            "Grote Donderdag is middelpunt van de Heilige Week vóór Golgotha."
        ),
    },
    {
        "id": "grote-vrijdag",
        "offset_dagen": -2,
        "namen": {"primair": "Grote Vrijdag (Heilige en Grote Vrijdag)"},
        "observances": ["feest", "vasten"],
        "samenvatting": "Kruisiging en graflegging van de Heer.",
        "verhaal": (
            "Op Grote Vrijdag gedenkt de Kerk het lijden, de kruisiging en de "
            "graflegging van Christus. Het is een dag van streng vasten, stilte "
            "en aanbidding van het Kruis — in verwachting van de Opstanding."
        ),
    },
    {
        "id": "grote-zaterdag",
        "offset_dagen": -1,
        "namen": {"primair": "Grote Zaterdag"},
        "observances": ["feest", "vasten"],
        "samenvatting": "Christus in het graf; vooravond van Pascha.",
        "verhaal": (
            "Grote Zaterdag viert Christus’ rust in het graf en zijn nederdaling "
            "ter helle. De liturgie draait al naar het licht van Pascha: de "
            "dood is verslagen, al is de Opstanding nog niet gevierd."
        ),
    },
    {
        "id": "pascha",
        "offset_dagen": 0,
        "namen": {
            "primair": "Pascha (Heilige Opstanding van Christus)",
            "alternatief": [
                "Orthodox Pasen",
                "Feest van de Opstanding",
                "Pascha",
                "Heilige Opstanding van Christus",
                "Heilige Opstanding",
                "Opstanding van Christus",
            ],
        },
        "observances": ["feest"],
        "samenvatting": "Feest van de Opstanding; middelpunt van het kerkelijk jaar.",
        "verhaal": (
            "Pascha is het feest van feesten: Christus is opgestaan uit de "
            "doden. Alle Orthodoxe kerken vieren Pascha op dezelfde datum, "
            "berekend volgens de Alexandrijnse/Juliaanse computus (wereldlijk "
            "vaak op een andere zondag dan westers Pasen). Vanaf hier telt de "
            "lichte week en de weg naar Pinksteren."
        ),
    },
    {
        "id": "lichte-maandag",
        "offset_dagen": 1,
        "namen": {
            "primair": "Lichte Maandag",
            "alternatief": ["Maandag van de Lichte Week"],
        },
        "observances": ["feest"],
        "samenvatting": "Tweede dag van de Lichte Week na Pascha.",
        "verhaal": (
            "De Lichte Week (Bright Week) verlengt de vreugde van Pascha: "
            "de deuren van het altaar blijven open, vasten wijkt, en de "
            "begroeting “Christus is opgestaan!” klinkt aanhoudend."
        ),
    },
    {
        "id": "thomaszondag",
        "offset_dagen": 7,
        "namen": {
            "primair": "Thomaszondag (Antipascha)",
            "alternatief": [
                "Zondag van de ongelovige Thomas",
                "Thomaszondag",
                "Antipascha",
                "Zondag van Thomas",
            ],
        },
        "observances": ["feest"],
        "samenvatting": "Eerste zondag na Pascha; belijdenis van Thomas.",
        "verhaal": (
            "Thomas belijdt “Mijn Heer en mijn God” wanneer hij de wonden van "
            "de Opgestane ziet (Joh. 20). Antipascha sluit de Lichte Week en "
            "opent de reeks zondagen tot Pinksteren."
        ),
    },
    {
        "id": "zondag-myrondraagsters",
        "offset_dagen": 14,
        "namen": {"primair": "Zondag van de myrondraagsters"},
        "observances": ["feest"],
        "samenvatting": "De vrouwen bij het graf; Jozef van Arimatea en Nicodemus.",
        "verhaal": (
            "De myrondraagsters gaan vroeg naar het graf en worden de eerste "
            "getuigen van de Opstanding. Met hen eert de Kerk ook wie Christus "
            "begroef: trouwe liefde na het kruis."
        ),
    },
    {
        "id": "zondag-verlamde",
        "offset_dagen": 21,
        "namen": {"primair": "Zondag van de verlamde"},
        "observances": ["feest"],
        "samenvatting": "Genezing bij Betesda; derde zondag na Pascha.",
        "verhaal": (
            "Christus geneest de verlamde bij het bad Betesda (Joh. 5). De "
            "lezing verbindt lichamelijke heling met het leven dat van de "
            "Opgestane uitgaat."
        ),
    },
    {
        "id": "midden-pinksterfeest",
        "offset_dagen": 24,
        "namen": {"primair": "Midden-Pinksterfeest"},
        "observances": ["feest"],
        "samenvatting": "Halverwege tussen Pascha en Pinksteren.",
        "verhaal": (
            "Het Midden-Pinksterfeest markeert het midden van de vijftig dagen. "
            "Christus leert in de tempel over levend water (Joh. 7): verlangen "
            "naar de gave van de Geest."
        ),
    },
    {
        "id": "zondag-samaritaanse",
        "offset_dagen": 28,
        "namen": {"primair": "Zondag van de Samaritaanse vrouw"},
        "observances": ["feest"],
        "samenvatting": "Ontmoeting bij de put; levend water.",
        "verhaal": (
            "Christus openbaart zich aan de Samaritaanse vrouw (Joh. 4) als "
            "gever van levend water. De Kerk leest dit als uitnodiging tot "
            "aanbidding in Geest en waarheid op weg naar Pinksteren."
        ),
    },
    {
        "id": "zondag-blinde",
        "offset_dagen": 35,
        "namen": {"primair": "Zondag van de blinde"},
        "observances": ["feest"],
        "samenvatting": "Genezing van de blindgeborene.",
        "verhaal": (
            "De genezing van de blindgeborene (Joh. 9) toont Christus als licht "
            "van de wereld. Geloof opent de ogen — thema in de dagen vóór "
            "Hemelvaart."
        ),
    },
    {
        "id": "teruggave-pascha",
        "offset_dagen": 38,
        "namen": {
            "primair": "Teruggave van Pascha",
            "alternatief": ["Apodosis van Pascha", "Teruggave van Pasen"],
        },
        "observances": ["feest"],
        "samenvatting": "Laatste dag van de Pascha-viering vóór Hemelvaart.",
        "verhaal": (
            "Met de teruggave van Pascha eindigt de periode waarin het "
            "opstandingsfeest liturgisch centraal staat. De volgende dag volgt "
            "Hemelvaart."
        ),
    },
    {
        "id": "hemelvaart",
        "offset_dagen": 39,
        "namen": {"primair": "Hemelvaart van de Heer"},
        "observances": ["feest"],
        "samenvatting": "Veertig dagen na Pascha; Christus’ hemelvaart.",
        "verhaal": (
            "Veertig dagen na Pascha viert de Kerk de Hemelvaart: de "
            "opgestane Heer gaat ten hemel en belooft de Geest. Het is een "
            "van de grote feesten van het kerkelijk jaar."
        ),
    },
    {
        "id": "zondag-vaderen-eerste-concilie",
        "offset_dagen": 42,
        "namen": {"primair": "Zondag van de heilige Vaderen van het Eerste Concilie"},
        "observances": ["feest"],
        "samenvatting": "Vaderen van Nicea (325); zondag na Hemelvaart.",
        "verhaal": (
            "Tussen Hemelvaart en Pinksteren eert de Kerk de Vaderen van het "
            "Eerste Oecumenische Concilie te Nicea, die het geloof in Christus "
            "als ware God beleden."
        ),
    },
    {
        "id": "allerzielen-zaterdag-pinksteren",
        "offset_dagen": 48,
        "namen": {"primair": "Allerzielen-zaterdag (vóór Pinksteren)"},
        "observances": ["feest"],
        "samenvatting": "Gedachtenis van de overledenen vóór Pinksteren.",
        "verhaal": (
            "Opnieuw gedenkt de Kerk de ontslapenen, nu aan de vooravond van "
            "Pinksteren, wanneer de Geest de gemeenschap van levenden en doden "
            "verzegelt in Christus."
        ),
    },
    {
        "id": "pinksteren",
        "offset_dagen": 49,
        "namen": {
            "primair": "Pinksteren (Nederdaling van de Heilige Geest)",
            "alternatief": [
                "Feest van de Drie-eenheid",
                "Pinksteren",
                "Nederdaling van de Heilige Geest",
                "Drie-eenheidsfeest",
            ],
        },
        "observances": ["feest"],
        "samenvatting": "Vijftig dagen na Pascha; gave van de Heilige Geest.",
        "verhaal": (
            "Op Pinksteren daalt de Heilige Geest neer op de apostelen. Het "
            "feest voltooit de paascyclus van vijftig dagen en viert de "
            "geborenwording van de Kerk in de kracht van de Geest. Vaak wordt "
            "ook de Allerheiligste Drie-eenheid bijzonder herdacht."
        ),
    },
    {
        "id": "geestesmaandag",
        "offset_dagen": 50,
        "namen": {"primair": "Maandag van de Heilige Geest"},
        "observances": ["feest"],
        "samenvatting": "Tweede dag van Pinksteren; eer aan de Heilige Geest.",
        "verhaal": (
            "De dag na Pinksteren is bijzonder gewijd aan de Heilige Geest. "
            "De vreugde van het feest duurt voort; in veel tradities begint "
            "hierna het Apostolisch vasten."
        ),
    },
    {
        "id": "allerheiligen-zondag",
        "offset_dagen": 56,
        "namen": {"primair": "Allerheiligen-zondag"},
        "observances": ["feest"],
        "samenvatting": "Eerste zondag na Pinksteren; alle heiligen.",
        "verhaal": (
            "Allerheiligen besluit de reeks na Pinksteren met de gedachtenis "
            "van alle heiligen — bekend en onbekend — als vrucht van de Geest. "
            "Daarna begint in veel kerken het Apostolisch vasten tot het feest "
            "van Petrus en Paulus."
        ),
    },
]

REF_DATE = "2026-08-16"
DEFAULT_REFS = [
    {
        "bron_id": "orthodoxwiki-pascha",
        "url": "https://orthodoxwiki.org/Pascha",
        "geraadpleegd": REF_DATE,
    },
    {
        "bron_id": "oca-calendar",
        "url": "https://www.oca.org/saints/lives",
        "geraadpleegd": REF_DATE,
    },
    {
        "bron_id": "orthodoxwiki-triodion",
        "url": "https://orthodoxwiki.org/Triodion",
        "geraadpleegd": REF_DATE,
    },
]
