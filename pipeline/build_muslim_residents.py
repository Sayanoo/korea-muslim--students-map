"""Build web/muslim_residents_by_region.json: per-province registered foreigners
from Muslim-majority countries (+ Mongolia reference line), for the 4th map."""
from __future__ import annotations

import json

from pipeline.muslim_countries import normalize_country
from pipeline.parse_residents import load_province_counts_from_zip

ZIP_PATH = "pipeline/data/raw/stat_yearbook_2024.zip"
GEOJSON = "web/skorea_provinces.geojson"
OUTPUT = "web/muslim_residents_by_region.json"

_MONGOLIA_KO = "몽골"
# 2023/2024 provincial renames -> names used in the (2013) GeoJSON
_PROVINCE_ALIASES = {"강원특별자치도": "강원도", "전북특별자치도": "전라북도"}


def build_region_residents(province_counts: dict, geojson: dict) -> dict:
    """{geojson_code: {code,name,name_eng,total_muslim,by_country}} — Muslim
    countries sorted desc, Mongolia pinned last (extra) and excluded from total."""
    name_to_props = {f["properties"]["name"]: f["properties"] for f in geojson["features"]}
    out: dict[str, dict] = {}
    for prov, counts in province_counts.items():
        props = name_to_props.get(_PROVINCE_ALIASES.get(prov, prov))
        if not props:
            continue
        muslim: dict[str, int] = {}
        for country_ko, n in counts.items():
            en = normalize_country(country_ko)
            if en and n > 0:
                muslim[en] = muslim.get(en, 0) + n
        by_country = [{"country": c, "count": n}
                      for c, n in sorted(muslim.items(), key=lambda kv: kv[1], reverse=True)]
        mongolia = counts.get(_MONGOLIA_KO, 0)
        if mongolia > 0:
            by_country.append({"country": "Mongolia", "count": mongolia, "extra": True})
        out[props["code"]] = {
            "code": props["code"], "name": props["name"], "name_eng": props["name_eng"],
            "total_muslim": sum(muslim.values()), "by_country": by_country,
        }
    return out


def main() -> None:
    province_counts = load_province_counts_from_zip(ZIP_PATH)
    geojson = json.load(open(GEOJSON, encoding="utf-8"))
    out = build_region_residents(province_counts, geojson)
    json.dump(out, open(OUTPUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    total = sum(r["total_muslim"] for r in out.values())
    print(f"Wrote {len(out)} provinces ({total:,} Muslim-country residents) to {OUTPUT}")
    top = max(out.values(), key=lambda r: r["total_muslim"])
    print(f"Top: {top['name_eng']} — {top['total_muslim']:,} "
          f"({', '.join(c['country'] for c in top['by_country'][:4])}…)")


if __name__ == "__main__":
    main()
