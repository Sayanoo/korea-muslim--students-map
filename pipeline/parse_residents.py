"""Parse the 법무부 통계연보 '시군구별 및 국적(지역)별 등록외국인' Excel into
province-level per-nationality counts (registered/resident foreigners)."""
from __future__ import annotations

import io
import zipfile

_META_COLS = {"시도", "시군구", "성별", "총합계"}


def _to_int(v) -> int:
    try:
        return int(float(str(v).replace(",", "").strip()))
    except (TypeError, ValueError):
        return 0


def parse_province_counts(df) -> dict[str, dict[str, int]]:
    """Return {province_ko: {country_ko: count}} from the province total rows
    (시군구 == '총계' and 성별 == '총계')."""
    nat_cols = [c for c in df.columns if c not in _META_COLS]
    out: dict[str, dict[str, int]] = {}
    for _, row in df.iterrows():
        if str(row.get("시군구")).strip() != "총계" or str(row.get("성별")).strip() != "총계":
            continue
        prov = str(row.get("시도")).strip()
        if not prov or prov == "총합계" or prov.lower() == "nan":
            continue
        out[prov] = {c: _to_int(row[c]) for c in nat_cols}
    return out


def load_province_counts_from_zip(zip_path: str) -> dict[str, dict[str, int]]:
    """Read the district×nationality sheet from the yearbook zip."""
    import pandas as pd
    z = zipfile.ZipFile(zip_path)

    def _name(n):
        try:
            return n.encode("cp437").decode("cp949")
        except Exception:  # noqa: BLE001
            return n

    target = next(n for n in z.namelist() if "시군구별 및 국적" in _name(n))
    df = pd.read_excel(io.BytesIO(z.read(target)), header=0)
    return parse_province_counts(df)
