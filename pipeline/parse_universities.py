"""Parse the academyinfo 'Foreign Student Status' XLSX into per-university records.

Column order (0-based) per docs/RAW_DATA_NOTES.md, item 33, universities:
  3=region 5=school 6=total(D) 7=degree(A)
  8=humanities 9=natural-sci 10=engineering 11=arts 12=medical
  13=joint(B) 14=non-degree(C) 15=language-training 16=exchange 17=visiting 18=other
"""
from __future__ import annotations

REGION_COL = 3
NAME_COL = 5
TOTAL_COL = 6
DEGREE_COL = 7
NON_DEGREE_COL = 14

FIELD_COLS = [
    (8, "Humanities & Social Sciences"),
    (9, "Natural Sciences"),
    (10, "Engineering"),
    (11, "Arts & Sports"),
    (12, "Medical"),
]
PROGRAM_COLS = [
    (15, "Language training"),
    (16, "Exchange"),
    (17, "Visiting"),
    (18, "Other"),
]


def _to_int(value) -> int:
    try:
        n = int(float(str(value).replace(",", "").strip()))
    except (TypeError, ValueError):
        return 0
    return n if n > 0 else 0


def _breakdown(row, cols) -> list[dict]:
    items = [{"name": label, "count": _to_int(row[i])} for i, label in cols]
    items = [it for it in items if it["count"] > 0]
    items.sort(key=lambda it: it["count"], reverse=True)
    return items


def read_data_rows(xlsx_path: str) -> list[list]:
    """Read the XLSX and return data rows (the 3-row merged header is skipped)."""
    import pandas as pd
    df = pd.read_excel(xlsx_path, header=None, skiprows=7)
    return df.values.tolist()


def parse_universities(rows) -> list[dict]:
    """Return one record per university with totals and breakdowns."""
    out = []
    for row in rows:
        name = str(row[NAME_COL]).strip()
        if not name or name.lower() == "nan":
            continue
        out.append({
            "name_ko": name,
            "region_ko": str(row[REGION_COL]).strip(),
            "total": _to_int(row[TOTAL_COL]),
            "degree": _to_int(row[DEGREE_COL]),
            "by_field": _breakdown(row, FIELD_COLS),
            "non_degree": _to_int(row[NON_DEGREE_COL]),
            "by_program": _breakdown(row, PROGRAM_COLS),
        })
    return out
