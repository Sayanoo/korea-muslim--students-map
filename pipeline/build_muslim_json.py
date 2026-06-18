"""Build web/muslim_universities.json: per-university Muslim-country student counts."""
from __future__ import annotations

from pipeline.muslim_countries import normalize_country
from pipeline.university_names_en import to_english

# Mongolia is not a Muslim-majority country; shown as a reference line pinned to the
# bottom of each university's list (map 2 only), and excluded from totals.
_MONGOLIA_KO = "몽골"


def build_muslim_records(scraped: dict, located: dict) -> list[dict]:
    """For each school, keep only majority-Muslim countries (>=1 student) and
    attach coordinates. Universities with no Muslim students or no coordinates
    are dropped. Sorted by total Muslim students descending."""
    records = []
    for info in scraped.values():
        name = info.get("rep_name")
        counts: dict[str, int] = {}
        for country_ko, n in info.get("countries", {}).items():
            en = normalize_country(country_ko)
            if en and n > 0:
                counts[en] = counts.get(en, 0) + n
        if not counts:
            continue
        coords = located.get(name)
        if not coords:
            continue
        by_country = [{"country": c, "count": n}
                      for c, n in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)]
        mongolia = info.get("countries", {}).get(_MONGOLIA_KO, 0)
        if mongolia > 0:
            by_country.append({"country": "Mongolia", "count": mongolia, "extra": True})
        records.append({
            "name_ko": name,
            "name_en": to_english(name),
            "lat": coords["lat"],
            "lon": coords["lon"],
            "total_muslim": sum(counts.values()),
            "by_country": by_country,
        })
    records.sort(key=lambda r: r["total_muslim"], reverse=True)
    return records
