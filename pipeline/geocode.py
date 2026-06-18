"""Resolve university coordinates with a cache and manual overrides."""
from __future__ import annotations

import json
import os
import re
import time

import requests


def _load_json(path: str) -> dict:
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def clean_name(name: str) -> str:
    """Normalize a name so branch/national-prefixed campuses geocode to the base."""
    name = re.sub(r"_(제\d+캠퍼스|분교|본교).*$", "", name)
    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"^국립", "", name)
    return name.strip()


def search_query(name: str, region: str | None = None) -> str:
    """Build the Nominatim query; region disambiguates multi-campus universities."""
    base = clean_name(name)
    if region:
        return f"{base}, {region}, South Korea"
    return f"{base}, South Korea"


def _lookup(query: str) -> dict | None:
    resp = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": query, "format": "json", "limit": 1, "countrycodes": "kr"},
        headers={"User-Agent": "korea-foreign-students-map/1.0"},
        timeout=30,
    )
    resp.raise_for_status()
    results = resp.json()
    time.sleep(1)  # Nominatim usage policy: max 1 req/sec
    if not results:
        return None
    return {"lat": float(results[0]["lat"]), "lon": float(results[0]["lon"])}


def nominatim_geocoder(name: str, region: str | None = None) -> dict | None:
    """Geocode a Korean university name. Region disambiguates multi-campus
    universities, but over-constrains some; fall back to a region-less query."""
    coords = _lookup(search_query(name, region))
    if coords is None and region:
        coords = _lookup(search_query(name, None))
    return coords


def resolve_coords(names, cache_path, overrides_path, geocoder=nominatim_geocoder):
    """Return (located, unlocated). Overrides > cache > geocoder. Cache is persisted."""
    cache = _load_json(cache_path)
    overrides = _load_json(overrides_path)
    located: dict[str, dict] = {}
    unlocated: list[str] = []
    for name in names:
        if name in overrides:
            located[name] = overrides[name]
            continue
        if name in cache:
            located[name] = cache[name]
            continue
        coords = geocoder(name)
        if coords:
            cache[name] = coords
            located[name] = coords
        else:
            unlocated.append(name)
    _save_json(cache_path, cache)
    return located, unlocated
