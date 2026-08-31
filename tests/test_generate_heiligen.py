"""Generatie van heiligenpagina’s, entries.json en beheer-selectie."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from datetime import date

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate import (  # noqa: E402
    CONTENT,
    ICS_YEAR_BACK,
    ICS_YEAR_FORWARD,
    KOMENDE_JAREN_AANTAL,
    _split_hugo_markdown,
    betekenis_bron_labels,
    komende_jaren,
    occurrence_years,
    render_beheer_selectie,
    write_beheer_selectie,
    write_entries_json,
    write_entry_page,
    write_plaatsen_json,
)
from load_entries import load_entries  # noqa: E402


def _heilige(**overrides):
    entry = {
        "id": "voorbeeld",
        "soort": "heilige",
        "bronlaag": "encyclopedie",
        "cyclus": "jaar",
        "lage_landen": True,
        "source_path": "data/heiligen/voorbeeld.yaml",
        "namen": {"primair": "Voorbeeld", "alternatief": ["Altnaam"]},
        "datum_norm": {
            "feestdatum": "11-07",
            "vorm": "dag",
            "stijl": "gregoriaans",
        },
        "datum_extra_norm": [],
        "titels": [],
        "referenties": [],
        "id_aliassen": [],
        "betekenis_lage_landen": "",
        "selectie": "nader-onderzoek",
        "selectie_toelichting": "",
        "observances": ["heilige"],
        "onderdrukt_wekelijks_vasten": False,
    }
    entry.update(overrides)
    return entry


def test_entry_page_heeft_betekenis_en_aliases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            betekenis_lage_landen="Predikte onder de Friezen.",
            id_aliassen=["oud-id"],
            selectie="voldoet",
            selectie_toelichting="niet op de publieke pagina",
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    meta, body = _split_hugo_markdown(text)
    assert meta["aliases"] == ["/heiligen/oud-id/"]
    assert meta["selectie"] == "voldoet"
    assert "niet op de publieke pagina" not in body
    assert "## Betekenis voor de Lage Landen" in body
    assert "Predikte onder de Friezen." in body
    assert "## Over de plaats in deze kalender" not in body
    assert "<details" not in body
    assert "nagekeken aan een lexikon" not in body
    # Bronnoot ná inhoud, onder kop Over de bronnen
    assert "## Over de bronnen" in body
    assert body.index("## Betekenis voor de Lage Landen") < body.index("## Over de bronnen")
    assert body.index("## Verder lezen en kijken") < body.index("## Over de bronnen")
    assert "open naslagwerken" in body
    assert body.index("## Over de bronnen") < body.index("open naslagwerken")
    assert "## Verder lezen en kijken" in body
    assert "## Referenties" not in body
    assert "Synaxarion:" not in body


def test_entry_page_selectie_paragraaf_bij_nader_onderzoek(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="nader-onderzoek",
            selectie_toelichting="Korte beheerzin.",
            selectie_toelichting_publiek="Uitleg voor bezoekers over het grensgeval.",
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    meta, body = _split_hugo_markdown(text)
    assert meta["selectie"] == "nader-onderzoek"
    assert "<details" in body
    assert "<summary>Plaats in deze kalender</summary>" in body
    assert "## Over de plaats in deze kalender" not in body
    assert "nog niet uitgemaakt" in body
    assert "Uitleg voor bezoekers over het grensgeval." in body
    assert "Korte beheerzin." not in body
    assert body.index("## Verder lezen en kijken") < body.index("<details")


def test_entry_page_selectie_fallback_toelichting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="kandidaat-schrappen",
            selectie_toelichting="Alleen cultus, geen werk hier.",
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    meta, body = _split_hugo_markdown(text)
    assert meta["selectie"] == "kandidaat-schrappen"
    assert "<details" in body
    assert "<summary>Plaats in deze kalender</summary>" in body
    assert "## Over de plaats in deze kalender" not in body
    assert "voldoet waarschijnlijk niet" in body
    assert "Alleen cultus, geen werk hier." in body


def test_entry_page_extra_yaml_veld_breekt_niet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="voldoet",
            onderzoek_notitie="Mag in YAML staan zonder render.",
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    assert "onderzoek_notitie" not in text
    assert "Mag in YAML staan" not in text


def test_entry_page_plaatsen_als_namen_en_rustplaats(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            locaties=["utrecht", "drongen"],
            rustplaats={
                "plaats": "echternach",
                "toelichting": "Abdij van Echternach",
            },
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    meta, body = _split_hugo_markdown(text)
    assert meta["locaties"] == ["Utrecht", "Drongen"]
    assert meta["locatie_ids"] == ["utrecht", "drongen"]
    assert meta["locatie_items"] == [
        {"id": "utrecht", "naam": "Utrecht", "soort": "plaats"},
        {"id": "drongen", "naam": "Drongen", "soort": "plaats"},
    ]
    assert "utrecht" not in meta["locaties"]
    assert "Utrecht" in meta["locatie_zoek"]
    assert "Vlaanderen" in meta["locatie_zoek"]
    assert meta["rustplaats_plaats"] == "Echternach"
    assert meta["rustplaats_toelichting"] == "Abdij van Echternach"
    # Plaatsen/rustplaats horen in de Hugo-infobox (front matter), niet in de body.
    assert "**Plaatsen:**" not in body
    assert "**Rustplaats:**" not in body
    assert "[7 november](/datum/?dag=11-07)" in body or "**Feestdag:**" in body


def test_entry_page_infobox_velden_in_front_matter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="voldoet",
            titels=["Apostel van de Friezen"],
            periode="658–739",
            vastenniveau="vis",
            onderdrukt_wekelijks_vasten=True,
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    meta, body = _split_hugo_markdown(text)
    assert meta["titels"] == ["Apostel van de Friezen"]
    assert meta["periode"] == "658–739"
    assert meta["vastenniveau"] == "vis"
    assert meta["onderdrukt_wekelijks_vasten"] is True
    assert meta["feestdatum"] == "11-07"
    assert meta["vierdatum_oud"] == "11-20"
    assert "*Apostel van de Friezen*" not in body
    assert "**Periode:**" not in body
    assert "**Vastenniveau" not in body


def test_entry_page_referentie_inhoud_wint_van_opmerking(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="voldoet",
            betekenis_lage_landen="Werkte hier.",
            referenties=[
                {
                    "label": "Lexikon",
                    "url": "https://example.org/lex",
                    "geraadpleegd": "2026-08-20",
                    "inhoud": "Lexikonvita over de Friese missie.",
                    "opmerking": "interne notitie niet tonen",
                }
            ],
        )
    )
    body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )[1]
    assert "## Verder lezen en kijken" in body
    assert "Lexikonvita over de Friese missie." in body
    assert "interne notitie niet tonen" not in body
    assert "geraadpleegd 2026-08-20" in body


def test_entry_page_selectie_na_verhaal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="nader-onderzoek",
            selectie_toelichting="Grensgeval.",
            betekenis_lage_landen="Indirecte rol.",
            verhaal="Korte vita.",
        )
    )
    body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )[1]
    assert body.index("## Betekenis voor de Lage Landen") < body.index("## Verhaal")
    assert body.index("## Verhaal") < body.index("## Verder lezen en kijken")
    assert body.index("## Verder lezen en kijken") < body.index("<details")


def test_entry_page_heilige_toont_geen_samenvatting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="voldoet",
            betekenis_lage_landen="Predikte onder de Friezen.",
            samenvatting="Angelsaksische missionaris. Feestdag 7 november.",
            verhaal="Korte vita.",
        )
    )
    body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )[1]
    assert "Predikte onder de Friezen." in body
    assert "Korte vita." in body
    assert "Angelsaksische missionaris" not in body


def test_entry_page_feestdag_link_en_geen_synaxarion_voet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(_heilige(selectie="voldoet"))
    meta, body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )
    assert meta["feestdatum"] == "11-07"
    assert meta["vierdatum_oud"] == "11-20"
    assert "**Feestdag:** [7 november](/datum/?dag=11-07)" in body
    assert "vierdatum-oud" in body
    assert "(20 nov)" in body
    assert "20 november oude kalender" not in body
    assert "Synaxarion:" not in body
    assert "/synaxarion/" not in body


def test_entry_page_andere_gedenkdagen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="voldoet",
            datum_extra_norm=[
                {
                    "feestdatum": "12-23",
                    "toelichting": "gedachtenis op de Orthodoxe kalender",
                }
            ],
        )
    )
    body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )[1]
    assert "**Feestdag:** [7 november](/datum/?dag=11-07)" in body
    assert "**Andere gedenkdagen:**" in body
    assert "[23 december](/datum/?dag=12-23)" in body
    assert "(5 jan)" in body
    assert "5 januari oude kalender" not in body
    assert "gedachtenis op de Orthodoxe kalender" in body
    assert "23 december —" not in body
    assert "extra-gedenkdag" in body
    assert "gedenkdagen_extra:" in (
        content / "heiligen" / "voorbeeld.md"
    ).read_text(encoding="utf-8")


def test_internal_links_in_verhaal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    catalog = [
        _heilige(
            id="willibrord",
            namen={"primair": "Willibrord", "alternatief": []},
            selectie="voldoet",
        ),
        _heilige(
            id="bonifatius",
            namen={"primair": "Bonifatius", "alternatief": ["Bonifacius"]},
            selectie="voldoet",
            verhaal="Hij werkte met Willibrord en stierf bij Dokkum.",
        ),
    ]
    write_entry_page(catalog[1], catalog)
    body = _split_hugo_markdown(
        (content / "heiligen" / "bonifatius.md").read_text(encoding="utf-8")
    )[1]
    assert "[Willibrord](/heiligen/willibrord/)" in body
    assert "[Bonifatius](/heiligen/bonifatius/)" not in body


def test_referenties_genummerd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="voldoet",
            over_bronnen="Volgens [1] predikte hij in Gent.",
            referenties=[
                {
                    "label": "Wikipedia (NL) — Voorbeeld",
                    "url": "https://nl.wikipedia.org/wiki/Voorbeeld",
                    "inhoud": "Overzicht.",
                }
            ],
        )
    )
    body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )[1]
    assert "[1] [Wikipedia (NL) — Voorbeeld]" in body
    assert "Volgens [1] predikte hij in Gent." in body


def test_andere_gedenkdagen_zonder_dubbele_datum_in_toelichting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="voldoet",
            datum_extra_norm=[
                {"feestdatum": "08-21", "toelichting": "21 augustus"},
                {
                    "feestdatum": "11-08",
                    "toelichting": "8 november (met alle heilige bisschoppen van Utrecht)",
                },
                {
                    "feestdatum": "11-14",
                    "toelichting": "14 november (gangbare gedenkdag)",
                },
            ],
        )
    )
    body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )[1]
    assert "[21 augustus](/datum/?dag=08-21)" in body
    assert "— 21 augustus" not in body
    assert "(met alle heilige bisschoppen van Utrecht)" in body
    assert "— 8 november (met" not in body
    assert "(gangbare gedenkdag)" in body
    assert "— 14 november (gangbare" not in body


def test_entry_page_over_bronnen_toelichting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="voldoet",
            over_bronnen="De vita van X is de hoofdbron.",
        )
    )
    body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )[1]
    assert "## Over de bronnen" in body
    assert "De vita van X is de hoofdbron." in body
    assert body.index("De vita van X is de hoofdbron.") < body.index("**Bron:**")


def test_entry_page_nagekeken_bronzin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            bronlaag="nagekeken",
            betekenis_lage_landen="Predikte onder de Friezen.",
            verhaal="Een vita.",
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    assert "nagekeken aan een lexikon" in text
    assert "open naslagwerken" not in text
    assert "Deze pagina is nog een stub" not in text


def test_entry_page_icoon_alleen_bij_rechten_ok(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            icoon={
                "bestand": "iconen/willibrord.jpg",
                "rechten": "ok",
                "bron": "Wikimedia Commons",
                "licentie": "Publiek domein",
            }
        )
    )
    meta, _body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )
    assert meta["icoon"] == "/iconen/willibrord.jpg"
    assert meta["icoon_bron"] == "Wikimedia Commons"
    assert meta["icoon_licentie"] == "Publiek domein"
    write_entry_page(
        _heilige(
            id="zonder",
            icoon={"bestand": "iconen/x.jpg", "rechten": "onbekend"},
        )
    )
    meta2, _ = _split_hugo_markdown(
        (content / "heiligen" / "zonder.md").read_text(encoding="utf-8")
    )
    assert "icoon" not in meta2


def test_entry_page_iconen_lijst_primair_en_extra(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            iconen=[
                {
                    "bestand": "iconen/odulphus-hemelum.jpg",
                    "rechten": "ok",
                    "primair": True,
                    "bron": "Klooster Hemelum",
                    "licentie": "Toestemming van het klooster",
                    "toelichting": "Icoon in het klooster.",
                    "soort": "foto",
                },
                {
                    "bestand": "iconen/odulphus.jpg",
                    "rechten": "ok",
                    "bron": "Wikimedia Commons",
                    "licentie": "Publiek domein",
                    "soort": "reproductie",
                },
            ]
        )
    )
    meta, _body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )
    assert meta["icoon"] == "/iconen/odulphus-hemelum.jpg"
    assert meta["icoon_bron"] == "Klooster Hemelum"
    assert meta["icoon_toelichting"] == "Icoon in het klooster."
    assert meta["iconen"][0]["bestand"] == "/iconen/odulphus.jpg"
    assert meta["iconen"][0]["soort"] == "reproductie"
    assert "icoon" in meta


def test_entries_json_heeft_betekenis_alleen_bij_heiligen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    static = tmp_path / "static" / "data"
    monkeypatch.setattr("generate.STATIC_DATA", static)
    heilige = _heilige(
        betekenis_lage_landen="Voor de Lage Landen.",
        locaties=["utrecht"],
        rustplaats={"plaats": "echternach", "toelichting": "Abdij"},
    )
    feest = {
        **_heilige(id="kerst", soort="feest"),
        "namen": {"primair": "Kerst", "alternatief": []},
        "source_path": "data/feesten/kerst.yaml",
        "observances": ["feest"],
        "betekenis_lage_landen": "",
        "betekenis": "Wat dit feest zegt.",
    }
    write_entries_json([heilige, feest])
    payload = json.loads((static / "entries.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in payload}
    assert by_id["voorbeeld"]["betekenis_lage_landen"] == "Voor de Lage Landen."
    assert "betekenis_lage_landen" not in by_id["kerst"]
    assert "betekenis" not in by_id["kerst"]
    assert "betekenis" not in by_id["kerst"]
    assert "selectie" in by_id["voorbeeld"]
    assert by_id["voorbeeld"]["selectie"] == "nader-onderzoek"
    assert "voorbeeld" in by_id
    assert by_id["voorbeeld"]["bronlaag"] == "encyclopedie"
    assert by_id["voorbeeld"]["locaties"] == ["utrecht"]
    assert by_id["voorbeeld"]["rustplaats"]["plaats"] == "echternach"
    assert "locaties" not in by_id["kerst"]


def test_entries_json_heeft_kandidaat_met_selectie(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    static = tmp_path / "static" / "data"
    monkeypatch.setattr("generate.STATIC_DATA", static)
    schrijf = _heilige(id="schrijf", selectie="kandidaat-schrappen")
    schrijf["namen"] = {"primair": "Schrijf", "alternatief": []}
    schrijf["source_path"] = "data/heiligen/schrijf.yaml"
    blijf = _heilige(id="blijf", selectie="voldoet")
    blijf["namen"] = {"primair": "Blijf", "alternatief": []}
    blijf["source_path"] = "data/heiligen/blijf.yaml"
    write_entries_json([schrijf, blijf])
    payload = json.loads((static / "entries.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in payload}
    assert by_id["schrijf"]["selectie"] == "kandidaat-schrappen"
    assert by_id["blijf"]["selectie"] == "voldoet"


def test_synaxarion_json_alleen_vaste_cyclus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    static = tmp_path / "static" / "data"
    monkeypatch.setattr("generate.STATIC_DATA", static)
    vast = _heilige(id="blijf", selectie="voldoet")
    vast["namen"] = {"primair": "Blijf", "alternatief": []}
    pascha = {
        **_heilige(id="pascha", soort="feest", cyclus="paascyclus"),
        "namen": {"primair": "Pascha", "alternatief": []},
        "source_path": "data/feesten/pascha.yaml",
        "observances": ["feest"],
        "datum_norm": {
            "vorm": "dag",
            "paascyclus_offset": 0,
            "stijl": "gregoriaans",
        },
    }
    write_entries_json([vast, pascha])
    data = json.loads((static / "synaxarion.json").read_text(encoding="utf-8"))
    namen = [
        item["naam"]
        for maand in data["maanden"]
        for dag in maand["dagen"]
        for item in dag["items"]
    ]
    assert "Blijf" in namen
    assert "Pascha" not in namen
    nov = next(m for m in data["maanden"] if m["key"] == "11")
    assert any(d["mmdd"] == "11-07" for d in nov["dagen"])


def test_beheer_selectie_groepeert_en_toont_toelichting() -> None:
    body = render_beheer_selectie(
        [
            _heilige(
                id="willibrord",
                namen={"primair": "Willibrord", "alternatief": []},
                selectie="voldoet",
                source_path="data/heiligen/willibrord.yaml",
            ),
            _heilige(
                id="fridolin",
                namen={"primair": "Fridolin", "alternatief": []},
                selectie="kandidaat-schrappen",
                selectie_toelichting="Vooral Boven-Rijn.",
                source_path="data/heiligen/fridolin.yaml",
            ),
            _heilige(
                id="bavo",
                namen={"primair": "Bavo", "alternatief": []},
                source_path="data/heiligen/bavo.yaml",
            ),
        ]
    )
    assert "## Voldoet (1)" in body
    assert "[Willibrord](/heiligen/willibrord/)" in body
    assert "## Nader onderzoek (1)" in body
    assert "[Bavo](/heiligen/bavo/)" in body
    assert "## Kandidaat om te schrappen (1)" in body
    assert "Vooral Boven-Rijn." in body


def test_write_beheer_selectie_naar_beheer_map(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_beheer_selectie(load_entries())
    path = content / "beheer" / "selectie.md"
    meta, body = _split_hugo_markdown(path.read_text(encoding="utf-8"))
    assert meta["title"] == "Selectie heiligen"
    assert meta["generator"] == "scripts/generate.py"
    assert "Willibrord" in body
    assert "Nader onderzoek" in body
    assert "lubuinus.yaml" not in body
    assert "alberik.yaml" not in body
    assert "lebuinus.yaml" in body
    assert "albericus-van-utrecht.yaml" in body
    heiligen = [e for e in load_entries() if e["soort"] == "heilige"]
    n_voldoet = sum(1 for e in heiligen if e["selectie"] == "voldoet")
    n_nader = sum(1 for e in heiligen if e["selectie"] == "nader-onderzoek")
    n_kand = sum(1 for e in heiligen if e["selectie"] == "kandidaat-schrappen")
    assert f"## Voldoet ({n_voldoet})" in body
    assert f"## Nader onderzoek ({n_nader})" in body
    assert f"## Kandidaat om te schrappen ({n_kand})" in body
    assert "Rath Melsigi" in body


def test_heiligen_list_layout_zoekt_alternatieve_namen() -> None:
    layout = (ROOT / "site" / "layouts" / "partials" / "heiligen-overzicht.html").read_text(
        encoding="utf-8"
    )
    listing = (ROOT / "site" / "layouts" / "heiligen" / "list.html").read_text(
        encoding="utf-8"
    )
    assert 'partial "heiligen-overzicht.html"' in listing
    assert "heiligen-zoek" in layout
    assert "alternatief" in layout
    assert "entry-filter.js" in layout
    assert "heiligen-kaart" in layout
    assert "locatie_zoek" in layout
    assert "vendor/leaflet/leaflet.js" in layout
    assert "heiligen-data" in layout
    assert "data-heiligen-sort" in layout
    assert "data-heiligen-selectie" in layout
    assert "data-heiligen-weergave" in layout
    js = (ROOT / "site" / "assets" / "js" / "entry-filter.js").read_text(
        encoding="utf-8"
    )
    assert "zoekHay" in js
    assert "siteUrl" in js
    assert "toLocaleLowerCase" in js
    assert 'params.get("plaats")' in js
    assert "heiligen-filter" in js
    assert 'sortMode === "datum"' in js
    assert 'sortMode === "plaats"' in js
    assert 'selectieMode === "kalender"' in js
    assert 'weergaveMode === "kaart"' in js
    assert "prevMonth !== mm" in js
    assert "heiligen-toon" in (
        ROOT / "site" / "layouts" / "partials" / "heiligen-overzicht.html"
    ).read_text(encoding="utf-8")
    cal = (ROOT / "site" / "assets" / "js" / "calendar.js").read_text(
        encoding="utf-8"
    )
    assert 'kind === "heiligen-toon"' in cal
    assert 'kind === "heiligen-weergave"' in cal
    assert 'kind === "heiligen-sorteren"' in cal
    kaart = (ROOT / "site" / "assets" / "js" / "heiligen-kaart.js").read_text(
        encoding="utf-8"
    )
    assert "plaatsen.json" in kaart
    assert "tile.openstreetmap.org" in kaart
    assert "unpkg.com" not in kaart


def test_betekenis_lage_landen_zonder_selectietokens() -> None:
    tokens = ("kandidaat-schrappen", "nader-onderzoek", "selectiegrens")
    for entry in load_entries():
        if entry.get("soort") != "heilige":
            continue
        text = entry.get("betekenis_lage_landen") or ""
        for tok in tokens:
            assert tok not in text, f"{entry['id']}: {tok}"


def _feest(**overrides):
    entry = _heilige(
        id="theofanie",
        soort="feest",
        lage_landen=False,
        source_path="data/feesten/theofanie.yaml",
        observances=["feest"],
        betekenis_lage_landen="",
        selectie="",
    )
    entry["namen"] = {
        "primair": "Theofanie (Doop des Heren)",
        "alternatief": [],
    }
    entry["datum_norm"] = {
        "feestdatum": "01-06",
        "vorm": "dag",
        "stijl": "juliaans",
    }
    entry.update(overrides)
    return entry


def test_komende_jaren_is_vijf_vanaf_huidig(monkeypatch: pytest.MonkeyPatch) -> None:
    class FrozenDate(date):
        @classmethod
        def today(cls) -> date:
            return date(2026, 8, 21)

    monkeypatch.setattr("generate.date", FrozenDate)
    assert KOMENDE_JAREN_AANTAL == 5
    assert list(komende_jaren()) == [2026, 2027, 2028, 2029, 2030]
    occ = list(occurrence_years())
    assert occ[0] == 2026 - ICS_YEAR_BACK
    assert occ[-1] == 2026 + ICS_YEAR_FORWARD
    assert len(occ) == ICS_YEAR_BACK + ICS_YEAR_FORWARD + 1
    assert occ != list(komende_jaren())


def test_paascyclus_feest_komende_jaren_tabel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    monkeypatch.setattr("generate.komende_jaren", lambda today=None: range(2026, 2031))
    write_entry_page(
        _feest(
            id="pinksteren",
            cyclus="paascyclus",
            datum_norm={
                "feestdatum": None,
                "vorm": "dag",
                "stijl": "gregoriaans",
                "paascyclus_offset": 49,
            },
        )
    )
    text = (content / "feesten" / "pinksteren.md").read_text(encoding="utf-8")
    _, body = _split_hugo_markdown(text)
    assert 'class="komende-jaren"' in body
    assert "<th>Jaar</th>" in body
    assert "<th>Datum</th>" in body
    assert "<th>Wereldlijk</th>" not in body
    assert "<th>Juliaans</th>" not in body
    assert "<td>2026</td>" in body
    assert "<td>2030</td>" in body
    assert "<td>2024</td>" not in body
    assert "<td>2031</td>" not in body
    assert "- 2026:" not in body
    assert "31 mei" in body
    assert 'href="/datum/?datum=2026-05-31&amp;stijl=gregoriaans"' in body or (
        'href="/datum/?datum=2026-05-31&stijl=gregoriaans"' in body
    )
    assert "18 mei" not in body
    assert "komende-jaren-note" not in body
    assert body.count("<tr>") == 6  # kop + 5 jaren


def test_paascyclus_periode_komende_jaren_tabel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    monkeypatch.setattr("generate.komende_jaren", lambda today=None: range(2026, 2031))
    write_entry_page(
        _feest(
            id="grote-vasten",
            soort="vasten",
            cyclus="paascyclus",
            observances=["vasten"],
            datum_norm={
                "feestdatum": None,
                "vorm": "periode",
                "stijl": "gregoriaans",
                "paascyclus_offset": -48,
                "van_offset_dagen": -48,
                "tot_offset_dagen": -8,
            },
        )
    )
    text = (content / "vasten" / "grote-vasten.md").read_text(encoding="utf-8")
    _, body = _split_hugo_markdown(text)
    assert "<th>Van</th>" in body
    assert "<th>Tot</th>" in body
    assert "<td>2026</td>" in body
    assert "<td>2031</td>" not in body
    assert "komende-jaren-note" not in body
    assert "oude kalender" not in body


def test_apostelvasten_tot_heeft_oude_kalender_haakjes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    monkeypatch.setattr("generate.komende_jaren", lambda today=None: range(2026, 2031))
    write_entry_page(
        _feest(
            id="apostolisch-vasten",
            soort="vasten",
            cyclus="paascyclus",
            observances=["vasten"],
            datum_norm={
                "feestdatum": None,
                "vorm": "periode_hybride",
                "stijl": "gregoriaans",
                "van_offset_dagen": 57,
                "tot_mmdd": "06-28",
            },
        )
    )
    text = (content / "vasten" / "apostolisch-vasten.md").read_text(encoding="utf-8")
    meta, body = _split_hugo_markdown(text)
    assert meta["tot"] == "06-28"
    assert meta["tot_oud"] == "07-11"
    assert "28 juni" in body
    assert "(11 jul)" in body
    assert "11 juli oude kalender" not in body
    assert "vierdatum-oud" in body
    assert "komende-jaren-note" not in body
    assert "Tussen haakjes" not in body
    assert "<th>Juliaans</th>" not in body
    assert body.count('data-info-tip="vierdatum-oud"') == 5


def test_weekdag_relatief_tabel_burgerlijk_nieuw_en_oud(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    monkeypatch.setattr("generate.komende_jaren", lambda today=None: range(2026, 2031))
    write_entry_page(
        _feest(
            id="zondag-vaderen-voor-kerst",
            cyclus="jaar",
            datum_norm={
                "feestdatum": None,
                "vorm": "weekdag_relatief",
                "stijl": "gregoriaans",
                "anker": "12-25",
                "weekdag": 7,
                "welke": 1,
                "richting": "voor",
            },
        )
    )
    text = (content / "feesten" / "zondag-vaderen-voor-kerst.md").read_text(
        encoding="utf-8"
    )
    _, body = _split_hugo_markdown(text)
    assert "<th>Datum</th>" in body
    assert "<th>Juliaans</th>" not in body
    assert "20 december" in body
    assert "(3 jan 2027)" in body
    assert "3 januari 2027 oude kalender" not in body
    assert "vierdatum-oud" in body
    assert "Tussen haakjes" not in body
    assert "komende-jaren-note" not in body


def test_vaste_vastenperiode_heeft_van_oud_tot_oud(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _feest(
            id="ontslapen-vasten",
            soort="vasten",
            cyclus="jaar",
            observances=["vasten"],
            datum_norm={
                "feestdatum": None,
                "vorm": "periode",
                "stijl": "gregoriaans",
                "van": "08-01",
                "tot": "08-14",
            },
        )
    )
    text = (content / "vasten" / "ontslapen-vasten.md").read_text(encoding="utf-8")
    meta, body = _split_hugo_markdown(text)
    assert meta["van"] == "08-01"
    assert meta["tot"] == "08-14"
    assert meta["van_oud"] == "08-14"
    assert meta["tot_oud"] == "08-27"
    assert "**Komende jaren" not in body


def test_feest_pagina_betekenis_na_verhaal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _feest(
            samenvatting="Openbaring van de Heilige Drie-eenheid.",
            verhaal="Bij de doop in de Jordaan.",
            betekenis="In de doop deelt de mens in ditzelfde geheim.",
            referenties=[
                {
                    "label": "OrthodoxWiki — Theofanie",
                    "url": "https://orthodoxwiki.org/Theophany",
                },
                {
                    "label": "OCA — Het Orthodoxe geloof: Theofanie",
                    "url": "https://www.oca.org/orthodoxy/the-orthodox-faith/worship/the-church-year/epiphany",
                },
            ],
        )
    )
    text = (content / "feesten" / "theofanie.md").read_text(encoding="utf-8")
    _, body = _split_hugo_markdown(text)
    assert 'data-info-tip="betekenis-goedkeuring"' in body
    assert "data-betekenis-bronnen=" in body
    start = body.index("data-betekenis-bronnen=")
    end = body.index("title=", start)
    attr = body[start:end]
    assert "Het Orthodoxe geloof: Theofanie" in attr
    assert "OrthodoxWiki" not in attr
    assert "Betekenis" in body
    assert "In de doop deelt de mens in ditzelfde geheim." in body
    assert "## Betekenis voor de Lage Landen" not in body
    assert body.index("## Verhaal") < body.index("betekenis-goedkeuring")
    assert body.index("betekenis-goedkeuring") < body.index(
        "## Verder lezen en kijken"
    )
    write_entry_page(_feest(id="transfiguratie", betekenis=""))
    text2 = (content / "feesten" / "transfiguratie.md").read_text(encoding="utf-8")
    _, body2 = _split_hugo_markdown(text2)
    assert "betekenis-goedkeuring" not in body2


def test_feest_betekenis_kop_heeft_goedkeuring_in_attr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _feest(
            betekenis="In de doop deelt de mens in ditzelfde geheim.",
            goedkeuring=[
                {
                    "naam": "A. N.",
                    "organisatie": "parochie X",
                    "datum": "2026-08-21",
                    "opmerking": "Akkoord.",
                }
            ],
        )
    )
    text = (content / "feesten" / "theofanie.md").read_text(encoding="utf-8")
    _, body = _split_hugo_markdown(text)
    assert 'data-info-tip="betekenis-goedkeuring"' in body
    assert "A. N." in body
    assert "parochie X" in body
    assert "Akkoord." in body


def test_betekenis_bron_labels_kiest_orthodoxe_geloof() -> None:
    labels = betekenis_bron_labels(
        {
            "referenties": [
                {"label": "OrthodoxWiki — X", "url": "https://orthodoxwiki.org/X"},
                {
                    "label": "OCA — Het Orthodoxe geloof: X",
                    "url": "https://www.oca.org/orthodoxy/the-orthodox-faith/x",
                },
            ]
        }
    )
    assert labels == ["OCA — Het Orthodoxe geloof: X"]
    fallback = betekenis_bron_labels(
        {"referenties": [{"label": "OrthodoxWiki — X"}]}
    )
    assert fallback == ["OrthodoxWiki — X"]


def test_grootfeesten_en_pascha_hebben_betekenis() -> None:
    expected = {
        "geboorte-moeder-gods",
        "kruisverheffing",
        "tempelgang-moeder-gods",
        "kerst",
        "theofanie",
        "ontmoeting-in-de-tempel",
        "aankondiging",
        "palmzondag",
        "pascha",
        "hemelvaart",
        "pinksteren",
        "transfiguratie",
        "ontslapen-moeder-gods",
        "lazarus-zaterdag",
        "grote-maandag",
        "grote-dinsdag",
        "grote-woensdag",
        "grote-donderdag",
        "grote-vrijdag",
        "grote-zaterdag",
        "allerheiligen-zondag",
        "zondag-heiligen-lage-landen",
        "geestesmaandag",
        "pokrov",
        "petrus-en-paulus",
        "geboorte-johannes-doper",
        "onthoofding-johannes-doper",
        "besnijdenis-des-heren",
        "begin-kerkelijk-jaar",
        "zacheus-zondag",
        "zondag-tollenaar-en-farizeeer",
        "zondag-verloren-zoon",
        "zondag-laatste-oordeel",
        "vergevingszondag",
        "schone-maandag",
        "zondag-orthodoxie",
        "zondag-gregorius-palamas",
        "zondag-kruisverering",
        "zondag-johannes-klimacus",
        "zondag-maria-van-egypte",
        "thomaszondag",
        "zondag-myrondraagsters",
        "zondag-verlamde",
        "zondag-samaritaanse",
        "zondag-blinde",
        "midden-pinksterfeest",
        "zondag-vaderen-eerste-concilie",
        "zondag-vaderen-zevende-concilie",
        "zondag-voorvaderen",
        "zondag-vaderen-voor-kerst",
        "zaterdag-allerzielen-vleesmijding",
        "allerzielen-zaterdag-pinksteren",
    }
    feesten = [e for e in load_entries() if e.get("soort") == "feest"]
    met = {e["id"] for e in feesten if (e.get("betekenis") or "").strip()}
    assert met == expected
    by_id = {e["id"]: e for e in feesten}
    assert "Jordaan" in by_id["theofanie"]["betekenis"]
    assert "doop" in by_id["theofanie"]["betekenis"].lower()
    for sid in expected:
        text = by_id[sid]["betekenis"]
        paras = [p for p in text.split("\n\n") if p.strip()]
        assert 1 <= len(paras) <= 3, sid
        assert by_id[sid].get("referenties"), sid


def test_write_plaatsen_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    static = tmp_path / "static" / "data"
    monkeypatch.setattr("generate.STATIC_DATA", static)
    write_plaatsen_json()
    payload = json.loads((static / "plaatsen.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in payload}
    assert by_id["utrecht"]["naam"] == "Utrecht"
    assert by_id["vlaanderen"]["soort"] == "streek"
    assert "lat" in by_id["utrecht"] and "lon" in by_id["utrecht"]
