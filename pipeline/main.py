"""Run the pipeline: read XLSX -> parse -> geocode -> write web/universities.json."""
from __future__ import annotations

import json
import os

from pipeline.parse_universities import read_data_rows, parse_universities
from pipeline.geocode import resolve_coords, nominatim_geocoder
from pipeline.build_json import build_records

XLSX_PATH = "pipeline/data/raw/foreign_students.xlsx"
CACHE_PATH = "pipeline/data/geocode_cache.json"
OVERRIDES_PATH = "pipeline/data/geocode_overrides.json"
OUTPUT_PATH = "web/universities.json"


def main() -> None:
    universities = parse_universities(read_data_rows(XLSX_PATH))
    print(f"Parsed {len(universities)} universities "
          f"({sum(u['total'] for u in universities):,} foreign students).")

    region_by_name = {u["name_ko"]: u["region_ko"] for u in universities}

    def geocoder(name):
        return nominatim_geocoder(name, region_by_name.get(name))

    located, unlocated = resolve_coords(
        [u["name_ko"] for u in universities], CACHE_PATH, OVERRIDES_PATH,
        geocoder=geocoder)

    records = build_records(universities, located)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(records)} universities to {OUTPUT_PATH}")
    if unlocated:
        print(f"{len(unlocated)} could not be geocoded "
              f"(add to {OVERRIDES_PATH}): {unlocated}")


if __name__ == "__main__":
    main()
