"""Assemble web/muslim_universities.json from the nationality scrape + geocode cache."""
from __future__ import annotations

import json

from pipeline.geocode import _load_json
from pipeline.build_muslim_json import build_muslim_records

NATIONALITY_CACHE = "pipeline/data/nationality_cache.json"
GEOCODE_CACHE = "pipeline/data/geocode_cache.json"
OVERRIDES = "pipeline/data/geocode_overrides.json"
OUTPUT = "web/muslim_universities.json"


def main() -> None:
    scraped = _load_json(NATIONALITY_CACHE)
    located = {**_load_json(GEOCODE_CACHE), **_load_json(OVERRIDES)}

    records = build_muslim_records(scraped, located)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    total = sum(r["total_muslim"] for r in records)
    print(f"Wrote {len(records)} universities with Muslim-country students "
          f"({total:,} students) to {OUTPUT}")
    if records:
        top = records[0]
        print(f"Top: {top['name_ko']} — {top['total_muslim']} "
              f"({', '.join(c['country'] for c in top['by_country'][:5])}…)")


if __name__ == "__main__":
    main()
