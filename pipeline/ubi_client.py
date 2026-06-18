"""Client for academyinfo.go.kr UbiReport disclosure data.

Proven capability: fetch the RdViewer page for a disclosure item, then POST its
embedded params to NewAcInfo.do to get the rendered report as positioned-cell
XML, and parse that into rows.

LIMITATION (verified): anonymous/stateless HTTP returns only the FIRST PAGE
(~19 rows) of a multi-page report. Full pagination requires a server-side
report daemon session (daemonid/serviceid) that stateless requests do not
establish; streaming, page-N, and Excel-export modes all fall back to page 1.
To get all universities, slice the query (e.g. per-school via paramSchlCd) or
use the bulk-download portal / a manual XLSX download.
"""
from __future__ import annotations

import re
import time
import requests

from pipeline.decode_ubi import extract_literal

VIEWER_URL = "https://www.academyinfo.go.kr/uipnh/unt/unmcom/RdViewer.do"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

# params echoed from the RdViewer page into the render POST
_ECHO_PARAMS = (
    "resultMaster", "resultHeader", "resultBody", "resultSum", "strQuery",
    "url", "strSvyYr", "strItemId", "strSchlDivCd", "strFormClftCd",
    "strMasterId", "isMerge", "columLaung", "strPgmNm", "strNowDate",
)


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Referer": VIEWER_URL})
    return s


def viewer_params(svy_yr="2025", item_id="33", schl_div="02",
                  form_clft="30", item_div="01", **extra):
    p = {
        "paramSvyYr": svy_yr, "paramMjrItem1": "00", "paramFormClftCd": form_clft,
        "paramItemId": item_id, "paramSchlDivCd": schl_div, "paramDiv": "A",
        "paramItemDivCd": item_div, "paramSchlKindCd": "99",
        "paramSchlEstabCd": "99", "paramZoneCd": "99",
    }
    p.update(extra)
    return p


def fetch_viewer_html(s: requests.Session, **params) -> str:
    return s.get(VIEWER_URL, params=viewer_params(**params), timeout=30).text


def build_render_payload(html: str) -> dict:
    payload = {
        "key": extract_literal(html, "pKey"),
        "resid": extract_literal(html, "pResId"),
        "jrffile": extract_literal(html, "pJrf"),
        "arg": extract_literal(html, "pArg"),
        "reqtype": "0", "exportseq": str(int(time.time() * 1000)),
        "isencrypt": "true", "isStreaming": "false", "issvg": "false",
        "language": "ko", "cHJvY2lk": "GATEWAY",
    }
    for name in _ECHO_PARAMS:
        v = extract_literal(html, "htmlViewer.params." + name)
        if v is not None:
            payload[name] = v
    return payload


def render(s: requests.Session, html: str) -> str:
    """POST the report params and return the rendered XML (page 1)."""
    server = extract_literal(html, "pServerUrl")
    payload = build_render_payload(html)
    r = s.post(server + "?cHJvY2lk=GATEWAY", data=payload, timeout=120)
    r.raise_for_status()
    return r.text


_CELL_RE = re.compile(
    r'<Item\b[^>]*\bx="(\d+)"[^>]*\by="(\d+)"[^>]*>\s*<Text[^>]*>(.*?)</Text>')


def parse_rows(xml: str) -> list[list[str]]:
    """Group positioned text cells into rows (by y, ordered by x)."""
    rows: dict[int, list[tuple[int, str]]] = {}
    for x, y, txt in _CELL_RE.findall(xml):
        rows.setdefault(int(y), []).append((int(x), txt))
    out = []
    for y in sorted(rows):
        out.append([t for _, t in sorted(rows[y])])
    return out


def data_rows(xml: str, min_numeric: int = 10) -> list[list[str]]:
    """Return only rows that look like school data (>= min_numeric numbers)."""
    num = re.compile(r"-?[\d,]+(?:\.\d+)?$")
    return [r for r in parse_rows(xml)
            if sum(1 for c in r if num.match(c)) >= min_numeric]
