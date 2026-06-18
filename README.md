# Foreign Students at Korean Universities — Map

Interactive map of South Korean universities by number of foreign students
(2025), with a per-university breakdown by academic field, program type, and
language ability. Data: KEDI / 대학알리미 disclosure item 33 ("외국학생 현황").

> **Scope note:** The project originally aimed to map students *by nationality*.
> That proved impossible — no public Korean source provides per-university ×
> per-nationality counts (the disclosure breaks foreign students down by program
> type / academic field / language only; nationality data exists at the national
> level only). See `docs/RAW_DATA_NOTES.md` for the full investigation. The map
> therefore shows **total foreign students per university** with the available
> breakdown.

## Data acquisition

The source data is served through academyinfo.go.kr's proprietary UbiReport
viewer; anonymous HTTP scraping only returns the first page. The complete
dataset is therefore obtained by a **one-time manual download**:

1. Open https://www.academyinfo.go.kr/popup/main0810/list.do
2. Select **"바-1. 외국학생 현황"** (item 33), 조사연도 **2025**, 학교구분 **대학**,
   output **학교별** (by school).
3. Download the ZIP, extract the XLSX to
   `pipeline/data/raw/foreign_students.xlsx`.

(`pipeline/decode_ubi.py` + `pipeline/ubi_client.py` can decode/scrape the
viewer directly, but only page 1 per query — see RAW_DATA_NOTES.md.)

## Pipeline

1. `pip install -r requirements.txt`
2. Place the XLSX at `pipeline/data/raw/foreign_students.xlsx` (see above).
3. `python -m pipeline.main` → geocodes universities and writes
   `web/universities.json`.

Geocoding uses OpenStreetMap Nominatim with a local cache
(`pipeline/data/geocode_cache.json`) and manual overrides
(`pipeline/data/geocode_overrides.json`). Of 226 universities, fully **online
"cyber" universities** (6) are excluded as they have no physical campus to map.

## Website

Open `web/index.html` in a browser, or serve statically:
`python -m http.server 8000 --directory web` → http://localhost:8000/

Markers are sized by total foreign students; hover (desktop) or tap (mobile)
shows the per-university breakdown. The search box jumps to a university.

## Tests

`pytest` from the repo root.
