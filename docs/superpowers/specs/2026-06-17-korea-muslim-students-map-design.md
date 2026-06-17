# Korea University Muslim-Student Map — Design

**Date:** 2026-06-17
**Status:** Approved (architecture)

## Goal

Build a website with an interactive map of South Korea. Each marker is a Korean
university that hosts at least one student from a majority-Muslim country.
Hovering (or tapping) a marker shows how many students from each majority-Muslim
nationality study there, ranked by count. Data is sourced from Korea's official
higher-education disclosure system (대학알리미 / academyinfo.go.kr) and the public
data portal (data.go.kr).

## Key decisions

- **Data freshness:** Source data updates only annually, so the site is fully
  **static** — a one-time pipeline produces a JSON file; the website just reads it.
  No backend.
- **Data source:** Prefer the single bulk XLSX on data.go.kr (KEDI "Foreign
  Student Status by University"). If it lacks a per-country breakdown, fall back to
  scraping the per-university "외국인 유학생 현황 (foreign students by country)"
  disclosure on academyinfo.go.kr.
- **Muslim country definition:** Countries whose population is **>50% Muslim**
  (~45 countries). Threshold is defensible and easy to maintain. List is editable.
- **Map scope:** Only universities with **≥1 student from a majority-Muslim
  country** get a marker. Universities with zero are excluded.
- **Interaction:** Card shown on **hover (desktop) and tap (mobile)**.
- **Delivery:** **Static, local-first** (open `index.html`). Deployable to GitHub
  Pages later.
- **UI language:** English. University names shown in both Korean and English.

## Architecture

Two clean, independent pieces.

### 1. Data pipeline (Python, re-runnable)

Produces a single `universities.json` consumed by the website.

Units:

- **`fetch_data`** — Acquire raw data.
  - Primary: download the data.go.kr KEDI XLSX; inspect columns for a per-country
    breakdown.
  - Fallback: scrape academyinfo.go.kr per-university disclosure (item "외국인
    유학생 현황"), which lists students by country.
- **`muslim_countries`** — The list of majority-Muslim countries (>50%) plus a
  normalization table mapping Korean country names → English / ISO codes. This is
  the highest bug-risk area and is unit-tested.
- **`geocode`** — Attach coordinates to each university by geocoding its address
  once. Results are **cached** to a file so reruns don't re-geocode. A manual
  **override file** supplies coordinates for any addresses that fail geocoding.
  Geocoding is the primary project risk.
- **`build_json`** — Filter foreign-student records to the Muslim-country list,
  join with coordinates, drop universities with zero qualifying students, and emit
  `universities.json`.

Output schema (`universities.json`):

```json
[
  {
    "name_ko": "한국외국어대학교",
    "name_en": "Hankuk University of Foreign Studies",
    "lat": 37.5972,
    "lon": 127.0589,
    "total_muslim": 312,
    "by_country": [
      { "country": "Uzbekistan", "count": 120 },
      { "country": "Indonesia", "count": 95 }
    ]
  }
]
```

(`by_country` is sorted descending by `count`.)

### 2. Static website (`index.html` + `app.js` + Leaflet)

- Map of South Korea via **Leaflet** with **OpenStreetMap tiles** (no API key).
- One **circle marker** per university, sized/colored by `total_muslim`.
- **Marker clustering** (Leaflet.markercluster) to handle dense Seoul.
- **Hover (desktop) / tap (mobile)** opens a card: university name (KO + EN),
  `total_muslim`, and the ranked `by_country` list with counts.
- A **search box** to locate and zoom to a university by name.
- UI text in English.

## Data flow

```
data.go.kr XLSX  ──┐
                   ├─> fetch_data ─> filter (muslim_countries)
academyinfo.go.kr ─┘                      │
   (fallback scrape)                       ├─> join geocode (+ overrides/cache)
                                           │
                                           └─> build_json ─> universities.json
                                                                    │
                                                          static site (Leaflet) renders
```

## Error handling

- **Missing coordinates:** logged and collected into an "unlocated" list; the
  university is omitted from the map but reported so it can be fixed via the
  override file.
- **Country-name mismatches:** handled by the normalization table; unmatched
  country names are logged so the table can be extended.
- **Source site blocking / failure (scrape fallback):** retry with back-off; allow
  a manually downloaded file to be dropped in as input.
- **Universities with zero qualifying students:** excluded from output.

## Testing

- **Unit tests:** the country filter and the Korean→English country-name mapping
  (highest bug risk).
- **Schema validation:** assert `universities.json` matches the expected shape.
- **Spot checks:** verify counts for a few known universities against the source.

## Out of scope (YAGNI)

- Live/real-time data or a backend server.
- Historical trends across years (single annual snapshot).
- Authentication, user accounts, or any write features.
- Non-Muslim-country nationalities.

## Tech stack

- **Pipeline:** Python (pandas/openpyxl for XLSX; requests/Playwright only if the
  scrape fallback is needed).
- **Frontend:** Leaflet + Leaflet.markercluster, OpenStreetMap tiles, vanilla JS.
  No build step.
