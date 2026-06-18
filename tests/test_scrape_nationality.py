from pipeline.scrape_nationality import country_totals_from_rows


def test_extracts_country_then_first_number_as_total():
    rows = [
        ["2025년_ [외국학생 현황 (대학)]"],
        ["기준연도", "학교", "국가", "학위과정 (대학)"],
        ["소계(A)", "인문사회계열", "자연과학계열"],            # header, no numbers
        ["합 계", "4,471", "2,929"],                          # total row -> skipped
        ["2025", "고려대학교", "아프가니스탄", "1", "0"],       # first row has year+school
        ["알제리", "6", "4", "2"],
        ["중국", "2,005", "1,500"],
    ]
    out = country_totals_from_rows(rows)
    assert out == {"아프가니스탄": 1, "알제리": 6, "중국": 2005}


def test_ignores_total_and_header_rows():
    rows = [["합 계", "100"], ["국가", "학위과정"], ["미수용", "수용"]]
    assert country_totals_from_rows(rows) == {}
