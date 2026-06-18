"""Scrape per-nationality counts for every university (resumable)."""
from __future__ import annotations

import json
import os
import time

from pipeline.scrape_nationality import scrape_school, make_session

PLAN = "pipeline/data/scrape_plan.json"
CACHE = "pipeline/data/nationality_cache.json"


def main():
    plan = json.load(open(PLAN, encoding="utf-8"))["byid"]
    cache = {}
    if os.path.exists(CACHE):
        cache = json.load(open(CACHE, encoding="utf-8"))
    todo = [sid for sid in plan if sid not in cache]
    print(f"{len(plan)} schools, {len(todo)} to scrape", flush=True)
    s = make_session()
    for i, sid in enumerate(todo, 1):
        info = plan[sid]
        try:
            totals = scrape_school(s, sid, expected_total=info["expected_total"])
            got = sum(totals.values())
            flag = "" if got == info["expected_total"] else f" !=exp({info['expected_total']})"
            cache[sid] = {"rep_name": info["rep_name"], "countries": totals,
                          "scraped_total": got, "expected_total": info["expected_total"]}
            print(f"[{i}/{len(todo)}] {info['rep_name']}: {len(totals)} countries, {got}{flag}", flush=True)
        except Exception as exc:  # noqa: BLE001
            cache[sid] = {"rep_name": info["rep_name"], "countries": {}, "error": repr(exc)}
            print(f"[{i}/{len(todo)}] {info['rep_name']}: ERROR {exc!r}", flush=True)
        if i % 10 == 0:
            json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        time.sleep(0.3)
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    mism = [v["rep_name"] for v in cache.values() if v.get("scraped_total") != v.get("expected_total") and "error" not in v]
    print(f"\nDONE. {len(cache)} cached. total mismatches: {len(mism)}", flush=True)
    if mism:
        print("mismatches:", mism[:30], flush=True)


if __name__ == "__main__":
    main()
