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

def test_non_muslim_country_returns_none():
    assert normalize_country("중국") is None      # China
    assert normalize_country("베트남") is None     # Vietnam
    assert normalize_country("") is None

def test_list_is_majority_muslim_sized():
    assert 40 <= len(set(MUSLIM_KO_TO_EN.values())) <= 50
