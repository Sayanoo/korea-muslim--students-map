"""Assemble the final web/universities.json record list."""
from __future__ import annotations

from pipeline.university_names_en import to_english


def build_records(universities: list[dict], located: dict[str, dict]) -> list[dict]:
    """Attach coordinates + English name, drop universities without coords, sort by total desc."""
    records = []
    for u in universities:
        coords = located.get(u["name_ko"])
        if not coords:
            continue
        records.append({**u, "name_en": to_english(u["name_ko"]),
                        "lat": coords["lat"], "lon": coords["lon"]})
    records.sort(key=lambda r: r["total"], reverse=True)
    return records
