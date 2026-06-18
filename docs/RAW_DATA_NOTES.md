# Raw Data Notes

- Source: data.go.kr dataset 15050054 (KEDI foreign students by university) →
  served via academyinfo.go.kr (대학알리미) UbiReport viewer, item_id **33**
  ("바-1. 외국학생 현황" / Foreign Student Status, universities).
- **Conclusion: this source does NOT expose a per-university × per-nationality
  breakdown.** See "Decoded schema (PROVEN)" below. The map's original
  per-nationality vision cannot be built from this source.

---

## Access mechanism (resolved)

The data.go.kr dataset is link-out (`atchFileTyCode: DATD01`); the real data is
the academyinfo UbiReport viewer:

```
https://www.academyinfo.go.kr/uipnh/unt/unmcom/RdViewer.do
  ?paramSvyYr=2025&paramItemId=33&paramSchlDivCd=02&paramFormClftCd=30
  &paramItemDivCd=01&paramDiv=A&paramSchlKindCd=99&paramSchlEstabCd=99&paramZoneCd=99
```

**Key discovery:** the RdViewer HTML response **embeds the entire report inline**
as zlib-compressed JS string literals — no separate binary-server call needed:

- `resultMaster` — report metadata (`row_num=3, col_num=32`)
- `resultHeader` — column header cells (labels, merges)
- `resultBody`   — body column definitions (`b_col_id`, `b_col_cd`, `b_col_hid_yn`)
- `strQuery`     — the actual Oracle SQL executed server-side
- `resultSum`    — totals (≈empty here)

### Decoding (working tool: `pipeline/decode_ubi.py`)

Each byte of the zlib stream is encoded in the HTML as `\\uXXXX` (note: backslashes
are **doubled** at the JS-source level — collapse `\\\\`→`\\` first), plus short
escapes for some bytes. Verified short-escape byte map:

| escape | byte | escape | byte |
|--------|------|--------|------|
| `\t`   | 0x09 | `\f`   | 0x0C |
| `\n`   | 0x0A | `\\`   | 0x5C |
| `\r`   | 0x0D | `\ ` (backslash-space) | 0x20 |
| `\e`   | 0x00 | `\b` `\v` | 0x08 0x0B |

After reconstruction → `zlib.decompress` (validates via Adler32). **Decoded report
text is UTF-8** (not EUC-KR, despite Korean content). Verified end-to-end against a
live fetch (HTTP 200).

---

## Decoded schema (PROVEN)

Item 33, `form_clft_cd=30`, universities (`schlDivCd=02`). One row **per school**
(SQL: `GROUP BY C.SCHL_ID, D.COL_5_VAL`). Column headers (decoded):

```
기준연도(year) | 학교종류(type) | 설립구분(estab) | 지역(region) | 상태(status) | 학교(school) |
국가(country, HIDDEN — see below) | 계(total D=A+B+C) |
학위과정(degree) → 소계(A) / 인문사회·자연과학·공학·예체능·의학 계열 (by academic FIELD) |
교육과정 공동운영생(B) | 연수과정 → 소계(C) / 어학연수생·교환학생·방문학생·기타 연수생 |
언어능력 → 계(E) / TOPIK4급↑ / 영어트랙 TOEFL IBT59↑ / 영어권 외국인유학생 |
언어능력충족 학생비율(%) | 기숙사 수용 여부(수용/미수용) | 최종수정일
```

Body columns (32): `APY_YR, SCHL_KND_CD, ESTB_DIV_CD, ZN_CD, SCHL_LST_STTS_CD,
SCHL_NM,` then numeric `COL_*_VAL` (program/field/language counts), `HSTR_CRTN_DTM`.

### CRITICAL: no nationality dimension is exposed

- The breakdown is by **academic field** (인문사회/자연과학/공학/예체능/의학) and
  **program type** (degree / language-training / exchange / visiting / other) and
  **language ability** (TOPIK/TOEFL) — **not by country**.
- A `국가` (country) header **does** exist at col 6, but it maps to body
  `col_no=6, id=COL_2_VAL, hidden=Y` — a **hidden** template column that the SQL
  never selects and never groups by. It is an unpopulated form-builder artifact.
- Form-variant probe (`pipeline/_probe_forms.py`) over `form_clft_cd` ∈
  {30, 10, 20, 50}: **none** groups by country, **none** selects `COL_2_VAL`,
  **none** joins a nationality code table. Forms {31, 32, 40} do not exist
  (server error pages).

---

## Where per-nationality data DOES live (national-level only)

- **법무부 (MOJ)** dataset `15100039`: monthly foreign students by nationality/region —
  **national totals, no per-university**.
- KEDI 교육통계(KESS) / studyinkorea.go.kr publish nationality aggregates — also
  **national-level**, not per-university.

No public Korean source found that gives per-university × per-nationality counts.

---

## Implication for the project

Task 4+ of the plan (parse per-university per-country → map with nationality hover
cards) is **not achievable** from this data. A pivot is required (e.g. national
by-nationality view, or per-university totals + national nationality split).
Pending product decision.
