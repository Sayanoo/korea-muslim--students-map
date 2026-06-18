"""Resolve academyinfo school IDs (schlId) for university names via search.do."""
from __future__ import annotations

import json
import os
import re
import time

import requests

SEARCH_URL = "https://www.academyinfo.go.kr/search/search.do"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

_CAND_RE = re.compile(r"gnf_go_schl_detail\('(\d{7})'\s*,\s*'[^']*'\)[^>]*>\s*([^<]+?)\s*<")


def parse_candidates(html: str) -> list[tuple[str, str]]:
    """Return [(schlId, school_name), ...] from search.do result links."""
    seen = []
    for sid, name in _CAND_RE.findall(html):
        if (sid, name) not in seen:
            seen.append((sid, name))
    return seen


def _norm(s: str) -> str:
    s = re.sub(r"_(제\d+캠퍼스|분교|본교).*$", "", s)
    s = re.sub(r"\s+", "", s)
    return s.strip()


def match_school_id(html: str, name: str) -> str | None:
    """Pick the schlId whose name matches `name` (exact, then normalized)."""
    cands = parse_candidates(html)
    for sid, nm in cands:
        if nm == name:
            return sid
    target = _norm(name)
    for sid, nm in cands:
        if _norm(nm) == target:
            return sid
    return None


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Referer": "https://www.academyinfo.go.kr/index.do",
                      "X-Requested-With": "XMLHttpRequest"})
    s.get("https://www.academyinfo.go.kr/index.do", timeout=30)
    return s


def fetch_school_id(session: requests.Session, name: str) -> str | None:
    r = session.post(SEARCH_URL, data={"kwd": name, "searchGbn": "0"}, timeout=30)
    return match_school_id(r.text, name)


def resolve_school_ids(names, cache_path: str, session=None) -> dict[str, str | None]:
    """Resolve names -> schlId, caching results (resumable)."""
    cache = {}
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            cache = json.load(f)
    todo = [n for n in names if n not in cache]
    if todo and session is None:
        session = make_session()
    for i, name in enumerate(todo, 1):
        cache[name] = fetch_school_id(session, name)
        time.sleep(0.4)
        if i % 25 == 0:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            print(f"  resolved {i}/{len(todo)}…", flush=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    return cache
