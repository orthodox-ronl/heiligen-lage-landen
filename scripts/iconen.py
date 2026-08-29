"""Normaliseer icoon / iconen op een entry."""

from __future__ import annotations

from typing import Any


def icoon_bestand(item: dict[str, Any] | None) -> str:
    """Pad relatief t.o.v. site/static/, zonder leading slash."""
    if not item:
        return ""
    return str(item.get("bestand") or "").strip().replace("\\", "/").lstrip("/")


def iconen_van(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Lijst van icoon-objecten. `iconen` wint van enkelvoud `icoon`."""
    raw = entry.get("iconen")
    if isinstance(raw, list) and raw:
        return [dict(item) for item in raw if isinstance(item, dict)]
    icoon = entry.get("icoon")
    if isinstance(icoon, dict) and icoon_bestand(icoon):
        return [dict(icoon)]
    return []


def zichtbare_iconen(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Items met lokaal bestand en rechten: ok (wat de site mag tonen)."""
    return [
        item
        for item in iconen_van(entry)
        if icoon_bestand(item) and str(item.get("rechten") or "") == "ok"
    ]


def primair_icoon(entry: dict[str, Any]) -> dict[str, Any] | None:
    """Hoofdicoon voor infobox, lijsten en entries.json."""
    items = zichtbare_iconen(entry)
    if not items:
        return None
    marked = [item for item in items if item.get("primair") is True]
    return marked[0] if marked else items[0]


def extra_iconen(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Zichtbare iconen die niet het primaire bestand zijn."""
    prim = primair_icoon(entry)
    prim_pad = icoon_bestand(prim)
    return [
        item for item in zichtbare_iconen(entry) if icoon_bestand(item) != prim_pad
    ]
