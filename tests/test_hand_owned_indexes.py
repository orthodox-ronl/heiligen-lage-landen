"""Tests voor handmatig beheerde Hugo-_index.md-bestanden."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate import (  # noqa: E402
    CONTENT,
    _dump_hugo_markdown,
    _split_hugo_markdown,
    ensure_achtergrond_topics,
    ensure_hand_owned_indexes,
    write_generated_indexes,
)


def test_split_and_dump_preserves_body_and_extra_front_matter() -> None:
    text = (
        '---\n'
        'title: "Agenda (ICS)"\n'
        "layout: agenda\n"
        "draft: false\n"
        "---\n\n"
        "Mijn eigen intro.\n"
    )
    meta, body = _split_hugo_markdown(text)
    assert meta["title"] == "Agenda (ICS)"
    assert meta["layout"] == "agenda"
    assert meta["draft"] is False
    assert body.strip() == "Mijn eigen intro."
    roundtrip = _dump_hugo_markdown(meta, body)
    meta2, body2 = _split_hugo_markdown(roundtrip)
    assert meta2 == meta
    assert body2.strip() == "Mijn eigen intro."


def test_ensure_hand_owned_indexes_keeps_body(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    (content / "kalender").mkdir(parents=True)
    (content / "synaxarion").mkdir(parents=True)
    (content / "datum").mkdir(parents=True)
    (content / "agenda").mkdir(parents=True)
    (content / "uitleg").mkdir(parents=True)

    kalender = content / "kalender" / "_index.md"
    kalender.write_text(
        '---\ntitle: "Mijn kalender"\nlayout: verkeerd\n---\n\nBlijf staan.\n',
        encoding="utf-8",
    )
    (content / "_index.md").write_text(
        '---\ntitle: "Home"\n---\n\n<!-- welcome -->\n',
        encoding="utf-8",
    )
    (content / "synaxarion" / "_index.md").write_text(
        '---\ntitle: "Synaxarion"\nlayout: synaxarion\n---\n\n',
        encoding="utf-8",
    )
    (content / "datum" / "_index.md").write_text(
        '---\ntitle: "Datum"\nlayout: datum\n---\n\n',
        encoding="utf-8",
    )
    (content / "agenda" / "_index.md").write_text(
        '---\ntitle: "Agenda (ICS)"\nlayout: agenda\n---\n\nx\n',
        encoding="utf-8",
    )
    uitleg = content / "uitleg" / "_index.md"
    uitleg.write_text(
        '---\ntitle: "Uitleg"\nlayout: uitleg\n---\n\ny\n',
        encoding="utf-8",
    )

    monkeypatch.setattr("generate.CONTENT", content)
    ensure_hand_owned_indexes()

    meta, body = _split_hugo_markdown(kalender.read_text(encoding="utf-8"))
    assert meta["title"] == "Mijn kalender"
    assert meta["layout"] == "kalender"
    assert "Blijf staan." in body

    umeta, ubody = _split_hugo_markdown(uitleg.read_text(encoding="utf-8"))
    assert "layout" not in umeta
    assert ubody.strip() == "y"


def test_ensure_rejects_empty_title(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    content.mkdir()
    (content / "_index.md").write_text('---\ntitle: ""\n---\n\n', encoding="utf-8")
    (content / "kalender").mkdir()
    (content / "kalender" / "_index.md").write_text(
        '---\ntitle: "K"\nlayout: kalender\n---\n\n', encoding="utf-8"
    )
    (content / "synaxarion").mkdir()
    (content / "synaxarion" / "_index.md").write_text(
        '---\ntitle: "M"\nlayout: synaxarion\n---\n\n', encoding="utf-8"
    )
    (content / "datum").mkdir()
    (content / "datum" / "_index.md").write_text(
        '---\ntitle: "D"\nlayout: datum\n---\n\n', encoding="utf-8"
    )
    (content / "agenda").mkdir()
    (content / "agenda" / "_index.md").write_text(
        '---\ntitle: "Agenda"\nlayout: agenda\n---\n\n', encoding="utf-8"
    )
    (content / "uitleg").mkdir()
    (content / "uitleg" / "_index.md").write_text(
        '---\ntitle: "U"\n---\n\n', encoding="utf-8"
    )

    monkeypatch.setattr("generate.CONTENT", content)
    with pytest.raises(SystemExit):
        ensure_hand_owned_indexes()


def test_ensure_achtergrond_topics_creates_stub(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    (content / "uitleg").mkdir(parents=True)
    monkeypatch.setattr("generate.CONTENT", content)
    monkeypatch.setattr(
        "generate.SPEC_PATH",
        Path(__file__).resolve().parents[1] / "docs" / "specs" / "lezingen.md",
    )
    ensure_achtergrond_topics()
    path = content / "uitleg" / "nieuw-oud.md"
    assert path.is_file()
    meta, body = _split_hugo_markdown(path.read_text(encoding="utf-8"))
    assert "Nieuw" in meta["title"]
    assert "toe te voegen" in body
    clerus = content / "uitleg" / "lezingen.md"
    tech = content / "uitleg" / "lezingen-technisch.md"
    assert clerus.is_file()
    assert tech.is_file()
    tech_meta, _ = _split_hugo_markdown(tech.read_text(encoding="utf-8"))
    assert tech_meta.get("build", {}).get("list") == "never"


def test_repo_hand_owned_indexes_ok() -> None:
    """Live content/ moet de checks doorstaan."""
    ensure_hand_owned_indexes()
    ensure_achtergrond_topics()
    assert (CONTENT / "kalender" / "_index.md").is_file()
    assert (CONTENT / "synaxarion" / "_index.md").is_file()
    assert (CONTENT / "datum" / "_index.md").is_file()
    assert (CONTENT / "uitleg" / "nieuw-oud.md").is_file()
    assert (CONTENT / "beheer" / "_index.md").is_file()


def test_write_generated_heiligen_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_generated_indexes(
        [
            {
                "id": "willibrord",
                "soort": "heilige",
                "namen": {"primair": "Willibrord"},
            },
            {
                "id": "servatius",
                "soort": "heilige",
                "namen": {"primair": "Servatius"},
            },
            {
                "id": "kerstfeest",
                "soort": "feest",
                "namen": {"primair": "Kerstfeest"},
            },
        ]
    )
    text = (content / "heiligen" / "_index.md").read_text(encoding="utf-8")
    assert 'title: "Heiligen van de Lage Landen"' in text
    assert "**2**" in text
    assert "Willibrord" in text
    assert "/heiligen/willibrord/" in text
    assert "Servatius" in text
    assert "Kerstfeest" not in text
    assert (content / "feesten" / "_index.md").is_file()
    assert (content / "vasten" / "_index.md").is_file()
