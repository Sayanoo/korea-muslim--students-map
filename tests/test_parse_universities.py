from pipeline.parse_universities import parse_universities


def _row(name, region, total, A, hum, nat, eng, art, med,
         B, C, lang_t, exch, visit, other):
    """Build a 30-column raw data row in the documented column order."""
    r = [""] * 30
    r[3] = region
    r[5] = name
    r[6] = total
    r[7] = A
    r[8], r[9], r[10], r[11], r[12] = hum, nat, eng, art, med
    r[13] = B
    r[14] = C
    r[15], r[16], r[17], r[18] = lang_t, exch, visit, other
    return r


def test_parses_total_and_field_breakdown_dropping_zeros():
    rows = [_row("테스트대학교", "서울", "100", "80", "50", "0", "30", "0", "0",
                 "0", "20", "15", "5", "0", "0")]
    out = parse_universities(rows)
    assert len(out) == 1
    u = out[0]
    assert u["name_ko"] == "테스트대학교"
    assert u["region_ko"] == "서울"
    assert u["total"] == 100
    assert u["degree"] == 80
    assert u["by_field"] == [
        {"name": "Humanities & Social Sciences", "count": 50},
        {"name": "Engineering", "count": 30},
    ]
    assert u["non_degree"] == 20
    assert u["by_program"] == [
        {"name": "Language training", "count": 15},
        {"name": "Exchange", "count": 5},
    ]


def test_parses_comma_thousands_separators():
    rows = [_row("가천대학교", "경기", "4,996", "3,616", "1,000", "1,000",
                 "1,616", "0", "0", "0", "1,380", "1,380", "0", "0", "0")]
    u = parse_universities(rows)[0]
    assert u["total"] == 4996
    assert u["degree"] == 3616
    assert u["non_degree"] == 1380


def test_skips_rows_with_blank_name():
    rows = [
        _row("", "서울", "10", "10", "10", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
        _row("nan", "서울", "10", "10", "10", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
        _row("진짜대학교", "서울", "5", "5", "5", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
    ]
    out = parse_universities(rows)
    assert [u["name_ko"] for u in out] == ["진짜대학교"]


def test_non_numeric_counts_treated_as_zero():
    rows = [_row("대학", "부산", "3", "3", "-", "3", "", "0", "0", "0", "0", "0", "0", "0", "0")]
    u = parse_universities(rows)[0]
    assert u["total"] == 3
    assert u["by_field"] == [{"name": "Natural Sciences", "count": 3}]
