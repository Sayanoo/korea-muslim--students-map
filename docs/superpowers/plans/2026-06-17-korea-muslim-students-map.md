# Korea University Muslim-Student Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static website with an interactive map of South Korea where each marker is a university hosting students from majority-Muslim countries, and hovering/tapping shows the per-nationality counts.

**Architecture:** A re-runnable Python pipeline acquires official foreign-student data, filters it to majority-Muslim nationalities, attaches university coordinates, and emits a single `web/universities.json`. A purely static Leaflet website reads that JSON — no backend.

**Tech Stack:** Python 3.11+ (pandas, openpyxl, requests, pytest), Leaflet + Leaflet.markercluster, OpenStreetMap tiles, vanilla JS/CSS.

## Global Constraints

- Source data: data.go.kr KEDI "Foreign Student Status by University" XLSX (primary); academyinfo.go.kr per-university disclosure (scrape fallback).
- Muslim country definition: population **>50% Muslim** (~46 countries). List is editable in one place.
- Map scope: only universities with **≥1** student from a majority-Muslim country.
- Interaction: card on **hover (desktop) and tap (mobile)**.
- UI language: **English**; university names shown in Korean + English.
- Delivery: **static, local-first**; no build step for the frontend.
- Output schema (`web/universities.json`): array of
  `{ name_ko, name_en, lat, lon, total_muslim, by_country: [{country, count}] }`,
  `by_country` sorted descending by `count`, zero-student universities excluded.
- All Python tests run with `pytest` from the repo root.

---

### Task 1: Project scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `pipeline/__init__.py` (empty)
- Create: `tests/__init__.py` (empty)
- Create: `pipeline/data/.gitkeep` (empty)
- Create: `.gitignore`
- Create: `README.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the package layout (`pipeline/`, `tests/`) and dependency list all later tasks rely on.

- [ ] **Step 1: Create `requirements.txt`**

```
pandas==2.2.2
openpyxl==3.1.5
requests==2.32.3
pytest==8.2.0
```

- [ ] **Step 2: Create `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
pipeline/data/raw/
```

- [ ] **Step 3: Create empty package files**

Create `pipeline/__init__.py`, `tests/__init__.py`, and `pipeline/data/.gitkeep` as empty files.

- [ ] **Step 4: Create `README.md`**

```markdown
# Korea University Muslim-Student Map

Interactive map of South Korean universities hosting students from
majority-Muslim countries.

## Pipeline
1. `pip install -r requirements.txt`
2. `python -m pipeline.main` → writes `web/universities.json`

## Website
Open `web/index.html` in a browser (or serve `web/` statically).
```

- [ ] **Step 5: Install and verify**

Run: `pip install -r requirements.txt && python -c "import pandas, openpyxl, requests, pytest; print('ok')"`
Expected: prints `ok`

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .gitignore README.md pipeline/ tests/
git commit -m "chore: project scaffolding"
```

---

### Task 2: Muslim country list + name normalization

**Files:**
- Create: `pipeline/muslim_countries.py`
- Test: `tests/test_muslim_countries.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `MUSLIM_KO_TO_EN: dict[str, str]` — Korean country name → canonical English name, containing only majority-Muslim countries.
  - `normalize_country(raw: str) -> str | None` — strips/normalizes a raw country string (Korean or English) and returns the canonical English name if it is a majority-Muslim country, else `None`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_muslim_countries.py
from pipeline.muslim_countries import normalize_country, MUSLIM_KO_TO_EN

def test_known_korean_names_map_to_english():
    assert normalize_country("우즈베키스탄") == "Uzbekistan"
    assert normalize_country("인도네시아") == "Indonesia"
    assert normalize_country("파키스탄") == "Pakistan"

def test_whitespace_is_stripped():
    assert normalize_country("  이집트 ") == "Egypt"

def test_english_input_is_accepted():
    assert normalize_country("Turkey") == "Turkey"
    assert normalize_country("Türkiye") == "Turkey"

def test_non_muslim_country_returns_none():
    assert normalize_country("중국") is None      # China
    assert normalize_country("베트남") is None     # Vietnam
    assert normalize_country("") is None

def test_list_is_majority_muslim_sized():
    assert 40 <= len(set(MUSLIM_KO_TO_EN.values())) <= 50
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_muslim_countries.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.muslim_countries'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/muslim_countries.py
"""Majority-Muslim (>50% Muslim population) country list and name normalization."""

# Korean country name -> canonical English name. Majority-Muslim countries only.
MUSLIM_KO_TO_EN: dict[str, str] = {
    "아프가니스탄": "Afghanistan",
    "알바니아": "Albania",
    "알제리": "Algeria",
    "아제르바이잔": "Azerbaijan",
    "바레인": "Bahrain",
    "방글라데시": "Bangladesh",
    "브루나이": "Brunei",
    "부르키나파소": "Burkina Faso",
    "차드": "Chad",
    "코모로": "Comoros",
    "지부티": "Djibouti",
    "이집트": "Egypt",
    "감비아": "Gambia",
    "기니": "Guinea",
    "인도네시아": "Indonesia",
    "이란": "Iran",
    "이라크": "Iraq",
    "요르단": "Jordan",
    "카자흐스탄": "Kazakhstan",
    "코소보": "Kosovo",
    "쿠웨이트": "Kuwait",
    "키르기스스탄": "Kyrgyzstan",
    "키르기스공화국": "Kyrgyzstan",
    "레바논": "Lebanon",
    "리비아": "Libya",
    "말레이시아": "Malaysia",
    "몰디브": "Maldives",
    "말리": "Mali",
    "모리타니": "Mauritania",
    "모로코": "Morocco",
    "니제르": "Niger",
    "오만": "Oman",
    "파키스탄": "Pakistan",
    "팔레스타인": "Palestine",
    "카타르": "Qatar",
    "사우디아라비아": "Saudi Arabia",
    "세네갈": "Senegal",
    "시에라리온": "Sierra Leone",
    "소말리아": "Somalia",
    "수단": "Sudan",
    "시리아": "Syria",
    "타지키스탄": "Tajikistan",
    "튀니지": "Tunisia",
    "튀르키예": "Turkey",
    "터키": "Turkey",
    "투르크메니스탄": "Turkmenistan",
    "아랍에미리트": "United Arab Emirates",
    "우즈베키스탄": "Uzbekistan",
    "예멘": "Yemen",
}

# English aliases -> canonical English name (for English-language sources).
_EN_ALIASES: dict[str, str] = {name.lower(): name for name in MUSLIM_KO_TO_EN.values()}
_EN_ALIASES["türkiye"] = "Turkey"
_EN_ALIASES["turkiye"] = "Turkey"
_EN_ALIASES["uae"] = "United Arab Emirates"


def normalize_country(raw: str) -> str | None:
    """Return canonical English name if `raw` is a majority-Muslim country, else None."""
    if raw is None:
        return None
    key = raw.strip()
    if not key:
        return None
    if key in MUSLIM_KO_TO_EN:
        return MUSLIM_KO_TO_EN[key]
    return _EN_ALIASES.get(key.lower())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_muslim_countries.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add pipeline/muslim_countries.py tests/test_muslim_countries.py
git commit -m "feat: majority-Muslim country list and name normalization"
```

---

### Task 3: Data source discovery (download + document schema)

This is a discovery task. Its deliverable is the downloaded raw file plus a
documented column mapping that Task 4 consumes. No production code logic beyond
the download helper.

**Files:**
- Create: `pipeline/fetch_data.py`
- Create: `docs/RAW_DATA_NOTES.md`
- Test: `tests/test_fetch_data.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `download_bulk_xlsx(dest_dir: str) -> str` — downloads the KEDI XLSX to `dest_dir`, returns the saved file path.
  - `docs/RAW_DATA_NOTES.md` documenting: the exact sheet name, the column header for university name, and the columns/shape that carry per-country counts (wide vs. long). Task 4 reads these notes.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_fetch_data.py
import os
from pipeline.fetch_data import download_bulk_xlsx

def test_download_writes_file(tmp_path, monkeypatch):
    # Stub the network call so the test is offline and deterministic.
    import pipeline.fetch_data as fd
    def fake_get(url, timeout):
        class R:
            status_code = 200
            content = b"PK\x03\x04fake-xlsx-bytes"
            def raise_for_status(self): pass
        return R()
    monkeypatch.setattr(fd.requests, "get", fake_get)
    path = download_bulk_xlsx(str(tmp_path))
    assert os.path.exists(path)
    assert path.endswith(".xlsx")
    assert os.path.getsize(path) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_fetch_data.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.fetch_data'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/fetch_data.py
"""Acquire raw foreign-student data from official Korean sources."""
import os
import requests

# data.go.kr file dataset detail page for KEDI "Foreign Student Status by University".
# The direct download URL is resolved during Task 3 discovery and pasted here.
BULK_XLSX_URL = "https://www.data.go.kr/download/15050054/fileData.do"


def download_bulk_xlsx(dest_dir: str) -> str:
    """Download the KEDI bulk XLSX into dest_dir and return the saved path."""
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, "foreign_students.xlsx")
    resp = requests.get(BULK_XLSX_URL, timeout=60)
    resp.raise_for_status()
    with open(path, "wb") as f:
        f.write(resp.content)
    return path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_fetch_data.py -v`
Expected: PASS

- [ ] **Step 5: Perform real discovery**

Run the real download and inspect it (one-off, not a committed script):

```bash
python -c "from pipeline.fetch_data import download_bulk_xlsx; print(download_bulk_xlsx('pipeline/data/raw'))"
python -c "import pandas as pd; xl=pd.ExcelFile('pipeline/data/raw/foreign_students.xlsx'); print(xl.sheet_names); df=xl.parse(xl.sheet_names[0]); print(list(df.columns)); print(df.head(3).to_dict('records'))"
```

If the real direct-download URL differs from `BULK_XLSX_URL`, fix the constant.
If the bulk file has **no per-country breakdown**, stop and switch to the scrape
fallback (see Task 3b note below) before continuing.

- [ ] **Step 6: Document findings in `docs/RAW_DATA_NOTES.md`**

Record verbatim: the chosen sheet name, the university-name column header, and
how per-country counts are represented. Use this template and fill the bracketed
values with what you observed:

```markdown
# Raw Data Notes

- Source: data.go.kr dataset 15050054 (KEDI foreign students by university)
- File: pipeline/data/raw/foreign_students.xlsx
- Sheet used: [exact sheet name]
- University name column: [exact header]
- Country representation: [WIDE: one column per country, headers are country names]
  OR [LONG: a "country" column + a "count" column, headers: [names]]
- Header row index (0-based): [n]
- Notes / quirks: [merged cells, totals rows to skip, etc.]
```

> **Task 3b (only if bulk file lacks per-country data):** add
> `scrape_university(name) -> list[dict]` to `pipeline/fetch_data.py` using
> `requests` against the academyinfo.go.kr disclosure endpoint for item "외국인
> 유학생 현황", with retry/back-off, and document its output shape in
> `RAW_DATA_NOTES.md` using the same field names Task 4 expects. The rest of the
> plan is unchanged because Task 4 consumes the documented shape, not the source.

- [ ] **Step 7: Commit**

```bash
git add pipeline/fetch_data.py tests/test_fetch_data.py docs/RAW_DATA_NOTES.md
git commit -m "feat: bulk data download + documented raw schema"
```

---

### Task 4: Parse raw data into per-university Muslim-country records

**Files:**
- Create: `pipeline/parse_records.py`
- Test: `tests/test_parse_records.py`

**Interfaces:**
- Consumes: `normalize_country` (Task 2); the column mapping documented in `docs/RAW_DATA_NOTES.md` (Task 3).
- Produces:
  - `parse_muslim_records(df: "pandas.DataFrame") -> dict[str, dict[str, int]]` — maps Korean university name → `{english_country_name: count}`, including only majority-Muslim countries with count > 0. The function accepts an already-loaded DataFrame so it is testable without files.

This task assumes the **WIDE** layout (one column per country). If Task 3 found
LONG layout, swap the inner loop for a `groupby` over the country/count columns;
the function signature and return type stay identical.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_parse_records.py
import pandas as pd
from pipeline.parse_records import parse_muslim_records

def test_keeps_only_muslim_countries_with_positive_counts():
    df = pd.DataFrame([
        {"학교명": "테스트대학교", "우즈베키스탄": 12, "중국": 300, "이집트": 0, "파키스탄": 5},
        {"학교명": "빈대학교",   "우즈베키스탄": 0,  "중국": 50,  "이집트": 0, "파키스탄": 0},
    ])
    result = parse_muslim_records(df, name_col="학교명")
    assert result["테스트대학교"] == {"Uzbekistan": 12, "Pakistan": 5}
    assert "중국" not in str(result)            # non-Muslim dropped
    assert "빈대학교" not in result              # no qualifying students -> excluded

def test_non_numeric_counts_treated_as_zero():
    df = pd.DataFrame([{"학교명": "테스트대학교", "이란": "-", "이라크": 3}])
    result = parse_muslim_records(df, name_col="학교명")
    assert result["테스트대학교"] == {"Iraq": 3}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_parse_records.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.parse_records'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/parse_records.py
"""Turn the raw foreign-student DataFrame into per-university Muslim-country counts."""
import pandas as pd
from pipeline.muslim_countries import normalize_country


def _to_int(value) -> int:
    try:
        n = int(float(value))
    except (TypeError, ValueError):
        return 0
    return n if n > 0 else 0


def parse_muslim_records(df: pd.DataFrame, name_col: str) -> dict[str, dict[str, int]]:
    """Return {university_name_ko: {english_country: count>0}} for Muslim countries."""
    out: dict[str, dict[str, int]] = {}
    country_cols = [c for c in df.columns if c != name_col and normalize_country(str(c))]
    for _, row in df.iterrows():
        name = str(row[name_col]).strip()
        if not name or name.lower() == "nan":
            continue
        counts: dict[str, int] = {}
        for col in country_cols:
            n = _to_int(row[col])
            if n > 0:
                counts[normalize_country(str(col))] = counts.get(normalize_country(str(col)), 0) + n
        if counts:
            out[name] = counts
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_parse_records.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add pipeline/parse_records.py tests/test_parse_records.py
git commit -m "feat: parse raw data into per-university Muslim-country counts"
```

---

### Task 5: Geocoding with cache and manual overrides

**Files:**
- Create: `pipeline/geocode.py`
- Create: `pipeline/data/geocode_overrides.json` (initially `{}`)
- Test: `tests/test_geocode.py`

**Interfaces:**
- Consumes: nothing (network call is injected/stubbed in tests).
- Produces:
  - `resolve_coords(names: list[str], cache_path: str, overrides_path: str, geocoder=...) -> tuple[dict[str, dict], list[str]]` — returns `(located, unlocated)` where `located` maps university name → `{"lat": float, "lon": float}` and `unlocated` is the list of names that could not be resolved. Results are read from / written to `cache_path`; `overrides_path` values win over everything.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_geocode.py
import json
from pipeline.geocode import resolve_coords

def test_overrides_win_and_cache_is_written(tmp_path):
    cache = tmp_path / "cache.json"
    overrides = tmp_path / "ov.json"
    overrides.write_text(json.dumps({"override대학교": {"lat": 1.0, "lon": 2.0}}), encoding="utf-8")

    calls = []
    def fake_geocoder(name):
        calls.append(name)
        return {"geo대학교": {"lat": 37.5, "lon": 127.0}}.get(name)

    located, unlocated = resolve_coords(
        ["override대학교", "geo대학교", "없는대학교"],
        str(cache), str(overrides), geocoder=fake_geocoder,
    )
    assert located["override대학교"] == {"lat": 1.0, "lon": 2.0}
    assert located["geo대학교"] == {"lat": 37.5, "lon": 127.0}
    assert unlocated == ["없는대학교"]
    assert "override대학교" not in calls            # override skips geocoder
    assert json.loads(cache.read_text(encoding="utf-8"))["geo대학교"]["lat"] == 37.5

def test_cache_prevents_second_geocoder_call(tmp_path):
    cache = tmp_path / "cache.json"
    cache.write_text(json.dumps({"x대학교": {"lat": 5.0, "lon": 6.0}}), encoding="utf-8")
    def boom(name):
        raise AssertionError("should not be called")
    located, unlocated = resolve_coords(["x대학교"], str(cache), str(tmp_path/"ov.json"), geocoder=boom)
    assert located["x대학교"] == {"lat": 5.0, "lon": 6.0}
    assert unlocated == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_geocode.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.geocode'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/geocode.py
"""Resolve university coordinates with a cache and manual overrides."""
import json
import os
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


def nominatim_geocoder(name: str) -> dict | None:
    """Geocode a Korean university name via OpenStreetMap Nominatim. Returns {lat,lon} or None."""
    resp = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": f"{name}, South Korea", "format": "json", "limit": 1},
        headers={"User-Agent": "korea-muslim-students-map/1.0"},
        timeout=30,
    )
    resp.raise_for_status()
    results = resp.json()
    time.sleep(1)  # Nominatim usage policy: max 1 req/sec
    if not results:
        return None
    return {"lat": float(results[0]["lat"]), "lon": float(results[0]["lon"])}


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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_geocode.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Create the empty overrides file**

Create `pipeline/data/geocode_overrides.json` with content `{}`.

- [ ] **Step 6: Commit**

```bash
git add pipeline/geocode.py pipeline/data/geocode_overrides.json tests/test_geocode.py
git commit -m "feat: geocoding with cache and manual overrides"
```

---

### Task 6: Assemble universities.json

**Files:**
- Create: `pipeline/build_json.py`
- Test: `tests/test_build_json.py`

**Interfaces:**
- Consumes: records from `parse_muslim_records` (Task 4) and `located` from `resolve_coords` (Task 5).
- Produces:
  - `build_records(muslim_by_uni: dict[str, dict[str, int]], located: dict[str, dict], name_en_map: dict[str, str]) -> list[dict]` — returns the final list matching the output schema, sorted by `total_muslim` descending, `by_country` sorted by `count` descending, universities without coordinates excluded.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_build_json.py
from pipeline.build_json import build_records

def test_builds_sorted_schema_and_drops_unlocated():
    muslim_by_uni = {
        "가대학교": {"Uzbekistan": 10, "Pakistan": 40},
        "나대학교": {"Egypt": 3},
        "위치없음대학교": {"Iran": 99},
    }
    located = {
        "가대학교": {"lat": 37.5, "lon": 127.0},
        "나대학교": {"lat": 35.1, "lon": 129.0},
    }
    name_en_map = {"가대학교": "Ga University", "나대학교": "Na University"}
    out = build_records(muslim_by_uni, located, name_en_map)

    assert [r["name_ko"] for r in out] == ["가대학교", "나대학교"]  # 50 > 3, unlocated dropped
    assert out[0]["total_muslim"] == 50
    assert out[0]["name_en"] == "Ga University"
    assert out[0]["lat"] == 37.5 and out[0]["lon"] == 127.0
    assert out[0]["by_country"] == [
        {"country": "Pakistan", "count": 40},
        {"country": "Uzbekistan", "count": 10},
    ]

def test_missing_english_name_falls_back_to_korean():
    out = build_records({"마대학교": {"Iran": 2}}, {"마대학교": {"lat": 1.0, "lon": 2.0}}, {})
    assert out[0]["name_en"] == "마대학교"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_build_json.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.build_json'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/build_json.py
"""Assemble the final universities.json record list."""


def build_records(muslim_by_uni, located, name_en_map):
    """Return the final sorted list of university records (see output schema)."""
    records = []
    for name_ko, counts in muslim_by_uni.items():
        if name_ko not in located:
            continue
        by_country = [
            {"country": c, "count": n}
            for c, n in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
        ]
        records.append({
            "name_ko": name_ko,
            "name_en": name_en_map.get(name_ko, name_ko),
            "lat": located[name_ko]["lat"],
            "lon": located[name_ko]["lon"],
            "total_muslim": sum(counts.values()),
            "by_country": by_country,
        })
    records.sort(key=lambda r: r["total_muslim"], reverse=True)
    return records
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_build_json.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add pipeline/build_json.py tests/test_build_json.py
git commit -m "feat: assemble final universities.json record list"
```

---

### Task 7: Pipeline entry point

**Files:**
- Create: `pipeline/main.py`
- Create: `web/.gitkeep` (empty, so `web/` exists before the frontend tasks)

**Interfaces:**
- Consumes: `download_bulk_xlsx` (Task 3), `parse_muslim_records` (Task 4), `resolve_coords` (Task 5), `build_records` (Task 6).
- Produces: `web/universities.json` on disk; prints a summary including the count of unlocated universities.

This task wires existing, already-tested units together, so it is verified by a
real run rather than a new unit test. Fill `NAME_COL`, sheet selection, and the
optional English-name column from `docs/RAW_DATA_NOTES.md`.

- [ ] **Step 1: Write the entry point**

```python
# pipeline/main.py
"""Run the full pipeline: download -> parse -> geocode -> write web/universities.json."""
import json
import os
import pandas as pd

from pipeline.fetch_data import download_bulk_xlsx
from pipeline.parse_records import parse_muslim_records
from pipeline.geocode import resolve_coords
from pipeline.build_json import build_records

RAW_DIR = "pipeline/data/raw"
CACHE_PATH = "pipeline/data/geocode_cache.json"
OVERRIDES_PATH = "pipeline/data/geocode_overrides.json"
OUTPUT_PATH = "web/universities.json"

# Filled in from docs/RAW_DATA_NOTES.md (Task 3):
SHEET_NAME = 0          # index or exact sheet name
HEADER_ROW = 0          # 0-based header row
NAME_COL = "학교명"      # Korean university-name column header
NAME_EN_COL = None      # English-name column header if the source provides one, else None


def main() -> None:
    xlsx_path = download_bulk_xlsx(RAW_DIR)
    df = pd.read_excel(xlsx_path, sheet_name=SHEET_NAME, header=HEADER_ROW)

    muslim_by_uni = parse_muslim_records(df, name_col=NAME_COL)

    name_en_map = {}
    if NAME_EN_COL and NAME_EN_COL in df.columns:
        for _, row in df.iterrows():
            name_en_map[str(row[NAME_COL]).strip()] = str(row[NAME_EN_COL]).strip()

    located, unlocated = resolve_coords(
        list(muslim_by_uni.keys()), CACHE_PATH, OVERRIDES_PATH,
    )

    records = build_records(muslim_by_uni, located, name_en_map)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(records)} universities to {OUTPUT_PATH}")
    if unlocated:
        print(f"{len(unlocated)} universities had no coordinates "
              f"(add them to {OVERRIDES_PATH}): {unlocated}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create `web/.gitkeep`** (empty file)

- [ ] **Step 3: Run the full pipeline**

Run: `python -m pipeline.main`
Expected: prints `Wrote N universities to web/universities.json` (N > 0), and `web/universities.json` exists. Add any unlocated universities to `geocode_overrides.json` and re-run until the unlocated list is acceptable.

- [ ] **Step 4: Sanity-check the output**

Run: `python -c "import json; d=json.load(open('web/universities.json',encoding='utf-8')); print(len(d)); print(d[0]['name_ko'], d[0]['total_muslim'], d[0]['by_country'][:3])"`
Expected: a positive count and a plausible top university with a descending `by_country` list.

- [ ] **Step 5: Commit**

```bash
git add pipeline/main.py web/.gitkeep web/universities.json pipeline/data/geocode_cache.json pipeline/data/geocode_overrides.json
git commit -m "feat: pipeline entry point producing universities.json"
```

---

### Task 8: Static map website

**Files:**
- Create: `web/index.html`
- Create: `web/style.css`
- Create: `web/app.js`

**Interfaces:**
- Consumes: `web/universities.json` (Task 7).
- Produces: the deliverable website. Verified by loading in a browser (manual), since it is presentation code with no pure logic to unit-test.

- [ ] **Step 1: Create `web/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Korea Universities — Muslim-Country Students</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <header>
    <h1>Muslim-Country Students at Korean Universities</h1>
    <input id="search" type="search" placeholder="Search a university…" autocomplete="off" />
  </header>
  <div id="map"></div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
  <script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create `web/style.css`**

```css
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; font-family: system-ui, sans-serif; }
body { display: flex; flex-direction: column; }
header { padding: 10px 16px; background: #0b3d2e; color: #fff; display: flex;
         gap: 16px; align-items: center; flex-wrap: wrap; }
header h1 { font-size: 18px; margin: 0; }
#search { padding: 6px 10px; border-radius: 6px; border: 1px solid #ccc; min-width: 220px; }
#map { flex: 1; }
.uni-card { font-size: 13px; line-height: 1.4; }
.uni-card h3 { margin: 0 0 2px; font-size: 14px; }
.uni-card .sub { color: #555; margin: 0 0 6px; }
.uni-card table { border-collapse: collapse; }
.uni-card td { padding: 1px 8px 1px 0; }
.uni-card td.n { text-align: right; font-variant-numeric: tabular-nums; }
```

- [ ] **Step 3: Create `web/app.js`**

```js
const map = L.map("map").setView([36.5, 127.8], 7);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

const cluster = L.markerClusterGroup();
const byName = new Map();

function radius(total) {
  return Math.max(6, Math.min(28, 5 + Math.sqrt(total) * 2));
}

function cardHtml(u) {
  const rows = u.by_country
    .map((c) => `<tr><td>${c.country}</td><td class="n">${c.count}</td></tr>`)
    .join("");
  return `<div class="uni-card">
      <h3>${u.name_en}</h3>
      <p class="sub">${u.name_ko} · ${u.total_muslim} students</p>
      <table>${rows}</table>
    </div>`;
}

fetch("universities.json")
  .then((r) => r.json())
  .then((data) => {
    data.forEach((u) => {
      const m = L.circleMarker([u.lat, u.lon], {
        radius: radius(u.total_muslim),
        color: "#0b3d2e",
        fillColor: "#1a9e6e",
        fillOpacity: 0.75,
        weight: 1,
      });
      m.bindPopup(cardHtml(u));            // tap (mobile) + click
      m.on("mouseover", () => m.openPopup());  // hover (desktop)
      byName.set(u.name_en.toLowerCase() + " " + u.name_ko, { marker: m, u });
      cluster.addLayer(m);
    });
    map.addLayer(cluster);
  });

document.getElementById("search").addEventListener("input", (e) => {
  const q = e.target.value.trim().toLowerCase();
  if (!q) return;
  for (const [key, { marker, u }] of byName) {
    if (key.includes(q)) {
      map.setView([u.lat, u.lon], 13);
      cluster.zoomToShowLayer(marker, () => marker.openPopup());
      break;
    }
  }
});
```

- [ ] **Step 4: Verify in a browser**

Run: `python -m http.server 8000 --directory web` then open `http://localhost:8000/`.
Expected: a map of South Korea with green markers; hovering a marker (desktop) or tapping (mobile) shows the university card with a ranked nationality table; typing in the search box zooms to a matching university and opens its card.

- [ ] **Step 5: Commit**

```bash
git add web/index.html web/style.css web/app.js
git commit -m "feat: static Leaflet map website with hover/tap cards and search"
```

---

## Notes for the executor

- Tasks 1–6 are pure TDD and fully offline (network calls are stubbed in tests).
- Task 3 includes a real download + manual schema documentation step; Tasks 4 and 7
  depend on those documented values (`SHEET_NAME`, `HEADER_ROW`, `NAME_COL`,
  layout WIDE vs LONG).
- Task 7 and Task 8 are verified by real runs, not unit tests.
- If the bulk file lacks per-country data, do Task 3b before Task 4; the rest of
  the plan is unaffected because Task 4 consumes the documented record shape.
