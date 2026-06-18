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

def test_official_data_spelling_variants_map_correctly():
    # spellings used in 법무부 / 대학알리미 data that differ from the canonical key
    assert normalize_country("키르기즈") == "Kyrgyzstan"
    assert normalize_country("모리타니아") == "Mauritania"
    assert normalize_country("아랍에미리트연합") == "United Arab Emirates"
    assert normalize_country("예멘공화국") == "Yemen"


def test_korean_ethnic_diaspora_categories_are_not_counted():
    # "재OO동포" = ethnic-Korean diaspora, excluded like 한국계중국인
    assert normalize_country("재키르기즈동포") is None
    assert normalize_country("재우즈베키스탄동포") is None


def test_non_muslim_country_returns_none():
    assert normalize_country("중국") is None      # China
    assert normalize_country("베트남") is None     # Vietnam
    assert normalize_country("") is None

def test_list_is_majority_muslim_sized():
    assert 40 <= len(set(MUSLIM_KO_TO_EN.values())) <= 50
