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
    "키르기즈": "Kyrgyzstan",
    "키르기즈스탄": "Kyrgyzstan",
    "레바논": "Lebanon",
    "리비아": "Libya",
    "말레이시아": "Malaysia",
    "몰디브": "Maldives",
    "말리": "Mali",
    "모리타니": "Mauritania",
    "모리타니아": "Mauritania",
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
    "아랍에미리트연합": "United Arab Emirates",
    "우즈베키스탄": "Uzbekistan",
    "예멘": "Yemen",
    "예멘공화국": "Yemen",
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
