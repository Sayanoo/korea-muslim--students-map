"""Scrape per-university foreign-student counts BY NATIONALITY.

Uses the per-school disclosure form (form_clft_cd=60) of academyinfo item 33,
which — unlike the aggregate form 30 — exposes one row per country of origin.
The report paginates; pages are fetched with a fixed exportseq + shared session
(reqtype=91#N), which the server serves from its per-session render cache.
"""
from __future__ import annotations

import re

import requests

from pipeline.decode_ubi import extract_literal
from pipeline.ubi_client import parse_rows

RDVIEWER = "https://www.academyinfo.go.kr/uipnh/unt/unmcom/RdViewer.do"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")
_ECHO = ("resultMaster", "resultHeader", "resultBody", "resultSum", "strQuery",
         "url", "strSvyYr", "strItemId", "strSchlDivCd", "strFormClftCd",
         "strMasterId", "isMerge", "columLaung", "strPgmNm", "strNowDate")

_NUM = re.compile(r"-?[\d,]+$")
_HANGUL = re.compile(r"[가-힣]")
_LABELS = {"합 계", "합계", "계", "소계", "국가", "학교", "기준연도", "수용", "미수용"}
# substrings that mark a token as a column label / school name, never a country
_NON_COUNTRY = ("대학", "계열", "과정", "연수생", "학생", "현황", "능력", "비율")


def country_totals_from_rows(rows: list[list[str]]) -> dict[str, int]:
    """{country_ko: total} — the first hangul non-label token followed by a number."""
    out: dict[str, int] = {}
    for cells in rows:
        cells = [c.strip() for c in cells]
        for i in range(len(cells) - 1):
            tok, nxt = cells[i], cells[i + 1]
            if (_HANGUL.search(tok) and tok not in _LABELS
                    and not any(s in tok for s in _NON_COUNTRY)
                    and _NUM.fullmatch(nxt)):
                out[tok] = int(nxt.replace(",", ""))
                break
    return out


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA,
                      "Referer": "https://www.academyinfo.go.kr/pubinfo/pubinfo0020/list.do"})
    return s


def _render_payload(html: str, exportseq: str) -> dict:
    payload = {
        "key": extract_literal(html, "pKey"), "resid": extract_literal(html, "pResId"),
        "jrffile": extract_literal(html, "pJrf"), "arg": extract_literal(html, "pArg"),
        "reqtype": "0", "exportseq": exportseq, "isencrypt": "true",
        "isStreaming": "false", "issvg": "false", "language": "ko", "cHJvY2lk": "GATEWAY",
    }
    for p in _ECHO:
        v = extract_literal(html, "htmlViewer.params." + p)
        if v is not None:
            payload[p] = v
    return payload


def scrape_school(session: requests.Session, schl_id: str,
                  expected_total: int | None = None, max_pages: int = 15) -> dict[str, int]:
    """Return {country_ko: total} for one school across all report pages."""
    data = {"paramSvyYr": "2025", "paramItemId": "33", "paramSchlDivCd": "02",
            "paramSchlCd": schl_id, "paramFormClftCd": "60", "paramSchlKindCd": "99",
            "paramSchlEstabCd": "99", "paramZoneCd": "99", "ui_schl_knd_cd": "03"}
    html = session.post(RDVIEWER, data=data, timeout=40).text
    server = extract_literal(html, "pServerUrl")
    exportseq = "17500000%07d" % (int(schl_id) % 9999999)
    payload = _render_payload(html, exportseq)
    gw = server + "?cHJvY2lk=GATEWAY"

    totals: dict[str, int] = {}
    r = session.post(gw, data=payload, timeout=60)
    totals.update(country_totals_from_rows(parse_rows(r.text)))
    for n in range(2, max_pages + 1):
        if expected_total is not None and sum(totals.values()) >= expected_total:
            break
        pg = dict(payload, reqtype=f"91#{n}")
        r = session.post(gw, data=pg, timeout=60)
        added = {k: v for k, v in country_totals_from_rows(parse_rows(r.text)).items()
                 if k not in totals}
        if not added:
            break
        totals.update(added)
    return totals
